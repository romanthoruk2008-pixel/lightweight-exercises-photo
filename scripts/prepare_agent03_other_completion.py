#!/usr/bin/env python3
"""Finish the other queue and record evidence-backed clarification decisions.

--prepare writes only new own batches, own queue/review/validation and handoff.
--check reads fresh fetched Git snapshots. No generation, pixel QA or Supabase.
"""
import argparse
import collections
import copy
import datetime
import json
import pathlib
import re
import sys
from zoneinfo import ZoneInfo

import prepare_agent03_other_queue as base
import prepare_agent03_other_round3 as previous

ROOT = base.ROOT
OLD_PATHS = [f'data/batches/agent-03-others-{n:03}.json' for n in range(1, 10)]
NEW_IDS = [f'agent-03-others-{n:03}' for n in range(10, 16)]
NEW_PATHS = {bid: f'data/batches/{bid}.json' for bid in NEW_IDS}
BLOCKED_ID = 'agent-03-other-blocked'
BLOCKED_PATH = 'data/queues/agent-03-other-blocked.json'
REVIEW_PATH = 'data/queues/agent-03-other-clarifications-review.json'
REPORT_PATH = 'data/queues/agent-03-other-completion-validation.json'
HANDOFF_PATH = 'docs/agent-03-other-completion-handoff.md'

# phase, pose, actual grip, actual supports, camera. Every key is an exact ID.
# No numerical angles, grip directions, attachments or loads are added unless
# the corresponding record or a cited same-ID source specifies them.
SCENES = {
 'low-row-suspension': ('Chest drawn toward handles', 'Lean back with body in one straight line, trunk braced; elbows travel back as chest approaches handles, hips do not sag.', 'Both hands firmly grip the suspension handles; no grip rotation or spacing is prescribed.', 'Both feet grounded; secured suspension straps carry the hand load, shoulders away from ears.', 'Side three-quarter view showing the straight body, feet, handles and complete secure suspension setup.'),
 'pullup-band-resistance-band': ('Chin above bar with band assistance', 'Arms bend to pull chest upward, chin clears bar, core engaged and shoulders down; no swing.', 'Palms face away, hands slightly wider than shoulders.', 'Hands on fixed pull-up bar; feet stand on the assisting band attached to that same bar, clear of floor. No knee-in-band substitution.', 'Rear three-quarter view showing back, hand-bar contacts and the complete band-to-feet path.'),
 'pullup-machine': ('Controlled chin-clearing top', 'Chest approaches fixed bar, elbows bend, chin clears bar as specified in description; trunk braced and still.', 'Both hands grip bar with palms facing away; no numeric width is prescribed.', 'Hands on secure fixed bar, full body hanging clear of floor; no cable, stack or seated machine.', 'Rear three-quarter view showing lat targets, fixed bar and complete figure.'),
 'ring-pushup': ('Chest lowered between low rings', 'Straight high-plank body with feet wide; chest lowers between rings and elbows angle back, no hip sag.', 'Each hand grips one ring in the source neutral position.', 'Low rings just above floor on secured straps, feet on floor; hands stay inside rings, not on ground.', 'Front-side three-quarter view showing ring grips, low ring height and both foot contacts.'),
 'scapular-pull-ups': ('Scapular depression endpoint', 'Elbows stay STRAIGHT while shoulder blades move down and slightly together, lifting body only by scapular movement.', 'Both hands on pull-up bar, palms facing away.', 'Secure overhead bar supports hands; body hangs without foot contact or kip.', 'Rear three-quarter view exposing shoulder blades, straight elbows and whole bar support.'),
 'squat-suspension': ('Controlled balance-assisted squat depth', 'Hips sit back and both knees bend, chest lifted and trunk braced; comfortable depth, no hard pull or rowing.', 'Both hands hold suspension handles with light strap tension; no special hand rotation is specified.', 'Feet shoulder-width, heels grounded, suspension securely anchored and used for balance only.', 'Front-side three-quarter view showing heels, knees, handles and complete strap/anchor setup.'),
 'sternum-pullup-gironda-machine': ('Upper chest approaching high bar', 'Torso leans back while sternum leads toward bar, elbows travel down and back toward ribs; no chin-only pull or kip.', 'Overhand grip, hands slightly wider than shoulders.', 'Hands on secure high fixed bar, body hanging clear of floor; no weighted machine attachments.', 'Side-rear three-quarter view showing sternum-bar relation, backward torso lean and full body.'),
 'toes-to-bar': ('Toes contacting bar between hands', 'Arms stay straight, legs together and straight; abdomen raises legs until toes contact bar, with controlled pelvis and no swing.', 'Overhand grip on secure pull-up bar.', 'Hands and toes contact the same fixed overhead bar at this endpoint; no floor support.', 'Side three-quarter view exposing straight elbows, straight legs and toe contact between the hands.'),
 'triceps-dip-machine': ('Controlled parallel-bar dip lower phase', 'Torso slightly forward, shoulders down, elbows bent until upper arms approach parallel; legs quiet and clear of floor.', 'One hand firmly grips each parallel bar, wrists straight, elbows point back.', 'Static parallel bars support hands. No seat, stack, assisted platform or bench-edge substitution.', 'Front-side three-quarter view showing both hand contacts, elbows and full stable bars.'),
 'triceps-dip-weighted-machine': ('Weighted dip lower phase', 'Torso slightly forward and shoulders stable; elbows bend to controlled upper-arm near-parallel depth, legs still.', 'One hand on each parallel bar, secure grip.', 'Stable parallel bars and a conservative centered WEIGHTED VEST, an explicit belt-or-vest source option. No invented load number or dangling plate.', 'Front-side three-quarter view showing vest, both hands and complete parallel supports.'),
 'triceps-extension-suspension': ('Forehead endpoint of elbow flexion', 'Face AWAY from overhead-anchored straps, lean forward with straight body; upper arms fixed, elbows bend so handles approach forehead. Choose the source forehead option.', 'Both hands grip suspension handles with palms facing down, wrists neutral.', 'Both feet on floor, secured overhead straps support hands; no bench or invented back pad.', 'Side three-quarter view showing forward body line, feet, forehead-handle clearance and anchor.'),
 'wide-pullup-machine': ('Chin at bar height', 'Pull elbows down and out until chin reaches bar, neck quiet and shoulders active; no behind-neck path.', 'Overhand grip wider than shoulder width.', 'Hands on fixed pull-up bar; body hangs clear of floor, no machine stack or cable.', 'Rear three-quarter view showing wide grip, back and full fixed bar.'),
 'box-squat-barbell-hevy-3338464331414239': ('Braced pause lightly touching box', 'Hips and knees bent, hips lightly contact box without rocking, trunk braced, heels planted and knees tracking toes.', 'Both hands secure one free barbell across upper back; no special width is specified.', 'Feet on floor, stable box behind hips lightly contacted at pause. No guided rails, invented box height or bounce.', 'Side three-quarter view showing bar, heel contacts and actual hip-box contact.'),
 'gorilla-row-kettlebell': ('Right kettlebell row with left arm long', 'Wide hip hinge, long spine; right kettlebell drawn toward right ribs while left arm stays long, hips do not twist.', 'One kettlebell handle firmly gripped in each hand, elbows pull close.', 'Both feet in wide grounded stance; no bench, barbell or floor-supported arm.', 'Rear-side three-quarter view showing both bells, right row and long left arm.'),
 'kettlebell-around-the-world': ('Controlled handoff behind waist', 'Stand tall, feet shoulder-width and planted, torso upright; single bell passes close around waist between hands behind back.', 'Hands transfer the SAME single kettlebell securely by its handle, fingers clear; no second bell.', 'Both feet on floor; no anchor, bench or overhead circling substitute.', 'Rear three-quarter view exposing the behind-waist handoff and full figure.'),
 'kettlebell-curl': ('Single-bell curl toward shoulder', 'Stand hip-width, trunk braced, working upper arm beside torso and still; elbow curls the single bell toward shoulder without swing.', 'One hand grips kettlebell with palm facing forward; wrist stays aligned.', 'Both feet grounded; free hand carries no second weight or support.', 'Front three-quarter view showing palm direction, fixed upper arm and bell.'),
 'kettlebell-goblet-squat': ('Controlled bottom with bell at chest', 'Feet shoulder-width, hips and knees bent until thighs parallel or comfortable source depth; chest up and trunk controlled.', 'Both hands firmly hold ONE kettlebell close to chest; no unsupported exact grip variant is prescribed.', 'Both feet planted, heels down; no bench, machine or second bell.', 'Front three-quarter view showing chest-held bell, knees and both heels.'),
 'kettlebell-shoulder-press': ('Two-bell overhead endpoint', 'Stand shoulder-width, trunk braced; arms extend overhead with controlled shoulders and no back arch.', 'One kettlebell per hand, palms facing forward as source states.', 'Both feet grounded; no bench, barbell or single-bell substitution.', 'Front three-quarter view including full arms, both bells and both feet.'),
 'landmine-row-barbell': ('Free end pulled toward lower ribs', 'Stand over loaded free end in hip-width stance, neutral hip hinge; torso and hips steady as elbows pull back.', 'Both hands grasp the free SLEEVE, choosing the explicit sleeve-or-handle source option; add no V-handle.', 'Opposite bar end fixed in secure landmine base, feet grounded; free load clears feet.', 'Side-rear three-quarter view showing secure anchor, free sleeve grips and full bar path.'),
 'lateral-box-jump': ('Quiet two-foot landing on box', 'Face forward while landing sideways onto stable box with both feet, hips and knees flexed and knees aligned.', 'Hands free, used naturally for balance; no held load.', 'Both feet on top of low stable box at landing; no hopping off, invented height or forward-jump substitution.', 'Front-side three-quarter view showing lateral relationship to box, both landing feet and full figure.'),
 'lying-neck-curls-weighted-plate': ('Small controlled neck-flexion nod', 'Supine body supported, shoulders relaxed; chin nods slightly toward chest in a small controlled range, no shoulder lift.', 'BOTH hands securely support a LIGHT plate centered on forehead without pressing it into head.', 'Back and head have a stable lying support; depict small supported range, no invented bench-edge overhang or extra weight.', 'Side three-quarter view showing forehead plate, both hand contacts and relaxed shoulders.'),
 'meadows-rows-barbell': ('One-arm sleeve row toward lower ribs', 'Stand BESIDE free end in staggered stance, neutral hip hinge; nearer working arm draws sleeve toward lower ribs without torso rotation.', 'Nearer hand firmly grasps the FREE barbell sleeve; no added handle.', 'Other end securely anchored in landmine base, feet staggered on floor, free end clear of knees/feet.', 'Side-rear three-quarter view exposing the nearer hand, staggered feet and full anchored bar.'),
 'overhead-plate-raise': ('Plate above shoulders', 'Stand stable, ribs over pelvis and abdomen braced; plate raised overhead without backward lean, elbows soft.', 'Both hands securely grip the SAME light plate.', 'Both feet grounded; no bench, machine or lowering behind head.', 'Front-side three-quarter view including both hands, complete plate and full body.'),
 'plate-curl': ('Centered underhand plate curl', 'Stand tall with elbows close to ribs and upper arms still; plate curls toward chest without leaning back.', 'Both hands hold plate by EDGES with palms facing UP, exactly as source states.', 'Both feet grounded, single plate only; no barbell or palms-down substitution.', 'Front three-quarter view exposing both palms-up edge grips and elbow flexion.'),
 'plate-front-raise': ('Plate at shoulder height in front', 'Stand stable, trunk braced, elbows softly bent; single plate held forward at shoulder height, shoulders down.', 'Secure two-handed grip on plate, no unsupported numerical hand spacing.', 'Both feet grounded; no overhead endpoint, machine or swing.', 'Front-side three-quarter view showing forward plate height, hands and full body.'),
 'plate-press': ('Nearly extended horizontal squeeze press', 'Stand tall with ribs over hips; arms press single plate straight FORWARD from chest until elbows nearly extend.', 'Palms squeeze plate BETWEEN them continuously, maintaining palm pressure; no loose rim-only carry.', 'Both feet grounded; no bench, overhead press or second plate.', 'Front-side three-quarter view showing palm-pressure contacts and horizontal press path.'),
 'preacher-curl-barbell': ('Supported bar curl toward shoulders', 'Sit on preacher bench, chest against support and upper arms resting on pad; elbows curl bar while upper arms remain still.', 'Underhand grip on free barbell, slightly wider than shoulder width.', 'Seat, chest support and upper-arm pad of static preacher bench; no cable, stack or curl machine.', 'Front-side three-quarter view showing pad contacts, underhand grip and whole bench.'),
 'preacher-curl-dumbbell': ('Two supported dumbbell curls at contraction', 'Sit at preacher bench with upper arms supported; both elbows curl weights toward shoulders without lifting elbows.', 'One dumbbell per hand, palms UP.', 'Static preacher bench and upper-arm pad, no guided resistance or machine stack.', 'Front three-quarter view showing both weights and supported upper arms.'),
 'rack-pull-barbell': ('Braced setup at knee-height rack', 'Stand shoulder-width with toes slightly outward; hinge and bend knees with neutral back, braced before lift.', 'Overhand grip, hands shoulder-width on free barbell.', 'Bar rests on stationary rack at KNEE HEIGHT, both feet on floor; no floor deadlift or Smith rails.', 'Side three-quarter view showing knee-height rack supports, hands and complete free bar.'),
 'russian-twist-weighted-plate': ('Controlled right-side trunk rotation', 'Sit on floor, knees bent and feet FLAT; lean back slightly with straight back and braced core, ribcage rotates right, pelvis balanced.', 'Both hands firmly hold ONE plate, the exact equipment enum, moving toward floor on right side. No medicine-ball substitution.', 'Seated pelvis and both feet contact floor; no elevated feet or momentum.', 'Front three-quarter view showing seated contacts and right-side plate position.'),
 'single-leg-standing-calf-raise-dumbbell': ('One-leg heel-rise on step with handhold', 'Only working forefoot supports load at step edge, heel raised vertically; other leg clear and not pushing, ankle aligned.', 'One hand holds ONE dumbbell; other hand contacts the source-permitted railing for balance.', 'Stable step supports working forefoot; secure railing supports free hand. Whole step/handhold visible, no machine or invented height.', 'Side three-quarter view showing heel clearance, one supporting foot, dumbbell and railing hand.'),
 'sissy-squat-weighted': ('Shallow backward-leaning knee-flexion phase', 'Feet hip-width on balls with heels lifted, torso and hips aligned leaning back; knees travel forward, hips stay extended.', 'Both hands secure one LIGHT plate against chest; do not replace with barbell despite equipment=none.', 'Balls of both feet on floor; stable support nearby for source safety, no invented contact that prevents holding plate.', 'Side three-quarter view exposing lifted heels, forward knees, extended hips and chest-held plate.'),
 'situp-weighted': ('Controlled rise with plate against sternum', 'From supine bent knees, torso curls toward knees into comfortable upright phase, neck controlled.', 'Both hands keep one LIGHT plate against chest/sternum, never overhead.', 'Feet flat and pelvis on floor; no decline bench or foot restraints absent from source.', 'Side-front three-quarter view showing plate contact, bent knees and planted feet.'),
 'step-up': ('Right-leg drive onto box', 'Entire RIGHT foot on stable box, torso leaning slightly over that leg; rise through right foot as trailing leg follows without hard push-off.', 'Hands carry no load; source is an unloaded step-up.', 'Whole right sole on box, trailing foot leaves floor during ascent; no invented box height.', 'Front-side three-quarter view showing right sole, box and rising trailing leg.'),
 'sumo-squat-kettlebell': ('Wide controlled squat with horn-held bell', 'Feet wider than shoulders, toes slightly out, heels down; pelvis lowers between thighs, chest lifted and knees follow toes.', 'Both hands hold ONE kettlebell by HORNS at chest, exactly as source specifies.', 'Both feet grounded; no between-leg deadlift load, machine or second bell.', 'Front three-quarter view showing horns grip, chest-held bell and wide stance.'),
 'walking-lunge-sandbag': ('Right forward-step lower phase', 'Right foot forward with heel down, both knees bend, torso tall; bag remains centered and still.', 'Both arms hold SAME sandbag firmly against chest.', 'Both feet in forward lunge contact during this phase, clear walking lane; no invented load number or barbell.', 'Front-side three-quarter view showing bag-to-chest contact and right forward leg.'),
 'wrist-roller-machine': ('Controlled mid-wind of hanging load', 'Stand with arms at shoulder height and elbows softly unlocked; shoulders quiet, bar level as wrists alternate turns.', 'Both hands firmly grip wrist-roller BAR; motion at wrists, not a shoulder lift.', 'One light suspended weight is raised by cord winding onto standard compatible wrist-roller bar; weight remains clear of feet. Manual roller, no cable station or stack.', 'Front-side three-quarter view showing both hands, bar, winding cord and full suspended weight.'),
}

# Decisions add exact same-ID textual evidence; source English remains intact.
# Each item: reason for resolution, field paths carrying the missing answer.
RESOLUTIONS = {
 'around-the-world-dumbbell': ('Дві гантелі, долоні вниз, початок із прямих рук убік на рівні плечей задано в es/ru; English описує передню й надголовну частини того ж кола.', ['content.es.instructions[0]', 'content.es.instructions[1]', 'content.es.instructions[2]']),
 'bench-press-close-grip-barbell': ('В es прямо задано хват трохи вужче плечей і лікті біля тулуба; це конкретизує загальний English grip.', ['content.es.instructions[1]', 'content.es.instructions[2]', 'content.uk.instructions[0]']),
 'bench-press-wide-grip-barbell': ('В es прямо задано хват трохи ширше плечей; English не задає протилежної ширини.', ['content.es.instructions[1]', 'content.es.instructions[3]']),
 'box-jump': ('Es задає позицію перед тумбою та стрибок угору на неї, ru підтверджує стрибок на тумбу; посадка на тумбу не вигадана.', ['content.es.instructions[0]', 'content.es.instructions[1]', 'content.ru.instructions[1]']),
 'chest-fly-band-resistance-band': ('Es прямо задає стояче положення й анкер позаду на рівні грудей; English chest support є умовним as required, не обов’язковою лавою.', ['content.es.instructions[0]', 'content.es.instructions[2]']),
 'chest-fly-suspension': ('Uk/ru/es задають руки на ременях і нахил тіла вперед; умовне English chest supported as required не задає обов’язкового грудного паду.', ['content.uk.instructions[0]', 'content.ru.instructions[0]', 'content.es.instructions[0]']),
 'crunch-weighted': ('Es/ru прямо задають plate or dumbbell на грудях; обрано дозволений plate, English не забороняє навантаження.', ['content.es.instructions[1]', 'content.ru.instructions[1]']),
 'decline-chest-fly-dumbbell': ('Es/ru прямо задають лежачи спиною на decline-лаві, стопи закріплені, долоні одна до одної. Умовний English support не є вимогою лежати грудьми.', ['content.es.instructions[0]', 'content.es.instructions[1]', 'content.uk.instructions[0]']),
 'decline-crunch-weighted': ('Ru прямо задає plate біля грудей на decline-лаві; інші блоки не задають іншого обтяження.', ['content.ru.instructions[0]', 'content.ru.instructions[1]']),
 'dumbbell-squeeze-press': ('Uk прямо задає притиснуті гантелі та постійний тиск між ними на всіх фазах; English звичайний press не містить протилежної вимоги.', ['content.uk.description', 'content.uk.instructions[0]', 'content.uk.instructions[1]', 'content.uk.instructions[3]']),
 'dumbbell-step-up': ('Es/ru прямо задають по гантелі в кожній руці долонями до тулуба та праву стопу на сходинці. English placement beside step — неповна підготовка, не заборона тримати вагу.', ['content.es.instructions[0]', 'content.es.instructions[1]', 'content.ru.instructions[0]']),
 'ez-bar-biceps-curl-barbell': ('Uk прямо задає EZ-штангу зворотним хватом; English barbell є ширшим типом, не вимогою прямого грифа.', ['content.uk.instructions[0]', 'content.en.instructions[0]', 'match.rationale']),
 'frog-jumps': ('Ru задає глибокий початковий присід, es — напрямок угору й уперед; обрано передній варіант, дозволений English upward or forward.', ['content.ru.instructions[0]', 'content.es.instructions[1]', 'content.en.instructions[1]']),
 'full-squat-barbell': ('Es/ru прямо задають гриф на верхній спині й глибину до паралелі або трохи нижче; обрано дозволену опору на трапеції та контрольовану нижню фазу.', ['content.es.instructions[1]', 'content.es.instructions[4]']),
 'glute-bridge-barbell': ('Es/ru прямо задають гриф на стегнах і утримання обома руками; uk уточнює складку стегон. Це відповідає English securely positioned.', ['content.es.instructions[0]', 'content.es.instructions[1]', 'content.uk.instructions[0]']),
 'hex-press-dumbbell': ('Власний match.rationale прямо визначає continuous inward dumbbell squeeze, uk description називає притискання. Це доповнення того самого ID, не запозичення Squeeze Press.', ['match.rationale', 'content.uk.description']),
}

SCENES.update({
 'around-the-world-dumbbell': ('Source-defined arms-out start of circular path', 'Stand shoulder-width, torso still, arms STRAIGHT out to sides at shoulder height before circling forward then overhead.', 'One dumbbell per hand, palms DOWN as same-ID Spanish instructions specify.', 'Both feet grounded; no bench or one-weight waist pass.', 'Front three-quarter view showing both straight arms, palms and complete weights.'),
 'bench-press-close-grip-barbell': ('Close-grip controlled chest approach', 'Lie on flat bench, feet planted, elbows close to torso as free bar approaches chest without bounce.', 'Both hands slightly NARROWER than shoulder width, exactly as cited Spanish source.', 'Flat bench supports back and shoulder blades; stationary rack safeties per English safety alternative, no extra person.', 'Front-side three-quarter view exposing narrow hand spacing, elbows, feet and whole bench.'),
 'bench-press-wide-grip-barbell': ('Wide-grip controlled lower position', 'Lie on flat bench, back supported and feet planted; lower bar toward chest with controlled slightly outward elbows.', 'Both hands slightly WIDER than shoulders as cited Spanish source.', 'Flat bench, grounded feet and stationary rack safeties; no guided rails or spotter figure.', 'Front-side three-quarter view exposing wide grip and controlled chest approach.'),
 'box-jump': ('Soft two-foot landing on top of box', 'Land on box with hips and knees flexed and balanced athletic stance following the same-ID forward/upward box ascent.', 'Hands free, arms used naturally as source cue permits.', 'Both feet on stable box, clear non-slip landing surface; no invented numeric height.', 'Front-side three-quarter view showing front approach relationship, both feet and whole box.'),
 'chest-fly-band-resistance-band': ('Standing chest-level band fly closure', 'Stand tall with soft fixed elbow bend, hands together in front of chest by chest contraction, ribs controlled.', 'Both hands firmly grasp resistance band, no invented attachments or handle brand.', 'Band SECURELY anchored BEHIND at CHEST height per same-ID es text; feet grounded, no bench or pulley.', 'Front-side three-quarter view exposing behind-chest anchor, elastic paths, grips and full figure.'),
 'chest-fly-suspension': ('Forward-inclined suspended fly open phase', 'Body leans forward in stable straight line; arms open within controlled shoulder range, elbows soft and constant, chest/ribs controlled.', 'Both hands on suspension handles as cited same-ID uk/ru source specifies.', 'Grounded feet and securely anchored straps support bodyweight; no invented chest pad or machine.', 'Front-side three-quarter view showing forward lean, soft elbows, foot contacts and whole secure strap setup.'),
 'crunch-weighted': ('Plate-at-chest small crunch top', 'Lie supine, knees bent and feet flat; ribs curl toward pelvis, shoulder blades lift, neck not pulled.', 'Both hands hold one LIGHT PLATE at chest, choosing explicit same-ID plate-or-dumbbell option.', 'Back/pelvis and feet on floor; no full sit-up or unspecified forehead load. Raw equipment=none preserved.', 'Side-front three-quarter view showing small curl and plate-to-chest contact.'),
 'decline-chest-fly-dumbbell': ('Decline-supported comfortable wide arc', 'Lie BACK on declined bench, head lower than hips, arms open in controlled wide arc with soft elbow bend.', 'One dumbbell per hand, palms facing EACH OTHER as cited Spanish source states.', 'Back on declined bench and feet SECURED; no prone chest pad or invented decline angle.', 'Front-side three-quarter view showing decline, foot supports, both grips and full bench.'),
 'decline-crunch-weighted': ('Decline crunch with plate kept near chest', 'Supine on declined bench, ribs curl toward pelvis without neck pull or swinging legs.', 'Both hands secure SAME plate against chest throughout, explicitly stated in cited Russian source.', 'Feet secured on decline bench, lower back/pelvis supported; no invented load number or head-held weight.', 'Side-front three-quarter view showing decline, secured feet and plate contact.'),
 'dumbbell-squeeze-press': ('Continuous-contact press lower phase', 'Lie on flat bench with feet planted; two dumbbells approach chest with controlled elbows and no bounce.', 'One dumbbell per hand, PRESSED AGAINST EACH OTHER with continuous inward pressure, as same-ID uk source explicitly requires.', 'Back and shoulder blades supported on flat bench, feet grounded; compatible stationary safety supports, no second person.', 'Front-side three-quarter view showing continuous dumbbell contact, wrists and full bench.'),
 'dumbbell-step-up': ('Right-foot box ascent carrying both dumbbells', 'Whole RIGHT foot on stable step, body rising by right-leg drive without trailing-leg push; shoulders quiet.', 'One dumbbell in EACH hand with palms toward body as cited same-ID es source states.', 'Full right sole on step, left foot follows from floor; no invented height or floor-resting weights during this phase.', 'Front-side three-quarter view showing right sole, both hanging weights and full step.'),
 'ez-bar-biceps-curl-barbell': ('Controlled supinated EZ curl top', 'Choose source standing option, upper arms still beside torso and elbows close; curl EZ bar toward shoulders without swing.', 'Both hands use source UNDERHAND grip on standard compatible bent EZ bar; no invented exact bends or numerical width.', 'Both feet grounded, no preacher pad or straight-bar substitution.', 'Front three-quarter view exposing bent EZ bar, underhand grip and fixed upper arms.'),
 'frog-jumps': ('Deep controlled crouch before forward/upward jump', 'Begin in DEEP bodyweight squat as cited Russian source states, hips/knees flexed and feet stable, ready for the upward-and-forward option cited in Spanish.', 'Hands free, use arms naturally for balance; no external load.', 'Both feet on clear non-slip floor in this pre-takeoff phase; no box or weighted variant.', 'Side-front three-quarter view showing deep crouch, controlled knees and complete grounded figure.'),
 'full-squat-barbell': ('Controlled squat just below parallel', 'Stand approximately shoulder-width with toes slightly out; hips/knees flexed to source parallel-or-slightly-below option, heels planted and trunk braced.', 'Both hands securely hold bar across upper back; choose source TRAPEZIUS support option, no numerical grip width.', 'Free bar rests on upper back and feet stay grounded; no Smith, front-rack substitution or forced excess depth.', 'Side-front three-quarter view showing upper-back bar support, thigh depth and both heels.'),
 'glute-bridge-barbell': ('Hip-extension top with hands steadying bar', 'Lie on back, knees bent and feet flat; hips lift until torso and thighs align, ribs down and no back arch.', 'Both hands HOLD BAR FIRMLY at hip crease as cited Spanish instructions specify.', 'Shoulder/upper back on floor, feet grounded; bar across HIPS per same-ID es/uk. No bench hip thrust or invented pad.', 'Side three-quarter view showing floor supports, bar-hip contact and both holding hands.'),
 'hex-press-dumbbell': ('Continuous inward-squeeze press above chest', 'Lie on flat bench, feet planted and shoulder blades supported, arms press weights above chest with controlled elbows.', 'One dumbbell per hand; continuously squeeze the two weights INWARD TOGETHER as exact-ID match.rationale explicitly defines.', 'Flat bench and grounded feet, compatible safety supports per English source; no invented hexagonal shape, machine or second person.', 'Front-side three-quarter view making inward dumbbell contact and both wrists visible.'),
})

def field_value(record, field):
    value = record
    for token in re.findall(r'[^.\[\]]+', field):
        value = value[int(token)] if isinstance(value, list) else value[token]
    return value

def configure():
    previous.configure()
    base.BATCH_PATHS = {**NEW_PATHS, BLOCKED_ID: BLOCKED_PATH}

def snapshot():
    s=base.snapshot()
    # Batch manifests are read by base.snapshot. Also read the committed approved
    # backup manifest as a reservation source, without opening/auditing PNGs or
    # contacting any upload service.
    path='data/approved-images-manifest.json'
    def walk(value, source, ptr=''):
        if isinstance(value,dict):
            eid=value.get('exercise_id',value.get('id'))
            if eid in s['by_id']:s['reserved'][eid].append(dict(source,json_pointer=ptr))
            for key,child in value.items():
                if key in s['by_id']:s['reserved'][key].append(dict(source,json_pointer=ptr+'/'+base.pointer(key)))
                walk(child,source,ptr+'/'+base.pointer(key))
        elif isinstance(value,list):
            for index,child in enumerate(value):walk(child,source,ptr+'/'+str(index))
    for ref,commit in s['commits'].items():
        if path not in base.git('ls-tree','-r','--name-only',commit).decode().splitlines():continue
        raw=base.git('show',commit+':'+path)
        source={'branch':ref.removeprefix('origin/') if ref!='HEAD' else base.BRANCH,'commit':commit,'path':path,'sha256':base.sha(raw)}
        s['source_files'].append(source);walk(json.loads(raw),source)
    return s

def load(path): return json.loads((ROOT / path).read_text())
def save(path, value): (ROOT / path).write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n')

def evidence(eid, fields, s):
    return [{'exercise_id': eid, 'catalog_path': base.CATALOG_PATH,
             'catalog_sha256': s['catalog_sha256'], 'source_commit': s['commits']['origin/work'],
             'field': field, 'value': copy.deepcopy(field_value(s['by_id'][eid], field)),
             'catalog_record_sha256': base.value_sha(s['by_id'][eid])} for field in fields]

def availability(eid, s, resolved=False):
    reason, details = base.readiness(s['by_id'][eid], s)
    if reason == 'needs_clarification' and resolved and eid in RESOLUTIONS:
        return 'eligible', None
    return reason, details

def freeze():
    paths = OLD_PATHS + [base.CATALOG_PATH, base.PROGRESS_PATH, base.INVENTORY_PATH, base.CLARIFICATIONS_PATH,
                        base.VALIDATION_PATH, base.HANDOFF_PATH, previous.REPORT_PATH, previous.HANDOFF_PATH,
                        'data/queues/agent-03-other-next-validation.json', 'docs/agent-03-other-next-handoff.md',
                        'docs/agent-03-other-clarifications-explained.md']
    return {p: base.sha((ROOT / p).read_bytes()) for p in paths}

QUESTION_GROUPS = {
 'muscle_style_mapping': ('style_mapping', 'Яке спільне правило v1 застосувати до full_body/cardio/other: погоджена локальна підсвітка чи окрема політика? Не фарбувати все тіло й не обирати м’язи самостійно.'),
 'movement_unspecified': ('movement_path', 'Уточніть траєкторію та характерну фазу для цих ID.'),
 'support_unspecified': ('supports', 'Уточніть точні опори, точки контакту та положення тіла.'),
 'conflicting_supports': ('supports', 'Які опори/контакти правильні там, де вихідні поля суперечать одне одному?'),
 'variant_missing': ('variant_grip_path', 'Уточніть відмінний хват, контакти або траєкторію варіанта; джерела не дають єдиного рішення.'),
 'anchor_unspecified': ('anchors', 'Уточніть анкер/контакт стрічки або фіксацію щиколоток та конфігурацію опори.'),
 'load_unspecified': ('loads', 'Уточніть тип, місце, спосіб безпечного закріплення обтяження або хват front-rack.'),
 'equipment_unspecified': ('equipment_grip', 'Уточніть конструкцію обладнання, положення тіла та хват.'),
 'conflicting_equipment': ('equipment_grip', 'Яке обладнання й конфігурація правильні при суперечливих полях?'),
 'conflicting_movement': ('movement_path', 'Уточніть правильний напрямок/кінці руху або рух, який описує цей ID.'),
 'conflicting_cues': ('cue_scope', 'Уточніть, до яких фаз належать cues/mistakes, що суперечать стрибку.'),
}

PARTIAL = {
 'clap-push-ups': ('Плеск підтверджено es, але English задає hands under or just inside shoulders, а es/ru — трохи ширше. Яка стартова ширина кистей правильна?', ['content.en.instructions[0]', 'content.es.instructions[0]', 'content.es.instructions[3]']),
 'deadlift-trap-bar-barbell': ('Uk задає стояти всередині трап-грифа, es/ru — гриф перед тілом і хват prono/сверху. Уточніть положення відносно рами та напрямок долонь; не обирати текст за здогадкою.', ['content.uk.instructions[0]', 'content.es.instructions[0]', 'content.es.instructions[1]']),
 'deadlift-band-resistance-band': ('It прямо каже band sotto la metà del piede, English — over the mid-foot. Уточніть, чи стрічка зафіксована під стопами та як проходять її кінці.', ['content.it.instructions[0]', 'content.en.instructions[0]']),
 'front-squat-barbell': ('Позицію грифа на передніх плечах/ключицях підтверджено es/uk, але тип хвата не визначено. Який хват рук/ліктів потрібен: clean, перехресний або інший?', ['content.es.instructions[1]', 'content.uk.instructions[0]']),
 'pushup-weighted': ('Plate підтверджено common_mistakes; ще не визначено спосіб закріплення на спині для однієї людини. Як безпечно утримувати млинець без додаткового страхувальника?', ['content.en.common_mistakes[0]', 'content.en.safety_note']),
 'biceps-curl-suspension': ('Опора/анкер/нахил тіла ще не визначені; English підхват, tr долоні вниз. Уточніть анкер, контакти стоп і напрямок долонь.', ['content.en.instructions[0]', 'content.tr.instructions[0]', 'match.rationale']),
}

def review_clarifications(s):
    original = load(base.CLARIFICATIONS_PATH)
    if original['catalog_sha256'] != s['catalog_sha256']: raise ValueError('Clarification catalogue changed')
    resolved, blocked, previous_rows = [], [], []
    for old in original['new_clarifications']:
        eid = old['exercise_id']; row = base.fields_for_id(eid, s)
        for key, value in row.items():
            if old.get(key) != value: raise ValueError('Original clarification/source mismatch: ' + eid + ':' + key)
        row.update(original_reason_kind=old['reason_kind'], original_question=old['reason_and_question_uk'])
        if eid in RESOLUTIONS:
            decision, fields = RESOLUTIONS[eid]
            row.update(status='ready', decision=decision, evidence=evidence(eid, fields, s))
            reason, _ = availability(eid, s, resolved=True)
            if reason != 'eligible':
                row.update(status='blocked', question='Не перепризначати: ' + reason, disposition=reason)
                blocked.append(row)
            else: resolved.append(row)
        else:
            row.update(status='blocked', question=old['reason_and_question_uk'], evidence=[])
            if eid in PARTIAL:
                question, fields = PARTIAL[eid]; row.update(question=question, evidence=evidence(eid, fields, s), partial_answer_only=True)
            row['question_group'] = QUESTION_GROUPS[old['reason_kind']][0]
            if old['reason_kind'] == 'muscle_style_mapping':
                # One policy question per group, not a repeated question per exercise.
                row['question'] = None
                row['question_group'] = 'style_mapping'
                row['technical_readiness_after_style_decision'] = 'must_check_before_preparation'
            blocked.append(row)

    old_path = 'data/batches/night-2026-10-01-clarifications.json'
    old_raw = base.git('show', s['commits']['origin/work'] + ':' + old_path)
    old_by_id = {row['exercise_id']: row for row in json.loads(old_raw)['exercises']}
    assert set(old_by_id) == {row['exercise_id'] for row in original['previous_clarifications_not_reassigned']}
    for eid, old in old_by_id.items():
        row = base.fields_for_id(eid, s)
        if row['source_english'] != old['source_english']: raise ValueError('Previous clarification/source mismatch: ' + eid)
        group = 'style_mapping' if row['primary_muscle'] in ['full_body', 'cardio', 'other'] else (
            'equipment_grip' if eid in ['cross-body-hammer-curl-dumbbell', 'concentration-curl-dumbbell'] else
            'variant_grip_path' if eid in ['diamond-pushup', 'waiter-curl-dumbbell'] else
            'movement_path' if eid in ['bicycle-crunch', 'bicycle-crunch-raised-legs'] else 'supports')
        row.update(status='blocked', assignment_disposition='retained_in_previous_foreign_clarification_file',
                   question=old.get('question_uk'), original_question=old.get('question_uk'), question_group=group,
                   reservation_sources=s['reserved'].get(eid, []),
                   original_source={'branch': 'work', 'commit': s['commits']['origin/work'], 'path': old_path, 'sha256': base.sha(old_raw)}, evidence=[])
        if group == 'style_mapping': row['question'] = None
        if eid == 'diamond-pushup':
            row.update(question=None, source_answer_found=True,
                       decision='Es прямо задає ромб великими/вказівними пальцями; uk задає звичайний жим без плеску. English for clap push-ups є умовою для іншого варіанта. ID вже належить попередньому файлу — нового пакета не створювати.',
                       evidence=evidence(eid, ['content.es.instructions[0]', 'content.uk.instructions[2]', 'content.en.instructions[2]'], s))
        previous_rows.append(row)

    groups = {}
    for row in blocked + previous_rows:
        if row.get('source_answer_found'): continue
        key = row.get('question_group', 'reservation_conflict')
        if key not in groups:
            question = next((value[1] for value in QUESTION_GROUPS.values() if value[0] == key), 'Зберегти попереднє призначення; не дублювати ID.')
            groups[key] = {'group_id': key, 'status': 'blocked', 'question': question, 'exercise_ids': [], 'previously_reserved_ids': []}
        groups[key]['exercise_ids'].append(row['exercise_id'])
        if row in previous_rows: groups[key]['previously_reserved_ids'].append(row['exercise_id'])
    for group in groups.values(): group['exercise_count'] = len(group['exercise_ids'])
    style_ids = groups['style_mapping']['exercise_ids']
    groups['style_mapping']['subgroups_by_original_primary_muscle'] = {
        muscle: [eid for eid in style_ids if s['by_id'][eid]['primary_muscle'] == muscle]
        for muscle in ['full_body', 'cardio', 'other']}
    return {'schema_version': 1, 'owner_agent': 'agent-03', 'branch': base.BRANCH,
            'catalog_sha256': s['catalog_sha256'], 'audited_commits': s['commits'],
            'new_clarifications_reviewed': len(original['new_clarifications']),
            'resolved_ready_count': len(resolved), 'own_blocked_count': len(blocked),
            'previous_clarifications_reviewed': len(previous_rows), 'previously_reserved_not_reassigned_count': len(previous_rows),
            'resolved': resolved, 'blocked': blocked, 'previously_reserved': previous_rows,
            'question_groups': list(groups.values()),
            'decision_rules': ['Only same exact-ID catalogue material may supplement omitted detail.',
                               'Original English copied without changes; supplementary original-language evidence stays separate.',
                               'Conflicting source statements are not repaired by choosing a preferred language.',
                               'Catalogue/muscles/style policy unchanged; one shared style decision for full_body/cardio/other.',
                               'Previous foreign clarification records are not reassigned, even when a textual answer is found.']}

def reference(s):
    path = s['reference_path']
    return {'repository_path': path, 'absolute_path': str(ROOT / path), 'sha256': s['reference_sha256'],
            'branch': 'work', 'source_commit': s['commits']['origin/work'],
            'role': 'Human appearance/proportions/materials/anatomical style ONLY. Exercise pose, grip, equipment and muscles come from the exact-ID catalogue, never the reference.',
            'pixels_reviewed_during_preparation': False}

def payload(eid, s, resolution=None):
    row = base.fields_for_id(eid, s); phase, pose, grip, supports, camera = SCENES[eid]
    src = row['source_english']
    selected = {'single_phase': phase, 'pose': pose, 'grip': grip, 'supports_and_equipment': supports, 'camera': camera,
                'source_instruction_quotes': [{'index': i, 'text': text} for i, text in enumerate(src['instructions'])]}
    result = {'identity_do_not_render_as_text': {'exercise_id': eid, 'name': row['name'],
                'source_catalog_sha256': row['source_catalog_sha256'], 'source_catalog_record_sha256': row['source_catalog_record_sha256']},
              'exact_catalogue_source': {key: row[key] for key in ['source_english', 'equipment', 'primary_muscle', 'secondary_muscles']},
              'human_reference': reference(s), 'style': copy.deepcopy(base.STYLE), 'style_document_sha256': s['style_sha256'],
              'scene': selected, 'supplementary_same_ID_sources': []}
    if resolution:
        result['supplementary_same_ID_sources'] = copy.deepcopy(resolution['evidence'])
        result['source_resolution'] = resolution['decision']
        result['source_use_rule'] = 'Preserve original English. The cited additional fields of THIS SAME exercise ID fill missing detail only; do not substitute another exercise or silently rewrite the source.'
    return result

def make_batch(bid, ids, s, timestamp, resolved_by_id, stage):
    rows = []
    for eid in ids:
        row = base.fields_for_id(eid, s); resolution = resolved_by_id.get(eid)
        p = payload(eid, s, resolution)
        prompt = 'Create exactly ONE square transparent PNG of the exact exercise below, using the referenced human for APPEARANCE ONLY. Render only the selected phase and camera. Identity/path/hash fields are metadata, never visible text.\n' + json.dumps(p, ensure_ascii=False, sort_keys=True, indent=2)
        output = f'/workspace/exercise-image-results/{bid}/{eid}/attempt-1.png'
        row.update(status='ready', preparation_status='prompt_prepared_not_generated', style_version='v1', style_sha256=s['style_sha256'],
                   human_reference=reference(s), scene=copy.deepcopy(p['scene']), prompt_payload=p,
                   generation_prompt=prompt, generation_prompt_sha256=base.sha(prompt.encode()),
                   planned_png_path=output, output_root='/workspace/exercise-image-results',
                   planned_output_relative_path=f'{bid}/{eid}/attempt-1.png', result_path=None, result_sha256=None,
                   attempts=0, user_review=None, technical_check=None, agent_visual_review='not_performed',
                   generation_authorized_now=False,
                   clarification_resolution=copy.deepcopy(resolution) if resolution else None)
        rows.append(row)
    return {'schema_version': 1, 'batch_id': bid, 'owner_agent': 'agent-03', 'branch': base.BRANCH,
            'status': 'ready', 'prepared_at': timestamp, 'preparation_stage': stage, 'generation_authorized_now': False,
            'catalog_path': base.CATALOG_PATH, 'catalog_sha256': s['catalog_sha256'], 'catalog_source_commit': s['commits']['origin/work'],
            'style_version': 'v1', 'style_path': 'docs/exercise-image-style.md', 'style_sha256': s['style_sha256'],
            'human_reference': reference(s), 'queue_path': base.QUEUE_PATH,
            'constraints': {'generation_performed': False, 'shared_progress_changes_allowed': False, 'catalog_changes_allowed': False,
                           'only_builtin_imagegen': True, 'automatic_retries_allowed': False, 'paid_api_allowed': False, 'supabase_allowed': False,
                           'no_agent_visual_QA': True, 'outputs_outside_git': True, 'revalidate_assignments_and_existing_results_before_call': True},
            'exercise_count': len(rows), 'exercise_ids': ids, 'exercises': rows}

def registry(s, batches, blocked):
    records = []
    for path in OLD_PATHS:
        old = load(path); ids = old['exercise_ids']; png_ids = [eid for eid in ids if s['png_sources'].get(eid)]
        remaining = [eid for eid in ids if eid not in png_ids]
        failed = [eid for eid in remaining if s['progress'][eid].get('attempts', 0)]
        records.append({'batch_id': old['batch_id'], 'status': 'blocked' if failed else 'ready', 'exercise_count': len(ids), 'path': path,
                        'newly_prepared': False, 'IDs_with_existing_PNG': png_ids, 'continuation_ids_retained_here': remaining,
                        'failed_without_PNG_ids': failed, 'action': 'continue_original_batch_after_blocker_clears' if remaining else 'do_not_regenerate_existing_results',
                        'progress_observations': {eid: {'status': s['progress'][eid].get('status'), 'attempts': s['progress'][eid].get('attempts'),
                                                      'result_path': s['progress'][eid].get('result_path')} for eid in remaining},
                        'note': 'PNG presence is not user approval. Old batch bytes unchanged; no result PNG audit performed.'})
    records.extend({'batch_id': batch['batch_id'], 'status': 'ready', 'exercise_count': batch['exercise_count'],
                    'path': NEW_PATHS[batch['batch_id']], 'newly_prepared': True, 'action': 'await_separate_generation_instruction'} for batch in batches)
    records.append({'queue_id': BLOCKED_ID, 'kind': 'clarification_queue_not_generation_batch', 'status': 'blocked',
                    'exercise_count': blocked['exercise_count'], 'path': BLOCKED_PATH, 'newly_prepared': False,
                    'action': 'answer_grouped_questions_then_recheck_each_ID'})
    return records

def validate(s, q, batches, review, blocked, protected):
    errors, seen, checked = [], set(), []
    source_counts = collections.Counter(e['id'] for e in s['catalog']['exercises'])
    if len(source_counts) != 451 or any(n != 1 for n in source_counts.values()): errors.append('catalog_ID_count_not_unique')
    resolved_by_id = {row['exercise_id']: row for row in review['resolved']}
    old_ids = [eid for path in OLD_PATHS for eid in load(path)['exercise_ids']]
    if len(old_ids) != 90 or len(set(old_ids)) != 90: errors.append('old_reservations_not_unique')
    for batch in batches:
        bid = batch['batch_id']
        if batch['status'] != 'ready' or batch['generation_authorized_now'] or batch['catalog_sha256'] != s['catalog_sha256'] or batch['style_sha256'] != s['style_sha256'] or batch['style_version'] != 'v1': errors.append('batch_source_or_status:' + bid)
        if not 1 <= batch['exercise_count'] <= 10 or batch['exercise_count'] != len(batch['exercises']) or batch['exercise_ids'] != [row['exercise_id'] for row in batch['exercises']]: errors.append('batch_size_or_ID_list:' + bid)
        for row in batch['exercises']:
            eid = row['exercise_id']; checked.append(eid)
            if eid in seen: errors.append('duplicate_new_ID:' + eid)
            seen.add(eid)
            if eid in old_ids: errors.append('old_batch_ID_reassigned:' + eid)
            if source_counts[eid] != 1: errors.append('unknown_or_duplicate_catalog_ID:' + eid); continue
            for key, value in base.fields_for_id(eid, s).items():
                if row.get(key) != value: errors.append('exact_catalog_field_mismatch:' + eid + ':' + key)
            if availability(eid, s, eid in resolved_by_id)[0] != 'eligible': errors.append('PNG_assignment_attempt_or_clarification_overlap:' + eid)
            if eid not in SCENES: errors.append('scene_missing:' + eid); continue
            original_s = dict(s)
            original_s['commits'] = dict(s['commits']); original_s['commits']['origin/work'] = batch['catalog_source_commit']
            expected = make_batch(bid, [eid], original_s, batch['prepared_at'], resolved_by_id, batch['preparation_stage'])['exercises'][0]
            # Exact reference commit is pinned at preparation; content hashes are
            # checked against the live source, not merely against the saved row.
            for key in ['human_reference', 'scene', 'prompt_payload', 'generation_prompt', 'generation_prompt_sha256',
                        'planned_png_path', 'planned_output_relative_path', 'style_version', 'style_sha256', 'clarification_resolution']:
                if row.get(key) != expected[key]: errors.append('self_contained_prompt_binding:' + eid + ':' + key)
            if row.get('human_reference', {}).get('sha256') != s['reference_sha256']: errors.append('reference_hash_changed:' + eid)
            if row.get('status') != 'ready' or row.get('attempts') != 0 or row.get('generation_authorized_now') or any(row.get(k) is not None for k in ['result_path','result_sha256','user_review','technical_check']): errors.append('preparation_claims_execution:' + eid)
    completion = q['completion']
    if checked != completion['new_exercise_ids'] or len(checked) != completion['new_prepared_count']: errors.append('queue_new_IDs_or_count_mismatch')
    input_ids = completion['input_remaining_ids']; excluded_ids = {row['exercise_id'] for row in completion['excluded_since_previous_round']}
    expected_first = [eid for eid in input_ids if eid not in excluded_ids]
    if [eid for batch in batches if batch['preparation_stage'] == 'remaining_queue' for eid in batch['exercise_ids']] != expected_first: errors.append('remaining_queue_not_fully_prepared_in_order')
    if [eid for batch in batches if batch['preparation_stage'] == 'resolved_clarifications' for eid in batch['exercise_ids']] != list(resolved_by_id): errors.append('resolved_IDs_not_prepared_once')
    if q['remaining_unprepared_ids'] or q['remaining_unprepared_count'] != 0: errors.append('eligible_queue_not_finished')
    if q['prepared_count'] != 90+len(seen) or q['eligible_count'] != len(q['eligible_exercise_ids']): errors.append('queue_counts_wrong')
    if set(q['eligible_exercise_ids']) != set(old_ids)|seen or len(q['eligible_exercise_ids']) != len(set(q['eligible_exercise_ids'])): errors.append('historical_prepared_queue_IDs_mismatch')
    if len(q['exercises']) != len(q['eligible_exercise_ids']): errors.append('queue_rows_missing')
    for row in q['exercises']:
        eid = row['exercise_id']; fields = base.fields_for_id(eid, s)
        for key in ['name','equipment','primary_muscle','secondary_muscles','source_catalog_sha256','source_catalog_record_sha256','source_english_sha256']:
            if row.get(key) != fields[key]: errors.append('queue_field_mismatch:' + eid + ':' + key)
        if eid in seen:
            bid = next((batch['batch_id'] for batch in batches if eid in batch['exercise_ids']), None)
            if row.get('batch_id') != bid or row.get('prompt_prepared') is not True: errors.append('queue_batch_binding:' + eid)
    blocked_ids = [row['exercise_id'] for row in review['blocked']]
    if set(blocked_ids) & seen or len(blocked_ids) != len(set(blocked_ids)): errors.append('ready_blocked_overlap')
    if blocked['status'] != 'blocked' or blocked['exercise_ids'] != blocked_ids or blocked['exercise_count'] != len(blocked_ids): errors.append('blocked_queue_mismatch')
    if set(resolved_by_id)|set(blocked_ids) != {row['exercise_id'] for row in load(base.CLARIFICATIONS_PATH)['new_clarifications']}: errors.append('clarification_partition_wrong')
    for row in review['resolved'] + review['blocked'] + review['previously_reserved']:
        eid = row['exercise_id']
        for key,value in base.fields_for_id(eid,s).items():
            if row.get(key) != value: errors.append('review_source_mismatch:' + eid + ':' + key)
        for proof in row['evidence']:
            if proof['exercise_id'] != eid or proof['catalog_sha256'] != s['catalog_sha256'] or proof['catalog_record_sha256'] != base.value_sha(s['by_id'][eid]) or proof['value'] != field_value(s['by_id'][eid],proof['field']): errors.append('evidence_ID_or_field_mismatch:' + eid)
    style = next(group for group in review['question_groups'] if group['group_id']=='style_mapping')
    if len(style['exercise_ids']) != len(set(style['exercise_ids'])) or any(s['by_id'][eid]['primary_muscle'] not in ['full_body','cardio','other'] for eid in style['exercise_ids']): errors.append('style_group_wrong')
    if any(row.get('question') is not None for row in review['blocked']+review['previously_reserved'] if row.get('question_group')=='style_mapping'): errors.append('duplicated_per_exercise_style_questions')
    for path, expected_sha in protected.items():
        if base.sha((ROOT/path).read_bytes()) != expected_sha: errors.append('protected_file_changed:' + path)
    return {'schema_version':1, 'status':'failed' if errors else 'passed','errors':errors,
            'checked_at':datetime.datetime.now(ZoneInfo('Europe/Kiev')).isoformat(), 'audited_commits':s['commits'],
            'catalog_sha256':s['catalog_sha256'],'style_version':'v1','style_sha256':s['style_sha256'],
            'unique_catalog_IDs':len(source_counts),'new_batch_count':len(batches),'new_prepared_count':len(seen),
            'prepared_from_remaining':len(expected_first),'prepared_from_resolved_clarifications':len(resolved_by_id),
            'own_blocked_count':len(blocked_ids),'previously_reserved_not_reassigned_count':len(review['previously_reserved']),
            'eligible_unprepared_remaining':0,'protected_sha256':protected,'source_files':s['source_files'],
            'checked_exercise_ids':checked,'scope_limit':q['scope_limit'],
            'checks':['exact_ID_exists_once','source_English_equipment_muscles_exact','no_old_or_other_assignment_or_PNG_overlap',
                      'concrete_phase_pose_grip_supports_camera','same_ID_supplementary_evidence_exact','full_prompt_style_reference_hash_path',
                      'future_PNG_path_matches_ID','ready_and_blocked_disjoint','failed_noPNG_ID_retained_in_old_batch','old_files_unchanged']}

def negative_checks(s,q,batches,review,blocked,protected):
    cases={}
    mutations={
        'wrong_name':lambda b:b[0]['exercises'][0].update(name='deliberate wrong name'),
        'wrong_English_ID':lambda b:b[0]['exercises'][0].update(source_english=b[0]['exercises'][1]['source_english']),
        'wrong_equipment':lambda b:b[0]['exercises'][0].update(equipment='cable'),
        'wrong_muscles':lambda b:b[0]['exercises'][0].update(primary_muscle='full_body'),
        'duplicate_between_batches':lambda b:b[1]['exercises'].__setitem__(0,copy.deepcopy(b[0]['exercises'][0])),
        'old_failed_noPNG_ID_reassigned':lambda b:b[0]['exercises'][0].update(exercise_id='hanging-knee-raise'),
        'wrong_prompt':lambda b:b[0]['exercises'][0].update(generation_prompt='wrong prompt'),
        'wrong_PNG_ID':lambda b:b[0]['exercises'][0].update(planned_png_path='/workspace/exercise-image-results/wrong.png'),
        'wrong_reference':lambda b:b[0]['exercises'][0]['human_reference'].update(sha256='0'*64),
        'wrong_style':lambda b:b[0].update(style_version='v999'),
    }
    for key, mutate in mutations.items():
        bad=copy.deepcopy(batches);mutate(bad);cases[key]=validate(s,q,bad,review,blocked,protected)['status']=='failed'
    for key,field in [('new_other_assignment','reserved'),('new_saved_PNG','png_sources')]:
        bad=copy.deepcopy(s);bad[field][batches[0]['exercise_ids'][0]].append({'branch':'synthetic_only'});cases[key]=validate(bad,q,batches,review,blocked,protected)['status']=='failed'
    badreview=copy.deepcopy(review);badreview['resolved'][0]['evidence'][0]['value']='deliberately changed source quote'
    cases['wrong_resolution_quote']=validate(s,q,batches,badreview,blocked,protected)['status']=='failed'
    if not all(cases.values()): raise ValueError('Negative guard did not reject mutation: '+repr(cases))
    return cases

def handoff(s,q,batches,review,report):
    completion=q['completion']; style=next(g for g in review['question_groups'] if g['group_id']=='style_mapping')
    lines=['# Agent-03: завершення придатної черги «Інші»', '',
           f'Дата підготовки: {completion["prepared_at"]}. Власна гілка `{base.BRANCH}`. Work `{s["commits"]["origin/work"]}`.', '',
           f'Catalog SHA256 `{s["catalog_sha256"]}`; стиль **v1**, SHA256 `{s["style_sha256"]}`.', '',
           f'Підготовлено **{completion["new_prepared_count"]}** нових завдань: **{completion["prepared_from_remaining"]}** з решти черги та **{review["resolved_ready_count"]}** із уточнень з однозначними текстовими джерелами того самого ID. Придатний непідготовлений залишок: **0**. Це завершення підготовки доступних вправ, не завершення генерації.', '',
           f'Власні уточнення: **{review["own_blocked_count"]} blocked**. Попередні **{review["previously_reserved_not_reassigned_count"]}** ID чужого clarification-файла не перепризначені. Для Diamond Push Up зафіксовано відповідь про ромб пальців із того самого ID, але нового пакета для нього не створено.', '',
           '## Нові пакети', '', '| Пакет | Статус | Кількість | Точний шлях |', '| --- | --- | ---: | --- |']
    for b in batches: lines.append(f'| {b["batch_id"]} | ready | {b["exercise_count"]} | `{NEW_PATHS[b["batch_id"]]}` |')
    lines += [f'| Список власних уточнень (не пакет генерації) | blocked | {review["own_blocked_count"]} | `{BLOCKED_PATH}` |', '',
              f'Повна черга: `{base.QUEUE_PATH}`. Реєстр усіх старих і нових пакетів із ready/blocked, count і path: queue.completion.package_registry. Історичні eligible_exercise_ids/prepared_count включають раніше підготовлені ID; actionable new IDs містить completion.new_exercise_ids. Залишок визначає remaining_unprepared_ids.', '']
    for b in batches:
        lines += [f'### {b["batch_id"]}', '']
        lines += [f'- `{row["exercise_id"]}` — {row["name"]}' for row in b['exercises']]
        lines.append('')
    lines += ['## Попередні пакети й продовження', '',
              '001–009 збережено байт-у-байт. PNG та призначення звіряли лише за Git tree, progress і manifests; пікселі/розміри/alpha повторно не перевіряли. Наявність PNG, включно з pending, виключає повторну підготовку. PNG не є схваленням. work, progress, user_review і Supabase не змінювали.', '']
    for entry in completion['package_registry']:
        if entry.get('newly_prepared') or 'batch_id' not in entry: continue
        lines.append(f'- `{entry["batch_id"]}`: **{entry["status"]}**, {entry["exercise_count"]} ID, `{entry["path"]}`; уже мають PNG {len(entry["IDs_with_existing_PNG"])}; продовження без PNG {len(entry["continuation_ids_retained_here"])}.')
        if entry['continuation_ids_retained_here']:
            lines.append('  Продовжити саме цей попередній пакет: '+', '.join('`'+eid+'`' for eid in entry['continuation_ids_retained_here'])+'.')
    lines += ['', 'Для `hanging-knee-raise` у work attempts=2, status=blocked_quota, result_path=null, PNG немає. Невдалий виклик не є готовим результатом. ID залишається в 009 разом із вісьмома не запущеними вправами; його не перенесли в 010–015 і не скидали історію. Генерацію зараз не запускати.', '',
              '## Самодостатність і джерела', '',
              'Кожен готовий запис містить точні exercise_id/name, незмінний повний content.en (description, instructions, form_cues, common_mistakes, safety_note, provenance), equipment/muscles та SHA256 каталогу, повного запису й English блока. Дані отримано exact-ID словником, не за назвою чи позицією.', '',
              'Для всіх завдань окремо задано scene.pose, grip, supports_and_equipment, single_phase і camera; весь prompt містить ці поля та спільний стиль v1. Контрольний SHA256 prompt збережено. Еталон людини: `'+str(ROOT/s['reference_path'])+'`, repository path `'+s['reference_path']+'`, SHA256 `'+s['reference_sha256']+'`. Path/hash/роль повторено в кожному записі й prompt: тільки зовнішність/пропорції/матеріали. Позу, обладнання та підсвітку еталона не копіювати.', '',
              'Запланований результат: `/workspace/exercise-image-results/<batch_id>/<exercise_id>/attempt-1.png`. Це майбутній шлях: result_path/result_sha256/user_review/technical_check=null, attempts=0. Ні генерації, ні візуального QA не проводили.', '',
              'Для 16 рішень збережено дослівні supplemental поля того самого ID з content.es/ru/uk або match.rationale, field path, ID, commit та catalog/record SHA256. Англійський текст не переписано й не замінено перекладом. Точні рішення та часткові відповіді: `'+REVIEW_PATH+'`.', '',
              'Приклад: Close Grip — content.es.instructions[1] задає трохи вужче плечей; Squeeze Press — content.uk.instructions[0,1,3] задають притиснуті гантелі та постійний тиск; Glute Bridge — content.es.instructions[1] задає гриф на стегнах і дві руки. Ширини, опори чи ваги інших вправ не переносили.', '',
              'Справжні суперечності не знято вибором мови. Зокрема Trap Bar має всередині рами в uk проти перед тілом/пронації в es; Clap має різну стартову ширину кистей; deadlift-band має under/over mid-foot. Front Squat має підтверджену опору на передніх плечах, але ще невизначений тип хвата. Partial evidence не дає автоматичного ready.', '',
              '## Згруповані питання', '',
              f'Одне спільне рішення стилю для **{style["exercise_count"]}** ID: '+style['question'], '',
              'Підгрупи original primary: '+', '.join(f'{muscle}={len(ids)}' for muscle,ids in style['subgroups_by_original_primary_muscle'].items())+'. '+
              'Це 55 власних і 5 раніше зарезервованих ID. Не створювати 60 окремих запитів. Після рішення стилю все одно перевірити техніку кожного ID перед допуском.', '',
              '| Група | Кількість ID | Питання |', '| --- | ---: | --- |']
    for group in review['question_groups']:
        if group['group_id']!='style_mapping': lines.append(f'| `{group["group_id"]}` | {group["exercise_count"]} | {group["question"]} |')
    lines += ['', 'Повні точні ID, вихідні поля, evidence й індивідуальні короткі питання техніки збережено у review/blocked JSON. Попередній clarification JSON та чужі batch-файли залишено незмінними.', '',
              '## Перевірка та майбутня передача', '',
              f'Перевірка `{REPORT_PATH}`: exact-ID поля, 1–10 записів у ready-пакеті, відсутність повторів і перетинів з PNG/призначеннями/001–009, evidence зі свого ID, prompt/style/reference/path/hash та незмінність protected файлів. {len(report["negative_guard_cases"])} навмисних підмін відхилено. Повторний аудит PNG та Supabase не запускали.', '',
              '```bash',
              "git fetch --no-tags origin '+refs/heads/work:refs/remotes/origin/work' '+refs/heads/agent-02-machines-001:refs/remotes/origin/agent-02-machines-001' '+refs/heads/agent-04-supabase-integration:refs/remotes/origin/agent-04-supabase-integration'",
              'python scripts/prepare_agent03_other_completion.py --check', '```', '',
              'Якщо з’явиться інша agent-гілка, fetch її перед check: валідатор сканує всі fetched agent-гілки. Нова PNG/бронь зупиняє відповідний ID. Старі скрипти --check є історичними перевірками своїх раундів; поточний формат перевіряє completion script.', '',
              'Після окремого доручення на генерацію брати record/prompt за exact exercise_id, не за порядком. Перед кожним викликом звірити поточні результати та призначення. Журнал має містити batch_id, exercise_id, catalog/record/prompt/reference hashes, фактичний tool-call identity, attempt, PNG path/SHA256. Файл цього виклику зберегти під його ID; не підміняти результат за схожістю назв. Хеші provenance не є доказом візуальної правильності.', '',
              'Межа: незапушені файли/призначення інших хмарних задач можуть бути недоступні. Лише cloud workspace; без локального Mac, пошуку зовнішніх референсів, генерації, автоматичних повторів/ресайзу, платного API чи Supabase. Зупинитися після commit/push і звірки віддалених власних JSON/Markdown файлів.']
    return '\n'.join(lines)+'\n'

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--prepare',action='store_true');parser.add_argument('--check',action='store_true');args=parser.parse_args()
    if args.prepare==args.check: parser.error('Choose --prepare or --check')
    if base.git('branch','--show-current').decode().strip()!=base.BRANCH: raise ValueError('Wrong branch')
    configure();s=snapshot();q=load(base.QUEUE_PATH)
    if args.prepare:
        if any((ROOT/path).exists() for path in [*NEW_PATHS.values(),BLOCKED_PATH,REVIEW_PATH,REPORT_PATH,HANDOFF_PATH]): raise ValueError('Completion artifacts already exist; use read-only --check')
        if q['prepared_count']!=90 or q['preparation_rounds'][-1]['round']!=3: raise ValueError('Unexpected starting queue round')
        if q['catalog_sha256']!=s['catalog_sha256'] or q['style_sha256']!=s['style_sha256']: raise ValueError('Catalogue/style changed, review first')
        protected=freeze(); timestamp=datetime.datetime.now(ZoneInfo('Europe/Kiev')).isoformat()
        original=q['remaining_unprepared_ids'][:]; available,excluded=previous.candidates(q,s)
        if any(eid not in SCENES for eid in available): raise ValueError('No reviewed exact-ID scene for remaining record')
        review=review_clarifications(s); resolved_by_id={row['exercise_id']:row for row in review['resolved']}
        if set(resolved_by_id)!=set(RESOLUTIONS): raise ValueError('A resolved ID became assigned/produced; exclude and review before preparing')
        # Verify only the required reference bytes, never pixel-QA any result PNG.
        if base.sha((ROOT/s['reference_path']).read_bytes())!=s['reference_sha256']: raise ValueError('Human reference unavailable or hash mismatch')
        batches=[];bid_index=0
        for stage,ids in [('remaining_queue',available),('resolved_clarifications',list(resolved_by_id))]:
            for start in range(0,len(ids),10):
                if bid_index>=len(NEW_IDS): raise ValueError('More batches required; add next unused IDs')
                bid=NEW_IDS[bid_index];bid_index+=1
                batches.append(make_batch(bid,ids[start:start+10],s,timestamp,resolved_by_id,stage))
        prepared=[eid for batch in batches for eid in batch['exercise_ids']]
        blocked={'schema_version':1,'queue_id':BLOCKED_ID,'kind':'blocked_clarifications_not_generation_batch','owner_agent':'agent-03',
                 'status':'blocked','catalog_sha256':s['catalog_sha256'],'style_version':'v1','generation_authorized_now':False,
                 'exercise_count':len(review['blocked']),'exercise_ids':[row['exercise_id'] for row in review['blocked']],
                 'question_groups':review['question_groups'],'exercises':[dict(row,prompt_prepared=False,generation_prompt=None,planned_png_path=None) for row in review['blocked']],
                 'previously_reserved_records_in_review_path':REVIEW_PATH}
        removed={row['exercise_id'] for row in excluded}
        q['eligible_exercise_ids']=[eid for eid in q['eligible_exercise_ids'] if eid not in removed]+list(resolved_by_id)
        q['exercises']=[row for row in q['exercises'] if row['exercise_id'] not in removed]
        for eid in resolved_by_id:
            fields=base.fields_for_id(eid,s)
            q['exercises'].append({key:copy.deepcopy(value) for key,value in fields.items() if key!='source_english'})
            q['exercises'][-1].update(priority_tier=4,source_clarification_resolution_path=REVIEW_PATH)
        for index,row in enumerate(q['exercises'],1):
            row['queue_order']=index
            if row['exercise_id'] in prepared:
                row.update(batch_id=next(batch['batch_id'] for batch in batches if row['exercise_id'] in batch['exercise_ids']),
                           prompt_prepared=True,status='ready',preparation_status='prompt_prepared_not_generated')
        q['excluded']=[row for row in q['excluded'] if row['exercise_id'] not in resolved_by_id]+excluded
        q['exclusion_counts_disjoint']=dict(collections.Counter(row['reason_code'] for row in q['excluded']))
        q.update(updated_at=timestamp,prepared_count=90+len(prepared),eligible_count=len(q['eligible_exercise_ids']),
                 remaining_unprepared_ids=[],remaining_unprepared_count=0,latest_launch_ids=prepared,
                 generation_authorized_now=False,blocked_clarification_count=len(review['blocked']),blocked_clarification_path=BLOCKED_PATH,
                 clarification_review_path=REVIEW_PATH,
                 last_live_check={'status':'passed','checked_at':timestamp,'audited_commits':s['commits']})
        q['batch_paths'] += [NEW_PATHS[batch['batch_id']] for batch in batches]
        package_registry=registry(s,batches,blocked)
        q['completion']={'status':'eligible_preparation_finished_blocked_clarifications_remain','prepared_at':timestamp,
                         'audited_commits':s['commits'],'input_remaining_ids':original,'excluded_since_previous_round':excluded,
                         'prepared_from_remaining':len(available),'prepared_from_clarifications':len(resolved_by_id),
                         'new_prepared_count':len(prepared),'new_exercise_ids':prepared,'new_batch_paths':[NEW_PATHS[batch['batch_id']] for batch in batches],
                         'eligible_unprepared_remaining':0,'package_registry':package_registry,
                         'scope_note':'Old batch IDs/results stay reserved; failed generator calls with no PNG remain in their original batches. No PNG technical audit or Supabase audit.'}
        q['preparation_rounds'].append({'round':4,'prepared_at':timestamp,'audited_commits':s['commits'],
                                        'input_remaining_ids':original,'excluded_since_previous_round':excluded,'exercise_ids':prepared,
                                        'batch_paths':q['completion']['new_batch_paths'],'status':'ready_preparation_only'})
        report=validate(s,q,batches,review,blocked,protected)
        report['negative_guard_cases']=negative_checks(s,q,batches,review,blocked,protected)
        if report['errors']: raise ValueError(json.dumps(report['errors']))
        for batch in batches: save(NEW_PATHS[batch['batch_id']],batch)
        save(base.QUEUE_PATH,q);save(REVIEW_PATH,review);save(BLOCKED_PATH,blocked);save(REPORT_PATH,report)
        (ROOT/HANDOFF_PATH).write_text(handoff(s,q,batches,review,report))
        assert protected==freeze()
    else:
        batches=[load(path) for path in q['completion']['new_batch_paths']];review=load(REVIEW_PATH);blocked=load(BLOCKED_PATH);saved=load(REPORT_PATH)
        report=validate(s,q,batches,review,blocked,saved['protected_sha256'])
        report['negative_guard_cases']=negative_checks(s,q,batches,review,blocked,saved['protected_sha256'])
    print(json.dumps({key:report[key] for key in ['status','audited_commits','new_batch_count','new_prepared_count','prepared_from_remaining','prepared_from_resolved_clarifications','own_blocked_count','eligible_unprepared_remaining','negative_guard_cases','errors']},ensure_ascii=False,indent=2))
    if report['errors']:sys.exit(1)

if __name__=='__main__':main()
