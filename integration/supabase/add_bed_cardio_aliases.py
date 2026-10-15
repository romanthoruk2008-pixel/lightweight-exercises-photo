#!/usr/bin/env python3
"""Store hidden aliases only on Bed Cardio; does not implement app search."""
import argparse
import copy
import json
import os
import sys
import urllib.parse

import import_bed_cardio as bed

ALIASES = ('sex', 'секс')
OUTPUT = bed.ROOT/'integration/supabase/uploads/bed-cardio-aliases-2026-10-15'


class AliasApi(bed.BedCardioApi):
    def request(self, method, path, payload=None, headers=None, authenticated=True):
        if method != 'GET' and not (method == 'PATCH' and isinstance(payload, dict)
                                     and set(payload) == {'content'}):
            raise RuntimeError('Only Bed Cardio content alias metadata may be patched')
        return super().request(method, path, payload, headers, authenticated)


def with_aliases(content):
    if set(content) != set(bed.LANGUAGES):
        raise RuntimeError('Unexpected Bed Cardio language set')
    result = copy.deepcopy(content)
    for lang, block in result.items():
        existing = block.get('search_aliases', [])
        if not isinstance(existing, list) or not all(isinstance(v, str) for v in existing):
            raise RuntimeError('Unexpected existing alias metadata: '+lang)
        block['search_aliases'] = existing + [v for v in ALIASES if v not in existing]
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--apply', action='store_true')
    args = parser.parse_args()
    api = AliasApi(False, [])
    initial = bed.optional_row(api)
    if initial is None:
        raise RuntimeError('Bed Cardio is missing; this script cannot create exercises')
    before = api.catalog()
    if before.get(bed.EID) != initial:
        raise RuntimeError('Bed Cardio changed during initial reads')
    content = with_aliases(initial['content'])
    OUTPUT.mkdir(parents=True, exist_ok=True)
    manifest = {'exercise_id': bed.EID, 'project_ref': bed.legacy.source.HOST.split('.')[0],
        'aliases': list(ALIASES), 'json_path': 'content.<language>.search_aliases',
        'languages': list(bed.LANGUAGES), 'before_content_sha256': bed.digest(initial['content']),
        'status': 'prepared', 'app_search_implemented': False, 'actual_app_search_verified': False,
        'scope': 'Store alias metadata in Supabase only; existing app search behavior is unknown.',
        'prepared_at_utc': bed.legacy.now()}
    bed.legacy.save(OUTPUT/'manifest.json', manifest)
    if not args.apply:
        print(json.dumps({'mode': 'read-only', 'aliases_to_store': list(ALIASES),
                          'languages': list(bed.LANGUAGES), 'app_search_implemented': False}))
        return
    if bed.optional_row(api) != initial:
        raise RuntimeError('Bed Cardio changed after preflight; no update issued')
    api = AliasApi(True, [])
    if content != initial['content']:
        raw, status, _ = api.require('PATCH', bed.legacy.patch_filter(initial), {'content': content},
                                     {'Prefer': 'return=representation'})
        saved = json.loads(raw)
        if len(saved) != 1 or saved[0].get('id') != bed.EID:
            current = bed.optional_row(api)
            if saved or current is None or current.get('content') != content:
                raise RuntimeError('Concurrent alias update conflict; no repeated write')
        manifest['write_http_status'] = status
        manifest['database_action'] = 'alias_metadata_updated'
    else:
        manifest['database_action'] = 'existing_aliases_identical_skipped'
    after = api.catalog()
    final = after[bed.EID]
    assert final['content'] == content
    for lang in bed.LANGUAGES:
        without_aliases = {k: v for k, v in final['content'][lang].items() if k != 'search_aliases'}
        expected = {k: v for k, v in initial['content'][lang].items() if k != 'search_aliases'}
        assert without_aliases == expected
    assert {k: v for k, v in final.items() if k not in ('content', 'updated_at')} == {
        k: v for k, v in initial.items() if k not in ('content', 'updated_at')}
    assert {k: v for k, v in before.items() if k != bed.EID} == {
        k: v for k, v in after.items() if k != bed.EID}
    probes = []
    for language in bed.LANGUAGES:
        for value in ('sex', 'SEX', '  Sex  ', 'секс', 'СЕКС', ' sexy ', 'asexual', 'unisex'):
            normalized = value.strip().casefold()
            query = {'id': 'eq.'+bed.EID, 'select': 'id', 'archived': 'eq.false',
                     'content->'+language+'->search_aliases': 'cs.'+json.dumps([normalized], ensure_ascii=False)}
            raw, _, _ = api.require('GET', '/rest/v1/catalog_exercise?'+urllib.parse.urlencode(query))
            ids = [row['id'] for row in json.loads(raw)]
            assert ids == ([bed.EID] if normalized in ALIASES else [])
            probes.append({'language': language, 'query': value, 'matched_ids': ids})
    query = {'id': 'eq.'+bed.EID, 'select': 'id', 'primary_muscle': 'eq.biceps',
             'content->en->search_aliases': 'cs.["sex"]'}
    raw, _, _ = api.require('GET', '/rest/v1/catalog_exercise?'+urllib.parse.urlencode(query))
    assert json.loads(raw) == []
    manifest.update(status='complete', stored_aliases_verified=True,
        display_names_descriptions_and_other_content_values_unchanged=True,
        all_noncontent_fields_except_updated_at_unchanged=True, other_479_records_unchanged=True,
        language_blocks=8, aliases_by_language={lang: final['content'][lang]['search_aliases'] for lang in bed.LANGUAGES},
        direct_rest_probes=probes, existing_filter_excludes_bed_cardio=True,
        normalization_location='verification Python client (strip/casefold), not Supabase or the app',
        app_search_implemented=False, actual_app_search_verified=False,
        completed_at_utc=bed.legacy.now())
    bed.legacy.save(OUTPUT/'manifest.json', manifest)
    print(json.dumps({'aliases_stored': list(ALIASES), 'languages': 8, 'other_records_unchanged': 479,
                      'direct_rest_probes_passed': len(probes), 'app_search_implemented': False}, ensure_ascii=False))


if __name__ == '__main__':
    try:
        main()
    except Exception as error:
        key = os.environ.get('exerciseuploader')
        print(str(error).replace(key, '[REDACTED]') if key else str(error), file=sys.stderr)
        sys.exit(1)
