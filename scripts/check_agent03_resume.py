#!/usr/bin/env python3
"""Read-only, exact-ID readiness check for the recovered 010–015 packages.

This calls the original preparation validator as a library, preserving its
branch guard and historical report. No preparation, generation or upload runs.
Only --save creates the separate current-task queue; shared progress is untouched.
"""
import argparse
import collections
import datetime
import hashlib
import json
from pathlib import Path
from zoneinfo import ZoneInfo

from PIL import Image
import prepare_agent03_other_completion as completion

ROOT = Path(__file__).resolve().parents[1]
PREPARATION_COMMIT = "d0e7bede47d8f21165015e74b00c58dafcadbe82"
QUEUE_PATH = ROOT / "data/queues/agent-03-resume-2026-10-02.json"
BATCH_PATHS = [f"data/batches/agent-03-others-{n:03}.json" for n in range(10, 16)]


def check():
    base = completion.base
    completion.configure()
    # Additions are byte-identical copies of the pinned preparation commit.
    for path in BATCH_PATHS:
        if (ROOT / path).read_bytes() != base.git("show", PREPARATION_COMMIT + ":" + path):
            raise ValueError("Recovered batch differs from pinned source: " + path)
    snapshot = completion.snapshot()
    batches = [completion.load(path) for path in BATCH_PATHS]
    queue = completion.load(base.QUEUE_PATH)
    review = completion.load(completion.REVIEW_PATH)
    blocked = completion.load(completion.BLOCKED_PATH)
    # The live work files, rather than the historical preparation-branch
    # progress, are authoritative. Capture them before the read-only validator.
    protected = completion.freeze()
    report = completion.validate(snapshot, queue, batches, review, blocked, protected)
    catalog = snapshot["catalog"]["exercises"]
    counts = {
        "records": len(catalog),
        "active": sum(not r["archived"] for r in catalog),
        "archived": sum(bool(r["archived"]) for r in catalog),
        "language_blocks": sum(len(r["content"]) for r in catalog),
    }
    if counts != {"records": 451, "active": 448, "archived": 3, "language_blocks": 4448}:
        report["errors"].append("unexpected_catalog_counts")
    reference = ROOT / snapshot["reference_path"]
    reference_sha = hashlib.sha256(reference.read_bytes()).hexdigest()
    progress = json.loads((ROOT / base.PROGRESS_PATH).read_text())
    accepted = progress["exercises"]["biceps-curl-dumbbell"]
    approved_manifest = completion.load("data/approved-images-manifest.json")
    manifest_reference = next(r for r in approved_manifest["images"] if r["exercise_id"] == "biceps-curl-dumbbell")
    if accepted["user_review"] != "approved" or accepted["accepted_sha256"] != reference_sha or manifest_reference["sha256"] != reference_sha:
        report["errors"].append("accepted_reference_mismatch")
    with Image.open(reference) as im:
        im.load()
        reference_details = {"format": im.format, "dimensions": list(im.size), "mode": im.mode}
        reference_details["transparent_pixels"] = im.getchannel("A").histogram()[0]
        if im.format != "PNG" or im.width != im.height or not reference_details["transparent_pixels"]:
            report["errors"].append("reference_decode_or_alpha_failure")

    # Metadata/tree checks cover all fetched other-agent branches; no library
    # image decoding or pixel audit is performed. Include local untracked PNGs.
    selected = {r["exercise_id"] for b in batches for r in b["exercises"]}
    local_pngs = collections.defaultdict(list)
    for path in (ROOT / "assets/exercises").rglob("*.png"):
        eid = path.parent.name if path.name.startswith("attempt-") else path.stem
        if eid in selected:
            local_pngs[eid].append(str(path.relative_to(ROOT)))
    packages = []
    excluded = []
    for path, batch in zip(BATCH_PATHS, batches):
        items = []
        for row in batch["exercises"]:
            eid = row["exercise_id"]
            current = progress["exercises"][eid]
            reasons = []
            if current.get("user_review") in ("approved", "rejected") or current.get("status") in ("approved", "uploaded", "rejected", "needs_fix"):
                reasons.append("review_or_fix_requires_exclusion")
            if current.get("status") != "not_started" or current.get("attempts") or current.get("attempt_history"):
                reasons.append("already_touched")
            if current.get("result_path") or current.get("accepted_path") or snapshot["png_sources"].get(eid) or local_pngs.get(eid):
                reasons.append("existing_result")
            if snapshot["reserved"].get(eid):
                reasons.append("existing_assignment")
            if snapshot["classifications"][eid] != "other":
                reasons.append("machine_cable_smith_or_ambiguous")
            output = f"assets/exercises/pending/{batch['batch_id']}/{eid}/attempt-1.png"
            if (ROOT / output).exists():
                reasons.append("output_path_occupied")
            item = {
                "exercise_id": eid,
                "name": row["name"],
                "batch_path": path,
                "record_lookup": "exercises[exercise_id=" + eid + "]",
                "generation_prompt_sha256": row["generation_prompt_sha256"],
                "source_catalog_record_sha256": row["source_catalog_record_sha256"],
                "source_english_sha256": row["source_english_sha256"],
                "current_progress_status": current["status"],
                "current_attempts": current["attempts"],
                "output_repository_path": output,
                "eligibility": "excluded" if reasons else "ready_awaiting_user_command",
                "exclusion_reasons": reasons,
            }
            (excluded if reasons else items).append(item)
        packages.append({"batch_id": batch["batch_id"], "batch_path": path, "prepared_count": len(batch["exercises"]), "remaining_count": len(items), "items": items})
    old009 = completion.load("data/batches/agent-03-others-009.json")
    old009_remaining = [eid for eid in old009["exercise_ids"] if not snapshot["png_sources"].get(eid)]
    if selected & (set(old009["exercise_ids"]) | set(blocked["exercise_ids"])):
        report["errors"].append("overlap_with_excluded_009_or_blocked")
    if completion.freeze() != protected:
        report["errors"].append("protected_file_changed_during_check")
    status = "failed" if report["errors"] else "passed"
    result = {
        "schema_version": 1,
        "task": "Lightweight cloud recovery; preparation only",
        "checked_at": datetime.datetime.now(ZoneInfo("Europe/Kiev")).isoformat(),
        "generation_authorized_now": False,
        "generation_calls": 0,
        "source_preparation_commit": PREPARATION_COMMIT,
        "source_commits": snapshot["commits"],
        "catalog_counts": counts,
        "catalog_sha256": snapshot["catalog_sha256"],
        "live_progress_sha256": protected[base.PROGRESS_PATH],
        "style_version": "v1",
        "style_sha256": snapshot["style_sha256"],
        "reference": {"repository_path": snapshot["reference_path"], "accepted_sha256": reference_sha, "role": "appearance/proportions/materials/detail only", "pixels_opened_by_agent": True, **reference_details},
        "validation": {"status": status, "errors": report["errors"], "checks": report["checks"]},
        "scope": "010–015 exact IDs only; existing PNGs checked by tree/path metadata, only reference decoded",
        "prepared_count": len(selected),
        "remaining_count": sum(p["remaining_count"] for p in packages),
        "packages": packages,
        "excluded": excluded,
        "excluded_previous_009_ids": old009_remaining,
        "excluded_blocked_count": blocked["exercise_count"],
        "limitations": ["Other tasks' unpushed files/reservations are not observable.", "Imagegen presence is confirmed; quota is untested because generation is forbidden now."],
        "current_user_overrides": {
            "result_root": "assets/exercises/pending/<batch_id>/<exercise_id>/attempt-1.png",
            "preserve_original_batch_prompts_and_source_files": True,
            "no_automatic_retry_resize_crop_or_visual_QA": True,
            "user_review": "pending",
            "agent_visual_review": "not_performed",
            "technical_failure_status": "needs_fix",
            "supabase_allowed": False,
        },
    }
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--save", action="store_true", help="Create the separate resume queue, never overwrite it.")
    args = parser.parse_args()
    result = check()
    if args.save:
        if result["validation"]["status"] != "passed":
            raise SystemExit("Readiness validation failed; queue not saved.")
        with QUEUE_PATH.open("x") as out:
            json.dump(result, out, ensure_ascii=False, indent=2)
            out.write("\n")
    print(json.dumps({"validation": result["validation"], "prepared_count": result["prepared_count"], "remaining_count": result["remaining_count"], "packages": [{k: p[k] for k in ("batch_id", "remaining_count")} for p in result["packages"]], "excluded": result["excluded"], "reference": result["reference"], "source_commits": result["source_commits"]}, ensure_ascii=False, indent=2))
    if result["validation"]["status"] != "passed":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
