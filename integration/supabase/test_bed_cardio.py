"""Bed Cardio: exact source, single-row authorization, and conflict safety."""
import copy
import json
import unittest
from unittest.mock import patch

import import_bed_cardio as bed


class BedCardioTests(unittest.TestCase):
    def api(self):
        api = object.__new__(bed.BedCardioApi)
        api.paths = {'bed-cardio/'+'a'*64+'.png'}
        return api

    def test_pinned_source_preserves_latest_meme_and_all_eight_full_languages(self):
        row, source = bed.load_source()
        self.assertEqual(row['id'], 'bed-cardio')
        self.assertEqual(set(row['content']), {'en', 'uk', 'es', 'it', 'tr', 'fr', 'ru', 'pl'})
        self.assertEqual(row['tracking_type'], 'duration')
        self.assertIn('pillows instead of dumbbells', row['content']['en']['description'])
        self.assertEqual(row['content']['uk']['name'], 'Кардіо в ліжку')
        self.assertTrue(source['metadata_hashes_verified'])

    def test_bulk_and_other_id_inserts_are_blocked_before_transport(self):
        for payload in [[{'id': 'other'}], [{'id': 'bed-cardio'}, {'id': 'other'}],
                        [{'id': 'bed-cardio', 'replaces_ids': ['guessed']}]]:
            with self.subTest(payload=payload), patch.object(bed.legacy.Api, 'request') as request:
                with self.assertRaises(RuntimeError):
                    self.api().request('POST', '/rest/v1/catalog_exercise', payload)
                request.assert_not_called()

    def test_patch_requires_exact_id_updated_at_and_scoped_columns(self):
        cases = [('/rest/v1/catalog_exercise?id=eq.other&updated_at=eq.time', {'name': 'x'}),
                 ('/rest/v1/catalog_exercise?id=eq.bed-cardio', {'name': 'x'}),
                 ('/rest/v1/catalog_exercise?updated_at=eq.time', {'name': 'x'}),
                 ('/rest/v1/catalog_exercise?id=eq.bed-cardio&updated_at=eq.time', {'id': 'other'}),
                 ('/rest/v1/catalog_exercise?id=eq.bed-cardio&updated_at=eq.time', {'replaces_ids': []})]
        for path, payload in cases:
            with self.subTest(path=path), patch.object(bed.legacy.Api, 'request') as request:
                with self.assertRaises(RuntimeError):
                    self.api().request('PATCH', path, payload)
                request.assert_not_called()

    def test_storage_overwrite_other_exercise_and_unselected_hash_are_blocked(self):
        cases = [('other/'+'a'*64+'.png', {'x-upsert': 'false'}),
                 ('bed-cardio/'+'b'*64+'.png', {'x-upsert': 'false'}),
                 ('bed-cardio/'+'a'*64+'.png', {'x-upsert': 'true'})]
        for path, headers in cases:
            with self.subTest(path=path), patch.object(bed.legacy.Api, 'request') as request:
                with self.assertRaises(RuntimeError):
                    self.api().request('POST', '/storage/v1/object/exercise-images/'+path, b'PNG', headers)
                request.assert_not_called()

    def test_identical_existing_record_issues_no_mutations(self):
        target, _ = bed.load_source()
        existing = {**target, 'updated_at': 'time', 'replaces_ids': []}
        class Fake:
            def require(self, method, path, *args):
                if method != 'GET':
                    raise AssertionError('Unexpected mutation')
                return json.dumps([existing]).encode(), 200, {}
        self.assertEqual(bed.ensure_text(Fake(), target, existing), 'existing_text_identical_skipped')

    def test_concurrent_text_change_is_reread_without_repeated_patch(self):
        target, _ = bed.load_source()
        old = {**copy.deepcopy(target), 'name': 'Old title', 'updated_at': 'time'}
        conflicting = {**old, 'name': 'Concurrent different title', 'updated_at': 'later'}
        class Fake:
            patches = 0
            def require(self, method, path, *args):
                if method == 'PATCH':
                    self.patches += 1
                    return b'[]', 200, {}
                return json.dumps([conflicting if self.patches else old]).encode(), 200, {}
        api = Fake()
        with self.assertRaisesRegex(RuntimeError, 'Concurrent Bed Cardio text conflict'):
            bed.ensure_text(api, target, old)
        self.assertEqual(api.patches, 1)


if __name__ == '__main__':
    unittest.main()
