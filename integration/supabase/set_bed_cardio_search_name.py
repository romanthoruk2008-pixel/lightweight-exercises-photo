#!/usr/bin/env python3
"""Apply the user-approved visible search-name workaround to Bed Cardio only."""
import argparse
import json
import os
import sys
import urllib.parse

import import_bed_cardio as bed

NAME = 'Bed Cardio · sex'
OUTPUT = bed.ROOT/'integration/supabase/uploads/bed-cardio-search-name-2026-10-15'


class NameApi(bed.BedCardioApi):
    def request(self, method, path, payload=None, headers=None, authenticated=True):
        if method != 'GET' and not (method == 'PATCH' and payload == {'name': NAME}):
            raise RuntimeError('Only the exact authorized Bed Cardio name may be written')
        return super().request(method, path, payload, headers, authenticated)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--apply', action='store_true')
    args = parser.parse_args()
    api = NameApi(False, [])
    current = bed.optional_row(api)
    if current is None or current['name'] not in ('Bed Cardio', NAME):
        raise RuntimeError('Bed Cardio missing or current name differs; reread before updating')
    before = api.catalog()
    if before.get(bed.EID) != current:
        raise RuntimeError('Bed Cardio changed during preflight')
    manifest = {'exercise_id': bed.EID, 'project_ref': bed.legacy.source.HOST.split('.')[0],
        'before_name': current['name'], 'target_name': NAME, 'changed_column': 'name',
        'localized_names_and_descriptions_to_preserve': True,
        'actual_app_search_verified': False, 'prepared_at_utc': bed.legacy.now(), 'status': 'prepared'}
    OUTPUT.mkdir(parents=True, exist_ok=True)
    bed.legacy.save(OUTPUT/'manifest.json', manifest)
    if not args.apply:
        print(json.dumps(manifest, ensure_ascii=False))
        return
    if bed.optional_row(api) != current:
        raise RuntimeError('Bed Cardio changed after preflight; no update issued')
    api = NameApi(True, [])
    if current['name'] != NAME:
        query = bed.legacy.patch_filter(current)+'&'+urllib.parse.urlencode({'name': 'eq.'+current['name']})
        raw, status, _ = api.require('PATCH', query, {'name': NAME}, {'Prefer': 'return=representation'})
        updated = json.loads(raw)
        if len(updated) != 1 or updated[0].get('id') != bed.EID or updated[0].get('name') != NAME:
            raise RuntimeError('Concurrent Bed Cardio name conflict; no repeated write')
        manifest.update(database_action='name_updated', write_http_status=status)
    else:
        manifest['database_action'] = 'existing_name_identical_skipped'
    after = api.catalog()
    final = after[bed.EID]
    assert final['name'] == NAME and 'секс' not in final['name']
    assert {k: v for k, v in current.items() if k not in ('name', 'updated_at')} == {
        k: v for k, v in final.items() if k not in ('name', 'updated_at')}
    assert {k: v for k, v in before.items() if k != bed.EID} == {
        k: v for k, v in after.items() if k != bed.EID}
    probes = []
    for value in ('sex', 'SEX', 'Bed Cardio'):
        query = {'id': 'eq.'+bed.EID, 'select': 'id,name', 'name': 'ilike.*'+value+'*'}
        raw, _, _ = api.require('GET', '/rest/v1/catalog_exercise?'+urllib.parse.urlencode(query))
        rows = json.loads(raw)
        assert rows == [{'id': bed.EID, 'name': NAME}]
        probes.append({'name_ilike_query': value, 'matched_ids': [bed.EID]})
    manifest.update(status='complete', final_name=final['name'], direct_rest_name_search_probes=probes,
        localized_names_and_descriptions_unchanged=True, all_content_including_alias_metadata_unchanged=True,
        image_fields_unchanged=True, other_records_unchanged=len(after)-1,
        other_records_sha256=bed.digest({k: v for k, v in after.items() if k != bed.EID}),
        actual_app_search_verified=False,
        app_behavior_limit='Direct Supabase name ilike filters verified; app query/cache and UI are unavailable.',
        completed_at_utc=bed.legacy.now())
    bed.legacy.save(OUTPUT/'manifest.json', manifest)
    print(json.dumps({'name': NAME, 'direct_supabase_name_search_verified': True,
                      'other_records_unchanged': len(after)-1, 'actual_app_search_verified': False}, ensure_ascii=False))


if __name__ == '__main__':
    try:
        main()
    except Exception as error:
        key = os.environ.get('exerciseuploader')
        print(str(error).replace(key, '[REDACTED]') if key else str(error), file=sys.stderr)
        sys.exit(1)
