"""Guard image-only scope and exact user approval evidence."""
import unittest
import continue_images as runner


class ContinuationTests(unittest.TestCase):
    def test_catalog_insert_is_prohibited_even_in_apply_mode(self):
        api = object.__new__(runner.ImagesOnlyApi)
        api.apply = True
        with self.assertRaises(RuntimeError):
            api.request('POST', '/rest/v1/catalog_exercise', [])

    def test_content_patch_is_prohibited(self):
        api = object.__new__(runner.ImagesOnlyApi)
        with self.assertRaises(RuntimeError):
            api.request('PATCH', '/rest/v1/catalog_exercise?id=eq.sample', {'content': {}})

    def test_approval_of_different_attempt_is_not_accepted(self):
        progress = {'user_review_history': [{'by': 'user', 'decision': 'approved',
                                            'accepted_sha256': 'old'}]}
        self.assertIsNone(runner.explicit_evidence(progress, [], 'sample', 'new'))

    def test_agent05_per_file_hash_requires_explicit_batch_approval(self):
        progress = {'user_review_history': [{'by': 'user', 'accepted_sha256': 'new'}]}
        self.assertIsNone(runner.explicit_evidence(progress, [], 'sample', 'new'))
        doc = {'approval_decision': {'by': 'user', 'decision': 'approved', 'exercise_ids': ['sample']}}
        self.assertIsNotNone(runner.explicit_evidence(progress, [('manifest.json', doc)], 'sample', 'new'))

    def test_pending_manifest_png_is_counted_without_shared_progress(self):
        path = 'assets/exercises/pending/batch/sample/attempt-1.png'
        manifests = [('manifest.json', {'exercises': [
            {'exercise_id': 'sample', 'user_review': 'pending',
             'branch_output_path': path, 'result_sha256': 'a' * 64},
            {'exercise_id': 'missing', 'user_review': 'pending',
             'result_path': 'assets/exercises/missing.png', 'result_sha256': 'b' * 64}]})]
        results = runner.manifest_pending_records(manifests, {path})
        self.assertEqual([r['exercise_id'] for r in results], ['sample'])

    def test_accepted_result_alias_selects_accepted_hash_not_latest_attempt(self):
        row = {'user_review': 'accepted', 'accepted_result_sha256': 'accepted',
               'accepted_result_path': 'assets/exercises/sample/attempt-2.png',
               'result_sha256': 'unaccepted-later-attempt'}
        result = runner.accepted_row(row)
        self.assertEqual(result['accepted_sha256'], 'accepted')
        self.assertEqual(result['source_user_review'], 'accepted')
        self.assertEqual(row['user_review'], 'accepted')
        self.assertNotIn('accepted_sha256', row)

    def test_no_accepted_hash_is_inferred_from_current_result(self):
        self.assertNotIn('accepted_sha256', runner.accepted_row(
            {'user_review': 'pending', 'result_sha256': 'newest'}))

    def test_nested_manifest_explicit_approval_without_shared_progress(self):
        row = {'exercise_id': 'sample', 'user_review': 'approved',
               'accepted_sha256': 'a' * 64, 'accepted_path': 'assets/exercises/sample.png',
               'accepted_at': 'timestamp', 'approval_source': 'explicit_user_approval_in_chat'}
        doc = {'approval_record': {'source': 'explicit_user_approval_in_chat', 'approved_at': 'timestamp'},
               'batches': [{'results': [row]}]}
        records = runner.manifest_rows(doc)
        self.assertEqual(len(records), 1)
        self.assertIsNotNone(runner.explicit_evidence({}, [('manifest.json', doc)], 'sample', 'a' * 64))
        self.assertIsNone(runner.explicit_evidence({}, [('manifest.json', doc)], 'sample', 'b' * 64))

    def test_handoff_evidence_requires_exact_id_and_hash(self):
        text = '# User decision\nThe user approved the package.\n- sample: SHA256 exact\n'
        self.assertIsNotNone(runner.handoff_evidence(text, 'sample', 'exact'))
        self.assertIsNone(runner.handoff_evidence(text, 'different', 'exact'))
        self.assertIsNone(runner.handoff_evidence(text, 'sample', 'wrong'))

    def test_user_accepted_history_is_exact_approval_not_pending(self):
        progress = {'user_review_history': [{'by': 'user', 'decision': 'accepted',
                                            'accepted_sha256': 'exact'}]}
        self.assertIsNotNone(runner.explicit_evidence(progress, [], 'sample', 'exact'))
        self.assertIsNone(runner.explicit_evidence(progress, [], 'sample', 'different'))

    def test_handoff_negative_user_decision_is_not_approval(self):
        text = '# User decision\nThe user did not approve the package.\n- sample: SHA256 exact\n'
        self.assertIsNone(runner.handoff_evidence(text, 'sample', 'exact'))


if __name__ == '__main__':
    unittest.main()
