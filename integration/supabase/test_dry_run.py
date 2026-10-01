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


class SqlEvidenceTests(unittest.TestCase):
    def evidence(self, rls=False):
        return {
            "project_ref": module.HOST.split(".")[0],
            "catalog_count_result": {"editor_role": "postgres",
                "rls_applies_to_editor": rls, "catalog_row_count": 0},
            "replaces_ids_column_result": {"sql_type": "jsonb", "not_null": True,
                "column_default": "'[]'::jsonb", "description": None},
            "check_constraints_result": {"count": 8, "full_definitions": None},
        }

    def test_sql_count_without_rls_confirms_empty_but_not_semantics(self):
        result = module.evaluate_sql_evidence(self.evidence())
        self.assertTrue(result["catalog_empty_confirmed"])
        self.assertTrue(result["column_default_confirmed"])
        self.assertEqual(result["replaces_ids_semantics"], "unknown")
        self.assertFalse(result["full_check_definitions_available"])

    def test_zero_count_with_rls_does_not_confirm_empty(self):
        self.assertFalse(module.evaluate_sql_evidence(self.evidence(rls=True))["catalog_empty_confirmed"])

    def test_different_project_evidence_is_refused(self):
        evidence = self.evidence()
        evidence["project_ref"] = "another-project"
        with self.assertRaises(RuntimeError):
            module.evaluate_sql_evidence(evidence)

    def test_missing_sql_evidence_remains_unconfirmed(self):
        result = module.evaluate_sql_evidence(None)
        self.assertFalse(result["catalog_empty_confirmed"])
        self.assertFalse(result["column_default_confirmed"])

    def test_unreviewed_check_definition_does_not_use_known_validator(self):
        evidence = module.read_json(module.ROOT / "integration/supabase/sql_editor_evidence.json")
        evidence["check_constraints_result"]["full_definitions"][0]["definition"] = "CHECK (false)"
        result = module.evaluate_sql_evidence(evidence)
        self.assertTrue(result["full_check_definitions_available"])
        self.assertFalse(result["check_definitions_supported_by_validator"])


class ConstraintTests(unittest.TestCase):
    def row(self):
        return {"id": "sample-exercise", "content": {"en": {}},
                "secondary_muscles": [], "replaces_ids": [],
                "image_path": None, "image_sha256": None, "image_width": None,
                "image_height": None, "image_origin": None}

    def test_seed_without_images_passes_nullable_image_checks(self):
        self.assertEqual(module.constraint_violations(self.row()), [])

    def test_partial_image_link_is_rejected(self):
        row = self.row()
        row["image_path"] = "sample.png"
        self.assertIn("catalog_exercise_image_all_or_nothing", module.constraint_violations(row))

    def test_invalid_catalog_content_slug_and_lists_are_rejected(self):
        row = self.row()
        row.update({"id": "sample--exercise", "content": {"uk": {}}, "replaces_ids": {}})
        failed = module.constraint_violations(row)
        self.assertIn("catalog_exercise_id_is_slug", failed)
        self.assertIn("catalog_exercise_has_english", failed)
        self.assertIn("catalog_exercise_lists_are_arrays", failed)

    def test_gym_visual_origin_requires_actual_credit(self):
        row = self.row()
        row.update({"image_path": "sample.png", "image_sha256": "a" * 64,
                    "image_width": 1254, "image_height": 1254, "image_origin": "gym_visual_edit"})
        self.assertIn("catalog_exercise_gym_visual_is_credited", module.constraint_violations(row))
        row["attribution"] = "Verified source credit"
        self.assertEqual(module.constraint_violations(row), [])

    def test_generated_accepted_non_square_image_is_allowed_by_sql(self):
        row = self.row()
        row.update({"image_path": "sample.png", "image_sha256": "a" * 64,
                    "image_width": 1536, "image_height": 1024, "image_origin": "generated"})
        self.assertEqual(module.constraint_violations(row), [])


if __name__ == "__main__":
    unittest.main()
