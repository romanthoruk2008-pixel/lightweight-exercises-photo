#!/usr/bin/env python3
"""Inspect only ZIP directory and the pinned source manifest using HTTPS ranges."""
import hashlib
import json
from pathlib import Path
import struct
import urllib.request
import zlib

ROOT = Path(__file__).resolve().parents[2]
source = json.loads((ROOT / "data/exercises/catalog.json").read_bytes())["source"]
url = source["release_url"].replace("/tag/", "/download/") + "/" + source["archive_name"]
with urllib.request.urlopen(urllib.request.Request(url, method="HEAD"), timeout=30) as response:
    size, direct = int(response.headers["Content-Length"]), response.url


def read_range(start, end):
    request = urllib.request.Request(direct, headers={"Range": f"bytes={start}-{end}"})
    with urllib.request.urlopen(request, timeout=30) as response:
        if response.status != 206:
            raise RuntimeError("Byte ranges unavailable; refusing a full archive download")
        if response.headers.get("Content-Range", "").split("/")[0] != f"bytes {start}-{end}":
            raise RuntimeError("Unexpected byte range")
        data = response.read(end - start + 2)
        if len(data) != end - start + 1:
            raise RuntimeError("Incomplete byte range")
        return data


tail = read_range(max(0, size - 65558), size - 1)
pos = tail.rfind(b"PK\x05\x06")
if pos < 0:
    raise RuntimeError("ZIP end record unavailable")
end = struct.unpack("<4s4H2IH", tail[pos:pos + 22])
if end[5] > 5 * 1024 * 1024:
    raise RuntimeError("ZIP directory exceeds inspection limit")
central = read_range(end[6], end[6] + end[5] - 1)
entries, pos = [], 0
while pos < len(central):
    header = struct.unpack("<4s6H3I5H2I", central[pos:pos + 46])
    if header[0] != b"PK\x01\x02":
        raise RuntimeError("Invalid ZIP directory")
    name = central[pos + 46:pos + 46 + header[10]].decode("utf-8")
    pos += 46 + header[10] + header[11] + header[12]
    entries.append({"path": name, "compressed_bytes": header[8], "bytes": header[9],
                    "method": header[4], "crc32": header[7], "offset": header[16]})
entry = next(item for item in entries if item["path"] == source["manifest_path_in_archive"])
if entry["bytes"] > 128 * 1024 * 1024:
    raise RuntimeError("Manifest exceeds inspection limit")
local = struct.unpack("<4s5H3I2H", read_range(entry["offset"], entry["offset"] + 29))
if local[0] != b"PK\x03\x04":
    raise RuntimeError("Invalid ZIP member header")
start = entry["offset"] + 30 + local[9] + local[10]
compressed = read_range(start, start + entry["compressed_bytes"] - 1)
if entry["method"] == 8:
    raw = zlib.decompress(compressed, -15)
elif entry["method"] == 0:
    raw = compressed
else:
    raise RuntimeError("Unsupported ZIP compression")
if len(raw) != entry["bytes"] or zlib.crc32(raw) & 0xffffffff != entry["crc32"]:
    raise RuntimeError("Manifest ZIP integrity check failed")
sha = hashlib.sha256(raw).hexdigest()
if sha != source["manifest_sha256"]:
    raise RuntimeError("Pinned source manifest SHA256 differs")
document = json.loads(raw)
keys = set()


def visit(value):
    if isinstance(value, dict):
        for key, child in value.items():
            if "replac" in key.lower():
                keys.add(key)
            visit(child)
    elif isinstance(value, list):
        for child in value:
            visit(child)


visit(document)
report = {
    "archive_bytes": size, "archive_entries": len(entries),
    "archive_full_sha256_verified": False,
    "method": "HTTPS byte-range reads; no media or tools extracted or executed",
    "manifest_path": entry["path"], "manifest_sha256": sha,
    "manifest_pinned_sha256_verified": True,
    "replacement_related_keys": sorted(keys), "contains_replaces_ids": b"replaces_ids" in raw,
    "schema_migration_file_candidates": [item["path"] for item in entries
        if not item["path"].startswith("__MACOSX/") and
        (item["path"].endswith(".sql") or "/migrations/" in item["path"])],
}
(ROOT / "integration/supabase/source_archive_inspection.json").write_text(
    json.dumps(report, indent=2) + "\n")
print(json.dumps(report, indent=2))
