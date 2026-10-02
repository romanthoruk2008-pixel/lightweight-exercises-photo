#!/usr/bin/env python3
"""Prepare a bounded A/B assignment; never call a generator or shared service.

Fetch all remote heads first. Own unexecuted plans 017/018 may be superseded;
foreign assignments and attempted batches cannot be moved. --check is read-only.
"""
import argparse
import collections
import copy
import datetime
import json
import re
from zoneinfo import ZoneInfo

import prepare_agent03_blocked_records as prior

base=prior.base
ROOT=base.ROOT
ROUND='agent-03-next50-2026-10-02'
ASSIGNMENTS=f'data/assignments/{ROUND}.json'
AUDIT=f'data/audits/{ROUND}-eligibility.json'
VALIDATION=f'data/queues/{ROUND}-validation.json'
SUMMARY=f'docs/{ROUND}-handoff.md'
SOURCE_BATCHES=[f'data/batches/agent-03-others-{n:03}.json' for n in [17,18]]
ROLES=['generator-a','generator-b']
MANIFESTS={r:f'data/manifests/{ROUND}/{r}.json' for r in ROLES}
HANDOFFS={r:f'docs/{ROUND}-{r}-handoff.md' for r in ROLES}
MESSAGES={r:f'docs/{ROUND}-{r}-message.md' for r in ROLES}
RECOMMENDATIONS='data/queues/agent-03-remaining-recommendations.json'
CATALOG_URL='https://github.com/romanthoruk2008-pixel/lightweight-exercises-photo/blob/'

def now():
    return datetime.datetime.now(ZoneInfo('Europe/Kiev')).isoformat()

def file_sha(path):
    return base.sha((ROOT/path).read_bytes())

def compact_sources(sources):
    """Keep each exact branch/file once, retaining all matching JSON pointers."""
    grouped={}
    for source in sources:
        value={k:v for k,v in source.items() if k!='json_pointer'}
        key=json.dumps(value,sort_keys=True,ensure_ascii=False)
        if key not in grouped:grouped[key]=value
        if 'json_pointer' in source:
            pointers=grouped[key].setdefault('json_pointers',[])
            if source['json_pointer'] not in pointers:pointers.append(source['json_pointer'])
    return list(grouped.values())

def snapshot():
    refs=base.git('for-each-ref','--format=%(refname:short)','refs/remotes/origin/').decode().splitlines()
    base.REFS=sorted(r for r in refs if r!='origin/HEAD')+['HEAD']
    base.BATCH_PATHS={}
    s=prior.snapshot();s['trees']={}
    # Queue entries are reservations only when actually tied to a batch. Read
    # existing assignment/manifest files too, excluding evidence/catalogs.
    def walk(value,source,ptr=''):
        if isinstance(value,dict):
            eid=value.get('exercise_id')
            if eid in s['by_id']:s['reserved'][eid].append(dict(source,json_pointer=ptr))
            for k,v in value.items():
                if k in ['source_english','generation_prompt','prompt_payload','human_reference','technique_resolution','supersedes_own_unexecuted_plans']:continue
                if k in ['exercise_ids','assigned_exercise_ids'] and isinstance(v,list):
                    for i,eid in enumerate(v):
                        if eid in s['by_id']:s['reserved'][eid].append(dict(source,json_pointer=ptr+'/'+k+'/'+str(i)))
                else:walk(v,source,ptr+'/'+base.pointer(k))
        elif isinstance(value,list):
            for i,v in enumerate(value):walk(v,source,ptr+'/'+str(i))
    for ref,commit in s['commits'].items():
        paths=base.git('ls-tree','-r','--name-only',commit).decode().splitlines();s['trees'][ref]=set(paths)
        branch=ref.removeprefix('origin/') if ref!='HEAD' else base.BRANCH
        for path in paths:
            if not path.endswith('.json'):continue
            if not (path.startswith(('data/queues/','data/assignments/','data/manifests/'))):continue
            raw=base.git('show',commit+':'+path);doc=json.loads(raw)
            source={'branch':branch,'commit':commit,'path':path,'sha256':base.sha(raw)};s['source_files'].append(source)
            if path.startswith(('data/assignments/','data/manifests/')):
                # Supersession records are historical links, not new tasks.
                walk(doc,source)
            elif isinstance(doc,dict):
                rows=doc.get('exercises',[])
                if isinstance(rows,list):
                    for i,r in enumerate(rows):
                        if isinstance(r,dict) and r.get('batch_id'):walk(r,source,'/exercises/'+str(i))
                for i,pkg in enumerate(doc.get('packages',[]) or []):
                    if isinstance(pkg,dict):walk(pkg,source,'/packages/'+str(i))
                for eid in doc.get('assigned_exercise_ids',[]) or []:
                    if eid in s['by_id']:s['reserved'][eid].append(dict(source,json_pointer='/assigned_exercise_ids'))
    return s

def source_rows():
    result={}
    for path in SOURCE_BATCHES:
        b=prior.load(path)
        for row in b['exercises']:
            eid=row['exercise_id']
            if eid in result:raise ValueError('Duplicate source ID: '+eid)
            result[eid]={'path':path,'batch_id':b['batch_id'],'row':row}
    return result

def disposition(eid,s,registry=None):
    e=s['by_id'][eid];own=source_rows()
    if e['archived']:return 'archived'
    if eid in s['png_sources']:return 'PNG_exists_including_pending'
    group=s['classifications'][eid]
    if group in ['specialized_machine','cable_station','smith_machine']:return 'deferred_'+group
    if group=='ambiguous':return 'ambiguous_equipment'
    if eid in prior.load(RECOMMENDATIONS)['exercise_ids']:return 'unresolved_technique_or_footwear'
    if eid in s['touched']:return 'existing_attempt_or_review_stays_in_previous_batch'
    reservations=s['reserved'].get(eid,[])
    if eid in own:
        allowed=set(SOURCE_BATCHES)|{base.QUEUE_PATH}
        if registry:
            allowed|={ASSIGNMENTS,MANIFESTS['generator-a'],*registry['batch_paths']}
        if any(r['branch']!=base.BRANCH or r['path'] not in allowed for r in reservations):return 'assigned_or_referenced_by_another_agent'
        row=own[eid]['row']
        if row['attempts']!=0 or row['status']!='ready' or row['technical_status']!='ready' or not row['generation_prompt']:return 'own_plan_not_unexecuted_ready'
        if any(row.get(k)!=v for k,v in base.fields_for_id(eid,s).items()):return 'exact_catalog_source_mismatch'
        return 'available_own_unexecuted_plan'
    if reservations:return 'existing_assignment_retained'
    return 'unprepared_no_verified_concrete_prompt'

def protected_files():
    # The queue and narrow output allowlist are the only existing files changed.
    paths=base.git('ls-files').decode().splitlines()
    # Existing PNGs are checked by Git tree presence only; do not reread or audit
    # all image bytes. Git diff separately verifies that no image was modified.
    return {p:file_sha(p) for p in paths if p not in [base.QUEUE_PATH,'.gitignore'] and not p.lower().endswith('.png')}

def role_paths(role):
    return {'planned_worker_branch':'agent-06-generator-a-2026-10-02' if role=='generator-a' else 'agent-07-generator-b-2026-10-02',
            'cloud_result_root':f'/workspace/exercise-image-results/{ROUND}/{role}',
            'repository_result_root':f'assets/exercises/pending/{ROUND}/{role}',
            'manifest_path':MANIFESTS[role]}

def make_row(eid,bid,role,s):
    origin=source_rows()[eid];row=copy.deepcopy(origin['row'])
    for k,v in base.fields_for_id(eid,s).items():
        if row.get(k)!=v:raise ValueError('Exact-ID source mismatch: '+eid+':'+k)
    p=role_paths(role);png=f"{p['cloud_result_root']}/{bid}/{eid}/attempt-1.png";gitpng=f"{p['repository_result_root']}/{bid}/{eid}/attempt-1.png"
    row.update(batch_id=bid,assigned_generator=role,assignment_registry_path=ASSIGNMENTS,assignment_status='assigned_preparation_only',
               source_preparation_batch_id=origin['batch_id'],source_preparation_batch_path=origin['path'],source_preparation_batch_sha256=file_sha(origin['path']),
               source_preparation_prompt_sha256=origin['row']['prompt_sha256'],catalog_source_commit=s['commits']['origin/work'],
               source_url=CATALOG_URL+s['commits']['origin/work']+'/'+base.CATALOG_PATH,source_selector=f'exercises[id="{eid}"]',
               planned_png_path=png,planned_git_png_path=gitpng,planned_output_relative_path=f'{ROUND}/{role}/{bid}/{eid}/attempt-1.png',
               style_path='docs/exercise-image-style.md',style_sha256=s['style_sha256'],generation_authorized_now=False)
    payload=copy.deepcopy(row['prompt_payload']);payload['planned_output_do_not_render_as_text']={'batch_id':bid,'exercise_id':eid,'assigned_generator':role,'cloud_path':png,'repository_path':gitpng}
    prompt='Create exactly ONE square transparent PNG of the exact exercise and selected single phase. Metadata fields must never appear as text.\nDo not render multiple phases, raw disputed alternatives, or inferred muscle targets.\n'+json.dumps(payload,ensure_ascii=False,sort_keys=True,indent=2)
    row.update(prompt_payload=payload,generation_prompt=prompt,prompt_sha256=base.sha(prompt.encode()))
    return row

def validate(s,registry,batches,frozen):
    errors=[];seen=set();old=source_rows()
    def check(ok,msg):
        if not ok:errors.append(msg)
    counts=collections.Counter(e['id'] for e in s['catalog']['exercises'])
    check(len(counts)==451 and set(counts.values())=={1},'451_unique_IDs')
    check(sum(len(e['content']) for e in s['catalog']['exercises'])==4448,'4448_language_blocks')
    check(s['local_reference_sha256']==s['reference_sha256'],'local_reference_matches_Git')
    check(registry['generation_authorized_now'] is False,'no_generation_in_preparation')
    for b in batches:
        check(1<=b['exercise_count']<=10 and b['exercise_count']==len(b['exercises']),'batch_size:'+b['batch_id'])
        check(b['exercise_ids']==[r['exercise_id'] for r in b['exercises']],'batch_ID_list:'+b['batch_id'])
        check(b['style_version']=='v1' and b['catalog_sha256']==s['catalog_sha256'] and b['style_sha256']==s['style_sha256'],'batch_source_style:'+b['batch_id'])
        expected_role='generator-a' if registry['batch_paths'].index(b['batch_path'])<3 else 'generator-b'
        check(b['assigned_generator']==expected_role,'role_order:'+b['batch_id'])
        for r in b['exercises']:
            eid=r['exercise_id'];check(eid not in seen,'duplicate:'+eid);seen.add(eid)
            check(disposition(eid,s,registry)=='available_own_unexecuted_plan','live_assignment_PNG_or_blocker:'+eid)
            check(eid in old,'not_an_owned_unexecuted_source:'+eid)
            if eid not in old:continue
            pinned=dict(s);pinned['commits']=dict(s['commits']);pinned['commits']['origin/work']=b['catalog_source_commit']
            check(r==make_row(eid,b['batch_id'],b['assigned_generator'],pinned),'full_prompt_source_output_binding:'+eid)
            check(r['scene']==old[eid]['row']['scene'] and r['technique_resolution']==old[eid]['row']['technique_resolution'],'unchanged_verified_technique:'+eid)
            check(r['prompt_payload']['style']==old[eid]['row']['prompt_payload']['style'],'unchanged_approved_style:'+eid)
            check(r['attempts']==0 and r['result_path'] is None and r['user_review'] is None,'no_attempt_or_image_approval:'+eid)
    check(seen==set(registry['exercise_ids']) and registry['prepared_count']==len(seen),'registry_ID_set')
    check(registry['shortfall']==50-len(seen),'shortfall50')
    check(len(registry['assignments'])==2,'two_role_records')
    for a in registry['assignments']:
        expected=[r['exercise_id'] for b in batches if b['assigned_generator']==a['generator'] for r in b['exercises']]
        check(a['exercise_ids']==expected and a['exercise_count']==len(expected),'exact_role_assignment:'+a['generator'])
    for transition in registry['supersedes_own_unexecuted_plans']:
        check(transition['source_batch_path'] in SOURCE_BATCHES and transition['source_batch_sha256']==file_sha(transition['source_batch_path']),'supersession_source_hash')
        check(all(eid in old and old[eid]['path']==transition['source_batch_path'] for eid in transition['exercise_ids']),'supersession_exact_IDs')
    for p,h in frozen.items():check(file_sha(p)==h,'protected_file_changed:'+p)
    q=prior.load(base.QUEUE_PATH);qrows={r['exercise_id']:r for r in q['exercises']}
    check(len(qrows)==len(q['exercises']) and len(q['eligible_exercise_ids'])==len(set(q['eligible_exercise_ids'])),'queue_ID_unique')
    for b in batches:
        for eid in b['exercise_ids']:check(qrows[eid]['batch_id']==b['batch_id'],'queue_route:'+eid)
    return {'status':'failed' if errors else 'passed','errors':errors,'checked_at':now(),'audited_commits':s['commits'],
            'prepared_count':len(seen),'shortfall':50-len(seen),'protected_sha256':frozen,
            'checks':['exact_ID_catalog_English_equipment_muscles_SHA256','all451_4448_source_immutable','no_existing_PNG_in_any_fetched_branch',
                      'no_foreign_assignment_or_attempt_taken','explicit_own_plan_supersession_only','unchanged_scene_style_reference',
                      'exact_A_B_scope_and_future_PNG_path','source_001_023_immutable','no_generation_Supabase_or_shared_progress_write']}

def handoff_text(role,core,registry):
    a=next(r for r in registry['assignments'] if r['generator']==role);p=role_paths(role)
    lines=[f'# Передача: {role}', '',f"Джерело: `{base.BRANCH}`, commit `{core}`.",f"Файл призначень: `{ASSIGNMENTS}`. Статус `{a['status']}`; {a['exercise_count']} вправ.", '',
           '```text','Порядок пакетів: '+(', '.join(a['batch_ids']) or 'немає'),'```','']
    for bid,path in zip(a['batch_ids'],a['batch_paths']):
        b=prior.load(path);lines += [f"Пакет `{bid}` — `{path}`:",'']+[f"- `{r['exercise_id']}` — {r['name']}" for r in b['exercises']]+['']
    lines += [f"Окрема гілка: `{p['planned_worker_branch']}`; почати саме від source commit, не змінювати поточні гілки інших агентів.",
              f"Локальні PNG: `{p['cloud_result_root']}/<batch_id>/<exercise_id>/attempt-1.png`.",
              f"PNG у Git: `{p['repository_result_root']}/<batch_id>/<exercise_id>/attempt-1.png`.",
              f"Власний manifest: `{p['manifest_path']}`; shared progress не змінювати.",'',
              'Еталон: `assets/exercises/biceps-curl-dumbbell.png`; SHA256 `52fef743ba2d7689aa81a8b995df3c6715cbb5d04c4bd688af4ca57b2d20057f`. Використовувати лише зовнішність/пропорції/матеріали; поза, обладнання та м’язи — exact-ID prompt.',
              'Стиль цих конкретних primary — `v1`, файл `docs/exercise-image-style.md`, SHA256 `8956307274990bdefd11bcc18e6d6deb2aed35580b5c2ea3ac0061dee708e578`. Загальне затверджене доповнення `docs/exercise-image-style-neutral-primary.md` прочитати також; broad-primary правило не потрібно для цих 12 concrete-primary записів. Не змінювати жоден стиль.', '',
              'Старі 017–018 є незмінними історичними підготовчими планами. Лише зазначені в assignments ID переадресовано на 024–025; не запускати для них старі пакети паралельно. 009 і чужі черги/завдання не забирати.', '',
              'Перед КОЖНИМ викликом fetch усі доступні remote heads і звірити actual PNG paths, manifests/queues/assignments. За наявного PNG будь-якого review — skip без повтору. Якщо інший агент уже має active assignment/call/PNG — skip/conflict у власному manifest, без переназначення. Непушені дані інших задач можуть бути невидимі.',
              'Для будь-якого майбутнього результату user_review=pending до явного рішення користувача; agent_visual_review=not_performed. Технічні dimension/alpha/path/hash перевірки записувати окремо; не ресайзити й не виправляти PNG автоматично.',
              'Один виклик на ID цієї передачі. При quota/usage_limit_reached/HTTP429 зупинити ВСІ наступні виклики одразу, записати помилку/resume_at та push checkpoint без повторів. Не переходити до решти ID чи іншого пакета після quota. Failed/noPNG — продовження цього самого batch/manifest лише за наступним прямим дорученням, не нове завдання.',
              'Після кожного пакета зберегти незмінні фактичні PNG, ID/prompt/style/reference/catalog hashes, actual attempt/path/PNG SHA256 у своєму manifest; commit і push лише власну нову worker-гілку, потім fetch/перевірити віддалені файли. Pending PNG paths уже мають вузькі .gitignore винятки. Не пушити work або підготовчу гілку. Supabase, catalogue, shared progress, чужі manifests не змінювати.', '',
              'Лише вбудований image_gen.imagegen; не платний API. Цей файл не запускає генерацію: почати лише після отримання користувацького повідомлення на виконання.', '']
    if not a['exercise_count']:lines += ['**Зараз 0 призначених ID і 0 пакетів. Генератор не викликати; нову гілку не створювати. Не брати завдання A або старі пакети.**','']
    return '\n'.join(lines)

def message_text(role,core,registry):
    a=next(r for r in registry['assignments'] if r['generator']==role);p=role_paths(role)
    scope=' → '.join(a['batch_ids']) or 'немає'
    lines=[f"Генератор {'A' if role=='generator-a' else 'B'}: джерело romanthoruk2008-pixel/lightweight-exercises-photo, гілка {base.BRANCH}, commit {core}.",
           f"Прочитай {ASSIGNMENTS} і {HANDOFFS[role]} (handoff у поточній вершині підготовчої гілки; дані/пакети зафіксовані в наведеному source commit).",
           f"Твій порядок: {scope}. Тільки {a['exercise_count']} ID з секції {role}; інші завдання не забирай.",
           f"Власна гілка для цього призначення: {p['planned_worker_branch']}, від наведеного source commit.",
           'Еталон assets/exercises/biceps-curl-dumbbell.png, SHA256 52fef743ba2d7689aa81a8b995df3c6715cbb5d04c4bd688af4ca57b2d20057f — лише зовнішність і матеріали. Стиль v1: docs/exercise-image-style.md; також прочитай docs/exercise-image-style-neutral-primary.md. Техніку/обладнання/підсвітку бери з exact-ID batch prompt.',
           f"PNG: {p['cloud_result_root']}/<batch_id>/<exercise_id>/attempt-1.png; у Git {p['repository_result_root']}/<batch_id>/<exercise_id>/attempt-1.png. Manifest: {p['manifest_path']}.",
           'Перед кожним викликом fetch усі агентські гілки й work, звір PNG та призначення. Наявний PNG, включно з pending, пропускай. Історичні 017–018 для цих ID замінені 024–025 в assignments; не запускати обидві версії.',
           'Один виклик на ID через вбудований image_gen.imagegen. user_review=pending до мого явного схвалення; agent_visual_review=not_performed. Не роби автоматичних повторів/ресайзу/корекцій.',
           'Після кожного пакета збережи PNG і власний manifest з exact ID/path/hashes, commit/push власної гілки й перевір віддалені файли. При quota/HTTP429 одразу зупини всі подальші виклики, збережи й запуш checkpoint без повтору.',
           'Каталог, shared progress, чужі manifests, work і підготовчу гілку не змінюй. Supabase не використовуй.']
    if a['exercise_count']:lines += ['Виконай тільки це призначення після отримання цього повідомлення від користувача.']
    else:lines += ['Зараз призначень для B немає: генерацію не запускай і worker-гілку не створюй. Очікуй нового списку, не підбирай вправи самостійно.']
    return '\n\n'.join(lines)+'\n'

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--prepare',action='store_true');parser.add_argument('--check',action='store_true');parser.add_argument('--handoffs',action='store_true');args=parser.parse_args()
    if sum([args.prepare,args.check,args.handoffs])!=1:parser.error('Select one action')
    if base.git('branch','--show-current').decode().strip()!=base.BRANCH:raise ValueError('Wrong branch')
    if args.handoffs:
        registry=prior.load(ASSIGNMENTS);core=base.git('rev-parse','HEAD').decode().strip()
        # Core commit really contains the exact published batch/assignment data.
        for path in [ASSIGNMENTS,*registry['batch_paths']]:
            if base.git('show',core+':'+path)!=(ROOT/path).read_bytes():raise ValueError('Core data not committed: '+path)
        for role in ROLES:
            (ROOT/HANDOFFS[role]).write_text(handoff_text(role,core,registry));(ROOT/MESSAGES[role]).write_text(message_text(role,core,registry))
        return
    s=snapshot()
    if args.prepare:
        for p in [ASSIGNMENTS,AUDIT,VALIDATION,*MANIFESTS.values(),SUMMARY]:
            if (ROOT/p).exists():raise ValueError('Round already exists: '+p)
        frozen=protected_files();timestamp=now();rows=[];eligible=[]
        for eid,e in s['by_id'].items():
            reason=disposition(eid,s)
            if reason=='available_own_unexecuted_plan':eligible.append(eid)
            rows.append({'exercise_id':eid,'name':e['name'],'archived':e['archived'],'equipment':e['equipment'],'equipment_group':s['classifications'][eid],
                         'catalog_record_sha256':base.value_sha(e),'disposition':reason,'PNG_sources':compact_sources(s['png_sources'].get(eid,[])),
                         'reservation_sources':compact_sources(s['reserved'].get(eid,[])),'attempt_sources':compact_sources(s['touched'].get(eid,[]))})
        # Preserve original source order using ID lookup, never array-position joins.
        ordered=[eid for eid in source_rows() if eid in eligible][:50]
        numbers=[int(m.group(1)) for paths in s['trees'].values() for p in paths if (m:=re.search(r'agent-03-others-(\d{3})',p))]
        first=max(numbers,default=0)+1;batches=[]
        for i in range(0,len(ordered),10):
            bid=f'agent-03-others-{first+i//10:03}';path=f'data/batches/{bid}.json';role='generator-a' if i//10<3 else 'generator-b'
            if (ROOT/path).exists() or any(path in paths for paths in s['trees'].values()):raise ValueError('Batch number occupied: '+path)
            entries=[make_row(eid,bid,role,s) for eid in ordered[i:i+10]]
            batches.append({'schema_version':1,'batch_id':bid,'batch_path':path,'status':'ready','owner_agent':'agent-03','branch':base.BRANCH,'assigned_generator':role,
                            'prepared_at':timestamp,'catalog_path':base.CATALOG_PATH,'catalog_sha256':s['catalog_sha256'],'catalog_source_commit':s['commits']['origin/work'],
                            'style_version':'v1','style_path':'docs/exercise-image-style.md','style_sha256':s['style_sha256'],
                            'exercise_count':len(entries),'exercise_ids':[r['exercise_id'] for r in entries],'exercises':entries,'assignment_registry_path':ASSIGNMENTS,'generation_authorized_now':False})
        registry={'schema_version':1,'assignment_round':ROUND,'status':'partial_ready_insufficient_eligible_exercises','prepared_at':timestamp,
                  'source_branch':base.BRANCH,'source_content_parent_commit':s['commits']['HEAD'],'catalog_source_commit':s['commits']['origin/work'],
                  'requested_count':50,'requested_batch_count':5,'prepared_count':len(ordered),'shortfall':50-len(ordered),'exercise_ids':ordered,
                  'batch_paths':[b['batch_path'] for b in batches],'audited_commits':s['commits'],'catalog_sha256':s['catalog_sha256'],
                  'generation_authorized_now':False,'execution_requires_user_delivery_to_generator':True,
                  'supersedes_own_unexecuted_plans':[{'source_batch_id':prior.load(path)['batch_id'],'source_batch_path':path,'source_batch_sha256':file_sha(path),
                     'exercise_ids':[i for i in ordered if source_rows()[i]['path']==path],'new_batch_ids':[b['batch_id'] for b in batches if any(source_rows()[i]['path']==path for i in b['exercise_ids'])],
                     'status':'superseded_for_listed_IDs_only','foreign_or_attempted_assignments_taken':False} for path in SOURCE_BATCHES],
                  'assignments':[{'generator':role,'status':'ready' if any(b['assigned_generator']==role for b in batches) else 'held_no_eligible_exercises',
                     'requested_count':30 if role=='generator-a' else 20,'exercise_count':sum(b['exercise_count'] for b in batches if b['assigned_generator']==role),
                     'exercise_ids':[i for b in batches if b['assigned_generator']==role for i in b['exercise_ids']],
                     'batch_ids':[b['batch_id'] for b in batches if b['assigned_generator']==role],'batch_paths':[b['batch_path'] for b in batches if b['assigned_generator']==role],**role_paths(role)} for role in ROLES],
                  'limits':['Only fetched committed Git data are visible; unpushed files of other cloud tasks may be inaccessible.',
                            'No PNG pixel QA, no generation, no Supabase. Existing failed/noPNG calls remain in previous batch.',
                            'Original 017/018 files remain immutable historical preparation, not an additional live generation assignment.']}
        audit={'schema_version':1,'checked_at':timestamp,'catalog_count':451,'language_blocks':4448,'active_count':448,'archived_count':3,
               'catalog_sha256':s['catalog_sha256'],'audited_commits':s['commits'],'source_files':compact_sources(s['source_files']),
               'disjoint_counts':dict(collections.Counter(r['disposition'] for r in rows)),'eligible_IDs':ordered,'records':rows,'limits':registry['limits']}
        q=prior.load(base.QUEUE_PATH);mapped={r['exercise_id']:r for r in q['exercises']}
        for b in batches:
            for row in b['exercises']:
                qr=mapped[row['exercise_id']];qr.update(batch_id=b['batch_id'],assigned_generator=b['assigned_generator'],assignment_registry_path=ASSIGNMENTS,
                        source_preparation_batch_id=row['source_preparation_batch_id'],style_version='v1',status='ready')
        q['batch_paths'] += registry['batch_paths'];q['latest_launch_ids']=ordered;q['updated_at']=timestamp
        q['next50_preparation']={'assignment_registry_path':ASSIGNMENTS,'new_batch_paths':registry['batch_paths'],'exercise_ids':ordered,
                  'prepared_count':len(ordered),'shortfall':50-len(ordered),'eligible_audit_path':AUDIT,'superseded_preparation_batch_ids':[prior.load(p)['batch_id'] for p in SOURCE_BATCHES],
                  'status':registry['status'],'generation_authorized_now':False}
        q['preparation_rounds'].append({'round':7,'prepared_at':timestamp,'exercise_ids':ordered,'batch_paths':registry['batch_paths'],
                                      'kind':'reassign_own_unexecuted_plans_not_new_unique_IDs','assignment_registry_path':ASSIGNMENTS,'audited_commits':s['commits']})
        q['count_semantics']='210 unique historically prepared IDs; this round reassigns 12 own unexecuted plans, adds no new unique ID. Active routing is next50_preparation and its assignment registry. Previous rounds are historical.'
        prior.save(base.QUEUE_PATH,q)
        report=validate(s,registry,batches,frozen)
        if report['errors']:raise ValueError(json.dumps(report['errors']))
        for b in batches:prior.save(b['batch_path'],b)
        prior.save(ASSIGNMENTS,registry);prior.save(AUDIT,audit);prior.save(VALIDATION,report)
        for role in ROLES:
            rs=[r for b in batches if b['assigned_generator']==role for r in b['exercises']]
            prior.save(MANIFESTS[role],{'schema_version':1,'assignment_round':ROUND,'generator':role,'status':'planned_not_generated' if rs else 'held_no_assignments',
               'assignment_registry_path':ASSIGNMENTS,'source_branch':base.BRANCH,'generation_calls':0,'user_review_policy':'pending_until_explicit_user_approval',
               'exercises':[{'exercise_id':r['exercise_id'],'name':r['name'],'batch_id':r['batch_id'],'status':'assigned_not_generated','attempts':0,
                 'planned_cloud_path':r['planned_png_path'],'planned_repository_path':r['planned_git_png_path'],'result_path':None,'result_sha256':None,'user_review':None,
                 'source_catalog_sha256':r['source_catalog_sha256'],'source_catalog_record_sha256':r['source_catalog_record_sha256'],'prompt_sha256':r['prompt_sha256'],
                 'style_version':'v1','style_sha256':s['style_sha256'],'reference_sha256':s['reference_sha256']} for r in rs]})
        ignored=(ROOT/'.gitignore').read_text();ignored+='\n# Exact pending PNG outputs authorized for '+ROUND+' (12 assigned IDs).\n'
        for b in batches:
            for r in b['exercises']:ignored+='!/'+r['planned_git_png_path']+'\n'
        (ROOT/'.gitignore').write_text(ignored)
        lines=['# Наступні 50 — фактична доступність', '',f'Запит: 50; підготовлено **{len(ordered)}**, нестача **{50-len(ordered)}**.',
               'Тільки власні 017/018 без чужих призначень і спроб переадресовано в нові пакети; їхні файли не змінено. 009/foreign/blocked/deferred не взято.', '',
               '| Пакет | Генератор | Кількість | Файл |','| --- | --- | ---: | --- |']
        lines += [f"| {b['batch_id']} | {b['assigned_generator']} | {b['exercise_count']} | `{b['batch_path']}` |" for b in batches]
        lines += ['',f'Призначення: `{ASSIGNMENTS}`. Повна точна-ID класифікація залишку: `{AUDIT}`. Перевірка: `{VALIDATION}`.',
                  'B: held, 0 IDs. Два role handoff і два копійовані повідомлення мають source core commit; створюються після коміту даних.', '',
                  'Наявні PNG (включно з pending) виключено. 22 власні питання не затверджено; 111 machine/cable/Smith відкладено; 6 конструкцій неоднозначні; 15 чужих зарезервованих ID і 9 старих 009 лишаються у попередніх чергах. Непушені чужі дані можуть бути невидимі.',
                  'Без генерації, Supabase або запису shared progress. Старі 001–023 й усі catalog/style/source файли незмінні. Вузькі .gitignore винятки додають тільки 12 запланованих attempt-1 PNG, не інші медіа.', '']
        (ROOT/SUMMARY).write_text('\n'.join(lines))
    else:
        registry=prior.load(ASSIGNMENTS);batches=[prior.load(p) for p in registry['batch_paths']];saved=prior.load(VALIDATION)
        report=validate(s,registry,batches,saved['protected_sha256'])
    print(json.dumps({k:report[k] for k in ['status','prepared_count','shortfall','audited_commits','errors']},ensure_ascii=False,indent=2))
    if report['errors']:raise SystemExit(1)

if __name__=='__main__':main()
