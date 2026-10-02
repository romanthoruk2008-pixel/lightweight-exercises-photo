#!/usr/bin/env python3
"""Prepare one worker's 30 tasks; never call an image generator.

Exact-ID catalogue extraction, selected-assignment reconciliation and immutable
old-file checks are reused from the earlier inventory tooling. --check is read-only.
"""
import argparse
import collections
import copy
import datetime
import json
import prepare_agent03_generator_b as b

base = b.base
ROOT = b.ROOT
ROUND = 'agent-03-single-generator-2026-10-03'
ROLE = 'generator-single'
WORKER = 'agent-08-generator-single-2026-10-03'
REG = f'data/assignments/{ROUND}.json'
MANIFEST = f'data/manifests/{ROUND}/{ROLE}.json'
EVIDENCE = f'data/audits/{ROUND}-technique.json'
ERRORS = f'data/audits/{ROUND}-source-errors.json'
CHECK = f'data/audits/{ROUND}-validation.json'
HANDOFF = f'docs/{ROUND}-handoff.md'
MESSAGE = f'docs/{ROUND}-message.md'
PREPARED = 'data/queues/agent-03-user-answers-2026-10-03-prepared.json'
DECISIONS = 'data/technique-decisions/agent-03-user-answers-2026-10-03.json'
BLOCKED = 'data/queues/agent-03-user-answers-2026-10-03-blocked.json'
PREFIX = 'data/batches/agent-03-others-'
BATCHES = [PREFIX + f'{i:03}.json' for i in [28, 29, 30]]
CLOUD = f'/workspace/exercise-image-results/{ROUND}/{ROLE}'
GIT = f'assets/exercises/pending/{ROUND}/{ROLE}'

# These are rendering decisions for exact, individually read records. Generic
# compatible unbranded geometry is permitted by AGENTS.md; brand, stack/plate
# type and numerical loading are not inferred from equipment="machine".
SCENES = {
 'biceps-curl-machine': ('Controlled bilateral curl near the top', 'Seated, upper arms resting flat on the arm pad, shoulders relaxed; elbows bent as handles approach shoulders; upper arms remain supported.', 'Both paired handles held palms up, wrists neutral.', 'Seat and upper-arm pad on a compatible seated lever curl machine; feet grounded; only forearms and lever rotate.', 'Flex both elbows without lifting upper arms; lower back toward nearly straight elbows.'),
 'chinup-assisted-machine': ('Chin just above fixed bar', 'Torso braced and upright, elbows draw toward ribs, shoulders down; both knees on assistance platform and feet clear of floor.', 'Underhand grip on FIXED bar about shoulder-width apart.', 'Unbranded counterweight-assisted station, fixed overhead bar, both knees on vertically moving platform. Platform supports knees, not hips.', 'Body and assistance platform rise together; bar remains still; lower to extended arms without kipping.'),
 'incline-chest-press-machine': ('Supported press nearing extension', 'Seated against inclined backrest, feet flat; hands press forward and upward away from upper chest, elbows nearly extended, shoulder blades controlled.', 'Overhand paired handles slightly wider than shoulder width, wrists stacked over elbows.', 'Compatible inclined seated lever press, pelvis on seat and back on pad, both feet on floor; no free barbell or Smith rail.', 'Both handles press away from upper chest on inclined lever arc and return toward chest.'),
 'iso-lateral-chest-press-machine': ('Both independent handles pressing forward', 'Seated with back flat against pad, feet grounded; two hands start beside chest with elbows about 90 degrees and press toward near extension.', 'Overhand grip, one handle in each hand, wrists neutral.', 'Seated horizontal lever chest press with TWO mechanically independent lever arms and handles, back pad and seat. No common bar linking hands.', 'Both independent handles advance forward from chest together for this scene; return under control.'),
 'iso-lateral-high-row-machine': ('High-row contracted endpoint', 'Seated, sternum on chest pad, feet flat on platform, long neutral back; elbows drawn back as high handles reach upper torso.', 'Overhand grip slightly wider than shoulder width, one independent high-row handle in each hand.', 'Compatible seated chest-supported HIGH lever row with two independent lever arms, seat and foot platform; no low-pulley cable substitute.', 'Pull high handles toward upper torso, squeeze shoulder blades without lifting sternum off pad; return to controlled forward reach.'),
 'seated-row-machine': ('Handles drawn toward lower ribs', 'Seated with sternum against pad and feet on footrests, back straight; elbows move behind ribs with shoulders down.', 'Overhand paired handles shoulder-width apart.', 'Seated chest-supported lever row, seat, chest pad and footrests; no unsupported cable-row substitute.', 'Pull both handles horizontally toward lower ribs; arms lengthen on return while chest remains supported.'),
 'shoulder-press-machine-plates': ('Near top of overhead press', 'Seated with pelvis on seat and back against pad, feet flat; elbows nearly straight but unlocked, hands upward and slightly forward of shoulders.', 'Overhand paired handles slightly wider than shoulder width.', 'Plate-loaded lever shoulder-press machine with backrest, seat, two handles and compatible plate-loading arms. No numerical load/plate count, no free overhead bar.', 'Press both handles up and forward from shoulder level along lever arc; lower under control.'),
 't-bar-row-machine': ('Chest-supported row contraction', 'SEATED as explicitly stated by selected dataset 0606, sternum on pad, feet flat on footplate; elbows back, handles near lower ribs.', 'Wide overhand handle slightly wider than shoulder width, both hands attached to same compatible T-bar lever handle assembly.', 'Seated chest-supported hinged T-bar lever machine with seat, chest pad and footplate. Do not substitute standing unsupported landmine row.', 'Pull lever handles toward lower ribs with sternum on pad; lower until arms lengthen without torso lift.'),
 'triceps-dip-assisted-machine': ('Controlled lower endpoint', 'Upright torso, shoulders down, elbows bent back until upper arms approach horizontal; BOTH KNEES remain on moving platform, hips off pad.', 'Both hands wrap fixed parallel dip handles, palms facing inward, elbows travel back.', 'Counterweight-assisted parallel-bar station, both knees on assistance platform, feet clear of floor. Platform travels with body; no seated press machine.', 'Bend elbows to lower body and platform together, then press through fixed handles to extend elbows. Catalogue hip-on-pad cue is erroneous; exact instructions and dataset explicitly specify knees.'),
 'single-leg-extensions-machine': ('Right leg nearly horizontal', 'Seated against back support, right knee aligned with machine pivot and nearly extended without lockout; left leg remains clear of working lever, left foot grounded for this scene.', 'Both hands hold the prescribed side handles.', 'Seat/back support, knee-aligned rotating lever and padded contact in front of right lower shin just above ankle; left leg clear of lever.', 'Right knee extension raises pad/working lower leg toward horizontal; controlled lowering by knee flexion, no elbow-driven pressing.'),
 'standing-leg-curls-machine': ('Right heel drawn toward glute', 'Standing upright with left foot supporting body, right thigh vertical and against stationary thigh pad, right knee bent; hips still and back neutral.', 'Both hands hold fixed upright support handles.', 'Standing leg-curl station with stationary working-thigh pad and moving padded lever behind right ankle; opposite foot on floor, both hands supported. Compatible stack resistance per catalogue common mistake.', 'Right knee flexion moves posterior ankle pad toward glute; right thigh and pelvis stay still; return without hip extension.'),
 'chest-press-machine': ('Seated lever press near extension', 'Seated with back against pad and feet planted, wrists stacked; handles travel forward away from chest, elbows almost straight and soft.', 'Overhand paired handles, elbows initially about 90 degrees; this grip is confirmed by the exact dataset 0576.', 'User-selected SEATED LEVER machine, seat, back pad and two handles, both feet on floor. No lying barbell bench scene despite erroneous English template.', 'Press handles forward from beside chest, return under control; no free-bar rerack.'),
 'air-bike-machine': ('One reciprocal pedaling stroke', 'Upright on saddle, feet on pedals; right pedal lower with right knee slightly bent, left knee flexed; left handle pushed forward and right handle pulled back.', 'Both hands hold moving bike handles, relaxed closed grip.', 'Unbranded fan-resistance AIR BIKE, saddle, crank-linked pedals and reciprocal moving handles. Functional front fan per exact-ID description and pinned-match text, not from category machine. No elliptical standing pedals.', 'Pedal continuously while arms push and pull reciprocally; freeze one stroke, no second body.'),
 'recumbent-bike-machine': ('One supported pedaling stroke', 'Seated/reclined with back firmly against backrest, pedals in FRONT of body; right leg nearer farthest pedal point with knee still slightly bent, left knee flexed.', 'No working hand grip is prescribed; hands rest neutrally on thighs as a scene choice, no invented arm mechanism.', 'Recumbent stationary bike, low supported seat/backrest, front crank and two pedals, feet on pedals; no upright saddle or moving arm handles.', 'Smooth seated pedal rotation with back supported; freeze one pedal stroke.'),
 'rowing-machine': ('Drive finish, handle at lower ribs', 'Seated on sliding ergometer seat, legs extended without forceful knee lock, hips opened and torso long with slight rearward hinge; elbows back, shoulders relaxed.', 'Both hands hold the SINGLE rowing handle, wrists straight, handle level. No independent cable handles.', 'Rowing ergometer with sliding seat on rail, two strapped footplates and single connected handle; both feet secured. No stationary lever-row seat.', 'Leg drive then hip opening then arm pull to lower ribs; depict finish only. Recovery reverses sequence.'),
 'spinning-machine': ('One seated cycling stroke', 'Seated on stationary saddle, back long; right pedal down with slight knee bend and opposite knee flexed; trunk steady.', 'Both hands relaxed on fixed handlebars; no moving air-bike handles.', 'Unbranded stationary resistance bike, saddle, fixed handlebars and two compatible secured pedals; both feet in pedals. No treadmill.', 'Smooth continuous seated pedal circles with even rhythm; depict one stroke.'),
 'stair-machine-floors': ('One grounded stair-climbing step', 'Torso tall, right whole foot on higher step, left whole foot on adjacent lower step, knees flexed according to step height; hips centered over supports.', 'Light bilateral rail contact for balance, no hanging bodyweight from rails.', 'Motorized stair machine with moving full steps and balance rails; both whole feet supported on consecutive steps. Not an elliptical or two independent pedal stepper.', 'Alternate stepping up while stairs move downward. Floors are counting metadata, not image text or a new movement variant.'),
 'stair-machine-steps': ('One alternating grounded stair step', 'Tall torso, left whole foot on higher step and right whole foot on next lower step; pelvis centered and shoulders relaxed.', 'Hands lightly touch balance rails as specified by exact form cue.', 'Motorized stair machine, moving full steps and rails, both whole feet supported on consecutive steps.', 'Alternate controlled stair steps; steps are counting metadata only. One phase, not an airborne running stride.'),
 'treadmill-machine': ('Grounded treadmill walking stride', 'Upright torso, leading heel contacting moving belt, trailing forefoot still in contact, natural opposite arm swing; no airborne running phase.', 'Hands free and OFF rails as prescribed once balanced.', 'Compatible motorized treadmill with moving belt, deck and handrails; both foot contacts on belt. Minimal compatible walking incline, no numerical angle. Barefoot per unchanged approved style.', 'Even controlled walking while belt moves beneath body; one grounded stride, no forward outdoor travel.'),
 'inverted-row-machine': ('Chest near stationary Smith bar', 'Straight braced line shoulders to heels, heels grounded, body inclined beneath bar; elbows drawn back as chest approaches bar, no sagging hips.', 'Overhand FIXED bar slightly wider than shoulder width, exact dataset 0499 confirms grip.', 'User-selected Smith frame with bar securely LOCKED at waist height, both heels grounded. The bar is a STATIC bodyweight support and MUST NOT translate on rails.', 'Pull BODY toward stationary bar and lower by extending arms; no barbell row, moving Smith press or suspension straps.'),
}

# Explicit order: all ten non-machine ready tasks first, then supported strength
# equipment, then cardio and fixed Smith. Only one worker owns every new batch.
EQUIPMENT_IDS = list(SCENES)
assert len(EQUIPMENT_IDS) == 20

SOURCE_ERRORS = {
 'chest-press-machine': [('description', 'supported chest press using the barbell'), ('instructions/0', 'Lie on a flat bench with feet planted. Grip the barbell and hold it over the chest.')],
 'triceps-dip-assisted-machine': [('form_cues/0', 'Keep hips on the pad.')],
 'single-leg-extensions-machine': [('form_cues/1', 'Track the elbows on the working path.'), ('common_mistakes/1', 'Flaring the elbows abruptly.')],
}

def now(): return datetime.datetime.now(datetime.timezone.utc).isoformat()

def conflict(eid, s, assignments, allow_own=False):
    e = s['by_id'][eid]
    if e['archived']: return 'archived'
    if s['png_sources'].get(eid): return 'PNG_exists_including_pending'
    if eid in b.load(BLOCKED)['exercise_ids']: return 'unresolved_technique'
    for a in assignments.get(eid, []):
        own = a['branch'] == base.BRANCH or a['branch'] == WORKER
        if allow_own and own and a['path'] in BATCHES + [REG, MANIFEST]: continue
        if allow_own and own and a['kind'] == 'batch_queue_route' and a.get('batch_id') in ['agent-03-others-028','agent-03-others-029','agent-03-others-030']: continue
        return 'existing_assignment:' + a['branch'] + ':' + a['path']
    if s['touched'].get(eid): return 'previous_attempt_stays_in_original_batch'
    return None

def make_equipment_row(eid, s, evidence):
    row = base.fields_for_id(eid, s)
    scene = b.n.prior.scene(eid, SCENES[eid], b.CAMERA)
    binding = next(r for r in evidence['records'] if r['exercise_id'] == eid)
    selected = b.load(DECISIONS)['equipment_choices_next_stage'].get(eid)
    resolution = {'status':'resolved', 'decision_kind':'user_selected_variant_with_exact_source_confirmation' if selected else 'exact_ID_written_technique_confirmation',
                  'evidence_path':EVIDENCE, 'evidence_selector':'records[exercise_id="'+eid+'"]',
                  'technique_fields_read':['content.en.description','content.en.instructions','content.en.form_cues','content.en.common_mistakes','content.en.safety_note','content.pl.instructions','source.dataset_id'],
                  'dataset_instruction_steps_read': binding['original_dataset_english'],
                  'binding_or_name_alone_is_not_confirmation':True,
                  'catalog_modified':False, 'PNG_approval':False,
                  'construction_rule':'Standard compatible unbranded geometry allowed by AGENTS.md; choose geometry only around specified contacts/motion. Category machine does not establish a load mechanism, brand, angle or weight count.',
                  'illustration_choices':'Side/phase and compatible layout are scene choices, not amendments to source technique. Do not infer muscle targets from scene or equipment.'}
    if selected:
        resolution.update(user_decision_path=DECISIONS, user_selected_configuration=selected['selected_configuration'])
    if eid in SOURCE_ERRORS: resolution['preserved_source_errors_path'] = ERRORS
    style = copy.deepcopy(base.STYLE)
    style['no_invention'] = 'Exact-ID catalogue controls source text and muscles. Render documented selected scene; recorded source corrections apply to the derived scene only. No reference-pose copying or imported muscle targets.'
    files = [{'path':'docs/exercise-image-style.md','sha256':s['style_sha256']}]
    if row['primary_muscle'] in ['full_body','cardio','other']:
        style['version'] = b.NEUTRAL_VERSION
        style['primary_highlight'] = {'hex':None,'rule':'Keep whole body opaque neutral silver-gray. No anatomical primary or whole-body orange tint for full_body/cardio/other.'}
        files.append({'path':b.NEUTRAL_DOC,'sha256':b.sha(b.NEUTRAL_DOC)})
    payload = {'identity_do_not_render_as_text':{'exercise_id':eid,'name':row['name'],'catalog_sha256':s['catalog_sha256'],'catalog_record_sha256':row['source_catalog_record_sha256']},
               'exact_catalogue_source':{k:copy.deepcopy(row[k]) for k in ['source_english','equipment','primary_muscle','secondary_muscles']},
               'human_reference':b.n.prior.reference(s),'style':style,'approved_style_files':files,
               'selected_render_scene':scene,'technique_resolution':resolution,
               'source_use_rule':'Preserve raw source texts verbatim; render only selected scene and documented exact-source/user resolution. Do not silently repair the catalogue.'}
    prompt = 'Create exactly ONE square 1024x1024 transparent PNG of this exact exercise and ONE selected phase. Metadata must never appear as image text.\n' + json.dumps(payload,ensure_ascii=False,sort_keys=True,indent=2)
    row.update(generation_prompt=prompt,prompt_payload=payload,prompt_sha256=base.sha(prompt.encode()),scene=scene,
               technique_resolution=resolution,style_version=style['version'],approved_style_files=files,human_reference=payload['human_reference'])
    return row

def route(row, bid, s):
    eid = row['exercise_id']
    row.update(batch_id=bid,status='ready',technical_status='ready',assigned_generator=ROLE,
               assignment_registry_path=REG,execution_branch=WORKER,prompt_prepared=True,
               generation_authorized_now=False,preparation_generation_calls=0,attempts=0,next_attempt_number=1,
               planned_png_path=f'{CLOUD}/{bid}/{eid}/attempt-1.png',
               planned_git_png_path=f'{GIT}/{bid}/{eid}/attempt-1.png',
               result_path=None,result_sha256=None,user_review=None,
               future_user_review_policy='pending until explicit user approval',agent_visual_review='not_performed',
               source_catalog_commit=s['commits']['origin/work'],source_selector=f'exercises[id="{eid}"]',
               source_url='https://github.com/romanthoruk2008-pixel/lightweight-exercises-photo/blob/'+s['commits']['origin/work']+'/'+base.CATALOG_PATH)
    return row

def prepare(s):
    assert base.git('branch','--show-current').decode().strip() == base.BRANCH
    assert all(p not in paths for p in BATCHES for paths in s['trees'].values()), 'Batch number already exists'
    for p in BATCHES + [REG,MANIFEST,EVIDENCE,ERRORS,CHECK,HANDOFF,MESSAGE]:
        assert not (ROOT/p).exists(), 'Never overwrite: '+p
    frozen = b.n.protected_files()
    old_queue = b.load(base.QUEUE_PATH)
    old_routes = {r['exercise_id']:copy.deepcopy(r) for r in old_queue['exercises']}
    source = b.load(PREPARED)
    assert source['exercise_count'] == 10
    first = source['exercise_ids']
    ids = first + EQUIPMENT_IDS
    assert len(ids) == len(set(ids)) == 30
    assignments = b.actual_assignments(s)
    for eid in ids:
        assert conflict(eid,s,assignments) is None, (eid,conflict(eid,s,assignments))
    evidence = b.source_evidence(s,EQUIPMENT_IDS)
    evidence.update(prepared_at=now(),confirmation_rule='Actual same-ID description/instructions, supports, grip and motion were read. Binding/name/match score alone do not resolve technique.',images_reviewed=False,external_research=[{'url':'https://www.concept2.com/training/rowing-technique','status':'unavailable_proxy_403','used_as_confirmation':False}],
                    read_but_not_selected=[{'exercise_id':'calf-press-machine','reason':'Selected dataset mixes shoulder-pad setup, knees under pad and downward pad movement while heels rise; do not resolve this by name.'},
                                          {'exercise_id':'shrug-machine','reason':'English description standing vs selected dataset seat adjustment; supported posture not conclusively specified.'},
                                          {'exercise_id':'crunch-machine','reason':'English feet secured vs dataset feet flat and different moving-pad start; additional construction validation retained for later.'},
                                          {'exercise_id':'pullup-assisted-machine','reason':'Selected dataset specifies hanging feet but not exact assistance contact; do not guess kneeling vs standing platform.'}])
    for rec in evidence['records']:
        eid=rec['exercise_id']; rec['selected_scene']=b.n.prior.scene(eid,SCENES[eid],b.CAMERA)
        rec['decision_basis']='User-selected construction plus exact same-ID written motion' if eid in b.load(DECISIONS)['equipment_choices_next_stage'] else 'Exact same-ID English describes this posture, support, and motion; selected dataset and Polish provide grip/support corroboration where present. No external exercise substituted.'
    b.save(EVIDENCE,evidence)
    error_rows=[]
    for eid,fields in SOURCE_ERRORS.items():
        e=s['by_id'][eid]
        for pointer,quote in fields:
            value=e['content']['en']
            for token in pointer.split('/'): value=value[int(token)] if isinstance(value,list) else value[token]
            assert quote in value
            error_rows.append({'exercise_id':eid,'source_field':'/content/en/'+pointer,'exact_value':value,'problem':'Generic field conflicts with user-selected or explicitly instructed supports/movement; source catalogue left untouched.',
                               'scene_resolution':SCENES[eid], 'decision_source':DECISIONS if eid=='chest-press-machine' else EVIDENCE,
                               'catalog_modified':False,'user_approval_of_source_edit':False})
    b.save(ERRORS,{'schema_version':1,'catalog_sha256':s['catalog_sha256'],'records':error_rows,'prior_error_ledger_unchanged':b.ERRORS})
    prepared={r['exercise_id']:r for r in source['exercises']}
    batches=[]
    for bi,path in enumerate(BATCHES):
        bid=path.rsplit('/',1)[1][:-5]; group=ids[bi*10:(bi+1)*10]; rows=[]
        for eid in group:
            if eid in prepared:
                row=copy.deepcopy(prepared[eid])
                row['supersedes_own_unassigned_staging']={'path':PREPARED,'sha256':b.sha(PREPARED),'prompt_sha256':row['prompt_sha256'],'prompt_preserved_byte_for_byte':True,'old_staging_path':row['planned_png_path']}
            else: row=make_equipment_row(eid,s,evidence)
            rows.append(route(row,bid,s))
        doc={'schema_version':1,'batch_id':bid,'status':'ready','exercise_count':10,'exercise_ids':group,'exercises':rows,
             'source_branch':base.BRANCH,'generator':ROLE,'execution_branch':WORKER,'assignment_registry_path':REG,
             'execution_order':bi+1,'phase':'non_machine' if bi==0 else 'equipment_tail',
             'catalog_sha256':s['catalog_sha256'],'audited_commits':s['commits'],'generation_calls':0,
             'style_policy':'Exact specific primary: v1. full_body/cardio/other: approved neutral addendum; only exact secondary muscles #F26445 at 40–50%, empty list has no highlights.',
             'handoff_path':HANDOFF,'manifest_path':MANIFEST,'live_recheck_before_every_call':True}
        b.save(path,doc);batches.append(doc)
    tasks=[r for d in batches for r in d['exercises']]
    registry={'schema_version':1,'assignment_id':ROUND,'created_at':now(),'source_branch':base.BRANCH,'source_base_commit':s['commits']['HEAD'],
              'status':'ready','assignment_count':1,'exercise_count':30,'batch_paths':BATCHES,'catalog_sha256':s['catalog_sha256'],
              'assignments':[{'generator':ROLE,'execution_branch':WORKER,'status':'assigned','exercise_count':30,'exercise_ids':ids,'batch_paths':BATCHES,'batch_ids':[d['batch_id'] for d in batches],'execution_order':[1,2,3],'manifest_path':MANIFEST,'handoff_path':HANDOFF}],
              'existing_A_B_assignments_unchanged':True,'supersedes_other_agents':False,
              'scope_authorization':'User explicitly selected 30 tasks for ONE generator: first ten non-machine, then twenty equipment tasks at the end.',
              'generation_calls_by_preparer':0,'audited_commits':s['commits'],'results_git_root':GIT,'results_cloud_root':CLOUD,
              'scope_limit':'Pushed Git files from available remote heads only; unpushed outputs and live calls in other cloud tasks may be inaccessible. Worker must recheck before each call.',
              'remaining_technique_blocked_path':BLOCKED,'remaining_technique_blocked_ids':b.load(BLOCKED)['exercise_ids']}
    b.save(REG,registry)
    b.save(MANIFEST,{'schema_version':1,'manifest_id':ROUND,'generator':ROLE,'execution_branch':WORKER,'assignment_path':REG,'source_branch':base.BRANCH,'status':'ready_not_started','exercise_count':30,
                     'batches':[{'batch_id':d['batch_id'],'batch_path':p,'status':'ready','exercise_count':10,'exercises':[{'exercise_id':r['exercise_id'],'name':r['name'],'status':'not_started','attempts':0,'attempt_history':[],'user_review':None,'technical_check':None,'agent_visual_review':'not_performed','result_path':None,'planned_png_path':r['planned_png_path'],'planned_git_png_path':r['planned_git_png_path'],'source_catalog_sha256':r['source_catalog_sha256'],'style_version':r['style_version'],'prompt_sha256':r['prompt_sha256']} for r in d['exercises']]} for p,d in zip(BATCHES,batches)],
                     'user_review_policy':'pending on result creation until explicit user approval','generation_calls':0,'quota_rule':'On first quota/rate-limit generation error save failure/history, push checkpoint and stop; no retry calls.'})
    q=copy.deepcopy(old_queue); qr={r['exercise_id']:r for r in q['exercises']}
    for r in tasks:
        eid=r['exercise_id']; route_fields={k:copy.deepcopy(r[k]) for k in ['exercise_id','name','equipment','primary_muscle','secondary_muscles','source_catalog_sha256','source_catalog_record_sha256','source_english_sha256','status','assigned_generator','batch_id','prompt_prepared','style_version','assignment_registry_path']}
        route_fields['current_task_path']=PREFIX+r['batch_id'].removeprefix('agent-03-others-')+'.json'
        if eid in qr:qr[eid].update(route_fields)
        else:q['exercises'].append(route_fields);qr[eid]=route_fields
        if eid not in q['eligible_exercise_ids']:q['eligible_exercise_ids'].append(eid)
    for p in BATCHES:
        if p not in q['batch_paths']:q['batch_paths'].append(p)
    q.update(updated_at=now(),eligible_count=len(q['eligible_exercise_ids']),prepared_count=len(q['eligible_exercise_ids']),latest_launch_ids=ids)
    q['latest_user_answers']['ready_unassigned_prompt_count']=0
    q['latest_user_answers']['assigned_continuation_path']=REG
    q['single_generator_preparation']={'assignment_path':REG,'batch_paths':BATCHES,'exercise_count':30,'generator':ROLE,'execution_branch':WORKER,'handoff_path':HANDOFF,'equipment_tail_count':20,'older_A_B_tasks_unchanged':True,'generation_calls':0}
    q['phase_plan']['latest_equipment_allocation_path']=REG
    q['phase_plan']['phase2_execution_gate']='This worker: finish 028 before 029 and 030; later equipment candidates remain separate future work. Existing other-agent tasks remain intact.'
    q['count_semantics']='Historical unique prepared/routed IDs, including exercises subsequently generated. These counts are NOT the current missing-PNG backlog.'
    q['current_assignment_snapshot']={'assignment_path':REG,'audited_commits':s['commits'],'exercise_count':30,'generation_calls':0}
    q['historical_fields_note']='Original exclusions, ordering and eligibility_rules describe earlier non-machine selection snapshots; current routing is in single_generator_preparation and phase_plan. Do not count historical excluded lists as live assignments.'
    b.save(base.QUEUE_PATH,q)
    with (ROOT/'.gitignore').open('a') as f:
        f.write('\n# Exact pending result paths for one worker; three new batches, thirty IDs.\n')
        for r in tasks:f.write('!/'+r['planned_git_png_path']+'\n')
    old_untouched={eid:base.value_sha(r) for eid,r in old_routes.items() if eid not in ids}
    b.save(CHECK,{'schema_version':1,'status':'pending_validation','protected_sha256':frozen,'previous_queue_routes_sha256':old_untouched,'source_base_commit':s['commits']['HEAD'],'catalog_sha256':s['catalog_sha256']})
    check(s)

def check(s):
    reg=b.load(REG);report=b.load(CHECK);assignments=b.actual_assignments(s)
    errors=[]
    def require(ok,msg):
        if not ok:errors.append(msg)
    require(base.git('branch','--show-current').decode().strip()==base.BRANCH,'wrong_branch')
    counter=collections.Counter(e['id'] for e in s['catalog']['exercises'])
    require(len(counter)==451 and sum(len(e['content']) for e in s['catalog']['exercises'])==4448,'catalog_shape')
    require(s['catalog_sha256']==reg.get('catalog_sha256',report['catalog_sha256']),'catalog_hash')
    require(base.sha(base.git('show',s['commits']['origin/work']+':'+base.CATALOG_PATH))==s['catalog_sha256'],'work_catalog_mismatch')
    for p,h in report['protected_sha256'].items():require(b.sha(p)==h,'protected_file_changed:'+p)
    prepared={r['exercise_id']:r for r in b.load(PREPARED)['exercises']}
    q=b.load(base.QUEUE_PATH);qr={r['exercise_id']:r for r in q['exercises']}
    for eid,h in report['previous_queue_routes_sha256'].items():require(base.value_sha(qr[eid])==h,'old_queue_route_changed:'+eid)
    require(len(qr)==len(q['exercises'])==len(set(q['eligible_exercise_ids']))==q['prepared_count']==q['eligible_count'],'queue_counts')
    evidence=b.load(EVIDENCE)
    live_evidence=b.source_evidence(s,EQUIPMENT_IDS)
    source_keys=['exercise_id','catalog_record_sha256','manifest_record_sha256','source_dataset_id','original_dataset_record_sha256','original_dataset_english','supplementary_exact_ID_fields']
    for a,c in zip(evidence['records'],live_evidence['records']):
        for k in source_keys:require(a[k]==c[k],'source_evidence_mismatch:'+a['exercise_id']+':'+k)
    seen=[];byid={}
    for bi,path in enumerate(BATCHES):
        d=b.load(path);require(d['exercise_count']==len(d['exercises'])==10,'batch_count:'+path)
        require(d['execution_order']==bi+1 and d['status']=='ready','batch_route:'+path)
        require(d['exercise_ids']==[r['exercise_id'] for r in d['exercises']],'batch_ID_list:'+path)
        for r in d['exercises']:
            eid=r['exercise_id'];seen.append(eid);byid[eid]=r
            require(counter[eid]==1,'missing_or_duplicate_catalog_ID:'+eid)
            for k,v in base.fields_for_id(eid,s).items():require(r.get(k)==v,'catalog_field_mismatch:'+eid+':'+k)
            require(conflict(eid,s,assignments,True) is None,'live_conflict:'+eid+':'+str(conflict(eid,s,assignments,True)))
            payload=r['prompt_payload']
            try:require(json.loads(r['generation_prompt'].split('\n',1)[1])==payload,'prompt_payload_mismatch:'+eid)
            except Exception:errors.append('invalid_prompt_payload:'+eid)
            require(base.sha(r['generation_prompt'].encode())==r['prompt_sha256'],'prompt_hash:'+eid)
            require(payload['identity_do_not_render_as_text']['exercise_id']==eid,'prompt_ID:'+eid)
            require(payload['identity_do_not_render_as_text']['name']==r['name'],'prompt_name:'+eid)
            for k in ['source_english','equipment','primary_muscle','secondary_muscles']:require(payload['exact_catalogue_source'][k]==r[k],'prompt_source:'+eid+':'+k)
            require(payload['selected_render_scene']==r['scene'],'scene_payload:'+eid)
            if eid in prepared:
                require(r['generation_prompt']==prepared[eid]['generation_prompt'],'ready_prompt_changed:'+eid)
            else:require(r['scene']==b.n.prior.scene(eid,SCENES[eid],b.CAMERA),'equipment_scene_changed:'+eid)
            require(r['human_reference']['sha256']==s['reference_sha256'],'reference_hash:'+eid)
            for f in r['approved_style_files']:require(b.sha(f['path'])==f['sha256'],'style_file_hash:'+eid)
            primary=r['primary_muscle'];style=payload['style']
            require(style['version']==r['style_version'],'style_version:'+eid)
            if primary in ['full_body','cardio','other']:require(style['primary_highlight']['hex'] is None and r['style_version']==b.NEUTRAL_VERSION,'neutral_primary:'+eid)
            else:require(style['primary_highlight']['hex']=='#F26445','specific_primary:'+eid)
            require(style['secondary_highlight']['intensity_fraction']==[0.4,0.5],'secondary_intensity:'+eid)
            require(r['planned_png_path']==f'{CLOUD}/{d["batch_id"]}/{eid}/attempt-1.png','cloud_path:'+eid)
            require(r['planned_git_png_path']==f'{GIT}/{d["batch_id"]}/{eid}/attempt-1.png','git_path:'+eid)
            require(qr[eid]['batch_id']==d['batch_id'] and qr[eid]['assigned_generator']==ROLE,'queue_route:'+eid)
            require(r['attempts']==0 and r['user_review'] is None and r['result_path'] is None,'preparation_result_state:'+eid)
    require(len(seen)==len(set(seen))==30,'duplicate_or_missing_new_ID')
    require(reg['assignment_count']==len(reg['assignments'])==1 and reg['assignments'][0]['exercise_ids']==seen,'single_assignment')
    manifest=b.load(MANIFEST);mr=[r for d in manifest['batches'] for r in d['exercises']]
    require([r['exercise_id'] for r in mr]==seen,'manifest_IDs')
    for r in mr:
        for k in ['prompt_sha256','planned_png_path','planned_git_png_path','style_version','source_catalog_sha256']:require(r[k]==byid[r['exercise_id']][k],'manifest_field:'+r['exercise_id']+':'+k)
    require(q['current_blocked_ids']==b.load(BLOCKED)['exercise_ids'],'blocked_records_unchanged')
    output={'status':'failed' if errors else 'passed','exercise_count':30,'batch_count':3,'generator_count':1,'errors':errors,'live_commits':s['commits'],'catalog_ID_count':451,'language_blocks':4448,'PNG_pixels_reviewed':False,'generation_calls':0}
    if errors: raise ValueError(json.dumps(output,ensure_ascii=False))
    return output

def finalize_validation(s):
    result=check(s);report=b.load(CHECK);report.update(result,checked_at=now());b.save(CHECK,report);return result

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--prepare',action='store_true');parser.add_argument('--check',action='store_true');parser.add_argument('--refresh-validation',action='store_true');parser.add_argument('--fetch',action='store_true');args=parser.parse_args()
    if args.fetch:b.fetch_heads()
    snapshot=b.n.snapshot()
    if args.prepare:prepare(snapshot)
    result=finalize_validation(snapshot) if args.prepare or args.refresh_validation else check(snapshot)
    print(json.dumps(result,ensure_ascii=False,indent=2))
