#!/usr/bin/env python3
"""Import the authorized catalog and approved PNGs with resumable checkpoints."""
import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import sys
import urllib.error
import urllib.parse
import urllib.request
import uuid

import dry_run as source

IMAGE_FIELDS = ("image_path", "image_sha256", "image_width", "image_height", "image_origin")
OUTPUT = source.ROOT / "integration/supabase/uploads"


def now():
    return datetime.now(timezone.utc).isoformat()


def save(path, value):
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n")
    temporary.replace(path)


def source_matches(row, original):
    return all(row.get(field) == original[field] for field in source.DIRECT_FIELDS)


def image_matches(row, patch):
    return all(row.get(field) == patch[field] for field in IMAGE_FIELDS)


def patch_filter(row):
    filters = {"id": "eq." + row["id"], "updated_at": "eq." + row["updated_at"]}
    for field in IMAGE_FIELDS:
        value = row.get(field)
        filters[field] = "is.null" if value is None else "eq." + str(value)
    return "/rest/v1/catalog_exercise?" + urllib.parse.urlencode(filters)


def is_missing_object(status, raw):
    try:
        error = json.loads(raw)
    except (ValueError, TypeError):
        return False
    # Storage may return HTTP 400 with logical statusCode 404. An auth/network
    # error must never be interpreted as an absent object.
    return status in (400, 404) and isinstance(error, dict) and (
        str(error.get("statusCode")) == "404" or error.get("error") in ("not_found", "NoSuchKey")
    )


class Api:
    def __init__(self, apply, paths):
        self.key = os.environ.get("exerciseuploader")
        proxy = urllib.request.getproxies().get("https")
        if not self.key or not proxy or urllib.request.proxy_bypass(source.HOST):
            raise RuntimeError("Secret binding or supported HTTPS proxy route unavailable")
        self.http = urllib.request.build_opener(urllib.request.ProxyHandler({"https": proxy}))
        self.apply = apply
        self.paths = set(paths)
        self.run_id = uuid.uuid4().hex

    def request(self, method, path, payload=None, headers=None, authenticated=True):
        is_catalog = path.split("?", 1)[0] == "/rest/v1/catalog_exercise"
        storage_prefix = "/storage/v1/object/" + source.BUCKET + "/"
        if method != "GET":
            allowed = (method == "POST" and is_catalog and "?" not in path
                       or method == "PATCH" and is_catalog and "?" in path
                       or method == "POST" and path.startswith(storage_prefix)
                          and path[len(storage_prefix):] in self.paths)
            if not self.apply or not allowed:
                raise RuntimeError("Mutation outside authorized catalog/image scope")
        elif not (is_catalog or path == "/storage/v1/bucket"
                  or path.startswith("/storage/v1/object/public/" + source.BUCKET + "/")):
            raise RuntimeError("Read outside integration scope")
        request_headers = dict(headers or {})
        if authenticated:
            request_headers["apikey"] = self.key
        if isinstance(payload, (list, dict)):
            payload = json.dumps(payload, ensure_ascii=False, separators=(",", ":")).encode()
            request_headers["Content-Type"] = "application/json"
        request = urllib.request.Request(source.BASE + path, data=payload,
                                         headers=request_headers, method=method)
        try:
            with self.http.open(request, timeout=45) as response:
                return response.read(), response.status, dict(response.headers)
        except urllib.error.HTTPError as error:
            return error.read(), error.code, dict(error.headers)
        except urllib.error.URLError:
            raise RuntimeError("Proxy/network error; operation outcome may be uncertain. Resume by reading current state.") from None

    def require(self, method, path, payload=None, headers=None):
        raw, status, response_headers = self.request(method, path, payload, headers)
        if not 200 <= status < 300:
            message = "HTTP " + str(status)
            try:
                error = json.loads(raw)
                message += " " + str(error.get("code", error.get("error", "")))
                message += ": " + str(error.get("message", ""))[:500]
            except (ValueError, AttributeError):
                pass
            raise RuntimeError(message.replace(self.key, "[REDACTED]"))
        return raw, status, response_headers

    def catalog(self):
        rows, offset = [], 0
        while True:
            query = urllib.parse.urlencode({"select": "*", "order": "id.asc", "limit": 500, "offset": offset})
            raw, _, _ = self.require("GET", "/rest/v1/catalog_exercise?" + query,
                                     headers={"Prefer": "count=exact"})
            page = json.loads(raw)
            if not isinstance(page, list):
                raise RuntimeError("Unexpected catalog response")
            rows.extend(page)
            if not page:
                break
            offset += len(page)
        result = {row["id"]: row for row in rows}
        if len(result) != len(rows):
            raise RuntimeError("Duplicate catalog IDs")
        return result

    def row(self, eid):
        query = urllib.parse.urlencode({"id": "eq." + eid, "select": "*"})
        raw, _, _ = self.require("GET", "/rest/v1/catalog_exercise?" + query)
        rows = json.loads(raw)
        if len(rows) != 1:
            raise RuntimeError("Expected one exact catalog ID: " + eid)
        return rows[0]

    def public(self, path, existence_check=False):
        url = "/storage/v1/object/public/" + source.BUCKET + "/" + path
        if existence_check:
            url += "?audit=" + self.run_id
        return self.request("GET", url, authenticated=False)


def verify_public(raw, status, headers, expected_sha):
    if status != 200 or source.digest(raw) != expected_sha:
        raise RuntimeError("Public PNG read/status/SHA256 verification failed")
    content_type = next((v for k, v in headers.items() if k.lower() == "content-type"), "")
    if content_type.split(";", 1)[0].strip().lower() != "image/png":
        raise RuntimeError("Public object MIME type is not image/png")
    return {"http_status": status, "sha256": source.digest(raw), "bytes": len(raw),
            "mime_type": "image/png", "without_apikey_or_authorization": True,
            "verified_at_utc": now()}


def load_inputs():
    source.pinned_sources()
    catalog = source.read_json(source.ROOT / "data/exercises/catalog.json")
    originals = {row["id"]: row for row in catalog["exercises"]}
    if len(originals) != 451 or sum(len(row["content"]) for row in originals.values()) != 4448:
        raise RuntimeError("Source catalog IDs/languages changed")
    draft = source.read_json(source.ROOT / "integration/supabase/results/catalog_import_plan.json")
    seeds = draft["insert_records"]
    if len(seeds) != 451 or len({row["id"] for row in seeds}) != 451:
        raise RuntimeError("Invalid insert draft scope")
    for row in seeds:
        if row["id"] not in originals or not source_matches(row, originals[row["id"]]):
            raise RuntimeError("Insert draft conflicts with source")
        if "replaces_ids" in row or "updated_at" in row or any(row.get(k) is not None for k in IMAGE_FIELDS):
            raise RuntimeError("Insert must omit server-default fields and start with all image fields NULL")
        if source.constraint_violations({**row, "replaces_ids": []}):
            raise RuntimeError("Insert draft violates supplied SQL constraints")
    plan = source.read_json(source.ROOT / "integration/supabase/results/approved_png_plan.json")
    progress = source.read_json(source.ROOT / "data/exercise-image-progress.json")["exercises"]
    if len(plan) != 135 or len({row["exercise_id"] for row in plan}) != 135:
        raise RuntimeError("Image plan differs from authorized 135 IDs")
    for row in plan:
        eid, sha = row["exercise_id"], row["accepted_sha256"]
        if progress[eid].get("user_review") != "approved" or progress[eid].get("accepted_sha256") != sha:
            raise RuntimeError("Pending/rejected/unaccepted image in import scope")
        if row["destination_path"] != eid + "/" + sha + ".png" or row["bucket"] != source.BUCKET:
            raise RuntimeError("Image destination differs from authorization")
        if source.source_path(row["source_png"]) != row["source_png"]:
            raise RuntimeError("Source path outside cloud repository assets")
        raw = (source.ROOT / row["source_png"]).read_bytes()
        check = row["byte_verification"]
        if source.digest(raw) != sha or len(raw) > source.SIZE_LIMIT or not check["ready_for_upload_bytes"] or check["sha256"] != sha:
            raise RuntimeError("Accepted PNG bytes differ from verified plan: " + eid)
        patch = row["proposed_image_patch"]
        if patch != {"image_path": row["destination_path"], "image_sha256": sha,
                     "image_width": check["width"], "image_height": check["height"], "image_origin": "generated"}:
            raise RuntimeError("Image patch differs from verified PNG")
    return originals, seeds, plan


def verify_catalog(rows, originals):
    if set(rows) != set(originals):
        raise RuntimeError("Catalog ID set differs from exact 451 source IDs")
    for eid, row in rows.items():
        if not source_matches(row, originals[eid]):
            raise RuntimeError("Catalog data/content conflict: " + eid)
    count = sum(len(row["content"]) for row in rows.values())
    if count != 4448:
        raise RuntimeError("Language block count differs")
    return {"verified_ids": len(rows), "language_blocks": count,
            "archived": sum(row["archived"] for row in rows.values()),
            "all_source_values_equal": True, "verified_at_utc": now()}


def import_catalog(api, originals, seeds):
    path = OUTPUT / "catalog_manifest.json"
    previous = source.read_json(path) if path.exists() else None
    current = api.catalog()  # Always reread before any insert.
    if set(current) - set(originals):
        raise RuntimeError("Unexpected catalog IDs; no rows will be overwritten or deleted")
    conflicts = [eid for eid, row in current.items() if not source_matches(row, originals[eid])]
    if conflicts:
        raise RuntimeError("Existing catalog conflicts; import stopped: " + ",".join(conflicts[:5]))
    missing = [row for row in seeds if row["id"] not in current]
    manifest = previous or {"project_ref": source.HOST.split(".")[0], "source_commit": source.SOURCE_COMMIT,
        "catalog_sha256": source.CATALOG_SHA256, "insert_batches": [], "created_at_utc": now()}
    if (manifest["catalog_sha256"] != source.CATALOG_SHA256
            or manifest["project_ref"] != source.HOST.split(".")[0]
            or manifest["source_commit"] != source.SOURCE_COMMIT):
        raise RuntimeError("Existing checkpoint belongs to another catalog")
    manifest["already_identical_on_this_run"] = len(current)
    for start in range(0, len(missing), 100):
        batch = missing[start:start + 100]
        # No upsert or replaces_ids field. PostgREST applies actual server defaults.
        _, status, _ = api.require("POST", "/rest/v1/catalog_exercise", batch,
                                   {"Prefer": "missing=default,return=minimal"})
        manifest["insert_batches"].append({"ids": [row["id"] for row in batch], "http_status": status,
                                          "missing_default_requested": True, "at_utc": now()})
        save(path, manifest)
    readback = api.catalog()
    verification = verify_catalog(readback, originals)
    inserted_ids = {eid for batch in manifest["insert_batches"] for eid in batch["ids"]}
    if any(readback[eid]["replaces_ids"] != [] for eid in inserted_ids):
        raise RuntimeError("Server replaces_ids default was not applied to inserted rows")
    manifest.update({"verification": verification, "newly_inserted_on_this_run": len(missing),
                     "unique_inserted_ids_recorded": len(inserted_ids), "status": "verified"})
    save(path, manifest)
    print("Catalog verified: 451 IDs / 4448 language blocks; inserted this run:", len(missing), flush=True)
    return manifest


def transfer_one(api, item, original, previous):
    eid, sha, path = item["exercise_id"], item["accepted_sha256"], item["destination_path"]
    patch = item["proposed_image_patch"]
    result = {"exercise_id": eid, "accepted_sha256": sha, "storage_path": path,
              "source_png": item["source_png"], "bucket": source.BUCKET,
              "public_url": item["public_url"], "started_at_utc": now()}
    if previous and previous.get("status") == "complete":
        if previous["accepted_sha256"] != sha or previous["storage_path"] != path:
            raise RuntimeError("Completed manifest identity conflict")
        result = dict(previous)
        result["resume_skipped"] = True
        row = api.row(eid)
        if not source_matches(row, original) or not image_matches(row, patch):
            raise RuntimeError("Previously verified database link changed")
        result["file_verification"] = verify_public(*api.public(path), sha)
        result["last_reverified_at_utc"] = now()
        return result
    row = api.row(eid)
    if not source_matches(row, original):
        raise RuntimeError("Catalog changed before image update: " + eid)
    if not image_matches(row, patch) and any(row.get(field) is not None for field in IMAGE_FIELDS):
        raise RuntimeError("Existing image link conflict; no overwrite: " + eid)
    raw, status, headers = api.public(path, existence_check=True)
    if status == 200:
        verify_public(raw, status, headers, sha)
        result["storage_action"] = "existing_bytes_verified_no_overwrite"
    elif is_missing_object(status, raw):
        local = (source.ROOT / item["source_png"]).read_bytes()
        if source.digest(local) != sha:
            raise RuntimeError("Source PNG changed before upload")
        _, upload_status, _ = api.require("POST", "/storage/v1/object/" + source.BUCKET + "/" + path,
            local, {"Content-Type": "image/png", "x-upsert": "false", "Cache-Control": "max-age=31536000"})
        result["storage_action"] = "uploaded_new_no_upsert"
        result["upload_http_status"] = upload_status
    else:
        raise RuntimeError("Storage existence check failed with HTTP " + str(status))
    # Canonical public URL, without secret/auth, must pass before PATCH.
    result["file_verification"] = verify_public(*api.public(path), sha)
    result["database_before"] = {"id": row["id"], "updated_at": row["updated_at"],
                                 **{field: row.get(field) for field in IMAGE_FIELDS}}
    if image_matches(row, patch):
        result["database_action"] = "existing_identical_link_skipped"
    else:
        raw, update_status, _ = api.require("PATCH", patch_filter(row), patch,
                                            {"Prefer": "return=representation"})
        updated = json.loads(raw)
        if len(updated) != 1 or updated[0]["id"] != eid or not image_matches(updated[0], patch):
            raise RuntimeError("Conditional image update did not affect exactly one expected row")
        result["database_action"] = "image_fields_updated"
        result["update_http_status"] = update_status
    after = api.row(eid)
    if not source_matches(after, original) or not image_matches(after, patch):
        raise RuntimeError("Database image/content read-back failed")
    result.update({"database_verification": {"id": eid, "image_fields_equal": True,
        "source_content_unchanged": True, "updated_at": after["updated_at"]},
        "status": "complete", "completed_at_utc": now()})
    return result


def run_batches(api, originals, plan):
    batches = [plan[:3]] + [plan[start:start + 10] for start in range(3, len(plan), 10)]
    for index, items in enumerate(batches, 1):
        path = OUTPUT / ("batch-%03d.json" % index)
        doc = source.read_json(path) if path.exists() else {
            "project_ref": source.HOST.split(".")[0], "source_commit": source.SOURCE_COMMIT,
            "batch_number": index, "expected_ids": [item["exercise_id"] for item in items],
            "entries": {}, "created_at_utc": now()}
        if (doc["expected_ids"] != [item["exercise_id"] for item in items]
                or doc["project_ref"] != source.HOST.split(".")[0]
                or doc["source_commit"] != source.SOURCE_COMMIT):
            raise RuntimeError("Checkpoint batch scope differs")
        for item in items:
            eid = item["exercise_id"]
            try:
                doc["entries"][eid] = transfer_one(api, item, originals[eid], doc["entries"].get(eid))
                doc["status"] = "in_progress"
                save(path, doc)
            except Exception as error:
                message = str(error).replace(api.key, "[REDACTED]")
                doc["status"] = "stopped"
                doc["last_error"] = {"exercise_id": eid, "accepted_sha256": item["accepted_sha256"],
                    "storage_path": item["destination_path"], "requires_state_reconciliation": True,
                    "message": message, "at_utc": now()}
                save(path, doc)
                raise
        doc["status"] = "complete"
        doc.pop("last_error", None)
        doc["completed_at_utc"] = now()
        save(path, doc)
        print("Batch", index, "verified:", len(items), "PNG(s); total", sum(len(b) for b in batches[:index]), flush=True)


def check_ordinary_client(originals):
    # Reuse only already-injected public client bindings; never expose their values.
    names = ("SUPABASE_PUBLISHABLE_KEY", "SUPABASE_ANON_KEY", "VITE_SUPABASE_PUBLISHABLE_KEY",
             "VITE_SUPABASE_ANON_KEY", "NEXT_PUBLIC_SUPABASE_ANON_KEY")
    name = next((key for key in names if os.environ.get(key)), None)
    if not name:
        return {"verified": False, "reason": "No publishable/anon key binding is available; admin read does not prove ordinary-client catalog access."}
    client = Api(False, [])
    client.key = os.environ[name]
    try:
        result = verify_catalog(client.catalog(), originals)
        return {"verified": True, "binding_name": name, **result}
    except Exception as error:
        return {"verified": False, "binding_name": name,
                "reason": str(error).replace(client.key, "[REDACTED]")}


def write_summary(completion, plan):
    batch_files = sorted(OUTPUT.glob("batch-*.json"))
    docs = [source.read_json(path) for path in batch_files]
    entries = [entry for doc in docs for entry in doc["entries"].values()]
    expected = {(row["exercise_id"], row["accepted_sha256"], row["destination_path"]) for row in plan}
    actual = {(row["exercise_id"], row["accepted_sha256"], row["storage_path"]) for row in entries}
    if len(entries) != 135 or expected != actual or any(doc["status"] != "complete" for doc in docs):
        raise RuntimeError("Cannot finalize summary: batch manifests differ from approved scope")
    if any(row["status"] != "complete" or row["file_verification"]["sha256"] != row["accepted_sha256"]
           or not row["database_verification"]["image_fields_equal"] for row in entries):
        raise RuntimeError("Cannot finalize summary: incomplete byte/database verification")
    catalog = source.read_json(OUTPUT / "catalog_manifest.json")
    paths = [OUTPUT / "catalog_manifest.json", OUTPUT / "completion.json", *batch_files]
    result = {
        "project_ref": source.HOST.split(".")[0], "source_commit": source.SOURCE_COMMIT,
        "catalog_inserted_unique_ids": catalog["unique_inserted_ids_recorded"],
        "catalog_verified_ids": completion["catalog_verification"]["verified_ids"],
        "language_blocks_verified": completion["catalog_verification"]["language_blocks"],
        "archived_preserved": completion["catalog_verification"]["archived"],
        "pngs_uploaded_new": sum(row["storage_action"] == "uploaded_new_no_upsert" for row in entries),
        "pngs_existing_bytes_skipped": sum(row["storage_action"] == "existing_bytes_verified_no_overwrite" for row in entries),
        "pngs_public_sha256_verified": completion["pngs_public_sha256_verified"],
        "pngs_linked_to_exact_ids": completion["pngs_linked_to_exact_ids"],
        "database_image_updates": sum(row["database_action"] == "image_fields_updated" for row in entries),
        "batch_sizes": [len(doc["entries"]) for doc in docs], "pending_excluded": 21,
        "ordinary_client_catalog": completion["ordinary_client_catalog"],
        "public_png_reads_without_apikey": completion["public_png_reads_without_apikey"],
        "replaces_ids_omitted_and_server_default_verified": True, "errors": [],
        "source_approval_and_technical_exceptions_unchanged": True,
        "user_tables_modified": False, "schema_rls_grants_modified": False,
        "manifest_sha256": {path.name: source.digest(path.read_bytes()) for path in paths},
        "finalized_at_utc": now(),
    }
    save(OUTPUT / "summary.json", result)
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply", action="store_true", help="Execute the explicitly authorized import")
    parser.add_argument("--verify-only", action="store_true", help="Read all catalog/image state without writes")
    args = parser.parse_args()
    originals, seeds, plan = load_inputs()
    api = Api(args.apply and not args.verify_only, [item["destination_path"] for item in plan])
    raw, _, _ = api.require("GET", "/storage/v1/bucket")
    bucket = next(row for row in json.loads(raw) if row["id"] == source.BUCKET)
    if bucket["public"] is not True or bucket["file_size_limit"] != source.SIZE_LIMIT or bucket["allowed_mime_types"] != ["image/png"]:
        raise RuntimeError("Bucket settings differ from authorized constraints")
    if not args.apply and not args.verify_only:
        current = api.catalog()
        conflicts = [eid for eid, row in current.items() if eid not in originals or not source_matches(row, originals[eid])]
        print(json.dumps({"dry_run": True, "source_ids": 451, "language_blocks": 4448,
            "missing_ids": len(set(originals) - set(current)), "conflicting_ids": conflicts,
            "approved_pngs": len(plan), "server_default_replaces_ids_omitted": True}))
        return 2 if conflicts else 0
    OUTPUT.mkdir(parents=True, exist_ok=True)
    if not args.verify_only:
        import_catalog(api, originals, seeds)
        run_batches(api, originals, plan)
    verification = verify_catalog(api.catalog(), originals)
    for item in plan:
        row = api.row(item["exercise_id"])
        if not image_matches(row, item["proposed_image_patch"]):
            raise RuntimeError("Final image link differs: " + item["exercise_id"])
        verify_public(*api.public(item["destination_path"]), item["accepted_sha256"])
    result = {"project_ref": source.HOST.split(".")[0], "source_commit": source.SOURCE_COMMIT,
        "catalog_verification": verification, "pngs_public_sha256_verified": len(plan),
        "pngs_linked_to_exact_ids": len(plan), "pending_excluded": 21,
        "ordinary_client_catalog": check_ordinary_client(originals),
        "public_png_reads_without_apikey": True, "user_tables_written": False,
        "rls_grants_schema_changed": False, "replaces_ids_sent_in_inserts": False,
        "completed_at_utc": now()}
    save(OUTPUT / "completion.json", result)
    write_summary(result, plan)
    print(json.dumps(result, ensure_ascii=False, indent=2), flush=True)
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as error:
        message = str(error)
        for key in ("exerciseuploader", "SUPABASE_PUBLISHABLE_KEY", "SUPABASE_ANON_KEY"):
            value = os.environ.get(key)
            if value:
                message = message.replace(value, "[REDACTED]")
        print("Import stopped: " + message, file=sys.stderr, flush=True)
        sys.exit(1)
