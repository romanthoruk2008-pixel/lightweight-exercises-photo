#!/usr/bin/env python3
"""Export the 28 requested catalog additions; Supabase access is GET-only."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import sys

import continue_images as integration

ROOT = integration.ROOT
DATA = ROOT / 'data/exercises/supabase-additions-2026-10-13.json'
MANIFEST = ROOT / 'integration/supabase/exports/2026-10-13/new-exercises-manifest.json'
EXPECTED_IDS = tuple('''archer-pullup-machine
archer-pushup
bulgarian-split-squat-body-weight
chest-to-bar-pullup-machine
crow-pose
dragon-flag-negative
explosive-pullup-machine
flexed-arm-hang
front-lever-hold-advanced-tuck
front-lever-hold-one-leg
front-lever-hold-straddle
front-lever-hold-tuck
handstand-hold-chest-to-wall
handstand-pushup-negative
hollow-body-hold
inverted-row-feet-elevated-machine
l-sit-hold-tuck
muscle-up-band-resistance-band
muscle-up-negative-machine
parallel-bar-support-hold
pike-pushup-feet-elevated
pseudo-planche-lean
pseudo-planche-pushup
shrimp-squat
single-leg-romanian-deadlift-body-weight
skin-the-cat
straight-bar-dip-machine
triceps-dip-negative-machine'''.splitlines())


class ReadOnlyApi(integration.ImagesOnlyApi):
    def request(self, method, path, payload=None, headers=None, authenticated=True):
        if method != 'GET':
            raise RuntimeError('Supabase writes are prohibited for this export')
        return super().request(method, path, payload, headers, authenticated)


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def record_digest(row):
    return digest(json.dumps(row, ensure_ascii=False, sort_keys=True,
                             separators=(',', ':')).encode())


def validate(rows, baseline):
    if len(EXPECTED_IDS) != 28 or len(set(EXPECTED_IDS)) != 28:
        raise RuntimeError('Export ID scope is invalid')
    if len(baseline['exercises']) != 451:
        raise RuntimeError('Historical baseline count changed')
    baseline_ids = {r['id'] for r in baseline['exercises']}
    if baseline_ids & set(EXPECTED_IDS):
        raise RuntimeError('Export scope overlaps historical catalog')
    if not baseline_ids <= set(rows):
        raise RuntimeError('Historical catalog IDs are missing in Supabase')
    if not set(EXPECTED_IDS) <= set(rows):
        raise RuntimeError('Requested new IDs are missing in Supabase')
    selected = [rows[eid] for eid in EXPECTED_IDS]
    for row in selected:
        if not re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*', row['id']):
            raise RuntimeError('Invalid exact source ID')
        if row.get('archived') is not False:
            raise RuntimeError('Requested addition is not active: ' + row['id'])
        if not isinstance(row.get('name'), str) or not row['name'].strip():
            raise RuntimeError('Missing source name: ' + row['id'])
        if not isinstance(row.get('secondary_muscles'), list):
            raise RuntimeError('Invalid muscles array: ' + row['id'])
        if not isinstance(row.get('content'), dict) or not row['content']:
            raise RuntimeError('Missing language blocks: ' + row['id'])
        en = row['content'].get('en')
        if not isinstance(en, dict):
            raise RuntimeError('Missing English block: ' + row['id'])
        for field in ('description', 'safety_note'):
            if not isinstance(en.get(field), str) or not en[field].strip():
                raise RuntimeError('Missing English ' + field + ': ' + row['id'])
        for field in ('instructions', 'form_cues', 'common_mistakes'):
            values = en.get(field)
            if not isinstance(values, list) or not values or not all(
                    isinstance(v, str) and v.strip() for v in values):
                raise RuntimeError('Invalid English ' + field + ': ' + row['id'])
    return selected


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument('--write', action='store_true', help='Save new cloud workspace files only')
    mode.add_argument('--check', action='store_true', help='Compare saved records against a fresh GET')
    args = parser.parse_args()
    baseline_raw = (ROOT / 'data/exercises/catalog.json').read_bytes()
    if digest(baseline_raw) != integration.legacy.source.CATALOG_SHA256:
        raise RuntimeError('Historical catalog bytes changed')
    baseline = json.loads(baseline_raw)
    rows = ReadOnlyApi(False, []).catalog()
    selected = validate(rows, baseline)
    language_blocks = sum(len(r['content']) for r in selected)
    languages = sorted({language for r in selected for language in r['content']})
    if args.write:
        if DATA.exists() or MANIFEST.exists():
            raise RuntimeError('Export already exists; use --check without overwriting it')
        checked_at = integration.legacy.now()
        payload = {
            'schema_version': baseline['schema_version'],
            'source': {
                'type': 'supabase_catalog_additions',
                'project_ref': integration.legacy.source.HOST.split('.')[0],
                'table': 'public.catalog_exercise',
                'retrieved_at_utc': checked_at,
                'method': 'HTTPS GET via configured proxy; bound apikey',
                'historical_catalog_path': 'data/exercises/catalog.json',
                'historical_catalog_sha256': digest(baseline_raw),
                'scope': 'The 28 exact IDs requested by the user on 2026-10-13',
                'record_values': 'Every returned column and all content values preserved',
            },
            'languages': languages,
            'exercises': selected,
        }
        serialized = (json.dumps(payload, ensure_ascii=False, indent=2) + '\n').encode()
        # Verify round-trip equality before saving anything.
        if json.loads(serialized)['exercises'] != selected:
            raise RuntimeError('Serialization changed source values')
        manifest = {
            'schema_version': 1, 'project_ref': payload['source']['project_ref'],
            'table': payload['source']['table'], 'retrieved_at_utc': checked_at,
            'data_path': DATA.relative_to(ROOT).as_posix(), 'data_sha256': digest(serialized),
            'baseline_catalog_sha256': digest(baseline_raw),
            'baseline_records': 451, 'exported_records': len(selected),
            'exported_language_blocks': language_blocks, 'languages': languages,
            'source_columns': sorted({k for r in selected for k in r}),
            'records': [{'exercise_id': r['id'], 'source_record_sha256': record_digest(r),
                         'source_updated_at': r.get('updated_at'),
                         'language_blocks': len(r['content'])} for r in selected],
            'all_returned_columns_preserved': True, 'all_content_values_preserved': True,
            'api_mutations_enabled': False,
        }
        DATA.parent.mkdir(parents=True, exist_ok=True)
        MANIFEST.parent.mkdir(parents=True, exist_ok=True)
        DATA.write_bytes(serialized)
        integration.legacy.save(MANIFEST, manifest)
    if args.check:
        raw = DATA.read_bytes()
        payload = json.loads(raw)
        manifest = integration.legacy.source.read_json(MANIFEST)
        if payload['exercises'] != selected:
            raise RuntimeError('Saved records differ from current full Supabase records')
        if (digest(raw) != manifest['data_sha256']
                or payload['languages'] != languages
                or manifest['exported_language_blocks'] != language_blocks
                or manifest['baseline_catalog_sha256'] != digest(baseline_raw)
                or manifest['records'] != [
                    {'exercise_id': r['id'], 'source_record_sha256': record_digest(r),
                     'source_updated_at': r.get('updated_at'),
                     'language_blocks': len(r['content'])} for r in selected]):
            raise RuntimeError('Export manifest differs from verified records')
    print(json.dumps({'mode': 'write' if args.write else 'check' if args.check else 'dry-run',
                      'exported_records': len(selected), 'language_blocks': language_blocks,
                      'languages': languages, 'current_supabase_catalog_records': len(rows),
                      'exact_id_scope': True, 'english_prompt_fields_complete': True,
                      'api_mutations_enabled': False}, ensure_ascii=False))


if __name__ == '__main__':
    try:
        main()
    except Exception as error:
        key = os.environ.get('exerciseuploader')
        message = str(error).replace(key, '[REDACTED]') if key else str(error)
        print(message, file=sys.stderr)
        sys.exit(1)
