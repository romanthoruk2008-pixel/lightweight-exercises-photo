#!/usr/bin/env python3
"""Prepare/check round two only. Fetch remote branches before running.

Never rewrites batches 001–003, catalogue, shared progress, or images.
Uses the original preparer's exact-ID source/eligibility/prompt functions.
"""
import argparse
import collections
import copy
import datetime
import json
import pathlib
import sys

import prepare_agent03_other_queue as base

ROOT = base.ROOT
OLD_PATHS = [f'data/batches/agent-03-others-{n:03}.json' for n in range(1, 4)]
NEW_IDS = [f'agent-03-others-{n:03}' for n in range(4, 7)]
NEW_PATHS = {bid: f'data/batches/{bid}.json' for bid in NEW_IDS}
REPORT_PATH = 'data/queues/agent-03-other-next-validation.json'
HANDOFF_PATH = 'docs/agent-03-other-next-handoff.md'

# Scenes are keyed by exact catalogue ID. No association by names or array position.
SCENES = {
    '21s-biceps-curl-barbell': ('Lower-half curl endpoint within the 21s sequence', "Stand tall with one barbell held by both hands, elbows fixed close to the sides, wrists neutral and torso still. Show the endpoint of the lower-half curl segment, before the upper-half and full-range segments. A single pose only; the complete seven/seven/seven sequence remains in the source block. Do not depict a shoulder-height ordinary full curl for this chosen phase.", [0, 1, 2, 3]),
    'arnold-press-dumbbell': ('Standing palms-in starting position', "Use the explicitly permitted standing variant. Hold one dumbbell in each hand at shoulder height with palms facing the man, both elbows bent. Ribs stacked over pelvis, shoulders down. This is the starting phase before both palms rotate forward during the upward press; not an ordinary palms-forward starting press. Show both weights and feet.", [0, 1, 2]),
    'bent-over-row-barbell': ('Lower-rib row endpoint from a fixed hinge', "Both feet hip-width on the floor. Hinge at the hips with the torso inclined, neck aligned and back fixed. Both hands hold one free barbell drawn toward lower ribs, elbows behind the torso, shoulders away from ears. Preserve the hinge throughout; no bench support, torso jerk, shrug or cable machine. Do not invent a numerical torso angle or grip width.", [0, 1, 2]),
    'bent-over-row-dumbbell': ('Two-dumbbell lower-rib row endpoint', "Stand hip-width and hold one dumbbell in each hand as specified by the plural dumbbells in this exact description. Hinge with an inclined fixed spine; both elbows draw behind the torso as weights reach lower ribs. Neck aligned, shoulders down, both feet on floor. No unilateral bench-supported row, barbell or cable station; no invented grip angle or torso angle.", [0, 1, 2]),
    'bulgarian-split-squat-barbell': ('Left front-leg controlled lower position', "The top of the RIGHT foot rests on a LOW bench behind the man. LEFT foot is forward with its heel grounded; left thigh approaches parallel as both knees bend and torso stays upright. One free barbell lies across upper back, held stable by both hands. Hips face forward and front knee tracks toes. Include a stationary rack as the source safety option, without another person or guided Smith rails. Show every contact and the rear bench.", [0, 1, 2]),
    'decline-bench-press-barbell': ('Controlled lower press position on decline bench', "Lie on a declined bench, back and shoulder blades supported and both feet secured by the bench's compatible foot supports. Both hands hold one free barbell lowered toward chest, wrists stacked, elbows controlled without flaring or bouncing. Show decline orientation, secured feet and complete bar. Include stationary rack safeties per the source; no spotter figure, guided rails or unspecified decline angle.", [0, 1, 2, 3]),
    'decline-bench-press-dumbbell': ('Two-dumbbell decline press lower position', "Lie with back and shoulder blades supported on a declined bench and feet secured in compatible foot supports. One dumbbell per hand is lowered toward the chest with controlled elbows and stacked wrists. Use a stable setup with compatible safety supports per the source safety alternative; show whole bench and feet without another person. No barbell, fly-wide straight arms, guided rails or invented decline angle.", [0, 1, 2, 3]),
    'floor-press-barbell': ('Floor-supported press at straight arms', "Lie directly on the floor with knees bent, feet grounded and shoulder blades supported by the floor. Both hands hold one free barbell above chest with straight controlled arms and stacked wrists. Use stationary safeties as the source permits, no second person. Show floor contact clearly; no bench, exaggerated arch or guided press machine.", [0, 1, 3]),
    'front-raise-barbell': ('Controlled shoulder-height front raise', "Stand tall holding one barbell in both hands forward at approximately shoulder height. Elbows retain a soft bend, wrists neutral, shoulders down. Torso stays upright without leaning back, swinging or shrugging. Show full free bar and both floor contacts; no press overhead, curl, machine or extra weights.", [0, 1, 2]),
    'handstand-pushup': ('Wall-supported controlled bent-elbow handstand', "Choose the wall option explicitly allowed in the source. The man is inverted against a plain supporting wall, hands shoulder-width contacting the floor, shoulders aligned over wrists. Trunk stays stacked as elbows bend and head lowers under control before uncontrolled floor contact. Both legs remain controlled against wall support; no kicking, extra person or free-floating hands. Include the complete figure and required wall contact within the transparent-background composition.", [0, 1, 2]),
    'incline-bench-press-barbell': ('Lower press pause on a 45-degree incline', "Lie on a bench inclined at the source's 45 degrees, feet flat on ground. Both hands grip a free barbell overhand slightly wider than shoulder width. Bar approaches upper chest with elbows at the source's 45-degree alignment; wrists over elbows, shoulder blades controlled. Show a stationary unracking support, the whole bench and bar, no Smith rails, bounced chest contact or exaggerated arch.", [0, 1, 2, 3, 4]),
    'incline-bench-press-dumbbell': ('Dumbbells lowered beside upper chest on 45-degree bench', "Back is firmly supported by the source's 45-degree incline bench, feet flat on floor. Hold one dumbbell in each hand with palms facing forward, lowered to the sides of chest; elbows bent to the stated 90-degree angle, wrists stacked over elbows. Keep trunk braced and shoulders controlled. Show both weights and full bench; no fly-wide nearly straight arms, barbell or unsupported seated torso.", [0, 1, 2, 3, 4]),
    'incline-chest-fly-dumbbell': ('Controlled wide-arc stretch on 45-degree incline', "Lie back on a bench inclined at the exact source 45 degrees. One dumbbell in each hand with palms facing each other opens to either side in a wide arc until a comfortable chest stretch. Elbow bend stays soft and constant, shoulders down, ribs controlled. Show supported torso, full bench and both arms; no bent-elbow press, forced end range or extra weight.", [0, 1, 2, 3, 4]),
    'jm-press-barbell': ('Tucked-elbow JM lower position near upper chest', "Lie on a FLAT bench with feet planted. Both hands hold a free barbell slightly wider than shoulder width. Lowered bar approaches upper chest, elbows tucked and forearms angled back, upper arms controlled. Preserve this exact JM position rather than lowering to the forehead or flaring for an ordinary chest press. Shoulder blades supported, wrists aligned; whole bar and bench visible.", [0, 1, 2]),
    'lunge-barbell': ('Right forward lunge lower position', "One barbell rests across upper back, held stable with both hands. RIGHT foot has stepped forward and right thigh reaches parallel to ground as both knees bend, torso upright. Right heel remains grounded and right knee tracks toes in this loaded phase. Show the rear foot and full bar; no feet permanently glued together, reverse step, Smith machine or unsupported trunk lean.", [0, 1, 2, 3]),
    'overhead-dumbbell-lunge': ('Front-foot lunge with both dumbbells stacked overhead', "One dumbbell in EACH hand is held overhead with both elbows extended and weights stacked over shoulders. One foot has stepped forward, both knees bend comfortably, front knee tracks toes; ribs down and trunk braced without lower-back arch. Show both weights, full arms and all foot contacts. Keep light controllable weights; no forward drift, barbell or shoulder-height weights.", [0, 1, 2, 3]),
    'overhead-press-barbell': ('Standing strict overhead position', "Stand with both feet planted and hold one free barbell overhead above the shoulders, both hands just outside shoulder width. Head is now under the bar following the source head-clearance path, abdomen and glutes braced, ribs down, no backward lean or leg drive. Show a stationary rack for the stated safe return, no guided rails. Whole body and bar visible.", [0, 1, 2, 3]),
    'partial-glute-bridge-barbell': ('Deliberately partial hip-extension endpoint', "Lie on the back with knees bent and both feet flat. One padded barbell is centered across the hips and held steady so it cannot roll. Hips rise ONLY PARTWAY, trunk braced and lumbar spine not arched; retain a clearly shortened extension rather than the full shoulders-to-knees bridge line. No numerical percentage invented. Shoulder support remains on the floor, no bench or hip-thrust substitution.", [0, 1, 2]),
    'pause-squat-barbell': ('Motionless stable bottom pause', "One free barbell sits securely across upper back, both hands steadying it. Feet approximately shoulder-width planted, hips and knees bent at the lowest STABLE depth described by the source, chest lifted and trunk tense. Show a motionless pause without bouncing or relaxed core; knees follow toes. Include a stationary rack with safety pins per source, no Smith guides, extra person or invented numeric depth.", [0, 1, 2, 3]),
    'pendlay-row-barbell': ('Upper-abdomen row endpoint from near-horizontal hinge', "Stand shoulder-width with knees slightly bent; hip hinge leaves the straight back and torso near horizontal. Both hands grip one free barbell overhand slightly wider than shoulder width. Bar is drawn from the floor to UPPER ABDOMEN, elbows back, shoulder blades together, torso steady. Show this one top row phase, not a standing deadlift; the full source records the floor reset each repetition. Full bar and feet in frame.", [0, 1, 2, 3, 4]),
    'pullover-dumbbell': ('Single dumbbell lowered behind head', "Lie lengthwise flat on a bench with head at one end and feet on floor. BOTH hands hold the same SINGLE dumbbell. Arms travel behind the head with softly bent elbows until a comfortable chest/shoulder stretch, trunk braced. Show a three-quarter side view exposing the supported back, head clearance, both hands and whole weight. No cross-bench pose, two dumbbells, press or exaggerated lumbar arch.", [0, 1, 2, 3]),
    'push-press-barbell': ('Shallow knee dip before upward drive', "Stand approximately shoulder-width, barbell held at upper chest by both hands. Knees bend in a shallow vertical dip with trunk braced and torso upright, ready to drive through feet and press overhead as legs extend. Show only this characteristic leg-drive setup; do not use a deep front squat, split jerk, unsupported back lean or ordinary strict press. Include stationary rack for safe return per source.", [0, 1, 2, 3]),
    'renegade-row-dumbbell': ('One row from a stable wide-foot plank', "High plank with feet wide on floor. LEFT hand grips the handle of a stable dumbbell resting on floor; RIGHT hand rows the second dumbbell toward the ribs. Trunk braced, shoulder and hip lines square, right elbow toward ribs, no twist or pike. Show both dumbbells, hand contact and both feet within frame; no bench-supported row or extra limbs. Chosen side is one permitted alternating repetition.", [0, 1, 2]),
    'reverse-grip-concentration-curl-dumbbell': ('Palms-down curl with elbow on inner thigh', "Sit on a bench holding ONE dumbbell with palm facing DOWN. That elbow remains in contact with the inner thigh and upper arm stays still while the weight curls toward the shoulder. Show the elbow-thigh contact and reverse grip clearly; no palms-up ordinary concentration curl, upper-arm swing or second dumbbell. Use an aligned wrist and controlled top phase.", [0, 1, 2]),
    'reverse-lunge-barbell': ('Left front-leg lower position after right backward step', "One free barbell lies across upper back, held securely by both hands. RIGHT foot has stepped BACK and contacts on its ball; LEFT leg is forward, left thigh parallel to ground with left heel grounded as both knees bend. Torso remains upright and knees track toes. Show exact source sides, bar and foot contacts; no forward right lunge or rear heel flattened by generic planted-foot cues.", [0, 1, 2, 3]),
    'seal-row-barbell': ('Prone bar row toward underside of elevated bench', "Lie face down on a FLAT ELEVATED bench, both chest and hips continuously on pad. Both hands grip one free barbell slightly wider than shoulder width with palms down; bar travels from beneath chest toward underside of bench/ribs, elbows back. Show the standard bench elevation needed for bar clearance, whole bar and supported body, without invented numeric height. No upright torso, cables or chest lift; the explicit prone instructions select the supported option in generic cues.", [0, 1, 2, 3]),
    'seal-row-dumbbell': ('Prone neutral-grip two-dumbbell row', "Lie face down on a FLAT ELEVATED bench, chest and hips stay on pad. Hold one dumbbell in EACH hand using the source NEUTRAL grip, rowing both toward ribs with elbows back and chest down. Show bench elevation sufficient for freely hanging arms/weights, whole supported figure and both dumbbells. No upright torso, barbell, cable or invented height; follow explicit prone instructions within the generic supported-or-upright cue.", [0, 1, 2, 3]),
    'seated-overhead-press-barbell': ('Back-supported seated bar at shoulder level', "Sit on a bench with a secure back pad as required by this exact description and cue. Back stays in contact, feet flat on ground. Both hands hold one free barbell at shoulder level using overhand grip slightly wider than shoulder width, elbows bent and palms forward. Show a stationary rack for the source unrack/return, no guided rails or press machine. No invented backrest angle or forced lockout; use the controlled starting press phase.", [0, 1, 2, 3]),
    'seated-overhead-press-dumbbell': ('Back-supported seated palms-forward starting press', "Sit with trunk against a secure back pad on the bench as required by this exact description and cue. Hold one dumbbell in each hand at shoulder height with palms forward after lifting them from thighs. Both elbows bent and wrists aligned, shoulders controlled. Show complete bench, body and both weights; no standing Arnold palms-in variant, machine, invented backrest angle or forced lockout.", [0, 1, 2]),
    'seated-wrist-extension-barbell': ('Palms-down wrist-extension endpoint with thighs supporting forearms', "Sit on a bench, feet flat. Both forearms REST on thighs and wrists extend beyond the thigh edges. Both hands hold a single barbell overhand, palms DOWN; lift backs of hands in wrist extension while forearms/elbows remain supported and still. Honor the source trunk-against-support cue with bench back support, without inventing an angle. Show hand orientation, thigh support and whole bar; no palms-up wrist curl, elbow-driven biceps curl or forced elbow lockout.", [0, 1, 2, 3]),
}

def configure():
    base.BATCH_PATHS = NEW_PATHS  # Old 001–003 remain reservations, always scanned.
    base.SCENES = SCENES

def read_json(path):
    return json.loads((ROOT / path).read_text())

def write_json(path, value):
    (ROOT / path).write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n')

def freeze():
    paths = OLD_PATHS + [base.CATALOG_PATH, base.PROGRESS_PATH, base.INVENTORY_PATH,
                        base.CLARIFICATIONS_PATH, base.VALIDATION_PATH, base.HANDOFF_PATH]
    return {p: base.sha((ROOT / p).read_bytes()) for p in paths}

def validate(s, queue, batches, protected):
    errors, seen, checked = [], set(), []
    old_ids = [r['exercise_id'] for p in OLD_PATHS for r in read_json(p)['exercises']]
    if len(old_ids) != 30 or len(set(old_ids)) != 30:
        errors.append('old_batch_IDs_invalid')
    for batch in batches:
        bid = batch['batch_id']
        if bid not in NEW_IDS or batch['catalog_sha256'] != s['catalog_sha256'] or batch['style_sha256'] != s['style_sha256']:
            errors.append('batch_source_mismatch:' + bid)
        rows = batch['exercises']
        if len(rows) != 10 or batch['exercise_ids'] != [r['exercise_id'] for r in rows]:
            errors.append('batch_size_or_ID_list_mismatch:' + bid)
        for row in rows:
            eid = row['exercise_id']; checked.append(eid)
            if eid in seen: errors.append('duplicate_new_ID:' + eid)
            seen.add(eid)
            if eid in old_ids: errors.append('old_assigned_ID_reused:' + eid)
            if eid not in s['by_id']:
                errors.append('ID_missing:' + eid); continue
            for key, value in base.fields_for_id(eid, s).items():
                if row.get(key) != value: errors.append('source_field_mismatch:' + eid + ':' + key)
            reason, _ = base.readiness(s['by_id'][eid], s)
            if reason != 'eligible': errors.append('unavailable:' + eid + ':' + reason)
            if eid not in SCENES:
                errors.append('scene_missing:' + eid); continue
            expected_payload = base.payload_for_id(eid, s)
            if row.get('prompt_payload') != expected_payload: errors.append('prompt_source_or_scene_mismatch:' + eid)
            expected_row = base.make_batch(bid, [eid], s, batch['prepared_at'])['exercises'][0]
            for key in ['generation_prompt', 'generation_prompt_sha256', 'planned_output_relative_path', 'output_root']:
                if row.get(key) != expected_row[key]: errors.append('prompt_or_PNG_binding_mismatch:' + eid + ':' + key)
            if row.get('planned_png_path') != f'/workspace/exercise-image-results/{bid}/{eid}/attempt-1.png':
                errors.append('absolute_PNG_path_mismatch:' + eid)
            if any(row.get(k) is not None for k in ['result_path', 'result_sha256', 'user_review', 'technical_check']) or row.get('attempts') != 0:
                errors.append('preparation_reported_as_generation:' + eid)
    if len(seen) != 30 or seen != set(SCENES): errors.append('new30_scene_set_mismatch')
    if queue.get('next_launch_ids') != checked: errors.append('queue_next30_mismatch')
    if queue.get('first_launch_ids') != old_ids: errors.append('old_launch_IDs_changed')
    rest = queue['remaining_unprepared_ids']
    all_ids = queue['eligible_exercise_ids']
    if len(all_ids) != len(set(all_ids)) or set(all_ids) != set(old_ids + checked + rest):
        errors.append('queue_partition_mismatch')
    if set(rest) & set(old_ids + checked): errors.append('remaining_queue_reserved_overlap')
    round_two = queue['preparation_rounds'][-1]
    input_pool = round_two['input_remaining_ids']
    blocked = {x['exercise_id'] for x in round_two['excluded_since_previous_round']}
    expected = [eid for eid in input_pool if eid not in blocked]
    if expected != checked + rest: errors.append('original_remaining_order_or_partition_changed')
    for row in queue['exercises']:
        eid = row['exercise_id']
        if eid not in s['by_id']: errors.append('queue_unknown_ID:' + eid); continue
        for key in ['name', 'equipment', 'primary_muscle', 'secondary_muscles', 'source_catalog_sha256', 'source_catalog_record_sha256', 'source_english_sha256']:
            if row.get(key) != base.fields_for_id(eid, s)[key]: errors.append('queue_source_mismatch:' + eid + ':' + key)
        if eid in rest:
            if base.readiness(s['by_id'][eid], s)[0] != 'eligible': errors.append('remaining_ID_now_unavailable:' + eid)
            if row.get('prompt_prepared') or row.get('batch_id') or any(k in row for k in ['prompt', 'generation_prompt', 'prompt_payload']):
                errors.append('remaining_prompt_or_assignment:' + eid)
        elif eid in seen:
            bid = next((b['batch_id'] for b in batches if eid in b['exercise_ids']), None)
            if row.get('batch_id') != bid or row.get('prompt_prepared') is not True:
                errors.append('queue_batch_binding_mismatch:' + eid)
    if queue['prepared_count'] != 60 or queue['remaining_unprepared_count'] != len(rest) or queue['eligible_count'] != len(all_ids):
        errors.append('queue_counts_mismatch')
    for path, expected_hash in protected.items():
        if base.sha((ROOT / path).read_bytes()) != expected_hash: errors.append('protected_file_changed:' + path)
    return {'schema_version': 1, 'status': 'failed' if errors else 'passed',
            'checked_at_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
            'catalog_sha256': s['catalog_sha256'], 'audited_commits': s['commits'],
            'unique_catalog_IDs': len(s['by_id']), 'new_batch_count': 3,
            'new_batch_ID_count': len(seen), 'old_assigned_ID_count': len(set(old_ids)),
            'remaining_without_prompts': len(rest), 'errors': errors,
            'checks': ['IDs_exist_once', 'exact_ID_catalogue_fields', 'exact_ID_prompt_source_and_hash',
                       'new_IDs_disjoint', 'no_old_assigned_IDs', 'no_other_assignment_or_result',
                       'PNG_paths_bound_to_exact_ID', 'remaining_order_and_no_prompts', 'protected_files_unchanged'],
            'protected_sha256': protected, 'checked_exercise_ids': checked,
            'source_files': s['source_files'], 'scope_limit': queue['scope_limit']}

def negative_checks(s, queue, batches, protected):
    cases = {}
    mutations = {
        'swapped_name': lambda b: b[0]['exercises'][0].update(name=b[0]['exercises'][1]['name']),
        'swapped_english': lambda b: b[0]['exercises'][0].update(source_english=b[0]['exercises'][1]['source_english']),
        'wrong_equipment': lambda b: b[0]['exercises'][0].update(equipment='machine'),
        'wrong_muscles': lambda b: b[0]['exercises'][0].update(primary_muscle='cardio'),
        'duplicate_between_batches': lambda b: b[1]['exercises'].__setitem__(0, copy.deepcopy(b[0]['exercises'][0])),
        'swapped_prompt': lambda b: b[0]['exercises'][0].update(generation_prompt=b[0]['exercises'][1]['generation_prompt']),
        'PNG_wrong_ID': lambda b: b[0]['exercises'][0].update(planned_png_path=b[0]['exercises'][1]['planned_png_path']),
        'reused_old_assigned_ID': lambda b: b[0]['exercises'][0].update(exercise_id=read_json(OLD_PATHS[0])['exercise_ids'][0]),
    }
    for name, mutate in mutations.items():
        bad = copy.deepcopy(batches); mutate(bad)
        cases[name] = validate(s, queue, bad, protected)['status'] == 'failed'
    for name, field in [('new_foreign_assignment', 'reserved'), ('new_PNG', 'png_sources')]:
        bad_s = copy.deepcopy(s)
        bad_s[field][batches[0]['exercise_ids'][0]].append({'branch': 'synthetic_test_only'})
        cases[name] = validate(bad_s, queue, batches, protected)['status'] == 'failed'
    if not all(cases.values()): raise ValueError('A negative identity/overlap guard did not fail: ' + repr(cases))
    return cases

def handoff(s, queue, batches, report):
    lines = ['# Agent-03: наступні 30 «Інші» — пакети 004–006', '',
             f'Гілка `{base.BRANCH}`. Актуальний work: `{s["commits"]["origin/work"]}`; agent-02: `{s["commits"]["origin/agent-02-machines-001"]}`.', '',
             f'Каталог SHA256: `{s["catalog_sha256"]}`. Стиль v1 SHA256: `{s["style_sha256"]}`.', '',
             '001–003 (30 ID) передані першому агенту за повідомленням користувача. Їхні файли й prompts залишено байт-у-байт незмінними; усі їхні ID зарезервовані та виключені з нового добору.', '',
             f'Перевірено решту {len(queue["preparation_rounds"][-1]["input_remaining_ids"])} ID через актуальні Git PNG, progress та всі batch/manifest/index/clarification файли work, agent-02 і власної гілки. Нових виключень: {len(queue["preparation_rounds"][-1]["excluded_since_previous_round"])}. Підготовлено наступні 30; без prompts залишається **{queue["remaining_unprepared_count"]}**.', '',
             'У queue збережено історичні eligible_exercise_ids усіх відібраних вправ, first_launch_ids першої тридцятки, next_launch_ids нової тридцятки й окремий remaining_unprepared_ids. prepared_count=60 включає обидва раунди; це не кількість виконаних зображень.', '',
             'Нові prompts обирають одну конкретну фазу й стандартні сумісні опори з англійського запису саме цього ID. У кожному batch — точні name, повний content.en, equipment, primary_muscle, secondary_muscles; SHA256 всього каталогу, запису, англійського блока й prompt. Текст каталогу не виправляли.', '',
             'Планований PNG: `/workspace/exercise-image-results/<batch_id>/<exercise_id>/attempt-1.png`. Це майбутній шлях, не наявний результат. attempts=0, result_path/result_sha256/user_review=null. Генерацію не запускали, візуального QA не було.', '']
    for batch in batches:
        lines.extend([f'## {batch["batch_id"]}', ''])
        lines.extend(f'- `{r["exercise_id"]}` — {r["name"]}' for r in batch['exercises'])
        lines.append('')
    lines.extend(['## Повторна перевірка й передача', '',
                  'Read-only перевірка нового раунду (старий скрипт --check перевіряв лише початковий формат черги й після її оновлення не є валідатором цього раунду):', '',
                  '```bash', "git fetch --no-tags origin '+refs/heads/work:refs/remotes/origin/work' '+refs/heads/agent-02-machines-001:refs/remotes/origin/agent-02-machines-001'", 'python scripts/prepare_agent03_other_followup.py --check', '```', '',
                  f'Звіт: [`{REPORT_PATH}`](../{REPORT_PATH}). Перевірено 451 унікальний catalog ID, 30 нових ID, точну відповідність полів, prompts/hash/PNG paths і відсутність перетинів. Негативні тести: {len(report["negative_guard_cases"])}; усі навмисні підміни/перетини відхилені.', '',
                  'Перед майбутнім дозволеним викликом fetch усі актуальні agent-гілки, звірити результати й призначення; новий конфлікт означає зупинити конкретний ID та повідомити. Незапушені файли й призначення інших хмарних задач можуть бути недоступні. Перевірка охоплює збережені Git-зрізи, не приховані локальні завдання.', '',
                  'Виконавцю брати запис та generation_prompt лише за exercise_id. Журнал зв’язує batch_id, exercise_id, source_catalog_sha256, source_catalog_record_sha256, generation_prompt_sha256, фактичний tool call, attempt і PNG SHA256/path. Зберегти саме output цього виклику під відповідним ID; не використовувати позицію масиву чи схожість назв. Хеші підтверджують походження файлів, не правильність зображеної техніки.', '',
                  'Reference тільки для зовнішності; зараз не відкривали, не шукали й не завантажували зовнішніх референсів. Подальша генерація лише за окремим дорученням, без автоматичних повторів/ресайзу, платного API чи Supabase.', '',
                  '## 105 уточнень', '',
                  '50 записів мають суперечність або недостатню конкретність техніки/обладнання. 55 мають primary_muscle=full_body/cardio/other без правила локальної підсвітки v1; це окреме питання стилю, не автоматичний дефект техніки. Усі лишаються виключеними; дані не змінено.', '',
                  'Точні проблемні поля, цитати, питання та приклади за категоріями й підтипами: [пояснення уточнень](agent-03-other-clarifications-explained.md). Початковий повний JSON 105 уточнень збережено без змін.', '',
                  'Каталог, спільний progress, інвентаризація, старі handoff/пакети/результати залишено незмінними. Роботу зупинено після підготовки й передачі.'])
    return '\n'.join(lines) + '\n'

def main():
    parser = argparse.ArgumentParser(); parser.add_argument('--prepare', action='store_true'); parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    if args.prepare == args.check: parser.error('Choose exactly one of --prepare or --check')
    if base.git('branch', '--show-current').decode().strip() != base.BRANCH: raise ValueError('Wrong branch')
    configure(); protected = freeze(); s = base.snapshot(); queue = read_json(base.QUEUE_PATH)
    if args.prepare:
        if any((ROOT / p).exists() for p in NEW_PATHS.values()): raise ValueError('Next batches already exist; use --check, never overwrite assignments')
        if queue['prepared_count'] != 30 or len(queue['remaining_unprepared_ids']) != 97: raise ValueError('Unexpected input queue round')
        if queue['catalog_sha256'] != s['catalog_sha256'] or queue['style_sha256'] != s['style_sha256']: raise ValueError('Changed catalogue/style; no guesses')
        original = queue['remaining_unprepared_ids'][:]; available, blocked = [], []
        for eid in original:
            reason, detail = base.readiness(s['by_id'][eid], s)
            if reason == 'eligible': available.append(eid)
            else: blocked.append({'exercise_id': eid, 'reason_code': reason, 'details': detail,
                                  'png_sources': s['png_sources'].get(eid, []), 'reservation_sources': s['reserved'].get(eid, []),
                                  'progress_sources': s['touched'].get(eid, [])})
        chosen = available[:30]
        if set(chosen) != set(SCENES): raise ValueError('Next IDs changed: exclude unavailable records and author exact-ID scenes; no guessed replacement: ' + repr(blocked))
        timestamp = datetime.datetime.now(datetime.timezone.utc).isoformat()
        batches = [base.make_batch(bid, chosen[i*10:(i+1)*10], s, timestamp) for i, bid in enumerate(NEW_IDS)]
        for b in batches:
            for row in b['exercises']: row['planned_png_path'] = row['output_root'] + '/' + row['planned_output_relative_path']
        queue.update(updated_at=timestamp, next_launch_ids=chosen, prepared_count=60,
                     remaining_unprepared_ids=available[30:], remaining_unprepared_count=len(available)-30,
                     last_live_check={'status': 'passed', 'audited_commits': s['commits'], 'checked_at_utc': timestamp},
                     count_semantics='eligible_exercise_ids includes historical prepared rounds; remaining_unprepared_ids alone is the available unprepared pool')
        if blocked:
            blocked_ids = {x['exercise_id'] for x in blocked}
            queue['eligible_exercise_ids'] = [eid for eid in queue['eligible_exercise_ids'] if eid not in blocked_ids]
            queue['exercises'] = [r for r in queue['exercises'] if r['exercise_id'] not in blocked_ids]
            queue['excluded'].extend(blocked)
            queue['exclusion_counts_disjoint'] = dict(collections.Counter(r['reason_code'] for r in queue['excluded']))
        queue['eligible_count'] = len(queue['eligible_exercise_ids'])
        queue['batch_paths'] += list(NEW_PATHS.values())
        queue['preparation_rounds'] = [
            {'round': 1, 'batch_paths': OLD_PATHS, 'exercise_ids': queue['first_launch_ids'], 'status': 'handed_to_first_agent_per_user', 'files_unchanged_sha256': {p: protected[p] for p in OLD_PATHS}},
            {'round': 2, 'prepared_at': timestamp, 'audited_commits': s['commits'], 'input_remaining_ids': original,
             'excluded_since_previous_round': blocked, 'batch_paths': list(NEW_PATHS.values()), 'exercise_ids': chosen, 'status': 'prepared_only'}]
        for row in queue['exercises']:
            eid = row['exercise_id']
            if eid in queue['first_launch_ids']: row['handoff_status'] = 'handed_to_first_agent_per_user'
            if eid in chosen:
                row.update(batch_id=next(b['batch_id'] for b in batches if eid in b['exercise_ids']), prompt_prepared=True, status='prompt_prepared_not_generated')
        report = validate(s, queue, batches, protected)
        report['negative_guard_cases'] = negative_checks(s, queue, batches, protected)
        if report['errors']: raise ValueError(json.dumps(report['errors']))
        # All validation occurs before saving any queue or batch.
        for b in batches: write_json(NEW_PATHS[b['batch_id']], b)
        write_json(base.QUEUE_PATH, queue); write_json(REPORT_PATH, report)
        (ROOT / HANDOFF_PATH).write_text(handoff(s, queue, batches, report))
        assert protected == freeze()
    else:
        batches = [read_json(p) for p in NEW_PATHS.values()]
        saved_report = read_json(REPORT_PATH)
        report = validate(s, queue, batches, saved_report['protected_sha256'])
        report['negative_guard_cases'] = negative_checks(s, queue, batches, saved_report['protected_sha256'])
    print(json.dumps({k: report[k] for k in ['status', 'audited_commits', 'new_batch_ID_count', 'remaining_without_prompts', 'negative_guard_cases', 'errors']}, ensure_ascii=False, indent=2))
    if report['errors']: sys.exit(1)

if __name__ == '__main__': main()
