#!/usr/bin/env python3
"""Prepare/check an explicit three-ID continuation; never generate images.

Preparation runs on agent-03 only. Old batches, manifests, queue routes and
attempts stay immutable. The user dispatches this packet to one existing worker.
"""
import argparse
import collections
import copy
import datetime
import json
import pathlib
from zoneinfo import ZoneInfo

import prepare_agent03_generator_b as b
import audit_agent03_unconfirmed as approval_audit

base = b.base
ROOT = base.ROOT
ROUND = 'agent-03-three-continuation-2026-10-03'
BID = 'agent-03-others-043'
BATCH = f'data/batches/{BID}.json'
REG = f'data/assignments/{ROUND}.json'
MANIFEST = f'data/manifests/{ROUND}/generator-single.json'
RESUME = f'data/resumes/{ROUND}.json'
EVIDENCE = f'data/audits/{ROUND}-technique.json'
CHECK = f'data/audits/{ROUND}-validation.json'
HANDOFF = f'docs/{ROUND}-handoff.md'
MESSAGE = f'docs/{ROUND}-message.md'
WORKER = 'agent-08-generator-single-2026-10-03'
IDS = ['treadmill-machine', 'reverse-grip-lat-pulldown-cable-machine', 'leg-press-horizontal-machine']
CLOUD = f'/workspace/exercise-image-results/{ROUND}/generator-single'
GIT = f'assets/exercises/pending/{ROUND}/generator-single'
USER_REQUEST = 'Підготуй пакет для treadmill machine, reverse grip lat pulldown cable machine і leg press horizontal machine, щоб я міг скинути агенту.'
OLD = {
    IDS[0]: ('origin/' + WORKER, 'data/manifests/agent-03-single-generator-2026-10-03/generator-single.json', 'agent-03-others-030', 'data/assignments/agent-03-single-generator-2026-10-03.json'),
    IDS[1]: ('origin/' + WORKER, 'data/manifests/agent-03-single-generator-next30-2026-10-03/generator-single.json', 'agent-03-others-032', 'data/assignments/agent-03-single-generator-next30-2026-10-03.json'),
    IDS[2]: ('origin/agent-02-machines-001', 'data/batches/agent-02-machines-001-manifest.json', 'agent-02-machines-001', None),
}
SCENES = {
    IDS[0]: ('One grounded treadmill walking stride',
             'Upright balanced torso; right heel at forward belt contact and left forefoot at trailing belt contact; both knees soft, natural opposite arm swing. Neither foot is airborne in this selected phase.',
             'Hands free, off the rails during balanced walking; no weights.',
             'Compatible motorized treadmill, belt and deck with a modest walking incline, fixed balance rails and console. Both feet contact the belt. The catalogue safety clip is attached to the black shorts waistband, with its lanyard connected to the console. Barefoot under the unchanged approved model rule; no outdoor trail.',
             'Even controlled walking as the treadmill belt moves; one phase only, not running, mounting, dismounting or a sequence.'),
    IDS[1]: ('Underhand cable pulldown at the upper chest',
             'Seated with both feet on the floor, braced upright spine and only slight backward torso lean; elbows drawn down beside the ribs, shoulders depressed, bar just in front of the upper chest.',
             'Both hands hold the same pulldown bar with a closed underhand/supinated grip, slightly wider than shoulder width; thumbs wrapped and wrists aligned.',
             'A seated cable pulldown station: a single bar attached at its centre to a taut cable from an overhead high pulley. A compatible seat and stable machine frame support the seated person. Show the continuous cable-bar connection; no band or independent moving lever handles.',
             'Pull the bar from overhead to the front of the upper chest, then return under control. Freeze the lower pulling endpoint, not a behind-neck pull or swinging row.'),
    IDS[2]: ('Horizontal leg press, mid press with knees still bent',
             'Sit against a supported backrest with pelvis and entire lower back on the pad. Both feet shoulder-width apart and whole soles flat on the vertical footplate. Hips and knees partly extended, knees tracking over feet without locking; pelvis remains seated.',
             'Hands rest on simple fixed side grips for stability only; their placement is a compatible illustration choice, not a working arm movement.',
             'Unbranded seated HORIZONTAL leg-press frame with a fixed seat/back pad and a moving vertical footplate carriage guided horizontally away from the seat. Include compatible travel/safety stops. The resistance is contained in the machine housing; do not invent a brand, plate count, load or exposed cable attachment. It is not a 45-degree inclined sled.',
             'Press the footplate horizontally away by extending hips and knees; return until the knees bend comfortably while the pelvis and lower back stay supported. Freeze one controlled mid-press phase.'),
}


def now():
    return datetime.datetime.now(ZoneInfo('Europe/Kiev')).isoformat()


def prior_record(eid, snapshot):
    ref, path, bid, registry = OLD[eid]
    raw = base.git('show', snapshot['commits'][ref] + ':' + path)
    doc = json.loads(raw)
    candidates = []

    def walk(value, pointer=''):
        if isinstance(value, dict):
            if value.get('exercise_id') == eid and 'attempts' in value:
                candidates.append((pointer, value))
            for key in ('batches', 'exercises', 'tasks'):
                walk(value.get(key, []), pointer + '/' + key)
        elif isinstance(value, list):
            for i, child in enumerate(value):
                walk(child, pointer + '/' + str(i))

    walk(doc)
    assert len(candidates) == 1, (eid, 'non-unique original execution record')
    pointer, row = candidates[0]
    assert row['attempts'] == 1 and row['status'] in ['failed', 'generation_failed'], eid
    assert not any(row.get(key) for key in ['result_path', 'path', 'accepted_path', 'result_sha256', 'sha256']), eid
    return {'exercise_id': eid, 'original_batch_id': bid, 'original_owner': ref.removeprefix('origin/'),
            'source': {'branch': ref.removeprefix('origin/'), 'commit': snapshot['commits'][ref], 'path': path,
                       'json_pointer': pointer, 'sha256': base.sha(raw)},
            'original_record_sha256': base.value_sha(row), 'original_record': copy.deepcopy(row),
            'previous_actual_attempts': row['attempts'], 'next_attempt_number': row['attempts'] + 1,
            'dispatch_kind': 'same_owner_continuation' if eid != IDS[2] else 'user_requested_transfer_of_failed_no_PNG_task',
            'original_registry_path': registry,
            'single_owner_when_dispatched': WORKER, 'old_records_preserved': True,
            'original_one_call_limit_is_not_automatic_retry_authorization': eid == IDS[2],
            'new_call_requires_user_dispatch_of_this_handoff': True}


def exclusions(snapshot):
    if 'approved_evidence' in snapshot and 'actual_assignments' in snapshot:
        approvals = snapshot['approved_evidence']
        assignments = snapshot['actual_assignments']
    else:
        approvals, _ = approval_audit.collect_review_evidence(snapshot)
        assignments = b.actual_assignments(snapshot)
    errors = []
    for eid in IDS:
        if snapshot['by_id'][eid]['archived'] or eid in snapshot['png_sources'] or eid in approvals:
            errors.append({'exercise_id': eid, 'reason': 'archived, PNG exists or protected approval exists'})
        _, manifest, bid, registry = OLD[eid]
        allowed = {manifest, f'data/batches/{bid}.json', BATCH, REG, MANIFEST, RESUME}
        if registry:
            allowed.add(registry)
        for assignment in assignments.get(eid, []):
            if assignment['path'] in allowed:
                continue
            if assignment['kind'] == 'batch_queue_route' and assignment.get('batch_id') == bid:
                continue
            errors.append({'exercise_id': eid, 'reason': 'unexpected assignment', 'source': assignment})
    return errors


def prepare(snapshot):
    assert base.git('branch', '--show-current').decode().strip() == base.BRANCH
    assert not exclusions(snapshot), exclusions(snapshot)
    assert all(BATCH not in paths for paths in snapshot['trees'].values()), 'Batch number already exists remotely'
    for path in [BATCH, REG, MANIFEST, RESUME, EVIDENCE, CHECK, HANDOFF, MESSAGE]:
        assert not (ROOT/path).exists(), ('Never overwrite', path)
    frozen = {path: b.sha(path) for path in base.git('ls-files').decode().splitlines()
              if path != '.gitignore' and not path.startswith('assets/')}
    old_ignore = (ROOT/'.gitignore').read_text()
    records = [prior_record(eid, snapshot) for eid in IDS]
    evidence = b.source_evidence(snapshot, IDS)
    assert evidence['records'][2]['source_dataset_id'] is None
    evidence.update(prepared_at_Kyiv=now(), audited_commits=snapshot['commits'], images_reviewed=False,
                    confirmation_rule='Read the exact catalogue English and bound written dataset steps. Binding/name alone is not confirmation. Horizontal leg press is authored in the catalogue and has no dataset binding.',
                    construction_rule='Standard compatible unbranded geometry is an illustration choice under AGENTS.md; no manufacturer model or external confirmation is claimed.')
    b.save(EVIDENCE, evidence)
    rows = []
    for eid, history in zip(IDS, records):
        row = base.fields_for_id(eid, snapshot)
        scene = b.n.prior.scene(eid, SCENES[eid], b.CAMERA)
        style = copy.deepcopy(base.STYLE)
        style['version'] = 'v1'
        files = [{'path': 'docs/exercise-image-style.md', 'sha256': b.sha('docs/exercise-image-style.md')}]
        if row['primary_muscle'] in ['full_body', 'cardio', 'other']:
            style['version'] = b.NEUTRAL_VERSION
            style['primary_highlight'] = {'hex': None, 'rule': 'Keep the body neutral opaque silver-gray. Highlight ONLY explicitly listed secondary muscles; an empty list means no highlights.'}
            files.append({'path': b.NEUTRAL_DOC, 'sha256': b.sha(b.NEUTRAL_DOC)})
        resolution = {'status': 'resolved_for_illustration', 'decision_kind': 'exact_ID_catalogue_written_technique',
                      'evidence_path': EVIDENCE, 'evidence_selector': f'records[exercise_id="{eid}"]',
                      'catalog_modified': False, 'PNG_approval': False, 'external_manufacturer_confirmation_claimed': False,
                      'written_technique': 'Seated underhand cable pull to upper chest' if eid == IDS[1] else 'Controlled walking on a treadmill' if eid == IDS[0] else 'Seated supported horizontal moving-footplate leg press',
                      'illustration_choices': 'Single phase, camera and compatible unbranded contact geometry; no invented muscle targets or dataset substitution.',
                      'catalogue_dataset_binding': snapshot['by_id'][eid]['source']['dataset_id']}
        cloud = f'{CLOUD}/{BID}/{eid}/attempt-2.png'
        git_path = f'{GIT}/{BID}/{eid}/attempt-2.png'
        payload = {'identity_do_not_render_as_text': {'exercise_id': eid, 'name': row['name'], 'catalog_sha256': snapshot['catalog_sha256'], 'catalog_record_sha256': row['source_catalog_record_sha256']},
                   'exact_catalogue_source': {k: copy.deepcopy(row[k]) for k in ['source_english', 'equipment', 'primary_muscle', 'secondary_muscles']},
                   'selected_render_scene': scene, 'technique_resolution': resolution,
                   'human_reference': b.n.prior.reference(snapshot), 'style': style, 'approved_style_files': files,
                   'source_use_rule': 'Use the exact ID source and documented compatible scene. Reference governs human appearance/materials only. Do not import other exercises or anatomical targets.',
                   'planned_output_do_not_render_as_text': {'exercise_id': eid, 'batch_id': BID, 'attempt': 2, 'cloud_path': cloud, 'git_path': git_path}}
        prompt = 'Create exactly ONE square 1024x1024 transparent PNG, ONE person and ONE phase of this exact exercise. Never render source metadata as text.\n' + json.dumps(payload, ensure_ascii=False, sort_keys=True, indent=2)
        old = history['original_record']
        row.update(batch_id=BID, status='ready', prompt_prepared=True, generation_prompt=prompt,
                   prompt_payload=payload, prompt_sha256=base.sha(prompt.encode()), scene=scene,
                   technique_resolution=resolution, style_version=style['version'], approved_style_files=files,
                   human_reference=payload['human_reference'], source_catalog_commit=snapshot['commits']['origin/work'],
                   source_url=b.n.CATALOG_URL+snapshot['commits']['origin/work']+'/'+base.CATALOG_PATH,
                   source_selector=f'exercises[id="{eid}"]', source_evidence_path=EVIDENCE,
                   assigned_generator='generator-single', execution_branch=WORKER, assignment_registry_path=REG,
                   continuation=copy.deepcopy(history), attempts=1, attempts_before=1, attempts_in_this_continuation=0,
                   next_attempt_number=2, attempt_history=copy.deepcopy(old.get('attempt_history', [])),
                   preserved_prior_manifest_record=copy.deepcopy(old), old_batch_id=history['original_batch_id'],
                   planned_png_path=cloud, planned_git_png_path=git_path, result_path=None, result_sha256=None,
                   user_review=None, future_user_review_policy='pending after PNG until explicit user approval',
                   agent_visual_review='not_performed', preparation_generation_calls=0,
                   generation_authorized_now=False, execution_requires_user_dispatch=True)
        rows.append(row)
    gate = 'Only one worker, after its already-taken jobs including 041–042. User dispatch activates this continuation. Retire the old execution route for ONLY these exact IDs at dispatch; preserve its history and do not run both old and new routes. No PNG/approval replacement.'
    b.save(BATCH, {'schema_version': 1, 'batch_id': BID, 'status': 'ready', 'task_kind': 'explicit_continuation_of_failed_no_PNG_tasks',
                   'exercise_count': 3, 'exercise_ids': IDS, 'exercises': rows, 'source_branch': base.BRANCH,
                   'catalog_sha256': snapshot['catalog_sha256'], 'generator': 'generator-single', 'execution_branch': WORKER,
                   'assignment_registry_path': REG, 'handoff_path': HANDOFF, 'manifest_path': MANIFEST,
                   'execution_gate': gate, 'audited_commits': snapshot['commits'], 'generation_calls': 0})
    b.save(REG, {'schema_version': 1, 'assignment_id': ROUND, 'source_branch': base.BRANCH, 'source_base_commit': snapshot['commits']['HEAD'],
                 'status': 'ready_for_user_dispatch', 'exercise_count': 3, 'batch_paths': [BATCH], 'user_request': USER_REQUEST,
                 'assignments': [{'generator': 'generator-single', 'execution_branch': WORKER, 'status': 'ready_for_user_dispatch',
                                  'exercise_ids': IDS, 'batch_paths': [BATCH], 'manifest_path': MANIFEST, 'continuations': records}],
                 'execution_gate': gate, 'old_assignments_modified': False, 'live_generation_dispatched_by_preparer': False,
                 'audited_commits': snapshot['commits'], 'generation_calls_by_preparer': 0})
    b.save(RESUME, {'schema_version': 1, 'status': 'ready_for_user_dispatch', 'batch_id': BID, 'exercise_ids': IDS,
                    'exercise_count': 3, 'exercises': records, 'execution_gate': gate, 'old_queue_routes_unchanged': True,
                    'user_request': USER_REQUEST, 'scope_limit': 'Pushed Git only; fresh local/live worker checks before every call.'})
    b.save(MANIFEST, {'schema_version': 1, 'manifest_id': ROUND, 'source_branch': base.BRANCH, 'execution_branch': WORKER,
                     'status': 'ready_not_started', 'exercise_count': 3, 'generation_calls': 0, 'prior_generation_calls': 3,
                     'assignment_path': REG, 'user_review_policy': 'pending after PNG until user decision',
                     'batches': [{'batch_id': BID, 'status': 'ready_not_started', 'exercises': copy.deepcopy(rows)}]})
    additions = '\n# Explicit three-ID continuation, attempt-2 only\n' + '\n'.join('!'+r['planned_git_png_path'] for r in rows) + '\n'
    (ROOT/'.gitignore').write_text(old_ignore + additions)
    b.save(CHECK, {'schema_version': 1, 'status': 'prepared_pending_validation', 'prepared_at_Kyiv': now(),
                   'audited_commits': snapshot['commits'], 'protected_sha256': frozen,
                   'original_gitignore_sha256': base.sha(old_ignore.encode()), 'gitignore_exact_append': additions,
                   'catalog_sha256': snapshot['catalog_sha256'], 'generation_calls': 0})
    return check(snapshot)


def check(snapshot):
    report = b.load(CHECK)
    assert not exclusions(snapshot), exclusions(snapshot)
    assert len(snapshot['by_id']) == 451 and sum(len(e['content']) for e in snapshot['by_id'].values()) == 4448
    for path, digest in report['protected_sha256'].items():
        assert b.sha(path) == digest, ('Protected old file changed', path)
    ignore = (ROOT/'.gitignore').read_text()
    addition = report['gitignore_exact_append']
    assert ignore.endswith(addition) and base.sha(ignore[:-len(addition)].encode()) == report['original_gitignore_sha256']
    batch = b.load(BATCH)
    assert batch['exercise_ids'] == IDS and batch['exercise_count'] == len(batch['exercises']) == len(set(IDS)) == 3
    binding = b.source_evidence(snapshot, IDS)
    saved = b.load(EVIDENCE)
    for key, value in binding.items():
        assert saved[key] == value, ('Source evidence mismatch', key)
    for row in batch['exercises']:
        eid = row['exercise_id']
        for key, value in base.fields_for_id(eid, snapshot).items():
            assert row[key] == value, (eid, 'Exact-ID field mismatch', key)
        live_history = prior_record(eid, snapshot)
        # Unrelated rows in the same manifest may change on a worker branch.
        # Require the exact-ID row to match, keeping immutable original
        # file/commit/pointer provenance, which is verified separately below.
        live_history['source'] = copy.deepcopy(row['continuation']['source'])
        assert row['continuation'] == live_history, (eid, 'History mismatch')
        source = row['continuation']['source']
        assert base.sha(base.git('show', source['commit'] + ':' + source['path'])) == source['sha256']
        assert row['preserved_prior_manifest_record'] == row['continuation']['original_record']
        assert row['attempt_history'] == row['preserved_prior_manifest_record'].get('attempt_history', [])
        assert row['attempts'] == row['attempts_before'] == 1 and row['next_attempt_number'] == 2
        assert row['attempts_in_this_continuation'] == row['preparation_generation_calls'] == 0
        prompt = row['generation_prompt']
        assert isinstance(prompt, str) and prompt.strip() and len(prompt) > 1000
        assert base.sha(prompt.encode()) == row['prompt_sha256']
        assert json.loads(prompt.split('\n', 1)[1]) == row['prompt_payload']
        assert row['scene'] == b.n.prior.scene(eid, SCENES[eid], b.CAMERA)
        for key in ['source_english', 'equipment', 'primary_muscle', 'secondary_muscles']:
            assert row['prompt_payload']['exact_catalogue_source'][key] == row[key], (eid, key)
        assert row['prompt_payload']['identity_do_not_render_as_text']['exercise_id'] == eid
        assert row['prompt_payload']['selected_render_scene'] == row['scene']
        assert row['human_reference']['sha256'] == snapshot['reference_sha256']
        for style_file in row['approved_style_files']:
            assert b.sha(style_file['path']) == style_file['sha256']
        if eid == IDS[0]:
            assert row['primary_muscle'] == 'cardio' and row['secondary_muscles'] == []
            assert row['style_version'] == b.NEUTRAL_VERSION and row['prompt_payload']['style']['primary_highlight']['hex'] is None
        else:
            assert row['style_version'] == 'v1' and row['prompt_payload']['style']['primary_highlight']['hex'] == '#F26445'
        assert row['prompt_payload']['style']['secondary_highlight']['intensity_fraction'] == [0.4, 0.5]
        assert row['planned_png_path'] == f'{CLOUD}/{BID}/{eid}/attempt-2.png'
        assert row['planned_git_png_path'] == f'{GIT}/{BID}/{eid}/attempt-2.png'
        assert row['result_path'] is None and row['user_review'] is None and row['generation_authorized_now'] is False
    assert b.load(MANIFEST)['batches'][0]['exercises'] == batch['exercises']
    assert b.load(REG)['assignments'][0]['exercise_ids'] == IDS
    assert b.load(RESUME)['exercise_ids'] == IDS
    report.update(status='passed', checked_at_Kyiv=now(), exercise_count=3, exercise_ids=IDS,
                  new_unique_IDs_assigned=0, explicit_continuations=3, historical_attempt_counts=[1, 1, 1],
                  next_attempt_numbers=[2, 2, 2], PNG_intersections=[], approval_intersections=[],
                  unexpected_assignment_intersections=[], old_batch_manifest_queue_files_unchanged=True,
                  catalog_ID_count=451, language_blocks=4448, generation_calls=0, errors=[])
    b.save(CHECK, report)
    return {k: report[k] for k in ['status', 'exercise_count', 'exercise_ids', 'next_attempt_numbers', 'generation_calls', 'errors']}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--prepare', action='store_true')
    parser.add_argument('--fetch', action='store_true')
    parser.add_argument('--snapshot', help='Previously freshly fetched read-only snapshot (preparation only).')
    args = parser.parse_args()
    if args.fetch:
        b.fetch_heads()
    snapshot = json.loads(pathlib.Path(args.snapshot).read_text()) if args.snapshot else b.n.snapshot()
    assert base.git('branch', '--show-current').decode().strip() == base.BRANCH
    print(json.dumps(prepare(snapshot) if args.prepare else check(snapshot), ensure_ascii=False, indent=2))
