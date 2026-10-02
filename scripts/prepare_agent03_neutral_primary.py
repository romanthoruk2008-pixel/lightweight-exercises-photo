#!/usr/bin/env python3
"""Record an approved style addition and promote exact-ID conditional tasks.

Preparation only. Fetch all remote heads before --prepare or --check. Historical
drafts and batches are immutable; recommendations never authorize technique.
"""
import argparse
import collections
import copy
import datetime
import json
import subprocess
from zoneinfo import ZoneInfo

import prepare_agent03_blocked_records as prior

base = prior.base
ROOT = base.ROOT
VERSION = 'v1-neutral-primary-2026-10-02'
ADDENDUM = 'docs/exercise-image-style-neutral-primary.md'
DECISION = 'data/style-decisions/agent-03-neutral-primary-approved.json'
RECOMMENDATIONS = 'data/queues/agent-03-remaining-recommendations.json'
RECOMMENDATIONS_DOC = 'docs/agent-03-remaining-recommendations.md'
HANDOFF = 'docs/agent-03-neutral-primary-handoff.md'
REPORT = 'data/queues/agent-03-neutral-primary-validation.json'
NEW_PATHS = {f'agent-03-others-{n:03}': f'data/batches/agent-03-others-{n:03}.json' for n in range(19, 24)}
APPROVAL_QUOTE = ('Для full_body, cardio, other тіло залишається нейтральним\n'
                  'сріблясто-сірим. Підсвічуються лише конкретні\n'
                  'secondary_muscles, записані для точного ID,\n'
                  'кольором #F26445 на 40–50% інтенсивності.\n'
                  'Порожній secondary список означає відсутність підсвітки.')

# These are proposals for user review, never source corrections or ready tasks.
# A source confirmation can still require a separate exception to barefoot v1.
RECS = {
 'chest-dip-weighted-machine': (
  'Паралельні бруси, нахил тулуба вперед, обтяження на поясі із замкнутим ланцюгом.',
  'English description/instructions визначають дві паралельні опори; dataset 3313 називає straight-bar. Рекомендовано пріоритет точного English варіанта, але суперечність джерела лишається.',
  'illustration_choice', ['content.en.description', 'content.en.instructions[0]', 'match.rationale'], 'Погодити саме паралельні бруси замість straight-bar; спосіб обтяження підтверджено виробником, опори — ні.'),
 'drag-curl-barbell': (
  'Стоячий drag curl: супінований хват, лікті відводяться назад, гриф рухається близько вздовж тулуба.',
  'match.rationale прямо задає bar-drag path, але English і dataset 0038 залишають верхні руки нерухомими. Це пропозиція розв’язання конфлікту, не підтверджена єдина техніка.',
  'illustration_choice', ['match.rationale', 'content.en.instructions[1]'], 'Погодити drag-траєкторію та відведення ліктів; не замінювати ID звичайним curl.'),
 'feet-up-bench-press-barbell': (
  'Рівна лава, стопи у повітрі й коліна зігнуті; лопатки підтримані, штанга над грудьми, пасивні safeties.',
  'Саме pl/it цього ID задають підняті стопи і зігнуті коліна; es ставить стопи на лаву, en — planted. Пропозиція обирає pl/it, не видає їх за одностайне джерело.',
  'illustration_choice', ['content.pl.instructions[0]', 'content.it.instructions[0]', 'content.es.instructions[0]', 'content.en.instructions[0]'], 'Погодити стопи у повітрі, а не на лаві чи підлозі.'),
 'hammer-curl-band-resistance-band': (
  'Стоячи на середині стрічки, по нейтральній ручці в кожній руці, лікті біля тулуба; без зовнішнього анкера.',
  'Neutral grip прямо заданий; точка фіксації та ручки не задані. Фіксація під стопами — запропонована сумісна композиція, не запозичення іншого band curl.',
  'illustration_choice', ['content.en.instructions[0]', 'match.rationale'], 'Погодити стрічку під стопами та дві сумісні нейтральні ручки.'),
 'hip-thrust-barbell': (
  'Верхня спина на краю лави, таз поза лавою, стопи на підлозі; штанга на тазі, обидві руки стабілізують її.',
  'Description задає плечі на лаві та штангу на тазі; instructions і dataset 0058 описують лежання на лаві. Пропозиція зберігає hip-thrust опори description, не приховує конфлікт.',
  'illustration_choice', ['content.en.description', 'content.en.instructions[0]', 'content.en.instructions[1]'], 'Погодити верхню спину на краю лави й таз поза нею.'),
 'landmine-180-barbell': (
  'Стоячи, двома руками тримати вільний кінець; контрольована дуга від одного стегна через верхню точку до іншого.',
  'Description задає hip-to-hip, але instructions/source 0562 закінчують дугу біля протилежного плеча. Пропозиція обирає description; анкер лишається нерухомим.',
  'illustration_choice', ['content.en.description', 'content.en.instructions[2]'], 'Погодити дві кінцеві точки біля стегон замість hip-to-shoulder.'),
 'lying-neck-extension-weighted-plate': (
  'Залишити blocked до перевірки опори голови; кандидат — лежачи животом на лаві, млинець на потилиці утримують обидві руки.',
  'Потилиця, дві руки й малий рух задані, але орієнтація не задана; head supported не дозволяє просто показати голову за краєм без пояснення опори.',
  'illustration_choice', ['content.en.instructions[0]', 'content.en.instructions[2]', 'content.en.safety_note'], 'Потрібне джерело/рішення щодо орієнтації та опори, яка допускає мале розгинання; сам вибір prone не розблоковує ID.'),
 'nordic-hamstrings-curls': (
  'Килимок під колінами; щиколотки під нерухомою м’якою поперечиною стійки, руки готові прийняти тіло на підлозі.',
  'Каталог прямо задає tall kneeling, secured ankles, eccentric і catch руками. Конкретна поперечина — запропонований анкер, не підтверджена конструкція з джерела.',
  'illustration_choice', ['content.en.instructions[0]', 'content.en.instructions[2]', 'content.en.instructions[3]', 'content.en.safety_note'], 'Погодити нерухому поперечину з м’якою опорою щиколоток; без другої людини чи тренажера.'),
 'pushup-weighted': (
  'Звичайний weighted push-up із щільно закріпленим ваговим жилетом; без вільного млинця й без plyometric drop.',
  'Каталог задає external load across upper back та secure loading method, але НЕ називає млинець. Жилет — рекомендований вибір навантаження для одного персонажа, не доведений спосіб утримання круглого млинця.',
  'illustration_choice', ['content.en.description', 'content.en.instructions[0]', 'content.en.safety_note', 'match.rationale'], 'Погодити жилет як конкретизацію external load; raw equipment=none не переписувати.'),
 'side-bend-dumbbell': (
  'Одна гантель у правій руці; контрольований нахил вправо опускає вагу, потім повернення вертикально.',
  'Одностороннє навантаження та lowering задані, але away/opposite side суперечить опусканню. Пропозиція обирає напрямок до ваги, а не видає його за підтвердження dataset 0407.',
  'illustration_choice', ['content.en.description', 'content.en.instructions[1]', 'match.rationale'], 'Погодити нахил до руки з вагою та відхилення суперечливого away.'),
 'single-arm-landmine-press-barbell': (
  'Стоячий split stance, один нерухомий анкер на підлозі; одна рука працює з ВІЛЬНОЮ втулкою біля плеча, друга на стегні; без спинки.',
  'Стояння, split stance і діагональний press задані; anchored end та back-pad cue суперечать рухомому кінцю. Пропозиція не підміняє вправу kneeling варіантом.',
  'illustration_choice', ['content.en.instructions[0]', 'content.en.instructions[1]', 'content.en.instructions[2]', 'content.en.safety_note'], 'Погодити free sleeve та стоячий варіант без спинки; окремо розв’язати back-pad safety/cues.'),
 'single-leg-standing-calf-raise-barbell': (
  'Залишити blocked: зберегти вільний гриф на верхній спині, дві руки на грифі й одну опорну стопу; спочатку визначити сумісну опору.',
  'Instructions задають вільну штангу та одну стопу, safety вимагає handhold/machine support. Ні відмова від safety, ні довільний Smith чи одноручне утримання не підтверджені.',
  'illustration_choice', ['content.en.description', 'content.en.instructions[1]', 'content.en.safety_note', 'match.rationale'], 'Потрібне джерело/рішення щодо сумісної опори; не призначати ready без нього.'),
 'clean-barbell': (
  'Приймання у повному front squat: гриф на передніх плечах, лікті вперед; показати одну фазу приймання.',
  'match відхиляє power clean через іншу глибину; окремий power-clean ID вже існує. Повний присід логічно відділяє варіанти, але soft knees не доводить цю глибину.',
  'illustration_choice', ['match.rationale', 'content.en.description', 'content.en.instructions[2]'], 'Погодити full-squat receiving та front-rack лікті, не оголошувати їх уже підтвердженими.'),
 'hiit': (
  'Показати робочий інтервал бігу на місці; один персонаж, одна фаза, без таймера чи колажу.',
  'HIIT є форматом, selected bodyweight movement не визначено. Біг на місці — рекомендований представник, а не встановлена каталожна техніка HIIT і не заміна на інший ID.',
  'illustration_choice', ['match.rationale', 'content.en.instructions[1]', 'content.en.instructions[2]'], 'Погодити біг на місці як представницьку ілюстрацію робочого інтервалу.'),
 'hiking': (
  'Звичайна фаза ходьби, сумісне туристичне взуття; не переносити barefoot на маршрут.',
  'Каталожна safety_note прямо вимагає врахувати footwear; outdoor footing заданий. Правило кольорів не затверджує виняток до barefoot v1.',
  'source_confirmation', ['content.en.description', 'content.en.instructions[2]', 'content.en.safety_note'], 'Погодити окремий виняток взуття; конкретний вигляд взуття — стандартна сумісна конструкція без бренду.'),
 'muscle-up-machine': (
  'Overhand bar muscle-up: кисті переходять над перекладиною зі збереженням pronated grip, завершення — верхня опора на прямих руках.',
  'Description визначає transition + press to support, instructions починаються overhand, але далі задають palms towards you й пропускають press. Обраний варіант — пропозиція розв’язання, не виправлення dataset 0631.',
  'illustration_choice', ['content.en.description', 'content.en.instructions[0]', 'content.en.instructions[2]', 'content.en.instructions[3]'], 'Погодити overhand rollover та повну press-to-support фазу замість зміни на supinated.'),
 'pilates': (
  'Представницька вправа Hundred на килимку: лежачи, ноги у tabletop, плечі трохи підняті, руки витягнуті вздовж тулуба.',
  'Метод Pilates і контроль дихання задані, конкретний рух не заданий. Hundred/tabletop — запропонований вибір для ілюстрації, не запозичений запис іншого ID.',
  'illustration_choice', ['match.rationale', 'content.en.instructions[1]'], 'Погодити Hundred з tabletop ногами або назвати інший конкретний Pilates рух.'),
 'press-under-barbell': (
  'Паралельна стійка, частковий присід під грифом із near-upper-chest старту; приймання над головою на прямих руках.',
  'Upper chest, overhand та overhead lockout задані; receiving depth і стопи не визначені. Частковий присід — композиційний вибір без підміни snatch/split jerk.',
  'illustration_choice', ['content.en.instructions[0]', 'content.en.instructions[1]', 'content.en.instructions[2]', 'content.en.instructions[3]'], 'Погодити partial-squat receiving і паралельні стопи, а не full squat чи split.'),
 'snowboarding': (
  'Одна фаза бокової стійки на дошці; snowboard boots у сумісних кріпленнях і належний захист.',
  'Feet secured та protective gear прямо задані. Точна модель черевиків/кріплень не задана; це стандартна сумісна конструкція, для якої потрібен виняток до barefoot v1.',
  'source_confirmation', ['content.en.instructions[0]', 'content.en.safety_note'], 'Погодити спільний виняток взуття/кріплень та захисту; не показувати босі ноги в boot bindings.'),
 'stretching': (
  'Представницьке статичне розтягування задньої поверхні стегна сидячи: одна нога випрямлена, легкий контрольований нахил від тазу.',
  'Каталог вимагає обрати target area, але не задає її чи пози. Це запропонований представник, не нова primary muscle; тіло нейтральне, secondary=[].',
  'illustration_choice', ['match.rationale', 'content.en.instructions[0]', 'content.en.instructions[2]'], 'Погодити цю конкретну stretch-позу; м’язи каталогу не змінювати й не додавати підсвітку.'),
 'walking': (
  'Звичайна heel-to-toe хода із сумісним взуттям, без додаткового навантаження.',
  'Heel-to-toe задано, safety_note прямо вимагає appropriate footwear. Це підтвердження потреби взуття, а його дозвіл у стилі — окреме рішення.',
  'source_confirmation', ['content.en.description', 'content.en.instructions[1]', 'content.en.instructions[2]', 'content.en.safety_note'], 'Погодити спільний виняток взуття для Walking/Hiking/Snowboarding.'),
 'yoga': (
  'Представницька стояча поза Mountain/Tadasana на килимку: стійкі стопи, руки розслаблені, спокійне дихання.',
  'Standing або kneeling setup дозволений, але асана не задана. Mountain — запропонований конкретний представник практики, не підміна ID чи джерела.',
  'illustration_choice', ['match.rationale', 'content.en.instructions[0]', 'content.en.instructions[2]'], 'Погодити Mountain/Tadasana або назвати іншу конкретну асану.'),
}

def now():
    return datetime.datetime.now(ZoneInfo('Europe/Kiev')).isoformat()

def json_file_sha(value):
    return base.sha((json.dumps(value,ensure_ascii=False,indent=2)+'\n').encode())

def snapshot():
    prior.previous.configure()
    base.BATCH_PATHS = NEW_PATHS
    refs=base.git('for-each-ref','--format=%(refname:short)','refs/remotes/origin/').decode().splitlines()
    base.REFS=sorted(r for r in refs if r not in ['origin/HEAD','origin/'+base.BRANCH])+['HEAD']
    s=prior.snapshot()
    # Read supplemental committed queue assignments. Exclusions and unprepared
    # pools are not assignments. Batch manifests/progress/PNG paths use base.
    for ref,commit in s['commits'].items():
        branch=ref.removeprefix('origin/') if ref!='HEAD' else base.BRANCH
        for path in base.git('ls-tree','-r','--name-only',commit,'data/queues').decode().splitlines():
            if not path.endswith('.json'):continue
            raw=base.git('show',commit+':'+path);doc=json.loads(raw)
            if not isinstance(doc,dict):continue
            source={'branch':branch,'commit':commit,'path':path,'sha256':base.sha(raw)}
            s['source_files'].append(source)
            # Exact batch-backed queue entries only; no style drafts/reviews.
            entries=[r for r in doc.get('exercises',[]) if isinstance(r,dict)] if isinstance(doc.get('exercises'),list) else []
            entries += [item for pkg in doc.get('packages',[]) if isinstance(pkg,dict) for item in pkg.get('items',[]) if isinstance(item,dict)]
            for i,r in enumerate(entries):
                eid=r.get('exercise_id');path_assigned=r.get('batch_path')
                bid=r.get('batch_id')
                if eid not in s['by_id'] or not (path_assigned or bid):continue
                current=NEW_PATHS.get(bid) or (path_assigned if path_assigned in NEW_PATHS.values() else None)
                if current:
                    # Only a byte-identical actual own batch proves same task.
                    try: identical=base.git('show',commit+':'+current)==(ROOT/current).read_bytes()
                    except (FileNotFoundError,subprocess.CalledProcessError):
                        identical=False
                    if identical:continue
                s['reserved'][eid].append(dict(source,json_pointer='/batch_backed_queue_entries/'+str(i)))
            for eid in doc.get('assigned_exercise_ids',[]):
                if eid in s['by_id']:s['reserved'][eid].append(dict(source,json_pointer='/assigned_exercise_ids'))
    return s

def frozen_files():
    paths=[f'data/batches/agent-03-others-{n:03}.json' for n in range(1,19)]
    paths += [base.CATALOG_PATH,base.PROGRESS_PATH,'docs/exercise-image-style.md',prior.STYLE_DRAFTS,prior.STYLE_DOC,prior.INPUT,prior.RESEARCH,prior.EVIDENCE,prior.REPORT,prior.HANDOFF]
    return {p:base.sha((ROOT/p).read_bytes()) for p in paths}

def addendum_text():
    return '\n'.join([
      '# Затверджене доповнення стилю: нейтральний primary', '',
      f'Версія `{VERSION}`. Затверджено користувачем у цьому чаті 2026-10-02 (Europe/Kiev). Базовий стиль — `v1` у `docs/exercise-image-style.md`; його файл не змінено.', '',
      'Для точного `exercise_id`, якщо `primary_muscle` дорівнює `full_body`, `cardio` або `other`:', '',
      '- Тіло залишається нейтральним непрозорим сріблясто-сірим. Не фарбувати все тіло та не виводити основну м’язову групу з назви, техніки чи референсу.',
      '- Підсвічувати лише конкретні `secondary_muscles`, записані в каталозі для цього самого ID: `#F26445`, 40–50% інтенсивності. Це інтенсивність кольору, не прозорість тканин.',
      '- Порожній список secondary означає повну відсутність підсвітки.', '',
      'Для конкретних anatomical primary продовжує діяти v1. Зовнішність, пропорції, анатомічні матеріали, деталізація, чорні шорти, barefoot, одна людина/одна фаза, квадратний PNG 1024×1024, справжній прозорий фон, відсутність UI/тексту/світіння та правила техніки збережені.', '',
      'Це затвердження лише кольорів. Воно не дозволяє генерацію, не схвалює жоден PNG, не вирішує технічних суперечностей і не надає винятку для взуття.', '',
      'Дослівне рішення користувача:', '', '```text',APPROVAL_QUOTE,'```', '',
      f'Машинозчитуваний запис рішення: `{DECISION}`. 60 ID попередньої групи «Інші» (55 власних + 5 чужих) перелічено там; історичний єдиний список також у `{prior.STYLE_DOC}`. Це загальне правило кольорів для відповідних primary labels, а список не обмежує його іншими ID. Інших завдань цим рішенням не призначено. Чужі призначення й результати не змінювати; прийняті PNG не перегенеровувати.', '',
      'Історичні conditional drafts мають статус на момент їх підготовки. Це доповнення й поточна власна queue supersede лише рішення про стиль; техніка має окремий статус.', ''])

def promote(draft,bid,s,decision,text):
    row=copy.deepcopy(draft);eid=row['exercise_id']
    for k,v in base.fields_for_id(eid,s).items():
        if row.get(k)!=v:raise ValueError('Exact source field mismatch: '+eid+':'+k)
    if not row['prompt_prepared'] or row['technical_status']!='ready' or row['scene'] is None:raise ValueError('Incomplete technique: '+eid)
    row.update(status='ready',style_version=VERSION,style_approval_status='approved',
               style_path=ADDENDUM,style_sha256=base.sha(text.encode()),
               style_addendum_path=ADDENDUM,style_addendum_sha256=base.sha(text.encode()),
               style_decision_path=DECISION,style_decision_sha256=json_file_sha(decision),
               style_proposal_path=None,style_proposal_sha256=None,
               assignment_kind='ready_own_batch_preparation_only',batch_id=bid,
               planned_png_path=f'/workspace/exercise-image-results/{bid}/{eid}/attempt-1.png',
               planned_output_relative_path=f'{bid}/{eid}/attempt-1.png',
               output_path_policy='Exact batch_id/exercise_id/attempt path. Do not map generated files by name similarity or array position.',
               source_draft_path=prior.STYLE_DRAFTS,source_draft_file_sha256=base.sha((ROOT/prior.STYLE_DRAFTS).read_bytes()),
               source_draft_prompt_sha256=draft['prompt_sha256'])
    payload=copy.deepcopy(draft['prompt_payload'])
    payload['style']['version']=VERSION;payload['style']['approval_status']='approved'
    payload.pop('style_proposal_sha256',None)
    payload['approved_style_addendum']={'version':VERSION,'path':ADDENDUM,'sha256':row['style_addendum_sha256'],
                                       'decision_path':DECISION,'decision_sha256':row['style_decision_sha256'],'user_quote':APPROVAL_QUOTE}
    prompt='Create exactly ONE square transparent PNG of the exact exercise and selected single phase. Metadata fields must never appear as text.\nDo not render multiple phases, raw disputed alternatives, or inferred muscle targets.\n'+json.dumps(payload,ensure_ascii=False,sort_keys=True,indent=2)
    row.update(prompt_payload=payload,generation_prompt=prompt,prompt_template=None,prompt_sha256=base.sha(prompt.encode()))
    return row

def recommendations(s,decision,timestamp):
    old={r['exercise_id']:r for r in prior.load(prior.RESEARCH)['exercises']}
    rows=[]
    for eid,(variant,why,kind,fields,question) in RECS.items():
        source=copy.deepcopy(old[eid]);row=base.fields_for_id(eid,s)
        row.update(status='blocked',technical_status='awaiting_user_technique_decision',style_approval_status='approved' if eid in prior.STYLE_EXTRA else 'unchanged_v1',
                   recommendation_kind=kind,recommended_variant=variant,rationale=why,decision_needed=question,
                   recommendation_status='proposed_not_approved',ready=False,generation_authorized_now=False,
                   original_question=prior.STYLE_EXTRA[eid][1] if eid in prior.STYLE_EXTRA else prior.QUESTIONS[eid][1],source_record_evidence=source['source_record_evidence'],
                   source_research_path=prior.RESEARCH,source_research_sha256=base.sha((ROOT/prior.RESEARCH).read_bytes()),
                   catalog_evidence=prior.proofs(eid,fields,s),technique_approval=None,
                   retain_blocked_until_support_verified=eid in ['lying-neck-extension-weighted-plate','single-leg-standing-calf-raise-barbell'])
        rows.append(row)
    return {'schema_version':1,'kind':'recommendations_for_user_review_NOT_generation_batch','owner_agent':'agent-03','branch':base.BRANCH,
            'prepared_at':timestamp,'audited_commits':s['commits'],'catalog_sha256':s['catalog_sha256'],
            'exercise_count':22,'technical_questions_count':12,'additional_style_records_count':10,
            'exercise_ids':list(RECS),'exercises':rows,'style_decision_path':DECISION,'style_decision_sha256':json_file_sha(decision),
            'shared_decisions':[{'group_id':'compatible_footwear_exception','exercise_ids':['hiking','walking','snowboarding'],
                                'status':'awaiting_user_decision','recommendation':'Дозволити сумісне взуття/кріплення і захист, прямо потрібні каталогом; решта зовнішності v1 незмінна.'}],
            'limits':['Evidence reuses exact-ID catalogue, verified original dataset binding and primary-source research from prior turn. No new external publication is claimed.',
                      'Illustration choices are proposals, not proof that conflicting source variants are identical. Footwear source confirmation still requires a separate style exception.',
                      'All 22 remain blocked; no recommended equipment, muscles, technique or English text has been written into catalogue.'],
            'generation_authorized_now':False}

def recommendations_text(rec):
    lines=['# Рекомендовані рішення для окремого перегляду', '',
           'Усі 22 записи залишаються **blocked**. Рішення щодо кольору approved тільки для 10 broad-primary записів; техніка/взуття не затверджені. Каталог не виправлено.', '',
           '«Вибір для ілюстрації» означає запропонований варіант, а не факт із джерела. «Підтвердження джерела» стосується лише прямо вказаної потреби взуття/кріплень; виняток до barefoot v1 ще потребує рішення.', '',
           '| Точний ID | Рекомендований варіант | Обґрунтування | Тип |', '| --- | --- | --- | --- |']
    for r in rec['exercises']:
        kind='Підтвердження джерела; виняток стилю не затверджено' if r['recommendation_kind']=='source_confirmation' else 'Вибір для ілюстрації; не затверджено'
        lines.append(f"| `{r['exercise_id']}` | {r['recommended_variant']} | {r['rationale']} | {kind} |")
    lines += ['', 'Одне спільне питання для Hiking/Walking/Snowboarding: дозволити сумісне взуття/кріплення та захист, зберігши решту v1? Рішення нейтрального primary цього не затверджує.', '',
              'Для neck extension і одноногого calf raise пропозиція — зберегти blocked до підтвердження сумісної опори; одного вибору пози недостатньо.', '',
              f'Точні проблемні поля/значення за ID, джерела й питання рішення: `{RECOMMENDATIONS}`. Original source bindings і перевірені URL/quotes збережено в `{prior.EVIDENCE}`. Непрочитані зовнішні сторінки не оголошено доказами.', '']
    return '\n'.join(lines)

def validate(s,q,batches,decision,rec,frozen,text):
    errors=[]
    def require(condition,message):
        if not condition:errors.append(message)
    drafts=prior.load(prior.STYLE_DRAFTS);bydraft={r['exercise_id']:r for r in drafts['exercises']}
    expected={eid for eid,r in bydraft.items() if r['prompt_prepared'] and r['technical_status']=='ready'}
    counts=collections.Counter(e['id'] for e in s['catalog']['exercises'])
    require(len(counts)==451 and set(counts.values())=={1},'catalog_unique451')
    require(s['local_reference_sha256']==s['reference_sha256'],'local_reference_matches_Git')
    require(decision['approval_status']=='approved' and decision['user_quote']==APPROVAL_QUOTE,'user_style_decision')
    require(decision['style_version']==VERSION and decision['addendum_sha256']==base.sha(text.encode()),'style_document_version_hash')
    if (ROOT/DECISION).exists():require(base.sha((ROOT/DECISION).read_bytes())==json_file_sha(decision),'saved_decision_file_hash')
    require(decision['catalog_sha256']==s['catalog_sha256'] and decision['base_style_sha256']==s['style_sha256'],'catalog_base_style_hash')
    require(decision['applicable_exercise_ids']==drafts['style_applicability_ids'] and len(set(decision['applicable_exercise_ids']))==60,'60_exact_affected_IDs')
    for r in decision['applicable_records']:
        require(r['catalog_record_sha256']==base.value_sha(s['by_id'][r['exercise_id']]) and r['secondary_muscles']==s['by_id'][r['exercise_id']]['secondary_muscles'],'decision_ID_binding:'+r['exercise_id'])
    seen=set()
    for batch in batches:
        require(batch['status']=='ready' and 1<=batch['exercise_count']<=10 and batch['exercise_count']==len(batch['exercises']),'batch_size_status:'+batch['batch_id'])
        require(batch['exercise_ids']==[r['exercise_id'] for r in batch['exercises']],'batch_ID_list:'+batch['batch_id'])
        require(batch['catalog_sha256']==s['catalog_sha256'] and batch['style_version']==VERSION and batch['base_style_sha256']==s['style_sha256'],'batch_catalog_style:'+batch['batch_id'])
        require(batch['style_addendum_sha256']==decision['addendum_sha256'] and batch['style_decision_sha256']==json_file_sha(decision),'batch_style_hash:'+batch['batch_id'])
        for r in batch['exercises']:
            eid=r['exercise_id'];require(eid not in seen,'duplicate:'+eid);seen.add(eid)
            require(counts[eid]==1 and eid in expected,'eligible_exact_ID:'+eid)
            if eid not in expected:continue
            require(prior.available(eid,s)=='available','live_PNG_assignment_or_attempt_overlap:'+eid)
            require(r==promote(bydraft[eid],batch['batch_id'],s,decision,text),'saved_row_source_prompt_scene_binding:'+eid)
            for k,v in base.fields_for_id(eid,s).items():require(r.get(k)==v,'catalog_field:'+eid+':'+k)
            require(r['scene']==bydraft[eid]['scene'],'unchanged_concrete_scene:'+eid)
            require(r['human_reference']['sha256']==s['reference_sha256'],'canonical_reference:'+eid)
            st=r['prompt_payload']['style'];oldst=bydraft[eid]['prompt_payload']['style']
            require(all(st[k]==v for k,v in oldst.items() if k not in ['version','approval_status']),'unchanged_other_style_rules:'+eid)
            require(st['primary_highlight']['hex'] is None and st['approval_status']=='approved','neutral_primary_rule:'+eid)
            require(st['secondary_highlight']==base.STYLE['secondary_highlight'],'secondary_intensity_rule:'+eid)
            require(r['primary_muscle'] in ['full_body','cardio','other'],'broad_primary:'+eid)
            require(r['attempts']==0 and not r['generation_authorized_now'] and all(r[k] is None for k in ['result_path','result_sha256','user_review','technical_check']),'no_generation_or_image_approval:'+eid)
    own_input=rec.get('eligible_input_ids',list(expected));excluded=rec.get('excluded_since_style_decision',[])
    require(seen==set(own_input)-{r['exercise_id'] for r in excluded},'all_available45_included')
    require(set(own_input)==expected and len(expected)==45,'45_input_drafts')
    require(set(rec['exercise_ids'])==set(prior.QUESTIONS)|set(prior.STYLE_EXTRA) and len(rec['exercises'])==22,'22_recommendation_IDs')
    for r in rec['exercises']:
        eid=r['exercise_id'];require(r['status']=='blocked' and r['ready'] is False and r['technique_approval'] is None and not r['generation_authorized_now'],'recommendation_not_ready:'+eid)
        require((r['recommended_variant'],r['rationale'],r['recommendation_kind'],r['decision_needed'])==(RECS[eid][0],RECS[eid][1],RECS[eid][2],RECS[eid][4]),'exact_recommendation:'+eid)
        for k,v in base.fields_for_id(eid,s).items():require(r.get(k)==v,'recommendation_source_ID:'+eid+':'+k)
        for proof in r['catalog_evidence']:
            require(proof['exercise_id']==eid and proof['value']==prior.old.field_value(s['by_id'][eid],proof['field']),'recommendation_evidence:'+eid)
    require(not (seen&set(decision['foreign_previously_assigned_ids'])),'foreign_ID_not_assigned')
    require(q['awaiting_style_decision_count']==0 and q['blocked_clarification_count']==22,'queue_current_style_blocked_counts')
    require(q['style_version']==VERSION and q['style_sha256']==decision['addendum_sha256'] and q['base_style_sha256']==s['style_sha256'],'queue_current_style_binding')
    require(q['neutral_primary_preparation']['new_ready_ids']==[eid for b in batches for eid in b['exercise_ids']],'queue_new_IDs')
    require(q['prepared_count']==165+len(seen) and len(q['eligible_exercise_ids'])==len(set(q['eligible_exercise_ids'])),'queue_historical_count_unique')
    qrows={r['exercise_id']:r for r in q['exercises']};require(len(qrows)==len(q['exercises']),'queue_row_uniqueness')
    for batch in batches:
        for r in batch['exercises']:
            eid=r['exercise_id'];qr=qrows.get(eid,{})
            require(qr.get('batch_id')==batch['batch_id'] and qr.get('style_version')==VERSION and qr.get('status')=='ready','queue_batch_style:'+eid)
            for k,v in base.fields_for_id(eid,s).items():
                if k!='source_english':require(qr.get(k)==v,'queue_exact_fields:'+eid+':'+k)
    require(set(q['current_blocked_ids'])==set(RECS),'queue_blocked22')
    for path,h in frozen.items():require(base.sha((ROOT/path).read_bytes())==h,'protected_file_changed:'+path)
    return {'schema_version':1,'status':'failed' if errors else 'passed','errors':errors,'checked_at':now(),'audited_commits':s['commits'],
            'catalog_sha256':s['catalog_sha256'],'base_style_sha256':s['style_sha256'],'style_version':VERSION,
            'style_addendum_sha256':decision['addendum_sha256'],'input_complete_prompts':45,'new_ready_count':len(seen),
            'new_batches':[{'batch_id':b['batch_id'],'status':b['status'],'count':b['exercise_count'],'path':NEW_PATHS[b['batch_id']]} for b in batches],
            'excluded_since_style_decision':excluded,'remaining_blocked_count':22,'awaiting_style_decision_count':0,
            'foreign_IDs_not_reassigned':5,'protected_sha256':frozen,'source_files':s['source_files'],
            'checks':['catalog_unique_exact_ID_lookup','all_original_English_fields_equipment_muscles_exact','only_approved_primary_color_change',
                      'local_and_Git_reference_SHA256','full_prompt_scene_source_and_future_PNG_binding','all_fetched_branches_PNG_assignment_progress_and_queue_scan',
                      'old001018_and_historical_evidence_immutable','all22_recommendations_blocked','no_foreign_assignment','no_generation_Supabase_or_image_approval'],
            'limits':prior.load(prior.RESEARCH)['limits']}

def handoff(q,report):
    lines=['# Agent-03: затверджений нейтральний primary — передача', '',
           f"Гілка `{base.BRANCH}`. Перевірка {report['checked_at']} (Europe/Kiev); work `{report['audited_commits']['origin/work']}`.", '',
           f"**{report['new_ready_count']} ready**, **22 blocked**, **0 awaiting_style_decision** щодо нейтрального primary. Генерацію не запускали; style approval не є image approval чи дозволом на запуск.", '',
           f'Чинна для цих пакетів версія `{VERSION}` = v1 + `{ADDENDUM}`. Decision: `{DECISION}`. Barefoot/зовнішність/матеріали/решта v1 незмінні.', '',
           '| Пакет | Статус | Вправ | Точний шлях |','| --- | --- | ---: | --- |']
    for b in report['new_batches']:lines.append(f"| {b['batch_id']} | ready | {b['count']} | `{b['path']}` |")
    lines += ['',f'Рекомендації: **blocked**, 22 записи, `{RECOMMENDATIONS}`; коротка таблиця `{RECOMMENDATIONS_DOC}`. 12 попередніх технічних + 10 додаткових. Жодна рекомендація не стала готовим prompt.', '',
              'Для Hiking/Walking/Snowboarding — одне окреме рішення про сумісне взуття/кріплення та захист. Для neck extension і unilateral barbell calf raise потрібне підтвердження сумісних опор; пропозиція пози сама їх не розблоковує.', '',
              'Кожний ready запис самодостатній: exact ID/name, весь source_english description/instructions/form_cues/common_mistakes/safety/provenance, equipment/muscles, конкретні phase/pose/grip/supports/trajectory/camera, full prompt/hash, unchanged appearance-only reference/path/hash, base style/addendum/decision hashes, exact-ID planned PNG path.', '',
              'Еталон `assets/exercises/biceps-curl-dumbbell.png`, SHA256 `52fef743ba2d7689aa81a8b995df3c6715cbb5d04c4bd688af4ca57b2d20057f`; зовнішність/пропорції/матеріали, без копіювання пози чи підсвітки. Результат `/workspace/exercise-image-results/<batch_id>/<exercise_id>/attempt-1.png` — планований, файла ще немає.', '',
              'Пакети 001–018 та всі їхні attempts/результати/призначення незмінні. Failed/noPNG залишається в попередньому пакеті. П’ять чужих ID (downward-dog, bear-crawl, jumping-jack, high-knees, mountain-climber) лише у style applicability, не включені в пакети й не перепризначені.', '',
              f'Історичні drafts `{prior.STYLE_DRAFTS}` і proposal `{prior.STYLE_DOC}` незмінні як датований snapshot; їхні awaiting_style_decision superseded рішенням `{DECISION}` та queue.neutral_primary_preparation. Попередній blocked research теж історичний; поточні blocked IDs — queue.current_blocked_ids та нова таблиця.', '',
              f"Queue prepared_count={q['prepared_count']} включає історичні 165 + нові {report['new_ready_count']}; це НЕ число відсутніх PNG чи вправ для повторного запуску. Нові actionable IDs — queue.neutral_primary_preparation.new_ready_ids.", '',
              'Перед майбутнім окремо дозволеним запуском: fetch ВСІ актуальні remote heads, перевірити PNG/призначення; не запускати ID з готовим/pending PNG або іншим призначенням. Інструмент перевірки тільки читає Git metadata, не робить візуального/технічного повторного QA PNG й не звертається до Supabase.', '',
              '```bash','python scripts/prepare_agent03_neutral_primary.py --check','```', '',
              f'Остання перевірка й точні audited commits/source paths: `{REPORT}`. Непушені файли інших cloud задач можуть бути недоступні; перевірка обмежена fetched Git та власними збереженими файлами.', '',
              'work/каталог/shared progress/Supabase/схвалення PNG не змінені. Рекомендації не є зміною джерел або затвердженням техніки.', '']
    if report['excluded_since_style_decision']:lines += ['Виключення: '+json.dumps(report['excluded_since_style_decision'],ensure_ascii=False),'']
    return '\n'.join(lines)

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--prepare',action='store_true');parser.add_argument('--check',action='store_true');args=parser.parse_args()
    if args.prepare==args.check:parser.error('Choose --prepare or --check')
    if base.git('branch','--show-current').decode().strip()!=base.BRANCH:raise ValueError('Wrong branch')
    s=snapshot();q=prior.load(base.QUEUE_PATH);text=addendum_text()
    if args.prepare:
        for path in [ADDENDUM,DECISION,RECOMMENDATIONS,RECOMMENDATIONS_DOC,HANDOFF,REPORT,*NEW_PATHS.values()]:
            if (ROOT/path).exists():raise ValueError('Artifact already exists: '+path)
        if q['prepared_count']!=165:raise ValueError('Unexpected input queue')
        frozen=frozen_files();timestamp=now();drafts=prior.load(prior.STYLE_DRAFTS)
        foreign=[r['exercise_id'] for r in drafts['foreign_reference_only']]
        decision={'schema_version':1,'approval_status':'approved','approved_by':'user_explicit_chat_message','recorded_at':timestamp,
                  'decision_date':'2026-10-02','timezone':'Europe/Kiev','user_quote':APPROVAL_QUOTE,'approval_scope':'neutral_primary_color_only',
                  'style_version':VERSION,'base_style_version':'v1','base_style_path':'docs/exercise-image-style.md','base_style_sha256':s['style_sha256'],
                  'addendum_path':ADDENDUM,'addendum_sha256':base.sha(text.encode()),'catalog_sha256':s['catalog_sha256'],
                  'catalog_source_commit':s['commits']['origin/work'],'applicable_exercise_ids':drafts['style_applicability_ids'],
                  'applicability_list_scope':'Prior Other clarification group (60 IDs); the color rule applies generally to exact IDs with full_body/cardio/other. No tasks assigned outside this round.',
                  'foreign_previously_assigned_ids':foreign,'applicable_records':[{'exercise_id':eid,'primary_muscle':s['by_id'][eid]['primary_muscle'],
                     'secondary_muscles':s['by_id'][eid]['secondary_muscles'],'catalog_record_sha256':base.value_sha(s['by_id'][eid]),
                     'disposition':'foreign_assignment_unchanged' if eid in foreign else 'own_technical_status_separate'} for eid in drafts['style_applicability_ids']],
                  'neutral_primary_values':['full_body','cardio','other'],'secondary_hex':'#F26445','secondary_intensity_fraction':[0.4,0.5],
                  'empty_secondary_means_no_highlight':True,'rest_of_style_unchanged':True,'footwear_exception_approved':False,
                  'technique_decisions_approved':False,'image_approvals_modified':False,'generation_authorized_now':False}
        rec=recommendations(s,decision,timestamp);candidate=[r for r in drafts['exercises'] if r['prompt_prepared'] and r['technical_status']=='ready']
        eligible=[];excluded=[]
        for r in candidate:
            eid=r['exercise_id'];reason=prior.available(eid,s)
            mismatches=[k for k,v in base.fields_for_id(eid,s).items() if r.get(k)!=v]
            if mismatches:reason='exact_catalog_source_mismatch:'+','.join(mismatches)
            if reason=='available':eligible.append(r)
            else:excluded.append({'exercise_id':eid,'reason':reason,'png_sources':s['png_sources'].get(eid,[]),'reservations':s['reserved'].get(eid,[]),'progress_sources':s['touched'].get(eid,[])})
        rec['eligible_input_ids']=[r['exercise_id'] for r in candidate];rec['excluded_since_style_decision']=excluded
        batches=[]
        for i in range(0,len(eligible),10):
            bid=list(NEW_PATHS)[i//10]
            rows=[promote(r,bid,s,decision,text) for r in eligible[i:i+10]]
            batches.append({'schema_version':1,'batch_id':bid,'owner_agent':'agent-03','branch':base.BRANCH,'status':'ready','prepared_at':timestamp,
                            'catalog_source_commit':s['commits']['origin/work'],'audited_commits':s['commits'],'catalog_sha256':s['catalog_sha256'],
                            'style_version':VERSION,'base_style_version':'v1','base_style_sha256':s['style_sha256'],'style_addendum_path':ADDENDUM,
                            'style_path':ADDENDUM,'style_sha256':decision['addendum_sha256'],
                            'style_addendum_sha256':decision['addendum_sha256'],'style_decision_path':DECISION,'style_decision_sha256':json_file_sha(decision),
                            'exercise_count':len(rows),'exercise_ids':[r['exercise_id'] for r in rows],'exercises':rows,
                            'source_evidence_path':prior.EVIDENCE,'source_evidence_sha256':base.sha((ROOT/prior.EVIDENCE).read_bytes()),
                            'generation_authorized_now':False,'constraints':{'no_generation':True,'old001018_immutable':True,'catalog_shared_progress_Supabase_immutable':True}})
        ids=[eid for b in batches for eid in b['exercise_ids']]
        for b in batches:
            for r in b['exercises']:
                row={k:copy.deepcopy(v) for k,v in base.fields_for_id(r['exercise_id'],s).items() if k!='source_english'}
                row.update(batch_id=b['batch_id'],status='ready',prompt_prepared=True,preparation_status='prompt_prepared_not_generated',style_version=VERSION,
                           style_approval_status='approved',source_draft_path=prior.STYLE_DRAFTS,priority_tier=6,queue_order=len(q['exercises'])+1)
                q['exercises'].append(row)
        q['eligible_exercise_ids']+=ids;q['eligible_count']=len(q['eligible_exercise_ids']);q['prepared_count']=q['eligible_count']
        q['batch_paths'] += [NEW_PATHS[b['batch_id']] for b in batches];q['latest_launch_ids']=ids
        q['excluded']=[r for r in q['excluded'] if r['exercise_id'] not in ids]
        for r in q['excluded']:
            if r['exercise_id'] in prior.STYLE_EXTRA:r.update(reason_code='blocked_technique_or_footwear',style_approval_status='approved',recommendations_path=RECOMMENDATIONS)
        q['exclusion_counts_disjoint']=dict(collections.Counter(r['reason_code'] for r in q['excluded']))
        q.update(updated_at=timestamp,awaiting_style_decision_count=0,awaiting_style_decision_ids=[],style_decision_status='approved',style_decision_path=DECISION,
                 style_version=VERSION,style_path=ADDENDUM,style_sha256=decision['addendum_sha256'],base_style_version='v1',base_style_sha256=s['style_sha256'],
                 style_metadata_scope='Current preparation uses v1 plus the approved addendum; historical batches retain their own pinned style versions and hashes.',
                 current_preparation_style_version=VERSION,current_blocked_ids=list(RECS),blocked_clarification_count=22,blocked_clarification_path=RECOMMENDATIONS,
                 count_semantics='eligible/prepared includes historical assigned rounds; only neutral_primary_preparation.new_ready_ids is this round. current_blocked_ids are separate. Style drafts are immutable historical snapshots.')
        q['neutral_primary_preparation']={'status':'ready_preparation_only_technique_recommendations_pending','prepared_at':timestamp,'audited_commits':s['commits'],
                     'new_ready_count':len(ids),'new_ready_ids':ids,'new_batch_paths':[NEW_PATHS[b['batch_id']] for b in batches],
                     'style_version':VERSION,'style_decision_path':DECISION,'style_addendum_path':ADDENDUM,'input_complete_prompt_ids':rec['eligible_input_ids'],
                     'excluded_since_style_decision':excluded,'remaining_blocked_ids':list(RECS),'recommendations_path':RECOMMENDATIONS,
                     'foreign_previously_assigned_ids_not_reassigned':foreign,'generation_authorized_now':False}
        q['preparation_rounds'].append({'round':6,'prepared_at':timestamp,'audited_commits':s['commits'],'exercise_ids':ids,'batch_paths':q['neutral_primary_preparation']['new_batch_paths'],
                                      'status':'ready_preparation_only','style_version':VERSION,'recommendations_path':RECOMMENDATIONS})
        report=validate(s,q,batches,decision,rec,frozen,text)
        if report['errors']:raise ValueError(json.dumps(report['errors']))
        q['last_live_check']={'status':'passed','checked_at':report['checked_at'],'audited_commits':s['commits'],'validation_path':REPORT}
        for b in batches:prior.save(NEW_PATHS[b['batch_id']],b)
        prior.save(DECISION,decision);prior.save(RECOMMENDATIONS,rec);prior.save(REPORT,report);prior.save(base.QUEUE_PATH,q)
        prior.save(prior.old.BLOCKED_PATH,{'schema_version':1,'kind':'unresolved_queue_NOT_generation_batch','owner_agent':'agent-03','status':'blocked',
                       'exercise_count':22,'technical_blocked_count':22,'awaiting_style_decision_count':0,'exercise_ids':list(RECS),
                       'exercises':rec['exercises'],'recommendations_path':RECOMMENDATIONS,'style_decision_path':DECISION,'generation_authorized_now':False})
        (ROOT/ADDENDUM).write_text(text);(ROOT/RECOMMENDATIONS_DOC).write_text(recommendations_text(rec));(ROOT/HANDOFF).write_text(handoff(q,report))
    else:
        decision=prior.load(DECISION);rec=prior.load(RECOMMENDATIONS);saved=prior.load(REPORT)
        batches=[prior.load(p) for p in q['neutral_primary_preparation']['new_batch_paths']]
        report=validate(s,q,batches,decision,rec,saved['protected_sha256'],text)
        if (ROOT/ADDENDUM).read_text()!=text:report['errors'].append('saved_addendum_text_mismatch');report['status']='failed'
        if (ROOT/RECOMMENDATIONS_DOC).read_text()!=recommendations_text(rec):report['errors'].append('saved_recommendations_table_mismatch');report['status']='failed'
    print(json.dumps({k:report[k] for k in ['status','audited_commits','new_ready_count','new_batches','remaining_blocked_count','awaiting_style_decision_count','excluded_since_style_decision','errors']},ensure_ascii=False,indent=2))
    if report['errors']:raise SystemExit(1)

if __name__=='__main__':main()
