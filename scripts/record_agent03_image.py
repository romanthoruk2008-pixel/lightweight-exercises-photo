#!/usr/bin/env python3
"""Record one explicitly authorized Agent-03 image call and its file checks."""
import argparse
import datetime
import hashlib
import json
import shutil
import subprocess
from pathlib import Path
from zoneinfo import ZoneInfo

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
QUEUE = ROOT / "data/queues/agent-03-resume-2026-10-02.json"
PROGRESS = ROOT / "data/exercise-image-progress.json"
MANIFEST = ROOT / "data/batches/agent-03-others-manifest.json"
RUN_ID = "lightweight-agent-03-others-010-015-2026-10-02"


def load(path):
    return json.loads(path.read_text())


def save(path, value):
    temp = path.with_suffix(path.suffix + ".tmp")
    temp.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n")
    temp.replace(path)


def now():
    return datetime.datetime.now(ZoneInfo("Europe/Kiev")).isoformat()


def git(*args):
    return subprocess.check_output(["git", *args], cwd=ROOT).decode().strip()


def verify_no_result_or_assignment(eid, output):
    if output.exists():
        raise ValueError("Output path already occupied; do not overwrite: " + str(output))
    local_pngs = []
    for path in (ROOT / "assets/exercises").rglob("*.png"):
        if path.parent.name == eid or path.stem == eid:
            local_pngs.append(path)
    if local_pngs:
        raise ValueError("An exercise PNG already exists locally; do not regenerate: " + str(local_pngs[0]))
    refs = git("for-each-ref", "--format=%(refname:short)", "refs/remotes/origin").splitlines()
    for ref in refs:
        for path in git("ls-tree", "-r", "--name-only", ref).splitlines():
            if not path.endswith(".png"):
                continue
            tail = path.split("/")[-1]
            existing_id = path.split("/")[-2] if tail.startswith("attempt-") else Path(tail).stem
            if existing_id == eid:
                raise ValueError("An exercise PNG already exists on " + ref + ": " + path)
    # Queued work on other agents' branches is a reservation even before a PNG
    # exists. Skip this run's six explicitly assigned Agent-03 source batches.
    for ref in refs:
        for path in git("ls-tree", "-r", "--name-only", ref).splitlines():
            if not path.startswith("data/batches/") or not path.endswith(".json"):
                continue
            doc = json.loads(subprocess.check_output(["git", "show", ref + ":" + path], cwd=ROOT))
            if doc.get("owner_agent") == "agent-03" and doc.get("batch_id", "").startswith("agent-03-others-"):
                continue
            if any(row.get("exercise_id") == eid for row in doc.get("exercises", []) if isinstance(row, dict)):
                if doc.get("generation_authorized_now") is True or doc.get("status") in ("active", "in_progress", "assigned"):
                    raise ValueError("Exercise assigned to other active work in " + ref + ": " + path)


def begin(eid, call_index):
    queue = load(QUEUE)["packages"]
    row = next((item for package in queue for item in package["items"] if item["exercise_id"] == eid), None)
    if row is None or row["eligibility"] != "ready_awaiting_user_command":
        raise ValueError("ID is absent from the ready exact-ID queue: " + eid)
    batch_path = ROOT / row["batch_path"]
    batch = load(batch_path)
    source = next(item for item in batch["exercises"] if item["exercise_id"] == eid)
    target = ROOT / row["output_repository_path"]
    progress = load(PROGRESS)
    state = progress["exercises"][eid]
    if state["status"] != "not_started" or state["attempts"] != 0 or state["attempt_history"] or state.get("result_path") or state.get("accepted_path"):
        raise ValueError("Live progress changed; do not generate this ID: " + eid)
    verify_no_result_or_assignment(eid, target)
    timestamp = now()
    reference_sha = source["human_reference"]["sha256"]
    if hashlib.sha256((ROOT / source["human_reference"]["repository_path"]).read_bytes()).hexdigest() != reference_sha:
        raise ValueError("Human-reference SHA256 changed; stop before generation.")
    history = {
        "attempt": 1,
        "id": eid,
        "batch_id": batch["batch_id"],
        "run_id": RUN_ID,
        "style_version": "v1",
        "tool": "image_gen.imagegen",
        "tool_call_index": call_index,
        "status": "in_progress",
        "started_at": timestamp,
        "prompt": source["generation_prompt"],
        "prompt_sha256": source["generation_prompt_sha256"],
        "reference_path": source["human_reference"]["repository_path"],
        "reference_sha256": reference_sha,
        "result_path": row["output_repository_path"],
    }
    state.update(status="in_progress", attempts=1, style_version="v1", last_error=None)
    state["attempt_history"].append(history)
    save(PROGRESS, progress)
    manifest = load(MANIFEST)
    if any(item["exercise_id"] == eid for item in manifest["exercises"]):
        raise ValueError("Manifest already has an entry for " + eid)
    manifest["exercises"].append({
        "exercise_id": eid, "name": source["name"], "batch_id": batch["batch_id"],
        "status": "in_progress", "attempt": 1, "style_version": "v1",
        "prompt": source["generation_prompt"], "prompt_sha256": source["generation_prompt_sha256"],
        "result_path": row["output_repository_path"], "cloud_output_path": str(target),
        "result_sha256": None, "dimensions": None, "mime_type": None,
        "generated_at": timestamp, "technical_check": None, "user_review": "pending",
        "agent_visual_review": "not_performed", "backup_status": "local_generation_in_progress",
        "source_catalog_sha256": source["source_catalog_sha256"],
        "source_catalog_record_sha256": source["source_catalog_record_sha256"],
        "source_english_sha256": source["source_english_sha256"],
        "tool_call_index": call_index, "branches_checked": refs_for_metadata(),
        "technical_check_details": None, "tool_response_metadata": None,
        "verified_commit": None, "verified_at": None,
        "reference_path": source["human_reference"]["repository_path"],
        "reference_sha256": reference_sha,
    })
    save(MANIFEST, manifest)
    print(json.dumps({"started": eid, "batch_id": batch["batch_id"], "prompt_sha256": history["prompt_sha256"], "reference_sha256": reference_sha, "result_path": history["result_path"], "tool_call_index": call_index}))


def refs_for_metadata():
    return ["work"]


def complete(eid, call_index, source_path, tool_call_id):
    queue = load(QUEUE)
    selected = next(item for package in queue["packages"] for item in package["items"] if item["exercise_id"] == eid)
    target = ROOT / selected["output_repository_path"]
    source_path = Path(source_path).resolve(strict=True)
    generated_root = Path("/workspace/generated_images").resolve()
    if not source_path.is_relative_to(generated_root) or source_path.suffix.lower() != ".png":
        raise ValueError("Imagegen output hint is outside the cloud generated_images directory or is not PNG.")
    target.parent.mkdir(parents=True, exist_ok=True)
    if source_path != target.resolve(strict=False):
        with source_path.open("rb") as src, target.open("xb") as dst:
            shutil.copyfileobj(src, dst)
    elif not target.is_file():
        raise ValueError("Direct image stream did not create the target PNG.")
    digest = hashlib.sha256(target.read_bytes()).hexdigest()
    errors = []
    try:
        with Image.open(target) as image:
            image.load()
            fmt, width, height, mode = image.format, image.width, image.height, image.mode
            has_alpha = "A" in image.getbands()
            transparent_pixels = image.getchannel("A").histogram()[0] if has_alpha else 0
            if fmt != "PNG": errors.append("not_png")
            if width != height: errors.append("not_square")
            if not has_alpha or transparent_pixels == 0: errors.append("no_transparent_pixels")
            details = {"format": fmt, "dimensions": {"width": width, "height": height}, "mode": mode,
                       "has_alpha": has_alpha, "transparent_pixel_count": transparent_pixels,
                       "sha256": digest, "exercise_id": eid, "repository_path": selected["output_repository_path"],
                       "errors": errors}
    except Exception as error:
        details = {"format": None, "dimensions": None, "sha256": digest, "exercise_id": eid,
                   "repository_path": selected["output_repository_path"], "errors": ["png_decode_failed:" + str(error)]}
        errors = details["errors"]
    technical = "failed" if errors else "passed"
    final_status = "needs_fix" if errors else "generated"
    progress = load(PROGRESS)
    state = progress["exercises"][eid]
    history = next(item for item in state["attempt_history"] if item["tool_call_index"] == call_index)
    timestamp = now()
    history.update(status="completed", completed_at=timestamp, result_sha256=digest,
                   result_path=selected["output_repository_path"], dimensions=details["dimensions"],
                   technical_check=technical, technical_check_details=details,
                   tool_response_metadata={"tool_call_id": tool_call_id, "output_hint": str(source_path)})
    state.update(status=final_status, style_version="v1", result_path=selected["output_repository_path"],
                 result_sha256=digest, technical_check=technical, technical_check_details=details,
                 agent_visual_review="not_performed", agent_visual_review_notes=None,
                 user_review="pending", last_error=None if not errors else ";".join(errors))
    save(PROGRESS, progress)
    manifest = load(MANIFEST)
    entry = next(item for item in manifest["exercises"] if item["exercise_id"] == eid)
    entry.update(status=final_status, result_sha256=digest,
                 dimensions=details.get("dimensions"), mime_type="image/png" if details.get("format") == "PNG" else None,
                 generated_at=timestamp, technical_check=technical, user_review="pending",
                 agent_visual_review="not_performed", backup_status="local_saved",
                 technical_check_details=details,
                 tool_response_metadata={"tool_call_id": tool_call_id, "output_hint": str(source_path)})
    save(MANIFEST, manifest)
    selected.update(eligibility="needs_fix" if errors else "generated_local", result_sha256=digest,
                    dimensions=details.get("dimensions"), technical_check=technical, completed_at=timestamp)
    save(QUEUE, queue)
    print(json.dumps({"exercise_id": eid, "status": final_status, "technical_check": technical,
                      "errors": errors, "sha256": digest, "dimensions": details.get("dimensions"),
                      "transparent_pixels": details.get("transparent_pixel_count"),
                      "result_path": selected["output_repository_path"], "tool_call_id": tool_call_id}))
    if errors:
        raise SystemExit(2)


def failure(eid, call_index, code, message):
    progress = load(PROGRESS)
    state = progress["exercises"][eid]
    history = next(item for item in state["attempt_history"] if item["tool_call_index"] == call_index)
    timestamp = now()
    status = "blocked_quota" if "429" in code or "quota" in (code + message).lower() or "usage_limit" in message.lower() else "generation_failed"
    history.update(status=status, completed_at=timestamp, error_code=code, error_message=message)
    state.update(status=status, last_error={"code": code, "message": message})
    save(PROGRESS, progress)
    manifest = load(MANIFEST)
    entry = next(item for item in manifest["exercises"] if item["exercise_id"] == eid)
    entry.update(status=status, backup_status="no_file", tool_response_metadata={"error_code": code, "error_message": message})
    save(MANIFEST, manifest)
    queue = load(QUEUE)
    selected = next(item for package in queue["packages"] for item in package["items"] if item["exercise_id"] == eid)
    selected.update(eligibility=status, error_code=code, error_message=message)
    save(QUEUE, queue)
    print(json.dumps({"exercise_id": eid, "status": status, "result_path": None, "error_code": code, "error_message": message}))


def main():
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command", required=True)
    start = sub.add_parser("begin"); start.add_argument("exercise_id"); start.add_argument("--call-index", type=int, required=True)
    finish = sub.add_parser("complete"); finish.add_argument("exercise_id"); finish.add_argument("--call-index", type=int, required=True); finish.add_argument("--source", required=True); finish.add_argument("--tool-call-id", default="unavailable")
    fail = sub.add_parser("failure"); fail.add_argument("exercise_id"); fail.add_argument("--call-index", type=int, required=True); fail.add_argument("--code", required=True); fail.add_argument("--message", required=True)
    args = parser.parse_args()
    if args.command == "begin": begin(args.exercise_id, args.call_index)
    elif args.command == "complete": complete(args.exercise_id, args.call_index, args.source, args.tool_call_id)
    else: failure(args.exercise_id, args.call_index, args.code, args.message)


if __name__ == "__main__":
    main()
