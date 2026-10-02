#!/usr/bin/env python3
"""Record exact-ID decisions and unassigned prompts, preserving existing jobs."""
import collections
import copy
import datetime
import hashlib
import json
from pathlib import Path
import sys
import prepare_agent03_generator_b as b

base=b.base
ROOT=b.ROOT
ROUND='agent-03-user-answers-2026-10-03'
DECISIONS=f'data/technique-decisions/{ROUND}.json'
PREPARED=f'data/queues/{ROUND}-prepared.json'
BLOCKED=f'data/queues/{ROUND}-blocked.json'
RESEARCH=f'data/audits/{ROUND}-research.json'
CHECK=f'data/audits/{ROUND}-validation.json'
DOC=f'docs/{ROUND}-handoff.md'
WEB=Path('/tmp/agent03-answers-web')

APPROVALS={
 'floor-triceps-dip':'floor triceps dip — це, поняв, долоні на підлозі стоять',
 'chest-dip-weighted-machine':'це бруся. Типу ти нахилений вперед ... роби обтяження на поясі',
 'drag-curl-barbell':'Це справжній drag curl ... Оце воно.',
 'feet-up-bench-press-barbell':'стопи по повітрі, тобто ноги випрямлені ... Оце feet up bench press.',
 'hammer-curl-band-resistance-band':'Стрічка під стоп... Да-да-да, оце під стопами. Всьо нормально.',
 'hip-thrust-barbell':'роби так, як ти це рекомендуєш: верхня спина на краю лави',
 'landmine-180-barbell':'стегно-стегно має бути. Так, як ти рекомендуєш',
}
SCENES={
 'floor-triceps-dip':('Small controlled elbow-bend phase','Sit with knees bent, hips lifted only slightly off floor; chest open, elbows point back and bend a short distance, shoulders controlled.','Palms ON FLOOR behind hips, fingers forward.','Both palms and both feet on floor, knees bent; no bench, chair or parallel bars.','Elbow flexion lowers hips a short controlled distance, then extension raises them. Do not swing hips or deepen into a parallel-bar dip.'),
 'chest-dip-weighted-machine':('Controlled lower phase on parallel bars','Torso slightly inclined forward, shoulders down; elbows bend until upper arms approach parallel to floor without loss of control; legs still and clear of floor.','Both palms hold parallel dip handles, closed grip.','Two STATIC parallel bars; weight attached to waist dip belt with secure chain. One compact plate shown hanging clear between legs; no vest, assistance platform or moving machine.','Body lowers between bars and presses back up, one selected lower phase. Belt choice user-approved; compact single plate is a compatible illustration selection, not a numerical load prescription.'),
 'drag-curl-barbell':('Mid drag-curl rise','Stand tall, trunk stable; elbows move BACK behind ribs as the bar rises close along front of torso; shoulders down, no torso swing.','Supinated/underhand closed grip on one free barbell, both hands.','Both feet planted shoulder-width; one free barbell, no bench or cable station.','Drag the bar upward along body by moving elbows backward, then lower along same path; not ordinary fixed-upper-arm forward curl.'),
 'feet-up-bench-press-barbell':('Controlled lower press phase, straight legs afloat','Lie supine on FLAT bench with head, shoulder blades and pelvis supported; BOTH legs straight and held off floor, feet unsupported in air. Bar above chest, elbows controlled.','Closed overhand grip with thumbs around one free barbell; wrists stacked and forearms aligned under bar.','Flat bench supports trunk, neither foot touches bench or floor. Free barbell in both hands; passive rack safeties outside bar path, no Smith rails or spotter figure.','Lower bar toward chest without bounce and press upward; freeze lower phase. Straight knees explicitly chosen by user, superseding earlier bent-knee proposal.'),
 'hammer-curl-band-resistance-band':('Neutral-grip curl rise','Stand tall, upper arms beside ribs, elbows close and stationary; forearms flex toward shoulders without torso swing.','One compatible band handle per hand, NEUTRAL palms-facing-each-other grip, wrists neutral.','Middle of one resistance band securely pinned beneath BOTH feet; two band ends rise from feet to handles. No door/wall anchor or cable stack.','Flex elbows to lift neutral handles toward shoulders, lower under tension. Under-foot anchor user-approved; compatible neutral handles follow the referenced proposal.'),
 'hip-thrust-barbell':('Controlled full hip-extension endpoint','Upper back/shoulders supported at EDGE of flat bench, pelvis OUTSIDE bench; hips raised until torso and thighs align, knees bent, trunk braced.','Both hands stabilize bar with overhand contact just outside thighs.','Upper back on bench; both feet flat on floor; ONE free barbell across hip crease/pelvis. Pelvis never lies on bench; no machine or pad invention.','Drive hips upward from outside bench and lower with upper-back contact maintained; one endpoint, not a whole-body lying bench hip lift.'),
 'landmine-180-barbell':('One right-hip endpoint of hip-to-hip arc','Stand shoulder-width, knees softly bent, feet planted; trunk rotates under control, both hands bring loaded FREE end toward right hip.','Both hands grip movable free-end sleeve securely; no grip on fixed pivot end.','Opposite bar end secured in standard unbranded floor landmine pivot; all pivot/bar/hand contacts visible; no second person.','Controlled arc from one HIP to the other HIP through front of body. Do not end at opposite shoulder, perform a press, or add motion arrows.'),
 'lying-neck-extension':('Gentle unloaded neutral-to-extension phase','Lie FACE DOWN with chest and stomach supported on flat bench, head just beyond edge and free; shoulders relaxed, feet on ground for stability. Head near neutral with only small controlled extension.','Hands free, no resistance or head weight.','Chest/stomach supported by bench; feet on floor; HEAD DOES NOT bear weight on bench/floor, no headrest pushing or four-point crawling.','Gently extend head a small distance and return smoothly toward neutral; no exaggerated backward crank. UNLOADED variant only.'),
 'lying-neck-extension-weighted-plate':('Small controlled plate-resisted neck-extension phase','Lie FACE DOWN with chest and stomach supported on flat bench, head free just beyond edge, shoulders relaxed; small neck extension near neutral, torso still.','BOTH hands hold edges of ONE light plate securely against back of head/occiput; plate never unsupported.','Torso supported on bench and feet stable on floor; head has NO bench/floor contact or load-bearing head support. No neck harness or triceps movement.','Small neck extension against plate and smooth return; no swing or forced end range. Torso support, not head contact, defines supported position.'),
 'seated-incline-curl-dumbbell':('Controlled bilateral curl rise','Sit with back supported by 45-degree incline bench, arms hanging vertically by sides BEHIND inclined torso; elbows stay beside body without resting upper arms on bench, trunk steady.','One dumbbell in EACH hand, palms forward/supinated, wrists aligned.','Pelvis/back on incline bench, both feet planted; upper arms free, no preacher pad or thigh elbow support.','Flex elbows to curl dumbbells toward shoulders and lower smoothly; one mid-lift phase with no elbow swing.'),
}

def pub(url,quotes,scope):
    d=json.loads((WEB/(hashlib.sha256(url.encode()).hexdigest()[:12]+'.json')).read_text())
    assert d['http_status']==200 and d['final_url']==url and all(q in d['text'] for q in quotes)
    return {k:d[k] for k in ['url','final_url','retrieved_at','http_status','html_sha256']}|{
        'publisher':'StrengthLog official first-party exercise library' if 'strengthlog' in url else 'Rogue equipment manufacturer',
        'extracted_text_sha256':base.sha(d['text'].encode()),'quotes':quotes,'scope':scope,
        'muscle_targets_from_publisher_used':False,'images_or_videos_downloaded':False}

def publications():
    neck=pub('https://www.strengthlog.com/lying-neck-extension/',[
        'Lie face down on a flat bench with your head hanging just off the edge.',
        'Position your body so your chest and stomach are supported. If you want to, you can keep your feet on the ground for stability.',
        'Place a weight plate on the back of your head, holding it with both hands.',
        'You can do it without any resistance or use a weight plate to progressively overload the neck extensors for more strength, muscle growth, and endurance.'],
        'Exact prone bench-supported neck extension with FREE head, unloaded option and both-hand plate variant. Never import publisher muscle lists or claim a medical recommendation.')
    incline=pub('https://www.strengthlog.com/incline-dumbbell-curl/',[
        'Grab a pair of dumbbells, and sit down on an inclined bench. Let your arms hang straight down by your sides.',
        'Lift the dumbbells with control, by flexing your elbows.'],
        'Same seated incline two-dumbbell curl; arms hang freely behind inclined torso. 45-degree bench and supinated grip come from exact catalogue ID, not guessed from another exercise.')
    drag=pub('https://www.strengthlog.com/drag-curl/',[
        'Stand with feet shoulder-width apart, holding a barbell with palms facing up in a relaxed underhand grip.',
        'Pull the bar up along your body by driving your elbows back, creating a “dragging” motion, unlike regular curls where you bend the elbow to lift the weight forward in a rotating movement.'],
        'Exact standing free-barbell drag curl corroborates user-selected elbows-back/bar-close variant.')
    belt=pub('https://www.roguefitness.com/rogue-dip-belt',[
        'Each Dip Belt comes equipped with a reinforced, comfort-fit nylon body, heavy stitching, a 30" total chain length, and a pair of straight-gate, locking carabiners.'],
        'Belt-chain secure loading component only; user selects parallel-bar chest dip. Do not copy brand or numerical chain length.')
    bench=pub('https://www.strengthlog.com/feet-up-bench-press/',[
        'Grip the bar slightly wider than shoulder-width apart.',
        'Lift your feet up and hold them in the air.'],
        'Exact feet-up free-barbell bench-press grip/support and floating feet; STRAIGHT knees explicitly chosen by user, not inferred from a demonstration.')
    bench_grip=pub('https://www.strengthlog.com/bench-press/',[
        'Your thumb must be on the opposing side of your other fingers. Meaning that you grip around the bar.'],
        'Closed-thumb grip component of the same free-barbell bench press only; does not determine floating-leg position or add leg drive.')
    return {'lying-neck-extension':[neck],'lying-neck-extension-weighted-plate':[neck],
            'seated-incline-curl-dumbbell':[incline],'drag-curl-barbell':[drag],
            'chest-dip-weighted-machine':[belt],'feet-up-bench-press-barbell':[bench,bench_grip]}

def make_row(eid,s,pubs):
    row=base.fields_for_id(eid,s);scene=b.n.prior.scene(eid,SCENES[eid],b.CAMERA)
    resolution={'status':'resolved','decision_kind':'user_selected_variant' if eid in APPROVALS else 'exact_variant_source_confirmation',
                'user_response_excerpt':APPROVALS.get(eid),'excerpt_is_shortened_not_verbatim_full_transcript':eid in APPROVALS,
                'user_decision_path':DECISIONS,'primary_publications':pubs.get(eid,[]),
                'catalog_conflicts_preserved_path':b.ERRORS,'catalog_modified':False,'PNG_approval':False}
    if eid in ['lying-neck-extension','lying-neck-extension-weighted-plate']:
        resolution['user_context']='User describes torso on bench and says head must not bear against support; exact prone orientation/foot support and unloaded/plate variants confirmed independently by cited instructions.'
    if eid=='seated-incline-curl-dumbbell':resolution['user_context']='User requests independent research, not approval of our prior proposal. Source confirms freely hanging arms; catalogue supplies seated 45-degree bench, two dumbbells, palms forward.'
    style=copy.deepcopy(base.STYLE)
    style['no_invention']='Exact-ID catalogue controls name, English and muscles. Render ONLY selected scene and documented user/source resolution. No copying reference pose/equipment/highlights or importing external muscle lists.'
    root=f'/workspace/exercise-image-results/{ROUND}';relative=f'{eid}/attempt-1.png'
    payload={'identity_do_not_render_as_text':{'exercise_id':eid,'name':row['name'],'catalog_sha256':s['catalog_sha256'],'catalog_record_sha256':row['source_catalog_record_sha256']},
             'exact_catalogue_source':{k:copy.deepcopy(row[k]) for k in ['source_english','equipment','primary_muscle','secondary_muscles']},
             'human_reference':b.n.prior.reference(s),'style':style,'approved_style_files':[{'path':'docs/exercise-image-style.md','sha256':s['style_sha256']}],
             'selected_render_scene':scene,'technique_resolution':resolution,
             'source_use_rule':'Raw source text remains verbatim for provenance. Explicit scene and documented decision override only recorded disputed generic fields. Never substitute another exercise or infer muscle targets.'}
    prompt='Create exactly ONE square 1024x1024 transparent PNG of this exact exercise and ONE selected phase. Metadata must never appear as image text.\n'+json.dumps(payload,ensure_ascii=False,sort_keys=True,indent=2)
    row.update(status='ready_unassigned',technical_status='ready',assigned_generator=None,batch_id=None,prompt_prepared=True,
               generation_authorized_now=False,generation_prompt=prompt,prompt_payload=payload,prompt_sha256=base.sha(prompt.encode()),
               scene=scene,technique_resolution=resolution,style_version='v1',approved_style_files=payload['approved_style_files'],human_reference=payload['human_reference'],
               source_catalog_commit=s['commits']['origin/work'],source_url=b.n.CATALOG_URL+s['commits']['origin/work']+'/'+base.CATALOG_PATH,
               source_selector=f'exercises[id="{eid}"]',planned_png_path=root+'/'+relative,
               planned_git_png_path=f'assets/exercises/pending/{ROUND}/'+relative,
               output_assignment_policy='Prepared staging paths only; assign an execution owner/batch and live-recheck before any call. Explicitly rebind paths if necessary, retaining ID and prompt hash.',
               attempts=0,result_path=None,result_sha256=None,user_review=None,future_user_review_policy='pending until explicit user approval',agent_visual_review='not_performed')
    return row

def main():
    assert base.git('branch','--show-current').decode().strip()==base.BRANCH
    assert all(not (ROOT/p).exists() for p in [DECISIONS,PREPARED,BLOCKED,RESEARCH,CHECK,DOC]),'Never overwrite prior response round'
    frozen={p:b.sha(p) for p in base.git('ls-files').decode().splitlines() if p!=base.QUEUE_PATH and not p.lower().endswith('.png')}
    b.fetch_heads();s=b.n.snapshot();assignments=b.actual_assignments(s);pubs=publications()
    stamp=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=3))).isoformat()
    rows=[];exclusions=[]
    for eid in SCENES:
        reason=b.conflict(eid,s,assignments)
        if reason:exclusions.append({'exercise_id':eid,'reason':reason,'PNG_sources':s['png_sources'].get(eid,[]),'assignment_sources':assignments.get(eid,[])})
        else:rows.append(make_row(eid,s,pubs))
    records=[{'exercise_id':r['exercise_id'],'status':'technique_resolved_prompt_prepared_unassigned','resolution':r['technique_resolution']} for r in rows]
    equipment={
       'chest-press-machine':{'spoken_label':'Chest press machine','selected_configuration':'Seated LEVER chest press, back supported, two handles press forward away from torso.',
                             'resolution_kind':'user_choice_and_exact_dataset_0576_confirmation','phase':2,'status':'equipment_choice_confirmed_held_next_stage'},
       'decline-bench-press-machine':{'spoken_label':'Decline bench press machine','selected_configuration':'Lying on declined bench between TWO independent plate-loaded lever arms; each arm has plate loading and its own hand contact. Not free barbell or Smith.',
                                    'resolution_kind':'user_equipment_choice','phase':2,'status':'equipment_choice_confirmed_geometry_validation_next_stage',
                                    'not_inferred':['exact bench angle','number/mass of plates','specific brand/model','exact foot restraint design'],
                                    'next_action':'Validate declined body position, feet secured from exact catalogue, and compatible independent lever/handle geometry before rendering. Manufacturer access failures are not evidence.'},
       'inverted-row-machine':{'spoken_label':'Military draw machine / Australian row','selected_configuration':'Australian/inverted bodyweight row beneath a FIXED Smith bar; bar locked at waist height, heels grounded, body straight, chest pulls toward stationary bar.',
                               'resolution_kind':'user_illustration_equipment_choice','ID_mapping_basis':'Original exact-ID question offered fixed Smith bar; user identifies Australian horizontal row and stationary Smith, not a similarly named exercise.',
                               'phase':2,'status':'fixed_Smith_choice_confirmed_held_next_stage','bar_must_not_move':True},
    }
    for eid,decision in equipment.items():
        decision.update(base.fields_for_id(eid,s))
        decision['source_question_path']='data/queues/agent-03-user-decisions-2026-10-02.json'
    pending={
       'bicycle-crunch':{'confirmed':'On floor, knees bent about 90 degrees, opposite elbow toward opposite knee.',
                        'not_confirmed':'Does other leg stay bent in tabletop or alternately extend? Need distinguish two catalogue IDs.', 'status':'awaiting_variant_distinction'},
       'bicycle-crunch-raised-legs':{'confirmed':'Opposite elbow/knee movement; legs must not rest on floor.',
                                    'not_confirmed':'Exact bent/straight alternating configuration versus first bicycle ID is unclear in spoken response.', 'status':'awaiting_variant_distinction'},
    }
    review=b.load(b.REVIEW);resolved=set(r['exercise_id'] for r in rows);remaining=[copy.deepcopy(r) for r in review['exercises'] if r['exercise_id'] not in resolved]
    for r in remaining:
        if r['exercise_id'] in pending:r['user_partial_answer']=pending[r['exercise_id']];r['block_reason']=pending[r['exercise_id']]['not_confirmed']
    seen_existing=[]
    for eid in ['cross-body-hammer-curl-dumbbell','concentration-curl-dumbbell','zottman-curl-dumbbell']:
        seen_existing.append({'exercise_id':eid,'PNG_sources':s['png_sources'].get(eid,[]),'assignment_sources':assignments.get(eid,[]),'action':'retain existing PNG/assignment; no new prompt or task',
                             'label_ambiguity':'User said Zottman but described seated single dumbbell with elbow on inner thigh, which describes Concentration; do not map this approval to either ID until confirmed.' if eid!='cross-body-hammer-curl-dumbbell' else None})
    decision={'schema_version':1,'recorded_at':stamp,'branch':base.BRANCH,'catalog_sha256':s['catalog_sha256'],'audited_commits':s['commits'],
              'user_approved_variants':APPROVALS,'source_confirmed_variants':['lying-neck-extension','lying-neck-extension-weighted-plate','seated-incline-curl-dumbbell'],
              'records':records,'equipment_choices_next_stage':equipment,'partial_answers_not_guessed':pending,'existing_tasks_unchanged':seen_existing,
              'source_catalog_unchanged':True,'PNG_approvals_unchanged':True,'new_execution_assignments':False,'generation_calls':0,
              'old_A_024_025_and_B_009_026_027_unchanged':True,'prepared_path':PREPARED,'remaining_blocked_path':BLOCKED,'research_path':RESEARCH}
    b.save(DECISIONS,decision)
    b.save(PREPARED,{'schema_version':1,'queue_id':ROUND,'status':'ready_unassigned','exercise_count':len(rows),'exercise_ids':[r['exercise_id'] for r in rows],
                     'exercises':rows,'new_execution_assignments':False,'generation_authorized_now':False,'decision_path':DECISIONS,'exclusions':exclusions,
                     'catalog_sha256':s['catalog_sha256'],'style_version':'v1','human_reference':b.n.prior.reference(s)})
    b.save(BLOCKED,{'schema_version':1,'exercise_count':len(remaining),'exercise_ids':[r['exercise_id'] for r in remaining],'exercises':remaining,
                    'current_decision_path':DECISIONS,'prior_review_retained_path':b.REVIEW,'equipment_next_stage_path':DECISIONS,
                    'generation_authorized_now':False,'no_missing_user_answer_treated_as_approval':True})
    accesses=[]
    for p in sorted(WEB.glob('*.json')):
        d=json.loads(p.read_text())
        if isinstance(d,dict) and 'url' in d:accesses.append({k:d.get(k) for k in ['url','retrieved_at','http_status','final_url','error','html_sha256']})
    b.save(RESEARCH,{'schema_version':1,'catalog_sha256':s['catalog_sha256'],'publications_by_exact_ID':pubs,'access_log':accesses,
                    'scope':'Written first-party technical demonstrations/instructions only. No photos/video downloaded, no soft-404/403 or generic different variant used as confirmation.',
                    'user_decisions_are_not_source_corrections':True})
    q=b.load(base.QUEUE_PATH);qb={r['exercise_id']:r for r in q['exercises']}
    for r in rows:
        eid=r['exercise_id'];assert eid not in qb,'Existing prepared row cannot be reassigned: '+eid
        qr={k:v for k,v in r.items() if k in ['exercise_id','name','equipment','primary_muscle','secondary_muscles','source_catalog_sha256','source_catalog_record_sha256','source_english_sha256','status','style_version','prompt_prepared','batch_id','assigned_generator']}
        qr.update(current_task_path=PREPARED,technique_decision_path=DECISIONS)
        q['exercises'].append(qr);q['eligible_exercise_ids'].append(eid)
    q.update(updated_at=stamp,eligible_count=len(q['eligible_exercise_ids']),prepared_count=len(q['eligible_exercise_ids']),
             current_blocked_ids=[r['exercise_id'] for r in remaining],blocked_clarification_count=len(remaining),
             blocked_clarification_path=BLOCKED,clarification_review_path=BLOCKED)
    q['latest_user_answers']={'decision_path':DECISIONS,'ready_unassigned_prompt_count':len(rows),'ready_unassigned_path':PREPARED,'blocked_count':len(remaining),
                              'existing_generator_routes_unchanged':True,'equipment_choices_next_stage_count':len(equipment),'no_generation':True}
    q['phase_plan']['latest_equipment_decisions_path']=DECISIONS
    b.save(base.QUEUE_PATH,q)
    checks=[]
    assert len(s['by_id'])==451 and sum(len(e['content']) for e in s['by_id'].values())==4448
    assert len(set(r['exercise_id'] for r in rows))==len(rows)
    for r in rows:
        eid=r['exercise_id'];assert all(r[k]==v for k,v in base.fields_for_id(eid,s).items())
        assert r['prompt_sha256']==base.sha(r['generation_prompt'].encode())
        assert json.loads(r['generation_prompt'][r['generation_prompt'].index('\n{')+1:])==r['prompt_payload']
        assert r['prompt_payload']['identity_do_not_render_as_text']['exercise_id']==eid
        assert all(r['prompt_payload']['exact_catalogue_source'][k]==r[k] for k in ['source_english','equipment','primary_muscle','secondary_muscles'])
        assert b.conflict(eid,s,assignments) is None
        assert r['assigned_generator'] is None and r['batch_id'] is None and r['attempts']==0 and r['user_review'] is None
        assert f'/{eid}/attempt-1.png' in r['planned_png_path']
    for p,h in frozen.items():assert b.sha(p)==h,p
    assert len(set(q['eligible_exercise_ids']))==q['eligible_count']==q['prepared_count']
    b.save(CHECK,{'schema_version':1,'status':'passed','checked_at':stamp,'catalog_unique_ID_count':451,'language_blocks':4448,'prepared_count':len(rows),
                  'remaining_blocked_count':len(remaining),'audited_commits':s['commits'],'protected_sha256':frozen,
                  'checks':['exact-ID source English/equipment/muscles and prompt payload','no existing PNG or selected assignment','no duplicate ID',
                            'old A/B batches manifests registry prompts and review approvals immutable','own unassigned queue only','no generation or Supabase']})
    lines=['# Відповіді користувача — 2026-10-03','',f'Підготовлено **{len(rows)} нових prompts**, статус **ready_unassigned**. Нових пакетів або призначень генераторам не створено.',
           f'Точні записи: `{PREPARED}`. Рішення: `{DECISIONS}`. Джерела/цитати/SHA256: `{RESEARCH}`.','',
           '## Готові до майбутнього призначення','', '| exercise_id | Підстава |','| --- | --- |']
    lines += [f'| `{r["exercise_id"]}` | '+('Явний вибір варіанта користувачем' if r['exercise_id'] in APPROVALS else 'Прямі технічні інструкції StrengthLog; не схвалення рекомендації від імені користувача')+' |' for r in rows]
    lines += ['', 'Feet-up bench press: **прямі ноги у повітрі**, не попередня пропозиція зі зігнутими колінами. Head support у neck extension: **тулуб на лаві, голова вільна за краєм**; weighted варіант — один легкий млинець на потилиці, обидві руки його утримують. Джерело прямо допускає unloaded варіант.','',
              'Підтвердження seated incline curl: руки вільно звисають за нахиленим тулубом; не лежать на bench pad. 45° і supinated grip беруться з цього самого ID.','',
              '## Обладнання наступного етапу','',
              '- chest-press-machine: сидячий важільний жим зі спинкою й двома ручками.','- decline-bench-press-machine: лежачий declined жим на двох незалежних plate-loaded важелях; не free barbell/Smith. Кількість дисків, кут і конкретний бренд не вигадані; детальну геометрію опор перевірити під час наступного етапу.','- inverted-row-machine: Australian row на **зафіксованому грифі Сміта**. Прив’язка за відповіддю на точне попереднє питання й рухом; spoken Military draw не створює нового ID.','',
              'Ці три конструкції зафіксовано як рішення, без нових generation tasks. Фото стандартного сумісного обладнання не вимагалися. Невдалі запити до виробника не є технічним підтвердженням.','',
              '## Що не змінено й що потребує уточнення','',
              '- A 024–025 і B 009/026/027, їхні prompts, manifests та призначення без змін. Cross-body Hammer Curl і Concentration Curl вже у 027, повторно не включені.','- Zottman Curl має PNG; його не змінено. Опис однієї гантелі з ліктем на внутрішній стороні стегна відповідає Concentration Curl. Суперечливу усну назву не вважали exact-ID схваленням.','- Bicycle Crunch: підтверджено підлогу, bent knees ~90° і протилежні лікоть/коліно. Треба розрізнити з Raised Legs: чи перший тримає другу ногу зігнутою, а другий чергує зігнуту/випрямлену над підлогою? До відповіді не вигадувати різницю двох ID.','',
              f'Залишок **{len(remaining)} blocked**: `{BLOCKED}`. Попередній source-error ledger `{b.ERRORS}` залишено без змін; нові рішення документують лише rendering override, не змінюють каталог/переклади.',
              'Обмеження: лише опубліковані Git дані; непушені результати інших хмарних задач можуть бути невидимі. Перед призначенням/викликом повторно звірити PNG та чинні jobs. Генерація, PNG QA, Supabase і зміна схвалень не виконувалися.','']
    (ROOT/DOC).write_text('\n'.join(lines))
    print(json.dumps({'prepared_count':len(rows),'prepared_IDs':[r['exercise_id'] for r in rows],'blocked_count':len(remaining),'equipment_decisions_next_stage':list(equipment),'validation':'passed'},ensure_ascii=False,indent=2))

def validate_saved():
    s=b.n.snapshot();assignments=b.actual_assignments(s);prepared=b.load(PREPARED);q=b.load(base.QUEUE_PATH)
    rows=prepared['exercises'];seen=set();errors=[]
    def check(ok,why):
        if not ok:errors.append(why)
    for r in rows:
        eid=r['exercise_id'];check(eid not in seen,'duplicate:'+eid);seen.add(eid)
        check(all(r[k]==v for k,v in base.fields_for_id(eid,s).items()),'exact_source:'+eid)
        check(r['prompt_sha256']==base.sha(r['generation_prompt'].encode()),'prompt_SHA:'+eid)
        payload=json.loads(r['generation_prompt'][r['generation_prompt'].index('\n{')+1:])
        check(payload==r['prompt_payload'],'prompt_payload:'+eid)
        check(payload['identity_do_not_render_as_text']['exercise_id']==eid and payload['identity_do_not_render_as_text']['name']==r['name'],'prompt_identity:'+eid)
        check(all(payload['exact_catalogue_source'][k]==r[k] for k in ['source_english','equipment','primary_muscle','secondary_muscles']),'prompt_source:'+eid)
        check(b.conflict(eid,s,assignments) is None,'live_PNG_or_job:'+eid)
        check(r['human_reference']['sha256']==s['reference_sha256'],'human_reference:'+eid)
        check(all(b.sha(f['path'])==f['sha256'] for f in r['approved_style_files']),'style_SHA:'+eid)
        check(r['assigned_generator'] is None and r['batch_id'] is None and r['attempts']==0 and r['user_review'] is None,'no_job_call_or_approval:'+eid)
        check(f'/{eid}/attempt-1.png' in r['planned_png_path'] and f'/{eid}/attempt-1.png' in r['planned_git_png_path'],'future_PNG_ID:'+eid)
    for path,expected in b.load(CHECK)['protected_sha256'].items():check(b.sha(path)==expected,'protected_file:'+path)
    check(len(s['by_id'])==451 and sum(len(e['content']) for e in s['by_id'].values())==4448,'catalog_counts')
    check(prepared['exercise_ids']==[r['exercise_id'] for r in rows] and prepared['exercise_count']==len(seen),'prepared_scope')
    check(len(set(q['eligible_exercise_ids']))==q['eligible_count']==q['prepared_count'],'queue_counts')
    check(set(q['current_blocked_ids'])==set(b.load(BLOCKED)['exercise_ids']),'blocked_scope')
    print(json.dumps({'status':'failed' if errors else 'passed','errors':errors,'prepared_count':len(rows),'blocked_count':len(q['current_blocked_ids']),'audited_commits':s['commits']},ensure_ascii=False,indent=2))
    if errors:raise SystemExit(1)

if __name__=='__main__':
    if '--check' in sys.argv:validate_saved()
    else:main()
