#!/usr/bin/env python3
"""Read pushed Git approval records before planning revisions; never inspect pixels.

By default this only reports. --write updates this preparation branch's separate
planning queue, never a generator manifest, PNG, approval or shared progress.
"""
import argparse
import collections
import copy
import json
import re

import prepare_agent03_generator_b as b

QUEUE = 'data/queues/agent-03-common-variants-2026-10-03-unconfirmed-rework.json'


def collect_review_evidence(snapshot):
    reviews = collections.defaultdict(list)
    max_attempt = collections.defaultdict(int)
    by_id = snapshot['by_id']

    def walk(value, ref, path, pointer='', hint=None):
        if isinstance(value, dict):
            eid = value.get('exercise_id', value.get('id', hint))
            eid = eid if isinstance(eid, str) and eid in by_id else None
            if eid:
                if isinstance(value.get('attempts'), int):
                    max_attempt[eid] = max(max_attempt[eid], value['attempts'])
                review, status = value.get('user_review'), value.get('status')
                explicit = isinstance(review, str) and review in ('approved', 'accepted')
                accepted = value.get('accepted_path') or value.get('accepted_sha256')
                trusted = path in ('data/approved-images-manifest.json',
                                   'data/approved-images-github-backup-manifest.json')
                accepted_state = isinstance(status, str) and status in ('approved', 'accepted') and any(
                    value.get(k) for k in ('result_path', 'accepted_path', 'accepted_sha256'))
                if explicit or accepted or trusted or accepted_state:
                    reviews[eid].append({
                        'branch': ref, 'commit': snapshot['commits'][ref], 'path': path,
                        'json_pointer': pointer, 'user_review': review, 'status': status,
                        **{k: value.get(k) for k in ('accepted_path', 'accepted_sha256',
                                                   'result_path', 'result_sha256')},
                        'approval_basis': 'explicit_user_review' if explicit else 'accepted_file_or_approved_backup',
                    })
            for key, child in value.items():
                if key in ('content', 'source_english', 'prompt', 'generation_prompt',
                           'prompt_payload', 'source_binding', 'human_reference',
                           'technique_resolution', 'supplementary_exact_ID_fields'):
                    continue
                walk(child, ref, path, pointer + '/' + str(key), key if key in by_id else None)
        elif isinstance(value, list):
            for index, child in enumerate(value):
                walk(child, ref, path, pointer + '/' + str(index))

    cache = {}
    for ref, paths in snapshot['trees'].items():
        commit = snapshot['commits'][ref]
        for path in paths:
            if not path.startswith('data/') or not path.endswith('.json'):
                continue
            if path.startswith(('data/exercises/', 'data/audits/', 'data/style-decisions/',
                                'data/technique-decisions/', 'data/queues/',
                                'data/assignments/')):
                continue
            # These are actual result/review manifests, unlike task batch JSON.
            # Excluding the whole data/batches directory loses explicit approvals.
            if path.startswith('data/batches/') and not path.endswith('-manifest.json'):
                continue
            key = (commit, path)
            if key not in cache:
                cache[key] = json.loads(b.base.git('show', commit + ':' + path))
            walk(cache[key], ref, path)
    return dict(reviews), dict(max_attempt)


def build_queue(snapshot):
    reviews, max_attempt = collect_review_evidence(snapshot)
    assignments = b.actual_assignments(snapshot)
    rows = []
    for eid, locations in snapshot['png_sources'].items():
        if snapshot['by_id'][eid]['archived'] or eid in reviews:
            continue
        known_max = max_attempt.get(eid, 0)
        for location in locations:
            match = re.search(r'attempt-(\d+)', location['path'])
            known_max = max(known_max, int(match[1]) if match else 1)
        rows.append({
            **b.base.fields_for_id(eid, snapshot), 'status': 'awaiting_prompt_revalidation',
            'user_authorized_new_version': True, 'existing_png_sources': locations,
            'existing_assignments': copy.deepcopy(assignments.get(eid, [])),
            'known_max_attempt': known_max, 'planned_next_attempt': known_max + 1,
            'preserve_all_existing_results_and_history': True,
            'change_user_review': False, 'new_generation_calls': 0,
        })
    protected = sorted(set(reviews) & set(snapshot['png_sources']))
    return {
        'schema_version': 1, 'source_branch': b.base.BRANCH,
        'audited_commits': snapshot['commits'], 'catalog_sha256': snapshot['catalog_sha256'],
        'exercise_count': len(rows), 'protected_approved_ID_count': len(protected),
        'protected_approved_IDs': protected, 'approval_sources': reviews,
        'user_authorization': 'Переробити потрібно ті, які мною не підтверджені. Ті, які мною підтверджені, ми їх не трогаємо.',
        'policy': 'Any approval/accepted-file evidence protects the entire exercise ID. Unconfirmed PNGs are candidates for NEW versions only. Never delete old attempts, change reviews, or steal live assignments. Revalidate exact-ID prompt and live ownership before scheduling.',
        'exercises': sorted(rows, key=lambda row: row['exercise_id']),
        'generation_calls': 0,
        'scope_limit': 'Pushed Git files only; unpushed work/review decisions may be inaccessible. No visual QA. Snapshot is not permission to bypass a fresh per-call approval/ownership check.',
    }


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--fetch', action='store_true')
    parser.add_argument('--write', action='store_true')
    args = parser.parse_args()
    if args.fetch:
        b.fetch_heads()
    snapshot = b.n.snapshot()
    result = build_queue(snapshot)
    if args.write:
        assert b.base.git('branch', '--show-current').decode().strip() == b.base.BRANCH
        b.save(QUEUE, result)
    print(json.dumps({
        'PNG_IDs': len(snapshot['png_sources']),
        'protected_approved_IDs': result['protected_approved_ID_count'],
        'unconfirmed_rework_candidates': result['exercise_count'],
        'queue_written': args.write,
        'audited_commits': snapshot['commits'],
        'generation_calls': 0,
    }, ensure_ascii=False, indent=2))
