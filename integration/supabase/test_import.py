"""Exercise upload ordering, no-overwrite, server defaults and resume offline."""
import copy
import io
import json
from pathlib import Path
import sys
import tempfile
import unittest

from PIL import Image

sys.path.insert(0, str(Path(__file__).parent))
import import_catalog_images as importer


class FakeApi:
    key = "test-only-placeholder"

    def __init__(self, row, raw):
        self.current = copy.deepcopy(row)
        self.expected = raw
        self.stored = None
        self.corrupt_public = False
        self.calls = []

    def row(self, eid):
        return copy.deepcopy(self.current)

    def public(self, path, existence_check=False):
        self.calls.append("existence" if existence_check else "public")
        if self.stored is None:
            return b'{"statusCode":"404","error":"not_found"}', 400, {"Content-Type": "application/json"}
        return (b"corrupt" if self.corrupt_public and not existence_check else self.stored), 200, {"Content-Type": "image/png"}

    def require(self, method, path, payload=None, headers=None):
        self.calls.append(method)
        if method == "POST":
            assert headers["x-upsert"] == "false"
            assert self.stored is None
            self.stored = payload
            return b"{}", 200, {}
        if method == "PATCH":
            assert "public" in self.calls
            self.current.update(payload)
            return json.dumps([self.current]).encode(), 200, {}
        raise AssertionError("Unexpected fake operation")


class TransferTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.original_root = importer.source.ROOT
        importer.source.ROOT = Path(self.tmp.name)
        path = importer.source.ROOT / "assets/exercises/sample.png"
        path.parent.mkdir(parents=True)
        Image.new("RGBA", (16, 16), (0, 0, 0, 0)).save(path)
        raw = path.read_bytes()
        sha = importer.source.digest(raw)
        self.original = {"id": "sample", "name": "Sample", "equipment": "none",
            "primary_muscle": "core", "secondary_muscles": [], "tracking_type": "reps",
            "archived": False, "content": {"en": {"description": "unchanged"}}}
        row = {**self.original, "updated_at": "2026-10-02T00:00:00+00:00",
               **{field: None for field in importer.IMAGE_FIELDS}}
        destination = "sample/" + sha + ".png"
        self.item = {"exercise_id": "sample", "accepted_sha256": sha, "destination_path": destination,
            "source_png": "assets/exercises/sample.png", "public_url": "public-url",
            "proposed_image_patch": {"image_path": destination, "image_sha256": sha,
                "image_width": 16, "image_height": 16, "image_origin": "generated"}}
        self.api = FakeApi(row, raw)

    def tearDown(self):
        importer.source.ROOT = self.original_root
        self.tmp.cleanup()

    def test_public_hash_must_pass_before_database_update(self):
        result = importer.transfer_one(self.api, self.item, self.original, None)
        self.assertEqual(result["status"], "complete")
        self.assertLess(self.api.calls.index("public"), self.api.calls.index("PATCH"))
        self.assertEqual(self.api.current["content"], self.original["content"])

    def test_resume_verified_transfer_performs_no_writes(self):
        first = importer.transfer_one(self.api, self.item, self.original, None)
        writes = self.api.calls.count("POST") + self.api.calls.count("PATCH")
        second = importer.transfer_one(self.api, self.item, self.original, first)
        self.assertTrue(second["resume_skipped"])
        self.assertEqual(self.api.calls.count("POST") + self.api.calls.count("PATCH"), writes)

    def test_existing_different_object_is_never_overwritten(self):
        self.api.stored = b"different-object"
        with self.assertRaises(RuntimeError):
            importer.transfer_one(self.api, self.item, self.original, None)
        self.assertNotIn("POST", self.api.calls)
        self.assertNotIn("PATCH", self.api.calls)

    def test_bad_download_after_upload_blocks_database_link(self):
        self.api.corrupt_public = True
        with self.assertRaises(RuntimeError):
            importer.transfer_one(self.api, self.item, self.original, None)
        self.assertIn("POST", self.api.calls)
        self.assertNotIn("PATCH", self.api.calls)

    def test_existing_different_database_image_is_preserved(self):
        self.api.current["image_path"] = "someone-else.png"
        with self.assertRaises(RuntimeError):
            importer.transfer_one(self.api, self.item, self.original, None)
        self.assertNotIn("POST", self.api.calls)
        self.assertNotIn("PATCH", self.api.calls)


class DefaultAndScopeTests(unittest.TestCase):
    def test_incomplete_manifest_cannot_produce_success_summary(self):
        with tempfile.TemporaryDirectory() as temp:
            old = importer.OUTPUT
            importer.OUTPUT = Path(temp)
            try:
                (importer.OUTPUT / "batch-001.json").write_text(json.dumps({"status": "complete", "entries": {}}))
                with self.assertRaises(RuntimeError):
                    importer.write_summary({}, [])
                self.assertFalse((importer.OUTPUT / "summary.json").exists())
            finally:
                importer.OUTPUT = old

    def test_mutations_cannot_touch_user_tables_schema_or_other_objects(self):
        api = object.__new__(importer.Api)
        api.apply = True
        api.paths = {"approved/hash.png"}
        attempts = (("POST", "/rest/v1/exercise"), ("PATCH", "/rest/v1/workout?id=eq.some-id"),
                    ("POST", "/rest/v1/rpc/rls_auto_enable"),
                    ("POST", "/storage/v1/object/exercise-images/unapproved/hash.png"),
                    ("DELETE", "/storage/v1/object/exercise-images/approved/hash.png"))
        for method, path in attempts:
            with self.subTest(method=method, path=path), self.assertRaises(RuntimeError):
                api.request(method, path, {})

    def test_read_only_api_cannot_write_even_authorized_catalog_endpoint(self):
        api = object.__new__(importer.Api)
        api.apply = False
        api.paths = set()
        with self.assertRaises(RuntimeError):
            api.request("POST", "/rest/v1/catalog_exercise", [])

    def test_missing_object_detection_does_not_confuse_permission_denial(self):
        self.assertTrue(importer.is_missing_object(400, b'{"statusCode":"404"}'))
        self.assertFalse(importer.is_missing_object(403, b'{"statusCode":"403"}'))
        self.assertFalse(importer.is_missing_object(400, b'{"statusCode":"401"}'))
        self.assertFalse(importer.is_missing_object(404, b"proxy error"))

    def test_patches_include_concurrency_and_exact_old_image_filters(self):
        row = {"id": "sample", "updated_at": "2026-10-02T00:00:00+00:00",
               **{field: None for field in importer.IMAGE_FIELDS}}
        path = importer.patch_filter(row)
        self.assertIn("id=eq.sample", path)
        self.assertIn("updated_at=eq.", path)
        for field in importer.IMAGE_FIELDS:
            self.assertIn(field + "=is.null", path)

    def test_catalog_defaults_and_resume_without_any_upsert(self):
        catalog = importer.source.read_json(importer.source.ROOT / "data/exercises/catalog.json")
        originals = {row["id"]: row for row in catalog["exercises"]}
        seeds = [{field: row[field] for field in importer.source.DIRECT_FIELDS} for row in originals.values()]
        for row in seeds:
            row.update({field: None for field in importer.IMAGE_FIELDS})

        class CatalogApi:
            current = {}
            writes = 0

            def catalog(self):
                return copy.deepcopy(self.current)

            def require(self, method, path, payload, headers):
                assert method == "POST" and path == "/rest/v1/catalog_exercise"
                assert headers["Prefer"] == "missing=default,return=minimal"
                for row in payload:
                    assert "replaces_ids" not in row and row["id"] not in self.current
                    self.current[row["id"]] = {**copy.deepcopy(row), "replaces_ids": []}
                self.writes += 1
                return b"", 201, {}

        api = CatalogApi()
        with tempfile.TemporaryDirectory() as temp:
            output = importer.OUTPUT
            importer.OUTPUT = Path(temp)
            try:
                first = importer.import_catalog(api, originals, seeds)
                count = api.writes
                second = importer.import_catalog(api, originals, seeds)
                self.assertEqual(first["verification"]["language_blocks"], 4448)
                self.assertEqual(second["newly_inserted_on_this_run"], 0)
                self.assertEqual(api.writes, count)
            finally:
                importer.OUTPUT = output


if __name__ == "__main__":
    unittest.main()
