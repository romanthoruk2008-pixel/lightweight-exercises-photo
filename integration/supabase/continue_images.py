#!/usr/bin/env python3
"""Continue approved-image imports; never insert or modify catalog content.

First fetch generator refs with native Git. Default mode prepares and verifies
only; --apply enables approved Storage POSTs and five-field catalog PATCHs.
Checkpoints pin Git commits, approvals, hashes and the initial database state.
PNG staging is outside the repository, entirely in the cloud workspace.
"""
import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import re
import subprocess
import sys

import import_catalog_images as legacy

ROOT = legacy.source.ROOT
STAGING = Path('/workspace/supabase-image-staging')
FIELDS = legacy.IMAGE_FIELDS


def git(*args):
    return subprocess.check_output(['git', *args], cwd=ROOT)


def document(commit, path):
    return json.loads(git('show', commit + ':' + path))


def ancestor(first, second):
    return subprocess.run(['git', 'merge-base', '--is-ancestor', first, second],
                          cwd=ROOT, capture_output=True).returncode == 0


def path_of(value):
    return legacy.source.source_path(value)


class ImagesOnlyApi(legacy.Api):
    def request(self, method, path, payload=None, headers=None, authenticated=True):
        if method != 'GET':
            if method == 'PATCH' and path.startswith('/rest/v1/catalog_exercise?'):
                if not isinstance(payload, dict) or set(payload) != set(FIELDS):
                    raise RuntimeError('Only the five image fields may be patched')
            elif not (method == 'POST' and path.startswith(
                    '/storage/v1/object/' + legacy.source.BUCKET + '/')):
                raise RuntimeError('Catalog INSERTs and other writes are prohibited')
        return super().request(method, path, payload, headers, authenticated)


def known_transfers():
    records = {}
    patches = {(v['exercise_id'], v['accepted_sha256']): v['proposed_image_patch']
               for v in legacy.source.read_json(ROOT/'integration/supabase/results/approved_png_plan.json')}
    for file in (ROOT/'integration/supabase/uploads').glob('*/plan.json'):
        for v in legacy.source.read_json(file).get('images', []):
            patches[(v['exercise_id'], v['accepted_sha256'])] = v['proposed_image_patch']
    for file in sorted((ROOT / 'integration/supabase/uploads').rglob('batch-*.json')):
        doc = legacy.source.read_json(file)
        if doc.get('project_ref') != legacy.source.HOST.split('.')[0]:
            raise RuntimeError('Checkpoint project mismatch')
        for row in doc.get('entries', {}).values():
            if row.get('status') != 'complete':
                continue
            if (row['file_verification']['sha256'] != row['accepted_sha256']
                    or not row['database_verification']['image_fields_equal']):
                raise RuntimeError('Unverified completed checkpoint')
            identity = (row['exercise_id'], row['accepted_sha256'])
            if identity not in patches:
                raise RuntimeError('Completed checkpoint has no verified image patch')
            records[identity] = {**row, '_verified_image_patch': patches[identity]}
    return records


def explicit_evidence(progress, manifests, eid, sha):
    history = progress.get('user_review_history', [])
    decision = history[-1] if history else progress.get('approval_decision', {})
    if (decision.get('by') != 'user'
            or decision.get('accepted_sha256', decision.get('sha256')) != sha):
        return None
    if decision.get('decision') == 'approved':
        return decision
    if decision.get('decision') is not None:
        return None
    # Agent-05 records per-file accepted hash and an explicit batch decision.
    for _, doc in manifests:
        batch = doc.get('approval_decision', {})
        if (batch.get('by') == 'user' and batch.get('decision') == 'approved'
                and eid in batch.get('exercise_ids', [])):
            return {'file_decision': decision, 'batch_decision': batch}
    return None


def manifest_pending_records(manifests, files):
    """Parallel generators may intentionally leave shared progress unchanged."""
    result = []
    for manifest_path, doc in manifests:
        records = doc.get('images', doc.get('exercises', doc.get('results', [])))
        records = records.values() if isinstance(records, dict) else records
        for row in records:
            if row.get('user_review') != 'pending':
                continue
            sha = row.get('result_sha256') or row.get('sha256')
            if not sha:
                continue
            paths = [path_of(row.get(k)) for k in ('result_path', 'repository_path',
                'relative_png_path', 'planned_branch_path', 'branch_output_path', 'branch_result_path')]
            path = next((p for p in paths if p in files), None)
            if path:
                result.append({'exercise_id': row['exercise_id'], 'path': path,
                    'sha256': sha, 'manifest': manifest_path})
    return result


def scan(originals, known):
    refs = git('for-each-ref', '--format=%(refname:short)',
               'refs/remotes/origin').decode().splitlines()
    refs = [r for r in refs if r == 'origin/work' or (
        r.startswith('origin/agent-') and r != 'origin/agent-04-supabase-integration')]
    snapshots, candidates, pending, progress_snapshots = [], {}, {}, []
    for ref in refs:
        commit = git('rev-parse', ref).decode().strip()
        files = set(git('ls-tree', '-r', '--name-only', commit).decode().splitlines())
        if 'data/exercise-image-progress.json' not in files:
            continue
        catalog_raw = git('show', commit + ':data/exercises/catalog.json')
        if legacy.source.digest(catalog_raw) != legacy.source.CATALOG_SHA256:
            raise RuntimeError('Source catalog changed: ' + ref)
        progress = document(commit, 'data/exercise-image-progress.json')['exercises']
        progress_snapshots.append((commit, progress))
        manifests = [(p, document(commit, p)) for p in sorted(files)
                     if p.startswith('data/') and 'manifest' in p and p.endswith('.json')]
        for record in manifest_pending_records(manifests, files):
            if record['exercise_id'] not in originals:
                raise RuntimeError('Unknown manifest exercise ID')
            pending.setdefault(record['exercise_id'], []).append({
                'branch': ref, 'path': record['path'], 'sha256': record['sha256'],
                'manifest': record['manifest']})
        snapshots.append({'branch': ref.removeprefix('origin/'), 'commit': commit,
                          'manifests': [p for p, _ in manifests]})
        for eid, row in progress.items():
            if row.get('user_review') == 'pending' and row.get('result_sha256'):
                paths = [path_of(row.get(k)) for k in ('result_path', 'repository_path', 'relative_png_path')]
                for _, doc in manifests:
                    records = doc.get('images', doc.get('exercises', []))
                    records = records.values() if isinstance(records, dict) else records
                    for record in records:
                        if (record.get('exercise_id') == eid and record.get('user_review') == 'pending'
                                and record.get('result_sha256', record.get('sha256')) == row['result_sha256']):
                            paths.extend(path_of(record.get(k)) for k in
                                         ('result_path', 'repository_path', 'relative_png_path', 'planned_branch_path'))
                path = next((p for p in paths if p in files), None)
                if path:
                    pending.setdefault(eid, []).append({'branch': ref, 'path': path,
                        'sha256': row['result_sha256']})
            if row.get('user_review') != 'approved':
                continue
            sha = row.get('accepted_sha256')
            if eid not in originals or not isinstance(sha, str) or not re.fullmatch('[0-9a-f]{64}', sha):
                raise RuntimeError('Invalid accepted ID/hash: ' + eid)
            witnesses, paths = [], []
            for manifest_path, doc in manifests:
                rows = doc.get('images', doc.get('exercises', []))
                rows = rows.values() if isinstance(rows, dict) else rows
                for record in rows:
                    if record.get('exercise_id') != eid or record.get('user_review') != 'approved':
                        continue
                    accepted = record.get('accepted_sha256') or record.get('sha256') or record.get('result_sha256')
                    if accepted != sha:
                        continue
                    witnesses.append({'manifest': manifest_path,
                        'accepted_sha256': sha, 'user_review': 'approved',
                        'technical_check': record.get('technical_check'),
                        'technical_exceptions': record.get('technical_exceptions', [])})
                    for name in ('accepted_repository_path', 'repository_path',
                                 'accepted_relative_png_path', 'relative_png_path', 'accepted_path'):
                        path = path_of(record.get(name))
                        if path in files:
                            paths.append(path)
            evidence = explicit_evidence(row, manifests, eid, sha)
            paths = [p for p in [path_of(row.get('accepted_repository_path')),
                     path_of(row.get('accepted_path')), *paths] if p in files]
            candidates.setdefault(eid, []).append({'exercise_id': eid,
                'accepted_sha256': sha, 'source_branch': ref.removeprefix('origin/'),
                'source_commit': commit, 'source_png': paths[0] if paths else None,
                'explicit_user_approval': evidence,
                'manifest_witnesses': witnesses,
                'historical_technical_check': row.get('technical_check'),
                'historical_technical_check_details': row.get('technical_check_details'),
                'approval_technical_exceptions': row.get('approval_decision', {}).get('technical_exceptions', [])})
    selected, blocked = [], []
    for eid, versions in sorted(candidates.items()):
        tips = [v for v in versions if not any(v['source_commit'] != w['source_commit']
                and ancestor(v['source_commit'], w['source_commit']) for w in versions)]
        hashes = {v['accepted_sha256'] for v in tips}
        if len(hashes) != 1:
            blocked.append({'exercise_id': eid, 'reason': 'ambiguous_accepted_versions',
                            'sha256': sorted(hashes)})
            continue
        v = tips[0]
        if any(commit != v['source_commit'] and ancestor(v['source_commit'], commit)
               and progress[eid].get('user_review') != 'approved'
               for commit, progress in progress_snapshots):
            blocked.append({'exercise_id': eid, 'reason': 'descendant_progress_not_approved'})
            continue
        if not v['source_png'] or not v['manifest_witnesses']:
            blocked.append({'exercise_id': eid, 'reason': 'missing_accepted_file_or_manifest'})
            continue
        if (eid, v['accepted_sha256']) not in known and not v['explicit_user_approval']:
            blocked.append({'exercise_id': eid, 'reason': 'no_exact_explicit_user_decision'})
            continue
        selected.append(v)
    approved_ids = set(candidates)
    pending = {k: v for k, v in pending.items() if k not in approved_ids}
    return selected, snapshots, pending, blocked


def image_patch(row):
    return {k: row.get(k) for k in FIELDS}


def prepare(output, originals, known, api):
    selected, snapshots, pending, blocked = scan(originals, known)
    current = api.catalog()
    catalog_check = legacy.verify_catalog(current, originals)
    raw, _, _ = api.require('GET', '/storage/v1/bucket')
    bucket = next(b for b in json.loads(raw) if b['id'] == legacy.source.BUCKET)
    if (bucket['public'] is not True or bucket['file_size_limit'] != legacy.source.SIZE_LIMIT
            or bucket['allowed_mime_types'] != ['image/png']):
        raise RuntimeError('Bucket constraints changed')
    prior, plan = [], []
    desired = {v['exercise_id']: v['accepted_sha256'] for v in selected}
    for (eid, sha), record in sorted(known.items()):
        verification = legacy.verify_public(*api.public(record['storage_path']), sha)
        row = current[eid]
        matches = row['image_sha256'] == sha and row['image_path'] == record['storage_path']
        patch = record['_verified_image_patch']
        if matches and not legacy.image_matches(row, patch):
            raise RuntimeError('Previous image dimensions/origin changed: ' + eid)
        if not matches and row['image_sha256'] != desired.get(eid):
            raise RuntimeError('Previous database link conflicts: ' + eid)
        prior.append({'exercise_id': eid, 'accepted_sha256': sha,
            'storage_path': record['storage_path'], 'file_verification': verification,
            'database_image_fields': image_patch(row), 'current_link_matches': matches})
    for item in selected:
        eid, sha = item['exercise_id'], item['accepted_sha256']
        if (eid, sha) in known and current[eid]['image_sha256'] == sha:
            continue
        stage_root = STAGING/item['source_commit']
        staged = stage_root/item['source_png']
        raw = git('show', item['source_commit'] + ':' + item['source_png'])
        if legacy.source.digest(raw) != sha:
            blocked.append({'exercise_id': eid, 'reason': 'accepted_sha256_mismatch'})
            continue
        staged.parent.mkdir(parents=True, exist_ok=True)
        staged.write_bytes(raw)
        previous_root = legacy.source.ROOT
        try:
            legacy.source.ROOT = stage_root
            check = legacy.source.verify_png(item['source_png'], sha)
        finally:
            legacy.source.ROOT = previous_root
        if not check['ready_for_upload_bytes']:
            blocked.append({'exercise_id': eid, 'reason': 'png_bytes_not_ready', 'issues': check['issues']})
            continue
        destination = eid + '/' + sha + '.png'
        patch = {'image_path': destination, 'image_sha256': sha,
            'image_width': check['width'], 'image_height': check['height'], 'image_origin': 'generated'}
        if legacy.source.constraint_violations({**current[eid], **patch}):
            raise RuntimeError('Image patch violates schema checks: ' + eid)
        old = image_patch(current[eid])
        replacement = any(old[k] is not None for k in FIELDS) and not legacy.image_matches(current[eid], patch)
        if replacement and (eid, old['image_sha256']) not in known:
            blocked.append({'exercise_id': eid, 'reason': 'unverified_previous_image_link'})
            continue
        plan.append({**item, 'bucket': legacy.source.BUCKET, 'destination_path': destination,
            'public_url': legacy.source.BASE + '/storage/v1/object/public/' + legacy.source.BUCKET + '/' + destination,
            'staged_source_png': str(staged), 'staging_root': str(stage_root),
            'byte_verification': check, 'proposed_image_patch': patch,
            'expected_previous_image': old if replacement else None,
            'initial_image_fields': old, 'replacement': replacement})
    doc = {'project_ref': legacy.source.HOST.split('.')[0], 'created_at_utc': legacy.now(),
        'source_snapshots': snapshots, 'catalog_verification': catalog_check,
        'prior_transfers_reverified': prior, 'already_transferred': len(prior),
        'pending_skipped': len(pending), 'pending_ids': sorted(pending),
        'pending_sources': pending, 'blocked': blocked, 'images': plan,
        'catalog_import_prohibited': True}
    output.mkdir(parents=True, exist_ok=True)
    legacy.save(output/'plan.json', doc)
    return doc


def checkpoint_handoff(output, plan, batches):
    entries = [v for b in batches for v in b.get('entries', {}).values() if v.get('status') == 'complete']
    summary = {'project_ref': plan['project_ref'], 'source_snapshots': plan['source_snapshots'],
        'new_uploads': sum(e.get('storage_action') == 'uploaded_new_no_upsert' for e in entries),
        'completed_transfers': len(entries),
        'accepted_version_replacements': sum(bool(e.get('replaced_image')) for e in entries),
        'already_transferred_reverified': plan['already_transferred'],
        'pending_skipped': plan['pending_skipped'], 'blocked': plan['blocked'],
        'planned_transfers': len(plan['images']), 'catalog_imported_again': False,
        'errors': [b['last_error'] for b in batches if b.get('last_error')],
        'user_tables_schema_rls_grants_changed': False, 'updated_at_utc': legacy.now()}
    legacy.save(output/'summary.json', summary)
    old = ROOT/'integration/supabase/handoff.md'
    marker = '\n<!-- continuation:' + output.name + ' -->\n'
    text = old.read_text().split(marker)[0]
    old.write_text(text + marker + '\n## Продовження схвалених PNG — ' + output.name + '\n\n'
        + 'Поточна контрольна точка: `' + summary['updated_at_utc'] + '`.\n'
        + f"Нових Storage uploads: {summary['new_uploads']}; завершених перенесень: {len(entries)}; "
        + f"заміни прийнятих версій: {summary['accepted_version_replacements']}.\n"
        + f"Попередніх перевірено: {plan['already_transferred']}; pending пропущено: {plan['pending_skipped']}.\n"
        + f"Артефакти: `uploads/{output.name}/plan.json`, `batch-*.json`, `summary.json`.\n"
        + 'Каталог не імпортувався повторно. Використано `continue_images.py` і перевірений '
        + '`import_catalog_images.transfer_one`; лише Storage POST без upsert і п’ять image-полів '
        + 'із concurrency filters. Старі PNG не видаляються; content/451 ID/4448 мовних блоків незмінні.\n'
        + 'PNG staging поза Git: `/workspace/supabase-image-staging/<source_commit>/<source_png>`.\n')
    return summary


def validate_plan(plan, originals):
    if plan['project_ref'] != legacy.source.HOST.split('.')[0]:
        raise RuntimeError('Frozen plan project differs')
    identities = set()
    sources = {}
    for item in plan['images']:
        eid, sha, commit = item['exercise_id'], item['accepted_sha256'], item['source_commit']
        if eid not in originals or eid in identities or not re.fullmatch('[0-9a-f]{64}', sha):
            raise RuntimeError('Invalid frozen plan ID/hash')
        identities.add(eid)
        if commit not in sources:
            sources[commit] = document(commit, 'data/exercise-image-progress.json')['exercises']
        approved = sources[commit][eid]
        if approved.get('user_review') != 'approved' or approved.get('accepted_sha256') != sha:
            raise RuntimeError('Frozen plan is not accepted at its source commit: ' + eid)
        if (item['destination_path'] != eid + '/' + sha + '.png'
                or path_of(item['source_png']) != item['source_png']
                or item['bucket'] != legacy.source.BUCKET):
            raise RuntimeError('Frozen plan source/destination differs')
        expected_stage = STAGING/commit/item['source_png']
        if item['staged_source_png'] != str(expected_stage) or item['staging_root'] != str(STAGING/commit):
            raise RuntimeError('Staging path outside cloud import scope')
        check = item['byte_verification']
        if (not check['ready_for_upload_bytes'] or check['sha256'] != sha
                or check['bytes'] > legacy.source.SIZE_LIMIT
                or item['proposed_image_patch'] != {
                    'image_path': item['destination_path'], 'image_sha256': sha,
                    'image_width': check['width'], 'image_height': check['height'], 'image_origin': 'generated'}):
            raise RuntimeError('Frozen PNG verification/patch differs')
        # Restore only the exact accepted blob if a new cloud runtime lacks staging.
        if not expected_stage.exists():
            raw = git('show', commit + ':' + item['source_png'])
            if legacy.source.digest(raw) != sha:
                raise RuntimeError('Pinned source bytes differ')
            expected_stage.parent.mkdir(parents=True, exist_ok=True)
            expected_stage.write_bytes(raw)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--apply', action='store_true')
    parser.add_argument('--run-id')
    args = parser.parse_args()
    if args.run_id is None:
        refs = git('for-each-ref', '--format=%(refname:short) %(objectname)', 'refs/remotes/origin')
        args.run_id = ('continuation-' + datetime.now(timezone.utc).strftime('%Y-%m-%d')
                       + '-' + legacy.source.digest(refs)[:12])
    if not re.fullmatch('[a-z0-9-]+', args.run_id):
        raise RuntimeError('Invalid run ID')
    output = ROOT/'integration/supabase/uploads'/args.run_id
    originals = {r['id']: r for r in legacy.source.read_json(ROOT/'data/exercises/catalog.json')['exercises']}
    if legacy.source.digest((ROOT/'data/exercises/catalog.json').read_bytes()) != legacy.source.CATALOG_SHA256:
        raise RuntimeError('Original catalog changed')
    known = known_transfers()
    api = ImagesOnlyApi(False, [])
    plan = legacy.source.read_json(output/'plan.json') if (output/'plan.json').exists() else prepare(output, originals, known, api)
    validate_plan(plan, originals)
    print(json.dumps({'prepared_images': len(plan['images']), 'prior_reverified': plan['already_transferred'],
        'pending_skipped': plan['pending_skipped'], 'blocked': plan['blocked']}, ensure_ascii=False), flush=True)
    if not args.apply or not plan['images']:
        return 0
    # Even on resume, reconcile catalog before enabling any mutation.
    legacy.verify_catalog(api.catalog(), originals)
    api = ImagesOnlyApi(True, [v['destination_path'] for v in plan['images']])
    batches = []
    for start in range(0, len(plan['images']), 10):
        items = plan['images'][start:start+10]
        path = output/('batch-%03d.json' % (start//10 + 1))
        batch = legacy.source.read_json(path) if path.exists() else {
            'project_ref': plan['project_ref'], 'batch_number': start//10 + 1,
            'expected_ids': [v['exercise_id'] for v in items], 'entries': {}}
        if batch['expected_ids'] != [v['exercise_id'] for v in items]:
            raise RuntimeError('Checkpoint batch scope changed')
        batches.append(batch)
        for item in items:
            eid = item['exercise_id']
            previous_root = legacy.source.ROOT
            try:
                legacy.source.ROOT = Path(item['staging_root'])
                result = legacy.transfer_one(api, item, originals[eid], batch['entries'].get(eid),
                                             item['expected_previous_image'])
                result.update(source_branch=item['source_branch'], source_commit=item['source_commit'],
                              staged_source_png=item['staged_source_png'])
                batch['entries'][eid] = result
                batch['status'] = 'in_progress'
                legacy.save(path, batch)
            except Exception as error:
                batch['status'] = 'stopped'
                batch['last_error'] = {'exercise_id': eid, 'message': str(error).replace(api.key, '[REDACTED]'),
                                       'at_utc': legacy.now()}
                legacy.save(path, batch)
                checkpoint_handoff(output, plan, batches)
                raise
            finally:
                legacy.source.ROOT = previous_root
        batch['status'] = 'complete'
        batch.pop('last_error', None)
        batch['completed_at_utc'] = legacy.now()
        legacy.save(path, batch)
        summary = checkpoint_handoff(output, plan, batches)
        print('Batch', batch['batch_number'], 'complete:', len(items), 'images', flush=True)
    current = api.catalog()
    summary['catalog_verification'] = legacy.verify_catalog(current, originals)
    updated_ids = {item['exercise_id'] for item in plan['images']}
    for previous in plan['prior_transfers_reverified']:
        if previous['current_link_matches'] and previous['exercise_id'] not in updated_ids:
            if not legacy.image_matches(current[previous['exercise_id']], previous['database_image_fields']):
                raise RuntimeError('Previous image link changed: ' + previous['exercise_id'])
    summary['all_previous_current_image_links_preserved'] = True
    for item in plan['images']:
        if not legacy.image_matches(api.row(item['exercise_id']), item['proposed_image_patch']):
            raise RuntimeError('Final image link differs: ' + item['exercise_id'])
        legacy.verify_public(*api.public(item['destination_path']), item['accepted_sha256'])
    summary['all_new_public_sha256_and_database_links_verified'] = True
    summary['completed_at_utc'] = legacy.now()
    legacy.save(output/'summary.json', summary)
    print(json.dumps(summary, ensure_ascii=False), flush=True)
    return 0


if __name__ == '__main__':
    try:
        sys.exit(main())
    except Exception as error:
        import os
        message = str(error)
        key = os.environ.get('exerciseuploader')
        if key:
            message = message.replace(key, '[REDACTED]')
        print(message, file=sys.stderr)
        sys.exit(1)
