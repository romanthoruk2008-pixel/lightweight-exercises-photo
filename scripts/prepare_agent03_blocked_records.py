#!/usr/bin/env python3
"""Prepare exact-ID blocked-record decisions; never generate or edit shared state.

--prepare uses the two individually range-read source JSONs and cached primary
web texts outside Git. --check uses the committed evidence and fresh fetched
Git assignment/result metadata. It performs no pixel QA or service API calls.
"""
import argparse
import collections
import copy
import datetime
import hashlib
import json
import pathlib
import sys
from zoneinfo import ZoneInfo

import prepare_agent03_other_completion as old
import prepare_agent03_other_queue as base
import prepare_agent03_other_round3 as previous

ROOT = base.ROOT
INPUT = old.REVIEW_PATH
RESEARCH = 'data/queues/agent-03-blocked-research.json'
EVIDENCE = 'data/audits/agent-03-blocked-source-evidence.json'
STYLE_DRAFTS = 'data/queues/agent-03-neutral-primary-style-drafts.json'
STYLE_DOC = 'docs/agent-03-neutral-primary-style-proposal.md'
HANDOFF = 'docs/agent-03-blocked-preparation-handoff.md'
REPORT = 'data/queues/agent-03-blocked-validation.json'
STYLE_VERSION = 'v1-neutral-primary-draft-2026-10-02'
NEW_BATCHES = {f'agent-03-others-{n:03}': f'data/batches/agent-03-others-{n:03}.json' for n in range(16, 19)}
SOURCE_DIR = pathlib.Path('/tmp/agent03-source-texts/exercise-catalog-v1')
WEB_DIR = pathlib.Path('/tmp/agent03-web')

# Exact-ID decisions. Values are rationale, exact same-record fields, optional
# original dataset fields, and primary-source keys. No name-based joins.
DECISIONS = {
 'assisted-pistol-squats': ('Обрано документований TRX-assisted pistol: саме асистований одноногий присід з другою ногою вперед. Дві ручки і верхній анкер уточнюють відсутній вид stable support; не брати unassisted pistol або присід до лави. Raw equipment=none збережено як загальний прапорець власної ваги.', ['content.en.instructions[0]', 'content.en.form_cues[2]', 'match.rationale'], [], ['trx_pistol']),
 'bench-dip': ('Пряма прив’язка 1399 bench dip on floor, match і English instructions визначають лаву позаду та стопи на підлозі. Parallel supports у generic description не є окремим завданням на брусах. Пальці вперед прямо задає вихідний dataset.', ['content.en.instructions[0]', 'match.rationale'], ['instruction_steps.en[0]', 'instruction_steps.en[1]'], []),
 'bent-over-row-band-resistance-band': ('Виробник описує саме двосторонній bent-over band row зі стрічкою під стопами й хватом зверху. Використано лише анкер/хват; ширина стоп hip-width і тяга до нижніх ребер залишаються з каталогу, а не shoulder-width/abdomen із зовнішньої статті.', ['content.en.description', 'content.en.instructions[0]', 'content.en.instructions[1]'], [], ['trx_row']),
 'biceps-curl-suspension': ('Виробник окремо розрізняє basic supinated Bicep Curl та palms-down Reverse Bicep Curl. Для цього ID English і match задають перший: дві ручки, верхній анкер, стопи на підлозі, прямий нахил назад. Tr palms-down належить іншому варіанту й не використано. Лікті фіксовані, без просування вперед чи розведення.', ['content.en.description', 'content.en.instructions[0]', 'content.en.common_mistakes[1]', 'content.tr.instructions[0]', 'match.rationale'], [], ['trx_curl_setup', 'trx_reverse_distinction']),
 'chest-press-band-resistance-band': ('Es саме цього ID прямо задає кріплення за лавою, лежачи на рівній лаві, стопи на підлозі й рукояті над грудьми. Обрано сумісну нерухому опору за заднім кінцем лави та повний вид стрічки; не замінювати standing band press або обмотуванням тулуба. Не задано числової висоти чи напруги.', ['content.es.instructions[0]', 'content.es.safety_note', 'content.en.instructions[0]', 'content.uk.safety_note'], [], []),
 'clap-push-ups': ('Точний selected dataset 1273 задає slightly wider та плеск у повітрі; ті самі source es/it/pl узгоджені. English authored adaptation under/inside shoulders суперечить саме вихідному clap-варіанту. У derived prompt явно застосовано ширший старт із source; raw English незмінний.', ['source.dataset_id', 'match.rationale', 'content.en.instructions[0]', 'content.es.instructions[0]'], ['instruction_steps.en[0]', 'instruction_steps.en[3]'], []),
 'deadlift-band-resistance-band': ('Основна прогресія band deadlift виробника прямо задає обидві стопи на середині стрічки, утримання її двох кінців та згинання колін/стегон. Це не stiff-leg/Romanian підрозділ. Усуває over/under mid-foot: анкер під стопами, кінці в руках; зберігається conventional knee-and-hip path цього ID.', ['content.en.instructions[0]', 'content.it.instructions[0]', 'content.en.instructions[2]', 'match.rationale'], [], ['trx_deadlift']),
 'deadlift-trap-bar-barbell': ('Виробник trap bar прямо задає stand inside frame та neutral-grip handles, що збігається з uk і exact trap-bar match. Перед тілом/пронація у dataset 0811 і source перекладах є задокументованою помилкою вихідного тексту; не виправлено каталог і не додано straight-bar deadlift.', ['content.uk.instructions[0]', 'source.dataset_id', 'match.rationale'], ['instruction_steps.en[0]', 'instruction_steps.en[1]'], ['rogue_trap_position', 'rogue_trap_grip']),
 'dragon-flag': ('Pl цього самого ID прямо задає лежачи вздовж лави, дві руки за краї за головою, верхню спину/плечі на опорі та одну пряму лінію. Обрано дозволений bench/shortened-range варіант English; не навантажувати шию і не запозичувати vertical-pole flag.', ['content.pl.instructions[0]', 'content.pl.instructions[1]', 'content.pl.instructions[2]', 'content.en.safety_note', 'match.rationale'], [], []),
 'dragonfly': ('Original manifest match визначає supine straight-body shoulder-supported extension, primary=abdominals; pl саме цього ID конкретизує лаву, хват за головою, зігнуті коліна та лінію плечі–коліна. Generic chest-fly English/es суперечить власній source correspondence. Derived prompt відтворює pl/match, зберігаючи неправильний raw English окремо, без запозичення Dragon Flag.', ['match.rationale', 'primary_muscle', 'content.pl.description', 'content.pl.instructions[0]', 'content.pl.instructions[1]', 'content.pl.safety_note', 'content.en.description'], [], []),
 'front-raise-band-resistance-band': ('Для того самого bilateral band front raise виробник задає step on band middle. Використано лише цей анкер; хват palms-down береться з exact dataset 0978, а не з неузгодженого neutral label зовнішньої статті. Висота плечей/м’які лікті з English.', ['content.en.instructions[0]', 'content.en.instructions[1]', 'source.dataset_id'], ['instruction_steps.en[0]'], ['trx_front_anchor']),
 'front-raise-suspension': ('Pl і uk/es саме цього ID задають дві ручки, спиною до точки підвісу, прямий нахил вперед від стоп та підйом рук із більш вертикальним тілом. Holding your bodyweight у English є неконкретним placeholder, не вільною вагою. Відтворено ці опори без відхилення назад.', ['content.pl.instructions[0]', 'content.pl.instructions[1]', 'content.pl.safety_note', 'content.uk.description', 'content.en.instructions[0]'], [], []),
 'front-squat-barbell': ('Вихідний 0042 і uk підтверджують front-rack на передніх плечах. Офіційний основний front squat CrossFit задає лікті вперед і loose fingertip contact; crossed arms описано окремою модифікацією. Обрано основний передній rack без перехрещених рук, не довільну модифікацію. Глибина контрольована до паралелі з dataset, а не додана глибина CrossFit.', ['content.uk.instructions[0]', 'match.rationale'], ['instruction_steps.en[1]', 'instruction_steps.en[3]'], ['crossfit_front']),
 'hack-squat-barbell': ('Точний dataset 0046 і match прямо задають barbell behind legs. Bodyweight у першому English instruction суперечить equipment та прив’язаному джерелу; derived scene використовує один вільний гриф за ногами, без hack machine. Тип долонь/ширину хвата, не визначені джерелом, не додано.', ['equipment', 'source.dataset_id', 'match.rationale', 'content.en.instructions[0]'], ['instruction_steps.en[1]'], []),
 'jump-squat': ('Exact dataset 0514 і English instructions прямо задають відрив стоп та м’яке приземлення. Generic feet planted / rising onto toes не можуть бути універсальною забороною стрибка цього ID. В derived instruction обмежено feet planted контрольованим початковим присідом; airborne/landing визначає original jump source. Каталог/cues не переписано.', ['content.en.instructions[2]', 'content.en.instructions[4]', 'content.en.form_cues[0]', 'content.en.common_mistakes[1]', 'match.rationale'], ['instruction_steps.en[2]', 'instruction_steps.en[4]'], []),
 'jumping-lunge': ('Selected 3582 lunge with jump і English instructions визначають переключення ніг у повітрі. Generic planted/toes cues не поширювати на відрив/переключення. Обрано конкретну м’яку лівоногу посадку з original instruction; не статичний випад.', ['content.en.instructions[2]', 'content.en.instructions[3]', 'content.en.form_cues[0]', 'content.en.common_mistakes[1]', 'match.rationale'], ['instruction_steps.en[2]', 'instruction_steps.en[3]'], []),
 'leg-raise-parallel-bars-machine': ('English/uk/es description прямо задають SUPPORT on parallel bars, match — supported parallel-bar position, source 0826 — vertical leg raise on parallel bars. Hang означає тут підвішене без стоп тіло, а не окремий overhead hanging raise: опора двома прямими руками зверху брусів. Не додано forearm pads/captain-chair machine.', ['content.en.description', 'content.es.description', 'content.uk.description', 'match.rationale'], ['name', 'equipment'], []),
 'negative-pullup': ('Original manifest match виключає концентричний підйом, pl description та всі exact English instructions визначають negative-only lowering зі стартом chin above bar на сходинці. Generic pulls-from-hang description не використано для сцени. Один опускальний рух, без повного pull-up.', ['match.rationale', 'content.pl.description', 'content.en.instructions[0]', 'content.en.instructions[2]', 'content.en.safety_note'], [], ['trx_negative']),
 'pullup-weighted-machine': ('Exact 0841 weighted pull-up та overhand English path збережено. Виробник прямо дозволяє dip belt для pull-ups і описує chain/locking carabiners. Обрано стандартний пояс із замкнутим ланцюгом та одним млинцем, без бренду, числової ваги чи тренажера.', ['match.rationale', 'source.dataset_id', 'content.en.instructions[0]', 'content.en.instructions[3]'], ['name', 'equipment'], ['rogue_belt']),
 'ring-dips': ('Сам description, uk/es/pl, механіка lower by elbow bending → press to straight arms і офіційна CrossFit ring-dip pressing movement визначають опору зверху кілець. Hanging body у першому instruction не означає інший overhead pull-up хват. Обрано верхню опору на прямих руках перед контрольованим опусканням; не вгадано нижню глибину.', ['content.en.description', 'content.es.description', 'content.pl.description', 'content.en.instructions[1]', 'content.en.form_cues[0]', 'match.rationale'], ['name', 'equipment'], ['crossfit_dip']),
 'ring-pullup': ('Generated match прямо каже, що bar candidates не підтверджують потрібні rings. Усі English instructions та uk/es/pl description задають chin above RING height. Bar у generic English description не є дозволом замінити кільця. Дві підвішені ручні опори, без вигаданого pronated/supinated повороту.', ['match.rationale', 'content.en.instructions[0]', 'content.en.instructions[2]', 'content.pl.description', 'content.en.description'], [], []),
 'squat-band-resistance-band': ('Selected 1004 і всі instructions задають петлю ВИЩЕ колін, не довгу band deadlift петлю під стопами. English safety дозволяє rack OR machine stops: обрано лише пасивну стійку поруч/навколо вправи як safety option, без направляючих, тросів, вагового стека чи зміни опор ніг. Каталожна safety вимога збережена, не оголошена помилкою здогадкою.', ['content.en.instructions[0]', 'content.en.safety_note', 'match.rationale'], ['instruction_steps.en[0]'], []),
}

# phase, pose, grip, supports/equipment, trajectory. Camera is added explicitly
# for each row from CAMERA; nothing below is joined by title or array offset.
READY_SCENES = {
 'assisted-pistol-squats': ('Controlled assisted single-leg squat', 'Right knee and hip flexed at a controlled depth, right heel down, left leg straight forward, chest lifted.', 'Both hands securely encircle one suspension handle each; straps used only as needed for assistance.', 'Right foot grounded; two taut suspension straps secured to an overhead static anchor; left foot clear.', 'Sit hips down/back on right leg then drive through whole right foot to stand; left leg remains extended.'),
 'bench-dip': ('Controlled lower bench dip', 'Hips just in front of bench edge, elbows bent back at comfortable depth, shoulders controlled, feet forward on floor.', 'Both hands grip front bench edge behind hips, fingers FORWARD as original 1399 states.', 'One stable flat bench supports hands, both feet on floor; no parallel bars or feet-up bench.', 'Lower hips by elbow flexion and press upward without shrugging.'),
 'bent-over-row-band-resistance-band': ('Bilateral row contraction', 'Hip-width stance, fixed neutral hip hinge, elbows behind torso, hands at lower ribs, no shrug or twist.', 'One band handle firmly in each hand with source-supported overhand grip; wrists neutral.', 'Middle of the same band SECURED UNDER both feet; both feet grounded, no remote anchor or bench.', 'Pull handles toward lower ribs with elbows back, then lengthen arms under control.'),
 'biceps-curl-suspension': ('Nearly extended controlled lowering phase', 'Face overhead anchor, lean back with head-to-heels straight body; upper arms remain fixed in front at shoulder line, elbows nearly straight.', 'Both hands on handles, SUPINATED palms up; no reverse palms-down curl.', 'Feet shoulder-width on floor, both suspension straps taut to a secure overhead anchor; no seated pad.', 'Bend only elbows to bring handles toward shoulders/temple region, then slowly straighten while keeping upper arms fixed and elbows unflared.'),
 'chest-press-band-resistance-band': ('Bench-supported band press endpoint', 'Supine on flat bench, shoulder blades/back supported, feet planted, hands above chest with nearly straight arms, no back arch.', 'One band HANDLE in each closed hand, wrists stacked over forearms; no invented exact grip width.', 'Flat bench and feet support body; elastic band secured to a stationary compatible support BEHIND rear end of bench, visible continuous elastic paths to both handles. No pulleys or torso-wrap substitution.', 'Lower handles toward chest under control and press back above chest without bounce.'),
 'clap-push-ups': ('Airborne hand clap', 'Rigid plank body just above floor after explosive press, hands briefly together clapping before soft landing, no sag or knee push-up.', 'No held equipment. On floor start/reset hands slightly WIDER than shoulders per source 1273; at depicted clap hands clear floor.', 'Toes on non-slip floor, hands briefly airborne; no elevated bench.', 'Explosive press lifts hands, clap once in air, return to wider floor contacts with softly bending elbows.'),
 'deadlift-band-resistance-band': ('Braced conventional band deadlift setup', 'Hip-width grounded stance, knees and hips bent with neutral back/chest lifted, hands holding ends close to legs before knee/hip extension.', 'Both hands securely grip the two ends of the SAME band; no added bar or invented handle attachment.', 'Both feet firmly stand ON band middle, elastic secured UNDER mid-foot and ends rising to hands; no stiff-leg setup.', 'Extend knees and hips together to tall stance, no lumbar lean-back; reverse hinge with controlled knee flexion.'),
 'deadlift-trap-bar-barbell': ('Trap-bar braced floor start', 'Stand INSIDE hexagonal frame, bend hips and knees, neutral spine, shoulders controlled over handles; plates on floor.', 'One SIDE handle per hand, NEUTRAL palms facing each other, both hands fully closed.', 'Free hex/trap bar surrounds feet with plates on both outer sleeves; both feet grounded. No straight bar in front or guided rails.', 'Drive floor away, extend hips/knees to tall stance with centered load; reverse to floor without rounding.'),
 'dragon-flag': ('Short controlled bench-supported lowering', 'Shoulders/upper back supported on bench, legs together straight, hips and legs remain in one long line slightly above bench in shortened lowering range; no neck loading.', 'Both hands grip bench EDGES BEHIND head, elbows controlled.', 'Stable lengthwise bench supports upper back/shoulders; hands anchor behind head, feet and hips clear, neck unloaded.', 'Raise and lower hips/legs as one straight unit within controlled shortened range, stop before lumbar sag.'),
 'dragonfly': ('Short bent-knee shoulder-supported lowering', 'Supine upper back/shoulders on bench, knees slightly bent, shoulder-to-knee line held rigid while lowering; no chest fly.', 'Both hands grip the SAME bench edge behind head, elbows softly bent.', 'Stable bench supports upper back/shoulders, hands fixed behind head; legs/hips elevated, no cervical load or extra weight.', 'Raise hips/legs then lower shoulder-to-knee line toward bench without changing hip angle; stop before support/control loss.'),
 'front-raise-band-resistance-band': ('Band front raise at shoulder height', 'Stand tall, trunk braced and no backward lean, arms forward at shoulder height with soft elbows and shoulders down.', 'Both hands securely grasp band ends, palms DOWN at raised phase per selected original 0978.', 'Band middle SECURED UNDER both grounded feet; no high anchor, pulley or extra dumbbells.', 'Raise arms forward to shoulder height and lower slowly without swing.'),
 'front-raise-suspension': ('Forward-lean suspension raise endpoint', 'Face AWAY from suspension anchor, straight body inclined slightly forward from grounded feet; arms raised forward at comfortable shoulder height as body becomes more upright.', 'Both closed hands grip one suspension handle each, wrists neutral; no held bodyweight object.', 'Two taut straps to secure overhead suspension point BEHIND body; both feet on floor, no back pad or chest support.', 'Raise arms forward with soft elbow bend and bring body toward upright, then return to controlled forward lean.'),
 'front-squat-barbell': ('Controlled front-rack squat lower phase', 'Feet about shoulder-width/toes slightly out, heels grounded, neutral braced torso upright, knees aligned, thighs at comfortable source parallel depth.', 'Both hands make loose FINGERTIP contact UNDER front-rack bar, elbows pointing FORWARD/high; no crossed arms.', 'Free bar rests on front shoulders above clavicles, feet support body; passive rack nearby for setup, no Smith.', 'Bend hips/knees to controlled depth while keeping front rack, then drive whole feet to stand.'),
 'hack-squat-barbell': ('Standing endpoint with rear bar', 'Tall balanced stance, feet about shoulder-width/toes slightly out, one bar BEHIND legs at rear upper thighs, arms straight and back neutral.', 'Both hands firmly grip the SAME free bar behind legs; no invented palm direction/spacing absent from source.', 'Feet grounded, free bar behind thighs, no machine sled, pad, rails or bodyweight-only substitution.', 'Bend knees/hips into controlled rear-loaded squat then stand while keeping bar behind legs.'),
 'jump-squat': ('Airborne hip-knee-ankle extension', 'Body just airborne after squat, hips/knees/ankles extending, arms forward for balance, trunk controlled and no knee collapse.', 'Hands free, no weight.', 'Both feet CLEAR of non-slip floor during jump; clear landing space. Feet planted cue belongs to grounded squat setup only.', 'Squat then jump, land softly on forefeet with knees/hips flexing; never depict locked-knee landing.'),
 'jumping-lunge': ('Left-foot-forward soft landing', 'After airborne switch, left foot forward and right foot back, knees/hips flexed into quiet balanced lunge landing; torso controlled.', 'Hands free, no load.', 'Both feet meet clear floor in switched LEFT-forward stance; no stationary step or step-up.', 'From right-front lunge jump and switch feet in air, land left-front and lower into lunge; reset under control.'),
 'leg-raise-parallel-bars-machine': ('Straight legs near hip height', 'Torso upright between bars, shoulders down, elbows STRAIGHT, both legs together straight in front near hip height, no swing.', 'One hand firmly encircles each parallel bar with load supported from ABOVE, wrists aligned.', 'Static parallel bars support hands at sides BELOW shoulders, full body otherwise clear of floor; no overhead hang, pads or machine stack.', 'Lift straight legs through controlled hip flexion toward hip height and lower without momentum.'),
 'negative-pullup': ('Midway through negative descent', 'Controlled vertical body hang descending from chin-above-bar start, elbows partially extending, trunk quiet and shoulders active.', 'Secure OVERHAND grip on fixed high bar.', 'Secure bar supports hands; stable setup step visible below and clear of feet during descent.', 'Start at top using step, ONLY lower slowly until arms straight, then step down/reset; no concentric pull or kip.'),
 'pullup-weighted-machine': ('Weighted chin-clearing top', 'Chin above fixed bar, elbows pulled toward torso, ribs stacked, shoulders down, legs quiet clear of floor.', 'Overhand grip slightly WIDER than shoulder width.', 'Static pull-up bar, waist dip belt with a CLOSED securely latched chain through ONE modest plate hanging centrally clear of feet; no branding/numerical load or machine.', 'Pull from controlled full hang to chin above bar, then lower under control without swing.'),
 'ring-dips': ('Upper straight-arm support before lower', 'Torso held above ring grips, arms STRAIGHT alongside trunk, shoulders controlled and wrists stacked, legs quiet below without ground contact.', 'One closed hand per ring, wrists aligned over elbows; no overhead pull-up grip.', 'Two rings suspended on taut securely anchored straps, hands support from ABOVE with rings at sides below shoulders; no foot platform or machine.', 'Lower torso by bending elbows and press back to straight-arm support; choose top phase, add no unverified bottom-depth angle.'),
 'ring-pullup': ('Controlled ring-height top', 'Chest raised toward rings, chin above ring height, elbows down, trunk and legs quiet.', 'One closed hand encircles each RING, wrists aligned; exact palm rotation not prescribed or invented.', 'Two rings on secure overhead straps, body hanging clear of floor; do not replace hand contacts with BAR.', 'Pull from straight-arm ring hang to controlled ring-height top, lower fully without ring swing.'),
 'squat-band-resistance-band': ('Controlled knees-out band squat bottom', 'Feet shoulder-width/heels grounded, hips back and knees aligned with toes, chest lifted, paused comfortable depth.', 'Hands free for balance, no held bar or long-band ends.', 'Short band LOOP just ABOVE knees, both feet on floor, passive unweighted RACK safety option nearby as English permits. No machine stops/rails, cable, weight stack or band under feet.', 'Flex hips/knees with controlled band tension above knees, then drive through heels to stand.'),
}
CAMERA = {eid: 'Front-side three-quarter view showing whole person, all supports/anchors and each prescribed contact; square frame, no crop.' for eid in READY_SCENES}
CAMERA.update({'deadlift-trap-bar-barbell': 'Front-side three-quarter view clearly exposing feet INSIDE frame and both neutral side grips.', 'dragon-flag': 'Side three-quarter view exposing behind-head edge grips, shoulder support and straight elevated body.', 'dragonfly': 'Side three-quarter view exposing upper-back support, behind-head grips and shoulder-to-knee line.', 'hack-squat-barbell': 'Rear-side three-quarter view showing free bar BEHIND legs and both hand contacts.', 'ring-dips': 'Front-side three-quarter view showing hands/rings BELOW shoulders in straight-arm support.'})

QUESTIONS = {
 'chest-dip-weighted-machine': ('parallel_or_straight_bar', 'Паралельні бруси з English instructions чи одна пряма перекладина з назви dataset 3313? Пояс із ланцюгом можливий для обтяження, але не вирішує суперечність опор.', ['Паралельні бруси', 'Одна пряма перекладина'], ['match.rationale', 'content.en.instructions[0]']),
 'drag-curl-barbell': ('drag_or_fixed_arms', 'Потрібен drag curl із ліктями назад і грифом уздовж тулуба чи звичайний curl з нерухомими верхніми руками, як у dataset 0038?', ['Drag: лікті назад, гриф уздовж тулуба', 'Звичайний curl: верхні руки нерухомі'], ['content.en.instructions[1]', 'match.rationale']),
 'feet-up-bench-press-barbell': ('feet_support', 'Стопи у повітрі зі зігнутими колінами (pl/it) чи поставлені на лаву (es)? English feet planted також збережено як суперечність; звичайним жимом ID не підміняти.', ['Стопи у повітрі, коліна зігнуті', 'Стопи стоять на лаві'], ['content.pl.instructions[0]', 'content.es.instructions[0]', 'content.en.instructions[0]']),
 'hammer-curl-band-resistance-band': ('band_anchor', 'Який саме band hammer curl: центр стрічки під стопами з двома нейтральними ручками чи низький зовнішній анкер? Знайдені regular/seated curls не є підтвердженням цього варіанта.', ['Стрічка під стопами, дві ручки', 'Низький зовнішній анкер: уточнити кріплення'], ['content.en.instructions[0]', 'match.rationale']),
 'hip-thrust-barbell': ('hip_support', 'Верхня спина на краю лави, таз поза лавою, чи lying hip lift із тулубом на лаві й підйомом таза з неї, як у 0058? Потрібна одна геометрія опор.', ['Верхня спина на краю, таз поза лавою', 'Лежачий hip lift на лаві з dataset 0058'], ['content.en.description', 'content.en.instructions[0]', 'content.en.instructions[2]']),
 'landmine-180-barbell': ('rotation_endpoints', 'Повна дуга від одного стегна до іншого чи right hip → left shoulder із вихідного 0562? Уточніть кінцеві точки та напрямок обох повторів.', ['Hip-to-hip дуга', 'Праве стегно → ліве плече'], ['content.en.description', 'content.en.instructions[2]', 'content.en.form_cues[1]']),
 'lying-neck-extension-weighted-plate': ('neck_support', 'Лежачи животом на лаві з головою за краєм (тоді head supported потребує пояснення) чи інша лежача орієнтація з рухомою опорою голови? Укажіть опору та доступний діапазон.', ['Животом на лаві, голова за краєм', 'Інша лежача орієнтація й тип опори: уточнити'], ['content.en.instructions[0]', 'content.en.instructions[2]']),
 'nordic-hamstrings-curls': ('ankle_anchor', 'Фіксувати щиколотки під нерухомою рейкою/валиком у стійці чи ременем до нерухомої опори? Потрібна однозначна конструкція без другої людини й спеціалізованого тренажера.', ['Нерухома рейка/валик у стійці', 'Ремінь до нерухомої опори'], ['content.en.instructions[0]', 'content.en.instructions[3]']),
 'pushup-weighted': ('secure_upper_back_load', 'Зберігаємо млинець на верхній спині — тоді який перевірений фіксатор для однієї людини — чи дозволено ваговий жилет/плитний носій? Виробник описує carrier, але це не доказ способу утримання круглого вільного млинця.', ['Млинець: потрібен конкретний сумісний фіксатор', 'Дозволити жилет/плитний носій'], ['content.en.instructions[0]', 'content.en.common_mistakes[0]', 'content.en.safety_note']),
 'side-bend-dumbbell': ('bend_direction', 'Нахил до руки з гантеллю, коли вага опускається, чи від неї, коли вага піднімається? Dataset 0407 повторює суперечливе away + lowering.', ['До гантелі: вага опускається', 'Від гантелі: вага піднімається'], ['content.en.description', 'content.en.instructions[1]']),
 'single-arm-landmine-press-barbell': ('landmine_support', 'Стоячий split-stance press вільного кінця без спинки чи окремий supported варіант зі спинкою? У всіх блоках переплутано anchored/free end і додано back-pad cues; half-kneeling приклад виробника має інші опори й відхилений.', ['Стоячи, вільний кінець, без спинки', 'Варіант з опорою тулуба: уточнити'], ['content.en.instructions[0]', 'content.en.instructions[1]', 'content.en.form_cues[0]', 'content.en.safety_note']),
 'single-leg-standing-calf-raise-barbell': ('bar_and_hand_support', 'Обидві руки утримують вільний гриф без ручної опори чи одна рука на грифі, друга на визначеній опорі? English safety handhold/machine support не задає спосіб одночасного утримання; Smith не додавати.', ['Дві руки на вільному грифі, без ручної опори', 'Одна рука на грифі, друга на опорі: уточнити'], ['content.en.instructions[1]', 'content.en.safety_note']),
}

# Separate from the shared neutral-primary proposal: these cannot become ready
# merely by approving a muscle-color rule. No movement/equipment is guessed.
STYLE_EXTRA = {
 'clean-barbell': ('receiving_variant', 'Яка глибина приймання Clean: повний присід чи partial/power? Match відкидає power як іншу глибину, але soft knees/elbows under не задають приймання. Уточніть також лікті вперед у front rack.'),
 'hiit': ('representative_movement', 'Який конкретний bodyweight рух показувати в робочому HIIT інтервалі? Ходьба в source є лише відновленням; оберіть рух або окрему ілюстрацію відновлення.'),
 'hiking': ('footwear_compatibility', 'Для Hiking з вимогою suitable footwear дозволити сумісне взуття чи окремо погодити анатомічну ілюстрацію босоніж? Нейтральне фарбування не змінює barefoot v1.'),
 'muscle-up-machine': ('grip_transition', 'Зберігати overhand bar muscle-up з переходом кистей над баром чи справді змінювати хват на supinated, як у instructions[2]? Визначте також повну press-to-support фазу, яку instructions пропускають.'),
 'pilates': ('representative_movement', 'Який конкретний Pilates рух/позу показувати? Selected Pilates movement не визначено; не підставляти Hundred, Roll-Up чи іншу вправу самостійно.'),
 'press-under-barbell': ('receiving_variant', 'Яке receiving положення Press Under: частковий присід, повний присід чи інше? Start chest/finish overhead задані, але рух тіла під грифом і опори ніг не визначені.'),
 'snowboarding': ('footwear_compatibility', 'Погодити snowboard boots/сумісні кріплення й захисне спорядження, чи потрібен окремо визначений тренувальний barefoot варіант? Наявний текст вимагає secured feet/protective gear.'),
 'stretching': ('representative_movement', 'Яку конкретну ділянку і stretch-позу показувати? Chosen muscle group/position відсутні; основну групу чи позу не вигадувати.'),
 'walking': ('footwear_compatibility', 'Для Walking з appropriate footwear дозволити сумісне взуття чи окремо погодити анатомічну ілюстрацію босоніж? Потрібне одне рішення разом із Hiking/Snowboarding.'),
 'yoga': ('representative_movement', 'Яку конкретну Yoga позу/перехід показувати? Planned poses не задані; standing/kneeling setup не підміняє визначену асану.'),
}

STYLE_SCENES = {
 'aerobics': ('Easy marching phase', 'Upright torso and relaxed shoulders, one knee lifting in gentle source march, opposite arm coordinating, no maximal effort.', 'Hands free, no equipment.', 'Other foot supports on clear non-slip floor; no step platform invented.', 'Alternate controlled marching steps and coordinated arms at comfortable rhythm.'),
 'ball-slams': ('Ball overhead before slam', 'Stand about shoulder-width, both arms securely hold ball overhead in FRONT, core braced and knees/hips soft.', 'Both hands securely support the SAME slam-rated medicine ball.', 'Both feet grounded, clear rebound/landing area, no wall target.', 'Drive overhead ball into floor in front, retrieve by controlled squat/hinge, reset.'),
 'battle-ropes-machine': ('Alternating rope waves', 'Stable athletic stance with soft knees, right hand higher and left lower creating alternating waves, quiet trunk.', 'One rope END firmly in each hand.', 'Both feet planted; the two ends belong to battle rope fixed at visible secure distant anchor. No cable station or weight stack.', 'Alternate lifting/lowering hands so waves travel toward rope anchor.'),
 'boxing': ('Controlled straight punch with opposite guard', 'Balanced boxing stance, hips rotate with one controlled straight punch, elbow not locked, chin tucked, opposite hand near face.', 'Hands unweighted; one fist punching, other at guard, no invented gloves or bag.', 'Stable floor foot contacts in clear space.', 'Alternate straight punches/hooks and return each hand to guard; choose one straight punch phase.'),
 'burpee': ('Braced plank transition', 'Straight high plank, trunk braced and no hip sag before feet return under hips.', 'Palms on floor directly under shoulders, no handles.', 'Both palms and toes on non-slip floor, no extra equipment.', 'Squat to palms down, step/jump feet to plank, return feet, stand and vertical jump with soft landing.'),
 'burpee-broad-jumps': ('Forward broad-jump soft landing', 'Both feet landing forward with knees/hips flexed after source burpee sequence, arms balancing naturally and torso controlled.', 'Hands free; earlier plank uses floor palms.', 'Both feet on clear non-slip landing floor, no box or vertical-only jump.', 'Same-ID es/pl: squat→hands down→plank→feet in→stand→FORWARD broad jump; depict only soft landing.'),
 'burpee-over-the-bar': ('Lateral airborne bar crossing', 'Athlete airborne SIDEWAYS over low grounded bar after standing from plank, knees soft and torso controlled, no bar load held.', 'Hands free; palms only contact floor in preceding plank.', 'A stationary standard free bar lies on floor below lateral jump; no moving bar or hurdle substitution.', 'Squat to plank and return feet, stand, jump sideways over bar, land softly on opposite side.'),
 'clean-and-jerk-barbell': ('Stable split-jerk overhead endpoint', 'Bar overhead with straight elbows and stable split stance, front/rear knees soft, neutral braced torso.', 'Both hands securely grip the SAME bar in overhead rack, no invented width or alternate weights.', 'Front and rear feet grounded in explicit split source option; free bar overhead with clear space.', 'Floor clean to shoulders, dip/drive overhead into source split option, lower safely; depict only jerk catch.'),
 'clean-and-press-barbell': ('Controlled overhead press endpoint', 'Stand tall with braced core, elbows straight and wrists stacked overhead, no lumbar lean-back.', 'Both hands on SAME free bar, source shoulder-width grip.', 'Both feet grounded, no split jerk or machine.', 'Clean floor-to-shoulders and stabilize, then press overhead, lower to shoulders and floor.'),
 'clean-pull-barbell': ('Tall extension with close upward bar', 'Neutral braced torso after knee/hip extension, bar close, elbows high only AFTER hip drive, no front-rack catch.', 'Both hands securely grip bar just OUTSIDE legs.', 'Feet grounded in controlled pulling stance, same free bar, clear lane.', 'Floor start from midfoot, knee/hip extension and upward pull, lower WITHOUT receiving in front rack.'),
 'climbing': ('Low three-contact controlled reach', 'Torso close to secure climbing holds; left hand and both feet securely placed while right hand reaches deliberately, legs push rather than continuous arm pull.', 'Left hand securely grips climbing hold, right reaching to next secure hold; no unspecified rope grip.', 'Low fixed climbing-hold surface, three contacts and appropriate padded LANDING surface choosing explicit landing-or-belay option. No height, harness or belay person invented.', 'Shift weight before reaching, stand through legs and establish next contact under control.'),
 'deadlift-high-pull-barbell': ('Upper-chest high-pull endpoint', 'Stand tall after knee/hip drive, bar close toward upper chest, elbows high and core controlled without lean-back.', 'Both hands firmly grip same free bar; no invented sumo stance or exact hand width.', 'Both feet grounded, free bar, no cable or rack pull substitution.', 'Hinge then extend hips/knees, AFTER extension high pull toward upper chest, lower/reset.'),
 'dumbbell-snatch': ('Single-dumbbell overhead reception', 'Right arm straight overhead with wrist stacked, knees/hips softly flexed, neutral core; left arm free and unweighted.', 'RIGHT hand holds ONE dumbbell, same-ID selected 3888/es one-arm source; no pair of dumbbells from generic English plural.', 'Both feet grounded, clear overhead space, one free dumbbell only.', 'One-arm close hinge-to-overhead path in continuous lift, receive softly and lower safely.'),
 'farmers-walk': ('Short controlled forward carry step', 'Tall braced torso, level shoulders and chin, arms straight at sides, one short forward step without swinging.', 'One DUMBBELL firmly in each hand, palms toward torso as same-ID es/selected 2133 defines.', 'Walking floor, both free dumbbells clear of legs; no unspecified kettlebells or carry frames.', 'Walk forward in short even steps, stop before safely lowering both dumbbells.'),
 'front-lever-hold': ('Straight horizontal hold', 'Body held in one horizontal line from shoulders through hips to pointed feet, no sag or kip, shoulders depressed.', 'Both hands on bar with OVERHAND grip.', 'Secure overhead fixed bar supports hands; hips/legs horizontal and clear of floor.', 'From controlled hang lift into horizontal body line and HOLD, lower safely; no repeated dynamic raise.'),
 'front-lever-raise': ('Horizontal raise endpoint', 'Long straight body at highest controlled horizontal lever line, shoulders down and legs together, no swing.', 'Both hands securely grip fixed bar; do not invent palm direction not stated for this ID.', 'Fixed secure bar supports hands, body clear of floor.', 'From still hang raise legs/hips toward horizontal, pause briefly, lower slowly.'),
 'handstand-hold': ('Supported wall handstand hold', 'Straight arms supporting inverted body, shoulders/hips/ankles stacked, ribs tucked, head neutral, toes lightly supported at clear wall.', 'Spread fingers and palms flat shoulder-width on floor.', 'Both palms on clear floor and clear WALL support choosing catalogue wall-or-spotter option; no second person.', 'Enter supported handstand, hold aligned and breathe, lower one foot at a time.'),
 'hang-clean-barbell': ('Front-shoulder reception after hang', 'Soft knees receiving bar on FRONT shoulders, trunk braced, elbows controlled without forcefully dropping.', 'Both hands securely grip same bar just OUTSIDE legs in hang, maintain shoulder rack support.', 'Both feet grounded, free bar at front shoulders; no floor-start setup.', 'Start bar at THIGH hang, hinge slightly, extend hips/knees close to body, receive shoulders, return to hang.'),
 'hang-snatch-barbell': ('Controlled hanging start', 'Stand braced with same bar hanging close in front of legs, straight controlled arms before continuous lift; no floor start.', 'Both hands firmly grip same free bar; exact numerical width not prescribed or invented.', 'Both feet grounded and bar CLEAR of floor in allowed HANG option.', 'From hang accelerate close to body into one continuous overhead reception, then lower safely.'),
 'high-knee-skips': ('Right knee drive before skip switch', 'Stand tall with RIGHT knee toward hip height and LEFT foot supporting, torso upright and arms controlled.', 'Hands free, no weights.', 'Left foot on non-slip floor, right foot clear.', 'Switch legs with small HOP as skips option, land quietly; no non-skipping quick-step substitution.'),
 'jump-rope': ('Light rope-clearance hop', 'Body a small hop above floor with soft knees, upright relaxed trunk, rope passing below both feet.', 'One jump-rope handle per hand, palms inward.', 'One complete rope loop visible, feet briefly airborne over clear non-slip floor.', 'Rotate rope over head and under feet, repeated light hops and soft forefoot landings.'),
 'jump-shrug-barbell': ('Explosive tall shrug above floor', 'Hips/knees extend after small dip, shoulders shrug as close bar rises, torso neutral; soft knees prepared for landing.', 'Both hands securely grip free bar just OUTSIDE legs.', 'Both feet briefly airborne in clear lane, same free bar close; no clean catch.', 'Thigh-hang dip, knee/hip extension plus shrug, soft landing and controlled lower.'),
 'kettlebell-clean': ('Soft single-bell rack catch', 'Tall braced hinge-driven finish, one bell softly at RIGHT forearm/rack, wrist aligned and no squat-under substitution.', 'Right hand around SAME kettlebell handle, hand rotates around handle as source specifies.', 'Both feet grounded, single kettlebell at right forearm, free hand unweighted.', 'Hike from between legs, hip drive close, rotate hand to receive forearm rack, return between legs.'),
 'kettlebell-high-pull': ('Close chin-height high pull', 'Wide stance/toes out, knees/hips extended after squat, single bell toward chin, elbows high and wide, no torso swing.', 'Both hands securely grip SAME kettlebell handle.', 'Both feet grounded, one free kettlebell, no pulley.', 'Squat then hip/knee drive, bell close upward with elbows above handle, lower under control.'),
 'kettlebell-snatch': ('One-bell overhead lockout', 'Right arm straight overhead, core controlled and no back arch, single bell stabilized at right hand/forearm.', 'Right hand securely through same bell handle after source rotation/punch-through.', 'Both feet grounded shoulder-width, clear overhead space, free left hand.', 'One-hand backswing/hip drive, rotate and punch through overhead in ONE fluid pull, return between legs.'),
 'kettlebell-swing': ('Two-hand shoulder-height float', 'Hips extended, neutral torso, both arms straight holding one bell forward at shoulder height; no arm-lift shrug.', 'Both hands firmly hold SAME kettlebell handle.', 'Both feet grounded shoulder-width/toes slightly out, one free bell.', 'Hip hinge sends bell between legs, hip drive floats it to SHOULDER height, return to hinge; no overhead swing.'),
 'kettlebell-turkish-get-up': ('Source initial supine lockout', 'Supine with RIGHT knee bent and right kettlebell straight above right shoulder, left leg long, neutral trunk before transition.', 'Right hand securely grips ONE bell, wrist stacked; left palm free on floor for support as transition permits.', 'Back/pelvis and right foot on floor, right arm vertical with same bell, no extra weight.', 'From specified supine setup progress to supported half-kneel and standing while bell stays overhead, reverse; show only initial setup.'),
 'landmine-squat-and-press-barbell': ('Forward/up press after stand', 'Face FREE bar end, legs extended after squat, chest up, same free end held forward/up without backward lean.', 'Both hands firmly hold FREE end of anchored bar.', 'Opposite end fixed in secure landmine base; both feet grounded, full bar/anchor visible.', 'Chest-held squat, stand through feet and press forward/up, return end to chest for next squat.'),
 'overhead-squat-barbell': ('Controlled overhead squat bottom', 'Feet shoulder-width/toes slightly out, heels grounded, knees tracking toes and chest up, controlled depth, elbows straight overhead.', 'WIDE bilateral grip on SAME free overhead bar.', 'Both feet grounded, free bar stacked above body, no Smith.', 'Hold bar overhead while hips/knees flex to controlled squat and extend to stand.'),
 'power-clean-barbell': ('Standing front-rack finish', 'Stand TALL after source catch, bar on FRONT shoulders, elbows HIGH, trunk neutral, no lean-back.', 'Both hands keep source overhand bar hold/front-rack contact, no cross-arm variant.', 'Both feet grounded, same free bar on front shoulders.', 'Floor bar over midfoot, extend hips/knees, pull under to front shoulders, STAND tall, lower safely.'),
 'power-snatch-barbell': ('Partial-squat overhead catch', 'Receive bar overhead with STRAIGHT locked elbows in PARTIAL squat, knees/hips flexed and back neutral.', 'WIDE OVERHAND grip on same free bar.', 'Both feet grounded, free bar overhead, clear area; no deep full-snatch catch.', 'Floor pull close, extend hips/knees then pull under into partial squat, stand and lower.'),
 'running': ('In-place running knee lift', 'Torso upright/relaxed, one knee lifted toward chest as source jogging-in-place states, opposite leg soft for ground contact.', 'Hands free and relaxed in running arm pattern.', 'Non-slip floor, no treadmill, track scenery or outdoor forward-running substitution.', 'Alternate IN-PLACE jogging knee lifts and soft forefoot contacts at steady pace.'),
 'skating': ('Right-foot skater bound landing', 'Soft RIGHT one-foot landing with chest slightly forward, left leg sweeps behind and taps floor, right knee aligned.', 'Hands free for balance; no skates or poles.', 'Right foot grounded with left toe light source tap; clear non-slip floor.', 'Bodyweight sideways bound right, free leg sweeps behind, repeat left; no ice equipment.'),
 'skiing': ('Right diagonal bodyweight step', 'Athletic softly bent knees, torso slightly inclined, step diagonally RIGHT with LEFT arm forward, controlled feet.', 'Hands free; no poles or skis absent from the specified cardio DRILL.', 'Clear LEVEL floor, no snow scene or ski machine.', 'Alternate quick diagonal right/left steps with opposite arms, steady rhythm.'),
 'sled-pull': ('Short backward sled step', 'Face sled, trunk braced/chest lifted, hips slightly back, one short backward step with uncrossed feet.', 'Both hands firmly hold rope/strap at WAIST height.', 'Rope/strap securely attached to weighted sled, taut line and clear lane visible, no hip harness substitution.', 'Walk BACKWARD with steady line tension dragging sled toward body, stop then lower line.'),
 'sled-push': ('Forward driving short step', 'Lean forward FROM ANKLES, neutral spine with aligned hips/shoulders, arms extended into handles, short controlled driving step.', 'Both hands firmly grip sled handles.', 'Stable weighted sled on clear contact surface, both handles and feet visible; no unrelated machine.', 'Continuous forward pressure through short steps, slow before releasing handles.'),
 'snatch-barbell': ('Deep overhead receiving squat', 'Catch same bar overhead in DEEP squat with elbows locked, knees aligned, neutral braced back and planted feet.', 'WIDE OVERHAND grip on same free bar.', 'Both feet grounded, free bar over shoulders, clear overhead space; no partial power-snatch substitution.', 'Floor pull/extension, pull under into deep receiving squat, stand through feet, lower safely.'),
 'split-jerk-barbell': ('Stable split overhead catch', 'Front RIGHT foot and rear LEFT foot grounded in stable split, knees bent, elbows locked and bar over shoulders, ribs controlled.', 'Both hands securely grip same bar, wrists stacked overhead.', 'Two grounded feet in explicit split, free bar overhead; passive rack for start, no extra person.', 'Shoulder rack, vertical dip/leg drive, split catch, recover front foot back and rear forward.'),
 'sprints': ('Controlled acceleration stride', 'Forward lean with knee drive, opposite arms driving straight, foot strike under hips and no overstride.', 'Hands free, no weights.', 'Clear level running contact surface, no starting blocks invented.', 'Progressively accelerate down straight path, controlled hard stride, gradual deceleration and recovery.'),
 'suitcase-carry-dumbbell': ('Short level unilateral carry step', 'Tall braced torso/level hips and shoulders, one short forward step, loaded RIGHT arm straight and left relaxed.', 'RIGHT hand holds ONE dumbbell at side, free left hand unweighted.', 'Walking contact surface, dumbbell clear of thigh; no second dumbbell or sideways lean.', 'Walk forward in even short steps, stop and safely set weight down before changing hand.'),
 'swimming': ('Prone opposite-limb lift', 'Lie PRONE with right arm and left leg slightly lifted, opposite limbs remain long, pelvis heavy and ribs not high.', 'Hands open/unweighted, arms extended overhead.', 'Floor/mat supports torso/pelvis; no pool, swim gear or standing stroke substitution.', 'Small alternating RIGHT-arm/LEFT-leg and LEFT-arm/RIGHT-leg beats with straight legs, steady breathing.'),
 'thruster-barbell': ('Overhead finish after squat drive', 'Stand after front-rack squat, knees/hips extended before overhead press, elbows straight overhead and ribs down.', 'Both hands securely hold same free front-rack bar, wrists stacked overhead; no numeric width.', 'Both feet grounded shoulder-width, free bar overhead; no jerk split.', 'Front-rack squat, leg drive immediately press overhead, controlled return to shoulders/squat.'),
 'thruster-kettlebell': ('Two-handed one-bell overhead finish', 'Stand after squat, knees/hips extended before same bell press overhead, elbows straight and ribs controlled.', 'BOTH hands hold ONE bell in source es/pl facing-palm grip, no pair of bells or unilateral rack.', 'Both feet grounded shoulder-width, one free bell above body.', 'Chest-held two-hand squat, leg drive press same bell overhead, return toward chest as source es/pl states.'),
 'wall-ball': ('Ball leaving hands toward wall target', 'Knees/hips extend from source squat as ball is released upward, chest controlled and torso balanced.', 'Both hands release SAME medicine ball upward after chest hold; no held second ball.', 'Feet grounded, impact-rated wall with a simple UNLABELED target area and clear catch zone; no invented target height.', 'Chest-held squat to near parallel, leg drive throws ball vertically toward wall target, catch with bent elbows.'),
 'warm-up': ('Easy source marching with arm swing', 'Tall relaxed torso, one gentle marching knee lift with smooth arm swing, no workout-intensity jump.', 'Hands free, no equipment.', 'Clear stable floor, no inferred stretch or added weight.', 'Begin with EASY marching and arm swings before source squat/hinge/reaches; show only initial marching.'),
}

# Primary publications actually fetched. Quotes below are short and scope-limited;
# publisher targets/load numbers never override catalogue equipment or muscles.
WEB = {
 'trx_pistol': ('https://www.trxtraining.com/blogs/news/single-balance-leg-exercises', 'TRX', '4. TRX-Assisted Pistol Squat', ['Anchor your Suspension Trainer™ overhead and grip both handles.', 'Extend one leg straight in front of you.', 'Sit back and down on the working leg, going as deep as control allows.']),
 'trx_row': ('https://www.trxtraining.com/blogs/news/resistance-band-back-exercises', 'TRX', '9. Bent-over Row', ['Begin by placing the resistance band under your feet', 'Hold the band handles or ends with an overhand grip, palms facing your body.']),
 'trx_curl_setup': ('https://www.trxtraining.com/blogs/news/bicep-workouts-at-home', 'TRX', 'TRX bicep curls', ['Securely anchor the TRX suspension trainer to a sturdy overhead point or door anchor, ensuring it can support your body weight.', 'Stand facing the anchor point and grasp the TRX handles with an underhand grip (palms facing upward).', 'Lean back slightly, maintaining a straight line from your head to your heels, engaging your core for stability.']),
 'trx_reverse_distinction': ('https://www.trxtraining.com/blogs/news/5-trx-bicep-workouts-you-should-be-doing-daily', 'TRX', 'Reverse Bicep Curl versus Bicep Curl', ['Though the stance and angles for the Reverse Bicep Curl are very similar to the Bicep Curl, the grip is different.', 'stand facing the anchor point with your palms facing down']),
 'trx_deadlift': ('https://www.trxtraining.com/blogs/news/resistance-band-deadlifts', 'TRX', 'Step-by-Step Instructions — main band deadlift, not variation subsection', ['Lay the band flat on the ground. Stand in the middle with feet hip-width apart, keeping both feet securely on the band.', 'Bend down and grab both ends of the band.', 'Push your hips back, bending your knees slightly.']),
 'rogue_trap_position': ('https://www.roguefitness.com/theindex/movement-library/barbell-vs-trap-bar-deadlift-which-is-better', 'Rogue Fitness', 'Trap bar deadlift', ['Stand inside the diamond-shaped frame with the weight balanced at mid-foot']),
 'rogue_trap_grip': ('https://www.roguefitness.com/rogue-tb-1-trap-bar-2-0', 'Rogue Fitness', 'TB-1 Trap Bar 2.0 — manufacturer construction, not an equipment photo', ['The Trap Bar’s hexagonal design and knurled, neutral grip handles']),
 'trx_front_anchor': ('https://www.trxtraining.com/blogs/news/shoulder-exercises-with-bands', 'TRX', '5. Front Raise — foot anchor ONLY; use catalog pronated grip', ["Step on the band's middle to create tension."]),
 'crossfit_front': ('https://www.crossfit.com/essentials/the-front-squat', 'CrossFit', 'Main front squat setup; crossed arms is separately labeled modification', ['The athlete then drives the elbows forward of the bar and sets the bar across the shoulders at the throat, above the clavicles.', 'As long as the athlete can have one finger in contact with the bar, they should be able to establish a proper rack position.']),
 'trx_negative': ('https://www.trxtraining.com/blogs/news/bicep-workouts-at-home', 'TRX', 'Negative Pull-ups — not negative supinated chin-ups', ['Start at the top position with your chin above the bar, then slowly lower yourself down in a controlled manner.']),
 'rogue_belt': ('https://www.roguefitness.com/rogue-dip-belt', 'Rogue Fitness', 'Dip belt for weighted pull-ups: compatible load fastening', ['Whether you’re performing dips, pull-ups, or the hip belt squat', 'the 1/4” wide steel chain-link system and D-shaped carabiners', 'a pair of straight-gate, locking carabiners.']),
 'crossfit_dip': ('https://www.crossfit.com/essentials/the-ring-dip', 'CrossFit', 'Ring dip is a pressing exercise', ['The movement requires upper-body strength, stability, and control while bringing the shoulders through full extension.', 'Practicing the ring dip will develop upper-body pressing strength']),
}

INVESTIGATIONS = {
 'chest-dip-weighted-machine': [('https://www.roguefitness.com/rogue-dip-belt', 'Підтверджує спосіб обтяження для dips, але не визначає single straight bar чи parallel bars прив’язаного 3313.')],
 'drag-curl-barbell': [('https://www.strengthlog.com/drag-curl/', 'Доступ відхилено HTTP CONNECT 403; не читано й не використано як доказ.'), ('https://www.trxtraining.com/search?q=drag+curl&type=article', 'Пошук виробника не дав конкретного drag curl instruction; generic curls не прийняті.')],
 'feet-up-bench-press-barbell': [],
 'hammer-curl-band-resistance-band': [('https://www.trxtraining.com/blogs/news/bicep-workouts-at-home', 'Hammer subsection використовує DUMBBELLS; band subsection — regular supinated curl. Немає exact neutral-band anchor, не об’єднано їх здогадкою.'), ('https://www.trxtraining.com/blogs/news/resistance-band-arm-workout', 'Seated supinated curl/other arm drills, не точний standing neutral hammer band curl.')],
 'hip-thrust-barbell': [('https://www.strengthlog.com/barbell-hip-thrust/', 'Доступ відхилено HTTP CONNECT 403; не використано як доказ.')],
 'landmine-180-barbell': [('https://www.trxtraining.com/blogs/news/front-delt-exercises', 'Одноручний half-kneeling shoulder PRESS, не landmine rotational 180; не визначає його кінцеві точки.')],
 'lying-neck-extension-weighted-plate': [('https://www.nsca.com', 'Недоступно HTTP 403; немає прочитаної exact weighted lying neck extension інструкції.')],
 'nordic-hamstrings-curls': [('https://www.roguefitness.com/rogue-nordic-hamstring-curl-strap', 'HTTP 404; не існуючий доказ конструкції.'), ('https://www.crossfit.com/essentials/the-nordic-curl', 'HTTP 200, але лише шаблон сайту без статті: soft missing page, не доказ.'), ('https://www.strengthlog.com/nordic-hamstring-eccentric/', 'Доступ відхилено CONNECT 403; не використано.')],
 'pushup-weighted': [('https://www.roguefitness.com/rogue-plate-carrier', 'Підтверджує закріплені vest plates у carrier, але не сумісність довільного круглого млинця на верхній спині. Не підмінено raw load carrier/vest без рішення користувача.')],
 'side-bend-dumbbell': [('https://www.strengthlog.com/dumbbell-side-bend/', 'Доступ відхилено CONNECT 403; dataset повторює суперечність, нових доказів немає.')],
 'single-arm-landmine-press-barbell': [('https://www.trxtraining.com/blogs/news/front-delt-exercises', 'Виробник описує One-Arm KNEELING Landmine Press. Це інші опори, ніж standing split stance цього ID; не підмінено.'), ('https://www.roguefitness.com/theindex/movement-library', 'Немає конкретної інструкції exact standing/back-supported варіанта у прочитаних матеріалах.')],
 'single-leg-standing-calf-raise-barbell': [('https://www.trxtraining.com/blogs/news/single-balance-leg-exercises', 'Одноногі drills з bodyweight/TRX/YBell не підтверджують barbell upper-back plus handhold setup цього ID.')],
}

STYLE_SOURCES = {
 'burpee-broad-jumps': ['content.es.instructions[0]', 'content.es.instructions[1]', 'content.es.instructions[2]', 'match.rationale'],
 'dumbbell-snatch': ['match.rationale', 'source.dataset_id', 'content.es.instructions[0]', 'content.es.instructions[5]'],
 'farmers-walk': ['match.rationale', 'source.dataset_id', 'content.es.instructions[0]'],
 'thruster-kettlebell': ['content.es.instructions[0]', 'content.es.instructions[3]', 'content.es.instructions[4]'],
 'burpee-over-the-bar': ['content.en.description', 'content.en.instructions[2]'],
 'handstand-hold': ['content.en.instructions[1]', 'content.en.safety_note'],
 'climbing': ['content.en.instructions[0]', 'content.en.safety_note'],
}

def load(path):
    return json.loads((ROOT/path).read_text())

def save(path, value):
    p=ROOT/path; p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n')

def configure():
    previous.configure()
    # Every old batch including changed generation copies 010–015 stays reserved.
    # Only this round's byte-identical ready files may be recognized as own work.
    base.BATCH_PATHS=NEW_BATCHES

def snapshot():
    s=old.snapshot()
    path=ROOT/s['reference_path']
    s['local_reference_sha256']=base.sha(path.read_bytes()) if path.is_file() else None
    return s

def available(eid,s):
    e=s['by_id'][eid]
    if e['archived']:return 'archived'
    if s['classifications'][eid]!='other':return 'deferred_or_ambiguous_equipment'
    if eid in s['png_sources']:return 'PNG_exists_in_fetched_Git'
    if eid in s['reserved']:return 'already_assigned_in_existing_batch_or_manifest'
    if eid in s['touched']:return 'existing_attempt_or_review_retained_in_previous_assignment'
    return 'available'

def protected():
    paths=[f'data/batches/agent-03-others-{n:03}.json' for n in range(1,16)]
    paths += [base.CATALOG_PATH,base.PROGRESS_PATH,'docs/exercise-image-style.md',INPUT,old.REPORT_PATH,old.HANDOFF_PATH]
    return {p:base.sha((ROOT/p).read_bytes()) for p in paths}

def build_evidence(s,ids):
    cat=s['catalog'];mr=(SOURCE_DIR/'working-manifest.json').read_bytes();dr=(SOURCE_DIR/'dataset.json').read_bytes()
    assert base.sha(mr)==cat['source']['manifest_sha256']
    manifest=json.loads(mr);dataset=json.loads(dr)
    assert manifest['dataset_commit']==cat['source']['dataset_commit']
    mc=collections.Counter(e['lightweight_id'] for e in manifest['exercises']);dc=collections.Counter(str(e['id']) for e in dataset)
    mb={e['lightweight_id']:e for e in manifest['exercises']};db={str(e['id']):e for e in dataset}
    rows=[]
    for eid in ids:
        assert mc[eid]==1
        e=s['by_id'][eid];m=mb[eid]
        for key in ['name','equipment','primary_muscle','secondary_muscles','archived','content','match','source']:assert m[key]==e[key],(eid,key)
        did=e['source']['dataset_id'];original=None;binding=None
        if did is not None:
            assert dc[did]==1
            d=db[did]; candidates=[v for v in m['candidates'] if str(v['id'])==did]
            assert len(candidates)==1
            for key in ['id','name','equipment','instructions','instruction_steps']:assert candidates[0][key]==d[key],(eid,did,key)
            original={key:copy.deepcopy(d[key]) for key in ['id','name','equipment','instructions','instruction_steps','attribution']}
            # Full multilingual original retained only as same explicit source ID;
            # no candidate was selected by similarity or position.
            binding={'catalog_exercise_id':eid,'catalog_source_dataset_id':did,'manifest_selected_source_id':m['source']['dataset_id'],
                     'original_ID_occurrences':dc[did],'selected_candidate_ID_occurrences':len(candidates),
                     'dataset_record_sha256':base.value_sha(d),'manifest_candidate_fields_exact':True}
        rows.append({'exercise_id':eid,'catalog_record_sha256':base.value_sha(e),'manifest_record_sha256':base.value_sha(m),
                     'catalog_and_manifest_fields_exact':True,'dataset_binding':binding,'original_dataset_record':original,
                     'unmatched_dataset_policy':'source.dataset_id=null means NO selected original. Similar candidates never substitute this record.' if did is None else None})
    web=[]
    for key,(url,publisher,section,quotes) in WEB.items():
        cache=WEB_DIR/(hashlib.sha256(url.encode()).hexdigest()[:12]+'.json');r=json.loads(cache.read_text())
        assert r['http_status']==200 and all(q in r['text'] for q in quotes),(key,url)
        web.append({'source_id':key,'publisher':publisher,'url':url,'final_url':r['final_url'],'section':section,
                    'http_status':200,'retrieved_at':datetime.datetime.now(ZoneInfo('Europe/Kiev')).isoformat(),
                    'html_sha256':r['sha256'],'extracted_text_sha256':base.sha(r['text'].encode()),'quotes':quotes,
                    'quote_sha256':[base.sha(q.encode()) for q in quotes],
                    'scope':'Only the recorded exact-variant technical component; never replace catalogue ID, name, source English, equipment flags or muscle lists.'})
    attempts=[]
    for eid,investigations in INVESTIGATIONS.items():
        for url,reason in investigations:
            p=WEB_DIR/(hashlib.sha256(url.encode()).hexdigest()[:12]+'.json')
            cache=json.loads(p.read_text()) if p.exists() else next((x for x in json.loads(pathlib.Path('/tmp/agent03-primary-access.json').read_text()) if x['url']==url),{})
            attempts.append({'exercise_id':eid,'url':url,'http_status':cache.get('http_status'),'access_error':cache.get('error'),
                             'used_as_resolution':False,'reason_not_sufficient':reason})
    return {'schema_version':1,'catalog_sha256':s['catalog_sha256'],'source_release_url':cat['source']['release_url'],
            'manifest_path_in_archive':cat['source']['manifest_path_in_archive'],'manifest_sha256':base.sha(mr),
            'manifest_expected_sha256':cat['source']['manifest_sha256'],'manifest_hash_verified':True,
            'dataset_path_in_archive':'exercise-catalog-v1/dataset.json','dataset_sha256':base.sha(dr),'dataset_commit':manifest['dataset_commit'],
            'acquisition':'HTTP byte ranges and ZIP CRC on exactly working-manifest.json and dataset.json. No source photographs acquired.',
            'whole_archive_sha256_verified':False,'whole_archive_expected_sha256':cat['source']['archive_sha256'],
            'archive_limit':'Whole media archive was not downloaded/hashed; no claim to have verified its whole-file checksum.',
            'records':rows,'primary_publications':web,'unresolved_investigations':attempts,
            'network_limit':'Some primary hosts reachable (TRX/CrossFit/Rogue); others returned 403. Soft missing pages and unrelated variants are NOT evidence.'}

def proofs(eid,fields,s):
    return old.evidence(eid,fields,s)

def decision(eid,s,evidence):
    reason,fields,dsfields,webkeys=DECISIONS[eid]
    record=next(x for x in evidence['records'] if x['exercise_id']==eid)
    orig=record['original_dataset_record']
    return {'exercise_id':eid,'rationale_uk':reason,'catalog_evidence':proofs(eid,fields,s),
            'original_dataset_evidence':[{'exercise_id':eid,'source_dataset_id':s['by_id'][eid]['source']['dataset_id'],
                'field':field,'value':copy.deepcopy(old.field_value(orig,field)),
                'release_url':evidence['source_release_url'],'dataset_file_sha256':evidence['dataset_sha256'],
                'binding':record['dataset_binding']} for field in dsfields],
            'primary_publications':[copy.deepcopy(next(p for p in evidence['primary_publications'] if p['source_id']==key)) for key in webkeys],
            'source_English_policy':'Quoted unchanged for provenance. Render the explicitly resolved scene and documented variant, not the disputed generic/erroneous fields; do not edit catalogue.'}

def scene(eid,values,camera):
    phase,pose,grip,supports,trajectory=values
    return {'exercise_id':eid,'single_phase':phase,'pose':pose,'grip':grip,'supports_and_equipment':supports,'movement_trajectory':trajectory,'camera':camera,
            'one_phase_only':True,'never_infer_muscles_from_pose_or_reference':True}

def reference(s):
    return old.reference(s)

def style_proposal(s,own_ids,foreign_ids):
    all_ids=own_ids+foreign_ids
    lines=['# Доповнення v1: нейтральне тіло для узагальненого primary', '',
           f'Пропонована версія: `{STYLE_VERSION}`. **awaiting_style_decision, НЕ затверджено.**', '',
           'Пропозиція: коли primary_muscle дорівнює full_body, cardio або other, залишати анатомічне тіло нейтральним непрозорим сріблясто-сірим. Не фарбувати все тіло й не виводити основну м’язову групу з руху, назви чи зовнішнього джерела.', '',
           'Підсвічувати лише конкретні secondary_muscles, прямо записані для цього exact ID, тим самим #F26445 на 40–50% інтенсивності. Порожній secondary список → жодної підсвітки. Це інтенсивність кольору, не прозорість тканин.', '',
           'Зовнішність, матеріали, чорні шорти, один манекен/одна фаза, квадратний PNG і прозорий фон успадковано від v1. Чинний docs/exercise-image-style.md не змінено. Правило не додає обладнання й не вирішує суперечностей техніки.', '',
           '**55 власних + 5 попередніх чужих = 60 ID.** Лише kettlebell-high-pull має secondary=[traps]; для нього легша підсвітка трапецій. У всіх інших 59 secondary=[]: повністю нейтральне тіло.', '',
           'Власні conditional prompts: `'+STYLE_DRAFTS+'`. Дозвіл на генерацію не надано. 45 записів мають конкретний повний prompt, 10 потребують ще визначення руху/варіанта або сумісності взуття; для них збережено template без вигаданих сцен.', '',
           'Одне спільне питання: **затвердити це доповнення нейтрального primary й підсвітки лише явно зазначених secondary?** До рішення всі 55 власних записи awaiting_style_decision.', '',
           'Окреме спільне питання footwear для hiking/walking/snowboarding: дозволити сумісне взуття/кріплення й захист, чи погодити окрему barefoot ілюстрацію/тренувальний варіант? Сама пропозиція кольорів НЕ змінює barefoot v1.', '',
           'Для HIIT, Pilates, Stretching і Yoga також потрібен один конкретний рух/поза; для Clean/Press Under — receiving варіант; Muscle Up має суперечливий поворот хвата. Ці питання не замінено рішенням стилю.', '',
           '## Єдиний список застосовності (точні ID)', '',
           'Позначка foreign означає вже зарезервований чужий запис: лише включений до групового рішення, без нового prompt/пакета/результату.', '', '| exercise_id | Власність |', '| --- | --- |']
    lines += [f'| `{eid}` | '+('foreign: night-2026-10-01-clarifications' if eid in foreign_ids else 'agent-03')+' |' for eid in all_ids]
    lines += ['', 'Після рішення спочатку перевірити актуальні PNG/призначення; лише technical_status=ready допускає окреме формування нових пакетів. Власний style draft не є запуском або схваленням зображення.', '']
    return '\n'.join(lines)

def task(eid,s,values,camera,resolution=None,proposal_hash=None):
    row=base.fields_for_id(eid,s);draft=proposal_hash is not None;extra=STYLE_EXTRA.get(eid) if draft else None
    st=copy.deepcopy(base.STYLE)
    st['no_invention']='Exact catalogue ID controls identity, raw equipment and muscles. Only the embedded verified same-ID/source-variant decisions may clarify rendering technique. No guessed weights, brands, attachments or muscle targets.'
    if draft:
        st['version']=STYLE_VERSION;st['base_version']='v1';st['approval_status']='awaiting_style_decision'
        st['primary_highlight']={'hex':None,'rule':'full_body/cardio/other are broad labels, NOT anatomical targets. Entire body neutral opaque silver-gray except explicitly listed concrete secondary targets.'}
    selected=scene(eid,values,camera) if values else None
    supplementary=proofs(eid,STYLE_SOURCES.get(eid,[]),s) if draft else []
    payload={'identity_do_not_render_as_text':{'exercise_id':eid,'name':row['name'],'catalog_sha256':s['catalog_sha256'],'catalog_record_sha256':row['source_catalog_record_sha256']},
             'exact_catalogue_source':{key:copy.deepcopy(row[key]) for key in ['source_english','equipment','primary_muscle','secondary_muscles']},
             'human_reference':reference(s),'style':st,'base_style_sha256':s['style_sha256'],'style_proposal_sha256':proposal_hash,
             'selected_render_scene':selected,'technique_resolution':resolution,'same_ID_supplementary_fields':supplementary,
             'technical_blocker':{'group':extra[0],'question_uk':extra[1]} if extra else None,
             'source_use_rule':'Render ONLY selected_render_scene and the explicit exact-ID resolution; original English stays verbatim for provenance even when a disputed field is overridden. Do not invent a substitute exercise or copy reference pose/equipment/muscle colors.'}
    prefix='CONDITIONAL PROMPT — STYLE PROPOSAL NOT APPROVED. Do not execute before user style decision.\n' if draft else 'Create exactly ONE square transparent PNG of the exact exercise and selected single phase. Metadata fields must never appear as text.\n'
    prefix+='Do not render multiple phases, raw disputed alternatives, or inferred muscle targets.\n'
    prompt=prefix+json.dumps(payload,ensure_ascii=False,sort_keys=True,indent=2)
    row.update(status='awaiting_style_decision' if draft else 'ready',technical_status='needs_clarification' if extra else 'ready',
               prompt_prepared=extra is None,prompt_status='blocked_missing_technique_or_footwear' if extra else 'complete',
               prompt_template=prompt if extra else None,generation_prompt=None if extra else prompt,
               prompt_payload=payload,prompt_sha256=base.sha(prompt.encode()),scene=selected,technique_resolution=resolution,
               same_ID_supplementary_fields=supplementary,style_version=STYLE_VERSION if draft else 'v1',
               base_style_version='v1',base_style_sha256=s['style_sha256'],style_proposal_path=STYLE_DOC if draft else None,
               style_proposal_sha256=proposal_hash,human_reference=reference(s),
               attempts=0,result_path=None,result_sha256=None,user_review=None,technical_check=None,
               agent_visual_review='not_performed',generation_authorized_now=False,technical_question=extra[1] if extra else None)
    return row

def make_batches(s,evidence,timestamp):
    batches=[];ids=list(DECISIONS)
    for i,start in enumerate(range(0,len(ids),10)):
        bid=list(NEW_BATCHES)[i];rows=[]
        for eid in ids[start:start+10]:
            row=task(eid,s,READY_SCENES[eid],CAMERA[eid],decision(eid,s,evidence))
            row.update(batch_id=bid,planned_png_path=f'/workspace/exercise-image-results/{bid}/{eid}/attempt-1.png',
                       planned_output_relative_path=f'{bid}/{eid}/attempt-1.png')
            rows.append(row)
        batches.append({'schema_version':1,'batch_id':bid,'owner_agent':'agent-03','branch':base.BRANCH,'status':'ready','prepared_at':timestamp,
                        'catalog_path':base.CATALOG_PATH,'catalog_sha256':s['catalog_sha256'],'catalog_source_commit':s['commits']['origin/work'],
                        'style_version':'v1','style_path':'docs/exercise-image-style.md','style_sha256':s['style_sha256'],'human_reference':reference(s),
                        'exercise_count':len(rows),'exercise_ids':[r['exercise_id'] for r in rows],'exercises':rows,
                        'generation_authorized_now':False,'source_evidence_path':EVIDENCE,
                        'constraints':{'old_batches_001_015_immutable':True,'no_generation':True,'no_pixel_QA':True,'no_Supabase':True,
                                       'catalog_and_shared_progress_immutable':True,'fresh_assignment_and_PNG_metadata_check_before_any_future_call':True}})
    return batches

def make_style_drafts(s,evidence,own_ids,foreign_ids,proposal_hash,timestamp):
    rows=[]
    for eid in own_ids:
        row=task(eid,s,STYLE_SCENES.get(eid),'Front-side three-quarter view showing complete person, prescribed grip and all supports/contacts within square; no crop.',proposal_hash=proposal_hash)
        row.update(assignment_kind='own_conditional_style_draft_NOT_ready_generation_batch',batch_id=None,
                   planned_png_path=f'/workspace/exercise-image-results/agent-03-neutral-primary-style-drafts/{eid}/attempt-1.png',
                   planned_output_relative_path=f'agent-03-neutral-primary-style-drafts/{eid}/attempt-1.png',
                   output_path_policy='Planned draft staging path; after approval and assignment, retain exact ID or explicitly rebind path in new batch/manifest. Never assign before live duplicate check.')
        rows.append(row)
    foreign=[dict(base.fields_for_id(eid,s),status='awaiting_style_decision',assignment_disposition='foreign_reference_only_do_not_reassign',
                  original_assignment_path='data/batches/night-2026-10-01-clarifications.json',reservation_sources=s['reserved'].get(eid,[]),
                  prompt_prepared=False,generation_prompt=None,planned_png_path=None) for eid in foreign_ids]
    return {'schema_version':1,'kind':'conditional_style_drafts_not_generation_batch','owner_agent':'agent-03','branch':base.BRANCH,
            'status':'awaiting_style_decision','prepared_at':timestamp,'catalog_sha256':s['catalog_sha256'],'catalog_source_commit':s['commits']['origin/work'],
            'style_version':STYLE_VERSION,'base_style_version':'v1','base_style_sha256':s['style_sha256'],'style_proposal_path':STYLE_DOC,
            'style_proposal_sha256':proposal_hash,'exercise_count':len(rows),'complete_prompt_count':sum(r['prompt_prepared'] for r in rows),
            'incomplete_template_count':sum(not r['prompt_prepared'] for r in rows),'exercise_ids':own_ids,'exercises':rows,
            'style_applicability_ids':own_ids+foreign_ids,'foreign_reference_only':foreign,'generation_authorized_now':False,
            'additional_question_groups':[{'group_id':group,'exercise_ids':[eid for eid in own_ids if eid in STYLE_EXTRA and STYLE_EXTRA[eid][0]==group]} for group in dict.fromkeys(v[0] for v in STYLE_EXTRA.values())],
            'source_evidence_path':EVIDENCE}

def make_review(s,evidence,own_ids,style_ids,foreign_ids,batches,timestamp):
    original=load(INPUT);oldrows={r['exercise_id']:r for r in original['blocked']};rows=[]
    for eid in own_ids:
        row=base.fields_for_id(eid,s);row.update(original_question=oldrows[eid]['question'],original_question_group=oldrows[eid]['question_group'],
                    reservation_check=available(eid,s),source_record_evidence=copy.deepcopy(next(r for r in evidence['records'] if r['exercise_id']==eid)))
        if eid in DECISIONS:
            row.update(status='ready',decision=decision(eid,s,evidence),batch_path=next(NEW_BATCHES[b['batch_id']] for b in batches if eid in b['exercise_ids']),question=None)
        elif eid in style_ids:
            row.update(status='awaiting_style_decision',style_drafts_path=STYLE_DRAFTS,question=None,
                       additional_question=STYLE_EXTRA[eid][1] if eid in STYLE_EXTRA else None)
        else:
            group,question,options,fields=QUESTIONS[eid]
            row.update(status='blocked',question_group=group,question=question,options=options,catalog_evidence=proofs(eid,fields,s),
                       external_investigations=[x for x in evidence['unresolved_investigations'] if x['exercise_id']==eid])
        rows.append(row)
    return {'schema_version':1,'owner_agent':'agent-03','branch':base.BRANCH,'prepared_at':timestamp,'audited_commits':s['commits'],
            'catalog_sha256':s['catalog_sha256'],'input_question_path':INPUT,'input_question_sha256':base.sha((ROOT/INPUT).read_bytes()),
            'input_own_count':89,'technical_input_count':34,'style_input_count':55,'technical_ready_count':len(DECISIONS),
            'technical_blocked_count':len(QUESTIONS),'awaiting_style_decision_count':len(style_ids),'foreign_style_reference_only_count':len(foreign_ids),
            'style_applicability_ids':style_ids+foreign_ids,'exercises':rows,'source_evidence_path':EVIDENCE,
            'limits':['Only fetched Git trees/committed assignment metadata. Unpushed files of other cloud tasks may be inaccessible.',
                      'No generation, no result-image pixel/dimension/hash QA, no Supabase audit or API calls.',
                      'An unsuccessful no-PNG call remains in its previous batch; no old attempts or approvals reset.']}

def validate(s,q,batches,drafts,review,evidence,frozen,proposal_text):
    errors=[];seen=set();original=load(INPUT);inputs={r['exercise_id']:r for r in original['blocked']}
    if s.get('local_reference_sha256')!=s['reference_sha256']:errors.append('local_human_reference_unavailable_or_hash_mismatch')
    catalog_counts=collections.Counter(r['id'] for r in s['catalog']['exercises'])
    if len(catalog_counts)!=451 or any(v!=1 for v in catalog_counts.values()):errors.append('catalog_IDs_not_unique_451')
    ev={r['exercise_id']:r for r in evidence['records']};pub={r['source_id']:r for r in evidence['primary_publications']}
    if not evidence['manifest_hash_verified'] or evidence['manifest_sha256']!=s['catalog']['source']['manifest_sha256']:errors.append('source_manifest_not_verified')
    for p in pub.values():
        if p['http_status']!=200 or [base.sha(t.encode()) for t in p['quotes']]!=p['quote_sha256']:errors.append('publication_quote_integrity:'+p['source_id'])
    ph=base.sha(proposal_text.encode())
    ownstyle={eid for eid,r in inputs.items() if r['question_group']=='style_mapping'}
    expected_ready=set(DECISIONS);expected_blocked=set(QUESTIONS)
    if expected_ready|expected_blocked|ownstyle!=set(inputs) or (expected_ready&expected_blocked):errors.append('input_partition_wrong')
    for row in review['exercises']:
        eid=row['exercise_id']
        if row['reservation_check']!='available' or available(eid,s)!='available':errors.append('live_PNG_assignment_attempt_conflict:'+eid)
        for key,value in base.fields_for_id(eid,s).items():
            if row.get(key)!=value:errors.append('review_catalog_field_mismatch:'+eid+':'+key)
        if ev[eid]['catalog_record_sha256']!=base.value_sha(s['by_id'][eid]):errors.append('evidence_catalog_ID_mismatch:'+eid)
        bound=ev[eid]['dataset_binding'];did=s['by_id'][eid]['source']['dataset_id']
        if did is not None and (bound['catalog_exercise_id']!=eid or bound['catalog_source_dataset_id']!=did or ev[eid]['original_dataset_record']['id']!=did or not bound['manifest_candidate_fields_exact']):errors.append('explicit_original_dataset_binding_wrong:'+eid)
        if did is None and ev[eid]['original_dataset_record'] is not None:errors.append('generated_record_borrowed_dataset:'+eid)
    def check_row(row,bid,style=False):
        eid=row['exercise_id']
        if eid in seen:errors.append('duplicate_new_ID:'+eid)
        seen.add(eid)
        if catalog_counts[eid]!=1:return errors.append('unknown_or_duplicate_ID:'+eid)
        if eid not in inputs:errors.append('ID_not_in_own89:'+eid)
        if available(eid,s)!='available':errors.append('PNG_assignment_overlap:'+eid)
        for key,value in base.fields_for_id(eid,s).items():
            if row.get(key)!=value:errors.append('exact_catalog_field_mismatch:'+eid+':'+key)
        # Reconstruct using pinned preparation commit, not a moving work ref.
        pinned=dict(s);pinned['commits']=dict(s['commits']);pinned['commits']['origin/work']=drafts['catalog_source_commit'] if style else bid['catalog_source_commit']
        exp=task(eid,pinned,STYLE_SCENES.get(eid) if style else READY_SCENES[eid],
                 'Front-side three-quarter view showing complete person, prescribed grip and all supports/contacts within square; no crop.' if style else CAMERA[eid],
                 None if style else decision(eid,pinned,evidence),ph if style else None)
        for key in exp:
            if row.get(key)!=exp[key]:errors.append('exact_prompt_source_scene_binding:'+eid+':'+key)
        group='agent-03-neutral-primary-style-drafts' if style else bid['batch_id']
        if row['planned_png_path']!=f'/workspace/exercise-image-results/{group}/{eid}/attempt-1.png' or row['planned_output_relative_path']!=f'{group}/{eid}/attempt-1.png':errors.append('planned_PNG_ID_wrong:'+eid)
        prompt=row['generation_prompt'] or row['prompt_template']
        if base.sha(prompt.encode())!=row['prompt_sha256'] or json.loads(prompt[prompt.index('{'):])!=row['prompt_payload']:errors.append('prompt_string_mismatch:'+eid)
        if row['attempts']!=0 or row['generation_authorized_now'] or any(row[k] is not None for k in ['result_path','result_sha256','user_review','technical_check']):errors.append('false_generation_claim:'+eid)
        if row['human_reference']['sha256']!=s['reference_sha256']:errors.append('human_reference_changed:'+eid)
        if style:
            if eid not in ownstyle or row['status']!='awaiting_style_decision' or row['style_version']!=STYLE_VERSION:errors.append('style_draft_made_ready:'+eid)
            st=row['prompt_payload']['style']
            if st['primary_highlight']['hex'] is not None or st['approval_status']!='awaiting_style_decision':errors.append('broad_primary_colored_or_approved:'+eid)
            if eid in STYLE_EXTRA and (row['generation_prompt'] is not None or row['scene'] is not None):errors.append('unresolved_style_technique_invented:'+eid)
    for batch in batches:
        if batch['status']!='ready' or not 1<=batch['exercise_count']<=10 or batch['exercise_count']!=len(batch['exercises']):errors.append('batch_size_status:'+batch['batch_id'])
        if batch['exercise_ids']!=[r['exercise_id'] for r in batch['exercises']]:errors.append('batch_ID_order:'+batch['batch_id'])
        if batch['catalog_sha256']!=s['catalog_sha256'] or batch['style_sha256']!=s['style_sha256'] or batch['style_version']!='v1':errors.append('batch_catalog_style_changed:'+batch['batch_id'])
        for row in batch['exercises']:check_row(row,batch)
    readyseen=seen.copy()
    if readyseen!=expected_ready:errors.append('ready_decision_set_wrong')
    for row in drafts['exercises']:check_row(row,None,True)
    if set(drafts['exercise_ids'])!=ownstyle or len(drafts['exercises'])!=55 or drafts['style_proposal_sha256']!=ph:errors.append('style_proposal_own_set_hash_wrong')
    foreign=[r['exercise_id'] for r in original['previously_reserved'] if r['question_group']=='style_mapping']
    if drafts['style_applicability_ids']!=drafts['exercise_ids']+foreign or len(set(drafts['style_applicability_ids']))!=60:errors.append('60_ID_style_list_wrong')
    if [r['exercise_id'] for r in drafts['foreign_reference_only']]!=foreign or any(r['generation_prompt'] is not None or r['planned_png_path'] is not None for r in drafts['foreign_reference_only']):errors.append('foreign_ID_reassigned')
    if set(review['style_applicability_ids'])!=set(drafts['style_applicability_ids']):errors.append('review_style_group_wrong')
    rows={r['exercise_id']:r for r in review['exercises']}
    if len(rows)!=89 or {eid for eid,r in rows.items() if r['status']=='ready'}!=expected_ready or {eid for eid,r in rows.items() if r['status']=='blocked'}!=expected_blocked:errors.append('89_review_partition_wrong')
    for eid in expected_blocked:
        if rows[eid]['question']!=QUESTIONS[eid][1] or len(rows[eid]['options'])<2:errors.append('concrete_blocked_question_missing:'+eid)
    for eid in expected_ready:
        d=rows[eid]['decision']
        for proof in d['catalog_evidence']:
            if proof['exercise_id']!=eid or proof['value']!=old.field_value(s['by_id'][eid],proof['field']) or proof['catalog_record_sha256']!=base.value_sha(s['by_id'][eid]):errors.append('decision_proof_ID_field_mismatch:'+eid)
        for proof in d['original_dataset_evidence']:
            if proof['exercise_id']!=eid or proof['source_dataset_id']!=s['by_id'][eid]['source']['dataset_id'] or proof['value']!=old.field_value(ev[eid]['original_dataset_record'],proof['field']):errors.append('decision_dataset_proof_mismatch:'+eid)
    latest=q['blocked_preparation']
    if latest['new_ready_ids']!=[eid for b in batches for eid in b['exercise_ids']] or latest['technical_blocked_ids']!=list(QUESTIONS):errors.append('queue_latest_ready_blocked_wrong')
    if q['prepared_count']!=143+len(expected_ready) or q['remaining_unprepared_ids']:errors.append('queue_historical_prepared_count_wrong')
    if q['awaiting_style_decision_count']!=55 or set(q['awaiting_style_decision_ids'])!=ownstyle:errors.append('queue_style_count_wrong')
    qrows={r['exercise_id']:r for r in q['exercises']}
    if len(qrows)!=len(q['exercises']) or set(qrows)!=set(q['eligible_exercise_ids']):errors.append('queue_historical_rows_or_ID_uniqueness_wrong')
    for eid in expected_ready:
        for key,value in base.fields_for_id(eid,s).items():
            if key!='source_english' and qrows[eid].get(key)!=value:errors.append('queue_catalog_field_mismatch:'+eid+':'+key)
        expected_bid=next(b['batch_id'] for b in batches if eid in b['exercise_ids'])
        if qrows[eid].get('batch_id')!=expected_bid or qrows[eid].get('prompt_prepared') is not True:errors.append('queue_batch_binding_wrong:'+eid)
    if latest['old_assigned_ids_001_015']!=[eid for n in range(1,16) for eid in load(f'data/batches/agent-03-others-{n:03}.json')['exercise_ids']]:errors.append('old_assignments_not_retained')
    for path,h in frozen.items():
        if base.sha((ROOT/path).read_bytes())!=h:errors.append('protected_file_changed:'+path)
    return {'schema_version':1,'status':'failed' if errors else 'passed','errors':errors,'checked_at':datetime.datetime.now(ZoneInfo('Europe/Kiev')).isoformat(),
            'audited_commits':s['commits'],'catalog_sha256':s['catalog_sha256'],'style_sha256':s['style_sha256'],
            'input_own89':89,'technical_ready_count':len(readyseen),'technical_blocked_count':len(expected_blocked),
            'awaiting_style_decision_count':55,'complete_conditional_prompt_count':drafts['complete_prompt_count'],
            'incomplete_conditional_template_count':drafts['incomplete_template_count'],'all_style_applicability_count':60,
            'new_batches':[{'batch_id':b['batch_id'],'status':b['status'],'count':b['exercise_count'],'path':NEW_BATCHES[b['batch_id']]} for b in batches],
            'protected_sha256':frozen,'source_files':s['source_files'],'limits':review['limits'],
            'checks':['451_unique_catalog_IDs','exact_name_full_English_equipment_muscles_by_ID','explicit_source_dataset_ID_join_no_similarity','local_reference_matches_Git_SHA256',
                      'original_manifest_SHA256_and_candidate_binding','primary_publication_quote_hashes','full_prompt_scene_ID_path_hash_binding',
                      'no_PNG_existing_assignment_or_attempt_overlap','old_001_015_immutable_including_failed_noPNG','one_style_group_60_IDs_5_foreign_readonly',
                      'no_broad_primary_coloring','awaiting_style_never_ready_or_generated','true_ambiguities_have_concrete_options']}

def negative_checks(s,q,batches,drafts,review,evidence,frozen,text):
    cases={
        'wrong_exact_name':lambda b,d:b[0]['exercises'][0].update(name='WRONG ID NAME'),
        'source_English_from_other_ID':lambda b,d:b[0]['exercises'][0].update(source_english=b[0]['exercises'][1]['source_english']),
        'invented_muscles':lambda b,d:b[0]['exercises'][0].update(primary_muscle='full_body'),
        'invented_equipment':lambda b,d:b[0]['exercises'][0].update(equipment='cable'),
        'duplicate_between_packages':lambda b,d:b[1]['exercises'].__setitem__(0,copy.deepcopy(b[0]['exercises'][0])),
        'old_assigned_ID_010':lambda b,d:b[0]['exercises'][0].update(exercise_id='low-row-suspension'),
        'wrong_PNG_ID':lambda b,d:b[0]['exercises'][0].update(planned_png_path='/workspace/exercise-image-results/wrong.png'),
        'style_draft_made_ready':lambda b,d:d['exercises'][0].update(status='ready'),
        'whole_body_primary_color':lambda b,d:d['exercises'][0]['prompt_payload']['style']['primary_highlight'].update(hex='#F26445'),
        'foreign_style_ID_reassigned':lambda b,d:d['foreign_reference_only'][0].update(generation_prompt='GENERATE'),
    }
    outcomes={}
    for label,change in cases.items():
        bb=copy.deepcopy(batches);dd=copy.deepcopy(drafts);change(bb,dd)
        try:result=validate(s,q,bb,dd,review,evidence,frozen,text);rejected=bool(result['errors'])
        except (KeyError,TypeError,ValueError):rejected=True
        if not rejected:raise ValueError('Guard accepted corruption:'+label)
        outcomes[label]=True
    return outcomes

def handoff(s,q,batches,drafts,review,report):
    lines=['# Agent-03: опрацювання 89 blocked записів', '',
           'Власна гілка `'+base.BRANCH+'`; підготовка без генерації. Дата '+review['prepared_at']+'.', '',
           'Актуальний work snapshot `'+s['commits']['origin/work']+'`. Каталог SHA256 `'+s['catalog_sha256']+'`. Чинний стиль v1 SHA256 `'+s['style_sha256']+'`.', '',
           '**22 ready** із 34 технічних; **12 blocked** із конкретними варіантами. **55 awaiting_style_decision**; із них 45 повних conditional prompts і 10 templates без вигадування відсутнього руху/спорядження. Ні approved, ні generation/attempt не додано.', '',
           '## Нові ready пакети', '', '| Пакет | Статус | Кількість | Точний файл |', '| --- | --- | ---: | --- |']
    lines += [f'| {b["batch_id"]} | ready | {b["exercise_count"]} | `{NEW_BATCHES[b["batch_id"]]}` |' for b in batches]
    lines += [f'| Власні style drafts (не generation пакет) | awaiting_style_decision | 55 | `{STYLE_DRAFTS}` |',
              f'| Технічні питання (не generation пакет) | blocked | 12 | `{RESEARCH}` |', '',
              'Пакети 001–015 незмінні; 010–015 вже передані генератору. Їхні 143 ID збережено зарезервованими, включно з failed/noPNG продовженням 009. Нові файли не скидають жодної попередньої спроби. Live PNG перевірено лише за Git paths і manifests/призначеннями; повторного технічного/візуального аудиту зображень не було.', '',
              '## Самодостатність і джерела', '',
              'Кожен ready запис містить exact exercise_id/name, повний незмінний source_english (description/instructions/form_cues/common_mistakes/safety/provenance), equipment/primary/secondary, catalog/record/English hashes, phase/pose/grip/supports/trajectory/camera, повний prompt і його SHA256, embedded evidence/URL/quotes, style v1/hash, human reference/path/hash та planned PNG path із тим самим ID.', '',
              'Еталон: `'+str(ROOT/s['reference_path'])+'`; repo path `'+s['reference_path']+'`; SHA256 `'+s['reference_sha256']+'`. Роль лише зовнішність/пропорції/матеріали. Нове вкладення в чаті не використано як техніку/обладнання/підсвітку; його локальних байтів/SHA не надано, тому самодостатній пакет посилається на чинний accepted reference, не вигаданий attachment path.', '',
              'Результати плануються поза Git: `/workspace/exercise-image-results/<batch_id>/<exercise_id>/attempt-1.png`. У style drafts є окремий planned staging path з exact ID; після рішення стилю формувати окремі нові пакети й явно зафіксувати остаточний шлях/manifest перед викликом. Draft не запускати напряму.', '',
              'Original archive прочитано HTTP ranges лише для working-manifest.json і dataset.json. Manifest SHA256 збігається з каталогом; dataset_commit збігається. Selected dataset records приєднані ВИКЛЮЧНО через source.dataset_id exact ID, із звіркою того самого selected candidate у verified manifest. Generated/null-source записи не отримували схожий кандидат. Whole 411MB media archive не завантажено/не хешовано; whole archive hash НЕ позначено перевіреним.', '',
              'Точні джерела, quotes та обмеження: `'+EVIDENCE+'`. Первинні матеріали TRX, CrossFit, Rogue прочитано як текст, без завантаження фото/відео. Не використано коментарі користувачів як інструкції. Не підмінялися half-kneeling landmine, dumbbell hammer curl або vest carrier там, де вони мають інші опори/обладнання.', '',
              'Для вирішених помилок raw English лишається дослівним provenance, а prompt явно надає пріоритет resolved scene та його same-ID/source-variant evidence. Каталог не виправлено. Зокрема Trap Bar має зафіксовану помилку source 0811, але виробник конкретно визначає inside-frame neutral handles; Clap — source 1273 wider hands; Dragonfly — власний pl/match описує shoulder-supported abdominals, а не generic chest fly.', '',
              '## Нерозв’язані технічні питання', '']
    for eid,(group,question,options,fields) in QUESTIONS.items():lines.append('- `'+eid+'`: '+question)
    lines += ['', '## Стиль — окреме рішення', '',
              'Пропозиція `'+STYLE_DOC+'` з одним списком усіх **60 ID** (55 власних + 5 чужих): broad primary нейтральний; лише explicit concrete secondary на 40–50% #F26445. Тільки kettlebell-high-pull має traps, решта 59 secondary пусті. Стиль НЕ затверджено, чинний style документ не змінено.', '',
              'Foreign IDs лише у груповому списку: downward-dog, bear-crawl, jumping-jack, high-knees, mountain-climber. Чужі prompts/пакети/результати не змінено й їх не перепризначено.', '',
              'Окремі additional questions для 10 власних style IDs (рішення кольору їх не усуває):', '']
    for eid,(group,question) in STYLE_EXTRA.items():lines.append('- `'+eid+'`: '+question)
    lines += ['', '## Перевірка та наступна передача', '',
              'Валідатор `'+REPORT+'`: '+str(len(report['negative_guard_cases']))+' навмисних підмін відхилено; exact-ID поля/source binding, prompt/hash/path, відсутність старих/чужих/PNG перетинів і незмінність protected файлів перевірено. Queue історичні prepared/eligible містять старі 143 ID; нові actionable ready IDs — queue.blocked_preparation.new_ready_ids; awaiting_style_decision_ids не є ready.', '',
              '```bash',
              "git fetch origin '+refs/heads/work:refs/remotes/origin/work' '+refs/heads/agent-02-machines-001:refs/remotes/origin/agent-02-machines-001' '+refs/heads/agent-04-supabase-integration:refs/remotes/origin/agent-04-supabase-integration'",
              'python scripts/prepare_agent03_blocked_records.py --check', '```', '',
              'Додаткові agent-гілки fetch перед check; --prepare не повторювати. Старі checker scripts є історичними й не перевіряють новий формат queue. Якщо з’явився PNG/нове призначення, НЕ запускати відповідний ID. Непушені файли інших cloud задач можуть бути недоступні; це межа перевірки.', '',
              'Для майбутнього окремо дозволеного запуску журнал має зв’язувати batch_id, exact exercise_id, catalog/record/prompt/reference/style hashes, фактичний виклик/attempt та PNG path/SHA. Не зіставляти отримані файли за назвами/позицією. Hash provenance не є візуальним QA.', '',
              'work/shared progress/каталог/style v1/Supabase/схвалення не змінені. Генерація не виконувалася. Пропозицію доступу до первинних доменів збережено через cloud-environment-onboarding:setup як draft; saving не означає застосування runtime-політики. Частина додаткових першоджерел усе ще повертає 403; це не дозвіл підбирати альтернативу навмання.', '']
    return '\n'.join(lines)

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--prepare',action='store_true');parser.add_argument('--check',action='store_true');args=parser.parse_args()
    if args.prepare==args.check:parser.error('Choose --prepare or --check')
    if base.git('branch','--show-current').decode().strip()!=base.BRANCH:raise ValueError('Wrong branch')
    configure();s=snapshot();q=load(base.QUEUE_PATH);original=load(INPUT)
    if args.prepare:
        for path in [*NEW_BATCHES.values(),RESEARCH,EVIDENCE,STYLE_DRAFTS,STYLE_DOC,HANDOFF,REPORT]:
            if (ROOT/path).exists():raise ValueError('New artifact already exists: '+path)
        if q['prepared_count']!=143:raise ValueError('Unexpected input queue')
        own_ids=[r['exercise_id'] for r in original['blocked']];style_ids=[r['exercise_id'] for r in original['blocked'] if r['question_group']=='style_mapping']
        foreign_ids=[r['exercise_id'] for r in original['previously_reserved'] if r['question_group']=='style_mapping']
        assert len(own_ids)==89 and len(style_ids)==55 and len(foreign_ids)==5
        if any(available(eid,s)!='available' for eid in own_ids):raise ValueError('New PNG/assignment conflict; exclude and review before saving')
        frozen=protected();timestamp=datetime.datetime.now(ZoneInfo('Europe/Kiev')).isoformat()
        evidence=build_evidence(s,own_ids);text=style_proposal(s,style_ids,foreign_ids);ph=base.sha(text.encode())
        batches=make_batches(s,evidence,timestamp);drafts=make_style_drafts(s,evidence,style_ids,foreign_ids,ph,timestamp)
        review=make_review(s,evidence,own_ids,style_ids,foreign_ids,batches,timestamp)
        ready_ids=[eid for b in batches for eid in b['exercise_ids']]
        for b in batches:
            for taskrow in b['exercises']:
                row={k:copy.deepcopy(v) for k,v in base.fields_for_id(taskrow['exercise_id'],s).items() if k!='source_english'}
                row.update(batch_id=b['batch_id'],status='ready',prompt_prepared=True,preparation_status='prompt_prepared_not_generated',
                           source_resolution_path=RESEARCH,priority_tier=5,queue_order=len(q['exercises'])+1)
                q['exercises'].append(row)
        q['eligible_exercise_ids']+=ready_ids;q['eligible_count']=len(q['eligible_exercise_ids']);q['prepared_count']=len(q['eligible_exercise_ids'])
        q['batch_paths']+=[NEW_BATCHES[b['batch_id']] for b in batches];q['latest_launch_ids']=ready_ids
        q['excluded']=[r for r in q['excluded'] if r['exercise_id'] not in ready_ids]
        for row in q['excluded']:
            if row['exercise_id'] in style_ids:row['reason_code']='awaiting_style_decision';row['style_proposal_path']=STYLE_DOC
        q['exclusion_counts_disjoint']=dict(collections.Counter(r['reason_code'] for r in q['excluded']))
        q.update(updated_at=timestamp,awaiting_style_decision_count=55,awaiting_style_decision_ids=style_ids,style_drafts_path=STYLE_DRAFTS,
                 blocked_clarification_count=len(QUESTIONS),blocked_clarification_path=RESEARCH,last_live_check={'status':'passed','checked_at':timestamp,'audited_commits':s['commits']})
        old_ids=[eid for n in range(1,16) for eid in load(f'data/batches/agent-03-others-{n:03}.json')['exercise_ids']]
        q['blocked_preparation']={'status':'ready_technical_tasks_prepared_style_proposal_pending','prepared_at':timestamp,'audited_commits':s['commits'],
                  'input_own89_ids':own_ids,'new_ready_ids':ready_ids,'new_ready_count':len(ready_ids),'new_batch_paths':[NEW_BATCHES[b['batch_id']] for b in batches],
                  'technical_blocked_ids':list(QUESTIONS),'technical_blocked_count':len(QUESTIONS),'awaiting_style_decision_ids':style_ids,
                  'style_applicability_ids':style_ids+foreign_ids,'style_proposal_path':STYLE_DOC,'research_path':RESEARCH,
                  'old_assigned_ids_001_015':old_ids,'generation_authorized_now':False,
                  'package_registry':[{'batch_id':b['batch_id'],'status':'ready','count':b['exercise_count'],'path':NEW_BATCHES[b['batch_id']]} for b in batches]+[
                      {'kind':'style_drafts_not_generation_batch','status':'awaiting_style_decision','count':55,'path':STYLE_DRAFTS},
                      {'kind':'technical_clarifications_not_generation_batch','status':'blocked','count':len(QUESTIONS),'path':RESEARCH}]}
        q['preparation_rounds'].append({'round':5,'prepared_at':timestamp,'audited_commits':s['commits'],'exercise_ids':ready_ids,
                                      'batch_paths':q['blocked_preparation']['new_batch_paths'],'status':'ready_preparation_only','style_drafts_path':STYLE_DRAFTS})
        report=validate(s,q,batches,drafts,review,evidence,frozen,text);report['negative_guard_cases']=negative_checks(s,q,batches,drafts,review,evidence,frozen,text)
        if report['errors']:raise ValueError(json.dumps(report['errors']))
        for b in batches:save(NEW_BATCHES[b['batch_id']],b)
        save(base.QUEUE_PATH,q);save(EVIDENCE,evidence);save(RESEARCH,review);save(STYLE_DRAFTS,drafts);save(REPORT,report)
        (ROOT/STYLE_DOC).write_text(text);(ROOT/HANDOFF).write_text(handoff(s,q,batches,drafts,review,report))
        save(old.BLOCKED_PATH,{'schema_version':1,'kind':'unresolved_queue_not_generation_batch','owner_agent':'agent-03','status':'blocked_or_awaiting_style_decision',
                             'exercise_count':len(QUESTIONS)+55,'technical_blocked_count':len(QUESTIONS),'awaiting_style_decision_count':55,
                             'exercise_ids':[r['exercise_id'] for r in review['exercises'] if r['status']!='ready'],
                             'exercises':[r for r in review['exercises'] if r['status']!='ready'],'research_path':RESEARCH,'style_proposal_path':STYLE_DOC,'generation_authorized_now':False})
        assert frozen==protected()
    else:
        review=load(RESEARCH);drafts=load(STYLE_DRAFTS);evidence=load(EVIDENCE);saved=load(REPORT);text=(ROOT/STYLE_DOC).read_text()
        batches=[load(path) for path in q['blocked_preparation']['new_batch_paths']]
        report=validate(s,q,batches,drafts,review,evidence,saved['protected_sha256'],text)
        report['negative_guard_cases']=negative_checks(s,q,batches,drafts,review,evidence,saved['protected_sha256'],text)
    print(json.dumps({k:report[k] for k in ['status','audited_commits','technical_ready_count','technical_blocked_count','awaiting_style_decision_count',
                                          'complete_conditional_prompt_count','incomplete_conditional_template_count','new_batches','negative_guard_cases','errors']},ensure_ascii=False,indent=2))
    if report['errors']:sys.exit(1)

if __name__=='__main__':main()
