"""Negative checks for integrity, transparency, pagination and read-only guards."""
import hashlib
import importlib.util
from pathlib import Path
import tempfile
import unittest

from PIL import Image

spec = importlib.util.spec_from_file_location("integration_dry_run", Path(__file__).with_name("dry_run.py"))
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class ImageIntegrityTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.old_root = module.ROOT
        module.ROOT = Path(self.directory.name)

    def tearDown(self):
        module.ROOT = self.old_root
        self.directory.cleanup()

    def png(self, opaque=False):
        path = module.ROOT / "source.png"
        Image.new("RGBA", (16, 16), (0, 0, 0, 255 if opaque else 0)).save(path)
        return path, hashlib.sha256(path.read_bytes()).hexdigest()

    def test_actual_transparency_and_dimensions(self):
        _, sha = self.png()
        result = module.verify_png("source.png", sha)
        self.assertTrue(result["ready_for_upload_bytes"])
        self.assertEqual(result["fully_transparent_pixels"], 256)
        self.assertEqual((result["width"], result["height"]), (16, 16))
        self.assertFalse(result["matches_historical_1024_target"])

    def test_unaccepted_hash_blocks_upload(self):
        self.png()
        result = module.verify_png("source.png", "0" * 64)
        self.assertIn("accepted_sha256_mismatch", result["issues"])
        self.assertFalse(result["ready_for_upload_bytes"])

    def test_alpha_channel_alone_is_insufficient(self):
        _, sha = self.png(opaque=True)
        result = module.verify_png("source.png", sha)
        self.assertTrue(result["has_alpha_or_transparency"])
        self.assertIn("no_actual_fully_transparent_pixels", result["issues"])

    def test_truncated_png_is_rejected_even_with_matching_hash(self):
        path, _ = self.png()
        path.write_bytes(path.read_bytes()[:20])
        result = module.verify_png("source.png", hashlib.sha256(path.read_bytes()).hexdigest())
        self.assertTrue(any(issue.startswith("png_decode_failed:") for issue in result["issues"]))

    def test_bucket_size_is_enforced(self):
        path, _ = self.png()
        path.write_bytes(path.read_bytes() + b"\0" * module.SIZE_LIMIT)
        result = module.verify_png("source.png", hashlib.sha256(path.read_bytes()).hexdigest())
        self.assertIn("bucket_size_limit_exceeded", result["issues"])


class ReadOnlyTests(unittest.TestCase):
    def test_mutation_and_rpc_endpoints_are_refused(self):
        client = object.__new__(module.ReadOnlySupabase)
        for endpoint, body in (("/rest/v1/catalog_exercise", {}),
                               ("/rest/v1/rpc/rls_auto_enable", None),
                               ("/storage/v1/object/exercise-images", {})):
            with self.subTest(endpoint=endpoint), self.assertRaises(RuntimeError):
                client.request(endpoint, body=body)

    def test_pagination_does_not_assume_server_page_size(self):
        client = object.__new__(module.ReadOnlySupabase)
        pages = iter(([{"id": "a"}, {"id": "b"}], [{"id": "c"}], []))
        queries = []

        def request(path, headers=None):
            queries.append(path)
            return next(pages), 200, None

        client.request = request
        rows, _ = client.table("catalog_exercise", "id")
        self.assertEqual([row["id"] for row in rows], ["a", "b", "c"])
        self.assertEqual(len(queries), 3)
        self.assertIn("offset=2", queries[1])
        self.assertIn("offset=3", queries[2])


if __name__ == "__main__":
    unittest.main()
