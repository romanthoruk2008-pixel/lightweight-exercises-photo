#!/usr/bin/env python3
"""Exact-ID decision sheet and equipment phase plan; no calls or assignments."""
import collections
import copy
import json
from pathlib import Path
import prepare_agent03_next50 as n

REVIEW='data/queues/agent-03-user-decisions-2026-10-02.json'
TAIL='data/queues/agent-03-equipment-tail-queue.json'
DOC='docs/agent-03-user-decisions-2026-10-02.md'
NIGHT='data/batches/night-2026-10-01-clarifications.json'
MACHINE_BATCH='data/batches/agent-02-machines-001.json'
MACHINE_MANIFEST='data/batches/agent-02-machines-001-manifest.json'

# Proposals never become approvals. Source-confirmed construction is recorded
# separately from conflicting technique and a prepared/assigned generation task.
EQUIPMENT={
 'chest-dip-assisted-machine':('resolved_from_exact_bound_source','Тренажер для assisted dip з допоміжною платформою під КОЛІНАМИ; паралельні ручки.','Відповідь не потрібна: dataset 0009 прямо визначає коліна на подушці.','source_confirmation',['match.rationale','content.en.safety_note']),
 'chest-press-machine':('awaiting_user_technique_decision','Сидячий важільний chest press зі спинкою та двома ручками за dataset 0576.','Підтверджуємо сидячий важільний жим, чи задумано жим штанги лежачи з English? Це різні сцени; каталог не виправлятимемо.','conflicting_source_choice',['equipment','match.rationale','content.en.description','content.en.instructions[0]']),
 'decline-bench-press-machine':('awaiting_user_equipment_decision','Не обирати конструкцію без уточнення; selected dataset відсутній.','Який саме declined machine press: положення лави/сидіння, фіксація стоп, ручки або гриф, важелі/напрямні і траєкторія? Smith і upright lever кандидати не підтверджують цей ID.','missing_equipment_definition',['source.dataset_id','match.rationale','content.en.description','content.en.instructions[0]']),
 'inverted-row-machine':('awaiting_user_illustration_choice','Нерухома горизонтальна перекладина в стійці на висоті талії, п’яти на підлозі; без Сміта.','Обираємо статичну перекладину в стійці чи іншу конкретну опору: зафіксований гриф Сміта або підвісні ручки? Джерело допускає bar/handles; потрібен вибір сцени.','illustration_choice',['equipment','content.en.description','content.en.instructions[0]','content.en.instructions[1]']),
 'lat-pulldown-machine':('resolved_from_exact_bound_source','Сидячий важільний pulldown, ручки, упори над стегнами, хват знизу.','Відповідь щодо конструкції не потрібна: dataset 0673 equipment=leverage machine. Не замінювати cable station.','source_confirmation',['source.dataset_id','match.rationale','content.en.instructions[0]','content.en.instructions[1]']),
 'vertical-traction-machine':('resolved_from_exact_bound_source','Сидячий важільний reverse-grip pulldown із ручками та упорами стегон; окремий вихідний ID.','Відповідь щодо конструкції не потрібна: точний прив’язаний dataset 0673. Спільне джерело не об’єднує цей ID з Lat Pulldown.','source_confirmation',['source.dataset_id','match.rationale','content.en.description','content.en.instructions[0]']),
}
TAIL_QUESTIONS={
 'cable-crunch-machine':('Скручування стоячи на колінах СПИНОЮ до верхнього блока, канат біля голови; за instructions.','Обираємо цей kneeling cable crunch чи лежачий варіант із description? Підтвердіть орієнтацію щодо блока.',['content.en.description','content.en.instructions[0]','content.en.instructions[1]','match.rationale']),
 'leg-press-machine':('Сидячий жим ногами у sled 45°: спина на опорі, дві стопи на платформі, руки на бічних ручках.','Підтверджуємо sled leg press за instructions/dataset 0739; фрази про рух ліктів і wrists у derived prompt не застосовуємо?',['content.en.instructions','content.en.form_cues','content.en.common_mistakes','content.en.safety_note','match.rationale']),
 'lying-leg-curl-machine':('Згинання ОБОХ колін лежачи животом, таз на опорі, щиколотки під валиком важеля.','Підтверджуємо prone leg curl; фрази про elbow curl/wrist alignment у derived prompt не застосовуємо?',['content.en.description','content.en.instructions[0]','content.en.form_cues[0]','content.en.common_mistakes[1]','content.en.safety_note']),
 'hip-abduction-machine':('Сидячий важільний hip-abduction за match/dataset 0597; кількість рухомих ніг потребує рішення.','Потрібне одночасне розведення двох ніг сидячи чи односторонній рух, як у English? Для одностороннього варіанта вкажіть опору другої ноги.',['content.en.description','content.en.instructions','match.rationale']),
 'standing-calf-raise-machine':('Стоячий підйом ОБОХ п’ят у навантажувальному важільному тренажері з плечовими подушками та платформою.','Підтверджуємо навантаження через плечові подушки, чи тренажер служить лише опорою для рівноваги, як у safety_note?',['content.en.description','content.en.instructions[1]','content.en.safety_note','match.rationale']),
}

def value_at(e,path):
    current=e
    import re
    for part in path.split('.'):
        match=re.fullmatch(r'([^\[]+)(?:\[(\d+)\])?',part)
        current=current[match.group(1)]
        if match.group(2) is not None:current=current[int(match.group(2))]
    return current

def source_row(eid,s):
    e=s['by_id'][eid]
    return {'exercise_id':eid,'name':e['name'],'source_english':copy.deepcopy(e['content']['en']),
            'equipment':e['equipment'],'primary_muscle':e['primary_muscle'],'secondary_muscles':e['secondary_muscles'],
            'source_catalog_sha256':s['catalog_sha256'],'source_catalog_record_sha256':n.base.value_sha(e),
            'source_catalog_commit':s['commits']['origin/work'],'source_url':n.CATALOG_URL+s['commits']['origin/work']+'/'+n.base.CATALOG_PATH,
            'generation_authorized_now':False,'prompt_prepared':False,'assigned_generator':None}

def evidence(eid,fields,s):
    return [{'exercise_id':eid,'field':f,'value':value_at(s['by_id'][eid],f)} for f in fields]

def main():
    assert n.base.git('branch','--show-current').decode().strip()==n.base.BRANCH
    for p in [REVIEW,TAIL,DOC]:assert not (n.ROOT/p).exists(),p
    s=n.snapshot();timestamp=n.now()
    assert len(s['by_id'])==451 and sum(len(e['content']) for e in s['by_id'].values())==4448
    frozen={p:n.file_sha(p) for p in n.base.git('ls-files').decode().splitlines() if p!=n.base.QUEUE_PATH and not p.endswith('.png')}
    old=n.prior.load(n.RECOMMENDATIONS);night=n.prior.load(NIGHT)
    source_evidence=n.prior.load('data/audits/agent-03-blocked-source-evidence.json')
    cache=Path('/tmp/agent03-source-texts/exercise-catalog-v1')
    mr=(cache/'working-manifest.json').read_bytes();dr=(cache/'dataset.json').read_bytes()
    assert n.base.sha(mr)==source_evidence['manifest_sha256'] and n.base.sha(dr)==source_evidence['dataset_sha256']
    manifest=json.loads(mr);mb={e['lightweight_id']:e for e in manifest['exercises']};dataset=json.loads(dr);db={e['id']:e for e in dataset}
    assert len(db)==len(dataset)
    own=[]
    for r in old['exercises']:
        eid=r['exercise_id'];assert not s['by_id'][eid]['archived'] and eid not in s['png_sources']
        assert all(r[k]==v for k,v in n.base.fields_for_id(eid,s).items())
        row=source_row(eid,s)
        row.update(status='awaiting_user_decision',question=r['original_question'],recommendation=r['recommended_variant'],rationale=r['rationale'],
                   decision_kind=r['recommendation_kind'],decision_needed=r['decision_needed'],recommendation_approved=False,
                   recommendation_source_path=n.RECOMMENDATIONS,catalog_evidence=r['catalog_evidence'],retain_blocked_until_support_verified=r['retain_blocked_until_support_verified'])
        own.append(row)
    equipment=[]
    for eid,(status,proposal,question,kind,fields) in EQUIPMENT.items():
        assert eid not in s['png_sources'];e=s['by_id'][eid];m=mb[eid]
        assert all(e[k]==m[k] for k in ['name','equipment','primary_muscle','secondary_muscles','source','match','content'])
        sid=e['source']['dataset_id'];original=db.get(sid)
        row=source_row(eid,s);row.update(status=status,recommendation=proposal,question=question,decision_kind=kind,
            user_answer_needed=status!='resolved_from_exact_bound_source',catalog_evidence=evidence(eid,fields,s),
            original_dataset={'id':sid,'name':original['name'],'equipment':original['equipment'],'instructions_en':original['instruction_steps']['en'],
                              'record_sha256':n.base.value_sha(original)} if original else None,
            source_binding={'catalog_exercise_id':eid,'dataset_id':sid,'manifest_matches_exact_catalog_record':True,
                            'dataset_sha256':n.base.sha(dr),'manifest_sha256':n.base.sha(mr),'source_release_url':source_evidence['source_release_url']})
        equipment.append(row)
    machine_ref='origin/agent-02-machines-001';commit=s['commits'][machine_ref]
    machine_raw=n.base.git('show',commit+':'+MACHINE_BATCH);machine=json.loads(machine_raw)
    machine_manifest=json.loads(n.base.git('show',commit+':'+MACHINE_MANIFEST))
    # Only selected top-level rows constitute a package assignment. Examples
    # explicitly marked not_selected_examples are never assignments.
    selected={r['exercise_id'] for r in machine['exercises']};assert len(selected)==machine['exercise_count']==10
    actual_machine_missing=sorted(eid for eid in selected if eid not in s['png_sources'])
    machine_questions=[]
    exclusions={r['exercise_id']:r for r in machine['not_selected_examples']}
    for eid,(proposal,question,fields) in TAIL_QUESTIONS.items():
        assert eid in exclusions and eid not in selected and eid not in s['png_sources']
        row=source_row(eid,s);row.update(status='awaiting_user_technique_decision',recommendation=proposal,question=question,
            decision_kind='conflicting_source_choice',recommendation_approved=False,catalog_evidence=evidence(eid,fields,s),
            prior_exclusion={'branch':machine['branch'],'commit':commit,'path':MACHINE_BATCH,'pointer':'/not_selected_examples',
                            'sha256':n.base.sha(machine_raw),'reason':exclusions[eid]['reason'],'constitutes_assignment':False})
        machine_questions.append(row)
    broad={'full_body','cardio','other'};historical=[]
    for r in night['exercises']:
        eid=r['exercise_id'];assert eid not in s['png_sources'];row=source_row(eid,s)
        resolved=s['by_id'][eid]['primary_muscle'] in broad
        status='style_resolved_owner_confirmation_needed' if resolved else 'awaiting_user_technique_and_owner_decision'
        if eid in ['diamond-pushup','chest-fly-dumbbell','waiter-curl-dumbbell']:status='technique_resolved_owner_confirmation_needed'
        row.update(status=status,historical_scope='night-2026-10-01',source_clarification_path=NIGHT,
                   current_owner_agent=None,current_owner_confirmed=False,confirmed_active_generation_assignment=False,
                   ownership_question='Хто продовжує історичний нічний список? Без вашого рішення не перепризначати.',
                   original_question=r['question_uk'],question=None if resolved or status=='technique_resolved_owner_confirmation_needed' else r['question_uk'],
                   reason=r['reason_uk'],clarification_sources=n.compact_sources(s['reserved'].get(eid,[])))
        if resolved:
            assert not s['by_id'][eid]['secondary_muscles']
            row.update(approved_style_decision_path='data/style-decisions/agent-03-neutral-primary-approved.json',
                       resolved_rule='Neutral silver-gray; no secondary muscles means no highlights. Do not ask again.')
        if eid=='diamond-pushup':
            row.update(derived_technique='Diamond thumb/index contact, close-elbow push-up without clap.',
                       resolution_evidence=evidence(eid,['content.pl.instructions','content.uk.instructions[2]','match.rationale'],s))
        if eid in ['chest-fly-dumbbell','waiter-curl-dumbbell']:
            e=s['by_id'][eid];m=mb[eid];sid=e['source']['dataset_id'];original=db[sid]
            assert all(e[k]==m[k] for k in ['name','equipment','primary_muscle','secondary_muscles','source','match','content'])
            row.update(derived_technique='Flat-bench dumbbell fly, palms facing each other, softly bent elbows.' if eid=='chest-fly-dumbbell' else
                       'Standing curl with TWO dumbbells, one in each hand, palms forward, elbows beside torso. No single-dumbbell variant substitution.',
                       resolution_evidence=evidence(eid,['match.rationale','content.en.instructions'],s),
                       original_dataset_evidence={'id':sid,'name':original['name'],'equipment':original['equipment'],
                           'instructions_en':original['instruction_steps']['en'],'record_sha256':n.base.value_sha(original),
                           'dataset_sha256':n.base.sha(dr),'source_release_url':source_evidence['source_release_url']})
        if eid=='floor-triceps-dip':
            row['question']='Долоні на підлозі за English instructions, паралельні опори з description чи край лави/стільця з точного dataset 0815?'
        if eid=='bicycle-crunch-raised-legs':
            row['question']+=' Уточніть положення піднятих ніг і відмінність від окремого bicycle-crunch ID.'
        historical.append(row)
    tail=[]
    for eid,e in s['by_id'].items():
        group=s['classifications'][eid]
        if e['archived'] or eid in s['png_sources'] or group not in ['specialized_machine','cable_station','smith_machine']:continue
        row=source_row(eid,s);row.update(phase=2,priority=200,equipment_group=group,batch_id=None,
              status='held_in_original_agent02_batch' if eid in actual_machine_missing else 'awaiting_user_technique_decision' if eid in TAIL_QUESTIONS else 'queued_for_prompt_preparation',
              source_presence=n.compact_sources(s['reserved'].get(eid,[])),
              reservation_note='File mentions/examples are evidence, not proof of an assignment; selected batch rows and explicit registries take precedence.')
        if eid in actual_machine_missing:row.update(existing_owner_agent='agent-02',existing_batch_id=machine['batch_id'],existing_batch_path=MACHINE_BATCH)
        if eid in TAIL_QUESTIONS:row['decision_sheet_path']=REVIEW
        tail.append(row)
    tail.sort(key=lambda r:({'specialized_machine':0,'cable_station':1,'smith_machine':2}[r['equipment_group']],r['exercise_id']))
    groups=dict(collections.Counter(r['equipment_group'] for r in tail));assert groups=={'specialized_machine':55,'cable_station':44,'smith_machine':12}
    report={'schema_version':1,'prepared_at':timestamp,'branch':n.base.BRANCH,'audited_commits':s['commits'],'catalog_sha256':s['catalog_sha256'],
        'kind':'user_decision_sheet_NOT_generation_batch','generation_authorized_now':False,'new_assignments_created':False,
        'own_unresolved':own,'equipment_review':equipment,'additional_tail_technique_questions':machine_questions,'historical_night_scope':historical,
        'shared_style_question':{'exercise_ids':['hiking','walking','snowboarding'],'question':'Дозволяємо потрібне каталогом взуття для Walking/Hiking та snowboard boots/кріплення/захист для Snowboarding? Решта стилю незмінна.','approved':False},
        'ownership':{'correction':'The previously reported 15 foreign assignments are historical clarification holds, not 15 confirmed active generation assignments.',
                     'historical_night_scope_current_owner':None,'historical_scope_ID_count':15,'agent02_actual_missing_selected_ids':actual_machine_missing,
                     'agent02_manifest_path':MACHINE_MANIFEST,'agent02_manifest_commit':commit,
                     'agent02_failed_records':[r for r in machine_manifest['exercises'] if r['exercise_id'] in actual_machine_missing],
                     'previous_009_missing_ids':[r['exercise_id'] for r in n.prior.load('data/batches/agent-03-others-009.json')['exercises'] if r['exercise_id'] not in s['png_sources']],
                     'previous_009_execution_owner_named_in_Git':None,'previous_009_preserve_original_batch':True,
                     'generator_a_assignment_path':n.ASSIGNMENTS,'generator_a_prepared_count':12,'generator_b_prepared_count':0},
        'limits':['Only pushed Git data and verified cached exact-ID source texts; unpublished other-task files may be invisible.',
                  'No generation, PNG pixel QA, photos, Supabase, shared progress/catalog/style/old batch edits.',
                  'Color approval does not approve unresolved technique or footwear. Source-confirmed equipment does not constitute a generation task.']}
    taildoc={'schema_version':1,'queue_id':'agent-03-equipment-tail','branch':n.base.BRANCH,'prepared_at':timestamp,
             'catalog_sha256':s['catalog_sha256'],'audited_commits':s['commits'],'generation_authorized_now':False,'new_assignments_created':False,
             'planning_decision':'User: start preparing machine/cable/Smith tasks, execute only after the non-machine wave; do not steal current assignments.',
             'phase':2,'priority':200,'must_follow':'phase 1: non-machine exercises with resolved technique and approval of illustration choices',
             'exercise_count':len(tail),'equipment_counts':groups,'exercise_ids':[r['exercise_id'] for r in tail],'exercises':tail,
             'source_resolved_additional_candidates':[r for r in equipment if not r['user_answer_needed']],
             'source_resolved_additional_candidate_count':3,'additional_candidates_are_not_assigned_or_prompt_ready':True,
             'preparation_gate':'Verify exact-ID technique, supports/grip/attachment/phase and current PNG/assignment before preparing each prompt. No photographs required for a standard source-compatible construction.',
             'execution_gate':'Non-machine wave first; hold failures in their original batches. Require an explicit generation instruction; this plan makes no generator calls.'}
    q=n.prior.load(n.base.QUEUE_PATH)
    q['updated_at']=timestamp;q['phase_plan']={'decision_source':'latest user message: equipment groups at the end; send all questions and clarify ownership',
        'phase1':'Non-machine eligible exercises first, including approved static bars; unresolved records await answers.',
        'phase2_queue_path':TAIL,'phase2_priority':200,'phase2_base_count':111,'phase2_source_resolved_additional_candidates':3,
        'decision_sheet_path':REVIEW,'generation_authorized_now':False,'existing_assignments_and_batches_unchanged':True}
    q['ownership_interpretation_update']={'review_path':REVIEW,'historical_night_scope_count':15,'confirmed_current_owner':None,
        'not_confirmed_active_generation_assignments':True,'retain_scope_until_user_owner_decision':True,
        'not_selected_examples_are_not_assignments':True}
    # Validate record provenance and disjoint scope before saving.
    for rows in [own,equipment,machine_questions,historical,tail]:
        assert len({r['exercise_id'] for r in rows})==len(rows)
        for row in rows:
            e=s['by_id'][row['exercise_id']]
            assert row['source_english']==e['content']['en'] and row['name']==e['name']
            assert all(row[k]==e[k] for k in ['equipment','primary_muscle','secondary_muscles'])
            assert not e['archived'] and row['exercise_id'] not in s['png_sources']
            assert not row['prompt_prepared'] and row['assigned_generator'] is None
    assert len(own)==22 and len(equipment)==6 and len(machine_questions)==5 and len(historical)==15 and len(tail)==111
    assert actual_machine_missing==['leg-press-horizontal-machine']
    assert not(set(r['exercise_id'] for r in own)&set(r['exercise_id'] for r in historical))
    assert all(n.file_sha(p)==sha for p,sha in frozen.items())
    report['validation']={'status':'passed','exact_ID_fields':True,'451_IDs_4448_language_blocks_unchanged':True,
                          'no_new_assignments_or_prompts':True,'all_old_batches_styles_and_shared_progress_unchanged':True}
    n.prior.save(REVIEW,report);n.prior.save(TAIL,taildoc);n.prior.save(n.base.QUEUE_PATH,q)
    lines=['# Питання для користувача та завершальна черга обладнання','',
      'Актуальна перевірка remote refs наведена в JSON. Тільки підготовка рішення; немає генерації, нових призначень або змін каталогу.',
      '',f'Точні вихідні поля, питання й джерела: `{REVIEW}`. Завершальна черга: `{TAIL}`.',
      '', '## Шість записів обладнання', '', '| ID / назва | Що відомо / рекомендовано | Потрібна відповідь |', '| --- | --- | --- |']
    for r in equipment:lines.append(f"| `{r['exercise_id']}` — {r['name']} | {r['recommendation']} | {r['question']} |")
    lines += ['', '## 22 власні невирішені записи', '', '| ID | Рекомендація | Питання |', '| --- | --- | --- |']
    for r in own:lines.append(f"| `{r['exercise_id']}` | {r['recommendation']} | {r['question']} |")
    lines += ['', 'Walking / Hiking / Snowboarding мають одне спільне питання взуття/кріплень; кольорове доповнення вже approved, його повторно не погоджуємо.',
      '', '## П’ять додаткових питань завершальної черги', '', 'Це `not_selected_examples` агента 02, а не його призначення.', '', '| ID | Рекомендація | Питання |', '| --- | --- | --- |']
    for r in machine_questions:lines.append(f"| `{r['exercise_id']}` | {r['recommendation']} | {r['question']} |")
    lines += ['', '## Історичні 15: виправлення трактування власника', '',
      'Раніше ці 15 названо чужими призначеннями. Фактично це старий нічний список уточнень, скопійований у різні гілки. Поточного призначеного генератора Git не підтверджує. Зберігаємо історичний резерв до рішення користувача, чужі файли не змінюємо.',
      '', '| ID | Поточний стан / потрібна відповідь |', '| --- | --- |']
    for r in historical:
        label=r['question'] or ('Підсвітку вирішено: нейтральне тіло, secondary порожні.' if r['status'].startswith('style_resolved') else 'Техніку визначено точним джерелом: '+r['derived_technique'])
        lines.append(f"| `{r['exercise_id']}` | {label} Поточний виконавець невідомий. |")
    lines += ['', '## Підтверджені пакети інших виконавців', '',
      '- Generator A: 024 (10) → 025 (2), власний новий реєстр; B: 0. Ці призначення не змінено.',
      '- Agent-02, гілка `agent-02-machines-001`: у selected пакеті 10 ID, 9 PNG; `leg-press-horizontal-machine` без PNG після HTTP 400 empty prompt. Залишити у його старому batch/manifest; не повторювати самовільно. Старий handoff про 0 викликів застарів; актуальний manifest має 10 спроб.',
      '- Попередній 009: 9 ID без PNG. `hanging-knee-raise` має quota failure; поточний work прямо каже не продовжувати 009 без нового доручення. Ім’я поточного execution owner не задане; owner_agent=agent-03 у batch — власник підготовки.',
      '', '009 без PNG: '+', '.join('`'+eid+'`' for eid in report['ownership']['previous_009_missing_ids'])+'.',
      '', '## Порядок підготовки', '',
      'Спочатку вправи без спеціалізованих тренажерів. У кінці — 111 початкових machine/cable/Smith ID (55/44/12), плюс 3 source-confirmed кандидати з колишньої неоднозначної групи. Це план, не 114 готових prompts. Один ID зі 111 залишається у вже виконуваному пакеті Agent-02, п’ять потребують наведених вище рішень. Перед кожним майбутнім завданням — актуальні PNG/призначення, без повторів.',
      '', 'Для відповідей можна використовувати точний ID → вибраний варіант. Окремо назвати виконавця історичних нічних 15 та продовження 009. Без відповіді не вважати рекомендацію схваленою.', '']
    (n.ROOT/DOC).write_text('\n'.join(lines))
    print(json.dumps({'status':'passed','own_questions':22,'equipment_records':6,'source_resolved_equipment':3,'additional_tail_questions':5,'historical_scope':15,'tail_base_count':111,'active_assignments_changed':False},ensure_ascii=False))

if __name__=='__main__':main()
