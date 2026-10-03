#!/usr/bin/env python3
"""Source-supported common variants and explicit answers; preparation only.

Existing batches/results/catalog/shared progress are never edited.
--check validates exact-ID extraction, sources, ownership and frozen files.
"""
import argparse,collections,copy,hashlib,json,pathlib
import prepare_agent03_single_generator as p
import prepare_agent03_single_generator_followup as previous
import audit_agent03_unconfirmed as approval_audit
b=p.b;base=p.base;ROOT=p.ROOT
ROUND='agent-03-common-variants-2026-10-03'
DECISIONS=f'data/technique-decisions/{ROUND}.json'
BLOCKED=f'data/queues/{ROUND}-blocked.json'
CHECK=f'data/audits/{ROUND}-validation.json'
EVIDENCE=f'data/audits/{ROUND}-technique.json'
ERRORS=f'data/audits/{ROUND}-source-notes.json'
REG=f'data/assignments/{ROUND}.json'
MANIFEST=f'data/manifests/{ROUND}/generator-single.json'
HANDOFF=f'docs/{ROUND}-handoff.md'
REWORK=f'data/queues/{ROUND}-unconfirmed-rework.json'
VEST='docs/exercise-image-style-weighted-vest.md'
BATCHES=[f'data/batches/agent-03-others-{i:03}.json' for i in [37,38,39,40]]
CLOUD=f'/workspace/exercise-image-results/{ROUND}/generator-single'
GIT=f'assets/exercises/pending/{ROUND}/generator-single'
WORKER=p.WORKER;ROLE=p.ROLE
conflict=previous.conflict

def configure():
    d=b.load(DECISIONS);scenes={r['exercise_id']:r['selected_scene'] for r in d['records']}
    for key in ['ROUND','REG','MANIFEST','EVIDENCE','ERRORS','CHECK','HANDOFF','BATCHES','CLOUD','GIT','BLOCKED']:
        setattr(p,key,globals()[key])
    p.SCENES=scenes;p.EQUIPMENT_IDS=list(scenes);p.SOURCE_ERRORS={eid:True for eid in scenes};p.conflict=conflict
    return d,scenes

def check(s):
    d,scenes=configure();reg=b.load(REG);report=b.load(CHECK);q=b.load(base.QUEUE_PATH)
    assert base.git('branch','--show-current').decode().strip()==base.BRANCH
    assert s['catalog_sha256']==d['catalog_sha256']==reg['catalog_sha256']
    assert len(s['by_id'])==451 and sum(len(r['content']) for r in s['by_id'].values())==4448
    assert base.sha(base.git('show',s['commits']['origin/work']+':'+base.CATALOG_PATH))==s['catalog_sha256']
    for path,h in report['protected_sha256'].items():assert b.sha(path)==h,path
    qr={r['exercise_id']:r for r in q['exercises']}
    for eid,h in report['previous_queue_routes_sha256'].items():assert base.value_sha(qr[eid])==h,eid
    assert len(qr)==len(q['exercises'])==len(set(q['eligible_exercise_ids']))==q['prepared_count']==q['eligible_count']
    ids=[];assignments=b.actual_assignments(s)
    evidence=b.load(EVIDENCE);live=b.source_evidence(s,list(scenes))
    for old,new in zip(evidence['records'],live['records']):
        for k,v in new.items():assert old[k]==v,(old['exercise_id'],k)
    assert len(evidence['records'])==len(scenes)
    decisions={r['exercise_id']:r for r in d['records']}
    for bi,path in enumerate(BATCHES):
        batch=b.load(path);assert batch['execution_order']==bi+1 and batch['status']=='ready'
        assert batch['exercise_count']==len(batch['exercises'])==len(list(scenes)[bi*10:(bi+1)*10])
        assert 0<batch['exercise_count']<=10
        assert batch['exercise_ids']==[r['exercise_id'] for r in batch['exercises']]
        for r in batch['exercises']:
            eid=r['exercise_id'];ids.append(eid)
            for k,v in base.fields_for_id(eid,s).items():assert r[k]==v,(eid,k)
            assert conflict(eid,s,assignments,True) is None,(eid,conflict(eid,s,assignments,True))
            assert r['scene']==b.n.prior.scene(eid,scenes[eid],b.CAMERA)
            assert json.loads(r['generation_prompt'].split('\n',1)[1])==r['prompt_payload']
            assert base.sha(r['generation_prompt'].encode())==r['prompt_sha256']
            payload=r['prompt_payload'];assert payload['identity_do_not_render_as_text']['exercise_id']==eid
            for k in ['source_english','equipment','primary_muscle','secondary_muscles']:assert payload['exact_catalogue_source'][k]==r[k]
            assert payload['selected_render_scene']==r['scene']
            assert payload['technique_resolution']==r['technique_resolution']
            assert r['technique_resolution']['common_variant_decision']==decisions[eid]
            assert payload['style']['version']==r['style_version']
            if r['primary_muscle'] in ['full_body','cardio','other']:
                assert payload['style']['primary_highlight']['hex'] is None and r['style_version']==b.NEUTRAL_VERSION
            else:assert payload['style']['primary_highlight']['hex']=='#F26445'
            assert payload['style']['secondary_highlight']['intensity_fraction']==[0.4,0.5]
            assert r['human_reference']['sha256']==s['reference_sha256']
            for f in r['approved_style_files']:assert b.sha(f['path'])==f['sha256']
            assert r['planned_png_path']==f'{CLOUD}/{batch["batch_id"]}/{eid}/attempt-1.png'
            assert r['planned_git_png_path']==f'{GIT}/{batch["batch_id"]}/{eid}/attempt-1.png'
            assert r['attempts']==0 and r['user_review'] is None and r['result_path'] is None
            assert qr[eid]['batch_id']==batch['batch_id']
    assert len(ids)==len(set(ids))==len(scenes)==len(d['records'])
    assert 0<len(ids)<=len(BATCHES)*10
    assert reg['assignment_count']==len(reg['assignments'])==1 and reg['assignments'][0]['exercise_ids']==ids
    mr=[r for batch in b.load(MANIFEST)['batches'] for r in batch['exercises']]
    assert [r['exercise_id'] for r in mr]==ids
    assert set(q['current_blocked_ids'])|set(q['current_equipment_blocked_ids'])==set(b.load(BLOCKED)['exercise_ids'])
    assert not(set(ids)&set(b.load(BLOCKED)['exercise_ids']))
    # Rework is a separate planning queue, never a live assignment or PNG rejection.
    rework=b.load(REWORK);protected=set(rework['protected_approved_IDs']);targets={r['exercise_id'] for r in rework['exercises']}
    live_approvals,_=approval_audit.collect_review_evidence(s)
    assert not(targets&set(live_approvals)), sorted(targets&set(live_approvals))
    assert not(set(ids)&set(live_approvals)), sorted(set(ids)&set(live_approvals))
    assert not(targets&protected) and rework['exercise_count']==len(targets)
    for r in rework['exercises']:
        for k,v in base.fields_for_id(r['exercise_id'],s).items():assert r[k]==v
        assert r['status']=='awaiting_prompt_revalidation' and r['new_generation_calls']==0 and r['change_user_review'] is False
    # Saved excerpts must match the source copies and checksum, never a soft 404.
    for slug,res in d['resources'].items():
        assert res['http_status']==200 and base.sha(res['quotation'].encode())==res['quotation_sha256']
        file=pathlib.Path('/tmp/agent03-research-current')/(hashlib.sha256(res['url'].encode()).hexdigest()[:16]+'.json')
        raw=json.loads(file.read_text());assert raw['text_sha256']==res['text_sha256'] and raw['html_sha256']==res['html_sha256']
        assert all(part in raw['text'] for part in res['quotation'].split('\n'))
        assert res['quotation_section'] in raw['text'],(slug,'actual technique section missing')
        assert 'Bench Press Alternatives' not in res['quotation'],(slug,'navigation is not technique evidence')
    return {'status':'passed','exercise_count':len(ids),'batch_counts':[b.load(path)['exercise_count'] for path in BATCHES],
        'generator_count':1,'catalog_ID_count':451,'language_blocks':4448,'generation_calls':0,'errors':[],
        'rework_planning_count':len(targets),'protected_approved_count':len(protected),'remaining_blocked_count':len(b.load(BLOCKED)['exercise_ids']),
        'live_commits':s['commits'],'PNG_pixels_reviewed':False,
        'live_approved_intersections_with_new_batches':[],
        'live_approved_intersections_with_rework_queue':[]}

def prepare(s):
    d,scenes=configure();ids=list(scenes);oldq=b.load(base.QUEUE_PATH)
    assert all(path not in tree for path in BATCHES for tree in s['trees'].values())
    for path in BATCHES+[REG,MANIFEST,EVIDENCE,ERRORS,CHECK]:assert not(ROOT/path).exists(),path
    frozen=b.n.protected_files();assignments=b.actual_assignments(s)
    for eid in ids:assert conflict(eid,s,assignments) is None,(eid,conflict(eid,s,assignments))
    evidence=b.source_evidence(s,ids);evidence.update(audited_commits=s['commits'],decisions_path=DECISIONS,photos_or_video_downloaded=False,images_reviewed=False)
    decisions={r['exercise_id']:r for r in d['records']}
    for r in evidence['records']:r['common_variant_decision']=decisions[r['exercise_id']]
    b.save(EVIDENCE,evidence)
    b.save(ERRORS,{'schema_version':1,'catalog_sha256':s['catalog_sha256'],'catalog_modified':False,
       'records':[{'exercise_id':eid,'raw_english':s['by_id'][eid]['content']['en'],'prior_issue':decisions[eid]['prior_block_reason'],
       'resolution_kind':decisions[eid]['resolution_kind'],'source_decision_path':DECISIONS,'scene_only_resolution':scenes[eid],
       'scope':'Preserved raw fields; distinguish actual contradiction from underspecified contact or chosen allowed variant. No catalogue edit or PNG approval.'} for eid in ids]})
    batches=[]
    for i,path in enumerate(BATCHES):
        bid=path.rsplit('/',1)[1][:-5];group=ids[i*10:(i+1)*10];rows=[]
        for eid in group:
            row=p.route(p.make_equipment_row(eid,s,evidence),bid,s)
            resolution=row['technique_resolution'];resolution['decision_kind']=decisions[eid]['resolution_kind'];resolution['common_variant_decision']=decisions[eid]
            resolution['claim_limit']='External evidence scopes are explicit; component-only sources are not called exact-variant confirmation. Common scene selection is authorized, not individual user technique approval.'
            row['prompt_payload']['technique_resolution']=copy.deepcopy(resolution)
            if eid=='pushup-weighted':
                row['style_version']='v1-weighted-vest-2026-10-03';row['prompt_payload']['style']['version']=row['style_version']
                row['approved_style_files'].append({'path':VEST,'sha256':b.sha(VEST)});row['prompt_payload']['approved_style_files']=copy.deepcopy(row['approved_style_files'])
                row['prompt_payload']['style']['equipment_clothing_addendum']='Opaque secured weighted vest approved by user. Highlight only visible anatomical surfaces; do not render muscles through vest or paint equipment as muscle.'
            row['generation_prompt']='Create exactly ONE square 1024x1024 transparent PNG of this exact exercise and ONE selected phase. Metadata must never appear as image text.\n'+json.dumps(row['prompt_payload'],ensure_ascii=False,sort_keys=True,indent=2)
            row['prompt_sha256']=base.sha(row['generation_prompt'].encode());rows.append(row)
        batch={'schema_version':1,'batch_id':bid,'status':'ready','exercise_count':len(rows),'exercise_ids':group,'exercises':rows,
          'source_branch':base.BRANCH,'execution_branch':WORKER,'generator':ROLE,'assignment_registry_path':REG,'execution_order':i+1,
          'catalog_sha256':s['catalog_sha256'],'audited_commits':s['commits'],'generation_calls':0,'handoff_path':HANDOFF,'manifest_path':MANIFEST,'live_recheck_before_every_call':True}
        b.save(path,batch);batches.append(batch)
    tasks=[r for doc in batches for r in doc['exercises']]
    b.save(REG,{'schema_version':1,'assignment_id':ROUND,'source_branch':base.BRANCH,'source_base_commit':s['commits']['HEAD'],'status':'ready',
        'catalog_sha256':s['catalog_sha256'],'exercise_count':len(ids),'assignment_count':1,'batch_paths':BATCHES,
        'assignments':[{'generator':ROLE,'execution_branch':WORKER,'status':'assigned','exercise_count':len(ids),'exercise_ids':ids,'batch_paths':BATCHES,'execution_order':[1,2,3,4],'manifest_path':MANIFEST,'handoff_path':HANDOFF}],
        'execution_gate':'Continue after existing 034–036; preserve all older tasks/results/history. This assignment contains only newly resolved missing-PNG IDs, not the separate unconfirmed rework planning queue.',
        'audited_commits':s['commits'],'supersedes_other_agents':False,'generation_calls_by_preparer':0,'decisions_path':DECISIONS,'blocked_path':BLOCKED,'rework_planning_queue_path':REWORK,
        'results_git_root':GIT,'results_cloud_root':CLOUD,'scope_limit':'Pushed Git only; unpushed outputs/approvals/live calls may be unavailable. Recheck before every call.'})
    b.save(MANIFEST,{'schema_version':1,'manifest_id':ROUND,'source_branch':base.BRANCH,'execution_branch':WORKER,'generator':ROLE,'assignment_path':REG,'status':'ready_not_started','exercise_count':len(ids),'generation_calls':0,
        'user_review_policy':'pending on result creation until explicit user approval','quota_rule':'Save first quota/rate-limit failure/history, push checkpoint and stop without repeat calls.',
        'batches':[{'batch_id':doc['batch_id'],'batch_path':path,'status':'ready','exercise_count':doc['exercise_count'],'exercises':[
         {'exercise_id':r['exercise_id'],'name':r['name'],'status':'not_started','attempts':0,'attempt_history':[],'user_review':None,'technical_check':None,'agent_visual_review':'not_performed','result_path':None,
          **{k:r[k] for k in ['planned_png_path','planned_git_png_path','prompt_sha256','source_catalog_sha256','style_version']}} for r in doc['exercises']]} for path,doc in zip(BATCHES,batches)]})
    q=copy.deepcopy(oldq);qr={r['exercise_id']:r for r in q['exercises']}
    for r in tasks:
        eid=r['exercise_id'];assert eid not in qr,eid
        q['exercises'].append({k:copy.deepcopy(r[k]) for k in ['exercise_id','name','equipment','primary_muscle','secondary_muscles','source_catalog_sha256','source_catalog_record_sha256','source_english_sha256','status','assigned_generator','batch_id','prompt_prepared','style_version','assignment_registry_path']})
        q['exercises'][-1]['current_task_path']=f'data/batches/{r["batch_id"]}.json';q['eligible_exercise_ids'].append(eid)
    q['batch_paths'].extend(BATCHES);q.update(updated_at=p.now(),eligible_count=len(q['eligible_exercise_ids']),prepared_count=len(q['eligible_exercise_ids']),latest_launch_ids=ids)
    q['current_blocked_ids']=[eid for eid in oldq['current_blocked_ids'] if eid not in ids]
    q['current_equipment_blocked_ids']=[eid for eid in oldq['current_equipment_blocked_ids'] if eid not in ids]
    q['current_equipment_blocked_count']=len(q['current_equipment_blocked_ids']);q['current_equipment_blocked_path']=BLOCKED;q['current_equipment_blocked_selector']='exercises'
    q['current_technique_blocked_path']=BLOCKED
    q['common_variant_preparation']={'assignment_path':REG,'batch_paths':BATCHES,'exercise_count':len(ids),'generator':ROLE,'execution_branch':WORKER,'handoff_path':HANDOFF,'source_decisions_path':DECISIONS,'generation_calls':0}
    q['unconfirmed_rework_policy']={'queue_path':REWORK,'accepted_approved_IDs_protected':True,'preserve_all_old_PNGs_and_attempts':True,'shared_review_statuses_unchanged':True,'planning_only_no_new_rework_assignment':True}
    q['phase_plan']['latest_equipment_allocation_path']=REG;q['phase_plan']['equipment_clarifications_path']=BLOCKED
    q['phase_plan']['phase2_execution_gate']='Existing 034–036 first; then same single worker 037–040. Unconfirmed-PNG rework is a separate plan requiring live approval/ownership/prompt validation; never touch approved/accepted IDs.'
    b.save(base.QUEUE_PATH,q)
    with (ROOT/'.gitignore').open('a') as f:
        f.write('\n# Exact pending paths for source-supported common variants and user answers.\n')
        for r in tasks:f.write('!/'+r['planned_git_png_path']+'\n')
    b.save(CHECK,{'schema_version':1,'status':'pending_validation','protected_sha256':frozen,'previous_queue_routes_sha256':{r['exercise_id']:base.value_sha(r) for r in oldq['exercises']},'catalog_sha256':s['catalog_sha256']})
    result=check(s);report=b.load(CHECK);report.update(result,checked_at=p.now());b.save(CHECK,report);return result

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--fetch',action='store_true');ap.add_argument('--prepare',action='store_true');args=ap.parse_args()
    configure()
    if args.fetch:b.fetch_heads()
    s=b.n.snapshot();result=prepare(s) if args.prepare else check(s)
    print(json.dumps(result,ensure_ascii=False,indent=2))
