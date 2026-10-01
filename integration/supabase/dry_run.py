#!/usr/bin/env python3
"""Prepare local artifacts and audit Supabase using read-only network operations."""

import argparse
from collections import Counter
from datetime import datetime, timezone
import hashlib
import io
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import urllib.error
import urllib.parse
import urllib.request

from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
SOURCE_COMMIT = "a6f296cbc6737991dd367e929b3e2df25874d4d8"
CATALOG_SHA256 = "a7cd78ba174d7277b4acaf95bd46c8a2774698d60a59cb2df6737fa2c7843989"
HOST = "yywyrbhqfavjdgonlzma.supabase.co"
BASE = "https://" + HOST
BUCKET = "exercise-images"
SIZE_LIMIT = 5 * 1024 * 1024
MANIFESTS = (
    "data/approved-images-manifest.json",
    "data/batches/night-2026-10-01-manifest.json",
    "data/batches/agent-03-others-manifest.json",
)
SOURCE_FILES = (
    "data/exercises/catalog.json", "data/exercise-image-progress.json",
    *MANIFESTS,
)
DIRECT_FIELDS = (
    "id", "name", "equipment", "primary_muscle", "secondary_muscles",
    "tracking_type", "archived", "content",
)


def digest(data):
    return hashlib.sha256(data).hexdigest()


def read_json(path):
    return json.loads(path.read_bytes())


def canonical_digest(value):
    return digest(json.dumps(value, ensure_ascii=False, sort_keys=True,
                             separators=(",", ":")).encode())


def source_path(value):
    """Convert historical cloud paths only when they identify repository assets."""
    if not isinstance(value, str):
        return None
    if "/assets/" in value:
        value = "assets/" + value.split("/assets/", 1)[1]
    if not value.startswith("assets/") or ".." in value.split("/"):
        return None
    path = (ROOT / value).resolve()
    if not path.is_relative_to(ROOT / "assets"):
        return None
    return value


def pinned_sources():
    for relative in SOURCE_FILES:
        expected = subprocess.check_output(
            ["git", "show", SOURCE_COMMIT + ":" + relative], cwd=ROOT)
        if (ROOT / relative).read_bytes() != expected:
            raise RuntimeError("Source changed since pinned commit: " + relative)
    raw = (ROOT / "data/exercises/catalog.json").read_bytes()
    if digest(raw) != CATALOG_SHA256:
        raise RuntimeError("Catalog SHA256 differs from the reviewed source")


def candidates():
    result = {}
    for relative in MANIFESTS:
        doc = read_json(ROOT / relative)
        for row in doc.get("images", doc.get("exercises", [])):
            if row.get("user_review") != "approved":
                continue
            sha = row.get("accepted_sha256") or row.get("sha256") or row.get("result_sha256")
            for field in ("accepted_repository_path", "repository_path",
                          "accepted_relative_png_path", "relative_png_path", "accepted_path"):
                path = source_path(row.get(field))
                if path:
                    result.setdefault((row["exercise_id"], sha), []).append((path, relative))
            # Never use a current result if it has a different, unaccepted hash.
            if not row.get("accepted_sha256") or row.get("result_sha256", sha) == sha:
                path = source_path(row.get("result_path"))
                if path:
                    result.setdefault((row["exercise_id"], sha), []).append((path, relative))
    return result


def verify_png(relative, expected_sha):
    path = ROOT / relative
    raw = path.read_bytes()
    result = {"bytes": len(raw), "sha256": digest(raw), "mime_type": "image/png"}
    issues = []
    if result["sha256"] != expected_sha:
        issues.append("accepted_sha256_mismatch")
    if len(raw) > SIZE_LIMIT:
        issues.append("bucket_size_limit_exceeded")
    if raw[:8] != b"\x89PNG\r\n\x1a\n":
        issues.append("invalid_png_signature")
    try:
        with Image.open(io.BytesIO(raw)) as image:
            image.verify()
        with Image.open(io.BytesIO(raw)) as image:
            image.load()
            alpha = image.convert("RGBA").getchannel("A")
            histogram = alpha.histogram()
            width, height = image.size
            result.update({
                "format": image.format, "width": width, "height": height,
                "mode": image.mode, "square": width == height,
                "has_alpha_or_transparency": "A" in image.getbands() or "transparency" in image.info,
                "fully_transparent_pixels": histogram[0],
                "partially_transparent_pixels": sum(histogram[1:255]),
                "corner_alpha": [alpha.getpixel(p) for p in
                                 ((0, 0), (width - 1, 0), (0, height - 1), (width - 1, height - 1))],
                "matches_historical_1024_target": image.size == (1024, 1024),
            })
            if image.format != "PNG":
                issues.append("not_png")
            if not result["has_alpha_or_transparency"] or histogram[0] == 0:
                issues.append("no_actual_fully_transparent_pixels")
    except Exception as error:
        issues.append("png_decode_failed:" + type(error).__name__)
    result["issues"] = issues
    result["ready_for_upload_bytes"] = not issues
    return result


class ReadOnlySupabase:
    def __init__(self):
        self.key = os.environ.get("exerciseuploader")
        proxy = urllib.request.getproxies().get("https")
        if not self.key or not proxy or urllib.request.proxy_bypass(HOST):
            raise RuntimeError("Secret binding or supported HTTPS proxy route unavailable")
        self.opener = urllib.request.build_opener(urllib.request.ProxyHandler({"https": proxy}))

    def request(self, path, body=None, headers=None):
        # The sole POST endpoint lists objects; no mutation endpoint is permitted.
        if body is not None and path != "/storage/v1/object/list/" + BUCKET:
            raise RuntimeError("Only the read-only Storage list POST is allowed")
        if body is None and not (
            path.startswith("/rest/v1/") and "/rpc/" not in path
            or path == "/storage/v1/bucket"
            or path == "/auth/v1/admin/users?page=1&per_page=1"
        ):
            raise RuntimeError("Endpoint outside read-only audit scope")
        request_headers = {"apikey": self.key, "Accept": "application/json", **(headers or {})}
        data = None
        if body is not None:
            data = json.dumps(body).encode()
            request_headers["Content-Type"] = "application/json"
        request = urllib.request.Request(BASE + path, data=data, headers=request_headers,
                                         method="GET" if data is None else "POST")
        try:
            with self.opener.open(request, timeout=30) as response:
                return json.load(response), response.status, response.headers.get("Content-Range")
        except urllib.error.HTTPError as error:
            # Record status only: do not persist error bodies or credentials.
            return None, error.code, None
        except urllib.error.URLError as error:
            raise RuntimeError("HTTPS proxy/network request failed; no automatic retry") from error

    def table(self, name, select):
        rows, ranges, offset = [], [], 0
        while True:
            query = urllib.parse.urlencode({"select": select, "order": "id.asc",
                                             "limit": 500, "offset": offset})
            page, status, content_range = self.request(
                "/rest/v1/" + name + "?" + query, headers={"Prefer": "count=exact"})
            if status != 200 or not isinstance(page, list):
                raise RuntimeError("Table read failed: " + name + " HTTP " + str(status))
            ranges.append(content_range)
            rows.extend(page)
            if not page:
                break
            offset += len(page)
        return rows, ranges


def inspect_database():
    api = ReadOnlySupabase()
    schema, status, _ = api.request("/rest/v1/", headers={"Accept": "application/openapi+json"})
    if status != 200:
        raise RuntimeError("REST schema unavailable: HTTP " + str(status))
    admin, admin_status, _ = api.request("/auth/v1/admin/users?page=1&per_page=1")
    # Discard all user objects: only authorization evidence is retained.
    del admin
    buckets, bucket_status, _ = api.request("/storage/v1/bucket")
    if bucket_status != 200:
        raise RuntimeError("Bucket metadata unavailable")
    bucket = next(row for row in buckets if row["id"] == BUCKET)
    safe_bucket = {field: bucket.get(field) for field in
                   ("id", "public", "file_size_limit", "allowed_mime_types", "type")}
    tables, ranges = {}, {}
    selects = {
        "catalog_exercise": "*", "exercise": "id,owner_id,is_custom,deleted_at",
        "workout": "id,owner_id,deleted_at",
        "logged_exercise": "id,owner_id,exercise_id,workout_id,deleted_at",
        "set_entry": "id,owner_id,logged_exercise_id,deleted_at",
    }
    for name, select in selects.items():
        tables[name], ranges[name] = api.table(name, select)
    ids = {name: {row["id"]: row for row in rows} for name, rows in tables.items()}
    ci, ei, wi, li = (ids[name] for name in
                      ("catalog_exercise", "exercise", "workout", "logged_exercise"))
    relationships = {
        "custom_catalog_id_collisions": sum(eid in ci for eid in ei),
        "logged_unknown_exercise": sum(r["exercise_id"] not in ci and r["exercise_id"] not in ei for r in li.values()),
        "logged_unknown_workout": sum(r["workout_id"] not in wi for r in li.values()),
        "logged_workout_owner_mismatch": sum(r["workout_id"] in wi and r["owner_id"] != wi[r["workout_id"]]["owner_id"] for r in li.values()),
        "logged_custom_owner_mismatch": sum(r["exercise_id"] in ei and r["owner_id"] != ei[r["exercise_id"]]["owner_id"] for r in li.values()),
        "set_unknown_logged_exercise": sum(r["logged_exercise_id"] not in li for r in tables["set_entry"]),
        "set_logged_owner_mismatch": sum(r["logged_exercise_id"] in li and r["owner_id"] != li[r["logged_exercise_id"]]["owner_id"] for r in tables["set_entry"]),
    }
    _, metadata_status, _ = api.request("/rest/v1/", headers={"Accept-Profile": "pg_catalog"})
    objects, list_status, _ = api.request("/storage/v1/object/list/" + BUCKET,
                                         body={"prefix": "", "limit": 100, "offset": 0})
    catalog_schema = schema["definitions"]["catalog_exercise"]
    snapshot = {
        "checked_at_utc": datetime.now(timezone.utc).isoformat(),
        "project_ref": HOST.split(".")[0], "secret_binding_name": "exerciseuploader",
        "auth_admin_read_http": admin_status, "server_admin_read_confirmed": admin_status == 200,
        "postgrest_role_and_bypassrls_independently_verified": False,
        "catalog_actual_emptiness_independently_confirmed": False,
        "catalog_visible_rows": len(ci), "bucket": safe_bucket,
        "table_visible_rows": {name: len(rows) for name, rows in tables.items()},
        "table_content_ranges": ranges,
        "duplicate_ids": {name: len(tables[name]) - len(ids[name]) for name in tables},
        "relationship_checks_visible_rows_only": relationships,
        "pg_catalog_http": metadata_status, "storage_list_http": list_status,
        "storage_root_entries_visible": len(objects) if isinstance(objects, list) else None,
        "replaces_ids_rest_schema": catalog_schema["properties"]["replaces_ids"],
        "replaces_ids_required_in_openapi": "replaces_ids" in catalog_schema["required"],
        "replaces_ids_sql_default": "not_exposed_in_available_metadata",
        "schema_definitions": schema["definitions"],
        "application_code_available": False, "ordinary_client_access_verified": False,
        "supabase_writes": 0,
    }
    return snapshot, ci


def build_plan(online):
    pinned_sources()
    catalog_doc = read_json(ROOT / "data/exercises/catalog.json")
    catalog = {row["id"]: row for row in catalog_doc["exercises"]}
    if len(catalog) != 451 or len(catalog_doc["exercises"]) != 451:
        raise RuntimeError("Catalog IDs are missing or duplicated")
    language_blocks = sum(len(row["content"]) for row in catalog.values())
    if language_blocks != 4448:
        raise RuntimeError("Language block count changed")
    progress = read_json(ROOT / "data/exercise-image-progress.json")["exercises"]
    choices = candidates()
    snapshot, db = inspect_database() if online else ({"network_checks_run": False}, {})
    pngs = []
    for eid, state in sorted(progress.items()):
        if state.get("user_review") != "approved":
            continue
        sha = state.get("accepted_sha256")
        if not re.fullmatch(r"[a-z0-9-]+", eid) or not isinstance(sha, str) or not re.fullmatch(r"[0-9a-f]{64}", sha):
            raise RuntimeError("Invalid approved ID or accepted SHA256")
        if eid not in catalog or catalog[eid]["archived"]:
            raise RuntimeError("Approved source ID missing or archived: " + eid)
        matches = [(p, m) for p, m in choices.get((eid, sha), []) if (ROOT / p).is_file()]
        if not matches:
            raise RuntimeError("Accepted source PNG unavailable: " + eid)
        source, manifest = sorted(set(matches), key=lambda item: ("/pending/" in item[0], item))[0]
        check = verify_png(source, sha)
        destination = eid + "/" + sha + ".png"
        row = db.get(eid)
        issues = list(check["issues"])
        if online:
            if row is None:
                issues.append("database_record_not_visible")
            else:
                for field in DIRECT_FIELDS:
                    if row.get(field) != catalog[eid][field]:
                        issues.append("database_catalog_field_differs:" + field)
                if row.get("image_path") and (row["image_path"] != destination or row.get("image_sha256") != sha):
                    issues.append("existing_database_image_conflict")
        else:
            issues.append("database_not_checked_offline")
        pngs.append({
            "exercise_id": eid, "source_png": source, "source_manifest": manifest,
            "source_commit": SOURCE_COMMIT, "accepted_sha256": sha,
            "accepted_attempt": state.get("accepted_attempt"), "accepted_at": state.get("accepted_at"),
            "user_review": "approved", "recorded_technical_check": state.get("technical_check"),
            "recorded_technical_details": state.get("technical_check_details"),
            "byte_verification": check, "bucket": BUCKET, "destination_path": destination,
            "public_url": BASE + "/storage/v1/object/public/" + BUCKET + "/" + destination,
            "db_record": None if row is None else {"table": "catalog_exercise", "id": row["id"],
                "image_path": row.get("image_path"), "image_sha256": row.get("image_sha256"),
                "updated_at": row.get("updated_at")},
            "proposed_image_patch": {"image_path": destination, "image_sha256": sha,
                "image_width": check.get("width"), "image_height": check.get("height"),
                "image_origin": "generated"},
            "issues": issues,
        })
    ready = sum(row["byte_verification"]["ready_for_upload_bytes"] for row in pngs)
    bucket_matches = not online or (snapshot["bucket"]["public"] is True
        and snapshot["bucket"]["file_size_limit"] == SIZE_LIMIT
        and snapshot["bucket"]["allowed_mime_types"] == ["image/png"])
    summary = {
        "source_commit": SOURCE_COMMIT, "catalog_sha256": CATALOG_SHA256,
        "catalog_records": len(catalog), "language_blocks": language_blocks,
        "approved_pngs": len(pngs), "pngs_ready_by_bytes": ready,
        "png_bytes_total": sum(row["byte_verification"]["bytes"] for row in pngs),
        "largest_png_bytes": max(row["byte_verification"]["bytes"] for row in pngs),
        "dimension_counts": dict(Counter(str(row["byte_verification"].get("width")) + "x" + str(row["byte_verification"].get("height")) for row in pngs)),
        "recorded_technical_failed_preserved": [row["exercise_id"] for row in pngs if row["recorded_technical_check"] == "failed"],
        "generated_pending_excluded": sum(state.get("user_review") == "pending" and bool(state.get("result_sha256")) for state in progress.values()),
        "bucket_constraints_match": bucket_matches,
        "import_blockers": ["replaces_ids_semantics_default_and_values_unresolved",
            "catalog_actual_emptiness_not_independently_confirmed",
            "ordinary_client_read_permissions_unverified", "supabase_write_not_authorized"],
        "supabase_writes": 0, "png_uploads": 0,
    }
    if online:
        summary["approved_missing_visible_db_record"] = sum(row["db_record"] is None for row in pngs)
        summary["catalog_missing_visible_ids"] = len(set(catalog) - set(db))
        summary["database_extra_visible_ids"] = len(set(db) - set(catalog))
    if not bucket_matches:
        summary["import_blockers"].append("bucket_constraints_changed")
    if ready != len(pngs):
        summary["import_blockers"].append("approved_png_byte_checks_failed")
    catalog_plan = {
        "source_commit": SOURCE_COMMIT, "catalog_sha256": CATALOG_SHA256,
        "join": "catalog.json.exercises[].id = public.catalog_exercise.id",
        "replaces_ids": {"status": "unresolved", "payload_not_generated": True},
        "records": [{"exercise_id": eid, "archived": row["archived"],
                     "language_blocks": len(row["content"]), "content_sha256": canonical_digest(row["content"]),
                     "database_record_visible": eid in db if online else None}
                    for eid, row in sorted(catalog.items())],
    }
    return summary, pngs, catalog_plan, snapshot


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--offline", action="store_true", help="Verify source PNGs without Supabase reads")
    parser.add_argument("--output-dir", type=Path, help="Explicit local artifact output; never writes source files")
    args = parser.parse_args()
    summary, pngs, catalog_plan, snapshot = build_plan(not args.offline)
    if args.output_dir:
        output = args.output_dir.resolve()
        if not output.is_relative_to(ROOT / "integration" / "supabase"):
            raise RuntimeError("Output directory must be inside integration/supabase")
        output.mkdir(parents=True, exist_ok=True)
        for name, value in (("summary.json", summary), ("approved_png_plan.json", pngs),
                            ("catalog_import_plan.json", catalog_plan), ("access_audit.json", snapshot)):
            (output / name).write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 2 if summary["import_blockers"] else 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as error:
        secret = os.environ.get("exerciseuploader")
        message = str(error)
        if secret:
            message = message.replace(secret, "[REDACTED]")
        print("Dry-run failed: " + message, file=sys.stderr)
        sys.exit(1)
