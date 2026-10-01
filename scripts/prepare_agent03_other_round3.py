#!/usr/bin/env python3
"""Exact-ID preparation/check of batches 007–009; no generation or shared writes.

Fetch current work and all other agent branches before running. --prepare never
overwrites an existing batch. --check is read-only and checks fresh Git snapshots.
"""
import argparse
import collections
import copy
import datetime
import json
import subprocess
import sys

import prepare_agent03_other_queue as base

ROOT = base.ROOT
OLD_PATHS = [f'data/batches/agent-03-others-{n:03}.json' for n in range(1, 7)]
NEW_IDS = [f'agent-03-others-{n:03}' for n in range(7, 10)]
NEW_PATHS = {bid: f'data/batches/{bid}.json' for bid in NEW_IDS}
REPORT_PATH = 'data/queues/agent-03-other-round3-validation.json'
HANDOFF_PATH = 'docs/agent-03-other-round3-handoff.md'
HEADER = 'Create exactly one image for the following exact exercise record. Identity fields are metadata, never visible text. Preserve the source technique and depict only the chosen single phase.\n'

# Full source data is always obtained through by_id[exercise_id]. These authored
# scenes select permitted variants/phases; they never edit source English fields.
SCENES = {
    'single-arm-triceps-extension-dumbbell': ('Supported one-arm behind-head lower phase', "Sit on a bench with back straight and feet flat. One hand holds the ONLY dumbbell overhead and lowers it behind the head through elbow flexion; that upper arm remains near the head and elbow points forward. The other hand contacts the bench for support. Keep trunk against bench support as the source cue requires; no invented backrest angle, two-handed dumbbell grip, shoulder press or forced lockout. Show the supporting hand and working elbow clearly.", [0, 1, 2, 3, 4]),
    'single-leg-hip-thrust-dumbbell': ('Loaded single-leg hip-extension top', "Upper back contacts the edge of a stable FLAT bench. One foot is planted, and one dumbbell lies across that SAME loaded hip, held securely by the hands. The other leg extends forward without floor contact. Drive through planted heel until loaded hip is fully extended, pelvis level and support points fixed. Show the bench edge, planted foot, extended free leg and single dumbbell; no two-foot bridge or lying lengthwise on the bench.", [0, 1, 2, 3]),
    'single-leg-romanian-deadlift-barbell': ('Left-foot hip hinge with right leg reaching back', "LEFT foot is the only floor contact, left knee slightly bent. RIGHT leg extends behind for balance as the torso hinges forward with a straight back. Both hands hold a single free barbell OVERHAND, lowered close to the body toward the ground. Preserve exact source sides, grip and single-leg balance. Stop before rounding; no floor-reset conventional deadlift, second grounded foot or bench support. No invented numeric hinge angle or grip width.", [0, 1, 2, 3, 4]),
    'skullcrusher-barbell': ('Bar just above forehead with upper arms fixed', "Lie on a flat bench with feet planted. Hold one barbell overhand with both hands. Upper arms remain nearly vertical while elbows bend to bring the bar JUST ABOVE the forehead, not behind the head. No face contact, elbow flare, shoulder motion or ordinary chest press. Include standard stationary safety supports as the source safety alternative, with no spotter figure or guided Smith rails. Show the whole bench and bar clearance.", [0, 1, 2, 3]),
    'skullcrusher-dumbbell': ('Two dumbbells lowered beside forehead', "Lie on a flat bench, feet planted, one light dumbbell in each hand. Upper arms remain vertical; both elbows flex so weights approach the SIDES of forehead and pause clear of the face and bench edges. Wrists neutral, elbows toward ceiling, both arms moving evenly. Show two separate weights, fixed upper arms and full bench; no single barbell, behind-head overhead extension or shoulder-driven press.", [0, 1, 2, 3]),
    'spider-curl-barbell': ('Prone supported underhand curl toward shoulders', "Lie face down on an incline bench, chest continuously on pad and feet on floor. Both hands grip one barbell UNDERHAND. Upper arms hang perpendicular to floor and remain fixed while elbows curl the bar toward shoulders. Show bench support, source hand orientation and whole bar without chest lift or swing. No preacher pad, standing curl or invented numerical incline angle.", [0, 1, 2, 3]),
    'squat-barbell': ('Controlled near-parallel back squat', "One free barbell rests across upper back, steadied by both hands. Feet approximately shoulder-width, heels grounded. Hips and knees bend until thighs near parallel; knees track toes and trunk remains braced with neutral back. Include a stationary rack as the source safety option, no Smith guides or leg-press machine. Show full bar, figure and both floor contacts; no bounce or front-held bar.", [0, 1, 2, 3]),
    'standing-calf-raise-barbell': ('Even bilateral heel-rise top with upper-back bar', "Stand approximately shoulder-width with one free barbell across upper back held securely by both hands. Both heels rise evenly while the balls of both feet remain on the floor, ankles vertically aligned over feet and knees not bending for momentum. Show controlled heel elevation, full bar and floor contacts; no tiptoe-only balancing, step platform, calf machine or guided rails. Use a light controllable load and stationary rack available only for balance as permitted by source safety.", [0, 1, 2]),
    'standing-military-press-barbell': ('Strict standing overhead endpoint', "Both feet planted and knees quiet, abdomen and glutes braced. Both hands hold one free barbell just outside shoulder width overhead, after head has moved slightly back then under the bar. Elbows extend as described without leg assistance or backward lean; ribs stacked over hips. Show a stationary return rack per source safety, not a guided press machine. Full arms, bar and feet remain in frame.", [0, 1, 2, 3]),
    'straight-leg-deadlift-barbell': ('Small-knee-bend hip-hinge lower endpoint', "Stand hip-width and hold one free barbell OVERHAND close to legs. Knees remain SOFTLY BENT as hips travel backward and long neutral spine hinges forward, stopping at controlled hamstring stretch. Show source's small knee bend despite the exercise name; no locked knees, squat-depth bend, lumbar rounding or invented numerical depth. No equipment beyond free bar and floor contacts.", [0, 1, 2, 3]),
    'sumo-deadlift-barbell': ('Wide toes-out braced lifting setup', "Stand over one free barbell with feet WIDE and toes outward. Both hands grip the bar INSIDE the knees. Hips and knees are bent in the controlled setup before extending together, chest lifted and neutral trunk braced. Show wide stance, hands inside legs, grounded feet and full bar close to body; no narrow conventional stance, back squat bar placement or forced specific grip orientation absent from source.", [0, 1, 2, 3]),
    'sumo-squat-barbell': ('Wide toes-out controlled squat lower phase', "One barbell lies across UPPER BACK, held securely by both hands. Feet wider than shoulder width, toes outward, heels grounded. Lower by bending hips and knees, knees following toes, until thighs approach parallel or source's deepest controlled position. Torso stays braced; show stationary rack as source safety option. No between-leg deadlift grip, Smith guides, knee collapse or invented numerical depth.", [0, 1, 2, 3]),
    'upright-row-barbell': ('Overhand row near upper chest with elbows leading', "Stand shoulder-width, torso upright and abdomen braced. Both hands grip one barbell OVERHAND. Bar travels close to torso toward upper chest, elbows leading UP AND OUT and wrists remaining below elbows. Stop within comfortable shoulder range, shoulders not shrugged first. Show full free bar and body without hip swing, overhead press or invented grip width.", [0, 1, 2, 3]),
    'wide-elbow-triceps-press-dumbbell': ('Wide-elbow dumbbells lowered toward shoulders', "Lie flat on a bench with feet planted, shoulders supported. One LIGHT dumbbell per hand lowers toward shoulders as elbows bend OUTWARD, visibly wider than a close press, at comfortable upper-arm depth. Wrists stacked and elbow width controlled. Show this distinct wide-elbow lower phase and both weights; no ordinary narrow skullcrusher, forced painful flare, bounce or shoulder press.", [0, 1, 2, 3]),
    'zercher-squat-barbell': ('Padded bar cradled in elbow creases at controlled squat depth', "Stand shoulder-width with one PADDED barbell cradled in the crooks of BOTH bent elbows, close to body. Brace abdomen and bend hips and knees with chest lifted and heels planted until thighs reach the controlled endpoint. Show actual elbow-crease bar support, flexed elbows and knees following toes. No upper-back bar, hands-only front rack, lumbar rounding or invented numerical depth.", [0, 1, 2, 3]),
    'band-pullaparts-resistance-band': ('Shoulder-height pull-apart with band at chest line', "Choose the standing variant explicitly permitted by source. Both hands hold the SAME light resistance band near shoulder height with arms long and elbows softly unlocked. Hands have moved apart as shoulder blades squeeze until band reaches chest line. Torso tall, ribs controlled, shoulders down. Show the band between hands under tension; no wall anchor, elbow-bent row, weight machine or snapping band.", [0, 1, 2, 3]),
    'chest-dip-machine': ('Slightly inclined bodyweight dip lower phase on parallel bars', "Support one man between two STABLE PARALLEL HANDLES by his hands. Torso slightly inclined, elbows bent until upper arms approach parallel to floor, shoulders down and legs still clear of floor. Show full bars and hand contacts, no extra load, cable, weight stack, assistance platform engaged or guided dip machine. The literal equipment enum machine is retained in metadata; source motion specifies fixed parallel supports. Stop before shoulder control is lost.", [0, 1, 2, 3]),
    'chinup-machine': ('Strict underhand chin-above-bar top', "Hang/pull on a SECURE FIXED BAR, both hands UNDERHAND about shoulder-width. Chin has cleared bar without neck craning; elbows toward ribs, ribs down and legs quiet off floor. Show one stationary overhead bar/support and full body, no cable pulldown, weight stack, kip or added load. Preserve underhand source grip despite generic machine enum.", [0, 1, 2, 3]),
    'chinup-weighted-machine': ('Underhand chin-up top with centered weighted vest', "Choose the WEIGHTED VEST alternative explicitly permitted in source; secure a conservative centered vest load to torso. Both hands grip a fixed bar UNDERHAND, elbows toward ribs and chin clears bar with shoulders active, legs still and no swing. Show full fixed bar, vest and figure; no belt or dangling plate added to this chosen vest variant, no pulldown machine, extra weights or invented load number.", [0, 1, 2, 3]),
    'clamshell-resistance-band': ('Side-lying top knee opened with feet together', "Loop band is ABOVE knees. Lie on one side with hips and knees bent about source's 45 degrees, hips stacked and feet touching. Top knee opens against band while pelvis stays still and abdomen braced. Show both contacting feet, band position and bent legs on floor; no pelvis rolled backward, feet separated, ankle band or standing abduction machine.", [0, 1, 2, 3]),
    'dead-hang': ('Static active-shoulder hold on secure overhead bar', "Both hands grip a secure OVERHEAD BAR; arms straight and feet completely clear of floor. Shoulders gently down away from ears, neck relaxed, ribs and pelvis controlled, body still. Show full figure, actual hand-bar contacts and stationary bar support within frame. No bend-elbow pull-up, swing, shrug, invented hand-spacing or grip orientation. Depict hold, not release or landing.", [0, 1, 2, 3]),
    'hanging-knee-raise': ('Bent knees raised toward torso without swing', "Both hands contact a secure overhead bar, arms straight and shoulders active. From still hang, both BENT knees rise toward torso at controlled top range, abdomen braced and trunk not swinging. Show hand-bar contacts, bent knees, feet clear of floor and full bar support. No straight-leg variation, kipping, elbow-supported captain's chair, invented grip direction or target height.", [0, 1, 2, 3]),
    'hanging-leg-raise': ('Straight legs lifted forward from quiet hang', "Both hands grip a secure overhead bar, arms straight, shoulders depressed. Legs stay TOGETHER AND STRAIGHT as they lift in front of body only within controlled pelvic range. No bent knees, back arch or swing. Show all hand contacts, full legs and secure static bar; no unsupported invented exact lift angle or knee-raise station.", [0, 1, 2, 3]),
    'jack-knife-suspension': ('Feet-in-straps knee draw with controlled hip pike', "Both feet remain SECURE in low suspension foot straps. Both hands contact floor directly under shoulders. From the source high-plank start, knees draw toward chest as hips lift into a controlled PIKE; shoulders controlled and hands stay fixed. Show hands, bent knees, feet inside loops and low suspension straps attached to a standard secure fixed anchor, whose brand/dimensions are not prescribed. No feet-on-floor plank, hand-held straps, swinging straps or straight-knee-only substitute for the specified knee draw.", [0, 1, 2, 3]),
    'kipping-pullup-machine': ('Chin-clearing pull after a compact coordinated kip', "Both hands grip a secure pull-up bar OVERHAND, shoulders active. Show the source chin-above-bar pull phase as elbows drive down following a compact hollow-to-slight-arch kip; hips rise with the pull and legs remain controlled. One pose only, no motion sequence or arrows. Full fixed bar and figure visible, no wild knee kick, cable pulldown or invented swing angle. Keep complete hollow/arch sequence in source metadata.", [0, 1, 2, 3]),
    'knee-raise-parallel-bars-machine': ('Straight-arm parallel-bar support with knees toward chest', "Both palms support body on STABLE PARALLEL BARS, elbows straight and shoulders down. Feet clear of floor as both bent knees rise toward chest together without torso swing. Show both hand contacts, straight supporting arms and complete bars. No forearm pads, back pad, captain's chair, overhead hanging bar, weight stack or additional machine parts absent from the source.", [0, 1, 2, 3]),
    'kneeling-pulldown-band-machine': ('Tall kneeling band pull toward upper chest', "Kneel facing a SECURE OVERHEAD BAND ANCHOR, trunk tall with ribs over pelvis. Both hands grip the resistance band and pull until hands approach upper chest, elbows DOWN toward ribs rather than behind back. Show grounded kneeling contacts, the band path to its overhead anchor and actual grips. One elastic band arrangement, no cable, pulley, weight stack or seat despite machine enum. No backward lean or invented anchor height.", [0, 1, 2, 3]),
    'lat-pulldown-band-resistance-band': ('Standing underhand band pull toward chest', "Choose the source's high PULL-UP BAR anchor example and attach resistance band securely to it. Stand facing that anchor, feet shoulder-width. Both hands grip BAND UNDERHAND, slightly wider than shoulder width, pulling down toward chest as shoulder blades squeeze. Torso braced and ribs stacked, no lean or swing. Show full high anchor, elastic band and both grip contacts; no cable bar, machine handles, seated station or invented numeric anchor height. The standing band instructions select the concrete variant within the generic description.", [0, 1, 2, 3, 4]),
    'lateral-band-walks-resistance-band': ('Controlled side-step with loop above knees', "Choose the ABOVE-KNEES loop-band alternative explicitly allowed in source. Lower into a shallow athletic stance, torso neutral and toes forward. One foot has stepped sideways while the other remains supported; keep band tension, hips low and knees tracking outward. Show the loop location, both feet and stable side-step, not dragging feet together, ankle-band variant or upright marching. No invented step distance or load.", [0, 1, 2, 3]),
    'lateral-raise-band-resistance-band': ('Hands out near shoulder height with band under feet', "Stand ON the resistance band with feet shoulder-width and grip its two ENDS, one in each hand. Both elbows slightly bent, hands raised to either side near shoulder height in frontal plane. Trunk braced, elbows leading and shoulders down. Show band anchored by both feet and tensioned to both hands. No machine pads, separate wall anchor, dumbbells or above-range shrug; the exact band instructions choose the variant in generic description.", [0, 1, 2, 3]),
}

def load(path):
    return json.loads((ROOT / path).read_text())

def save(path, data):
    (ROOT / path).write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n')

def configure():
    base.BATCH_PATHS = NEW_PATHS
    base.SCENES = SCENES
    # Scan every fetched agent branch; own HEAD covers the preserved old batches.
    refs = base.git('for-each-ref', '--format=%(refname:short)', 'refs/remotes/origin/').decode().splitlines()
    base.REFS = ['origin/work'] + sorted(r for r in refs if r.startswith('origin/agent-') and r != 'origin/' + base.BRANCH) + ['HEAD']

def protected_hashes():
    paths = OLD_PATHS + [base.CATALOG_PATH, base.PROGRESS_PATH, base.INVENTORY_PATH,
                        base.CLARIFICATIONS_PATH, base.VALIDATION_PATH, base.HANDOFF_PATH,
                        'docs/agent-03-other-next-handoff.md', 'docs/agent-03-other-clarifications-explained.md',
                        'data/queues/agent-03-other-next-validation.json']
    return {p: base.sha((ROOT / p).read_bytes()) for p in paths}

def candidates(queue, s):
    available, excluded = [], []
    for eid in queue['remaining_unprepared_ids']:
        reason, detail = base.readiness(s['by_id'][eid], s)
        if reason == 'eligible': available.append(eid)
        else: excluded.append({'exercise_id': eid, 'name': s['by_id'][eid]['name'], 'reason_code': reason,
                               'details': detail, 'png_sources': s['png_sources'].get(eid, []),
                               'reservation_sources': s['reserved'].get(eid, []), 'progress_sources': s['touched'].get(eid, [])})
    return available, excluded

def validate(s, queue, batches, protected):
    errors, seen, checked = [], set(), []
    old_ids = [eid for path in OLD_PATHS for eid in load(path)['exercise_ids']]
    if len(old_ids) != 60 or len(set(old_ids)) != 60: errors.append('old_IDs_invalid')
    round3 = queue['preparation_rounds'][-1]
    input_ids = round3['input_remaining_ids']
    blocked = {r['exercise_id'] for r in round3['excluded_since_previous_round']}
    expected_available = [eid for eid in input_ids if eid not in blocked]
    expected_new = expected_available[:30]
    expected_rest = expected_available[30:]
    for i, batch in enumerate(batches):
        bid = batch['batch_id']; rows = batch['exercises']
        if bid != NEW_IDS[i] or batch['catalog_sha256'] != s['catalog_sha256'] or batch['style_sha256'] != s['style_sha256'] or batch['style_version'] != 'v1':
            errors.append('batch_identity_or_source_mismatch:' + bid)
        if len(rows) != len(expected_new[i*10:(i+1)*10]) or batch['exercise_count'] != len(rows): errors.append('batch_size_mismatch:' + bid)
        if batch['exercise_ids'] != [r['exercise_id'] for r in rows]: errors.append('batch_ID_list_mismatch:' + bid)
        for row in rows:
            eid = row['exercise_id']; checked.append(eid)
            if eid in seen: errors.append('duplicate_new_ID:' + eid)
            seen.add(eid)
            if eid in old_ids: errors.append('old_assigned_ID:' + eid)
            if eid not in s['by_id']: errors.append('missing_ID:' + eid); continue
            for key, value in base.fields_for_id(eid, s).items():
                if row.get(key) != value: errors.append('catalog_field_mismatch:' + eid + ':' + key)
            reason, _ = base.readiness(s['by_id'][eid], s)
            if reason != 'eligible': errors.append('unavailable_ID:' + eid + ':' + reason)
            if eid not in SCENES: errors.append('missing_reviewed_scene:' + eid); continue
            payload = base.payload_for_id(eid, s)
            prompt = HEADER + json.dumps(payload, ensure_ascii=False, sort_keys=True, indent=2)
            if row.get('prompt_payload') != payload or row.get('generation_prompt') != prompt or row.get('generation_prompt_sha256') != base.sha(prompt.encode()):
                errors.append('prompt_binding_mismatch:' + eid)
            expected_relative = f'{bid}/{eid}/attempt-1.png'
            if row.get('planned_output_relative_path') != expected_relative or row.get('output_root') != '/workspace/exercise-image-results' or row.get('planned_png_path') != '/workspace/exercise-image-results/' + expected_relative:
                errors.append('PNG_binding_mismatch:' + eid)
            if row.get('attempts') != 0 or any(row.get(k) is not None for k in ['user_review', 'result_path', 'result_sha256', 'technical_check']):
                errors.append('preparation_claims_execution:' + eid)
    if checked != expected_new or len(seen) != len(expected_new) or queue['latest_launch_ids'] != expected_new:
        errors.append('next_IDs_or_order_mismatch')
    if queue['remaining_unprepared_ids'] != expected_rest: errors.append('remaining_order_mismatch')
    all_ids = queue['eligible_exercise_ids']
    if len(all_ids) != len(set(all_ids)) or set(all_ids) != set(old_ids + checked + expected_rest): errors.append('queue_partition_mismatch')
    if queue['eligible_count'] != len(all_ids) or queue['prepared_count'] != 60+len(checked) or queue['remaining_unprepared_count'] != len(expected_rest): errors.append('queue_counts_mismatch')
    old_batches = {eid: path.rsplit('/', 1)[-1][:-5] for path in OLD_PATHS for eid in load(path)['exercise_ids']}
    new_batches = {eid: batch['batch_id'] for batch in batches for eid in batch['exercise_ids']}
    for row in queue['exercises']:
        eid = row['exercise_id']
        if eid not in s['by_id']: errors.append('unknown_queue_ID:' + eid); continue
        source = base.fields_for_id(eid, s)
        for key in ['name', 'equipment', 'primary_muscle', 'secondary_muscles', 'source_catalog_sha256', 'source_catalog_record_sha256', 'source_english_sha256']:
            if row.get(key) != source[key]: errors.append('queue_field_mismatch:' + eid + ':' + key)
        if eid in expected_rest:
            if base.readiness(s['by_id'][eid], s)[0] != 'eligible': errors.append('remaining_ID_unavailable:' + eid)
            if row.get('prompt_prepared') or row.get('batch_id') or any(k in row for k in ['prompt', 'generation_prompt', 'prompt_payload']): errors.append('unprepared_ID_has_prompt_or_batch:' + eid)
        elif row.get('batch_id') != {**old_batches, **new_batches}.get(eid) or row.get('prompt_prepared') is not True:
            errors.append('queue_batch_binding_mismatch:' + eid)
    if queue['first_launch_ids'] != old_ids[:30] or queue['next_launch_ids'] != old_ids[30:]: errors.append('historical_launch_IDs_changed')
    if queue['catalog_sha256'] != s['catalog_sha256'] or queue['style_sha256'] != s['style_sha256']: errors.append('queue_source_changed')
    for path, expected_hash in protected.items():
        if base.sha((ROOT / path).read_bytes()) != expected_hash: errors.append('protected_file_changed:' + path)
    return {'schema_version': 1, 'status': 'failed' if errors else 'passed', 'errors': errors,
            'checked_at_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
            'audited_commits': s['commits'], 'catalog_sha256': s['catalog_sha256'], 'style_version': 'v1', 'style_sha256': s['style_sha256'],
            'unique_catalog_IDs': len(s['by_id']), 'new_batch_ID_count': len(seen), 'old_reserved_ID_count': len(set(old_ids)),
            'remaining_without_prompts': len(expected_rest), 'excluded_since_previous_round': round3['excluded_since_previous_round'],
            'checked_exercise_ids': checked, 'protected_sha256': protected, 'source_files': s['source_files'],
            'checks': ['catalog_IDs_exist_once', 'source_fields_equal_exact_ID_record', 'prompt_source_text_and_hash_equal_exact_ID',
                       'PNG_paths_bound_to_ID', 'new_IDs_disjoint', 'no_001_to_006_overlap', 'no_other_assignment_or_PNG_or_attempt',
                       'active_other_only_no_unresolved_clarifications', 'rest_without_prompts', 'protected_files_unchanged'],
            'scope_limit': queue['scope_limit']}

def negative_checks(s, queue, batches, protected):
    cases = {}
    if not any(b['exercises'] for b in batches): return cases
    mutations = {
        'wrong_name': lambda b: b[0]['exercises'][0].update(name='deliberately wrong test name'),
        'wrong_English_ID': lambda b: b[0]['exercises'][0].update(source_english=s['by_id']['bench-press-barbell']['content']['en']),
        'wrong_equipment': lambda b: b[0]['exercises'][0].update(equipment='cable'),
        'wrong_muscles': lambda b: b[0]['exercises'][0].update(primary_muscle='cardio'),
        'wrong_catalog_SHA': lambda b: b[0]['exercises'][0].update(source_catalog_sha256='0'*64),
        'wrong_style': lambda b: b[0].update(style_version='v999'),
        'old_assigned_ID': lambda b: b[0]['exercises'][0].update(exercise_id=load(OLD_PATHS[0])['exercise_ids'][0]),
        'wrong_prompt': lambda b: b[0]['exercises'][0].update(generation_prompt='wrong exercise prompt'),
        'wrong_PNG_ID': lambda b: b[0]['exercises'][0].update(planned_png_path='/workspace/exercise-image-results/wrong-id.png'),
    }
    if len(batches[1]['exercises']):
        mutations['duplicate_between_batches'] = lambda b: b[1]['exercises'].__setitem__(0, copy.deepcopy(b[0]['exercises'][0]))
    for name, mutate in mutations.items():
        bad = copy.deepcopy(batches); mutate(bad)
        cases[name] = validate(s, queue, bad, protected)['status'] == 'failed'
    for name, field in [('foreign_assignment', 'reserved'), ('new_saved_PNG', 'png_sources')]:
        bad = copy.deepcopy(s); bad[field][batches[0]['exercise_ids'][0]].append({'branch': 'synthetic_test_only'})
        cases[name] = validate(bad, queue, batches, protected)['status'] == 'failed'
    if not all(cases.values()): raise ValueError('Negative guard failed: ' + repr(cases))
    return cases

def handoff(s, queue, batches, report):
    n = report['new_batch_ID_count']; rest = queue['remaining_unprepared_count']
    old_ids = [eid for path in OLD_PATHS for eid in load(path)['exercise_ids']]
    saved_old = {eid: s['png_sources'].get(eid, []) for eid in old_ids if eid in s['png_sources']}
    lines = ['# Agent-03: раунд 3 — пакети 007–009, тільки підготовка', '',
             f'Власна гілка `{base.BRANCH}`. Work `{s["commits"]["origin/work"]}`. Інші перевірені commits: `{json.dumps(s["commits"], ensure_ascii=False)}`.', '',
             f'Каталог SHA256 `{s["catalog_sha256"]}`. Стиль v1 SHA256 `{s["style_sha256"]}`.', '',
             f'У вхідній черзі {len(queue["preparation_rounds"][-1]["input_remaining_ids"])} ID. Після актуальної перевірки виключено {len(report["excluded_since_previous_round"])}. Підготовлено **{n}** вправ у пакетах по максимум 10; **{rest}** залишаються без prompts. Нестача до 30: {30-n}.', '',
             f'Усі 60 ID пакетів 001–006 зарезервовані й не включені повторно. У work вже збережено PNG для {len(saved_old)} з цих ID; це зафіксовано окремо у queue Git-зрізі. Власні файли 001–006 збережено байт-у-байт. Каталог, shared progress, старі handoff, manifests і результати не змінено.', '',
             'Відбір: тільки active inventory group other, без PNG, спроб, поданого pending/rejected/approved результату, іншого batch/manifest/index/clarification призначення або невирішеного уточнення. Untouched not_started/attempts=0 без output/history і з legacy default pending не є поданим результатом; це правило попередньої інвентаризації.', '',
             'Категорію machine не трактувати як точну конструкцію. chest-dip/chinup/kipping-pullup/knee-raise-parallel-bars задають статичні перекладини/бруси; kneeling-pulldown-band задає еластичну стрічку на верхньому анкері. Їхні вихідні equipment та ID збережено; prompts не додають ваговий стек, блоки, троси або Сміт. Тренажери/блокові станції/Сміт і всі невирішені уточнення лишаються поза пакетами.', '']
    for batch in batches:
        lines.extend([f'## {batch["batch_id"]} — {batch["exercise_count"]}', ''])
        lines.extend(f'- `{row["exercise_id"]}` — {row["name"]}' for row in batch['exercises'])
        lines.append('')
    lines.extend(['## ID → каталог → prompt → PNG', '',
                  'Дані вправ тільки з catalog.json. Повний запис отримано exact-ID словником, не за назвою чи позицією масиву. У кожному batch збережено точні name, весь content.en (description, instructions, form_cues, common_mistakes, safety_note, provenance), equipment, primary_muscle, secondary_muscles; SHA256 каталогу, запису, en-блока й generation_prompt. Prompt payload містить ті самі поля, конкретну одну фазу та цитати instructions цього ID.', '',
                  'Планований шлях `/workspace/exercise-image-results/<batch_id>/<exercise_id>/attempt-1.png`; це не наявний PNG. attempts=0, result_path/result_sha256/user_review/technical_check=null. generation_authorized_now=false. Генерацію та візуальний QA не запускали.', '',
                  'Перед майбутнім виконанням отримати всі актуальні agent-гілки та work, звірити PNG/призначення. Нова невідповідність або суперечність → виключити конкретний ID і повідомити, не підставляти сусідній запис. Виклик/вихідний файл пов’язувати з exact exercise_id, batch_id, source_catalog_sha256, source_catalog_record_sha256, generation_prompt_sha256, фактичним attempt та tool-call identity; записати PNG SHA256 і фактичний шлях. Не асоціювати outputs за порядком повернення або схожістю назв.', '',
                  '## Перевірка', '',
                  f'Звіт [`{REPORT_PATH}`](../{REPORT_PATH}): 451 унікальний catalog ID, {n} нових ID, 60 захищених попередніх ID, відповідність полів/prompt/hash/PNG, відсутність перетинів, {len(report["negative_guard_cases"])} негативних контрольних випадків. Власні черга та packages мають історичні prepared_count/eligible_exercise_ids; вільний залишок визначає тільки remaining_unprepared_ids. latest_launch_ids — раунд 3; first_launch_ids і next_launch_ids залишені як історичні раунди 1 і 2.', '',
                  'Read-only перевірка після fetch:', '', '```bash',
                  "git fetch --no-tags origin '+refs/heads/work:refs/remotes/origin/work' '+refs/heads/agent-02-machines-001:refs/remotes/origin/agent-02-machines-001'",
                  'python scripts/prepare_agent03_other_round3.py --check', '```', '',
                  'Якщо з’явились інші віддалені agent-гілки, спочатку fetch їх у refs/remotes/origin; валідатор сканує всі fetched agent-гілки. Попередні скрипти --check є історичними валідаторами своїх раундів, не поточного формату черги.', '',
                  'Межа: незапушені файли/призначення інших хмарних задач можуть бути недоступні. Поточна перевірка охоплює збережені Git-зрізи. References не шукали/не завантажували/не відкривали для візуального QA. Хеші та provenance не доводять візуальної правильності майбутньої картинки.', '',
                  'Працювати лише в хмарному checkout. Після окремого дозволу на генерацію — тільки вбудований image_gen, без автоматичних повторів/ресайзу, платного API, Supabase або змін shared progress. На цьому етапі зупинитися після підготовки, commit, push і віддаленої звірки.'])
    return '\n'.join(lines) + '\n'

def main():
    parser = argparse.ArgumentParser(); parser.add_argument('--prepare', action='store_true'); parser.add_argument('--check', action='store_true'); args = parser.parse_args()
    if args.prepare == args.check: parser.error('Choose --prepare or --check')
    if base.git('branch', '--show-current').decode().strip() != base.BRANCH: raise ValueError('Wrong branch')
    configure(); s = base.snapshot(); queue = load(base.QUEUE_PATH)
    if args.prepare:
        if any((ROOT / p).exists() for p in NEW_PATHS.values()): raise ValueError('Existing 007–009 files must not be overwritten')
        if queue['prepared_count'] != 60 or queue['preparation_rounds'][-1]['round'] != 2: raise ValueError('Unexpected input queue round')
        if queue['catalog_sha256'] != s['catalog_sha256'] or queue['style_sha256'] != s['style_sha256']: raise ValueError('Catalogue/style changed; stop and review')
        protected = protected_hashes(); original = queue['remaining_unprepared_ids'][:]
        available, excluded = candidates(queue, s); chosen = available[:30]
        if any(eid not in SCENES for eid in chosen): raise ValueError('Missing exact-ID reviewed scene; no guessed replacement: ' + repr(chosen))
        timestamp = datetime.datetime.now(datetime.timezone.utc).isoformat()
        batches = [base.make_batch(bid, chosen[i*10:(i+1)*10], s, timestamp) for i, bid in enumerate(NEW_IDS)]
        for batch in batches:
            for row in batch['exercises']: row['planned_png_path'] = row['output_root'] + '/' + row['planned_output_relative_path']
        queue.update(updated_at=timestamp, latest_launch_ids=chosen, prepared_count=60+len(chosen),
                     remaining_unprepared_ids=available[30:], remaining_unprepared_count=len(available[30:]),
                     last_live_check={'status': 'passed', 'checked_at_utc': timestamp, 'audited_commits': s['commits']})
        queue['preparation_rounds'].append({'round': 3, 'prepared_at': timestamp, 'audited_commits': s['commits'], 'input_remaining_ids': original,
                                            'excluded_since_previous_round': excluded, 'exercise_ids': chosen, 'batch_paths': list(NEW_PATHS.values()), 'status': 'prepared_only', 'shortfall_to_30': 30-len(chosen)})
        blocked = {row['exercise_id'] for row in excluded}
        queue['eligible_exercise_ids'] = [eid for eid in queue['eligible_exercise_ids'] if eid not in blocked]
        queue['exercises'] = [row for row in queue['exercises'] if row['exercise_id'] not in blocked]
        queue['excluded'].extend(excluded)
        queue['exclusion_counts_disjoint'] = dict(collections.Counter(row['reason_code'] for row in queue['excluded']))
        queue['eligible_count'] = len(queue['eligible_exercise_ids']); queue['batch_paths'] += list(NEW_PATHS.values())
        old_ids = [eid for path in OLD_PATHS for eid in load(path)['exercise_ids']]
        queue['previous_batches_live_git_state'] = {'audited_commits': s['commits'], 'reserved_ids': old_ids,
            'IDs_with_saved_PNG': [eid for eid in old_ids if eid in s['png_sources']],
            'png_sources_by_ID': {eid: s['png_sources'].get(eid, []) for eid in old_ids},
            'reservation_sources_by_ID': {eid: s['reserved'].get(eid, []) for eid in old_ids},
            'progress_sources_by_ID': {eid: s['touched'].get(eid, []) for eid in old_ids},
            'note': 'Live Git observations only; own prior batch files unchanged. PNG presence is not user approval.'}
        for row in queue['exercises']:
            eid = row['exercise_id']
            if eid in chosen: row.update(batch_id=next(batch['batch_id'] for batch in batches if eid in batch['exercise_ids']), prompt_prepared=True, status='prompt_prepared_not_generated')
        report = validate(s, queue, batches, protected); report['negative_guard_cases'] = negative_checks(s, queue, batches, protected)
        if report['errors']: raise ValueError(json.dumps(report['errors']))
        # No writes occur until every source/eligibility/identity check passes.
        for batch in batches: save(NEW_PATHS[batch['batch_id']], batch)
        save(base.QUEUE_PATH, queue); save(REPORT_PATH, report)
        (ROOT / HANDOFF_PATH).write_text(handoff(s, queue, batches, report))
        assert protected == protected_hashes()
    else:
        batches = [load(p) for p in NEW_PATHS.values()]; saved = load(REPORT_PATH)
        report = validate(s, queue, batches, saved['protected_sha256'])
        report['negative_guard_cases'] = negative_checks(s, queue, batches, saved['protected_sha256'])
    print(json.dumps({key: report[key] for key in ['status', 'audited_commits', 'new_batch_ID_count', 'remaining_without_prompts', 'excluded_since_previous_round', 'negative_guard_cases', 'errors']}, ensure_ascii=False, indent=2))
    if report['errors']: sys.exit(1)

if __name__ == '__main__': main()
