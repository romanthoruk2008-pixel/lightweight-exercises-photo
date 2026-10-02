#!/usr/bin/env python3
"""Prepare B's explicitly authorized continuation; never invoke a generator.

Fetch all origin heads before running. --check reads and validates saved plans.
Existing batches, A's assignment and shared state are protected byte for byte.
"""
import argparse
import collections
import copy
import hashlib
import json
import pathlib
import re
import prepare_agent03_next50 as n

base=n.base
ROOT=n.ROOT
ROUND='agent-03-generator-b-continuation-2026-10-02'
REG=f'data/assignments/{ROUND}.json'
RESUME='data/resumes/agent-03-others-009-generator-b.json'
MANIFEST=f'data/manifests/{ROUND}/generator-b.json'
EVIDENCE=f'data/audits/{ROUND}-technique.json'
ERRORS='data/audits/agent-03-source-description-errors-2026-10-02.json'
VALIDATION=f'data/queues/{ROUND}-validation.json'
REVIEW=f'data/queues/{ROUND}-blocked.json'
DECISION='data/style-decisions/agent-03-illustration-footwear-approved-2026-10-02.json'
STYLE_DOC='docs/exercise-image-style-illustration-footwear.md'
HANDOFF=f'docs/{ROUND}-handoff.md'
MESSAGE=f'docs/{ROUND}-message.md'
NIGHT='data/batches/night-2026-10-01-clarifications.json'
OLD009='data/batches/agent-03-others-009.json'
WORKER='agent-07-generator-b-2026-10-02'
GIT_ROOT=f'assets/exercises/pending/{ROUND}/generator-b'
CLOUD_ROOT=f'/workspace/exercise-image-results/{ROUND}/generator-b'
NEUTRAL_DOC='docs/exercise-image-style-neutral-primary.md'
NEUTRAL_VERSION='v1-neutral-primary-2026-10-02'
FOOTWEAR_VERSION='v1-neutral-primary-footwear-2026-10-02'
CAMERA='Full-body front-side three-quarter view exposing every prescribed contact, grip and support. Entire person and all equipment visible within square; no crop, text, arrows or second phase.'
INITIAL_NIGHT=['downward-dog','bear-crawl','jumping-jack','high-knees','mountain-climber','diamond-pushup','chest-fly-dumbbell','waiter-curl-dumbbell']
SCENE_CHOICES={
 'hiit':'Running in place, one phase.',
 'pilates':'Mat Hundred, legs in tabletop.',
 'stretching':'Seated hamstring stretch with one straight leg.',
 'yoga':'Mountain / Tadasana.',
}
FOOTWEAR={'walking':'Walking shoes suitable for controlled heel-to-toe walking.',
          'hiking':'Hiking footwear with traction appropriate to the depicted trail footing.',
          'snowboarding':'Snowboard boots, compatible bindings and protective helmet.'}

# Rendering scenes are explicit decisions with evidence below, never substitute
# catalogue fields or infer muscles from the external publisher's target lists.
SCENES={
 'downward-dog':('Inverted-V held endpoint','Hips raised back and up, neutral long spine, head aligned with spine, arms extended; knees softly bent if needed; heels relaxed toward floor, not forced down.','Open palms shoulder-width on mat, fingers forward.','Both palms and both feet on a simple mat; no bench or straps.','Hips travel back and up from hands-and-knees; depict only the held endpoint.'),
 'bear-crawl':('One contralateral crawl step','Low hips and flat back, knees bent and hovering just above floor; right hand and left foot advance together while left palm and right toes support.','Open palms on floor.','Floor/mat contacts at left palm and right toes; bent knees remain off the floor; no external apparatus.','Alternate opposite hand and foot; no same-side crawl or straight-legged high-hip walk.'),
 'jumping-jack':('Feet-apart soft landing, arms overhead','Upright torso, feet apart after outward jump, knees soft, both arms raised overhead.','No equipment grip; hands free.','Both feet meet a clear level contact surface; no bicycle/pedals.','Feet jump apart as arms rise; show this one landing, no starting-pose duplicate.'),
 'high-knees':('Right knee at hip-height, left support','Upright torso, right knee driven forward toward hip height, left foot supporting body; arms relaxed for balance.','Hands free; no external grip.','Left foot contacts a clear level floor; right foot off floor.','Alternate with a quick STEP as expressly specified for high knees; not the skips/hop alternative.'),
 'mountain-climber':('Right knee driven toward chest','High plank, hands directly under shoulders, low hips and braced trunk; right knee toward chest, left leg extended behind.','Open palms under shoulders.','Both palms and left forefoot on mat/floor; right foot moving forward; no TRX straps.','Knees alternate toward chest; no crossed elbow-to-knee substitution.'),
 'diamond-pushup':('Controlled lower phase above diamond hands','Rigid plank from head through heels; elbows bent close to sides, chest near hands without resting on floor.','Thumbs and index fingers form diamond on floor; palms stable.','Two palms on floor and toes supporting plank; no clap or airborne hands.','Chest lowers toward diamond, then presses up; freeze lower phase only.'),
 'chest-fly-dumbbell':('Wide-arc lower endpoint','Lie supine on FLAT bench; head, upper back and pelvis on pad; both feet planted, elbows softly bent and wrists neutral; arms open to shoulder/chest level.','One dumbbell per hand; palms face EACH OTHER, closed grip.','One flat bench, two dumbbells, both feet on floor. No chest-down incline support.','Dumbbells move in matching wide arcs; retain slight elbow bend, not a press.'),
 'hiit':('Single running-in-place step','Upright torso, right knee raised in a controlled running step, left foot at ground contact, arms naturally opposite legs; no exaggerated sprint lean.','Hands free.','Clear level footing; no cardio machine or added weight.','Run on the spot, not forward travel; one working step, not recovery walking or a montage.'),
 'pilates':('Hundred tabletop held arm-pump phase','Supine on mat, head and upper shoulders gently curled up, hips and knees bent about 90 degrees in tabletop, shins parallel to floor; arms long by sides hovering above mat.','Hands free, palms down; no straps or handles.','Back/pelvis supported on simple mat; legs unsupported in tabletop; no reformer or suspension anchor.','Small controlled arm pumping coordinated with breathing; freeze ONE tabletop phase, no leg extension or duplicate figure.'),
 'stretching':('Gentle seated single-leg hamstring hold','Sit on mat with right leg straight forward, left knee bent comfortably to side; hinge mildly from hips toward right leg, spine long, no bounce or forced reach.','Hands rest lightly along straight leg without pulling the neck or forcing toes.','Pelvis and straight-leg heel supported by mat; bent leg relaxed; no band or elevated bench.','Mild static posterior-thigh stretch of one straight leg; user-selected illustration, not a new anatomical primary target.'),
 'yoga':('Mountain / Tadasana held stance','Stand tall with feet together or comfortably close, weight evenly over both feet, neutral spine, relaxed shoulders, arms long by sides.','Hands relaxed with palms facing forward, no equipment grip.','Both feet on simple mat, barefoot.','Still upright Mountain pose, no lunge, arms-up variation or sequence.'),
 'walking':('One grounded heel-to-toe stride','Upright torso, forward foot meeting ground at heel while trailing foot approaches toe-off; short natural stride and relaxed opposite arm swing.','Hands free; no poles or weights.','Compatible walking shoes; level contact surface only, no treadmill.','Controlled walking stride, not airborne running; show only one phase.'),
 'hiking':('Controlled short uphill trail step','Upright balanced torso with slight whole-body lean appropriate to a modest rise; leading foot on a small stable trail foothold, rear foot on lower contact surface.','Hands free for balance; no invented trekking poles.','Traction hiking footwear on a minimal functional trail contact patch; no landscape, backpack or machine.','One controlled hiking step over uneven footing; not running or an invented steep climbing route.'),
 'snowboarding':('Controlled edge-glide stance','One person side-on on snowboard, both knees softly bent, hips centered over board, torso balanced and arms relaxed for balance; slight controlled board edge engagement.','Hands free; no poles.','Both feet wear snowboard boots locked into compatible front/back snowboard bindings, with protective snowboard helmet. Show all boot-binding-board contacts; no barefoot board contact.','One stable steering/gliding phase on minimal snow contact patch; no jump, trick, landscape or sequence.'),
 'cross-body-hammer-curl-dumbbell':('Right diagonal curl toward opposite shoulder','Stand tall, both elbows close to torso; right elbow bends bringing its dumbbell diagonally toward left shoulder, left dumbbell stays down at side; no torso swing.','One dumbbell in EACH hand; neutral hammer grip, palms toward body.','Both feet on floor; no barbell, bench support or band.','Right dumbbell crosses torso toward opposite shoulder; controlled lowering, not straight bilateral supinated curl.'),
 'concentration-curl-dumbbell':('Single-arm supported curl','Sit on flat bench with legs apart, right elbow firmly supported on inside of right thigh; right elbow bent, one dumbbell toward right shoulder, trunk steady.','One dumbbell in right hand with underhand/supinated grip; free hand relaxed, not assisting working elbow or weight.','Pelvis on bench, both feet on floor, working elbow on inside of thigh; no barbell or preacher pad.','Only supported working forearm curls toward same-side shoulder and lowers under control.'),
 'clean-barbell':('Full squat receiving phase','Free barbell received on FRONT shoulders in deep front squat, hips below knees, neutral braced spine, heels planted, elbows driven forward; wrists extended appropriately for front rack.','Overhand/hook-grip pull transitions to front rack; hands just outside hips, fingers retain contact under bar in receiving phase.','Both feet on clear floor; one free barbell across front shoulders. No bench, Smith rails or rear-neck rack.','Ground-to-shoulders clean with pull-under and FULL squat catch, then stand; one receiving phase. Power-clean candidate rejected in exact catalogue match rationale.'),
}

BLOCKED={
 'waiter-curl-dumbbell':'English and selected dataset both describe an ordinary TWO-dumbbell supinated curl; no verified distinctive Waiter Curl grip/quantity. Binding and name do not confirm this variant. Do not replace it with either ordinary curl or a guessed single-dumbbell curl.',
 'bicycle-crunch':'English specifies feet-flat ordinary crunch. Match rationale specifies alternating opposite elbow/knee cycling, but no exact supported leg configuration; generic bicycle demonstrations cannot determine this catalogue variant.',
 'bicycle-crunch-raised-legs':'English is identical feet-flat crunch while ID/match require raised-leg alternating rotation. Height/extension and distinction from the separate bicycle-crunch ID are not defined.',
 'floor-triceps-dip':'Three incompatible supports: English instructions floor, description parallel bars, selected dataset/Polish chair or bench edge. A demonstration of one does not determine the intended catalogue variant.',
 'lying-neck-extension':'English leaves prescribed supported position undefined; match says supine while neck-extension orientation/support remains unspecified. No exact source fixes head/torso geometry.',
 'seated-incline-curl-dumbbell':'Description requires arms hanging BEHIND torso; English and original dataset require upper arms resting ON incline bench. Do not substitute a preacher or unsupported incline curl without exact confirmation.',
 'chest-dip-weighted-machine':'Parallel supports in English conflict with selected straight-bar dip source name; Rogue belt verifies external loading only, not which support/variant is intended.',
 'drag-curl-barbell':'English/selected source keep upper arms still as ordinary curl; drag variant would require moving elbows backward with bar close to torso. No verified exact-variant source resolves this conflict.',
 'feet-up-bench-press-barbell':'English feet planted; Polish/Italian legs raised with bent knees; Spanish feet on bench. Exact supported position remains unresolved; Larsen straight-leg examples cannot choose it.',
 'hammer-curl-band-resistance-band':'Neutral grip is known; exact band construction, handles and foot/anchor contact are not specified. Official dumbbell hammer curl does not resolve a band anchor.',
 'hip-thrust-barbell':'Description/cue support upper back only; English/dataset lie flat on bench and lift hips off it. Retrieved dumbbell hip-thrust material is not exact barbell-variant confirmation.',
 'landmine-180-barbell':'Hip-to-hip description/cues versus right-hip to left-shoulder instructions. A landmine press/row is a different trajectory and cannot choose endpoints.',
 'lying-neck-extension-weighted-plate':'Head described as supported with plate on back of head; torso orientation and free neck range absent. Unloaded neck examples do not verify this weighted variant.',
 'nordic-hamstrings-curls':'Secured ankles are stated, but passive anchor/contact and assisted return without a second person are undefined. No verified standard rack/bench anchor selected; specialized apparatus remains next stage.',
 'pushup-weighted':'Official TRX confirms a vest is an admissible weighted push-up variant, not that this exact catalogue upper-back/plate load is a vest. Preserve alternatives; do not call our vest recommendation user-approved.',
 'side-bend-dumbbell':'Away/opposite the dumbbell plus lowering the weight gives contradictory lateral direction. No verified exact source determines which catalogue statement to override.',
 'single-arm-landmine-press-barbell':'Standing split stance/free sleeve conflicts with anchored-end wording and required back pad. Official half-kneeling landmine press is not the catalogue standing supported variant.',
 'single-leg-standing-calf-raise-barbell':'Free bar across upper back needs both hands while safety requires a handhold/machine support; simultaneous support geometry is undefined. No substitution with Smith.',
 'muscle-up-machine':'Official bar muscle-up confirms pull/transition/dip to extended-arm support. Catalogue/dataset demand turning overhand palms toward self and finish fully flexed; retrieved written sources do not settle exact grip transition. Rings or strict-only replacement forbidden.',
 'press-under-barbell':'Overhead press-under receiving stance/depth unspecified: partial squat, full squat or split. Generic overhead press/clean examples do not define this drill.',
}

def load(p):return n.prior.load(p)
def save(p,d):n.prior.save(p,d)
def sha(p):return n.file_sha(p)

def fetch_heads():
    heads=base.git('ls-remote','--heads','origin').decode().splitlines()
    for line in heads:
        ref=line.split()[1];branch=ref.removeprefix('refs/heads/')
        base.git('fetch','--quiet','origin','+'+ref+':refs/remotes/origin/'+branch)

def provenance(ref,path,s,ptr):
    raw=base.git('show',s['commits'][ref]+':'+path)
    return {'branch':ref.removeprefix('origin/') if ref!='HEAD' else base.BRANCH,
            'commit':s['commits'][ref],'path':path,'json_pointer':ptr,'sha256':base.sha(raw)}

def actual_assignments(s):
    """Only selected task rows and explicit assignment lists; never examples.

    Historical clarification sheets, source-evidence records and copied base
    progress defaults are not an active new assignment. Same-batch continuation
    is permitted only by the user's explicit transfer below.
    """
    result=collections.defaultdict(list)
    for ref,paths in s['trees'].items():
        for path in sorted(paths):
            if not path.endswith('.json') or not path.startswith(('data/batches/','data/assignments/','data/manifests/','data/queues/')):continue
            d=json.loads(base.git('show',s['commits'][ref]+':'+path))
            if not isinstance(d,dict):continue
            if path==NIGHT or path==REG or path==MANIFEST:continue
            if path.startswith('data/batches/'):
                if d.get('batch_id'):
                    for i,r in enumerate(d.get('exercises',[])):
                        if isinstance(r,dict) and r.get('exercise_id') in s['by_id']:
                            result[r['exercise_id']].append(dict(provenance(ref,path,s,'/exercises/'+str(i)),batch_id=d['batch_id'],kind='selected_batch'))
            elif path.startswith('data/assignments/'):
                for i,a in enumerate(d.get('assignments',[])):
                    if a.get('status') in ['held','blocked','cancelled','superseded']:continue
                    for eid in a.get('exercise_ids',[]):
                        if eid in s['by_id']:result[eid].append(dict(provenance(ref,path,s,'/assignments/'+str(i)),kind='explicit_assignment',generator=a.get('generator')))
            elif path.startswith('data/manifests/'):
                # Execution manifests have source prose/history and nested
                # batches. Only their actual task rows count as assignments.
                def rows(obj,ptr):
                    if isinstance(obj,list):
                        for i,r in enumerate(obj):rows(r,ptr+'/'+str(i))
                    elif isinstance(obj,dict):
                        eid=obj.get('exercise_id')
                        if eid in s['by_id'] and any(k in obj for k in ['attempts','status','result_path','batch_id']):
                            result[eid].append(dict(provenance(ref,path,s,ptr),kind='execution_manifest',generator=d.get('generator')))
                        for k in ['exercises','batches','tasks']:rows(obj.get(k,[]),ptr+'/'+k)
                rows(d,'')
            elif path.startswith('data/queues/'):
                for i,r in enumerate(d.get('exercises',[]) or []):
                    if isinstance(r,dict) and r.get('batch_id') and r.get('exercise_id') in s['by_id']:
                        result[r['exercise_id']].append(dict(provenance(ref,path,s,'/exercises/'+str(i)),batch_id=r['batch_id'],kind='batch_queue_route'))
    return result

def conflict(eid,s,assignments,resume=False,allow_new=False):
    if s['by_id'][eid]['archived']:return 'archived'
    if eid in s['png_sources']:return 'PNG_exists_including_pending'
    if s['classifications'][eid] in ['specialized_machine','cable_station','smith_machine']:return 'equipment_next_stage'
    allowed={OLD009} if resume else set()
    if allow_new:allowed|={'data/batches/agent-03-others-026.json','data/batches/agent-03-others-027.json'}
    for a in assignments.get(eid,[]):
        if a['path'] in allowed:continue
        if a['kind']=='batch_queue_route' and (resume and a.get('batch_id')=='agent-03-others-009' or allow_new and a.get('batch_id') in ['agent-03-others-026','agent-03-others-027']):continue
        return 'existing_selected_assignment:'+a['branch']+':'+a['path']
    if not resume and s['touched'].get(eid):return 'existing_attempt_stays_in_original_batch'
    return None

def history(eid,s):
    versions=[]
    for ref,paths in s['trees'].items():
        p=base.PROGRESS_PATH
        if p not in paths:continue
        row=json.loads(base.git('show',s['commits'][ref]+':'+p))['exercises'].get(eid)
        if row and (row.get('attempts',0) or row.get('attempt_history') or row.get('last_error')):
            versions.append({'source':provenance(ref,p,s,'/exercises/'+base.pointer(eid)),'record':row})
    high=max([v['record'].get('attempts',0) for v in versions]+[0])
    chosen=max(versions,key=lambda v:(v['record'].get('attempts',0),len(v['record'].get('attempt_history',[])))) if versions else None
    return {'attempts_before':high,'next_attempt_number':high+1,'attempt_history':copy.deepcopy(chosen['record'].get('attempt_history',[])) if chosen else [],
            'last_error':copy.deepcopy(chosen['record'].get('last_error')) if chosen else None,
            'status_before':chosen['record'].get('status') if chosen else 'not_started','source_versions':versions,
            'preparation_generation_calls':0,'rule':'Failed no-PNG attempts remain in ORIGINAL batch; append new attempt, never overwrite/reset history.'}

def source_evidence(s,ids):
    folder=pathlib.Path('/tmp/agent03-source-texts/exercise-catalog-v1')
    mr=(folder/'working-manifest.json').read_bytes();dr=(folder/'dataset.json').read_bytes()
    old=load('data/audits/agent-03-blocked-source-evidence.json')
    assert base.sha(mr)==old['manifest_sha256']==s['catalog']['source']['manifest_sha256']
    assert base.sha(dr)==old['dataset_sha256']
    m=json.loads(mr);dataset=json.loads(dr)
    mc=collections.Counter(r['lightweight_id'] for r in m['exercises']);dc=collections.Counter(r['id'] for r in dataset)
    mb={r['lightweight_id']:r for r in m['exercises']};db={r['id']:r for r in dataset};records=[]
    for eid in ids:
        e=s['by_id'][eid];v=mb[eid];assert mc[eid]==1
        for k in ['name','equipment','primary_muscle','secondary_muscles','archived','content','source','match']:assert e[k]==v[k],(eid,k)
        sid=e['source']['dataset_id'];d=db.get(sid)
        if sid is not None:
            candidates=[c for c in v['candidates'] if c['id']==sid];assert dc[sid]==1 and len(candidates)==1
            for k in ['id','name','equipment','instructions','instruction_steps']:assert candidates[0][k]==d[k]
        records.append({'exercise_id':eid,'catalog_record_sha256':base.value_sha(e),'manifest_record_sha256':base.value_sha(v),
                        'all_catalog_manifest_fields_exact':True,'source_dataset_id':sid,'source_selector':'dataset[id="'+str(sid)+'"]' if sid is not None else None,
                        'original_dataset_record_sha256':base.value_sha(d) if d else None,
                        'original_dataset_english':copy.deepcopy(d['instruction_steps']['en']) if d else None,
                        'original_dataset_name':d['name'] if d else None,'original_dataset_equipment':d['equipment'] if d else None,
                        'catalog_match':copy.deepcopy(e['match']),
                        'supplementary_exact_ID_fields':{lang:copy.deepcopy(e['content'][lang]) for lang in ['pl','uk'] if lang in e['content']},
                        'binding_alone_is_not_technique_confirmation':True})
    return {'schema_version':1,'catalog_sha256':s['catalog_sha256'],'manifest_sha256':base.sha(mr),'dataset_sha256':base.sha(dr),
            'dataset_commit':m['dataset_commit'],'source_release_url':old['source_release_url'],
            'whole_media_archive_downloaded':False,'whole_archive_sha256_verified':False,'records':records}

def publication(url,publisher,quotes,scope):
    p=pathlib.Path('/tmp/agent03-b-web-v2')/(hashlib.sha256(url.encode()).hexdigest()[:12]+'.json')
    d=json.loads(p.read_text());assert d['http_status']==200 and d['final_url']==url
    assert all(q in d['text'] for q in quotes),(url,quotes)
    return {'url':url,'publisher':publisher,'retrieved_at':d['retrieved_at'],'http_status':200,'final_url':d['final_url'],
            'html_sha256':d['html_sha256'],'extracted_text_sha256':base.sha(d['text'].encode()),'quotes':quotes,
            'quote_sha256':[base.sha(q.encode()) for q in quotes],'exact_scope':scope,'photos_or_video_downloaded':False,
            'muscle_targets_from_publisher_used':False}

def external_evidence():
    trx='https://www.trxtraining.com/blogs/news/bicep-workouts-at-home'
    return {
     'downward-dog':[publication('https://www.acefitness.org/resources/everyone/exercise-library/18/downward-facing-dog/','American Council on Exercise',[
         'Allow a slight bend in the knees if required to achieve the inverted-V position.',
         'Continue moving until your body forms an inverted-V, keeping both arms and legs extended and a neutral (flat) spine.'],
         'Same inverted-V endpoint, hand/foot supports and optional soft knees; catalogue still determines ID and muscles.')],
     'bear-crawl':[publication('https://www.acefitness.org/resources/everyone/exercise-library/150/bear-crawl/','American Council on Exercise',[
         'Move the\xa0left hand and the\xa0right leg forward to start crawling.',
         'Alternate the arm and leg movements while\xa0keeping the back\xa0straight and the\xa0hips and shoulders at the same height.'],
         'Contralateral crawl and low aligned hips/back; render mirrored right-hand/left-foot step, not a different crawl.')],
     'diamond-pushup':[publication(trx,'TRX',[
         'Start in a high plank position with your hands close together, forming a diamond shape with your index fingers and thumbs.',
         'Lower your body down by bending your elbows while keeping them close to your sides.'],
         'Diamond hand geometry and close elbows only; corroborates exact-ID Polish instructions. Ignore unrelated publisher biceps claims and generic clap cue.')],
     'chest-fly-dumbbell':[publication('https://www.acefitness.org/resources/everyone/exercise-library/21/lying-chest-fly/','American Council on Exercise',[
         'Downward Phase: Inhale and slowly lower the dumbbells in unison in a wide arc until they lie level with your shoulders or chest.',
         'Keep the dumbbells parallel with each other during the movement.'],
         'Flat supine two-dumbbell fly with inward palms and soft elbows matches explicit selected dataset; no chest-down support.')],
     'cross-body-hammer-curl-dumbbell':[publication(trx,'TRX',[
         'Cross-Body Hammer Curls: During the curling motion, bring the weights across your body towards the opposite shoulder.'],
         'Dumbbell hammer-curl diagonal variation, not a straight curl or band; exact dataset supplies neutral grip, standing posture and two dumbbells.')],
     'clean-barbell':[publication('https://www.crossfit.com/essentials/foundational-movement-clean-what-is-a-clean','CrossFit',[
         'Hook grip on the bar.',
         'aggressively driving the elbows forward to receive the bar on the shoulders.',
         'The bar can be received either in the bottom of a squat or in a power position (in which the hips remain above the knees), depending on the workout and load.',
         'The full movement finishes with the hips and legs working by squatting the weight and standing up to full extension.'],
         'Both catch variants are admissible generally; this exact catalogue match rejects the power candidate because of depth. Select full-squat receiving illustration; front rack uses elbows forward, not dangling under load.')],
     'pushup-weighted':[publication('https://www.trxtraining.com/blogs/news/the-beginners-guide-to-weighted-belt-and-weight-vest-workouts','TRX',[
         'Weight Vests are great for everything from running to powering up a plank, push-up, or pull-up.'],
         'Admissible vest variant ONLY; not proof this exact upper-back plate record intends vest. Remains blocked, no user approval claimed.')],
     'single-arm-landmine-press-barbell':[publication('https://www.trxtraining.com/blogs/news/front-delt-exercises','TRX',[
         'Start in a half-kneeling position holding onto the end of the barbell with one hand'],
         'A DIFFERENT half-kneeling variant, not exact catalogue standing split stance with back-pad wording. Not used to unblock.')],
     'muscle-up-machine':[publication('https://www.crossfit.com/essentials/the-strict-bar-muscle-up','CrossFit',[
         'The muscle-up is a movement that begins from the hang, passes through portions of a pull-up and a dip, then finishes in a supported position with arms extended.'],
         'Bar final support confirms elbow-extension component only, not catalogue overhand-to-underhand grip transition or chosen kip. Remains blocked.')],
    }

def resolution(eid,s,record,external):
    if eid in SCENE_CHOICES or eid in FOOTWEAR:
        return {'status':'resolved','decision_kind':'user_illustration_choice','user_decision_path':DECISION,
                'choice':SCENE_CHOICES.get(eid,FOOTWEAR.get(eid)),'technique_source':'Exact-ID English posture/trajectory plus explicitly selected illustration.',
                'not_catalog_correction':True,'not_PNG_approval':True}
    paths=['content.en.description','content.en.instructions','content.en.form_cues','content.en.common_mistakes','content.en.safety_note','source.dataset_id','match.rationale']
    note='Entire English block reviewed for this ID; specific posture, contacts and path, not merely dataset ID/name, control the selected single phase.'
    if eid=='diamond-pushup':paths+=['content.pl.instructions'];note='Exact-ID Polish instruction defines diamond thumb/index contact; TRX corroborates high plank and close elbows. Generic conditional clap is not this variant.'
    if eid=='chest-fly-dumbbell':note='Selected dataset instructions explicitly supine on flat bench, two inward-facing dumbbells, softly bent elbows, wide arc; ACE independently corroborates supports/path.'
    if eid=='cross-body-hammer-curl-dumbbell':paths+=['content.pl.instructions'];note='Exact selected dataset and same-ID Polish specify standing TWO dumbbells, neutral grip, elbow close and diagonal path to opposite shoulder; TRX corroborates cross-body hammer variation. English barbell is recorded as error, never used to render.'
    if eid=='concentration-curl-dumbbell':paths+=['content.pl.instructions'];note='Exact selected dataset and same-ID Polish explicitly specify seated ONE dumbbell, elbow on inside thigh, supinated supported curl to shoulder. English barbell/stand-or-sit is recorded as error, never used to render.'
    if eid=='clean-barbell':note='Catalogue match explicitly rejects Power Clean for different depth; CrossFit independently describes full-squat clean and front rack/elbows forward. Full-squat receiving is source-compatible illustration selection, not a claimed user approval of our earlier recommendation.'
    return {'status':'resolved','decision_kind':'technique_confirmation' if eid!='clean-barbell' else 'source_confirmation_and_illustration_selection',
            'catalog_fields_reviewed':paths,'source_binding':record,'primary_publications':external.get(eid,[]),'rationale':note,
            'user_approved_recommendation':False,'source_description_error_ledger':ERRORS,'catalog_changed':False}

def output(eid,bid,attempt):
    relative=f'{bid}/{eid}/attempt-{attempt}.png'
    return {'planned_png_path':CLOUD_ROOT+'/'+relative,'planned_git_png_path':GIT_ROOT+'/'+relative,'planned_output_relative_path':relative}

def make_task(eid,bid,s,ev,ext):
    row=base.fields_for_id(eid,s);scene=n.prior.scene(eid,SCENES[eid],CAMERA);r=resolution(eid,s,ev,ext)
    style=copy.deepcopy(base.STYLE);broad=row['primary_muscle'] in ['full_body','cardio','other']
    version=NEUTRAL_VERSION if broad else 'v1';style_files=['docs/exercise-image-style.md']+([NEUTRAL_DOC] if broad else [])
    if broad:style['primary_highlight']={'hex':None,'rule':'full_body/cardio/other are broad labels. Opaque silver-gray neutral body; only exact explicitly listed secondary muscles #F26445 at 40–50% intensity. Empty secondary list means NO highlights.'}
    if eid in FOOTWEAR:
        version=FOOTWEAR_VERSION;style_files.append(STYLE_DOC)
        style['human_model']=style['human_model'].removesuffix('barefoot.')+'footwear/protection ONLY as specified by exact-ID approved scene; human appearance/materials and black shorts otherwise unchanged.'
        style['footwear_exception']={'exercise_id':eid,'decision_path':DECISION,'equipment':FOOTWEAR[eid]}
    style['version']=version;style['approval_status']='approved'
    style['no_invention']='Exact-ID source and verified explicit technique/illustration decisions determine pose/equipment. Do not transfer reference pose or invent muscle targets. No brand, numerical load or extra attachments.'
    files=[{'path':p,'sha256':sha(p)} for p in style_files]
    payload={'identity_do_not_render_as_text':{'exercise_id':eid,'name':row['name'],'catalog_sha256':s['catalog_sha256'],'catalog_record_sha256':row['source_catalog_record_sha256']},
             'exact_catalogue_source':{k:copy.deepcopy(row[k]) for k in ['source_english','equipment','primary_muscle','secondary_muscles']},
             'human_reference':n.prior.reference(s),'style':style,'approved_style_files':files,
             'selected_render_scene':scene,'technique_resolution':r,
             'source_use_rule':'Render selected_render_scene and exact-ID documented decisions only. Raw English retained verbatim for provenance; ledger-listed erroneous generic phrases must not override verified selected variant. Never infer muscles from pose, reference, name or publisher.',
             'planned_output_do_not_render_as_text':dict(output(eid,bid,1),batch_id=bid,exercise_id=eid)}
    prompt='Create exactly ONE 1024x1024 transparent PNG of this exact exercise, ONE person and ONE selected phase. Metadata and source prose must never appear as image text.\n'+json.dumps(payload,ensure_ascii=False,sort_keys=True,indent=2)
    row.update(batch_id=bid,status='ready',technical_status='ready',prompt_prepared=True,prompt_status='complete',
               style_version=version,approved_style_files=files,human_reference=n.prior.reference(s),scene=scene,technique_resolution=r,
               source_url=n.CATALOG_URL+s['commits']['origin/work']+'/'+base.CATALOG_PATH,source_selector=f'exercises[id="{eid}"]',
               source_catalog_commit=s['commits']['origin/work'],source_evidence_path=EVIDENCE,
               generation_prompt=prompt,prompt_payload=payload,prompt_sha256=base.sha(prompt.encode()),assigned_generator='generator-b',
               assignment_registry_path=REG,attempts=0,next_attempt_number=1,result_path=None,result_sha256=None,user_review=None,
               future_user_review_policy='pending until explicit user approval',agent_visual_review='not_performed',generation_authorized_now=False,**output(eid,bid,1))
    return row

def old009_task(row,s):
    eid=row['exercise_id']
    assert all(row.get(k)==v for k,v in base.fields_for_id(eid,s).items()),eid
    prompt=row['generation_prompt'];assert row['generation_prompt_sha256']==base.sha(prompt.encode())
    h=history(eid,s);r=copy.deepcopy(row)
    # Original complete prompt remains byte-identical. Execution/output metadata
    # is an explicit sidecar rebind, not a replacement of exercise or prompt.
    r.update(batch_id='agent-03-others-009',status='ready_to_continue',assigned_generator='generator-b',assignment_registry_path=REG,
             original_batch_path=OLD009,original_batch_sha256=sha(OLD009),original_row_attempts=row['attempts'],
             original_output_root=row.get('output_root'),output_root=CLOUD_ROOT,
             original_generation_prompt_sha256=row['generation_prompt_sha256'],prompt_sha256=row['generation_prompt_sha256'],
             human_reference=n.prior.reference(s),approved_style_files=[{'path':'docs/exercise-image-style.md','sha256':s['style_sha256']}],
             continuation=h,attempts=h['attempts_before'],next_attempt_number=h['next_attempt_number'],
             previous_attempt_history=h['attempt_history'],last_error=h['last_error'],generation_authorized_now=False,
             future_user_review_policy='pending until explicit user approval',
             source_url=n.CATALOG_URL+s['commits']['origin/work']+'/'+base.CATALOG_PATH,
             source_selector=f'exercises[id="{eid}"]',source_catalog_commit=s['commits']['origin/work'],
             output_rebinding_rule='Use sidecar planned paths. Original batch/prompt and historic failed attempts stay unchanged.',
             **output(eid,'agent-03-others-009',h['next_attempt_number']))
    return r

def blocked_rows(s,evidence,ext):
    rows=[];old=load(n.RECOMMENDATIONS);by={r['exercise_id']:r for r in old['exercises']}
    historical=load('data/audits/agent-03-blocked-source-evidence.json')['unresolved_investigations']
    for eid,reason in BLOCKED.items():
        r=base.fields_for_id(eid,s);r.update(status='blocked',technical_status='blocked',block_reason=reason,assigned_generator=None,
           generation_prompt=None,prompt_prepared=False,source_evidence_path=EVIDENCE,source_binding=evidence[eid],
           primary_publications=ext.get(eid,[]),user_approval_claimed=False,needs_user_to_guess_technique=False,
           next_action='Find an exact-variant official technical source; if unavailable preserve blocked status, never substitute a similar exercise.',
           original_question=by[eid]['original_question'] if eid in by else next(v['question_uk'] for v in load(NIGHT)['exercises'] if v['exercise_id']==eid))
        r['historical_official_research_not_confirmation']=[v for v in historical if v['exercise_id']==eid]
        r['current_official_research_not_confirmation']=research_for_blocked(eid)
        rows.append(r)
    return rows

def research_for_blocked(eid):
    """Bind attempted primary research to the exact unresolved question."""
    links={
      'waiter-curl-dumbbell':['https://athleanx.com/articles/biceps-exercises','https://www.trxtraining.com/search?q=waiter+curl&type=article'],
      'bicycle-crunch':['https://www.acefitness.org/resources/everyone/exercise-library/body-part/abs/'],
      'bicycle-crunch-raised-legs':['https://www.acefitness.org/resources/everyone/exercise-library/body-part/abs/'],
      'floor-triceps-dip':['https://www.trxtraining.com/blogs/news/bodyweight-exercises'],
      'lying-neck-extension':['https://www.acefitness.org/resources/everyone/exercise-library/body-part/neck/'],
      'seated-incline-curl-dumbbell':['https://www.trxtraining.com/search?q=incline+curl&type=article'],
      'chest-dip-weighted-machine':['https://www.roguefitness.com/rogue-dip-belt'],
      'drag-curl-barbell':['https://www.trxtraining.com/search?q=drag+curl&type=article'],
      'feet-up-bench-press-barbell':['https://www.trxtraining.com/search?q=feet+up+bench&type=article'],
      'hammer-curl-band-resistance-band':['https://www.acefitness.org/resources/everyone/exercise-library/10/hammer-curl/','https://www.trxtraining.com/blogs/news/bicep-workouts-at-home'],
      'hip-thrust-barbell':['https://www.trxtraining.com/blogs/news/hamstring-exercises-at-home','https://www.trxtraining.com/search?q=hip+thrust+barbell&type=article'],
      'landmine-180-barbell':['https://www.trxtraining.com/blogs/news/front-delt-exercises','https://www.trxtraining.com/search?q=landmine+press&type=article'],
      'lying-neck-extension-weighted-plate':['https://www.acefitness.org/resources/everyone/exercise-library/body-part/neck/'],
      'nordic-hamstrings-curls':['https://www.trxtraining.com/search?q=nordic+curl&type=article'],
      'pushup-weighted':['https://www.roguefitness.com/rogue-plate-carrier','https://www.trxtraining.com/blogs/news/the-beginners-guide-to-weighted-belt-and-weight-vest-workouts'],
      'side-bend-dumbbell':['https://www.trxtraining.com/search?q=side+bend&type=article'],
      'single-arm-landmine-press-barbell':['https://www.trxtraining.com/blogs/news/front-delt-exercises'],
      'single-leg-standing-calf-raise-barbell':[],
      'muscle-up-machine':['https://www.crossfit.com/essentials/the-strict-bar-muscle-up','https://www.crossfit.com/essentials/the-kipping-bar-muscle-up'],
      'press-under-barbell':['https://www.crossfit.com/essentials/foundational-movement-clean-what-is-a-clean'],
    }
    records=[]
    for url in links.get(eid,[]):
        path=pathlib.Path('/tmp/agent03-b-web-v2')/(hashlib.sha256(url.encode()).hexdigest()[:12]+'.json')
        if not path.exists():continue
        d=json.loads(path.read_text())
        records.append({k:d.get(k) for k in ['url','retrieved_at','http_status','final_url','error','html_sha256']}|{
             'used_to_unblock':False,'reason_insufficient':BLOCKED[eid],'query_or_component_is_not_exact_variant_confirmation':True})
    return records

def update_queue(tasks,packages,registry,blocks,timestamp):
    q=load(base.QUEUE_PATH);q['updated_at']=timestamp
    qb={r['exercise_id']:r for r in q['exercises']}
    new_ids=[]
    for task in tasks:
        eid=task['exercise_id'];row=qb.get(eid)
        if row is None:
            row={k:v for k,v in task.items() if k in ['exercise_id','name','equipment','primary_muscle','secondary_muscles','source_catalog_sha256','source_catalog_record_sha256','source_english_sha256']}
            q['exercises'].append(row);qb[eid]=row
        if eid not in q['eligible_exercise_ids']:new_ids.append(eid);q['eligible_exercise_ids'].append(eid)
        row.update(batch_id=task['batch_id'],status='ready_to_continue' if 'continuation' in task else 'ready',prompt_prepared=True,
                   style_version=task['style_version'],assigned_generator='generator-b',assignment_registry_path=REG,
                   current_task_path=RESUME if 'continuation' in task else f"data/batches/{task['batch_id']}.json")
    q['eligible_count']=len(q['eligible_exercise_ids']);q['prepared_count']=q['eligible_count']
    q['count_semantics']='Unique historically prompt-prepared IDs, including already generated ones; NOT a remaining-to-generate count. Current B scope is generator_b_continuation; A routing stays in unchanged next50_preparation. Previous rounds are historical.'
    q['current_blocked_ids']=[r['exercise_id'] for r in blocks];q['blocked_clarification_count']=len(blocks)
    q['blocked_clarification_path']=REVIEW;q['clarification_review_path']=REVIEW
    for p in packages:
        if p['kind']=='new_exact_ID_tasks' and p['path'] not in q['batch_paths']:q['batch_paths'].append(p['path'])
    q['generator_b_continuation']={'registry_path':REG,'packages':packages,'exercise_count':registry['exercise_count'],'blocked_path':REVIEW,
                                 'generation_authorized_now':False,'source_errors_path':ERRORS,'newly_prepared_prompt_count':registry['new_prompt_count'],
                                 'new_unique_prompt_ID_count':registry['new_prompt_count'],'not_A_reassignment':True}
    q['ownership_interpretation_update']={'historical_night_scope_count':15,'confirmed_current_preparation_owner':'agent-03','user_decision_registry':REG,
                                         'retain_scope_until_user_owner_decision':False,'not_selected_examples_are_not_assignments':True}
    q['phase_plan']['phase1']='Source-confirmed non-machine tasks first; approved general scenes/footwear recorded. Remaining blocked variants need exact technical evidence, not user guesses.'
    q['phase_plan']['phase2_execution_gate']='NEXT stage after non-machine wave; do not transfer all 114 candidates as one assignment.'
    q['last_live_check_current_B']={'checked_at':timestamp,'commits':registry['audited_commits'],'scope':'PNG Git-tree presence, actual selected assignments and saved no-PNG history; no pixel/Supabase audit.'}
    save(base.QUEUE_PATH,q)

def error_ledger(s,ev):
    problem_fields={
      'waiter-curl-dumbbell':['name','content.en.description','content.en.instructions','match.rationale'],
      'diamond-pushup':['content.en.instructions'],
      'jumping-jack':['content.en.form_cues'],
      'chest-fly-dumbbell':['content.en.instructions'],
      'cross-body-hammer-curl-dumbbell':['content.en.description','content.en.instructions','content.en.safety_note'],
      'concentration-curl-dumbbell':['content.en.description','content.en.instructions','content.en.safety_note'],
      'clean-barbell':['content.en.instructions','match.rationale'],
    }
    notes={
      'diamond-pushup':'Generic conditional clap instruction does not apply to exact diamond no-clap variant; same-ID Polish + TRX confirm fixed hand geometry.',
      'jumping-jack':'Cue Land or pedal softly contains irrelevant pedal alternative; this ID is jumping jack, no bicycle. No catalogue edit.',
      'chest-fly-dumbbell':'Generic set up on dumbbells/chest supported does not itself define supine flat bench; selected original instructions + ACE explicitly do.',
      'cross-body-hammer-curl-dumbbell':'English barbell/straight toward shoulders conflicts with equipment=dumbbell and original/Polish neutral diagonal path.',
      'concentration-curl-dumbbell':'English barbell/stand or sit conflicts with equipment=dumbbell and original/Polish seated one-arm elbow-on-inner-thigh support.',
      'clean-barbell':'Elbows under load is insufficient front-rack geometry; CrossFit explicitly elbows forward. Power catch rejected by exact match rationale; full squat scene chosen with cited support.',
    }
    for eid in BLOCKED:
        problem_fields.setdefault(eid,['content.en.description','content.en.instructions','content.en.form_cues','content.en.common_mistakes','content.en.safety_note','match.rationale'])
    from prepare_agent03_decision_review import value_at
    return {'schema_version':1,'branch':base.BRANCH,'catalog_sha256':s['catalog_sha256'],'catalog_modified':False,
            'purpose':'Separate exact source errors, contradictions and unresolved variant gaps; no silent catalogue/translation repair.',
            'exercises':[{'exercise_id':eid,'name':s['by_id'][eid]['name'],
                          'status':'blocked_variant_or_source_conflict' if eid in BLOCKED else 'rendering_resolved_catalog_unchanged',
                          'problem_fields':[{'path':p,'exact_value':copy.deepcopy(value_at(s['by_id'][eid],p))} for p in fields],
                          'problem':BLOCKED.get(eid,notes.get(eid)),
                          'comparison_source':ev[eid],'decision_source':EVIDENCE,'not_user_PNG_approval':True} for eid,fields in problem_fields.items()]}

def style_addendum():
    return '''# Затверджені сцени й виняток щодо взуття

Рішення користувача 2026-10-02. Запис: `data/style-decisions/agent-03-illustration-footwear-approved-2026-10-02.json`.
Це **вибір ілюстрації**, не твердження, що ці широкі категорії мають лише одну техніку, і не схвалення PNG.

| Точний ID | Обрана ілюстрація |
| --- | --- |
| hiit | Біг на місці, одна фаза |
| pilates | Mat Hundred, ноги в tabletop; без ременів або reformer |
| stretching | Сидяче розтягування задньої поверхні стегна, одна нога випрямлена |
| yoga | Mountain / Tadasana |
| walking | Звичайний крок із відповідним взуттям |
| hiking | Контрольований крок по нерівній поверхні з відповідним взуттям |
| snowboarding | Сумісні черевики й кріплення на дошці, захист; одна фаза ковзання |

Версія для walking/hiking/snowboarding: `v1-neutral-primary-footwear-2026-10-02`, наслідує `docs/exercise-image-style.md` та `docs/exercise-image-style-neutral-primary.md`.
Лише ці три ID мають виняток до barefoot. Для snowboarding як захисний елемент ілюстрації обрано snowboard helmet, без бренду; це не твердження про вичерпний комплект захисту. Інші вправи залишаються barefoot.
Зовнішність лисого атлетичного сріблясто-сірого чоловічого манекена, пропорції, анатомічні матеріали й чорні шорти збережені. Еталон визначає тільки зовнішність/матеріали, не позу, обладнання чи м’язи.

Затверджене правило кольорів незмінне: primary full_body/cardio/other нейтральний сріблясто-сірий; лише конкретні secondary точного ID — #F26445 на 40–50% інтенсивності. Порожній список — без підсвітки. У семи ID вище secondary порожній; не вигадувати анатомічний primary навіть для stretching/Hundred.
Для чотирьох barefoot сцен чинна версія `v1-neutral-primary-2026-10-02`; документ сцени прочитати разом зі стилем.
Одна людина, одна фаза, PNG 1024×1024 зі справжнім прозорим фоном; лише потрібні контакти поверхні, без пейзажів, тексту або колажів. Генерацію підготовчий агент не запускає.
'''

def prepare():
    assert base.git('branch','--show-current').decode().strip()==base.BRANCH
    targets=[REG,RESUME,MANIFEST,EVIDENCE,ERRORS,VALIDATION,REVIEW,DECISION,STYLE_DOC]
    assert all(not (ROOT/p).exists() for p in targets),'Never overwrite an existing preparation round'
    fetch_heads();s=n.snapshot();assignments=actual_assignments(s);timestamp=n.now()
    frozen={p:sha(p) for p in base.git('ls-files').decode().splitlines() if p not in [base.QUEUE_PATH,'.gitignore'] and not p.lower().endswith('.png')}
    nightids=[r['exercise_id'] for r in load(NIGHT)['exercises']]
    ownids=load(n.RECOMMENDATIONS)['exercise_ids'];allids=list(dict.fromkeys(nightids+ownids))
    evdoc=source_evidence(s,allids);ev={r['exercise_id']:r for r in evdoc['records']};ext=external_evidence()
    evdoc.update(prepared_at=timestamp,primary_publications=ext,
                 research_limit='Official text only. 403/404, generic homepages and unrelated variants are never confirmation. No exercise/reference photographs acquired.')
    accesses=[]
    for p in sorted(pathlib.Path('/tmp/agent03-b-web-v2').glob('*.json')):
        d=json.loads(p.read_text())
        if isinstance(d,dict) and d.get('url'):
            used=any(d['url']==v['url'] for vals in ext.values() for v in vals)
            accesses.append({k:d.get(k) for k in ['url','retrieved_at','http_status','final_url','error','html_sha256']}|{'cited_for_limited_component':used,'HTTP_200_alone_is_not_evidence':True})
    evdoc['research_access_log']=accesses
    decision={'schema_version':1,'decision_date':timestamp,'approved_by':'user in current conversation','decision_kind':'illustration_choices_and_narrow_footwear_style_addendum',
              'approved_illustration_scenes':SCENE_CHOICES,'approved_footwear_categories':FOOTWEAR,
              'illustration_selection_by_preparer':{'snowboarding':'Protective snowboard helmet, unbranded compatible boots/bindings; not a claim user selected a specific helmet/model.'},
              'source_user_text':'hiit → біг на місці, одна фаза; pilates → Hundred, ноги в tabletop; stretching → сидяче розтягування задньої поверхні стегна з однією випрямленою ногою; yoga → Mountain / Tadasana. walking і hiking → відповідне взуття; snowboarding → черевики, сумісні кріплення та захист.',
              'neutral_primary_rule_preserved_path':NEUTRAL_DOC,'neutral_primary_rule_preserved_sha256':sha(NEUTRAL_DOC),
              'neutral_primary_decision_path':'data/style-decisions/agent-03-neutral-primary-approved.json',
              'addendum_path':STYLE_DOC,'footwear_style_version':FOOTWEAR_VERSION,'exercise_ids':list(SCENE_CHOICES)+list(FOOTWEAR),
              'catalog_changed':False,'PNG_approval':False,'does_not_resolve_other_technical_blockers':True}
    save(DECISION,decision);(ROOT/STYLE_DOC).write_text(style_addendum())
    resume_rows=[];skipped=[]
    for row in load(OLD009)['exercises']:
        eid=row['exercise_id'];reason=conflict(eid,s,assignments,resume=True)
        if reason:skipped.append({'exercise_id':eid,'reason':reason,'png_sources':s['png_sources'].get(eid,[])})
        else:resume_rows.append(old009_task(row,s))
    resume={'schema_version':1,'kind':'explicit_continuation_sidecar_ORIGINAL_batch_009_NOT_new_exercise_batch',
            'batch_id':'agent-03-others-009','status':'ready','assigned_generator':'generator-b','prepared_at':timestamp,
            'original_batch_path':OLD009,'original_batch_sha256':sha(OLD009),'catalog_sha256':s['catalog_sha256'],
            'authorization':'User explicitly assigns generator B continuation of nine original 009 IDs without PNG; preserve failed calls/errors and original IDs. Overrides historical quota continuation hold, not permission to regenerate PNG.',
            'exercise_count':len(resume_rows),'exercise_ids':[r['exercise_id'] for r in resume_rows],'exercises':resume_rows,'skipped_original_records':skipped,
            'generation_calls_during_preparation':0,'shared_progress_modified':False,'generation_authorized_now':False}
    save(RESUME,resume)
    intended=[INITIAL_NIGHT[:-1],list(SCENE_CHOICES)+list(FOOTWEAR)+['cross-body-hammer-curl-dumbbell','concentration-curl-dumbbell','clean-barbell']]
    batches=[];exclusions=[]
    for number,ids in zip([26,27],intended):
        bid=f'agent-03-others-{number:03}';path=f'data/batches/{bid}.json';assert not (ROOT/path).exists(),path
        rows=[]
        for eid in ids:
            reason=conflict(eid,s,assignments)
            if reason:exclusions.append({'exercise_id':eid,'reason':reason,'sources':assignments.get(eid,[]),'png_sources':s['png_sources'].get(eid,[])})
            else:rows.append(make_task(eid,bid,s,ev[eid],ext))
        if not rows:continue
        b={'schema_version':1,'batch_id':bid,'batch_path':path,'status':'ready','owner_agent':'agent-03','branch':base.BRANCH,
           'assigned_generator':'generator-b','assignment_registry_path':REG,'prepared_at':timestamp,
           'catalog_path':base.CATALOG_PATH,'catalog_sha256':s['catalog_sha256'],'catalog_source_commit':s['commits']['origin/work'],
           'human_reference':n.prior.reference(s),'style_versions':sorted({r['style_version'] for r in rows}),
           'source_evidence_path':EVIDENCE,'exercise_count':len(rows),'exercise_ids':[r['exercise_id'] for r in rows],
           'exercises':rows,'generation_authorized_now':False,'user_review_policy':'pending until explicit user approval',
           'constraints':{'no_generator_calls_by_preparer':True,'catalog_translations_shared_progress_Supabase_immutable':True,
                          'existing_batches_001_025_and_A_immutable':True,'recheck_all_remote_PNG_and_assignments_before_each_call':True}}
        save(path,b);batches.append(b)
    save(EVIDENCE,evdoc);save(ERRORS,error_ledger(s,ev))
    blocks=blocked_rows(s,ev,ext)
    save(REVIEW,{'schema_version':1,'status':'blocked','exercise_count':len(blocks),'exercise_ids':[r['exercise_id'] for r in blocks],
                 'exercises':blocks,'source_evidence_path':EVIDENCE,'source_errors_path':ERRORS,'no_user_technique_guess_requested':True,
                 'historical_review_supersession_note':'Older user-decision tables are historical; this review/current registry supersede ownership and selected illustration decisions only.',
                 'equipment_phase':'Machines/cables/Smith next stage; existing 114 planning candidates are NOT one generator assignment.'})
    packages=[{'batch_id':resume['batch_id'],'path':RESUME,'kind':'continuation_of_009','status':'ready','exercise_count':len(resume_rows),'exercise_ids':resume['exercise_ids']}]
    packages += [{'batch_id':b['batch_id'],'path':b['batch_path'],'kind':'new_exact_ID_tasks','status':'ready','exercise_count':b['exercise_count'],'exercise_ids':b['exercise_ids']} for b in batches]
    registry={'schema_version':1,'assignment_round':ROUND,'source_branch':base.BRANCH,'source_content_parent_commit':s['commits']['HEAD'],
              'prepared_at':timestamp,'status':'ready_preparation_no_calls','assigned_generator':'generator-b','planned_worker_branch':WORKER,
              'audited_commits':s['commits'],'catalog_sha256':s['catalog_sha256'],'generator_a_assignment_unchanged_path':n.ASSIGNMENTS,
              'generator_a_assignment_unchanged_sha256':sha(n.ASSIGNMENTS),'prior_B_hold_superseded_without_modifying_A':True,
              'packages':packages,'exercise_ids':[eid for p in packages for eid in p['exercise_ids']],
              'exercise_count':sum(p['exercise_count'] for p in packages),'new_prompt_count':sum(b['exercise_count'] for b in batches),
              'continuation_count':len(resume_rows),'manifest_path':MANIFEST,'cloud_result_root':CLOUD_ROOT,'repository_result_root':GIT_ROOT,
              'user_review_policy':'pending until explicit user approval','generation_authorized_now':False,
              'historical_night_reclaimed':{'source_path':NIGHT,'source_sha256':sha(NIGHT),'exercise_ids':nightids,'new_preparation_owner':'agent-03',
                   'user_authorization':'Історичні нічні 15 поверни під свою підготовку. Це не дозвіл перегенеровувати наявні PNG.',
                   'first_eight_checked':INITIAL_NIGHT,'first_eight_ready':[eid for eid in INITIAL_NIGHT if eid in SCENES],
                   'first_eight_blocked':['waiter-curl-dumbbell'],'all_15_actual_technique_reviewed':True},
              'exclusions':exclusions,'skip_existing_PNG':skipped,'active_assignment_sources':{eid:assignments.get(eid,[]) for eid in [e for p in packages for e in p['exercise_ids']]},
              'blocked_review_path':REVIEW,'scope_limit':'Pushed Git data only; unpublished files/calls in other cloud tasks may be invisible. Runtime must fetch/recheck before every call.'}
    save(REG,registry)
    tasks=resume_rows+[r for b in batches for r in b['exercises']]
    manifest={'schema_version':1,'assignment_round':ROUND,'generator':'generator-b','planned_worker_branch':WORKER,'status':'prepared_not_started',
              'assignment_registry_path':REG,'source_branch':base.BRANCH,'generation_calls_during_this_assignment':0,
              'user_review_policy':'pending until explicit user approval','exercises':[{
                  'exercise_id':r['exercise_id'],'name':r['name'],'batch_id':r['batch_id'],'source_task_path':RESUME if r['batch_id'].endswith('009') else f"data/batches/{r['batch_id']}.json",
                  'prompt_sha256':r['prompt_sha256'],'catalog_sha256':s['catalog_sha256'],'status':'ready_to_continue' if 'continuation' in r else 'not_started',
                  'attempts':r['next_attempt_number']-1,'next_attempt_number':r['next_attempt_number'],
                  'attempt_history':copy.deepcopy(r.get('previous_attempt_history',[])),'last_error':copy.deepcopy(r.get('last_error')),
                  'history_provenance':copy.deepcopy(r.get('continuation',{}).get('source_versions',[])),
                  'assignment_generation_calls':0,'result_path':None,'result_sha256':None,'user_review':None,'agent_visual_review':'not_performed',
                  **output(r['exercise_id'],r['batch_id'],r['next_attempt_number'])} for r in tasks]}
    save(MANIFEST,manifest)
    update_queue(tasks,packages,registry,blocks,timestamp)
    with (ROOT/'.gitignore').open('a') as f:
        f.write('\n# Exact pending PNG paths for newly authorized B continuation; old A rules unchanged.\n')
        for r in tasks:f.write('!/'+r['planned_git_png_path']+'\n')
    report=validate(s,registry,resume,batches,frozen)
    save(VALIDATION,report)
    if report['errors']:raise ValueError(report['errors'])
    print(json.dumps({'packages':packages,'total_B_tasks':registry['exercise_count'],'new_prompts':registry['new_prompt_count'],'blocked':len(blocks),'validation':'passed'},ensure_ascii=False,indent=2))

def validate(s,reg,resume,batches,frozen):
    errors=[]
    def check(value,label):
        if not value:errors.append(label)
    check(base.sha((ROOT/base.CATALOG_PATH).read_bytes())==s['catalog_sha256'],'catalog_bytes_exact')
    check(len(s['by_id'])==451 and sum(len(e['content']) for e in s['by_id'].values())==4448,'451_unique_ID_4448_blocks')
    check(s['local_reference_sha256']==s['reference_sha256'],'reference_blob_SHA')
    assignments=actual_assignments(s);seen=set();orig={r['exercise_id']:r for r in load(OLD009)['exercises']}
    tasks=resume['exercises']+[r for b in batches for r in b['exercises']]
    for r in tasks:
        eid=r['exercise_id'];check(eid not in seen,'duplicate_ID:'+eid);seen.add(eid)
        check(all(r.get(k)==v for k,v in base.fields_for_id(eid,s).items()),'exact_ID_source_fields:'+eid)
        check(r['prompt_sha256']==base.sha(r['generation_prompt'].encode()),'prompt_SHA:'+eid)
        try:embedded=json.loads(r['generation_prompt'][r['generation_prompt'].index('\n{')+1:])
        except (ValueError,TypeError):embedded={};errors.append('prompt_payload_not_parseable:'+eid)
        check(embedded==r['prompt_payload'],'prompt_contains_saved_payload:'+eid)
        check(embedded.get('identity_do_not_render_as_text',{}).get('exercise_id')==eid,'prompt_contains_exact_ID:'+eid)
        check(embedded.get('identity_do_not_render_as_text',{}).get('name')==r['name'],'prompt_contains_exact_name:'+eid)
        check(all(embedded.get('exact_catalogue_source',{}).get(k)==r[k] for k in ['source_english','equipment','primary_muscle','secondary_muscles']),'prompt_contains_exact_source_fields:'+eid)
        check(r['human_reference']['sha256']==s['reference_sha256'],'reference_SHA:'+eid)
        for f in r['approved_style_files']:check(sha(f['path'])==f['sha256'],'style_file_SHA:'+eid+':'+f['path'])
        check(conflict(eid,s,assignments,resume='continuation' in r,allow_new=True) is None,'live_PNG_or_foreign_assignment:'+eid)
        check(r['planned_git_png_path']==output(eid,r['batch_id'],r['next_attempt_number'])['planned_git_png_path'],'exact_output_ID_attempt:'+eid)
        if 'continuation' in r:
            check(r['generation_prompt']==orig[eid]['generation_prompt'],'original_009_prompt_byte_exact:'+eid)
            check(r['continuation']['attempts_before']==history(eid,s)['attempts_before'],'live_counter_no_reset:'+eid)
            check(r['previous_attempt_history']==r['continuation']['attempt_history'],'historic_failed_calls_preserved:'+eid)
            check(r['next_attempt_number']==r['attempts']+1,'next_attempt_monotonic:'+eid)
        else:
            p=r['prompt_payload'];check(p['selected_render_scene']['exercise_id']==eid,'scene_exact_ID:'+eid)
            check(p['identity_do_not_render_as_text']['exercise_id']==eid,'payload_exact_ID:'+eid)
            check(all(p['exact_catalogue_source'][k]==r[k] for k in ['source_english','equipment','primary_muscle','secondary_muscles']),'payload_exact_fields:'+eid)
            check(eid not in BLOCKED and r['status']=='ready','no_unresolved_blockers:'+eid)
            check(r['attempts']==0 and r['user_review'] is None and r['result_path'] is None,'no_fake_call_PNG_approval:'+eid)
            if r['primary_muscle'] in ['full_body','cardio','other']:
                check(p['style']['primary_highlight']['hex'] is None,'approved_neutral_primary:'+eid)
                check(r['style_version'] in [NEUTRAL_VERSION,FOOTWEAR_VERSION],'approved_version:'+eid)
    check(seen==set(reg['exercise_ids']) and len(seen)==reg['exercise_count'],'registry_exact_scope')
    check(all(1<=b['exercise_count']<=10 and b['exercise_ids']==[r['exercise_id'] for r in b['exercises']] for b in batches),'new_batch_size_lists')
    for b in batches:
        for ref,paths in s['trees'].items():
            if b['batch_path'] in paths:
                check(base.sha(base.git('show',s['commits'][ref]+':'+b['batch_path']))==sha(b['batch_path']),'batch_number_conflict:'+ref+':'+b['batch_id'])
    check(reg['generator_a_assignment_unchanged_sha256']==sha(n.ASSIGNMENTS),'A_assignment_immutable')
    for path,h in frozen.items():check(sha(path)==h,'protected_file_modified:'+path)
    check(resume['original_batch_sha256']==sha(OLD009),'old_009_immutable')
    q={r['exercise_id']:r for r in load(base.QUEUE_PATH)['exercises']}
    check(all(q[r['exercise_id']]['batch_id']==r['batch_id'] for r in tasks),'own_queue_exact_route')
    queue=load(base.QUEUE_PATH)
    check(len(q)==len(queue['exercises']) and len(set(queue['eligible_exercise_ids']))==queue['eligible_count']==queue['prepared_count'],'queue_unique_counts')
    check(queue['blocked_clarification_count']==len(queue['current_blocked_ids'])==len(BLOCKED),'queue_blocked_counts')
    mf=load(MANIFEST);mrows={r['exercise_id']:r for r in mf['exercises']}
    check(set(mrows)==seen and mf['generation_calls_during_this_assignment']==0,'manifest_exact_scope_no_calls')
    for r in tasks:
        m=mrows.get(r['exercise_id'],{})
        check(m.get('prompt_sha256')==r['prompt_sha256'] and m.get('next_attempt_number')==r['next_attempt_number'],'manifest_prompt_counter:'+r['exercise_id'])
        check(m.get('attempt_history')==r.get('previous_attempt_history',[]) and m.get('last_error')==r.get('last_error'),'manifest_history_preserved:'+r['exercise_id'])
    check(not set(reg['exercise_ids'])&set(load(n.ASSIGNMENTS)['exercise_ids']),'no_A_overlap')
    return {'schema_version':1,'status':'failed' if errors else 'passed','checked_at':n.now(),'errors':errors,
            'audited_commits':s['commits'],'protected_sha256':frozen,'prepared_task_count':len(seen),
            'checks':['exact_ID_unique_source_English_equipment_muscles_hash','451_4448_catalog_immutable','prompt_reference_style_output_ID_hash',
                      'fresh_all_remote_PNG_tree_including_pending','selected_assignments_only_not_historical_examples',
                      '009_original_prompt_attempt_errors_preserved','no_foreign_job_taken_except_explicit_user_continuation',
                      'A_001_025_shared_progress_translations_approvals_immutable','no_generation_photos_pixel_QA_Supabase']}

def check_saved():
    s=n.snapshot();reg=load(REG);resume=load(RESUME);batches=[load(p['path']) for p in reg['packages'] if p['kind']=='new_exact_ID_tasks']
    report=validate(s,reg,resume,batches,load(VALIDATION)['protected_sha256'])
    print(json.dumps({'status':report['status'],'errors':report['errors'],'audited_commits':report['audited_commits'],'prepared_task_count':report['prepared_task_count']},ensure_ascii=False,indent=2))
    if report['errors']:raise SystemExit(1)

def write_handoff(core):
    assert base.git('rev-parse',core).decode().strip()==core
    reg=load(REG);stylepaths=['docs/exercise-image-style.md',NEUTRAL_DOC,STYLE_DOC]
    lines=['# Генератор B: продовження 009 і нові перевірені записи','',
           f'Джерельна гілка `{base.BRANCH}`, commit `{core}`.',
           f'Призначення `{REG}`; {reg["exercise_count"]} вправ ({reg["continuation_count"]} продовжень + {reg["new_prompt_count"]} нових prompts).',
           f'Власна нова гілка генератора `{WORKER}` від джерельного commit. Поточні чужі задачі/гілки не забирати. A: 12 вправ 024–025 незмінні.','']
    for p in reg['packages']:
        lines += [f'## `{p["batch_id"]}` — {p["exercise_count"]}, `{p["status"]}`', '',f'Точний файл: `{p["path"]}`. Порядок — як у registry.','']
        d=load(p['path']);lines += [f'- `{r["exercise_id"]}` — {r["name"]}' for r in d['exercises']]+['']
    lines += ['009 — продовження того самого пакета, не нова генерація тих самих ID. Читати sidecar, НЕ весь історичний 009: dead-hang виключено через наявний PNG. Оригінальний 009 та всі попередні помилки/спроби зберегти. hanging-knee-raise починає з attempt-3, решта восьми — attempt-1. Ці номера нижня межа: перед викликом врахувати новішу опубліковану історію.','',
              '026: сім із перших восьми нічних записів. Waiter Curl лишається blocked: два джерела повторюють звичайний двогантельний curl, а не підтверджують його відмінний варіант.',
              '027: сім затверджених загальних сцен/взуття + Cross-body Hammer Curl, Concentration Curl та Clean. Це джерельно підтверджені технічні рішення або явно названі вибори ілюстрації; не автоматичне схвалення PNG.','',
              'Еталон: `assets/exercises/biceps-curl-dumbbell.png`, SHA256 `52fef743ba2d7689aa81a8b995df3c6715cbb5d04c4bd688af4ca57b2d20057f`. Лише зовнішність/матеріали; не копіювати позу, обладнання або підсвітку.','',
              'Файли стилю: '+', '.join('`'+p+'`' for p in stylepaths)+'. Дотримуватись конкретного style_version кожного рядка: v1, v1-neutral-primary-2026-10-02 або v1-neutral-primary-footwear-2026-10-02.',
              'Broad primary full_body/cardio/other — сріблясто-сірий нейтральний; лише явно зазначені secondary #F26445 на 40–50%. Порожній secondary — без підсвітки. Взуття дозволено тільки для walking/hiking/snowboarding.','',
              f'Локальна окрема папка: `{CLOUD_ROOT}/<batch_id>/<exercise_id>/attempt-N.png`.',
              f'Git PNG: `{GIT_ROOT}/<batch_id>/<exercise_id>/attempt-N.png`.',
              f'Власний manifest: `{MANIFEST}`. Дописувати історію, не скидати лічильники й не стирати старі помилки. Source-task path, prompt/catalog SHA256, фактичний PNG path/SHA256, час, виклик/помилку зберігати для exact ID.','',
              'Перед КОЖНИМ викликом fetch усі доступні гілки; звірити PNG, manifests і активні призначення. Будь-який PNG, зокрема pending/rejected — skip без повторної генерації. Нове стороннє призначення/спроба — conflict і skip; цей registry дозволяє тільки явно описане продовження старого 009. Незапушені файли інших хмарних задач можуть бути невидимі.',
              'Генерація тільки у хмарі вбудованим imagegen; не зовнішні paid API. user_review=pending для кожного нового PNG до явного рішення користувача. Агентський технічний QA не є схваленням.',
              'Після кожного пакета зберегти PNG та manifest, commit і push власної гілки, перевірити віддалені файли. При quota/usage_limit_reached/HTTP429 — зберегти помилку й ЗУПИНИТИСЯ без повторних викликів; ID залишаються в поточному пакеті. Інші помилки записати, без автоматичних повторів.',
              'Каталог, усі переклади, work, shared progress, наявні PNG/схвалення, чужі результати й Supabase не змінювати. Тренажери/троси/Сміт — наступний етап; жодних 114 завдань тут немає.','',
              f'Технічні джерела: `{EVIDENCE}`. Помилки вихідних описів: `{ERRORS}`. Решта {len(BLOCKED)} blocked: `{REVIEW}`. Не вгадувати їхню техніку й не включати до цього доручення.','']
    (ROOT/HANDOFF).write_text('\n'.join(lines))
    message=f'''Ти генератор B. Працюй тільки в хмарі. Джерело: romanthoruk2008-pixel/lightweight-exercises-photo, гілка {base.BRANCH}, commit {core}. Створи власну гілку {WORKER} саме від цього commit; поточні завдання інших агентів не забирай.

Прочитай {REG}. Виконуй ПО ПОРЯДКУ лише:
1. agent-03-others-009 — {reg['packages'][0]['exercise_count']} продовжень, файл {RESUME}; старий пакет не змінювати, dead-hang не включати. hanging-knee-raise: наступна спроба 3, решта восьми: спроба 1; всю попередню історію й помилки зберегти.
2. agent-03-others-026 — {next(p['exercise_count'] for p in reg['packages'] if p['batch_id'].endswith('026'))} вправ, data/batches/agent-03-others-026.json.
3. agent-03-others-027 — {next(p['exercise_count'] for p in reg['packages'] if p['batch_id'].endswith('027'))} вправ, data/batches/agent-03-others-027.json.

Еталон assets/exercises/biceps-curl-dumbbell.png (SHA256 52fef743ba2d7689aa81a8b995df3c6715cbb5d04c4bd688af4ca57b2d20057f) — лише зовнішність/матеріали. Стиль: docs/exercise-image-style.md, {NEUTRAL_DOC}, {STYLE_DOC}; версію брати з exact-ID рядка. Для full_body/cardio/other тіло нейтральне; secondary тільки з цього ID, #F26445 40–50%; порожній список — без підсвітки. Взуття лише для трьох дозволених ID. Поза/хват/опори/обладнання — з готового prompt та джерельно підтвердженого рішення, не з еталона.

PNG локально: {CLOUD_ROOT}/<batch_id>/<exercise_id>/attempt-N.png; PNG у Git: {GIT_ROOT}/<batch_id>/<exercise_id>/attempt-N.png. Власний manifest {MANIFEST}; дописувати, не стирати історію 009. Перед кожним викликом fetch усі доступні гілки, перевірити PNG та призначення: існуючий PNG будь-якого статусу — skip; нове стороннє призначення — conflict/skip. Непушені дані інших задач можуть бути невидимі.

Нові PNG: user_review=pending до явного схвалення користувача. Після КОЖНОГО пакета зберегти результати/manifest, commit і push власної гілки та перевірити remote. При quota/HTTP429/usage_limit_reached записати помилку й одразу зупинитися БЕЗ повторних викликів; вправи залишаються у цьому ж пакеті. Автоматичні повтори заборонені.

A — 12 вправ 024–025 — не чіпати. Blocked, тренажери/троси/Сміт не виконувати. Каталог/переклади/work/shared progress/схвалення/чужі PNG/Supabase не змінювати. Генерація лише вбудованим imagegen у хмарі. Детальний handoff: {HANDOFF} у підготовчій гілці (опублікований після source commit); його можна прочитати через git show актуального origin/{base.BRANCH}, не переносити інші завдання у свою гілку.
'''
    (ROOT/MESSAGE).write_text(message)
    print(message)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--check',action='store_true');p.add_argument('--handoff-source-commit');a=p.parse_args()
    if a.check:check_saved()
    elif a.handoff_source_commit:write_handoff(a.handoff_source_commit)
    else:prepare()
