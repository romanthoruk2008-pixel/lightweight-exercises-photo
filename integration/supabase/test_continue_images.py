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


if __name__ == '__main__':
    unittest.main()
