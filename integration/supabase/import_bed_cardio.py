#!/usr/bin/env python3
"""Import only bed-cardio; default is read-only preflight, --apply enables it."""
import argparse
import json
import os
from pathlib import Path
import sys
import urllib.parse

import continue_images as integration

legacy = integration.legacy
ROOT = integration.ROOT
EID = 'bed-cardio'
SOURCE_COMMIT = 'd8e01b672a7125790033b2f7a600dd01c3f9427c'
LANGUAGES = ('en', 'uk', 'es', 'it', 'tr', 'fr', 'ru', 'pl')
OUTPUT = ROOT/'integration/supabase/uploads/bed-cardio-2026-10-15'
TEXT_FIELDS = tuple(k for k in legacy.source.DIRECT_FIELDS if k != 'id')
INSERT_FIELDS = {'id', *TEXT_FIELDS, 'attribution', *legacy.IMAGE_FIELDS}


def digest(value):
    return legacy.source.canonical_digest(value)


def load_source():
    paths = ['data/exercises/bed-cardio-addition.json',
             'data/imports/bed-cardio/catalog-exercise.insert.json',
             'data/cards/bed-cardio.json', 'data/catalog-changes/bed-cardio.json',
             'data/catalog-changes/bed-cardio-description-v2.json']
    raw = {p: integration.git('show', SOURCE_COMMIT+':'+p) for p in paths}
    docs = {p: json.loads(v) for p, v in raw.items()}
    source, inserts, card, metadata, revision = [docs[p] for p in paths]
    assert legacy.source.digest(raw[paths[0]]) == metadata['source_catalog_sha256']
    assert legacy.source.digest(raw[paths[1]]) == metadata['import_payload_sha256']
    assert len(source['exercises']) == len(inserts) == 1
    original, payload = source['exercises'][0], inserts[0]
    assert original['id'] == payload['id'] == card['exercise_id'] == metadata['exercise_id'] == EID
    assert digest(original) == metadata['source_record_sha256'] == card['source_catalog_record_sha256']
    assert card['source_catalog_sha256'] == metadata['source_catalog_sha256']
    assert original['content'] == payload['content']
    assert set(payload) == INSERT_FIELDS
    assert set(payload['content']) == set(LANGUAGES)
    assert payload['tracking_type'] == 'duration' and payload['equipment'] == 'none'
    assert payload['primary_muscle'] == 'cardio' and payload['secondary_muscles'] == []
    assert payload['name'] == 'Bed Cardio' and payload['archived'] is False
    assert all(payload[k] is None for k in legacy.IMAGE_FIELDS)
    assert revision['revision'] == 'description-v2-meme'
    for language in LANGUAGES:
        block = payload['content'][language]
        assert block['description'] == revision['descriptions'][language]
        assert card['localized_views'][language] == {
            'title': block['name'], **{k: block[k] for k in
                ('description', 'instructions', 'form_cues', 'common_mistakes', 'safety_note')}}
        assert all(block[k] for k in ('name', 'description', 'instructions', 'form_cues',
                                     'common_mistakes', 'safety_note', 'provenance'))
    assert not legacy.source.constraint_violations({**payload, 'replaces_ids': []})
    return payload, {'commit': SOURCE_COMMIT, 'source_record_sha256': digest(original),
        'metadata_hashes_verified': True, 'revision': revision['revision'],
        'documents': [{'path': p, 'sha256': legacy.source.digest(raw[p])} for p in paths]}


class BedCardioApi(legacy.Api):
    def request(self, method, path, payload=None, headers=None, authenticated=True):
        base = path.split('?', 1)[0]
        if method == 'POST' and base == '/rest/v1/catalog_exercise':
            if ('?' in path or not isinstance(payload, list) or len(payload) != 1
                    or not isinstance(payload[0], dict) or payload[0].get('id') != EID
                    or not set(payload[0]) <= INSERT_FIELDS):
                raise RuntimeError('Only a singleton bed-cardio INSERT is authorized')
        elif method == 'PATCH' and base == '/rest/v1/catalog_exercise':
            query = urllib.parse.parse_qs(urllib.parse.urlsplit(path).query)
            if (query.get('id') != ['eq.'+EID] or len(query.get('updated_at', [])) != 1
                    or not query['updated_at'][0].startswith('eq.')
                    or not isinstance(payload, dict) or not payload
                    or not set(payload) <= set(TEXT_FIELDS) | set(legacy.IMAGE_FIELDS)):
                raise RuntimeError('Only a concurrency-guarded bed-cardio PATCH is authorized')
        elif method == 'POST' and path.startswith('/storage/v1/object/'+legacy.source.BUCKET+'/'):
            destination = path.removeprefix('/storage/v1/object/'+legacy.source.BUCKET+'/')
            if not destination.startswith(EID+'/') or destination not in self.paths:
                raise RuntimeError('Storage write outside the exact bed-cardio file')
            if (headers or {}).get('x-upsert') != 'false':
                raise RuntimeError('Storage overwrites are prohibited')
        elif method != 'GET':
            raise RuntimeError('Write outside bed-cardio scope')
        return super().request(method, path, payload, headers, authenticated)


def optional_row(api):
    query = urllib.parse.urlencode({'id': 'eq.'+EID, 'select': '*'})
    raw, _, _ = api.require('GET', '/rest/v1/catalog_exercise?'+query)
    rows = json.loads(raw)
    if len(rows) > 1 or any(r.get('id') != EID for r in rows):
        raise RuntimeError('Exact bed-cardio read returned an unexpected ID set')
    return rows[0] if rows else None


def find_image():
    found, evidence = [], []
    refs = integration.git('for-each-ref', '--format=%(refname:short)', 'refs/remotes/origin').decode().splitlines()
    for ref in refs:
        if ref != 'origin/work' and not (ref.startswith('origin/agent-')
                                         and ref != 'origin/agent-04-supabase-integration'):
            continue
        commit = integration.git('rev-parse', ref).decode().strip()
        files = set(integration.git('ls-tree', '-r', '--name-only', commit).decode().splitlines())
        for path in sorted(files):
            if not (path.startswith('data/manifests/bed-cardio/') and path.endswith('.json')):
                continue
            raw = integration.git('show', commit+':'+path)
            doc = json.loads(raw)
            if (doc.get('exercise_id') != EID or doc.get('image_origin') != 'generated'
                    or not isinstance(doc.get('generation_calls'), int) or doc['generation_calls'] < 1):
                continue
            png = integration.path_of(doc.get('accepted_path') or doc.get('git_result_path'))
            sha = doc.get('accepted_sha256') or doc.get('result_sha256')
            proof = {'branch': ref.removeprefix('origin/'), 'commit': commit, 'manifest': path,
                'manifest_sha256': legacy.source.digest(raw), 'source_png': png, 'sha256': sha,
                'user_review': doc.get('user_review'), 'generation_calls': doc['generation_calls'],
                'canvas_adjustment_performed_by_source_task': doc.get('canvas_adjustment'),
                'review_history': doc.get('review_history', []), 'file_available': png in files}
            evidence.append(proof)
            if not png or not isinstance(sha, str) or not integration.re.fullmatch('[0-9a-f]{64}', sha):
                continue
            if doc.get('result_sha256') != sha:
                raise RuntimeError('Generator final and selected Bed Cardio hashes conflict')
            if doc.get('user_review') == 'approved':
                history = doc.get('review_history', [])
                if not history or history[-1].get('accepted_sha256') != sha:
                    raise RuntimeError('Bed Cardio approval does not bind the final hash')
            if png in files:
                found.append(proof)
    if len({v['sha256'] for v in found}) > 1:
        raise RuntimeError('Multiple Bed Cardio image versions; no version chosen automatically')
    if not found:
        return None, evidence
    chosen = found[0]
    raw = integration.git('show', chosen['commit']+':'+chosen['source_png'])
    if legacy.source.digest(raw) != chosen['sha256']:
        raise RuntimeError('Bed Cardio PNG differs from generation manifest')
    stage = Path('/workspace/supabase-image-staging')/chosen['commit']
    staged = stage/chosen['source_png']
    staged.parent.mkdir(parents=True, exist_ok=True)
    staged.write_bytes(raw)
    previous = legacy.source.ROOT
    try:
        legacy.source.ROOT = stage
        check = legacy.source.verify_png(chosen['source_png'], chosen['sha256'])
    finally:
        legacy.source.ROOT = previous
    if not check['ready_for_upload_bytes']:
        raise RuntimeError('Bed Cardio generated PNG fails technical checks')
    destination = EID+'/'+chosen['sha256']+'.png'
    patch = {'image_path': destination, 'image_sha256': chosen['sha256'],
             'image_width': check['width'], 'image_height': check['height'], 'image_origin': 'generated'}
    return {'exercise_id': EID, 'source_png': chosen['source_png'], 'source_commit': chosen['commit'],
            'accepted_sha256': chosen['sha256'], 'destination_path': destination,
            'public_url': legacy.source.BASE+'/storage/v1/object/public/'+legacy.source.BUCKET+'/'+destination,
            'staging_root': str(stage), 'staged_source_png': str(staged), 'byte_verification': check,
            'proposed_image_patch': patch, 'generation_evidence': chosen}, evidence


def ensure_text(api, target, initial):
    current = optional_row(api)
    if current != initial:
        raise RuntimeError('Bed Cardio changed since preflight; reread before applying')
    if current is None:
        raw, status, _ = api.request('POST', '/rest/v1/catalog_exercise', [target],
                                    {'Prefer': 'missing=default,return=representation'})
        if not 200 <= status < 300:
            if status != 409:
                raise RuntimeError('Singleton Bed Cardio INSERT failed: HTTP '+str(status))
            current = optional_row(api)
            if current is None or not legacy.source_matches(current, target):
                raise RuntimeError('Concurrent Bed Cardio insertion conflict; no overwrite')
            return 'concurrent_identical_insert_verified'
        saved = json.loads(raw)
        if len(saved) != 1 or saved[0].get('id') != EID:
            raise RuntimeError('Unexpected singleton INSERT response')
        return 'created'
    changes = {k: target[k] for k in TEXT_FIELDS if current.get(k) != target[k]}
    if not changes:
        return 'existing_text_identical_skipped'
    if not current.get('updated_at'):
        raise RuntimeError('Cannot guard Bed Cardio text update without updated_at')
    raw, _, _ = api.require('PATCH', legacy.patch_filter(current), changes,
                            {'Prefer': 'return=representation'})
    saved = json.loads(raw)
    if len(saved) != 1:
        reread = optional_row(api)
        if saved or reread is None or not legacy.source_matches(reread, target):
            raise RuntimeError('Concurrent Bed Cardio text conflict; no repeated PATCH')
        return 'concurrent_identical_text_verified'
    return 'updated'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--apply', action='store_true')
    args = parser.parse_args()
    target, source = load_source()
    api = BedCardioApi(False, [])
    initial = optional_row(api)  # The first Supabase read is the exact requested ID.
    before = api.catalog()
    if before.get(EID) != initial:
        raise RuntimeError('Bed Cardio changed during initial reads')
    other_hashes = {eid: digest(row) for eid, row in before.items() if eid != EID}
    image, evidence = find_image()
    bucket_raw, _, _ = api.require('GET', '/storage/v1/bucket')
    bucket = next(b for b in json.loads(bucket_raw) if b['id'] == legacy.source.BUCKET)
    if (bucket['public'] is not True or bucket['file_size_limit'] != legacy.source.SIZE_LIMIT
            or bucket['allowed_mime_types'] != ['image/png']):
        raise RuntimeError('Storage bucket constraints changed')
    plan = {'exercise_id': EID, 'project_ref': legacy.source.HOST.split('.')[0],
            'text_source': source, 'target_insert_record': target, 'image': image,
            'image_source_evidence': evidence, 'initial_row': initial,
            'other_record_hashes_before': other_hashes, 'planned_at_utc': legacy.now(),
            'authorization': 'User explicitly authorized only Bed Cardio texts and the existing generated illustration; source review status is preserved.',
            'transforms_this_task': [], 'new_generation_calls': 0}
    OUTPUT.mkdir(parents=True, exist_ok=True)
    legacy.save(OUTPUT/'preflight.json', plan)
    print(json.dumps({'mode': 'apply' if args.apply else 'read-only', 'exercise_id': EID,
        'row_exists': initial is not None, 'languages': list(LANGUAGES), 'image_found': image is not None,
        'image_sha256': image['accepted_sha256'] if image else None}, ensure_ascii=False), flush=True)
    if not args.apply:
        return
    result = {'exercise_id': EID, 'text_source': source, 'languages': list(LANGUAGES),
              'generation_review_status_unchanged': True, 'new_generation_calls': 0,
              'transforms_this_task': [], 'started_at_utc': legacy.now()}
    legacy.save(OUTPUT/'manifest.json', result)
    try:
        api = BedCardioApi(True, [image['destination_path']] if image else [])
        result['text_action'] = ensure_text(api, target, initial)
        legacy.save(OUTPUT/'manifest.json', result)
        if image:
            current = optional_row(api)
            patch = image['proposed_image_patch']
            if (any(current.get(k) is not None for k in legacy.IMAGE_FIELDS)
                    and not legacy.image_matches(current, patch)):
                raise RuntimeError('Existing Bed Cardio image differs; selection must be clarified before replacement')
            previous = (legacy.source.read_json(OUTPUT/'image-transfer.json')
                        if (OUTPUT/'image-transfer.json').exists() else None)
            old_root = legacy.source.ROOT
            try:
                legacy.source.ROOT = Path(image['staging_root'])
                transfer = legacy.transfer_one(api, image, target, previous)
            finally:
                legacy.source.ROOT = old_root
            legacy.save(OUTPUT/'image-transfer.json', transfer)
            result['image_action'] = transfer['storage_action']
            result['image_linked'] = True
            result['file_verification'] = transfer['file_verification']
        else:
            result['image_linked'] = False
            result['image_blocker'] = 'Generated standalone Bed Cardio PNG is unavailable in accessible source branches.'
        final = optional_row(api)
        if final is None or not legacy.source_matches(final, target):
            raise RuntimeError('Bed Cardio text readback differs from the exact pinned payload')
        if image and not legacy.image_matches(final, image['proposed_image_patch']):
            raise RuntimeError('Bed Cardio image fields differ on final readback')
        if initial is None and not image and any(final.get(k) is not None for k in legacy.IMAGE_FIELDS):
            raise RuntimeError('Text-only insertion has unexpected image fields')
        after = api.catalog()
        others_after = {eid: digest(row) for eid, row in after.items() if eid != EID}
        changed = sorted(eid for eid in set(other_hashes) | set(others_after)
                         if other_hashes.get(eid) != others_after.get(eid))
        if changed:
            result['other_records_changed_during_run'] = changed
            raise RuntimeError('Other catalog records changed during this run; no writes to them were issued')
        result.update(status='complete', text_readback_exact=True, source_fields_verified=list(legacy.source.DIRECT_FIELDS),
            language_blocks=8, all_8_full_content_blocks_and_localized_names_exact=True,
            other_records_count=len(other_hashes), other_records_full_values_unchanged=True,
            other_records_sha256=digest(other_hashes), final_row=final,
            final_catalog_count=len(after), completed_at_utc=legacy.now())
        legacy.save(OUTPUT/'manifest.json', result)
        print(json.dumps({'status': 'complete', 'text_action': result['text_action'],
            'language_blocks': 8, 'image_linked': result['image_linked'],
            'other_records_unchanged': len(other_hashes)}, ensure_ascii=False), flush=True)
    except Exception as error:
        result.update(status='stopped', error=str(error).replace(api.key, '[REDACTED]'), stopped_at_utc=legacy.now())
        legacy.save(OUTPUT/'manifest.json', result)
        raise


if __name__ == '__main__':
    try:
        main()
    except Exception as error:
        key = os.environ.get('exerciseuploader')
        print(str(error).replace(key, '[REDACTED]') if key else str(error), file=sys.stderr)
        sys.exit(1)
