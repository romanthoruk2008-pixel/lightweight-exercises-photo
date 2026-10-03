#!/usr/bin/env python3
"""Prepare user-selected variants of the last 13 blocked records, without generation.

Preserve catalogue text and all previous batches. External citation placeholders
in the supplied text are not verified URLs or independent technique confirmation.
"""
import argparse
import collections
import copy
import json
import pathlib
import re

import prepare_agent03_single_generator as p
import prepare_agent03_single_generator_followup as previous
import audit_agent03_unconfirmed as approval_audit

b = p.b
base = p.base
ROOT = p.ROOT
ROUND = 'agent-03-final13-user-variants-2026-10-03'
DECISIONS = f'data/technique-decisions/{ROUND}.json'
SOURCE = f'docs/{ROUND}-source.txt'
REG = f'data/assignments/{ROUND}.json'
MANIFEST = f'data/manifests/{ROUND}/generator-single.json'
EVIDENCE = f'data/audits/{ROUND}-technique.json'
ERRORS = f'data/audits/{ROUND}-catalogue-conflicts.json'
CHECK = f'data/audits/{ROUND}-validation.json'
BLOCKED = f'data/queues/{ROUND}-blocked.json'
HANDOFF = f'docs/{ROUND}-handoff.md'
MESSAGE = f'docs/{ROUND}-message.md'
CLOUD = f'/workspace/exercise-image-results/{ROUND}/generator-single'
GIT = f'assets/exercises/pending/{ROUND}/generator-single'
WORKER = p.WORKER
ROLE = p.ROLE
BATCHES = []

# These are derived render scenes explicitly selected by the supplied user text.
# Ordering keeps the three free-weight tasks first, cable constructions last.
SCENES = {
    'waiter-curl-dumbbell': (
        'Single vertical dumbbell near chest, controlled elbow-flexion contraction',
        'Stand tall, feet hip-width apart, upper arms beside ribs; elbows flexed, shoulders relaxed and torso still. ONE dumbbell remains vertical in front of the body with its upper head above its lower head.',
        'Both open palms face upward directly beneath the UPPER dumbbell head, supporting it like a tray. Fingers only stabilize its edges; neither hand grips the central handle. Wrists remain controlled, no ordinary two-dumbbell supinated curl.',
        'Both bare feet planted on floor. Only ONE intact dumbbell with two solid heads and one connecting handle; its lower head hangs below the supported upper head. No bench, cable, second dumbbell or preacher pad.',
        'Flex elbows to bring the vertical dumbbell from lower abdomen/thigh level toward chest, then lower smoothly. Keep elbows near ribs and dumbbell upright; render only the near-chest phase.'),
    'single-leg-standing-calf-raise-barbell': (
        'Single-leg heel-rise endpoint on a low fixed step',
        'Upright braced torso, free bar across upper trapezius rather than neck. Right forefoot on the step edge, right heel raised, knee softly unlocked. Left knee bent with left foot behind right ankle and clear of floor/step; no assistance from that foot.',
        'BOTH hands firmly hold the free bar with a comfortable overhand back-squat grip. Neither hand touches a rack or handhold; no one-handed support while holding the bar.',
        'Low stable nonslip step supports only the right forefoot and permits free heel travel. Compatible rack/safety arms may stand nearby as passive protection without touching the hands or guiding/loading the bar. Select an empty/light free bar for the illustration, no claimed numerical load or plate count. No Smith rails.',
        'Plantarflex the right ankle to raise heel/body, pause and lower slowly under control with ankle tracking vertically. No bouncing, knee-driven lift or pushing with left leg. The user selected step geometry rather than the raw catalogue floor variant.'),
    'press-under-barbell': (
        'Behind-neck press-under received overhead in a shallow quarter squat',
        'Feet approximately hip-width in a stable bilateral stance; hips and knees flexed only into a QUARTER squat. Trunk braced, free bar stacked overhead, both elbows locked and wrists/elbows/shoulders aligned. No split stance or deep/full overhead squat.',
        'Wide snatch-style overhand grip, one hand on each side of the free bar; even stable lockout.',
        'Both bare feet on floor, empty/light free bar and nearby compatible safety rack without bar-to-rail attachment or hand support. No machine, bench or Smith guide.',
        'User-selected start is bar across upper trapezius BEHIND the neck. A short vertical dip and small leg drive unload the bar; actively move underneath, receive on straight arms in shallow quarter squat, then stand. Render ONLY the quarter-squat receiving phase, not several phases or a front-chest start.'),
    'back-extension-machine': (
        'Seated back-extension lever pressed to neutral upright torso',
        'Remain seated with pelvis supported and stabilized, feet braced on fixed platform. Torso has moved from modest forward inclination to neutral upright; head follows spine. No prone hip hinge over a Roman chair and no forced hyperextension.',
        'Hands rest together in front of chest without pulling handles or pushing against the frame; movement is produced by controlled trunk pressure into the rear pad.',
        'Compatible SEATED SELECTORIZED back-extension machine: fixed seat/pelvic supports, stable foot platform and a padded moving lever behind the upper/middle back. Visible intact linkage to weight stack; no 45-degree bench or abdomen resting on pad.',
        'Torso presses the rear lever pad backward from the seated forward-inclined start to neutral upright, then returns under control. Seat/pelvis/feet stay stable; render the neutral endpoint, not an extreme backward arch.'),
    'seated-dip-machine': (
        'Moving side handles pressed down while the seated body remains fixed',
        'Pelvis stays on FIXED seat, back against support, both feet flat; elbows nearly extended without forced lockout. Trunk neither rises nor drops.',
        'Firm closed overhand grip on paired side lever handles with palms down as the exact catalogue specifies. Align handle geometry and straight wrists; hands move with handles, not against a knee-assistance platform.',
        'Compatible seated leverage dip machine with fixed seat/back pad and two MOVING handles beside hips. Thigh restraint selected from the user-permitted stabilization options, feet planted. No parallel-bar body dip or counterweight-assisted moving knee platform.',
        'From bent elbows, extend elbows to press side lever handles DOWN and return handles upward under control. Only handles/linkage and forearms move; body/seat remain stationary.'),
    'seated-triceps-press-machine': (
        'Dip-style triceps-press handles near the lower endpoint',
        'Sit with back against fixed pad, pelvis still and feet flat. Upper arms stay close to torso; elbows have extended from approximately 90 degrees to almost straight without forced lockout.',
        'Each hand fully wraps one dip-style lever handle with a straight wrist. Compatible comfortable closed grip is an illustration choice; no preacher-style overhead or forward chest-press grip.',
        'Compatible seated DIP-STYLE triceps-press station, fixed seat/back pad and moving side handles. It may share the general mechanism of the seated dip; do not invent a different machine solely to distinguish the IDs.',
        'Press the handles DOWN along their lever arc by elbow extension, then allow controlled upward return. The user selects downward motion despite the raw English forward direction; no movement of the whole body.'),
    'shrug-machine': (
        'Standing plate-loaded shrug at controlled shoulder-elevation endpoint',
        'Stand upright on the fixed platform, torso stable and arms fully straight beside the body. Shoulders elevated vertically toward ears; head and neck neutral, elbows do not bend.',
        'NEUTRAL grip on paired side handles, palms toward the body, wrists straight. This is the user-selected handle configuration, rather than the raw overhand cue.',
        'Compatible STANDING plate-loaded shrug machine with paired side lever arms and intact plate horns carrying plates. Both feet planted; no seat, free barbell, overhead shoulder pads or cable station. No numerical plate count/load claim.',
        'Elevate shoulders vertically to lift handles through the lever arc, pause and lower smoothly. No shoulder circles, arm curl, torso swing or deep knee drive.'),
    'belt-squat-machine': (
        'Controlled comfortable squat depth on a plate-loaded belt-squat platform',
        'Feet evenly planted on two sides of the raised split platform, knees tracking over toes, hips and knees flexed to a comfortable squat depth. Torso braced, heels down; shoulders carry no bar.',
        'Both hands lightly hold fixed vertical stability handles; arms do not lift the load.',
        'Wide padded belt around pelvis/upper hips. ONE secured central chain and carabiner run VERTICALLY DOWN BETWEEN THE LEGS into the platform gap to a secure lower anchor on the lever under the platform. Weight plates sit on the lever weight horns, not dangling directly from belt. Show intact compatible plate-loaded lever/frame/anchor geometry, no invented manufacturer branding.',
        'Squat by controlled hip/knee flexion against hip-belt lever load, then drive through both feet to stand with softly unlocked knees. Chain remains continuous from belt to lever; hands only stabilize.'),
    'rear-kick-machine': (
        'Standing rear kick with working sole pushing lever footplate backward',
        'Face station with modest forward torso inclination, pelvis square and spine neutral. Left leg bears weight on fixed platform; right knee softly bent and right hip extended backward within controlled range.',
        'Both hands hold fixed handles; forearms/upper torso rest on the prescribed chest/forearm support without twisting.',
        'Compatible STANDING rear-kick lever station, fixed stance platform and chest/forearm support. The RIGHT FOOT SOLE presses the face of the moving lever FOOTPLATE/pad; contact is not an ankle cuff, cable, kneeling pad or loose pad laid on shin.',
        'Extend right hip to push lever footplate backward and slightly upward while the right knee stays softly bent and pelvis still. Return slowly; no spinal arch, leg swing or torso rotation.'),
    'single-leg-standing-calf-raise-machine': (
        'One working heel raised beneath a dedicated standing calf machine',
        'Stand upright beneath shoulder pads on upper trapezius, right forefoot on platform edge and right heel raised. Right knee softly unlocked; left leg bent behind with left foot completely clear of platform and floor.',
        'Both hands wrap the machine stability handles; wrists straight, no hand on free bar.',
        'DEDICATED STANDING calf-raise machine with connected shoulder-pad lever, fixed handles, nonmoving forefoot platform and compatible selectorized weight stack as an illustration choice among the user-provided loading options. No Smith bar/guide rails, seated knee-pad machine or leg-press sled.',
        'Plantarflex ONLY right ankle to raise heel/body and shoulder-pad load; lower heel below platform edge with controlled vertical ankle tracking. Left foot never helps. The user explicitly selected dedicated shoulder pads over the raw Smith setup.'),
    'bench-press-cable-machine': (
        'Supine bilateral cable bench press approaching extension above chest',
        'Lie on FLAT bench, head/back/pelvis supported and both feet planted. Hands above chest, elbows almost straight without forced lockout; shoulders remain controlled against bench.',
        'One D-HANDLE in each hand, closed grip with wrists aligned to forearms. No shared bar or cross-body fly arc.',
        'Flat bench centered between TWO cable towers. Both pulley exits equally LOW, one continuous taut cable from each low side pulley to its own D-handle, clear of bench/body. No standing chest-height press, machine lever or dumbbell substitution.',
        'From bent elbows and hands beside chest, PRESS both handles upward and slightly inward over chest; lower toward chest under control. Elbows flex/extend, not a nearly straight-arm fly. Render the one near-extension phase.'),
    'reverse-fly-single-arm-cable-machine': (
        'Far arm finishes a cross-body reverse-fly arc at shoulder line',
        'Stand SIDE-ON with cable tower on LEFT, feet stable, torso still with slight permitted hip hinge. RIGHT working arm has small fixed elbow bend and has swept outward/back to shoulder line; no torso rotation or row.',
        'RIGHT/FAR hand holds ONE D-handle; LEFT/NEAR nonworking hand grips tower stability point. The source phrase far hand supporting is explicitly overridden by the user-selected layout.',
        'Single shoulder/chest-height pulley on LEFT tower and one taut cable to right-hand D-handle. Both feet on floor; left hand supports on fixed frame clear of moving cable. At start the right hand reaches across body; at selected finish it is out/back at shoulder line.',
        'Right shoulder horizontal abduction sweeps handle from across torso outward/back along a wide arc while elbow bend stays small; controlled return. No double-arm reverse fly, torso twist or elbow-driven row.'),
    'squat-row-machine': (
        'Rope row contracted while REMAINING in the squat',
        'Face cable stack, hips/knees held in a stable comfortable squat, chest lifted and back neutral. Both feet planted; elbows drawn back close to ribs and hands near lower ribs/abdomen. Body does NOT rise during the selected row.',
        'One end of ONE rope in each hand, NEUTRAL palms facing each other; closed grips and straight wrists.',
        'LOW pulley in front connected by ONE taut cable to the rope junction. Stand far enough back to keep cable tension, both feet on floor. No waist-height attachment, barbell or rowing seat.',
        'User-selected sequence: squat with arms extended, HOLD squat and row rope to lower ribs/abdomen, re-extend arms while still squatting, THEN stand. Render only contracted row IN squat. Do not blend in the raw partway-standing squat-to-row sequence.'),
}

CAMERAS = {
    'back-extension-machine': 'Full-body rear-side three-quarter view showing the fixed seat, feet/platform, pelvic support and rear lever contact. Keep exposed lumbar anatomy visible where possible, without showing muscles through opaque pad. Entire person and machine visible; no crop or second phase.',
    'rear-kick-machine': 'Full-body side three-quarter view showing supported torso, fixed stance foot, right sole pressing moving footplate and complete lever linkage. Entire person/equipment visible; no crop or second phase.',
    'bench-press-cable-machine': 'Slightly elevated full-body side-front three-quarter view showing supine bench supports, both low pulley exits and both continuous cable-to-handle paths. Entire person, bench and both towers visible; no crop or second phase.',
}

CONFLICT_FIELDS = {
    'back-extension-machine': ['description', 'instructions', 'form_cues'],
    'press-under-barbell': ['instructions'],
    'reverse-fly-single-arm-cable-machine': ['instructions'],
    'seated-dip-machine': ['instructions'],
    'seated-triceps-press-machine': ['instructions'],
    'shrug-machine': ['description', 'instructions'],
    'single-leg-standing-calf-raise-barbell': ['instructions', 'safety_note'],
    'single-leg-standing-calf-raise-machine': ['description', 'instructions', 'safety_note'],
    'squat-row-machine': ['instructions', 'form_cues', 'common_mistakes'],
    'waiter-curl-dumbbell': ['description', 'instructions', 'safety_note'],
}


def configure(paths):
    global BATCHES
    BATCHES = paths
    for key in ['ROUND', 'REG', 'MANIFEST', 'EVIDENCE', 'ERRORS', 'CHECK', 'HANDOFF', 'MESSAGE', 'DECISIONS', 'BLOCKED', 'BATCHES', 'CLOUD', 'GIT']:
        setattr(p, key, globals()[key])
    p.SCENES = SCENES
    p.SOURCE_ERRORS = {eid: True for eid in SCENES}


def parsed_source(text):
    matches = list(re.finditer(r'^(\d+)\. \*\*`([^`]+)`', text, re.M))
    assert len(matches) == 13 and len({m[2] for m in matches}) == 13
    end = text.find('\nТобто **всі 13', matches[-1].end())
    assert end > matches[-1].end()
    return {m[2]: {'point': int(m[1]), 'paragraph': text[m.start():(matches[i+1].start() if i+1<len(matches) else end)].strip()}
            for i, m in enumerate(matches)}


def exclusion(eid, snapshot, assignments, approvals, allow_own=False):
    if eid in approvals:
        return 'approved_or_accepted_ID_protected'
    # Previous helper admits only this round's own published routes/manifest.
    return previous.conflict(eid, snapshot, assignments, allow_own)


def validate(snapshot):
    registry = b.load(REG)
    configure(registry['batch_paths'])
    report, decisions = b.load(CHECK), b.load(DECISIONS)
    source_bytes = (ROOT/SOURCE).read_bytes()
    assert base.sha(source_bytes) == decisions['source_document']['sha256']
    supplied = parsed_source(source_bytes.decode())
    assert set(supplied) == set(SCENES)
    assert base.git('branch', '--show-current').decode().strip() == base.BRANCH
    counts = collections.Counter(row['id'] for row in snapshot['catalog']['exercises'])
    assert len(counts) == 451 and set(counts.values()) == {1}
    assert sum(len(row['content']) for row in snapshot['by_id'].values()) == 4448
    assert snapshot['catalog_sha256'] == registry['catalog_sha256'] == decisions['catalog_sha256']
    assert base.sha(base.git('show', snapshot['commits']['origin/work']+':'+base.CATALOG_PATH)) == snapshot['catalog_sha256']
    for path, expected in report['protected_sha256'].items():
        assert b.sha(path) == expected, path
    queue = b.load(base.QUEUE_PATH)
    routes = {row['exercise_id']: row for row in queue['exercises']}
    for eid, expected in report['previous_queue_routes_sha256'].items():
        assert base.value_sha(routes[eid]) == expected, eid
    assert len(routes) == len(queue['exercises']) == len(set(queue['eligible_exercise_ids'])) == queue['prepared_count']
    approvals, _ = approval_audit.collect_review_evidence(snapshot)
    assignments = b.actual_assignments(snapshot)
    saved_evidence = b.load(EVIDENCE)
    ids = registry['assignments'][0]['exercise_ids']
    current_evidence = b.source_evidence(snapshot, ids)
    assert len(saved_evidence['records']) == len(current_evidence['records']) == len(ids)
    for saved, current in zip(saved_evidence['records'], current_evidence['records']):
        for key, value in current.items():
            assert saved[key] == value, (saved['exercise_id'], key)
    selected = {row['exercise_id']: row for row in decisions['records']}
    all_ids = []
    for i, path in enumerate(BATCHES):
        batch = b.load(path)
        assert batch['status'] == 'ready' and batch['execution_order'] == i+1
        assert batch['exercise_count'] == len(batch['exercises']) == len(batch['exercise_ids'])
        assert 0 < batch['exercise_count'] <= 10
        assert batch['exercise_ids'] == [row['exercise_id'] for row in batch['exercises']]
        for row in batch['exercises']:
            eid = row['exercise_id']
            all_ids.append(eid)
            assert counts[eid] == 1
            for key, value in base.fields_for_id(eid, snapshot).items():
                assert row[key] == value, (eid, key)
            assert exclusion(eid, snapshot, assignments, approvals, True) is None, eid
            decision = selected[eid]
            assert decision['provided_user_paragraph'] == supplied[eid]['paragraph']
            assert decision['source_document_point'] == supplied[eid]['point']
            assert not decision['independently_verified_external_sources']
            assert decision['resolution_kind'] == 'user_selected_illustration_variant'
            assert not decision['catalog_modified'] and not decision['PNG_approval']
            assert row['technique_resolution']['user_selected_variant_decision'] == decision
            payload = row['prompt_payload']
            assert json.loads(row['generation_prompt'].split('\n', 1)[1]) == payload
            assert base.sha(row['generation_prompt'].encode()) == row['prompt_sha256']
            assert payload['identity_do_not_render_as_text']['exercise_id'] == eid
            for key in ['source_english', 'equipment', 'primary_muscle', 'secondary_muscles']:
                assert payload['exact_catalogue_source'][key] == row[key]
            assert row['scene'] == b.n.prior.scene(eid, SCENES[eid], CAMERAS.get(eid, b.CAMERA))
            assert payload['selected_render_scene'] == row['scene']
            assert payload['technique_resolution'] == row['technique_resolution']
            assert row['human_reference']['sha256'] == snapshot['reference_sha256']
            assert payload['human_reference'] == row['human_reference']
            for style in row['approved_style_files']:
                assert b.sha(style['path']) == style['sha256']
            assert payload['style']['version'] == row['style_version']
            if row['primary_muscle'] in ['full_body', 'cardio', 'other']:
                assert payload['style']['primary_highlight']['hex'] is None
                assert row['style_version'] == b.NEUTRAL_VERSION
            else:
                assert payload['style']['primary_highlight']['hex'] == '#F26445'
            assert payload['style']['secondary_highlight']['intensity_fraction'] == [0.4, 0.5]
            assert row['planned_png_path'] == f'{CLOUD}/{batch["batch_id"]}/{eid}/attempt-1.png'
            assert row['planned_git_png_path'] == f'{GIT}/{batch["batch_id"]}/{eid}/attempt-1.png'
            assert row['attempts'] == 0 and row['result_path'] is None and row['user_review'] is None
            assert routes[eid]['batch_id'] == batch['batch_id']
    assert all_ids == ids and len(all_ids) == len(set(all_ids)) == 13
    assert set(all_ids) == set(SCENES) and registry['assignment_count'] == 1
    manifest_ids = [row['exercise_id'] for batch in b.load(MANIFEST)['batches'] for row in batch['exercises']]
    assert manifest_ids == all_ids
    assert queue['current_blocked_ids'] == queue['current_equipment_blocked_ids'] == []
    assert b.load(BLOCKED)['exercise_count'] == 0
    return {'status': 'passed', 'exercise_count': 13, 'batch_counts': [b.load(path)['exercise_count'] for path in BATCHES],
            'batch_paths': BATCHES, 'generator_count': 1, 'catalog_ID_count': 451, 'language_blocks': 4448,
            'remaining_own_technique_blocked_count': 0, 'approved_intersections': [], 'PNG_intersections': [],
            'foreign_assignment_intersections': [], 'external_citation_URLs_verified': 0,
            'user_variant_decisions': 13, 'generation_calls': 0, 'PNG_pixels_reviewed': False,
            'live_commits': snapshot['commits'], 'errors': []}


def prepare(snapshot, source_file):
    assert base.git('branch', '--show-current').decode().strip() == base.BRANCH
    assert not (ROOT/REG).exists()
    source_bytes = pathlib.Path(source_file).read_bytes()
    provided = parsed_source(source_bytes.decode())
    assert set(provided) == set(SCENES)
    frozen = b.n.protected_files()
    old_queue = b.load(base.QUEUE_PATH)
    assert set(old_queue['current_blocked_ids']) | set(old_queue['current_equipment_blocked_ids']) == set(SCENES)
    numbers = [int(re.fullmatch(r'data/batches/agent-03-others-(\d+)\.json', path)[1])
               for tree in snapshot['trees'].values() for path in tree
               if re.fullmatch(r'data/batches/agent-03-others-(\d+)\.json', path)]
    first = max(numbers)+1
    paths = [f'data/batches/agent-03-others-{number:03}.json' for number in [first, first+1]]
    configure(paths)
    for path in paths+[SOURCE, DECISIONS, REG, MANIFEST, EVIDENCE, ERRORS, CHECK, BLOCKED]:
        assert not (ROOT/path).exists(), path
    approvals, _ = approval_audit.collect_review_evidence(snapshot)
    assignments = b.actual_assignments(snapshot)
    # User decisions resolve the old illustration blockers. Historical ledger is frozen.
    b.save(BLOCKED, {'schema_version': 1, 'exercise_count': 0, 'exercise_ids': [], 'exercises': [],
                    'resolved_by_user_document_path': SOURCE, 'historical_blocked_ledgers_unchanged': True,
                    'catalogue_contradictions_preserved_path': ERRORS, 'generation_calls': 0})
    for eid in SCENES:
        assert exclusion(eid, snapshot, assignments, approvals) is None, (eid, exclusion(eid, snapshot, assignments, approvals))
    (ROOT/SOURCE).write_bytes(source_bytes)
    decisions = {
        'schema_version': 1, 'catalog_sha256': snapshot['catalog_sha256'],
        'source_document': {'path': SOURCE, 'sha256': base.sha(source_bytes),
                            'uploaded_file_id': 'file_00000000990c8210bc5e5cdb43edc36c',
                            'original_filename': 'Вставлений текст.txt', 'type': 'user_supplied_variant_instructions'},
        'external_citations': {'status': 'unresolved_chatgpt_content_reference_placeholders',
                               'URL_count': 0, 'independent_verification_claimed': False},
        'equipment_choices_next_stage': {}, 'records': [], 'generation_calls': 0,
    }
    for eid in SCENES:
        decisions['records'].append({
            'exercise_id': eid, 'name': snapshot['by_id'][eid]['name'], 'status': 'resolved_for_illustration',
            'resolution_kind': 'user_selected_illustration_variant',
            'source_document_path': SOURCE, 'source_document_sha256': base.sha(source_bytes),
            'source_document_point': provided[eid]['point'], 'provided_user_paragraph': provided[eid]['paragraph'],
            'citation_placeholders': re.findall(r':chatgpt-content-reference\{[^}]+\}', provided[eid]['paragraph']),
            'independently_verified_external_sources': [],
            'selected_scene': list(SCENES[eid]), 'selected_camera': CAMERAS.get(eid, b.CAMERA),
            'source_catalog_record_sha256': base.value_sha(snapshot['by_id'][eid]),
            'render_precedence': 'User-selected scene governs pose/equipment where raw catalogue or dataset conflicts. Raw source texts remain provenance, not conflicting render instructions. Exact catalogue ID/name/equipment category/muscles remain unchanged.',
            'catalog_modified': False, 'PNG_approval': False,
        })
    b.save(DECISIONS, decisions)
    evidence = b.source_evidence(snapshot, list(SCENES))
    evidence.update(audited_commits=snapshot['commits'], user_variant_decisions_path=DECISIONS,
                    source_binding_is_not_technique_confirmation=True, external_URLs_verified=0,
                    photos_or_video_downloaded=False, images_reviewed=False)
    b.save(EVIDENCE, evidence)
    b.save(ERRORS, {'schema_version': 1, 'catalog_sha256': snapshot['catalog_sha256'], 'catalog_modified': False,
                   'records': [{'exercise_id': eid, 'raw_english': copy.deepcopy(snapshot['by_id'][eid]['content']['en']),
                                'conflicting_catalogue_fields': {f'/content/en/{key}': copy.deepcopy(snapshot['by_id'][eid]['content']['en'][key]) for key in CONFLICT_FIELDS.get(eid, [])},
                                'original_dataset_english': next(row['original_dataset_english'] for row in evidence['records'] if row['exercise_id'] == eid),
                                'resolution_kind': 'user_selected_illustration_variant', 'decision_path': DECISIONS,
                                'user_selected_scene': list(SCENES[eid]),
                                'catalogue_issue_state': 'preserved_not_repaired' if eid in CONFLICT_FIELDS else 'specified_construction_or_variant',
                                'scope': 'Render the user-selected variant only; this is not an independent source confirmation, catalogue correction or PNG acceptance.'}
                               for eid in SCENES]})
    batches = []
    by_decision = {row['exercise_id']: row for row in decisions['records']}
    for i, path in enumerate(paths):
        bid = pathlib.Path(path).stem
        ids = list(SCENES)[i*10:(i+1)*10]
        rows = []
        for eid in ids:
            row = p.route(p.make_equipment_row(eid, snapshot, evidence), bid, snapshot)
            row['scene'] = b.n.prior.scene(eid, SCENES[eid], CAMERAS.get(eid, b.CAMERA))
            resolution = {'status': 'resolved_for_illustration', 'decision_kind': 'user_selected_illustration_variant',
                          'user_selected_variant_decision': copy.deepcopy(by_decision[eid]),
                          'evidence_path': EVIDENCE, 'evidence_selector': f'records[exercise_id="{eid}"]',
                          'technique_fields_read': ['content.en.description', 'content.en.instructions', 'content.en.form_cues', 'content.en.common_mistakes', 'content.en.safety_note'],
                          'dataset_instruction_steps_read': next(r['original_dataset_english'] for r in evidence['records'] if r['exercise_id'] == eid),
                          'binding_or_name_alone_is_not_confirmation': True, 'independent_external_confirmation': False,
                          'preserved_source_errors_path': ERRORS, 'catalog_modified': False, 'PNG_approval': False}
            row['technique_resolution'] = resolution
            row['prompt_payload'].update(selected_render_scene=copy.deepcopy(row['scene']), technique_resolution=copy.deepcopy(resolution),
                                         source_use_rule=by_decision[eid]['render_precedence'])
            row['prompt_payload']['style']['no_invention'] = 'Exact ID catalogue controls source text and muscles; explicit supplied user variant controls the derived render scene. Do not mix contradictory raw pose instructions into the selected scene or add muscles from external sources.'
            row['generation_prompt'] = 'Create exactly ONE square 1024x1024 transparent PNG of this exact exercise and ONE selected phase. Metadata must never appear as image text.\n'+json.dumps(row['prompt_payload'], ensure_ascii=False, sort_keys=True, indent=2)
            row['prompt_sha256'] = base.sha(row['generation_prompt'].encode())
            rows.append(row)
        batch = {'schema_version': 1, 'batch_id': bid, 'status': 'ready', 'exercise_count': len(rows),
                 'exercise_ids': ids, 'exercises': rows, 'source_branch': base.BRANCH,
                 'generator': ROLE, 'execution_branch': WORKER, 'assignment_registry_path': REG,
                 'execution_order': i+1, 'catalog_sha256': snapshot['catalog_sha256'],
                 'audited_commits': snapshot['commits'], 'generation_calls': 0,
                 'handoff_path': HANDOFF, 'manifest_path': MANIFEST, 'live_recheck_before_every_call': True}
        b.save(path, batch)
        batches.append(batch)
    ids = list(SCENES)
    b.save(REG, {'schema_version': 1, 'assignment_id': ROUND, 'source_branch': base.BRANCH,
                'source_base_commit': snapshot['commits']['HEAD'], 'status': 'ready',
                'catalog_sha256': snapshot['catalog_sha256'], 'exercise_count': len(ids), 'assignment_count': 1,
                'batch_paths': paths, 'assignments': [{'generator': ROLE, 'execution_branch': WORKER,
                    'status': 'assigned', 'exercise_count': len(ids), 'exercise_ids': ids, 'batch_paths': paths,
                    'execution_order': [1, 2], 'manifest_path': MANIFEST, 'handoff_path': HANDOFF}],
                'execution_gate': 'Continue after existing 037–040 and all prior taken tasks. No revision jobs or transfer of older three missing-PNG assignments.',
                'audited_commits': snapshot['commits'], 'supersedes_other_agents': False,
                'generation_calls_by_preparer': 0, 'decisions_path': DECISIONS, 'user_document_path': SOURCE,
                'results_git_root': GIT, 'results_cloud_root': CLOUD,
                'scope_limit': 'Pushed Git only; unpushed results/approvals/live calls may be unavailable. Recheck before every call.'})
    b.save(MANIFEST, {'schema_version': 1, 'manifest_id': ROUND, 'source_branch': base.BRANCH,
                     'execution_branch': WORKER, 'generator': ROLE, 'assignment_path': REG,
                     'status': 'ready_not_started', 'exercise_count': len(ids), 'generation_calls': 0,
                     'user_review_policy': 'pending after PNG creation until explicit user approval',
                     'quota_rule': 'Save the first quota/rate-limit failure, push checkpoint and stop without retries.',
                     'batches': [{'batch_id': batch['batch_id'], 'batch_path': path, 'status': 'ready',
                        'exercise_count': batch['exercise_count'], 'exercises': [{'exercise_id': row['exercise_id'],
                            'name': row['name'], 'status': 'not_started', 'attempts': 0, 'attempt_history': [],
                            'user_review': None, 'technical_check': None, 'agent_visual_review': 'not_performed',
                            'result_path': None, **{key: row[key] for key in ['planned_png_path', 'planned_git_png_path', 'prompt_sha256', 'source_catalog_sha256', 'style_version']}}
                            for row in batch['exercises']]} for path, batch in zip(paths, batches)]})
    queue = copy.deepcopy(old_queue)
    for row in [row for batch in batches for row in batch['exercises']]:
        assert row['exercise_id'] not in queue['eligible_exercise_ids']
        queue['exercises'].append({key: copy.deepcopy(row[key]) for key in ['exercise_id', 'name', 'equipment', 'primary_muscle', 'secondary_muscles', 'source_catalog_sha256', 'source_catalog_record_sha256', 'source_english_sha256', 'status', 'assigned_generator', 'batch_id', 'prompt_prepared', 'style_version', 'assignment_registry_path']})
        queue['exercises'][-1]['current_task_path'] = f'data/batches/{row["batch_id"]}.json'
        queue['eligible_exercise_ids'].append(row['exercise_id'])
    queue['batch_paths'].extend(paths)
    queue.update(updated_at=p.now(), prepared_count=len(queue['eligible_exercise_ids']),
                 eligible_count=len(queue['eligible_exercise_ids']), latest_launch_ids=ids,
                 current_blocked_ids=[], current_equipment_blocked_ids=[], current_equipment_blocked_count=0,
                 current_technique_blocked_path=BLOCKED, current_equipment_blocked_path=BLOCKED,
                 current_equipment_blocked_selector='exercises')
    queue['final13_user_variant_preparation'] = {'assignment_path': REG, 'batch_paths': paths,
        'exercise_count': 13, 'generator': ROLE, 'execution_branch': WORKER, 'handoff_path': HANDOFF,
        'source_decisions_path': DECISIONS, 'catalogue_conflicts_path': ERRORS, 'generation_calls': 0}
    queue['phase_plan']['latest_equipment_allocation_path'] = REG
    queue['phase_plan']['equipment_clarifications_path'] = BLOCKED
    queue['phase_plan']['phase2_execution_gate'] = 'Existing 037–040 first, then the final13 continuation for the same single worker. Three older no-PNG assignments and unconfirmed revision planning queue are unchanged; protect all approved IDs.'
    b.save(base.QUEUE_PATH, queue)
    with (ROOT/'.gitignore').open('a') as file:
        file.write('\n# Exact pending paths for final13 user-selected variants.\n')
        for batch in batches:
            for row in batch['exercises']:
                file.write('!/'+row['planned_git_png_path']+'\n')
    b.save(CHECK, {'schema_version': 1, 'protected_sha256': frozen,
                   'previous_queue_routes_sha256': {row['exercise_id']: base.value_sha(row) for row in old_queue['exercises']}})
    result = validate(snapshot)
    report = b.load(CHECK)
    report.update(result, checked_at=p.now())
    b.save(CHECK, report)
    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--fetch', action='store_true')
    parser.add_argument('--prepare', action='store_true')
    parser.add_argument('--source-file')
    args = parser.parse_args()
    if args.fetch:
        b.fetch_heads()
    snapshot = b.n.snapshot()
    result = prepare(snapshot, args.source_file) if args.prepare else validate(snapshot)
    print(json.dumps(result, ensure_ascii=False, indent=2))
