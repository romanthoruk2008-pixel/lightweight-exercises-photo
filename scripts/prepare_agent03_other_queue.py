#!/usr/bin/env python3
"""Prepare or validate agent-03 queues from immutable Git snapshots, using exact IDs.

No dependency, catalogue, shared progress, existing batch, or image writes.
Run from the repository root: python scripts/prepare_agent03_other_queue.py --check
Fetch work and other agents' refs first; --prepare regenerates ONLY this agent's artifacts.
"""
import argparse
import collections
import copy
import datetime
import hashlib
import json
import pathlib
import re
import subprocess
import sys
from zoneinfo import ZoneInfo

ROOT = pathlib.Path(__file__).resolve().parents[1]
CATALOG_PATH = 'data/exercises/catalog.json'
PROGRESS_PATH = 'data/exercise-image-progress.json'
INVENTORY_PATH = 'data/audits/agent-03-inventory.json'
QUEUE_PATH = 'data/queues/agent-03-other-queue.json'
CLARIFICATIONS_PATH = 'data/queues/agent-03-other-clarifications.json'
VALIDATION_PATH = 'data/queues/agent-03-other-validation.json'
HANDOFF_PATH = 'docs/agent-03-other-handoff.md'
BATCH_IDS = ['agent-03-others-001', 'agent-03-others-002', 'agent-03-others-003']
BATCH_PATHS = {bid: f'data/batches/{bid}.json' for bid in BATCH_IDS}
BRANCH = 'agent-03-inventory-2026-10-01'
REFS = ['origin/work', 'origin/agent-02-machines-001', 'HEAD']

def git(*args):
    return subprocess.check_output(['git', *args], cwd=ROOT)

def sha(data):
    return hashlib.sha256(data).hexdigest()

def canonical(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':'))

def value_sha(value):
    return sha(canonical(value).encode())

def pointer(s):
    return str(s).replace('~', '~0').replace('/', '~1')

# New clarifications found by reading only candidate English records.
# These reasons never replace or repair the source English text.
TECHNICAL_CLARIFICATIONS = {
    'assisted-pistol-squats': ('support_unspecified', 'Assisted в назві, але stable support лише if needed; вид опори й контакт руки не визначені. Уточніть потрібну опору та спосіб тримання.'),
    'around-the-world-dumbbell': ('movement_unspecified', 'arms extended as appropriate та weight(s) не визначають площину кола й однозначну кількість/контакти гантелей. Уточніть конкретний варіант.'),
    'bench-dip': ('conflicting_supports', 'Description задає parallel supports, instructions — лавку позаду та стопи на підлозі. Уточніть опори; не підміняти опис здогадкою.'),
    'bench-press-close-grip-barbell': ('variant_missing', 'Назва Close Grip, але весь англійський блок не задає вузьку ширину хвата. Вкажіть хват цього варіанта.'),
    'bench-press-wide-grip-barbell': ('variant_missing', 'Назва Wide Grip, але весь англійський блок не задає широкий хват. Вкажіть хват цього варіанта.'),
    'bent-over-row-band-resistance-band': ('anchor_unspecified', 'Вказано band handles, але не визначено точку/спосіб закріплення стрічки. Вкажіть анкер або контакт зі стопами.'),
    'biceps-curl-suspension': ('support_unspecified', 'Не визначено анкер, нахил тіла та контакти зі стопами; текст схожий на звичайний curl. Уточніть suspension-композицію.'),
    'box-jump': ('movement_unspecified', 'upward or forward as the exercise requires не задає однозначного напрямку й місця приземлення відносно box. Уточніть одну фазу та траєкторію.'),
    'chest-dip-weighted-machine': ('load_unspecified', 'Weighted у назві, але немає зовнішньої ваги, способу закріплення чи місця навантаження. Вкажіть конкретне обтяження.'),
    'chest-fly-band-resistance-band': ('anchor_unspecified', 'Set up on the resistance band та chest supported as required не визначають анкер, положення тулуба й опору. Уточніть конструкцію.'),
    'chest-fly-suspension': ('support_unspecified', 'Instructions кажуть set up on your bodyweight та chest supported as required, не задаючи ролі straps або нахилу. Уточніть опори/анкер.'),
    'chest-press-band-resistance-band': ('anchor_unspecified', 'Жим лежачи з band handles задано, але точка закріплення стрічки відсутня. Уточніть конфігурацію стрічки відносно лави.'),
    'clap-push-ups': ('variant_missing', 'Назва Clap, але instructions задають лише leave the floor briefly, без однозначного плескання й пози рук. Уточніть характерну фазу.'),
    'crunch-weighted': ('load_unspecified', 'Weighted у назві при equipment=none; весь англійський блок описує crunch без ваги. Вкажіть тип, місце й тримання обтяження.'),
    'deadlift-band-resistance-band': ('anchor_unspecified', 'band over the mid-foot не визначає, як стрічка зафіксована й натягнута. Уточніть контакт стрічки зі стопами/анкером.'),
    'deadlift-trap-bar-barbell': ('equipment_unspecified', 'Trap bar у назві, але опис та setup — barbell over the mid-foot, без положення всередині рами чи бічних руків’їв. Уточніть конструкцію й хват.'),
    'decline-crunch-weighted': ('load_unspecified', 'Weighted у назві при equipment=none; declined crunch не має визначеної ваги або місця навантаження. Уточніть обтяження.'),
    'decline-chest-fly-dumbbell': ('support_unspecified', 'Decline у назві, але instructions не визначають declined bench та положення лежачи; є chest supported as required. Уточніть лаву й опори.'),
    'dragon-flag': ('support_unspecified', 'Bench or floor та stable support if used не визначають хват рук, опору й контакт верхньої спини. Уточніть конкретний варіант.'),
    'dragonfly': ('conflicting_movement', 'Для Dragonfly подано chest-fly текст з your bodyweight та невизначеною chest support. Уточніть сам рух і положення тіла.'),
    'drag-curl-barbell': ('variant_missing', 'Текст задає звичайний curl з нерухомими upper arms, не описує drag-траєкторію або відведення ліктів. Уточніть варіант.'),
    'dumbbell-squeeze-press': ('variant_missing', 'Squeeze Press у назві, але description/instructions/cues не задають контакту гантелей або постійного стискання. Уточніть контакт і хват.'),
    'dumbbell-step-up': ('load_unspecified', 'Instructions кажуть place the dumbbells beside a stable step, але не кажуть взяти чи тримати їх під час руху. Уточніть кількість/позицію ваг.'),
    'ez-bar-biceps-curl-barbell': ('equipment_unspecified', 'Назва EZ Bar, але техніка задає лише barbell та underhand grip, без відповідної конструкції/контактів хвата. Підтвердьте гриф і хват.'),
    'feet-up-bench-press-barbell': ('conflicting_supports', 'Feet Up у назві суперечить Lie on a flat bench with feet planted. Уточніть положення ніг.'),
    'frog-jumps': ('movement_unspecified', 'Типовий jump текст upward or forward as the exercise requires не визначає frog-позицію та напрямок. Уточніть варіант.'),
    'front-raise-band-resistance-band': ('anchor_unspecified', 'Відсутні анкер стрічки/контакт зі стопами. Уточніть точку опору.'),
    'front-raise-suspension': ('conflicting_equipment', 'Instructions пропонують holding your bodyweight in front of the thighs замість конфігурації suspension. Уточніть straps, анкер і нахил тіла.'),
    'front-squat-barbell': ('load_unspecified', 'Front Squat не має описаної позиції грифа на плечах чи хвата; задано лише Stand with the barbell. Уточніть front-rack опори.'),
    'full-squat-barbell': ('variant_missing', 'Не визначено положення грифа та full-глибину; controlled depth не задає конкретного варіанта. Уточніть їх.'),
    'glute-bridge-barbell': ('load_unspecified', 'barbell positioned securely if used не визначає місце грифа та контакти рук/подушки. Уточніть навантаження на таз.'),
    'hack-squat-barbell': ('conflicting_equipment', 'equipment=barbell, але instructions починаються Stand with bodyweight і не описують гриф. Уточніть обладнання та його положення.'),
    'hammer-curl-band-resistance-band': ('anchor_unspecified', 'Neutral grip задано, але точка фіксації стрічки та її конструкція відсутні. Уточніть анкер/контакт зі стопами.'),
    'hex-press-dumbbell': ('variant_missing', 'Hex Press не визначає взаємний контакт гантелей чи напрямок стискання; текст звичайного chest press. Уточніть відмінний хват/контакти.'),
    'hip-thrust-barbell': ('conflicting_supports', 'Description/cue: upper back on bench; instructions: lie flat on your back on a bench, lift hips off bench. Уточніть геометрію опор.'),
    'jump-squat': ('conflicting_cues', 'Instructions вимагають стрибка з відривом стоп, form_cues — Keep the feet planted, mistakes — Rising onto the toes. Уточніть область дії цих суперечливих cues.'),
    'jumping-lunge': ('conflicting_cues', 'Instructions вимагають переключення ніг у повітрі, form_cues — Keep the feet planted, mistakes — Rising onto the toes. Уточніть cues для стрибкового варіанта.'),
    'landmine-180-barbell': ('conflicting_movement', 'Description/cue задають hip-to-hip arc, instructions — right hip to left shoulder. Уточніть кінцеві точки.'),
    'leg-raise-parallel-bars-machine': ('conflicting_supports', 'Description задає опору зверху на брусах, instructions — Hang from the parallel bars. Уточніть підтримку чи вис.'),
    'lying-neck-extension-weighted-plate': ('support_unspecified', 'head supported із plate на потилиці не задає орієнтацію тулуба/опору і доступний діапазон. Уточніть їх.'),
    'negative-pullup': ('conflicting_movement', 'Description каже pulls from a controlled hang until chin clears; instructions — почати зверху й тільки опускатися. Уточніть опис негативної фази.'),
    'nordic-hamstrings-curls': ('anchor_unspecified', 'ankles secured не задає анкера/контакту, а assistance для повернення не конкретизовано. Уточніть опору без другої людини чи відкладеного тренажера.'),
    'pullup-weighted-machine': ('load_unspecified', 'Weighted у назві, але весь англійський блок не задає зовнішньої ваги чи її закріплення. Уточніть спосіб обтяження.'),
    'pushup-weighted': ('load_unspecified', 'Задано зовнішній load на upper back, але не тип/спосіб закріплення. Не вибирати plate/vest за здогадкою; уточніть.'),
    'ring-dips': ('conflicting_supports', 'Description задає support on rings, instructions починаються hanging from rings та пропонують lower by elbow bending. Уточніть опору зверху замість вису.'),
    'ring-pullup': ('conflicting_equipment', 'Description задає chin clears the bar, instructions — кільця. Підтвердьте текст без підміни одного обладнання іншим.'),
    'side-bend-dumbbell': ('conflicting_movement', 'Нахил away/opposite side of dumbbell одночасно описаний як lowering the weight. Напрямок нахилу й рух ваги суперечать один одному; уточніть.'),
    'single-arm-landmine-press-barbell': ('conflicting_supports', 'Stand beside the anchored end й hold its sleeve не відрізняють закріплений та вільний кінці, хоча гриф має рухатись. Уточніть робочу точку.'),
    'single-leg-standing-calf-raise-barbell': ('conflicting_supports', 'Гриф на upper back утримується руками, але safety вимагає handhold or machine support; спосіб одночасної опори не визначено. Уточніть.'),
    'squat-band-resistance-band': ('conflicting_equipment', 'Instructions задають стрічку над колінами, safety — Use a rack or machine stops. Уточніть, чи потрібна зовнішня рама, не додаючи відкладений тренажер.'),
}

# Only these 30 have scene decisions/prompts. Everything else remains ID-only queue data.
FIRST30 = [
    'standing-calf-raise', 'single-leg-standing-calf-raise', 'spiderman', 'plank-pushup',
    'wall-sit', 'l-sit-hold', 'decline-pushup', 'decline-crunch', 'frog-pumps-dumbbell',
    'standing-calf-raise-dumbbell',
    'sumo-squat-dumbbell', 'curtsy-lunge-dumbbell', 'lunge-dumbbell', 'reverse-lunge-dumbbell',
    'walking-lunge-dumbbell', 'deadlift-dumbbell', 'single-leg-romanian-deadlift-dumbbell',
    'upright-row-dumbbell', 'zottman-curl-dumbbell', 'overhead-press-dumbbell',
    'dumbbell-row', 'hip-thrust-dumbbell', 'rear-delt-reverse-fly-dumbbell',
    'chest-supported-incline-row-dumbbell', 'chest-supported-reverse-fly-dumbbell',
    'chest-supported-y-raise-dumbbell', 'spider-curl-dumbbell', 'good-morning-barbell',
    'deadlift-barbell', 'romanian-deadlift-barbell',
]
SCENES = {
    'standing-calf-raise': ('Heel-raise top hold', 'Stand with both forefeet contacting the floor, feet shoulder-width, toes forward and both heels raised. Hands touch a stable wall for balance; ankles travel vertically, torso upright. Show the wall contact and both lifted heels; no weights.', [0, 1, 2, 3]),
    'single-leg-standing-calf-raise': ('Single working heel at the top', 'Use the left foot as the sole loaded floor contact: its forefoot stays down and heel rises. Right foot is off the floor. Hands touch the wall as explicitly permitted; torso upright, working ankle aligned. No machine or weights.', [0, 1, 2, 3]),
    'spiderman': ('Right knee approaching the outside of right elbow', 'High plank with palms on the floor beneath shoulders, left leg long with toes contacting the floor. Right knee travels outside toward the right elbow. Shoulders remain over hands, hips level and trunk low; do not turn this into a crunch or put the knee inside the arm.', [0, 1, 2]),
    'plank-pushup': ('Mid-transition between forearm and high plank', 'Body remains one straight plank; toes set wide enough for balance. Right palm is planted beneath its shoulder, left forearm still contacts the floor. Depict exactly this one-arm-at-a-time transition without extra limbs; pelvis and ribs braced, hips still.', [0, 1]),
    'wall-sit': ('Static near-parallel hold', 'Back and head contact one plain stable wall; feet are forward on the floor. Knees bent about 90 degrees, thighs near parallel to the floor. Show the wall contact, both soles and the unsupported space beneath hips; no seat, weights or machine.', [0, 1, 2]),
    'l-sit-hold': ('Straight-leg L hold', 'Hands contact the floor beside hips and press down to support the body. Both legs are long, together and lifted forward near parallel to the floor, forming an L with the braced torso. Do not add bars, blocks or hanging support.', [0, 1, 2]),
    'decline-pushup': ('Controlled lowered-chest phase', 'Feet contact a stable low step and palms contact the floor; the entire body stays in one rigid inclined plank with hips aligned. Elbows bend as the chest approaches the floor. Keep both palms down. The conditional source clause "for clap push-ups" does not apply to this ID; no clap, airborne hands, knee-supported variation or added load.', [0, 1]),
    'decline-crunch': ('Small trunk curl on decline bench', 'Feet secured on a standard declined bench; pelvis and lower trunk remain supported by its pad. Curl the ribs toward the pelvis with the chin relaxed, without pulling the neck or turning the motion into a full sit-up. Show the entire bench and its actual foot-securement contacts; no external weight.', [0, 1, 2]),
    'frog-pumps-dumbbell': ('Controlled hip-extension top', 'Lie on the floor with soles pressed together and knees open. One light dumbbell is secured across the padded hip crease as stated in the source. Raise the hips through the feet, ribs down, without lumbar arching. Show the feet together, knees outward, supported upper back and centered dumbbell.', [0, 1, 2]),
    'standing-calf-raise-dumbbell': ('Both heels raised', 'Stand shoulder-width with one dumbbell in each hand hanging at the sides. Forefeet stay on the floor while both heels rise vertically; torso steady and knees do not create momentum. Both arms remain long with weights clear of the legs; no platform, machine or invented support.', [0, 1, 2]),
    'sumo-squat-dumbbell': ('Near-parallel squat bottom', 'Wide stance, toes turned outward, heels grounded. Hold one centered dumbbell in front of the hips/between the legs as the source describes; knees track toes and chest stays lifted. Hips and knees bend until thighs approach parallel. Do not convert to a chest-held goblet squat or add a second dumbbell.', [0, 1, 2]),
    'curtsy-lunge-dumbbell': ('Right foot crossed behind left in lowered phase', 'One dumbbell in each hand hangs still at the sides. Left foot stays planted; right foot steps diagonally behind and left of it. Both knees bend while torso remains upright and hips face forward. Use the short controlled diagonal step specified by the safety note, not an extreme twist.', [0, 1, 2]),
    'lunge-dumbbell': ('Right-foot-forward lowered lunge', 'One dumbbell in each hand at the sides. Right foot has stepped forward; both knees bend in the stationary lowered phase, torso upright and front heel down. Keep the weights still, knee tracking toes and back straight. This is the forward step-and-return ID, not walking or reverse lunge.', [0, 1, 2, 3]),
    'reverse-lunge-dumbbell': ('Right leg stepped backward, left thigh near parallel', 'One dumbbell in each hand hangs at the sides. Right foot is behind; left foot is the planted front foot, with left thigh parallel at the source endpoint. Torso stays straight, both knees bent, front heel down. Depict the single lowered phase of a backward step-and-return, not a forward step.', [0, 1, 2, 3]),
    'walking-lunge-dumbbell': ('Right-foot-forward loaded phase within a walking lunge', 'One dumbbell in each hand hangs at the sides. Right foot is forward and flat, both knees bend, torso upright and right knee aligned over ankle. Show the quiet loaded phase before the left foot advances into the next step; no return-to-start pose, arrows or second figure.', [0, 1, 2]),
    'deadlift-dumbbell': ('Braced hinged setup over mid-foot', 'Stand with dumbbells over the mid-foot, bend hips and knees to grip the weights close to the legs. Keep back neutral, trunk braced, head aligned and shoulders over the weights. Show the controlled setup before extending hips and knees; no squat-only posture, machine or barbell.', [0, 1]),
    'single-leg-romanian-deadlift-dumbbell': ('Left-leg-supported near-horizontal hinge', 'Left foot is the only loaded floor contact, left knee slightly bent. Right hand holds the single dumbbell lowered near the body; right leg reaches straight back. Torso and right leg approach parallel to the floor, back straight. Depict these exact source sides, without swapping hand and support leg or adding a second weight.', [0, 1, 2, 3, 4]),
    'upright-row-dumbbell': ('Controlled upper-chest endpoint', 'Stand shoulder-width with one dumbbell in each hand using the source overhand grip. Raise the elbows upward and outward as the weights travel close to the torso toward upper chest; wrists and loads remain below the leading elbows. Trunk braced, no lean or shrug-to-ear substitution.', [0, 1, 2]),
    'zottman-curl-dumbbell': ('Top curl after rotation to palms down', 'Stand hip-width, upper arms still alongside torso. Both dumbbells are at shoulder height after the palms-up curl; wrists have rotated so palms now face down, ready for the controlled reverse-grip descent. Show exactly one phase and two weights; no mixed opposite grips or extra arms.', [0, 1, 2]),
    'overhead-press-dumbbell': ('Overhead lockout', 'Standing shoulder-width, one dumbbell in each hand above its shoulder, arms extended overhead with palms facing forward. Torso braced and ribs controlled, no backward lean or leg drive. Whole arms and both weights remain in frame; no bench, Smith rails or press machine.', [0, 1]),
    'dumbbell-row': ('Right-arm row near the ribs', 'Left palm and left knee contact a flat bench; right foot contacts the floor. Right hand holds the only dumbbell and right elbow draws toward right ribs. Back flat, hips square, neck neutral, shoulder away from ear. Preserve exact left/right supports; show all three support contacts and the full bench.', [0, 1, 2]),
    'hip-thrust-dumbbell': ('Two-foot hip-extension top', 'Upper back/shoulders contact the bench edge, both feet flat, knees bent. Torso becomes level with thighs as hips rise. One padded dumbbell crosses the hip crease; both hands steady it as required by the safety note. Chin slightly tucked and ribs controlled; no lower-back overextension or full-body lying on top of bench.', [0, 1, 2, 3]),
    'rear-delt-reverse-fly-dumbbell': ('Seated hinged fly at the upper-back line', 'Sit at the bench edge, feet flat, chest near thighs in a hip hinge. One dumbbell per hand, palms face each other, elbows softly bent. Arms open to the sides until they align with upper back, without raising the chest. Show the bench, seated support and both floor contacts; no standing or prone-bench variation.', [0, 1, 2]),
    'chest-supported-incline-row-dumbbell': ('Chest-supported row toward lower ribs', 'Lie face down on an incline bench, chest firmly on the pad. Both dumbbells are drawn toward lower ribs with elbows traveling back while the chest stays down and spine steady. Show one bench, both weights and the supported torso. No invented numerical incline angle, chest lift or standing row.', [0, 1, 2]),
    'chest-supported-reverse-fly-dumbbell': ('Supported arms-out fly', 'Lie face down on an incline bench with chest on its pad. One light dumbbell in each hand; elbows softly bent, arms lifted to the sides in line with shoulders. Shoulder blades gently together, shoulders away from ears; no rowing bend or chest lift. Show bench and both weights, with no invented incline angle.', [0, 1, 2]),
    'chest-supported-y-raise-dumbbell': ('Supported Y endpoint', 'Lie face down on the incline bench with chest on its pad. Light dumbbells in both hands, thumbs lead forward; arms lift forward and outward into a Y with the torso. Keep shoulders away from ears and chest supported. Show both entire arms, bench and weights; do not turn into a lateral T raise or row, do not invent the incline angle.', [0, 1, 2]),
    'spider-curl-dumbbell': ('Prone supported curl toward shoulders', 'Chest down on an incline bench, sternum on pad. One dumbbell per hand with palms facing forward; upper arms hang still beneath shoulders as elbows bend to curl toward the shoulders. No chest lift, shrug or upper-arm swing. Show the support and full weights; no invented incline angle or preacher pad.', [0, 1, 2]),
    'good-morning-barbell': ('Controlled hip hinge', 'A light barbell rests across the upper back and is held stable; both feet planted. Hips travel backward while the neutral torso hinges forward until hamstrings are loaded, before the back rounds. Neck follows the spine; do not turn into a knee-driven squat, back extension machine or Smith movement.', [0, 1, 2]),
    'deadlift-barbell': ('Braced setup with bar over mid-foot', 'One free barbell lies over the mid-foot, close to shins. Hinge and bend knees to grip it, neutral back and braced trunk, shoulders over bar. Depict the controlled pre-lift phase before hips and knees extend together. No trap bar, guided rails, raised rack pull, lumbar rounding or exaggerated weight load.', [0, 1]),
    'romanian-deadlift-barbell': ('Controlled hip-hinge lower endpoint', 'Stand hip-width with knees softly bent. Hold one free barbell close to legs as hips travel backward and torso hinges with a neutral spine, stopping when hamstrings stretch. Keep knees only softly bent; do not turn into a deep squat, floor-reset deadlift or Smith lift. No unsupported specific grip width, load number or height measurement.', [0, 1, 2]),
}

STYLE = {
    'version': 'v1', 'human_model': 'One athletic bald male anatomical mannequin, opaque silver-gray muscular surfaces, consistent proportions and detailed 3D materials, plain black shorts, barefoot.',
    'primary_highlight': {'hex': '#F26445', 'rule': 'Highlight only the exact primary muscle group provided for this exercise.'},
    'secondary_highlight': {'hex': '#F26445', 'intensity_fraction': [0.4, 0.5], 'rule': 'Only the exact secondary muscles, lighter same-hue highlight; if the list is empty add no secondary target.'},
    'background': 'Genuinely transparent PNG background, no white/checkerboard layer, no environment scene.',
    'output': {'format': 'PNG', 'width': 1024, 'height': 1024, 'one_person': True, 'one_phase': True},
    'material_rules': 'Highlights never make tissue transparent; no glow, whole-body orange tint, hair, text, labels, arrows, UI, borders, collage or extra person.',
    'framing': 'Full figure and all required equipment/supports visible within a square. Scale and use a three-quarter view to expose the specified contacts without changing anatomy, equipment, grip or technique.',
    'no_invention': 'Technique, equipment and muscles come only from the attached exact catalogue record. No extra attachments, numerical weights, brands or exact angles absent from the source.',
}

def snapshot():
    commits = {r: git('rev-parse', r).decode().strip() for r in REFS}
    raw = git('show', commits['origin/work'] + ':' + CATALOG_PATH)
    cat = json.loads(raw)
    counts = collections.Counter(e['id'] for e in cat['exercises'])
    duplicates = [eid for eid, n in counts.items() if n != 1]
    if duplicates:
        raise ValueError('Duplicate catalogue IDs; cannot prepare: ' + repr(duplicates))
    by_id = {e['id']: e for e in cat['exercises']}
    inventory_raw = (ROOT / INVENTORY_PATH).read_bytes()
    inventory = json.loads(inventory_raw)
    original_cat_source = next(s for s in inventory['source_files'] if s['branch'] == 'work' and s['path'] == CATALOG_PATH)
    if original_cat_source['sha256'] != sha(raw):
        raise ValueError('Catalogue changed since inventory: classify changed records separately; no guessing.')
    classifications = {r['exercise_id']: r['equipment_classification']['group'] for r in inventory['exercises']}
    assert set(classifications) == set(by_id)
    docs = {}
    sources = []
    png_sources = collections.defaultdict(list)
    reserved = collections.defaultdict(list)
    touched = collections.defaultdict(list)

    def extract(v, source, ptr=''):
        if isinstance(v, dict):
            eid = v.get('exercise_id', v.get('id'))
            if isinstance(eid, str) and eid in by_id:
                reserved[eid].append({**source, 'json_pointer': ptr})
            for k, x in v.items():
                if k in ['human_reference', 'reference', 'source_english', 'prompt', 'generation_prompt', 'constraints', 'protected_source_sha256']:
                    continue
                if k == 'exercise_ids' and isinstance(x, list):
                    for i, eid in enumerate(x):
                        if isinstance(eid, str) and eid in by_id:
                            reserved[eid].append({**source, 'json_pointer': ptr + '/' + k + '/' + str(i)})
                else:
                    extract(x, source, ptr + '/' + pointer(k))
        elif isinstance(v, list):
            for i, x in enumerate(v): extract(x, source, ptr + '/' + str(i))

    for ref, commit in commits.items():
        branch = ref.removeprefix('origin/') if ref != 'HEAD' else BRANCH
        for path in git('ls-tree', '-r', '--name-only', commit).decode().splitlines():
            if path.endswith('.png'):
                parts = path.split('/')
                eid = parts[-2] if parts[-1].startswith('attempt-') else parts[-1][:-4]
                if eid in by_id: png_sources[eid].append({'branch': branch, 'commit': commit, 'path': path})
            if path.startswith('data/batches/') and path.endswith('.json') or path == PROGRESS_PATH:
                data = git('show', commit + ':' + path)
                doc = json.loads(data)
                if path in BATCH_PATHS.values() and doc.get('owner_agent') == 'agent-03':
                    # A byte-identical copy is the same reservation, not another task.
                    local_path = ROOT / path
                    if local_path.exists() and data == local_path.read_bytes(): continue
                    raise ValueError('Conflicting own-batch file on ' + ref + ':' + path)
                source = {'branch': branch, 'commit': commit, 'path': path, 'sha256': sha(data)}
                sources.append(source)
                docs[ref, path] = doc
                if path.startswith('data/batches/'):
                    extract(doc, source)
                else:
                    for eid, p in doc['exercises'].items():
                        if (p.get('status') != 'not_started' or p.get('attempts', 0) != 0 or p.get('attempt_history') or
                            p.get('result_path') or p.get('accepted_path') or p.get('result_sha256') or p.get('accepted_sha256') or
                            p.get('user_review') in ['approved', 'rejected'] or p.get('supabase_upload_status') == 'uploaded'):
                            touched[eid].append({**source, 'json_pointer': '/exercises/' + pointer(eid),
                                                 'status': p.get('status'), 'user_review': p.get('user_review'), 'attempts': p.get('attempts')})
    progress = docs['origin/work', PROGRESS_PATH]['exercises']
    style_raw = git('show', commits['origin/work'] + ':docs/exercise-image-style.md')
    workflow_raw = git('show', commits['origin/work'] + ':docs/exercise-image-workflow.md')
    handoff_raw = git('show', commits['origin/work'] + ':docs/handoff.md')
    # All context is read from the current work snapshot; no image display/download.
    reference_path = 'assets/exercises/biceps-curl-dumbbell.png'
    reference_hash = sha(git('show', commits['origin/work'] + ':' + reference_path))
    return {'commits': commits, 'catalog_raw': raw, 'catalog_sha256': sha(raw), 'catalog': cat,
            'by_id': by_id, 'classifications': classifications, 'inventory_sha256': sha(inventory_raw),
            'progress': progress, 'png_sources': png_sources, 'reserved': reserved,
            'touched': touched, 'source_files': sources,
            'style_sha256': sha(style_raw), 'workflow_sha256': sha(workflow_raw), 'handoff_sha256': sha(handoff_raw),
            'reference_path': reference_path, 'reference_sha256': reference_hash}

def readiness(e, s):
    eid = e['id']
    group = s['classifications'][eid]
    if group == 'ambiguous': return 'inventory_equipment_ambiguous', None
    if group != 'other': return 'deferred_machine_cable_smith', None
    if e['archived']: return 'archived', None
    if eid in s['png_sources']: return 'png_already_saved', None
    if eid in s['reserved']: return 'existing_batch_or_clarification', None
    if eid in s['touched']: return 'already_attempted_or_reviewed', None
    en = e['content'].get('en')
    if not isinstance(en, dict) or not en.get('description') or not en.get('instructions'):
        return 'needs_clarification', ('missing_english', 'Відсутній повний англійський description/instructions; потрібне вихідне уточнення.')
    if e['primary_muscle'] in ['full_body', 'cardio', 'other']:
        return 'needs_clarification', ('muscle_style_mapping', f'primary_muscle={e["primary_muscle"]} не задає локальної анатомічної групи для primary #F26445 у v1. Уточніть конкретні primary/secondary або окреме правило стилю; не фарбувати все тіло й не вигадувати групи.')
    if eid in TECHNICAL_CLARIFICATIONS: return 'needs_clarification', TECHNICAL_CLARIFICATIONS[eid]
    return 'eligible', None

def tier(e):
    # Actual catalogue text, not just equipment enum: some machine IDs are static bars;
    # some none IDs explicitly prescribe a plate. No new prompts for remaining IDs.
    eid, equipment = e['id'], e['equipment']
    en = e['content']['en']
    text = ' '.join(en['instructions']).lower()
    if eid in FIRST30: return 0
    if equipment == 'none' and not re.search(r'\b(bar|rings|plate|weight|support|wall)\b', text): return 1
    if equipment in ['dumbbell', 'barbell'] and not re.search(r'preacher|rack at|rack-pull|\banchor|landmine|\bbox\b|edge of a step|\bplatform\b', text): return 1
    if equipment == 'none' and re.search(r'wall', text): return 1
    if equipment in ['resistance_band', 'suspension'] or equipment == 'machine' and eid != 'wrist-roller-machine': return 2
    if re.search(r'pull-up bar|secure.*bar|overhead bar|rings', text): return 2
    return 3

def fields_for_id(eid, s):
    # This is the only exercise lookup used by queue, clarification and batch writers.
    e = s['by_id'][eid]
    return {'exercise_id': eid, 'name': e['name'], 'source_english': copy.deepcopy(e['content']['en']),
            'equipment': e['equipment'], 'primary_muscle': e['primary_muscle'],
            'secondary_muscles': copy.deepcopy(e['secondary_muscles']),
            'source_catalog_sha256': s['catalog_sha256'],
            'source_catalog_record_sha256': value_sha(e),
            'source_english_sha256': value_sha(e['content']['en'])}

def payload_for_id(eid, s):
    row = fields_for_id(eid, s)
    phase, composition, indices = SCENES[eid]
    source = row['source_english']
    payload = {'identity_do_not_render_as_text': {'exercise_id': eid, 'name': row['name'],
                'source_catalog_sha256': row['source_catalog_sha256']},
               'exact_catalogue_source': {k: row[k] for k in ['source_english', 'equipment', 'primary_muscle', 'secondary_muscles']},
               'style': STYLE, 'scene': {'single_phase': phase, 'composition': composition,
                'source_instruction_quotes': [{'index': i, 'text': source['instructions'][i]} for i in indices]},
               'reference_role': 'Human appearance/proportions/materials only. Never copy pose, equipment or muscle targets from a reference.'}
    return payload

def make_batch(bid, ids, s, timestamp):
    rows = []
    for eid in ids:
        row = fields_for_id(eid, s)
        payload = payload_for_id(eid, s)
        prompt = 'Create exactly one image for the following exact exercise record. Identity fields are metadata, never visible text. Preserve the source technique and depict only the chosen single phase.\n' + json.dumps(payload, ensure_ascii=False, sort_keys=True, indent=2)
        row.update({'prompt_payload': payload, 'generation_prompt': prompt,
                    'generation_prompt_sha256': sha(prompt.encode()), 'style_version': 'v1',
                    'planned_output_relative_path': f'{bid}/{eid}/attempt-1.png',
                    'output_root': '/workspace/exercise-image-results',
                    'result_path': None, 'result_sha256': None, 'attempts': 0,
                    'technical_check': None, 'user_review': None, 'agent_visual_review': 'not_performed',
                    'preparation_status': 'prompt_prepared_not_generated'})
        rows.append(row)
    return {'schema_version': 1, 'batch_id': bid, 'owner_agent': 'agent-03', 'branch': BRANCH,
            'prepared_at': timestamp, 'status': 'prepared_only', 'generation_authorized_now': False,
            'catalog_path': CATALOG_PATH, 'catalog_sha256': s['catalog_sha256'],
            'catalog_source_commit': s['commits']['origin/work'], 'style_version': 'v1',
            'style_path': 'docs/exercise-image-style.md', 'style_sha256': s['style_sha256'],
            'queue_path': QUEUE_PATH,
            'human_reference': {'repository_path': s['reference_path'], 'sha256': s['reference_sha256'],
                'role': 'Human appearance only; verified committed blob, not visually reviewed during preparation.'},
            'constraints': {'only_builtin_imagegen': True, 'paid_api_allowed': False, 'supabase_allowed': False,
                'shared_progress_changes_allowed': False, 'catalog_changes_allowed': False,
                'automatic_retries_allowed': False, 'generation_performed': False,
                'reuse_unchanged_ID_and_prompt_hash_for_output_manifest': True,
                'outputs_outside_git': True, 'revalidate_live_branches_before_each_call': True},
            'exercise_count': len(rows), 'exercise_ids': ids, 'exercises': rows}

def validate(s, queue, batches, clarifications):
    checked = []
    errors = []
    seen = set()
    if set(SCENES) != set(FIRST30): errors.append('scene_IDs_not_exact_first30')
    for batch in batches:
        if batch['catalog_sha256'] != s['catalog_sha256']: errors.append('batch_catalog_hash_mismatch:' + batch['batch_id'])
        if len(batch['exercises']) != 10: errors.append('batch_not_ten:' + batch['batch_id'])
        if batch['exercise_ids'] != [r['exercise_id'] for r in batch['exercises']]: errors.append('batch_id_list_mismatch:' + batch['batch_id'])
        for row in batch['exercises']:
            eid = row['exercise_id']
            if eid not in s['by_id']: errors.append('ID_missing:' + eid); continue
            if eid in seen: errors.append('duplicate_new_ID:' + eid)
            seen.add(eid)
            expected = fields_for_id(eid, s)
            for k, v in expected.items():
                if row.get(k) != v: errors.append('catalogue_field_mismatch:' + eid + ':' + k)
            disposition, _ = readiness(s['by_id'][eid], s)
            if disposition != 'eligible': errors.append('not_eligible_or_reserved:' + eid + ':' + disposition)
            if row['prompt_payload'] != payload_for_id(eid, s): errors.append('prompt_payload_mismatch:' + eid)
            expected_prompt = 'Create exactly one image for the following exact exercise record. Identity fields are metadata, never visible text. Preserve the source technique and depict only the chosen single phase.\n' + json.dumps(payload_for_id(eid, s), ensure_ascii=False, sort_keys=True, indent=2)
            if row['generation_prompt'] != expected_prompt or not row['generation_prompt'].strip(): errors.append('prompt_mismatch_or_empty:' + eid)
            if row['generation_prompt_sha256'] != sha(row['generation_prompt'].encode()): errors.append('prompt_hash_mismatch:' + eid)
            if row['planned_output_relative_path'] != f'{batch["batch_id"]}/{eid}/attempt-1.png': errors.append('output_ID_path_mismatch:' + eid)
            if row['result_path'] is not None or row['attempts'] != 0 or row['user_review'] is not None: errors.append('preparation_misreported_as_execution:' + eid)
            checked.append(eid)
    if len(seen) != 30 or checked != FIRST30: errors.append('first30_mismatch')
    all_ids = queue['eligible_exercise_ids']
    if len(all_ids) != len(set(all_ids)): errors.append('queue_duplicate_ID')
    expected_eligible = {eid for eid, e in s['by_id'].items() if readiness(e, s)[0] == 'eligible'}
    if set(all_ids) != expected_eligible: errors.append('full_queue_missing_or_extra_ID')
    if all_ids[:30] != FIRST30 or queue['remaining_unprepared_ids'] != all_ids[30:]: errors.append('remaining_queue_mismatch')
    for row in queue['exercises']:
        eid = row['exercise_id']; e = s['by_id'][eid]
        if row['name'] != e['name'] or row['equipment'] != e['equipment'] or row['primary_muscle'] != e['primary_muscle'] or row['secondary_muscles'] != e['secondary_muscles']: errors.append('queue_field_mismatch:' + eid)
        if eid not in seen and any(k in row for k in ['prompt', 'generation_prompt', 'prompt_payload']): errors.append('unexpected_rest_prompt:' + eid)
    for row in clarifications['new_clarifications']:
        for k, v in fields_for_id(row['exercise_id'], s).items():
            if row[k] != v: errors.append('clarification_field_mismatch:' + row['exercise_id'] + ':' + k)
    report = {'schema_version': 1, 'status': 'passed' if not errors else 'failed',
              'catalog_sha256': s['catalog_sha256'], 'work_commit': s['commits']['origin/work'],
              'unique_catalog_IDs': len(s['by_id']), 'batch_count': len(batches),
              'new_batch_ID_count': len(seen), 'eligible_queue_count': len(all_ids),
              'checks': {'all_IDs_exist_once': not errors, 'all_catalogue_fields_exact': not errors,
                         'new_batch_IDs_disjoint': not errors, 'no_executed_or_assigned_overlap': not errors,
                         'prompt_payload_text_and_hash_bound_to_exact_ID': not errors,
                         'planned_PNG_path_bound_to_exact_ID': not errors,
                         'remaining_queue_has_no_prepared_prompts': not errors},
              'errors': errors, 'checked_exercise_ids': checked}
    return report

def prepare(s):
    timestamp = datetime.datetime.now(ZoneInfo('Europe/Kyiv')).isoformat()
    excluded, clarifications, eligible = [], [], []
    for eid, e in s['by_id'].items():
        disposition, reason = readiness(e, s)
        if disposition == 'eligible': eligible.append(eid); continue
        row = {'exercise_id': eid, 'name': e['name'], 'reason_code': disposition,
               'inventory_group': s['classifications'][eid], 'archived': e['archived'],
               'png_sources': s['png_sources'].get(eid, []), 'reservation_sources': s['reserved'].get(eid, []),
               'progress_sources': s['touched'].get(eid, [])}
        excluded.append(row)
        if disposition == 'needs_clarification':
            clarifications.append({**fields_for_id(eid, s), 'reason_kind': reason[0],
                                   'reason_and_question_uk': reason[1], 'status': 'needs_clarification',
                                   'prompt_prepared': False, 'generation_authorized': False})
    missing = [eid for eid in FIRST30 if eid not in eligible]
    if missing:
        # No silent replacement, neighbour-record copy, or speculative correction.
        raise ValueError('First launch IDs unavailable/ambiguous; exclude and report, do not replace by guess: ' + repr(missing))
    ordered = FIRST30 + sorted((eid for eid in eligible if eid not in FIRST30), key=lambda eid: (tier(s['by_id'][eid]), eid))
    exclusions = dict(collections.Counter(r['reason_code'] for r in excluded))
    queue = {'schema_version': 1, 'queue_id': 'agent-03-other-queue', 'owner_agent': 'agent-03',
             'branch': BRANCH, 'prepared_at': timestamp, 'generation_authorized_now': False,
             'catalog_path': CATALOG_PATH, 'catalog_sha256': s['catalog_sha256'],
             'inventory_path': INVENTORY_PATH, 'inventory_sha256': s['inventory_sha256'],
             'audited_commits': s['commits'], 'source_files': s['source_files'],
             'style_version': 'v1', 'style_sha256': s['style_sha256'],
             'eligibility_rules': ['inventory other', 'active', 'no committed PNG in any checked branch',
                 'no execution attempt, result, accepted hash, reviewed result or upload',
                 'no occurrence in existing batch/manifest/index/clarification assignments',
                 'English equipment, support and technique sufficiently specified without correction',
                 'specific catalogue muscle groups usable by current v1'],
             'default_pending_note': 'Untouched not_started records carry raw user_review=pending by default. They have no submitted result and were unknown in inventory; they are not awaiting review. Existing submitted pending results are excluded by PNG/result/attempt checks.',
             'ordering': 'First 30 concrete simple compositions; then simple bodyweight/dumbbell/barbell/bench, then bars/rings/bands/suspension, then other explicitly specified apparatus. No exact angles/loads/attachments invented.',
             'eligible_count': len(ordered), 'prepared_count': 30, 'remaining_unprepared_count': len(ordered) - 30,
             'eligible_exercise_ids': ordered, 'first_launch_ids': FIRST30,
             'remaining_unprepared_ids': ordered[30:], 'batch_paths': list(BATCH_PATHS.values()),
             'exclusion_counts_disjoint': exclusions, 'excluded': excluded,
             'scope_limit': 'Only fetched committed branch snapshots and this cloud checkout; unpushed files/reservations in other cloud tasks may be unavailable. Fetch/check again before every future call.'}
    queue['exercises'] = []
    for order, eid in enumerate(ordered, 1):
        e = s['by_id'][eid]
        queue['exercises'].append({'queue_order': order, 'exercise_id': eid, 'name': e['name'],
            'equipment': e['equipment'], 'primary_muscle': e['primary_muscle'], 'secondary_muscles': e['secondary_muscles'],
            'source_catalog_sha256': s['catalog_sha256'], 'source_catalog_record_sha256': value_sha(e),
            'source_english_sha256': value_sha(e['content']['en']), 'priority_tier': tier(e),
            'batch_id': BATCH_IDS[(order - 1) // 10] if order <= 30 else None,
            'prompt_prepared': order <= 30, 'status': 'prepared_not_generated' if order <= 30 else 'queued_unprepared'})
    previous = []
    for eid, e in s['by_id'].items():
        if s['classifications'][eid] != 'other': continue
        refs = [r for r in s['reserved'].get(eid, []) if 'clarifications' in r['path']]
        if refs: previous.append({'exercise_id': eid, 'name': e['name'], 'status': 'previously_flagged_not_reassigned', 'sources': refs})
    clarify_doc = {'schema_version': 1, 'queue_id': queue['queue_id'], 'catalog_sha256': s['catalog_sha256'],
                  'work_commit': s['commits']['origin/work'], 'new_clarification_count': len(clarifications),
                  'new_reason_counts': dict(collections.Counter(r['reason_kind'] for r in clarifications)),
                  'new_clarifications': clarifications, 'previous_clarification_count': len(previous),
                  'previous_clarifications_not_reassigned': previous}
    batches = [make_batch(bid, FIRST30[i * 10:(i + 1) * 10], s, timestamp) for i, bid in enumerate(BATCH_IDS)]
    report = validate(s, queue, batches, clarify_doc)
    if report['errors']:
        raise ValueError('Pre-save validation failed; no batches saved: ' + repr(report['errors']))
    handoff = make_handoff(s, queue, clarify_doc, report)
    docs = {QUEUE_PATH: queue, CLARIFICATIONS_PATH: clarify_doc, VALIDATION_PATH: report,
            **{BATCH_PATHS[b['batch_id']]: b for b in batches}}
    for path, value in docs.items():
        dest = ROOT / path; dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n')
    (ROOT / HANDOFF_PATH).write_text(handoff)
    return queue, clarify_doc, report

def make_handoff(s, queue, clarification, report):
    lines = ['# Agent-03: черга «Інші» — тільки підготовка', '',
        f'Власна гілка: `{BRANCH}`. Work-зріз: `{s["commits"]["origin/work"]}`; agent-02: `{s["commits"]["origin/agent-02-machines-001"]}`. Каталог SHA256: `{s["catalog_sha256"]}`. У робочій гілці збережено попередній shared progress; актуальні дані читалися через Git із origin/work, не переносилися й не редагувалися.', '',
        f'Доступно **{queue["eligible_count"]}** вправ. Підготовлено **30** (3×10); **{queue["remaining_unprepared_count"]}** лишаються у черзі без prompts. Повний впорядкований список ID: [`{QUEUE_PATH}`](../{QUEUE_PATH}). Усі інші ID мають конкретну причину виключення й джерела в цьому ж файлі.', '',
        '## Відбір та уточнення', '',
        'Лише активні ID з inventory other, без PNG у work/agent-02/власній гілці; без спроб, result/accepted hashes та reviewed/uploaded результатів; без записів у старих batch/manifest/index/clarification файлах. Категорія machine сама по собі не визначає конструкцію: статичні турніки/бруси залишаються other за інвентаризацією, але тренажери/блоки/Сміт відкладено. Untouched not_started + attempts=0 + порожня історія й відсутній result при raw pending — не поданий на перегляд результат; це legacy default, effective unknown у попередній інвентаризації. Подані pending результати виключено.', '',
        'Виключення взаємовиключні за першою причиною:', '']
    labels = {'deferred_machine_cable_smith': 'Відкладені тренажери/блоки/Сміт', 'inventory_equipment_ambiguous': 'Неоднозначне обладнання в інвентаризації',
              'archived': 'Архівні з other', 'png_already_saved': 'Other із уже збереженим PNG', 'existing_batch_or_clarification': 'У старих пакетах/списках уточнень',
              'already_attempted_or_reviewed': 'Спроби/результати/перегляд без доступного PNG', 'needs_clarification': 'Нові уточнення техніки/стилю'}
    for key, n in queue['exclusion_counts_disjoint'].items(): lines.append(f'- {labels[key]}: **{n}**.')
    lines += ['', f'Нові уточнення: **{clarification["new_clarification_count"]}**; попередні не перепризначені: **{clarification["previous_clarification_count"]}**. Детальні питання й незмінний англійський текст за кожним ID: [`{CLARIFICATIONS_PATH}`](../{CLARIFICATIONS_PATH}). Загальні primary full_body/cardio/other відкладені до правила локальної підсвітки v1; це не автоматична оцінка техніки як помилкової. Не вигадувати м’язові групи, пози, ваги чи анкери.', '',
        '## Перший запуск — лише підготовлені пакети', '']
    for i, bid in enumerate(BATCH_IDS):
        lines += [f'### [{bid}](../{BATCH_PATHS[bid]})', '']
        for eid in FIRST30[i * 10:(i + 1) * 10]: lines.append(f'- `{eid}` — {s["by_id"][eid]["name"]}')
        lines.append('')
    lines += ['## Відповідність ID → джерело → prompt → PNG', '',
        'Єдине джерело даних вправ — catalog.json. Кожен повний запис отримано через словник exact ID; не через назву, схожість чи номер у масиві. У batch збережено точні name, весь en-блок (description/instructions/cues/mistakes/safety/provenance), equipment, primary/secondary muscles та SHA256 повних байтів каталогу. Додатково зафіксовано SHA256 конкретного запису, en-блока і prompt. Payload prompt містить ті самі поля; окремий scene вибрано за точним ID, із цитатами конкретних instructions, однією фазою й явними опорами. Каталог/старі пакети не виправлялися.', '',
        'Перед записом скрипт перевірив: кожен ID у каталозі рівно один раз; усі вихідні поля точно рівні своєму запису; 30 ID унікальні між пакетами; немає перетину з виконаними або старими призначеними ID; prompt/hash і планований шлях містять відповідний ID. Результат — [`validation.json`](../' + VALIDATION_PATH + '). Повторна read-only перевірка:', '',
        '```bash', "git fetch --no-tags origin '+refs/heads/work:refs/remotes/origin/work' '+refs/heads/agent-02-machines-001:refs/remotes/origin/agent-02-machines-001'", 'python scripts/prepare_agent03_other_queue.py --check', '```', '',
        'Скрипт --check нічого не записує. Якщо будь-який ID став виконаним/призначеним, source/style hash змінився чи поля не збігаються — зупинити його, виключити та повідомити; не копіювати сусідній запис, не заміняти ID автоматично й не виправляти англійську техніку здогадкою. Перед новим запуском перевірити також нові agent-гілки, якщо вони з’являться.', '',
        '## Правила майбутнього виконання — зараз не запускати', '',
        'Підготовка не є дозволом на генерацію; attempts=0, результатів і user_review немає. Чекати окремої команди користувача на цей запуск. Не створювати worktree й не працювати з локальним Mac. Перед кожним дозволеним викликом fetch/read актуальні work та agent-гілки, перевірити progress, batches і наявні PNG; пропускати approved, submitted pending, вже виконане або чужі призначення.', '',
        f'Стиль v1 з current work, SHA256 `{s["style_sha256"]}`. Human-appearance reference: `{s["reference_path"]}`, SHA256 `{s["reference_sha256"]}`. Під час підготовки еталон не відкривали для візуальної оцінки; перед майбутньою генерацією окремо перевірити файл/hash/доступність пікселів. Роль тільки зовнішність/пропорції/матеріали; не поза, обладнання чи м’язова підсвітка. Не отримувати референси з інших сервісів або старих вихідних 48 PNG.', '',
        'Після дозволу — тільки вбудований image_gen, точний непорожній generation_prompt із record, отриманого за exercise_id. Не брати prompt за позицією в масиві. Журнал фактичного виклику має містити exercise_id, batch_id, source_catalog_sha256, source_catalog_record_sha256, generation_prompt_sha256, tool-call identity, фактичний attempt, result_path і result_sha256. Планований шлях: `/workspace/exercise-image-results/<batch_id>/<exercise_id>/attempt-1.png`; він ще не існує і не видається за збережений результат. Записувати фактичний PNG від саме цього виклику під саме цим ID; звірити поля журналу й SHA256, не перейменовувати чужий output за схожістю.', '',
        'Файлова відповідність та provenance не доводять візуальної правильності картинки. У цьому етапі ні генерації, ні візуального QA немає. Не підміняти рішення користувача агентською оцінкою. Не робити автоматичних повторів/ресайзу, не працювати із Supabase чи платним API, не міняти каталог/shared progress. Майбутній журнал вести у власному окремому manifest, лише після окремого дозволу на виконання.', '',
        '**Межа:** незапушені файли/бронювання інших хмарних завдань можуть бути недоступні. Черга є перевіреним Git-зрізом, а не гарантією відсутності прихованих паралельних завдань. Зображення не генерувалися; наступний етап не розпочато.', '']
    return '\n'.join(lines)

def check_existing(s):
    queue = json.loads((ROOT / QUEUE_PATH).read_bytes())
    batches = [json.loads((ROOT / path).read_bytes()) for path in BATCH_PATHS.values()]
    clarifications = json.loads((ROOT / CLARIFICATIONS_PATH).read_bytes())
    if queue['catalog_sha256'] != s['catalog_sha256']: raise ValueError('Saved source catalogue hash is outdated')
    if queue['style_sha256'] != s['style_sha256']: raise ValueError('Style changed; revalidate prompts without guesses')
    report = validate(s, queue, batches, clarifications)
    if report['errors']: raise ValueError('Validation errors: ' + repr(report['errors']))
    return queue, clarifications, report

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument('--prepare', action='store_true')
    mode.add_argument('--check', action='store_true')
    args = parser.parse_args()
    if git('branch', '--show-current').decode().strip() != BRANCH: raise ValueError('Use agent-03 own branch only')
    s = snapshot()
    queue, clarifications, report = prepare(s) if args.prepare else check_existing(s)
    print(json.dumps({'status': report['status'], 'work_commit': s['commits']['origin/work'],
          'eligible_count': queue['eligible_count'], 'prepared_count': 30,
          'remaining_unprepared_count': queue['remaining_unprepared_count'],
          'exclusion_counts': queue['exclusion_counts_disjoint'],
          'new_clarification_reason_counts': clarifications['new_reason_counts'],
          'first_launch_ids': FIRST30}, ensure_ascii=False, indent=2))

if __name__ == '__main__':
    try:
        main()
    except (ValueError, AssertionError, KeyError, subprocess.CalledProcessError) as exc:
        print('ERROR; no guessing or silent replacement:', exc, file=sys.stderr)
        raise SystemExit(1)
