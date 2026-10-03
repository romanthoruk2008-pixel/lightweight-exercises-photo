"""Guard image-only scope and exact user approval evidence."""
import unittest
import continue_images as runner


class ContinuationTests(unittest.TestCase):
    def reference_rework_manifest(self):
        path = 'assets/exercises/sample/attempt-2.png'
        attempt = {'attempt_number': 2, 'user_review': 'approved',
                   'user_reviewed_at': 'timestamp', 'git_result_path': path,
                   'result_sha256': 'a' * 64}
        row = {'exercise_id': 'sample', 'user_review': 'approved',
               'user_reviewed_at': 'timestamp', 'result_sha256': 'a' * 64,
               'git_result_path': path, 'attempt_history': [attempt,
                   {'attempt_number': 3, 'user_review': 'pending',
                    'result_sha256': 'b' * 64}]}
        event = {'approved_at': 'timestamp', 'approval_source': 'explicit_user_approval_in_chat',
                 'approved_exercise_ids': ['sample'], 'not_approved_exercise_ids': []}
        return row, {'exercises': [row], 'user_approval_events': [event]}

    def test_rework_reads_exact_approved_attempt_and_preserves_source(self):
        row, doc = self.reference_rework_manifest()
        normalized = runner.manifest_rows(doc)[0]
        self.assertEqual(normalized['accepted_sha256'], 'a' * 64)
        self.assertEqual(normalized['accepted_attempt'], 2)
        self.assertNotIn('accepted_sha256', row)
        proof = runner.explicit_evidence({}, [('manifest.json', doc)], 'sample', 'a' * 64)
        self.assertEqual(proof['accepted_attempt_approval']['attempt_number'], 2)
        self.assertIsNone(runner.explicit_evidence({}, [('manifest.json', doc)], 'sample', 'b' * 64))

    def test_rework_requires_exact_attempt_and_row_hash_path_time(self):
        for field, value in [('result_sha256', 'b' * 64), ('git_result_path', 'wrong.png'),
                             ('user_reviewed_at', 'other'), ('user_review', 'pending')]:
            with self.subTest(field=field):
                row, doc = self.reference_rework_manifest()
                row['attempt_history'][0][field] = value
                self.assertNotIn('accepted_sha256', runner.manifest_rows(doc)[0])
        row, doc = self.reference_rework_manifest()
        row['result_sha256'] = 'b' * 64
        self.assertNotIn('accepted_sha256', runner.manifest_rows(doc)[0])

    def test_rework_rejects_ambiguous_approved_attempts(self):
        row, doc = self.reference_rework_manifest()
        row['attempt_history'].append(dict(row['attempt_history'][0]))
        self.assertNotIn('accepted_sha256', runner.manifest_rows(doc)[0])

    def test_rework_requires_explicit_event_scope_and_latest_decision(self):
        for field, value in [('approved_exercise_ids', []), ('not_approved_exercise_ids', ['sample']),
                             ('approval_source', 'agent'), ('approved_at', None)]:
            with self.subTest(field=field):
                row, doc = self.reference_rework_manifest()
                doc['user_approval_events'][0][field] = value
                self.assertNotIn('accepted_sha256', runner.manifest_rows(doc)[0])
        row, doc = self.reference_rework_manifest()
        doc['user_approval_events'].append({'not_approved_exercise_ids': ['sample']})
        self.assertNotIn('accepted_sha256', runner.manifest_rows(doc)[0])

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

    def test_scalar_approval_label_does_not_replace_user_hash_evidence(self):
        progress = {'approval_decision': 'approved'}
        self.assertIsNone(runner.explicit_evidence(progress, [], 'sample', 'exact'))
        progress['user_review_history'] = [{'by': 'user', 'decision': 'approved', 'accepted_sha256': 'exact'}]
        self.assertIsNotNone(runner.explicit_evidence(progress, [], 'sample', 'exact'))

    def generator_b_manifest(self):
        row = {'exercise_id': 'sample', 'user_review': 'approved',
               'accepted_sha256': 'a' * 64, 'accepted_path': 'assets/exercises/sample.png',
               'user_approved_at': 'timestamp', 'technical_issue_accepted_by_user': True}
        doc = {'exercises': [row], 'user_approval': {'accepted_by': 'user',
               'decision': 'approved', 'approved_at': 'timestamp', 'exercise_count': 1,
               'technical_dimension_mismatch_acknowledged': True}}
        return row, doc

    def test_generator_b_manifest_approval_keeps_exact_file_and_exception(self):
        row, doc = self.generator_b_manifest()
        evidence = runner.manifest_user_evidence(row, doc, 'sample', 'a' * 64)
        self.assertEqual(evidence['file']['accepted_path'], row['accepted_path'])
        self.assertTrue(evidence['file']['technical_issue_accepted_by_user'])
        self.assertIsNotNone(runner.explicit_evidence({}, [('manifest.json', doc)], 'sample', 'a' * 64))
        self.assertIsNone(runner.manifest_user_evidence(row, doc, 'sample', 'b' * 64))

    def test_generator_b_manifest_approval_rejects_conflicting_scope_or_actor(self):
        for key, value in [('accepted_by', 'agent'), ('decision', 'pending'),
                           ('exercise_count', 2), ('approved_at', 'different'),
                           ('approved_at', None)]:
            with self.subTest(key=key, value=value):
                row, doc = self.generator_b_manifest()
                doc['user_approval'][key] = value
                self.assertIsNone(runner.manifest_user_evidence(row, doc, 'sample', 'a' * 64))

    def test_generator_b_manifest_does_not_infer_accepted_hash_from_result(self):
        row, doc = self.generator_b_manifest()
        row['result_sha256'] = row.pop('accepted_sha256')
        self.assertIsNone(runner.explicit_evidence({}, [('manifest.json', doc)], 'sample', 'a' * 64))

    def single_generator_manifest(self):
        row = {'exercise_id': 'sample', 'user_review': 'approved',
               'accepted_sha256': 'a' * 64, 'accepted_path': 'assets/exercises/sample.png',
               'accepted_at': 'timestamp', 'approval_source': 'explicit_user_approval_in_chat'}
        event = {'approved_at': 'timestamp', 'approval_source': 'explicit_user_approval_in_chat',
                 'approved_exercise_ids': ['sample'], 'not_approved_exercise_ids': [],
                 'failed_without_png_ids': []}
        return row, {'batches': [{'exercises': [row]}], 'user_approval_events': [event]}

    def test_single_generator_event_requires_exact_accepted_hash_and_timestamp(self):
        row, doc = self.single_generator_manifest()
        self.assertIsNotNone(runner.explicit_evidence({}, [('manifest.json', doc)], 'sample', 'a' * 64))
        self.assertIsNone(runner.manifest_user_evidence(row, doc, 'sample', 'b' * 64))
        row['accepted_at'] = 'different'
        self.assertIsNone(runner.manifest_user_evidence(row, doc, 'sample', 'a' * 64))

    def test_single_generator_exclusions_and_later_decisions_take_precedence(self):
        for field in ['not_approved_exercise_ids', 'failed_without_png_ids']:
            with self.subTest(field=field):
                row, doc = self.single_generator_manifest()
                doc['user_approval_events'][0][field] = ['sample']
                self.assertIsNone(runner.manifest_user_evidence(row, doc, 'sample', 'a' * 64))
        row, doc = self.single_generator_manifest()
        doc['user_approval_events'].append({'not_approved_exercise_ids': ['sample']})
        self.assertIsNone(runner.manifest_user_evidence(row, doc, 'sample', 'a' * 64))

    def test_single_generator_pending_git_path_is_counted_without_approval(self):
        path = 'assets/exercises/sample/attempt-1.png'
        row = {'exercise_id': 'sample', 'user_review': 'pending',
               'result_sha256': 'a' * 64, 'planned_git_png_path': path}
        doc = {'batches': [{'exercises': [row]}]}
        records = runner.manifest_pending_records([('manifest.json', doc)], {path})
        self.assertEqual(len(records), 1)
        self.assertEqual(records[0]['path'], path)
        self.assertIsNone(runner.explicit_evidence({}, [('manifest.json', doc)], 'sample', 'a' * 64))

    def next30_manifest(self):
        row = {'exercise_id': 'sample', 'user_review': 'approved',
               'accepted_sha256': 'a' * 64, 'accepted_path': 'assets/exercises/sample.png',
               'user_reviewed_at': 'timestamp'}
        approval = {'decision': 'explicit_user_acceptance', 'reviewed_at': 'timestamp',
                    'accepted_exercise_ids': ['sample'], 'excluded_pending_exercise_ids': [],
                    'failed_without_png_exercise_ids': []}
        return row, {'batches': [{'exercises': [row]}], 'user_approval': approval}

    def test_next30_explicit_acceptance_requires_exact_hash_and_review_time(self):
        row, doc = self.next30_manifest()
        self.assertIsNotNone(runner.explicit_evidence({}, [('manifest.json', doc)], 'sample', 'a' * 64))
        self.assertIsNone(runner.manifest_user_evidence(row, doc, 'sample', 'b' * 64))
        row['user_reviewed_at'] = 'different'
        self.assertIsNone(runner.manifest_user_evidence(row, doc, 'sample', 'a' * 64))

    def test_next30_acceptance_exclusions_and_missing_decision_are_rejected(self):
        for field, value in [('excluded_pending_exercise_ids', ['sample']),
                             ('failed_without_png_exercise_ids', ['sample']),
                             ('accepted_exercise_ids', []), ('decision', 'pending'),
                             ('reviewed_at', None)]:
            with self.subTest(field=field):
                row, doc = self.next30_manifest()
                doc['user_approval'][field] = value
                self.assertIsNone(runner.manifest_user_evidence(row, doc, 'sample', 'a' * 64))

    def test_next30_approval_does_not_infer_accepted_hash_or_accept_pending(self):
        row, doc = self.next30_manifest()
        row['result_sha256'] = row.pop('accepted_sha256')
        self.assertIsNone(runner.explicit_evidence({}, [('manifest.json', doc)], 'sample', 'a' * 64))
        row['accepted_sha256'] = 'a' * 64
        row['user_review'] = 'pending'
        self.assertIsNone(runner.manifest_user_evidence(row, doc, 'sample', 'a' * 64))

    def round3_manifest(self):
        row = {'exercise_id': 'sample', 'user_review': 'approved', 'accepted_attempt': 1,
               'accepted_path': 'assets/exercises/sample/attempt-1.png',
               'accepted_sha256': 'a' * 64, 'accepted_at': 'timestamp',
               'approval_source': 'explicit_user_approval_in_chat'}
        row['attempt_history'] = [{'attempt': 1, **{k: row[k] for k in (
            'user_review', 'accepted_path', 'accepted_sha256', 'accepted_at', 'approval_source')}}]
        return row, {'batches': [{'exercises': [row]}]}

    def test_round3_requires_exact_explicitly_accepted_attempt(self):
        row, doc = self.round3_manifest()
        evidence = runner.explicit_evidence({}, [('manifest.json', doc)], 'sample', 'a' * 64)
        self.assertEqual(evidence['accepted_attempt_approval']['attempt'], 1)
        self.assertIsNone(runner.manifest_user_evidence(row, doc, 'sample', 'b' * 64))
        row['accepted_attempt'] = 2
        self.assertIsNone(runner.manifest_user_evidence(row, doc, 'sample', 'a' * 64))

    def test_round3_conflicting_attempt_approval_is_rejected(self):
        for field, value in [('user_review', 'pending'), ('approval_source', 'agent_review'),
                             ('accepted_at', 'different'), ('accepted_path', 'other.png'),
                             ('accepted_sha256', 'b' * 64)]:
            with self.subTest(field=field):
                row, doc = self.round3_manifest()
                row['attempt_history'][0][field] = value
                self.assertIsNone(runner.manifest_user_evidence(row, doc, 'sample', 'a' * 64))

    def test_round3_marker_without_attempt_proof_does_not_approve(self):
        row, doc = self.round3_manifest()
        row['attempt_history'] = []
        self.assertIsNone(runner.manifest_user_evidence(row, doc, 'sample', 'a' * 64))

    def review_record_row(self):
        return {'exercise_id': 'sample', 'user_review': 'approved', 'user_reviewed_at': 'timestamp',
                'user_review_record': {'exercise_id': 'sample', 'reviewed_by': 'user',
                'decision': 'approved', 'approved_at': 'timestamp', 'sha256': 'a' * 64,
                'path': 'assets/exercises/sample.png'}}

    def test_review_record_alias_preserves_explicit_user_file_not_result(self):
        row = self.review_record_row()
        row['result_sha256'] = 'b' * 64
        accepted = runner.accepted_row(row)
        self.assertEqual(accepted['accepted_sha256'], 'a' * 64)
        self.assertIsNotNone(runner.manifest_user_evidence(accepted, {}, 'sample', 'a' * 64))
        self.assertNotIn('accepted_sha256', row)

    def test_review_record_wrong_actor_id_hash_or_timestamp_is_rejected(self):
        for field, value in [('reviewed_by', 'agent'), ('exercise_id', 'other'),
                             ('decision', 'pending'), ('approved_at', 'other')]:
            with self.subTest(field=field):
                row = self.review_record_row(); row['user_review_record'][field] = value
                self.assertIsNone(runner.manifest_user_evidence(runner.accepted_row(row), {}, 'sample', 'a' * 64))

    def test_final13_per_file_user_approval_requires_exact_hash_and_timestamp(self):
        row = {'exercise_id': 'sample', 'user_review': 'approved', 'accepted_sha256': 'a' * 64,
               'accepted_path': 'assets/exercises/sample.png', 'approved_at': 'timestamp',
               'user_approval': {'decision': 'approved', 'recorded_at': 'timestamp',
                                'approval_source': 'explicit_user_approval_in_chat'}}
        self.assertIsNotNone(runner.manifest_user_evidence(row, {}, 'sample', 'a' * 64))
        self.assertIsNone(runner.manifest_user_evidence(row, {}, 'sample', 'b' * 64))
        row['approved_at'] = 'different'
        self.assertIsNone(runner.manifest_user_evidence(row, {}, 'sample', 'a' * 64))

    def test_final13_pending_is_not_approved_by_per_file_note(self):
        row = {'exercise_id': 'sample', 'user_review': 'pending', 'accepted_sha256': 'a' * 64,
               'accepted_path': 'assets/exercises/sample.png', 'approved_at': 'timestamp',
               'user_approval': {'decision': 'approved', 'recorded_at': 'timestamp',
                                'approval_source': 'explicit_user_approval_in_chat'}}
        self.assertIsNone(runner.manifest_user_evidence(row, {}, 'sample', 'a' * 64))


if __name__ == '__main__':
    unittest.main()
