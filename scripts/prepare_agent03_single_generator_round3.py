#!/usr/bin/env python3
"""Prepare exact-ID batches 034–036 (10,10,9) for the existing single worker.

No image generation. --check is read-only on the preparation branch.
Older jobs and catalog/shared progress are protected byte-for-byte.
"""
import argparse
import copy
import json
import collections
import prepare_agent03_single_generator as p
import prepare_agent03_single_generator_followup as previous
b=p.b
base=p.base
ROOT=p.ROOT
ROUND='agent-03-single-generator-round3-2026-10-03'
conflict=previous.conflict
SCENES={'back-extension-hyperextension-machine': ['Neutral return endpoint',
                                           'Torso and straight legs form one neutral line, upper thighs '
                                           'supported and feet secured; head aligned, no lumbar '
                                           'hyperextension.',
                                           'Arms crossed over chest, an explicit dataset option.',
                                           'Compatible static hyperextension bench, upper-thigh/hip pad and '
                                           'secured feet. No moving seated lumbar pad or external weight. '
                                           'Bench layout follows these contacts without a numeric angle '
                                           'claim.',
                                           'Hip hinge lowers torso and raises it only into line with legs.'],
 'chest-supported-t-bar-row-machine': ['Supported row contraction',
                                       'Sternum stays on angled chest pad, neutral trunk held in supported '
                                       'hip hinge, feet grounded; elbows drawn behind ribs.',
                                       'Both hands close around the prescribed paired handles; preserve '
                                       'wrist alignment without claiming a source-specific palm orientation.',
                                       'Compatible chest-supported hinged T-bar row, sternum pad and '
                                       'grounded stance; no unsupported standing landmine substitution. '
                                       'Standard frame/pad layout is an illustration choice, not a newly '
                                       'asserted source posture.',
                                       'Pull handles toward lower ribs with scapular squeeze and chest '
                                       'fixed; lower slowly.'],
 'hip-thrust-machine': ['Hip-extension endpoint',
                        'Upper back on back support, both feet flat, knees tracking toes; hips extended only '
                        'until torso and thighs align.',
                        'Hands relaxed away from moving load; no working arm pull is prescribed.',
                        'Compatible machine hip thrust with back support and padded loading contact across '
                        'hips. PAD option selected from explicit belt-or-pad instruction; do not infer '
                        'stack, plate count or brand.',
                        'Drive through whole feet to extend hips against hip pad; lower pelvis under control '
                        'without lumbar arch.'],
 'iso-lateral-low-row-machine': ['Independent low-row contraction',
                                 'Seated with sternum on chest support, feet grounded, shoulders down; '
                                 'elbows close and back, handles near lower ribs.',
                                 'One closed hand on each prescribed independent handle, wrists aligned; no '
                                 'unsupported palm direction claim.',
                                 'Compatible seated low row, seat and chest support, two independently '
                                 'moving low-start handles; no shared bar.',
                                 'Pull each handle from low forward reach toward lower ribs, then extend '
                                 'arms without leaving chest support.'],
 'iso-lateral-row-machine': ['Chest-supported horizontal row contraction',
                             'Seated facing machine, sternum remains against pad as exact-ID safety note '
                             'requires, back neutral; elbows behind ribs.',
                             'Overhand grip on two independent handles confirmed by exact dataset.',
                             'Compatible lever row with independent handles, seat and chest pad. Chest '
                             'support is explicit in this ID safety note; no source claim of load type '
                             'beyond dataset lever.',
                             'Independent horizontal handles travel from reach toward ribs; return without '
                             'trunk jerk.'],
 'leg-press-machine': ['Two-leg press near extension',
                       'Seated with back on backrest, both feet shoulder-width on footplate, heels '
                       'supported; knees nearly straight, not locked.',
                       'Both hands hold prescribed handles beside seat.',
                       'Compatible sled leg press with seat/backrest, moving footplate and side handles. No '
                       'inferred rail angle, shoulder-squat pads or arm press.',
                       'Extend both knees/hips to push footplate away; controlled knee bend returns sled.'],
 'lying-leg-curl-machine': ['Prone curl contraction',
                            'Prone, hips and torso on pad, knees bent with both heels curling toward hips; '
                            'pelvis stays down.',
                            'Both hands hold stability handles, explicit dataset option.',
                            'Compatible prone leg-curl lever, padded contact behind lower legs above ankles, '
                            'supported hips/torso and stability handles.',
                            'Knee flexion curls posterior ankle lever upward toward hips; lower until knees '
                            'comfortably extended. Do not interpret generic elbow cues as working-arm '
                            'motion.'],
 'pendulum-squat-machine': ['Controlled lower squat phase',
                            'Back remains on pad, shoulders under pads, feet planted on footplate; '
                            'hips/knees bent with knees following toes, pelvis supported.',
                            'Hands relaxed outside moving linkage; no unprescribed working hand pull.',
                            'Compatible pendulum squat with back/shoulder pads, footplate and pivot-guided '
                            'moving support arc. Arc is explicit; no straight-rail substitution or '
                            'brand/load count.',
                            'Bend hips/knees along machine arc, then press whole feet to rise without knee '
                            'lock.'],
 'single-leg-press-machine': ['Right-leg press near extension',
                              'Seated against sled back pad; RIGHT whole foot on plate, right knee nearly '
                              'straight; left foot off moving plate, left leg bent clear of carriage as '
                              'nonworking scene choice.',
                              'No working hand grip prescribed; hands relaxed on thighs clear of sled.',
                              'Exact source 45-degree sled, back pad and footplate; only right foot loads '
                              'plate in this selected phase. Left leg clearance is a scene choice, not an '
                              'extra exercise instruction.',
                              'Right leg presses sled away and bends on return; no bilateral working phase '
                              'or arm press.'],
 'squat-machine': ['Supported carriage squat lower phase',
                   'Back on pad, shoulder pads loaded, both whole feet evenly planted; hips/knees bent, '
                   'knees track toes, pelvis remains supported.',
                   'Hands relaxed beside torso away from carriage; no unprescribed working grip.',
                   'Compatible shoulder-pad squat carriage on guided track, back pad and foot platform. '
                   'Straight guided carriage, not pendulum arc or Smith bar.',
                   'Bend hips/knees to lower supported carriage; press whole feet to rise without knee '
                   'lock.'],
 'triceps-extension-machine': ['Front/forehead lever-extension bent-elbow phase',
                               'Seated against back pad with feet planted, upper arms elevated forward and '
                               'stationary; elbows flexed, handles approach forehead without contact.',
                               'Overhand paired machine handles, wrists neutral, confirmed by dataset.',
                               'Compatible seated lever elbow-extension station with back pad and paired '
                               'handles. FRONT/FOREHEAD option selected from English alternatives and actual '
                               'dataset; no behind-head variant.',
                               'Only forearms rotate at elbows from forehead approach to straight forward '
                               'arms; keep shoulders and trunk still.'],
 'cycling-machine': ['One seated pedal stroke',
                     'Seated upright on stationary saddle, back neutral; right pedal down with knee softly '
                     'bent, left knee flexed, feet on pedals.',
                     'Hands rest neutrally on thighs as nonworking scene choice; no invented reciprocal arm '
                     'drive.',
                     'Compatible stationary bike with saddle and crank pedals, exact dataset specifies '
                     'seated bike. No elliptical standing platforms or lever-arm press despite broad source '
                     'equipment flag.',
                     'Continuous seated pedal circles, freeze one stroke; no second body.'],
 'elliptical-trainer-machine': ['One grounded elliptical stride',
                                'Standing upright on two full-foot pedals, one leg more extended and other '
                                'flexed; hands follow reciprocal moving handles, core braced.',
                                'Light closed grip on prescribed moving handles, no hanging bodyweight.',
                                'Compatible elliptical with grounded pedal linkage and reciprocal moving '
                                'handles, as actual dataset push/pull motion describes. No bike saddle or '
                                'treadmill belt.',
                                'Alternating pedal push and handle pull in one frozen stride; no airborne '
                                'phase.'],
 'cable-crunch-machine': ['Kneeling torso-flexion contraction',
                          'Kneel facing AWAY from high pulley, hips vertically above knees and stationary; '
                          'ribs curl toward pelvis, neck relaxed.',
                          'One rope end per hand beside/behind head, elbows out; hands hold but do not pull '
                          'head.',
                          'High pulley behind kneeling body, one rope attachment, knees on floor; no supine '
                          'scene. Exact instructions AND dataset confirm kneeling; contradictory supine '
                          'description recorded separately.',
                          'Flex trunk to bring ribs toward pelvis while hips stay over knees; return to '
                          'upright kneeling.'],
 'front-raise-cable-machine': ['Bilateral shoulder-height front raise',
                               'Stand tall, feet shoulder-width, arms raised forward to shoulder height with '
                               'soft elbows; ribs down, shoulders not shrugged.',
                               'Both hands overhand on one compatible shared cable handle, palms down as '
                               'dataset states; no invented rope or special bar shape.',
                               'Compatible cable attachment held in front of body, low frontal cable exit '
                               'resisting upward raise, both feet grounded. Low exit/layout is compatible '
                               'construction selection, not a source-provided numeric height.',
                               'Raise shared handle forward from thighs to shoulder height without swing or '
                               'lean; lower slowly.'],
 'lat-pulldown-close-grip-cable-machine': ['Close neutral handle at upper chest',
                                           'Seated tall, knees secured under pad and feet grounded; elbows '
                                           'down toward ribs, handle in front of upper chest.',
                                           'Close NEUTRAL grip explicitly selected from '
                                           'neutral-or-close-overhand options; palms face each other.',
                                           'High cable, seat and knee pad, one compatible close-grip '
                                           'attachment; no band or separate lever handles.',
                                           'Pull handle from overhead to upper chest and return without '
                                           'torso swing or behind-neck travel.'],
 'lateral-raise-cable-machine': ['Bilateral shoulder-height lateral raise',
                                 'Standing shoulder-width, trunk still; both arms straight but not forced '
                                 'into lock, raised out to sides parallel to floor.',
                                 'Overhand grip on prescribed two cable handles, one per hand.',
                                 'Compatible low cable exits resisting upward lateral raises, separate '
                                 'handles and feet grounded. Pulley/frame layout is unbranded compatible '
                                 'construction choice; no source claim of crossed-hand routing or numerical '
                                 'height.',
                                 'Raise handles laterally to shoulder level then lower under control; no '
                                 'machine arm-pad substitution.'],
 'overhead-triceps-extension-cable-machine': ['Overhead bent-elbow phase',
                                              'Stand facing AWAY from station, trunk braced, upper arms '
                                              'overhead stationary close to head; elbows bent with rope '
                                              'behind head.',
                                              'Both hands securely hold the two rope ends, wrists neutral; '
                                              'no unsupported palm-angle claim.',
                                              'HIGH pulley behind body with ONE rope; feet on floor, clear '
                                              'cable path behind head and outside limbs.',
                                              'Elbow extension raises rope overhead while upper arms stay '
                                              'still; controlled elbow bend returns rope behind head.'],
 'rear-delt-reverse-fly-cable-machine': ['Back-and-up fly contraction',
                                         'Standing centered, one step forward of low pulleys, knees soft, '
                                         'slight neutral hip hinge; arms out/back with small fixed elbow '
                                         'bend and shoulders down.',
                                         'Pronated palms-down D-handle in each hand, exact dataset grip.',
                                         'Two LOW pulleys and D-handles, both feet grounded. Frame behind '
                                         'the stepped-forward body gives cables forward/downward resistance; '
                                         'keep each cable outside torso. No unconfirmed crossed-hand '
                                         'reassignment.',
                                         'Pull arms back/up in reverse-fly arc with scapular squeeze; elbows '
                                         'keep fixed bend, no row.'],
 'rope-straight-arm-pulldown-machine': ['Rope ends at thighs',
                                        'Standing facing high station, ribs stacked; arms nearly straight '
                                        'with soft elbows, hands at thighs, shoulders down.',
                                        'Both rope ends held palms DOWN as exact dataset explicitly states; '
                                        'do not replace with a different attachment.',
                                        'Highest cable setting in front, one rope, feet shoulder-width '
                                        'grounded.',
                                        'Shoulder extension draws rope down to thighs with near-fixed '
                                        'elbows; return overhead, no elbow-driven pushdown.'],
 'shrug-cable-machine': ['Vertical shoulder-elevation endpoint',
                         'Standing facing station, feet shoulder-width, arms straight hanging in front; '
                         'shoulders lifted toward ears, torso motionless.',
                         'Overhand grip on two prescribed cable handles.',
                         'Compatible low frontal cable exits with separate handles opposing upward shoulder '
                         'elevation; feet grounded. Exit geometry is compatible construction choice, not a '
                         'quoted source height.',
                         'Elevate shoulders vertically without elbow flexion or rolling; lower quietly.'],
 'single-arm-cable-row-machine': ['Right handle at lower ribs',
                                  'Seated upright on bench facing station, feet flat, knees softly bent; '
                                  'right elbow close and behind ribs, shoulders down; left hand relaxed on '
                                  'thigh.',
                                  'Right hand closes around prescribed single handle, wrist aligned; no '
                                  'source-specific palm orientation asserted.',
                                  'Simple bench, feet on ground, one forward cable line opposing horizontal '
                                  'rib-directed pull. Functional exit layout is compatible construction '
                                  'choice; no chest pad added to explicitly upright variant.',
                                  'Pull right handle from forward reach to lower ribs with scapular '
                                  'retraction; extend arm slowly, no torso twist.'],
 'single-arm-curl-cable-machine': ['Right supinated curl near shoulder',
                                   'Stand facing station, feet shoulder-width, right elbow fixed beside '
                                   'torso; right forearm curled toward shoulder; left hand relaxed.',
                                   'Right single handle held UNDERHAND, palm up, exact source.',
                                   'LOW frontal pulley and one handle, feet grounded; no preacher bench or '
                                   'two-hand shared bar.',
                                   'Flex right elbow to curl handle then lower without shoulder drift.'],
 'single-arm-lat-pulldown-machine': ['Standing right-arm pull to ribs',
                                     'Stand facing station, feet shoulder-width, trunk braced; right elbow '
                                     'down close to body, hand near side ribs, left arm relaxed.',
                                     'Right single handle OVERHAND grip as exact dataset states.',
                                     'HIGH pulley in front, one cable/handle; standing feet grounded, no '
                                     'seat or kneeling support.',
                                     'Pull right arm from overhead to side ribs, then return controlled '
                                     'without torso swing.'],
 'triceps-extension-cable-machine': ['Forehead-directed bent-elbow phase',
                                     'Stand facing AWAY from high station, torso upright; upper arms '
                                     'elevated forward above torso and fixed, elbows pointing forward, rope '
                                     'near forehead without contact.',
                                     'Both rope ends held NEUTRAL, palms facing each other, per exact '
                                     'English.',
                                     'HIGH pulley behind body, rope and feet grounded; FACE-AWAY / FOREHEAD '
                                     'options explicitly selected from catalogue alternatives. Cable clears '
                                     'head/arms.',
                                     'Only elbows flex bringing rope toward forehead and extend forearms '
                                     'forward to straight arms; no behind-head overhead variant or shoulder '
                                     'swing.'],
 'triceps-kickback-cable-machine': ['Right elbow-extension endpoint',
                                    'Stand facing station with feet hip-width per catalogue, knees soft and '
                                    'trunk in neutral hip hinge; right upper arm at ribs, forearm extended '
                                    'behind; left hand relaxed on thigh.',
                                    'Right hand closes around prescribed single cable handle, wrist aligned; '
                                    'no unprescribed palm rotation.',
                                    'One forward cable line opposing backward forearm motion, feet grounded; '
                                    'compatible exit below working hand keeps taut line clear of torso. Exit '
                                    'geometry is construction choice, no bench or chest pad.',
                                    'Right elbow extends from about 90 degrees to straight arm behind body; '
                                    'return with upper arm still.'],
 'upright-row-cable-machine': ['Upper-chest controlled endpoint',
                               'Stand tall shoulder-width, elbows leading up/out with wrists below elbows; '
                               'shared handle near upper chest, no hip swing.',
                               'Overhand grip on one compatible shared cable handle; no unprescribed '
                               'attachment shape.',
                               'LOW frontal pulley and feet grounded; no dumbbell, rope claim or machine '
                               'chest pad.',
                               'Pull close to body from thighs to upper chest per English comfortable '
                               'endpoint. Dataset chin-level endpoint is not rendered; same upward '
                               'trajectory stopped at catalogue-permitted height.'],
 'decline-bench-press-smith-machine': ['Guided bar near chest on decline',
                                       'Supine on declined bench, head/back/pelvis supported, feet secured '
                                       'under foot pads, elbows controlled and wrists stacked; guided bar '
                                       'just above chest.',
                                       'Overhand Smith bar slightly wider than shoulder width, confirmed by '
                                       'actual dataset.',
                                       'Smith frame with bar attached to two guide rails, declined bench and '
                                       'prescribed foot pads. No invented numeric decline angle or free bar.',
                                       'Lower guided bar toward chest and press along rails; no bounce, '
                                       'free-bar walkout or weights set on floor.'],
 'hip-thrust-smith-machine': ['Controlled hip-extension endpoint',
                              'Upper back stays on bench edge as exact-ID cue states, pelvis off bench, feet '
                              'shoulder-width flat; hips extended to straight knees-to-shoulders line, no '
                              'lumbar arch.',
                              'Both hands steady Smith bar slightly wider than shoulders, exact '
                              'instructions.',
                              'Smith frame with guided bar across hips, upper-back bench support and feet on '
                              'floor; bar remains attached to rails. No free bar or unsupported shoulders.',
                              'Extend hips by driving feet until knees/hips/shoulders align; lower pelvis '
                              'under control, bench and feet remain fixed.']}
NEW_BLOCKED={'back-extension-machine': 'Catalogue hip-supported hinge versus dataset seated lumbar machine/rounded-back '
                           'start: confirm actual support and moving segment.',
 'back-extension-weighted-hyperextension-machine': 'External weight placement/grip is absent; do not invent '
                                                   'plate-on-chest or load behind head.',
 'belt-squat-machine': 'Hip belt is stated, but load attachment/anchor and compatible belt machine mechanism '
                       'are not defined.',
 'butterfly-pec-deck-machine': 'Hand-handle versus forearm-pad contact and exact supported orientation '
                               'remain unspecified.',
 'calf-extension-machine': 'Source combines shoulder/lever setup with downward pad movement and rising '
                           'heels; contact and load path need reconciliation.',
 'calf-press-machine': 'Previously held: shoulder-pad setup versus knees under pad and downward pad motion '
                       'cannot define a compatible calf press.',
 'chest-fly-machine': 'Generic fly arc does not determine handles versus elbow/forearm pads and supported '
                      'orientation.',
 'crunch-machine': 'Previously held: secured feet versus flat-foot source setup and differing moving support '
                   'require exact variant confirmation.',
 'glute-ham-raise-machine': 'Hip-supported straight-body text does not establish knee-flexion support/pivot '
                            'versus hip-hinge back extension. Binding/name alone cannot choose GHR geometry.',
 'glute-kickback-machine': 'Standing supports are given, but working-leg load contact/attachment is not '
                           'defined.',
 'hack-squat-machine': 'Sled/footplate/handles are given, but body orientation and load/support contacts do '
                       'not establish back-supported versus facing-sled variant.',
 'hip-abduction-machine': 'Catalogue unilateral sweep and dataset bilateral seated knee-pad setup need exact '
                          'variant reconciliation.',
 'pullup-assisted-machine': 'Previously held: hanging legs alone do not identify kneeling versus standing '
                            'assistance contact.',
 'rear-kick-machine': 'Pad-and-foot-or-ankle lever alternatives do not specify exact working contact and '
                      'torso-support layout.',
 'reverse-hyperextension-machine': 'Upper-body-hanging/secured-foot wording does not establish '
                                   'supported-torso versus moving-leg reverse-hyper geometry.',
 'seated-calf-raise-machine': 'Seat/toes/heel rise specified, but resistance contact and slightly-bent-knee '
                              'posture do not confirm knee-pad loading versus another calf station.',
 'seated-dip-machine': 'Description pushes handles down while instructions/source lower and raise body: '
                       'moving body versus moving lever conflict.',
 'seated-leg-curl-machine': 'Source curls legs upward from under-ankle pad; required seated knee-flexion '
                            'lever direction/contact is not established.',
 'seated-triceps-press-machine': 'Fixed upper arms close to torso combined with forward handle press needs '
                                 'elbow-extension trajectory confirmation; do not substitute chest press or '
                                 'downward seated dip.',
 'shrug-machine': 'Previously held: standing English versus seat adjustment in selected dataset does not '
                  'confirm posture/contact.',
 'behind-the-back-curl-cable-machine': 'Underhand low-handle curl with upper arms behind torso is stated, '
                                       'but unilateral versus shared-handle setup is not determined.',
 'hip-abduction-cable-machine': 'Outward sweep does not specify load attachment/anchor and precise supported '
                                'standing setup.',
 'overhead-curl-cable-machine': 'Elevated-arm curl toward shoulders versus source high-bar forehead curl '
                                'with elbows beside torso needs posture/endpoint reconciliation.',
 'reverse-fly-single-arm-cable-machine': 'Far hand is explicitly supporting; working-hand side and clear '
                                         'side-on cable/support geometry need confirmation without swapping '
                                         'hands.',
 'single-arm-triceps-pushdown-cable-machine': 'Single-handle high-pulley description versus chest-height '
                                              'straight-bar and already-extended-arm source fails to '
                                              'establish attachment/start phase.'}
READ_BUT_BLOCKED={**previous.READ_BUT_BLOCKED,**NEW_BLOCKED}
assert len(SCENES)==29 and len(NEW_BLOCKED)==25

def configure():
    p.ROUND=ROUND
    for attr,prefix,suffix in [('REG','data/assignments/','.json'),('MANIFEST','data/manifests/','/generator-single.json'),('EVIDENCE','data/audits/','-technique.json'),('ERRORS','data/audits/','-source-errors.json'),('CHECK','data/audits/','-validation.json'),('HANDOFF','docs/','-handoff.md'),('MESSAGE','docs/','-message.md')]:
        setattr(p,attr,prefix+ROUND+suffix)
    p.BATCHES=[p.PREFIX+f'{i:03}.json' for i in [34,35,36]]
    p.CLOUD=f'/workspace/exercise-image-results/{ROUND}/{p.ROLE}'
    p.GIT=f'assets/exercises/pending/{ROUND}/{p.ROLE}'
    p.SCENES=SCENES
    p.EQUIPMENT_IDS=list(SCENES)
    p.SOURCE_ERRORS={eid:True for eid in ['cable-crunch-machine','leg-press-machine','single-leg-press-machine','lying-leg-curl-machine']}
    p.conflict=conflict
    p.check=check
    for key in ['REG','MANIFEST','EVIDENCE','ERRORS','CHECK','PREPARED','BLOCKED','BATCHES','CLOUD','GIT','WORKER','ROLE','EQUIPMENT_IDS','SOURCE_ERRORS']:
        globals()[key]=getattr(p,key)

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
    assert len(ids)==29 and not(set(ids)&set(READ_BUT_BLOCKED))
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
        r['illustration_selection_scope']='Exact scene states permitted alternatives and compatible unbranded frame/exit geometry separately; no missing source height, palm angle, load type or brand is asserted as source fact.'
        if eid=='cable-crunch-machine':r['resolved_conflict']='Supine description is erroneous: both actual kneeling instructions and selected dataset specify away-facing high-pulley kneel with stationary hips. Raw description preserved; see source-error ledger.'
        if eid in ['hip-thrust-machine','lat-pulldown-close-grip-cable-machine','triceps-extension-machine','triceps-extension-cable-machine']:r['variant_selection']='Selected one explicit English alternative, written in selected_scene; compatible construction/phase is illustration choice, not approval or catalogue correction.'
    evidence['blocked_source_records']=b.source_evidence(s,list(READ_BUT_BLOCKED))['records']
    b.save(p.EVIDENCE,evidence)
    error_rows=[]
    erroneous_fields={
        'cable-crunch-machine':['description'],
        'leg-press-machine':['form_cues/0','common_mistakes/0','safety_note'],
        'single-leg-press-machine':['form_cues/1','common_mistakes/1','safety_note'],
        'lying-leg-curl-machine':['form_cues/0','common_mistakes/1','safety_note']}
    for eid,pointers in erroneous_fields.items():
        for pointer in pointers:
            value=s['by_id'][eid]['content']['en']
            for token in pointer.split('/'):value=value[int(token)] if isinstance(value,list) else value[token]
            error_rows.append({'exercise_id':eid,'source_field':'/content/en/'+pointer,'exact_value':value,
              'problem':'Supine description conflicts with kneeling instructions/dataset' if eid=='cable-crunch-machine' else 'Generic upper-limb wording is not a working-joint instruction for this lower-limb exercise; preserve it without interpreting the task as an arm press/curl.',
              'resolution_source':p.EVIDENCE,'scene_resolution':SCENES[eid],
              'decision_kind':'same_ID_actual_instruction_and_dataset_confirmation','catalog_modified':False,'user_approval_of_source_edit':False})
    b.save(p.ERRORS,{'schema_version':1,'catalog_sha256':s['catalog_sha256'],'catalog_modified':False,'records':error_rows,
      'conditional_or_range_notes':[{'exercise_id':'single-arm-cable-row-machine','note':'Explicitly permitted upright bench variant; conditional chest-pad mistake does not require adding pad.'},
       {'exercise_id':'iso-lateral-row-machine','note':'Chest pad selected because same-ID safety note explicitly requires its contact, independently of source name.'},
       {'exercise_id':'upright-row-cable-machine','note':'Render catalogue upper-chest stop only. Dataset chin height is beyond selected phase, no different grip/trajectory adopted.'}],
      'prior_ledgers_unchanged':['data/audits/agent-03-single-generator-2026-10-03-source-errors.json','data/audits/agent-03-single-generator-next30-2026-10-03-source-errors.json']})
    batches=[]
    for i,path in enumerate(p.BATCHES):
        bid=path.rsplit('/',1)[1][:-5];group=ids[i*10:(i+1)*10]
        rows=[p.route(p.make_equipment_row(eid,s,evidence),bid,s) for eid in group]
        for row in rows:
            row['technique_resolution']['illustration_choices_are_not_user_approvals']=True
            row['prompt_payload']['technique_resolution']=copy.deepcopy(row['technique_resolution'])
            row['generation_prompt']='Create exactly ONE square 1024x1024 transparent PNG of this exact exercise and ONE selected phase. Metadata must never appear as image text.\n'+json.dumps(row['prompt_payload'],ensure_ascii=False,sort_keys=True,indent=2)
            row['prompt_sha256']=base.sha(row['generation_prompt'].encode())
        doc={'schema_version':1,'batch_id':bid,'status':'ready','exercise_count':len(group),'exercise_ids':group,'exercises':rows,'source_branch':base.BRANCH,'generator':p.ROLE,'execution_branch':p.WORKER,
             'assignment_registry_path':p.REG,'execution_order':i+1,'phase':'equipment_tail','catalog_sha256':s['catalog_sha256'],'audited_commits':s['commits'],
             'generation_calls':0,'handoff_path':p.HANDOFF,'manifest_path':p.MANIFEST,'live_recheck_before_every_call':True}
        b.save(path,doc);batches.append(doc)
    tasks=[r for d in batches for r in d['exercises']]
    reg={'schema_version':1,'assignment_id':ROUND,'created_at':p.now(),'source_branch':base.BRANCH,'source_base_commit':s['commits']['HEAD'],'catalog_sha256':s['catalog_sha256'],
         'status':'ready','assignment_count':1,'exercise_count':len(ids),'batch_paths':p.BATCHES,
         'assignments':[{'generator':p.ROLE,'execution_branch':p.WORKER,'status':'assigned','exercise_count':len(ids),'exercise_ids':ids,'batch_paths':p.BATCHES,'batch_ids':[d['batch_id'] for d in batches],
                         'execution_order':[1,2,3],'manifest_path':p.MANIFEST,'handoff_path':p.HANDOFF}],
         'continuation_of_single_worker':True,'prior_assignment_path':'data/assignments/agent-03-single-generator-2026-10-03.json','prior_manifest_unchanged':True,
         'existing_A_B_assignments_unchanged':True,'supersedes_other_agents':False,'generation_calls_by_preparer':0,'audited_commits':s['commits'],
         'equipment_groups':{'specialized_machine':13,'cable_station':14,'smith_machine':2},'results_git_root':p.GIT,'results_cloud_root':p.CLOUD,
         'scope_authorization':'User requests next three batches; previous explicit instruction: one generator, equipment at end. No image generation by preparer.',
         'validation_path':p.CHECK,'remaining_technique_blocked_path':p.BLOCKED,'remaining_technique_blocked_ids':b.load(p.BLOCKED)['exercise_ids'],
         'additional_equipment_blocked_evidence_path':p.EVIDENCE,
         'scope_limit':'All available pushed remote heads read; unpushed outputs/ongoing calls in other cloud tasks may be inaccessible. Recheck before every call.'}
    b.save(p.REG,reg)
    b.save(p.MANIFEST,{'schema_version':1,'manifest_id':ROUND,'generator':p.ROLE,'execution_branch':p.WORKER,'assignment_path':p.REG,'source_branch':base.BRANCH,
                       'status':'ready_not_started','exercise_count':len(ids),'generation_calls':0,'user_review_policy':'pending on result creation until explicit user approval',
                       'quota_rule':'On first generator quota/rate-limit error save failure and history, push checkpoint and stop without repeat calls.',
                       'batches':[{'batch_id':d['batch_id'],'batch_path':path,'status':'ready','exercise_count':d['exercise_count'],
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
    q['single_generator_round3']={'assignment_path':p.REG,'batch_paths':p.BATCHES,'exercise_count':len(ids),'generator':p.ROLE,'execution_branch':p.WORKER,'handoff_path':p.HANDOFF,'equipment_groups':reg['equipment_groups'],'older_tasks_unchanged':True,'generation_calls':0}
    q['current_assignment_snapshot']={'assignment_path':p.REG,'audited_commits':s['commits'],'exercise_count':len(ids),'generation_calls':0}
    q['phase_plan']['latest_equipment_allocation_path']=p.REG
    q['current_equipment_blocked_ids']=list(READ_BUT_BLOCKED)
    q['current_equipment_blocked_count']=len(READ_BUT_BLOCKED)
    q['current_equipment_blocked_path']=p.EVIDENCE
    q['current_equipment_blocked_selector']='read_but_not_selected'
    q['phase_plan']['equipment_clarifications_path']=p.EVIDENCE
    q['phase_plan']['phase2_execution_gate']='Next three packs 034 then 035 then 036 belong to the SAME single worker. Old 001–033 tasks/history stay in original assignment/manifest; no reassignment or reset.'
    q['historical_fields_note']='Original exclusions and eligibility rules are past snapshots. Current ownership is read from existing assignments plus single_generator_preparation, single_generator_followup and single_generator_round3. Historical prepared_count is not current missing-PNG backlog.'
    q['single_generator_round3']['shortage']=dict(requested=30,prepared=29,missing=1,reason='Remaining 25 newly reviewed candidates require technique/contact clarification; no invented replacement.')
    b.save(base.QUEUE_PATH,q)
    with (ROOT/'.gitignore').open('a') as f:
        f.write('\n# Exact pending outputs for the same single worker, next three batches.\n')
        for r in tasks:f.write('!/'+r['planned_git_png_path']+'\n')
    b.save(p.CHECK,{'schema_version':1,'status':'pending_validation','protected_sha256':frozen,'previous_queue_routes_sha256':{r['exercise_id']:base.value_sha(r) for r in oldq['exercises']},
                    'source_base_commit':s['commits']['HEAD'],'catalog_sha256':s['catalog_sha256']})
    p.check(s)

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
        d=b.load(path);require(d['exercise_count']==len(d['exercises'])==len(list(SCENES)[bi*10:(bi+1)*10]),'batch_count:'+path)
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
    require(len(seen)==len(set(seen))==len(SCENES),'duplicate_or_missing_new_ID')
    require(reg['assignment_count']==len(reg['assignments'])==1 and reg['assignments'][0]['exercise_ids']==seen,'single_assignment')
    manifest=b.load(MANIFEST);mr=[r for d in manifest['batches'] for r in d['exercises']]
    require([r['exercise_id'] for r in mr]==seen,'manifest_IDs')
    for r in mr:
        for k in ['prompt_sha256','planned_png_path','planned_git_png_path','style_version','source_catalog_sha256']:require(r[k]==byid[r['exercise_id']][k],'manifest_field:'+r['exercise_id']+':'+k)
    require(q['current_blocked_ids']==b.load(BLOCKED)['exercise_ids'],'blocked_records_unchanged')
    require(not(set(seen)&set(q.get('current_equipment_blocked_ids',[]))),'selected_equipment_blocked')
    require(q['current_equipment_blocked_ids']==list(READ_BUT_BLOCKED),'blocked_equipment_ledger')
    require(evidence['blocked_source_records']==b.source_evidence(s,list(READ_BUT_BLOCKED))['records'],'blocked_source_fields')
    output={'status':'failed' if errors else 'passed','exercise_count':len(SCENES),'batch_count':3,'generator_count':1,'errors':errors,'live_commits':s['commits'],'catalog_ID_count':451,'language_blocks':4448,'PNG_pixels_reviewed':False,'generation_calls':0}
    if errors: raise ValueError(json.dumps(output,ensure_ascii=False))
    return output

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--prepare',action='store_true');parser.add_argument('--check',action='store_true');parser.add_argument('--fetch',action='store_true');parser.add_argument('--refresh-validation',action='store_true');args=parser.parse_args()
    configure()
    if args.fetch:b.fetch_heads()
    snapshot=b.n.snapshot()
    if args.prepare:prepare(snapshot)
    result=p.finalize_validation(snapshot) if args.prepare or args.refresh_validation else check(snapshot)
    print(json.dumps(result,ensure_ascii=False,indent=2))
