#!/usr/bin/env python3
"""Thirty additional exact-ID tasks for the existing single worker; no generation.

Reuse the previous round's extraction, prompt payload and read-only validators,
with new paths/scenes. All older batches, assignments and manifests are frozen.
"""
import argparse
import copy
import json
import prepare_agent03_single_generator as p

b=p.b
base=p.base
ROOT=p.ROOT
ROUND='agent-03-single-generator-next30-2026-10-03'
SCENES={
 'standing-calf-raise-machine':('Bilateral heel-rise endpoint','Stand upright under shoulder pads, knees softly unlocked and torso still; both heels raised with ankles tracking vertically.','Both hands wrap the prescribed stability handles.','Standing calf machine with shoulder pads, fixed support handles and footplate; both forefeet supported on footplate, heels free to rise. No seated knee-pad machine.','Extend both ankles to lift heels/body and machine shoulder load; lower slowly without knee-driven momentum.'),
 'lat-pulldown-machine':('Lever handles drawn to upper chest','Seated upright, knees secured below pads, both feet flat, chest lifted with natural spine curve; elbows draw down toward ribs.','Underhand/supinated paired handles slightly wider than shoulder width.','LEVER pulldown, seat and thigh/knee pads, both feet on floor; selected dataset 0673 equipment explicitly leverage machine. No cable bar or band substitution.','Pull overhead lever handles toward chest in front of face; return to extended arms without torso swing.'),
 'vertical-traction-machine':('Underhand lever-pull contraction','Seated with thighs below pads and feet grounded, upright braced torso; elbows toward ribs, handles near upper chest.','Underhand paired handles slightly wider than shoulders.','Compatible LEVER reverse-grip traction station, seat, thigh pads and moving lever handles; dataset 0673 corroborates this exact ID. No pulley-bar substitute.','Handles move down toward upper chest and return overhead; torso stays upright and no behind-neck pull.'),
 'torso-rotation-machine':('Controlled rightward torso rotation','Seated upright against backrest, pelvis stable below thigh pads and feet grounded; ribs/upper torso rotate to right within comfortable range.','Both hands hold the prescribed handles at chest height; hands and upper support travel with torso, no isolated arm pull.','Seated torso-rotation station with seat/thigh pads anchoring pelvis, rotating upper-body back support and chest-height handles. Standard compatible construction, no brand or load-type claim.','Rotate torso right against resistance while hips remain fixed; return to center. One rightward phase only.'),
 'biceps-curl-cable-machine':('Bilateral supinated curl near top','Stand tall facing station, feet shoulder-width, elbows beside ribs and upper arms stationary; forearms curled toward shoulders. Standing option is explicit in catalogue and exact dataset.','Both hands grasp one compatible cable handgrip attachment palms up; no rope hammer grip or preacher support. Attachment brand/shape is not claimed beyond a graspable shared handle.','One low cable pulley in front, cable taut to attachment; both feet on floor, no bench.','Elbow flexion lifts low cable attachment toward shoulders; controlled lowering with upper arms fixed.'),
 'hammer-curl-cable-machine':('Neutral rope curl near shoulders','Standing upright, knees soft, torso steady and upper arms beside ribs; elbows bent bringing rope to shoulder level.','One end of rope per hand, NEUTRAL palms facing each other. Dataset ambiguous word underhand is qualified by explicit palms-facing-each-other instruction and exact-ID English neutral grip.','Rope attachment on low cable pulley in front, both feet grounded; no supinated straight-bar attachment.','Flex elbows while upper arms remain stationary; lower rope under tension.'),
 'rope-cable-curl-machine':('Rope curl controlled contracted phase','Stand tall facing low pulley, elbows still at sides and wrists neutral; rope ends near shoulders.','Both ends of ONE rope held with neutral palms-facing-each-other grip.','Low cable pulley and rope attachment, both feet on floor, no dumbbells or bar.','Curl rope toward shoulders with elbow flexion, then lower under control without driving elbows forward.'),
 'triceps-pressdown-machine':('V-bar pressdown lower endpoint','Stand facing station with feet shoulder-width and knees soft; upper arms fixed at ribs, elbows extended but not forcefully locked.','Overhand grip on the two sides of ONE V-bar, as explicitly described in catalogue/dataset.','High pulley above body, one cable descending to V-bar in front; feet grounded.','Extend elbows to press V-bar toward thighs/floor, then allow controlled elbow flexion; no whole-body lean.'),
 'triceps-pushdown-machine':('V-bar pushdown extended-arm endpoint','Upright facing high pulley, knees soft, elbows beside ribs and shoulders down; hands at lower endpoint.','Overhand V-bar grip, one hand on each end; exact-ID muscles preserved independently of triceps-pressdown ID.','High cable pulley and V-bar, both feet on floor; no rope or seated lever-dip substitution.','Extend both elbows downward while upper arms stay fixed; controlled return.'),
 'reverse-grip-triceps-pushdown-machine':('Supinated pushdown lower endpoint','Stand facing station, trunk braced, elbows close to ribs, upper arms stationary; elbows nearly straight at lower endpoint.','UNDERHAND palms-UP grip on one straight bar, hands shoulder-width per exact dataset.','Straight bar attached to HIGH pulley, both feet grounded; no V-bar or overhand substitution.','Push bar down by elbow extension, then return slowly without upper-arm movement.'),
 'straight-arm-lat-pulldown-cable-machine':('Bar at thighs, shoulder-extension endpoint','Stand facing station with feet shoulder-width, braced ribs and shoulders down; arms nearly straight with elbows softly unlocked, bar near thighs.','Overhand grip on ONE straight bar, palms down.','High pulley with straight-bar attachment and both feet on floor; no seated thigh pad or lower pulley.','Shoulder extension sweeps bar down to thighs with nearly fixed elbows; return overhead under control. Do not turn into triceps elbow-extension pushdown.'),
 'reverse-grip-lat-pulldown-cable-machine':('Cable bar at upper chest','Seated on prescribed seat, feet grounded, back straight with only slight rearward torso lean; elbows down beside ribs, bar in front of upper chest.','Underhand/supinated pulldown bar, slightly wider than shoulder width.','HIGH cable pulley with one pulldown bar over seated body; seat and compatible stable support. No lever-handles or band substitute; no invented required knee-pad contact absent source.','Pull bar from overhead toward chest and return under control; no behind-neck path.'),
 'low-cable-fly-crossovers-machine':('Upward/inward fly with hands crossing slightly in front of chest','Stand centered between low pulleys, feet shoulder-width and knees soft, torso braced; elbows keep a small bend as arms converge upward in front of chest.','One handle per hand, overhand grip as exact dataset prescribes; no elbow-driven press.','Two LOW lateral pulleys, one cable/handle to each hand, both feet on floor. Cables remain attached to corresponding sides and clear of body.','Sweep both handles upward and inward until they slightly cross in front of chest, then reverse the wide arc; one crossing phase, not a montage.'),
 'seated-cable-row-bar-grip-machine':('Straight bar drawn toward lower ribs','Seated upright without chest-pad support, feet on footrests and knees slightly bent; elbows behind torso and shoulders relaxed.','Overhand grip on ONE straight bar specified by exact-ID description.','LOW seated-row pulley ahead, straight bar, seat and footrests; no added chest pad or lever machine.','Pull bar horizontally toward lower ribs and extend arms on return without torso jerk. Generic optional chest-pad cue/mistake does not add a pad to this explicitly upright source variant.'),
 'seated-cable-row-bar-wide-grip-machine':('Wide row bar toward lower chest','Seated with feet flat on footrests, knees soft and back straight; slight forward hip lean as stated, elbows drawn back, handle near lower chest.','WIDE OVERHAND grip on ONE straight bar, palms down.','Low seated-row cable pulley, straight bar, seat and footrests; torso upright/controlled, no invented chest pad.','Pull handle to lower chest, squeeze shoulder blades, then lengthen arms under control; no pad-dependent posture added by generic optional cue.'),
 'face-pull-machine':('Rope at forehead with hands apart','Standing braced after stepping back; elbows high and traveling behind torso, hands separated beside forehead during controlled external rotation, shoulders down.','Both hands wrap the separate ends of ONE rope; keep rope ends apart beside face.','Cable at FACE height with rope attachment, feet on floor; cable runs forward from rope to pulley, no dumbbells or low-pulley row.','Pull rope toward forehead and rotate hands apart; return slowly with ribs stacked, not a chest-level row.'),
 'standing-y-raise-cable-machine':('Y-shaped raised-arm endpoint','Stand centered between low cables, trunk braced, arms raised forward/outward above shoulder height into Y; shoulders remain down and ribs stacked.','One handle per hand, THUMBS POINT UP as exact-ID cue specifies.','Two LOW cable pulleys and separate handles, both feet grounded; no bench or unsupported bands.','Raise both arms forward/outward diagonally to Y, then lower to sides without shrugging or lumbar arch.'),
 'cable-core-pallof-press-machine':('Hands pressed straight forward, anti-rotation hold','Stand sideways to left chest-height pulley, feet shoulder-width, hips/ribs square facing forward; both arms extended in front of sternum without turning toward station.','Both hands together around ONE cable handle; no wide two-handle grip.','One pulley at CHEST height to left of body, taut cable to shared handle; feet planted and body clear of station. No attachment-specific D/rope claim beyond catalogue handle.','Press handle straight forward from sternum while resisting cable rotation; return to sternum without changing pelvis/rib orientation.'),
 'cable-pull-through-machine':('Neutral-spine hip-hinge lower phase','Stand facing AWAY from low station, feet shoulder-width, knees softly bent; hips back and torso hinged with neutral spine, hands between legs, no deep squat.','Both hands hold the two ends of ONE rope attachment, confirmed by exact dataset.','LOW pulley BEHIND body, rope/cable travels between legs; feet grounded and cable path clear.','Hinge hips back allowing rope between legs; drive hips forward to stand tall without arm curl or backward lean.'),
 'single-arm-cable-crossover-machine':('Right hand across chest to opposite midline','Stand beside LEFT chest-height pulley with staggered feet, right far arm sweeping across chest, elbow softly bent and trunk facing forward without rotation.','Right hand wraps the prescribed single handle; left hand relaxed, not assisting or holding another attachment.','ONE pulley at CHEST height on left, one handle in RIGHT/far hand, both staggered feet grounded; no additional cable or bench.','Start right arm open beside body and sweep handle across chest toward left/opposite midline; return along same arc.'),
 'seated-chest-flys-cable-machine':('Hands meet in front of sternum','Sit centered between chest-height pulleys on simple compatible seat, torso upright, feet grounded; both arms forward at chest level with small constant elbow bend.','One handle firmly held in each hand, both hands meet in front of sternum; no additional attachment shape or unprescribed grip rotation specified.','TWO chest-height lateral pulleys, separate handles, simple seat; no pec-deck arm pads or added chest support.','Sweep both handles forward in matching wide arcs until hands meet, then reverse to gentle chest stretch; no pressing elbow extension.'),
 'bench-press-smith-machine':('Guided bar just above chest, lower endpoint','Supine on FLAT bench, head/back/pelvis supported and feet planted, elbows controlled near torso; wrists stacked under bar.','Overhand guided bar slightly wider than shoulder width; closed hands maintain secure bar contact.','Smith frame with bar attached to TWO guide rails, flat bench positioned under bar, feet on floor. Moving bar remains mechanically connected to rails.','Lower guided bar toward chest without bounce; press along guide path to extended arms; no free-barbell substitute.'),
 'bent-over-row-smith-machine':('Guided bar drawn toward lower ribs','Stand feet hip-width per catalogue, knees softly bent, torso held in fixed neutral hip hinge; elbows behind torso, bar close to lower ribs.','Overhand Smith bar slightly wider than shoulder width, confirmed by same-ID dataset.','Smith frame, moving bar attached to rails, both feet grounded, no chest pad or bench; torso stays hinged throughout.','Pull guided bar toward lower ribs and lower until arms lengthen, no standing shrug or torso jerk.'),
 'deadlift-smith-machine':('Standing tall at controlled lockout','Stand upright with hips/knees extended, braced neutral spine and shoulders relaxed; bar close to front thighs over mid-foot, no backward lean.','Overhand guided bar slightly wider than shoulder width, as selected dataset states.','Smith frame with moving bar attached to guide rails, both feet under body hip-width; no free bar, block or invented floor-start height.','Hip/knee extension lifts guided bar close to body, reverse hip hinge to lower. Show upper lockout phase only; setup height is not inferred from generic deadlift name.'),
 'incline-bench-press-smith-machine':('Guided bar near upper chest on incline','Back against bench set at 30 degrees, within exact source 30–45 range; pelvis/head supported and feet planted, elbows slightly tucked and wrists stacked.','Overhand guided bar slightly wider than shoulder width.','Smith moving bar connected to rails, bench at SOURCE-PERMITTED 30-degree incline and both feet on floor. No free barbell or lever-handles.','Lower bar to upper chest and press along rails; one lower phase, no bounce or lumbar arch.'),
 'overhead-press-smith-machine':('Standing press near overhead extension','Stand feet shoulder-width with knees softly bent, torso braced and ribs down; hands above head, elbows nearly extended, no backward lean.','Overhand guided bar slightly wider than shoulder width, palms forward.','Smith frame with moving guided bar attached to rails, both feet on floor; no seat/back pad or free bar.','Press guided bar from shoulder level to overhead and return under control; compatible guide/body layout must keep bar clear of face.'),
 'romanian-deadlift-smith-machine':('Controlled hip-hinge lower endpoint','Stand feet hip-width, knees softly bent but not deep squatting; hips pushed back, neutral long spine, guided bar close to thighs and shins within hamstring-controlled range.','Overhand Smith bar as explicitly prescribed; hands remain stable on bar.','Smith frame with moving bar on rails, both feet grounded; no blocks, bench or straps added.','Hip hinge lowers bar close to legs until hamstrings stretch before spine rounds; drive hips forward to stand, no floor-reset deadlift.'),
 'shrug-smith-machine':('Vertical shoulder-elevation endpoint','Stand feet shoulder-width with knees soft, arms straight and torso still; shoulders elevated toward ears, guided bar held in front of thighs.','Overhand guided bar slightly wider than shoulder width.','Smith frame with moving bar attached to rails, both feet on floor; no seat or support pad.','Elevate shoulders vertically with elbows straight, then lower quietly; no upright-row elbow bend or shoulder rolling.'),
 'squat-smith-machine':('Controlled squat near parallel','Smith bar across upper back/traps, torso braced, feet shoulder-width and heels grounded; hips/knees bent until thighs approach parallel, knees track toes.','Both hands grip guided bar slightly wider than shoulders, stabilizing upper-back contact.','Smith frame with bar guided on rails and across upper back; both feet remain in chosen planted stance. No free-bar walk-out or horizontal bar translation.','Bend hips/knees to descend and extend to stand. Exact catalogue instructions specify Smith-guided squat; incompatible original dataset walk-out boilerplate is recorded, not performed.'),
 'standing-calf-raise-smith-machine':('Both heels raised','Stand upright with Smith bar across upper back, feet shoulder-width and toes forward; forefeet on FLOOR, heels raised, knees softly unlocked.','Both hands hold guided bar for stability.','Smith frame with moving bar attached to rails, bar across upper back, both forefeet on level floor as exact instructions prescribe. No invented step/block or ankle-level bar.','Extend both ankles to raise heels and body, then lower heels to floor under control without knee momentum.'),
}
assert len(SCENES)==30

def configure():
    p.ROUND=ROUND
    for attr,prefix,suffix in [('REG','data/assignments/','.json'),('MANIFEST','data/manifests/','/generator-single.json'),('EVIDENCE','data/audits/','-technique.json'),('ERRORS','data/audits/','-source-errors.json'),('CHECK','data/audits/','-validation.json'),('HANDOFF','docs/','-handoff.md'),('MESSAGE','docs/','-message.md')]:
        setattr(p,attr,prefix+ROUND+suffix)
    p.BATCHES=[p.PREFIX+f'{i:03}.json' for i in [31,32,33]]
    p.CLOUD=f'/workspace/exercise-image-results/{ROUND}/{p.ROLE}'
    p.GIT=f'assets/exercises/pending/{ROUND}/{p.ROLE}'
    p.SCENES=SCENES
    p.EQUIPMENT_IDS=list(SCENES)
    p.SOURCE_ERRORS={'squat-smith-machine':True}

READ_BUT_BLOCKED={
 'reverse-curl-cable-machine':'Catalog describes palms-down overhand reverse curl; selected dataset explicitly says underhand. Exact grip conflict requires source confirmation.',
 'standing-cable-glute-kickbacks-machine':'Catalog faces machine with a hand support; selected dataset says face away, changing cable direction. Do not choose by name.',
 'cable-twist-down-to-up-machine':'Catalog sideways outside-hip-to-opposite-shoulder; dataset facing station waist-height start. Initial orientation/anchor need exact variant confirmation.',
 'cable-twist-up-to-down-machine':'Catalog high-to-opposite-hip diagonal; original dataset only horizontal chest-height rotations. Match alone cannot confirm trajectory.',
 'hip-adduction-cable-machine':'Catalog side-on ankle-cuffed standing sweep, generic pelvis-against-pad cue, and dataset facing station need support/orientation reconciliation.',
 'single-leg-standing-calf-raise-machine':'Catalog description other foot on block versus instructions other foot clear; original dataset places Smith bar above ankles and describes bilateral rise. Incompatible support/loading geometry.',
 'ski-erg-machine':'Catalog standing hip-hinge pull versus source seated footrest setup. Name/equipment match does not confirm standing variant.',
 'chest-dip-assisted-machine':'Kneeling assistance confirmed, but source palm-down grip needs reconciliation with exact parallel-support hand geometry; not assigned on a guessed grip.',
 'bench-press-cable-machine':'Catalog supine flat bench between low pulleys versus original standing chest-height cable press. This is not merely a construction brand choice.',
 'squat-row-machine':'Catalog neutral rope grip with partial rise before pull versus original overhand squat row. Combined phase/grip not silently selected.',
 'single-arm-lateral-raise-cable-machine':'Description beside low pulley versus instructions/dataset facing station; starting cable/hand/body orientation not resolved here.',
}

def prepare(s):
    assert base.git('branch','--show-current').decode().strip()==base.BRANCH
    for path in p.BATCHES:
        assert not any(path in paths for paths in s['trees'].values()),'Occupied batch number: '+path
    for path in p.BATCHES+[p.REG,p.MANIFEST,p.EVIDENCE,p.ERRORS,p.CHECK,p.HANDOFF,p.MESSAGE]:
        assert not (ROOT/path).exists(),'Never overwrite '+path
    frozen=b.n.protected_files()
    oldq=b.load(base.QUEUE_PATH)
    assignments=b.actual_assignments(s)
    ids=list(SCENES)
    for eid in ids:
        assert eid not in oldq.get('current_equipment_blocked_ids',[]),'Unresolved equipment question: '+eid
        assert p.conflict(eid,s,assignments) is None,(eid,p.conflict(eid,s,assignments))
    evidence=b.source_evidence(s,ids)
    evidence.update(prepared_at=p.now(),audited_commits=s['commits'],confirmation_rule='Exact-ID English description/instructions/cues/mistakes/safety and actual selected dataset instruction_steps were read. No confirmation by ID/name/thumbnail alone.',photos_or_video_downloaded=False,images_reviewed=False,
                    read_but_not_selected=[dict(base.fields_for_id(eid,s),status='blocked',reason=reason,new_assignment=False) for eid,reason in READ_BUT_BLOCKED.items()])
    for r in evidence['records']:
        eid=r['exercise_id'];r['selected_scene']=b.n.prior.scene(eid,SCENES[eid],b.CAMERA)
        r['technique_confirmation']='Actual same-ID written posture, grip, supports and movement, plus original dataset where present; no external muscle targets.'
        r['permitted_illustration_choices']='Select one documented phase/side and compatible unbranded geometry; do not treat scene choices as user approval or catalogue edits.'
        if eid in ['biceps-curl-cable-machine','hammer-curl-cable-machine']:r['variant_selection']='Standing option is explicitly permitted by English and corroborated by original dataset. This is selection of a permitted posture, not repair of a contradictory exercise.'
        if eid=='incline-bench-press-smith-machine':r['variant_selection']='30 degrees selected within exact 30–45-degree source range as illustration choice; not a new technique claim.'
        if eid in ['seated-cable-row-bar-grip-machine','seated-cable-row-bar-wide-grip-machine']:r['variant_selection']='English explicitly permits torso upright; dataset prescribes seated upright row. Optional chest-support boilerplate does not require adding an absent chest pad.'
    evidence['blocked_source_records']=b.source_evidence(s,list(READ_BUT_BLOCKED))['records']
    b.save(p.EVIDENCE,evidence)
    squat=next(r for r in evidence['records'] if r['exercise_id']=='squat-smith-machine')
    bad=squat['original_dataset_english'][4]
    assert 'stepping back' in bad
    b.save(p.ERRORS,{'schema_version':1,'catalog_sha256':s['catalog_sha256'],'catalog_modified':False,
                     'records':[{'exercise_id':'squat-smith-machine','source_path':p.EVIDENCE,'source_field':'records[exercise_id="squat-smith-machine"].original_dataset_english[4]','exact_value':bad,
                                 'problem':'Free-bar walk-out boilerplate is mechanically incompatible with the Smith bar remaining on guide rails.',
                                 'resolution':'Use exact catalogue Smith-bar instructions: planted stance, guided bar across upper back, hip/knee flexion then extension. No walk-out or horizontal translation. Dataset original kept verbatim.',
                                 'resolution_kind':'exact_catalogue_and_compatible_mechanics_confirmation','user_approval_of_source_edit':False}],
                     'variant_scope_notes':[{'exercise_id':eid,'field':'/content/en/common_mistakes/0','exact_value':s['by_id'][eid]['content']['en']['common_mistakes'][0],
                                           'note':'Conditional chest-pad boilerplate is not applicable to the explicitly selected upright seated-row variant; do not add a pad.'} for eid in ['seated-cable-row-bar-grip-machine','seated-cable-row-bar-wide-grip-machine']],
                     'prior_ledgers_unchanged':[b.ERRORS,'data/audits/agent-03-single-generator-2026-10-03-source-errors.json']})
    batches=[]
    for i,path in enumerate(p.BATCHES):
        bid=path.rsplit('/',1)[1][:-5];group=ids[i*10:(i+1)*10]
        rows=[p.route(p.make_equipment_row(eid,s,evidence),bid,s) for eid in group]
        for row in rows:
            row['technique_resolution']['illustration_choices_are_not_user_approvals']=True
            row['prompt_payload']['technique_resolution']=copy.deepcopy(row['technique_resolution'])
            row['generation_prompt']='Create exactly ONE square 1024x1024 transparent PNG of this exact exercise and ONE selected phase. Metadata must never appear as image text.\n'+json.dumps(row['prompt_payload'],ensure_ascii=False,sort_keys=True,indent=2)
            row['prompt_sha256']=base.sha(row['generation_prompt'].encode())
        doc={'schema_version':1,'batch_id':bid,'status':'ready','exercise_count':10,'exercise_ids':group,'exercises':rows,'source_branch':base.BRANCH,'generator':p.ROLE,'execution_branch':p.WORKER,
             'assignment_registry_path':p.REG,'execution_order':i+1,'phase':'equipment_tail','catalog_sha256':s['catalog_sha256'],'audited_commits':s['commits'],
             'generation_calls':0,'handoff_path':p.HANDOFF,'manifest_path':p.MANIFEST,'live_recheck_before_every_call':True}
        b.save(path,doc);batches.append(doc)
    tasks=[r for d in batches for r in d['exercises']]
    reg={'schema_version':1,'assignment_id':ROUND,'created_at':p.now(),'source_branch':base.BRANCH,'source_base_commit':s['commits']['HEAD'],'catalog_sha256':s['catalog_sha256'],
         'status':'ready','assignment_count':1,'exercise_count':30,'batch_paths':p.BATCHES,
         'assignments':[{'generator':p.ROLE,'execution_branch':p.WORKER,'status':'assigned','exercise_count':30,'exercise_ids':ids,'batch_paths':p.BATCHES,'batch_ids':[d['batch_id'] for d in batches],
                         'execution_order':[1,2,3],'manifest_path':p.MANIFEST,'handoff_path':p.HANDOFF}],
         'continuation_of_single_worker':True,'prior_assignment_path':'data/assignments/agent-03-single-generator-2026-10-03.json','prior_manifest_unchanged':True,
         'existing_A_B_assignments_unchanged':True,'supersedes_other_agents':False,'generation_calls_by_preparer':0,'audited_commits':s['commits'],
         'equipment_groups':{'specialized_machine':4,'cable_station':17,'smith_machine':9},'results_git_root':p.GIT,'results_cloud_root':p.CLOUD,
         'scope_authorization':'User requests next three batches; previous explicit instruction: one generator, equipment at end. No image generation by preparer.',
         'validation_path':p.CHECK,'remaining_technique_blocked_path':p.BLOCKED,'remaining_technique_blocked_ids':b.load(p.BLOCKED)['exercise_ids'],
         'additional_equipment_blocked_evidence_path':p.EVIDENCE,
         'scope_limit':'All available pushed remote heads read; unpushed outputs/ongoing calls in other cloud tasks may be inaccessible. Recheck before every call.'}
    b.save(p.REG,reg)
    b.save(p.MANIFEST,{'schema_version':1,'manifest_id':ROUND,'generator':p.ROLE,'execution_branch':p.WORKER,'assignment_path':p.REG,'source_branch':base.BRANCH,
                       'status':'ready_not_started','exercise_count':30,'generation_calls':0,'user_review_policy':'pending on result creation until explicit user approval',
                       'quota_rule':'On first generator quota/rate-limit error save failure and history, push checkpoint and stop without repeat calls.',
                       'batches':[{'batch_id':d['batch_id'],'batch_path':path,'status':'ready','exercise_count':10,
                                   'exercises':[{'exercise_id':r['exercise_id'],'name':r['name'],'status':'not_started','attempts':0,'attempt_history':[],'user_review':None,'technical_check':None,'agent_visual_review':'not_performed',
                                                 'result_path':None,**{k:r[k] for k in ['planned_png_path','planned_git_png_path','source_catalog_sha256','style_version','prompt_sha256']}} for r in d['exercises']]} for path,d in zip(p.BATCHES,batches)]})
    q=copy.deepcopy(oldq);qr={r['exercise_id']:r for r in q['exercises']}
    for r in tasks:
        eid=r['exercise_id'];assert eid not in qr,'No reassignment of existing queue task: '+eid
        route={k:copy.deepcopy(r[k]) for k in ['exercise_id','name','equipment','primary_muscle','secondary_muscles','source_catalog_sha256','source_catalog_record_sha256','source_english_sha256','status','assigned_generator','batch_id','prompt_prepared','style_version','assignment_registry_path']}
        route['current_task_path']=p.PREFIX+r['batch_id'].removeprefix('agent-03-others-')+'.json'
        q['exercises'].append(route);q['eligible_exercise_ids'].append(eid)
    q['batch_paths'].extend(p.BATCHES)
    q.update(updated_at=p.now(),eligible_count=len(q['eligible_exercise_ids']),prepared_count=len(q['eligible_exercise_ids']),latest_launch_ids=ids)
    q['single_generator_followup']={'assignment_path':p.REG,'batch_paths':p.BATCHES,'exercise_count':30,'generator':p.ROLE,'execution_branch':p.WORKER,'handoff_path':p.HANDOFF,'equipment_groups':reg['equipment_groups'],'older_tasks_unchanged':True,'generation_calls':0}
    q['current_assignment_snapshot']={'assignment_path':p.REG,'audited_commits':s['commits'],'exercise_count':30,'generation_calls':0}
    q['phase_plan']['latest_equipment_allocation_path']=p.REG
    q['current_equipment_blocked_ids']=list(READ_BUT_BLOCKED)
    q['current_equipment_blocked_count']=len(READ_BUT_BLOCKED)
    q['current_equipment_blocked_path']=p.EVIDENCE
    q['current_equipment_blocked_selector']='read_but_not_selected'
    q['phase_plan']['equipment_clarifications_path']=p.EVIDENCE
    q['phase_plan']['phase2_execution_gate']='Next three packs 031 then 032 then 033 belong to the SAME single worker. Old 028–030 tasks/history stay in original assignment/manifest; no reassignment or reset.'
    q['historical_fields_note']='Original exclusions and eligibility rules are past snapshots. Current ownership is read from existing assignments plus single_generator_preparation and single_generator_followup. Historical prepared_count is not current missing-PNG backlog.'
    b.save(base.QUEUE_PATH,q)
    with (ROOT/'.gitignore').open('a') as f:
        f.write('\n# Exact pending outputs for the same single worker, next three batches.\n')
        for r in tasks:f.write('!/'+r['planned_git_png_path']+'\n')
    b.save(p.CHECK,{'schema_version':1,'status':'pending_validation','protected_sha256':frozen,'previous_queue_routes_sha256':{r['exercise_id']:base.value_sha(r) for r in oldq['exercises']},
                    'source_base_commit':s['commits']['HEAD'],'catalog_sha256':s['catalog_sha256']})
    p.check(s)

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--prepare',action='store_true');parser.add_argument('--check',action='store_true');parser.add_argument('--fetch',action='store_true');parser.add_argument('--refresh-validation',action='store_true');args=parser.parse_args()
    configure()
    if args.fetch:b.fetch_heads()
    snapshot=b.n.snapshot()
    if args.prepare:prepare(snapshot)
    queue=b.load(base.QUEUE_PATH)
    assert not(set(SCENES)&set(queue.get('current_equipment_blocked_ids',[]))),'Selected equipment is still blocked'
    assert b.load(p.EVIDENCE)['blocked_source_records']==b.source_evidence(snapshot,list(READ_BUT_BLOCKED))['records'],'Blocked source evidence mismatch'
    result=p.finalize_validation(snapshot) if args.prepare or args.refresh_validation else p.check(snapshot)
    print(json.dumps(result,ensure_ascii=False,indent=2))
