#!/usr/bin/env python3
"""Read-only checks for the restored one-exercise addition; no import or images."""
import ast
import collections
import copy
import hashlib
import json
import pathlib
import re
import subprocess

ROOT = pathlib.Path(__file__).resolve().parents[1]
BASE = 'e0482c2f50b71a4be17450e81f7d73c46ec15334'
ORIGINAL = 'ae10de334e4ef0c952e1a954187282b08be91adf'
IMPORTER = '19882a38fa1b80ee9ff4a9b8e203a6e47488c342'
SOURCE = 'data/exercises/bed-cardio-addition.json'
DESCRIPTION_REVISION = 'data/catalog-changes/bed-cardio-description-v2.json'
LANGUAGES = {'en', 'uk', 'es', 'it', 'tr', 'fr', 'ru', 'pl'}
NEW_FILES = {
    SOURCE, DESCRIPTION_REVISION, 'data/cards/bed-cardio.json', 'data/image-decisions/bed-cardio.json',
    'data/style-decisions/bed-cardio-original-image.json',
    'data/imports/bed-cardio/catalog-exercise.insert.json',
    'data/catalog-changes/bed-cardio.json', 'docs/bed-cardio-card.html',
    'docs/bed-cardio-handoff.md', 'docs/bed-cardio-import-message.md',
    'data/audits/bed-cardio-validation.json', 'scripts/check_bed_cardio_addition.py',
}


def git(*args):
    return subprocess.check_output(['git', *args], cwd=ROOT)


def read(path):
    return json.loads((ROOT / path).read_text())


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def check():
    doc = read(SOURCE)
    assert len(doc['exercises']) == 1
    row = doc['exercises'][0]
    assert row['id'] == 'bed-cardio'
    old = json.loads(git('show', ORIGINAL + ':data/exercises/catalog.json'))
    original = [r for r in old['exercises'] if r['id'] == row['id']]
    assert len(original) == 1
    revision = read(DESCRIPTION_REVISION)
    assert revision['exercise_id'] == row['id']
    assert revision['revision'] == 'description-v2-meme'
    assert set(revision['descriptions']) == LANGUAGES
    assert set(revision['changed_fields']) == {f'content.{lang}.description' for lang in LANGUAGES}
    assert doc['source']['description_revision_path'] == DESCRIPTION_REVISION
    prior_raw = git('show', revision['previous_commit'] + ':' + SOURCE)
    assert sha(prior_raw) == revision['previous_source_sha256']
    assert json.loads(prior_raw)['exercises'] == original
    description_free_comparison = copy.deepcopy(row)
    for lang in LANGUAGES:
        assert row['content'][lang]['description'] == revision['descriptions'][lang]
        assert row['content'][lang]['description'] != original[0]['content'][lang]['description']
        description_free_comparison['content'][lang]['description'] = original[0]['content'][lang]['description']
    assert description_free_comparison == original[0], 'Non-description exercise fields changed'
    assert set(row['content']) == set(doc['languages']) == LANGUAGES
    for language, text in row['content'].items():
        for field in ('name', 'description', 'instructions', 'form_cues',
                      'common_mistakes', 'safety_note', 'provenance'):
            assert text.get(field), (language, field)
        assert len(text['instructions']) == 4
        assert len(text['form_cues']) == len(text['common_mistakes']) == 3
        assert text['provenance'] == 'authored'
    assert row['tracking_type'] == 'duration' and row['equipment'] == 'none'
    assert row['primary_muscle'] == 'cardio' and row['secondary_muscles'] == []
    assert not row['archived'] and row['hevy_reference_id'] is None
    assert all(value is None for value in row['source'].values())
    existing = []
    for path in ('data/exercises/catalog.json',
                 'data/exercises/supabase-additions-2026-10-13.json'):
        raw = (ROOT / path).read_bytes()
        assert raw == git('show', BASE + ':' + path)
        existing.extend(json.loads(raw)['exercises'])
    assert len(existing) == 479
    combined = existing + [row]
    counts = collections.Counter(r['id'] for r in combined)
    assert len(combined) == len(counts) == 480 and all(n == 1 for n in counts.values())
    assert sum(bool(r['archived']) for r in combined) == 3
    assert sum(len(r['content']) for r in combined) == 4484
    card = read('data/cards/bed-cardio.json')
    assert card['exercise_id'] == row['id'] and card['source_catalog_path'] == SOURCE
    assert card['source_catalog_sha256'] == sha((ROOT / SOURCE).read_bytes())
    record_sha = sha(json.dumps(row, ensure_ascii=False, sort_keys=True,
                                separators=(',', ':')).encode())
    assert card['source_catalog_record_sha256'] == record_sha
    assert card['metric_fields'] == ['duration'] and card['duration_unit'] == 'seconds'
    assert card['tracking_type'] == 'duration' and card['renderer'] == 'standard_exercise_card'
    assert not any(card[k] for k in ('show_sets', 'show_reps', 'show_weight', 'show_distance'))
    assert set(card['localized_views']) == LANGUAGES
    for lang, text in row['content'].items():
        expected = {k: v for k, v in text.items() if k not in ('name', 'provenance')}
        expected['title'] = text['name']
        assert card['localized_views'][lang] == expected
    assert card['application_implementation_status'] == 'data_contract_only_application_repository_not_available'
    preview = (ROOT / 'docs/bed-cardio-card.html').read_text()
    embedded = preview.split('<script id="exercise-data" type="application/json">', 1)[1].split('</script>', 1)[0]
    preview_data = json.loads(embedded)
    assert preview_data['exercise_id'] == row['id']
    assert preview_data['content'] == row['content']
    assert preview_data['catalog_sha256'] == card['source_catalog_sha256']
    assert set(preview_data['labels']) == LANGUAGES
    assert 'object-fit:contain' in preview.replace(' ', '')
    payload = read('data/imports/bed-cardio/catalog-exercise.insert.json')
    assert len(payload) == 1 and payload[0]['id'] == row['id']
    for k in ('id', 'name', 'equipment', 'primary_muscle', 'secondary_muscles',
              'tracking_type', 'archived', 'content'):
        assert payload[0][k] == row[k]
    image_fields = ('image_path', 'image_sha256', 'image_width', 'image_height', 'image_origin')
    assert all(payload[0][k] is None for k in image_fields)
    assert payload[0]['attribution'] is None
    assert 'replaces_ids' not in payload[0] and 'updated_at' not in payload[0]
    # Use the importer's existing eight SQL CHECK rules, never its API code.
    path = 'integration/supabase/dry_run.py'
    importer_source = git('show', IMPORTER + ':' + path).decode()
    fn = next(n for n in ast.parse(importer_source).body
              if isinstance(n, ast.FunctionDef) and n.name == 'constraint_violations')
    namespace = {'re': re}
    exec(compile(ast.Module(body=[fn], type_ignores=[]), path, 'exec'), namespace)
    # Only local effective-value validation; actual payload keeps server defaults.
    effective = {**payload[0], 'replaces_ids': []}
    assert namespace['constraint_violations'](effective) == []
    image = read('data/image-decisions/bed-cardio.json')
    assert image['exercise_id'] == row['id'] and image['status'] == 'awaiting_original_file'
    assert image['selected_visual_approved_by_user'] and not image['exact_original_bytes_bound']
    assert not image['generation_allowed'] and image['transformations_allowed'] == []
    for k in ('accepted_path', 'accepted_sha256', 'actual_mime_type', 'actual_width',
              'actual_height', 'alpha_check', 'image_origin_for_supabase'):
        assert image[k] is None
    assert not (ROOT / image['planned_repository_path']).exists()
    style = read('data/style-decisions/bed-cardio-original-image.json')
    assert style['exercise_id'] == row['id'] and style['preserve_original_people_pose_materials_highlights_aspect_ratio']
    delta = read('data/catalog-changes/bed-cardio.json')
    assert delta['source_catalog_sha256'] == card['source_catalog_sha256']
    assert delta['source_record_sha256'] == record_sha
    assert delta['import_payload_sha256'] == sha((ROOT / 'data/imports/bed-cardio/catalog-exercise.insert.json').read_bytes())
    assert delta['combined_records_in_Git_preparation'] == 480
    assert delta['database_import_status'] == 'not_performed'
    assert delta['description_revision_path'] == DESCRIPTION_REVISION
    assert delta['only_description_fields_changed_from_restored_record']
    for change in git('diff', '--name-status', BASE, '--').decode().splitlines():
        status, path = change.split('\t')
        assert status == 'A' and path in NEW_FILES, ('Existing file changed', path)
    return {
        'schema_version': 1, 'exercise_id': row['id'], 'status': 'passed',
        'source_path': SOURCE, 'source_sha256': sha((ROOT / SOURCE).read_bytes()),
        'record_sha256': record_sha, 'original_record_restored_unchanged': False,
        'description_only_revision_validated': True,
        'description_revision_path': DESCRIPTION_REVISION,
        'names_instructions_cues_mistakes_safety_and_other_fields_unchanged': True,
        'localized_names_and_full_content_languages': sorted(LANGUAGES),
        'duration_only_card_and_import_payload_match': True,
        'importer_SQL_CHECK_rules_passed': 8, 'importer_commit': IMPORTER,
        'importer_validator_path': 'integration/supabase/dry_run.py',
        'other_479_records_and_preexisting_project_files_unchanged': True,
        'combined_Git_preparation_records': 480, 'combined_active_records': 477,
        'archived': 3, 'combined_language_blocks': 4484,
        'image_status': 'awaiting_original_file', 'original_image_bytes_bound': False,
        'application_renderer_verified': False, 'generation_calls': 0,
        'Supabase_API_calls': 0, 'database_import_status': 'not_performed',
    }


if __name__ == '__main__':
    print(json.dumps(check(), ensure_ascii=False, indent=2))
