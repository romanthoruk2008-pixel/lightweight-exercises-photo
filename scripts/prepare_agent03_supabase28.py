#!/usr/bin/env python3
"""Prepare/validate exact-ID image tasks from the immutable 28-record export.

No network API mutations, image calls, catalogue edits or foreign-branch writes.
Run --prepare once, then --check. Refresh Git refs separately before either run.
"""
import argparse
import collections
import copy
import datetime
import hashlib
import json
import pathlib
import re
import subprocess
from zoneinfo import ZoneInfo

ROOT = pathlib.Path(__file__).resolve().parents[1]
BRANCH = 'agent-03-inventory-2026-10-01'
BASE = '83ee71adab8703fe286e8c161899dbf29dfe7eb1'
SOURCE_COMMIT = 'f64538a37d63f7512527ab2a57cb195645a4a354'
SOURCE_BRANCH = 'agent-04-supabase-integration'
SOURCE_PATH = 'data/exercises/supabase-additions-2026-10-13.json'
SOURCE_SHA = '907950559a5bf4be84a791deb73fcd03d502a48ec8b936296df8a3e42651bf0f'
MANIFEST_SOURCE = 'integration/supabase/exports/2026-10-13/new-exercises-manifest.json'
SOURCE_MANIFEST = 'data/source-manifests/agent-03-supabase-additions-2026-10-13.json'
SCENES = 'data/technique-decisions/agent-03-supabase28-2026-10-13-scenes.json'
ROUND = 'agent-03-supabase28-2026-10-13'
QUEUE = f'data/queues/{ROUND}.json'
REGISTRY = f'data/assignments/{ROUND}.json'
EVIDENCE = f'data/audits/{ROUND}-source-review.json'
VALIDATION = f'data/audits/{ROUND}-validation.json'
HANDOFF = f'docs/{ROUND}-handoff.md'
PUBLICATION = f'data/assignments/{ROUND}-publication.json'
REFERENCE = 'assets/exercises/biceps-curl-dumbbell.png'
REFERENCE_SHA = '52fef743ba2d7689aa81a8b995df3c6715cbb5d04c4bd688af4ca57b2d20057f'
STYLE = 'docs/exercise-image-style.md'
NEUTRAL = 'docs/exercise-image-style-neutral-primary.md'
GROUPS = {
    'agent-03-others-044': [
        'archer-pushup', 'bulgarian-split-squat-body-weight', 'crow-pose',
        'hollow-body-hold', 'pseudo-planche-lean', 'pseudo-planche-pushup',
        'shrimp-squat', 'single-leg-romanian-deadlift-body-weight',
        'pike-pushup-feet-elevated', 'handstand-hold-chest-to-wall'],
    'agent-03-others-045': [
        'dragon-flag-negative', 'handstand-pushup-negative', 'l-sit-hold-tuck',
        'parallel-bar-support-hold', 'flexed-arm-hang', 'front-lever-hold-tuck',
        'front-lever-hold-advanced-tuck', 'front-lever-hold-one-leg',
        'front-lever-hold-straddle', 'skin-the-cat'],
    'agent-03-others-046': [
        'archer-pullup-machine', 'chest-to-bar-pullup-machine',
        'explosive-pullup-machine', 'inverted-row-feet-elevated-machine',
        'muscle-up-band-resistance-band', 'muscle-up-negative-machine',
        'straight-bar-dip-machine', 'triceps-dip-negative-machine'],
}
EN_FIELDS = ('description', 'instructions', 'form_cues', 'common_mistakes',
             'safety_note', 'provenance')


def git(*args):
    return subprocess.check_output(['git', *args], cwd=ROOT)


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def canonical(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True,
                      separators=(',', ':')).encode()


def read(path):
    return json.loads((ROOT / path).read_text())


def save_new(path, value):
    target = ROOT / path
    assert not target.exists(), ('Never overwrite', path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n')


def now():
    return datetime.datetime.now(ZoneInfo('Europe/Kiev')).isoformat()


def batch_path(bid):
    return f'data/batches/{bid}.json'


def manifest_path(bid):
    return f'data/manifests/{ROUND}/{bid}.json'


def own_paths():
    return {QUEUE, REGISTRY, EVIDENCE, VALIDATION, HANDOFF, SCENES,
            SOURCE_PATH, SOURCE_MANIFEST, PUBLICATION, __file__.removeprefix(str(ROOT) + '/'),
            *[batch_path(bid) for bid in GROUPS],
            *[manifest_path(bid) for bid in GROUPS],
            *[f'docs/{ROUND}-{bid[-3:]}-message.md' for bid in GROUPS]}


def source():
    raw = (ROOT / SOURCE_PATH).read_bytes()
    assert sha(raw) == SOURCE_SHA
    assert raw == git('show', SOURCE_COMMIT + ':' + SOURCE_PATH)
    manifest_raw = (ROOT / SOURCE_MANIFEST).read_bytes()
    assert manifest_raw == git('show', SOURCE_COMMIT + ':' + MANIFEST_SOURCE)
    exported = json.loads(raw)
    manifest = json.loads(manifest_raw)
    rows = exported['exercises']
    counts = collections.Counter(r['id'] for r in rows)
    assert len(rows) == 28 and all(n == 1 for n in counts.values())
    by_id = {r['id']: r for r in rows}
    planned = [eid for ids in GROUPS.values() for eid in ids]
    assert len(planned) == len(set(planned)) == 28
    assert set(planned) == set(by_id)
    source_hashes = {r['exercise_id']: r['source_record_sha256'] for r in manifest['records']}
    assert set(source_hashes) == set(by_id)
    baseline_raw = (ROOT / 'data/exercises/catalog.json').read_bytes()
    assert baseline_raw == git('show', BASE + ':data/exercises/catalog.json')
    assert sha(baseline_raw) == manifest['baseline_catalog_sha256']
    baseline = json.loads(baseline_raw)
    assert len(baseline['exercises']) == 451
    assert sum(len(e['content']) for e in baseline['exercises']) == 4448
    assert not set(by_id) & {e['id'] for e in baseline['exercises']}
    for eid, record in by_id.items():
        assert not record['archived']
        assert record['primary_muscle'] and isinstance(record['secondary_muscles'], list)
        assert all(record['content']['en'].get(k) for k in EN_FIELDS), eid
        assert sha(canonical(record)) == source_hashes[eid], eid
        assert not any(record.get(k) for k in (
            'image_path', 'image_sha256', 'image_width', 'image_height', 'image_origin'))
    assert sha((ROOT / REFERENCE).read_bytes()) == REFERENCE_SHA
    scenes = read(SCENES)
    assert set(scenes['scenes']) == set(by_id)
    assert scenes['source_commit'] == SOURCE_COMMIT
    for eid, scene in scenes['scenes'].items():
        for k in ('phase', 'pose', 'grip', 'supports', 'equipment', 'trajectory',
                  'camera', 'illustration_choices'):
            assert scene[k], (eid, k)
    return exported, manifest, by_id, scenes['scenes']


def remote_snapshot(ids):
    """Read actual pushed files; no pixels, Supabase or web calls."""
    refs = git('for-each-ref', '--format=%(refname)', 'refs/remotes/origin').decode().splitlines()
    refs = [r for r in refs if not r.endswith('/HEAD')]
    commits = {r.removeprefix('refs/remotes/origin/'): git('rev-parse', r).decode().strip()
               for r in refs}
    collisions = []
    cache = {}
    seen_batches = {}

    def walk(value, branch, path, pointer=''):
        if isinstance(value, dict):
            eid = value.get('exercise_id', value.get('id'))
            if isinstance(eid, str) and eid in ids:
                collisions.append({'branch': branch, 'path': path,
                                   'json_pointer': pointer, 'exercise_id': eid,
                                   'status': value.get('status')})
            for key, child in value.items():
                if key not in ('content', 'source_english', 'source_record', 'prompt_payload',
                               'generation_prompt', 'prompt', 'scene'):
                    walk(child, branch, path, pointer + '/' + str(key))
        elif isinstance(value, list):
            for i, child in enumerate(value):
                walk(child, branch, path, pointer + '/' + str(i))

    for ref in refs:
        branch = ref.removeprefix('refs/remotes/origin/')
        for row in git('ls-tree', '-rz', ref).split(b'\0'):
            if not row:
                continue
            meta, encoded_path = row.split(b'\t', 1)
            path = encoded_path.decode()
            blob = meta.decode().split()[2]
            if path.endswith('.png'):
                p = pathlib.PurePosixPath(path)
                eid = p.stem if p.stem in ids else p.parent.name
                if eid in ids:
                    collisions.append({'branch': branch, 'path': path,
                                       'exercise_id': eid, 'kind': 'PNG'})
            if branch == BRANCH and path in own_paths():
                # Exactly these new preparation files are our reservation, not
                # an existing foreign assignment. Never exempt another branch.
                continue
            if path in {batch_path(b) for b in GROUPS}:
                seen_batches.setdefault(path, []).append(branch)
            execution = (path.startswith(('data/batches/', 'data/assignments/',
                                         'data/queues/', 'data/manifests/'))
                         or path == 'data/exercise-image-progress.json')
            if not path.endswith('.json') or not execution:
                continue
            if blob not in cache:
                cache[blob] = json.loads(git('cat-file', 'blob', blob))
            walk(cache[blob], branch, path)
    assert not collisions, ('Existing PNG/assignment intersection', collisions)
    assert not seen_batches, ('Batch numbers occupied', seen_batches)
    return {'checked_at_Kyiv': now(), 'commits': commits,
            'PNG_or_assignment_intersections': collisions,
            'batch_number_collisions': seen_batches,
            'scope': 'Pushed files in current remote branch tips only. Unpushed work in other cloud tasks may be inaccessible. No PNG visual/technical audit and no live Supabase query.'}


def style_for(record):
    files = [{'path': STYLE, 'sha256': sha((ROOT / STYLE).read_bytes())}]
    neutral = record['primary_muscle'] in ('full_body', 'cardio', 'other')
    if neutral:
        files.append({'path': NEUTRAL, 'sha256': sha((ROOT / NEUTRAL).read_bytes())})
    return ('v1-neutral-primary-2026-10-02' if neutral else 'v1'), files


def prompt_for(record, scene):
    eid = record['id']
    primary, secondary = record['primary_muscle'], record['secondary_muscles']
    if primary in ('full_body', 'cardio', 'other'):
        colouring = ('Primary is the non-anatomical category ' + primary +
                     ': keep the body neutral opaque silver-gray; never colour the whole body '
                     'or infer an anatomical primary. Highlight ONLY these explicitly listed '
                     'secondary regions with #F26445 at 40–50% colour intensity: ' +
                     ', '.join(secondary) + '.' if secondary else
                     'Keep the entire body neutral opaque silver-gray with no muscle highlights.')
    else:
        colouring = (f'Highlight ONLY the source primary region {primary} with #F26445 at full '
                     'colour intensity. ' +
                     ('Highlight the explicitly listed secondary regions with the same #F26445 '
                      'at 40–50% colour intensity: ' + ', '.join(secondary) + '.' if secondary else
                      'There are no secondary targets: do not add any secondary highlights.'))
    style = (
        'Create exactly ONE 1024x1024 PNG with a genuinely transparent background, ONE adult '
        'anatomical male figure and ONE movement phase. Match the supplied human reference '
        'ONLY for appearance, proportions and materials: bald athletic male anatomical mannequin, '
        'opaque silver-gray muscle surfaces with detailed realistic 3D anatomy, plain black shorts '
        'and bare feet. Keep the same head, body proportions and material finish across the library. '
        'Do not copy its pose, barbell or muscle highlights. '
        + colouring +
        ' Colour intensity is not tissue transparency: no see-through anatomy, glow, overall orange '
        'tint or unlisted coloured muscle groups. Show the necessary stable equipment and all '
        'actual body contacts; fit the full person and relevant equipment in the square without '
        'cropping or distorting anatomy. No text, labels, arrows, logos, UI, border, collage, second '
        'person, duplicate limbs, motion blur, white backdrop or baked-in checkerboard. Necessary '
        'wall/mat surfaces are physical supports only, not a filled image background. Equipment '
        'category machine/none is source metadata, not permission to invent a moving machine '
        'or omit supports explicitly required by the technique.')
    scene_text = '\n'.join(f'{k.upper()}: {scene[k]}' for k in (
        'phase', 'pose', 'grip', 'supports', 'equipment', 'trajectory', 'camera'))
    exact = json.dumps({
        'exercise_id': eid, 'name': record['name'], 'equipment': record['equipment'],
        'primary_muscle': primary, 'secondary_muscles': secondary,
        'tracking_type': record['tracking_type'], 'source_english': record['content']['en'],
    }, ensure_ascii=False, sort_keys=True, indent=2)
    return (style + '\n\nEXACT EXERCISE: ' + eid + ' — ' + record['name'] +
            '\n\nSELECTED SINGLE-PHASE SCENE:\n' + scene_text +
            '\n\nEXACT SOURCE DATA (instructions and safety govern this ID; metadata is never '
            'rendered as text):\n' + exact +
            '\n\nPreserve the source-defined technique. Do not substitute a similarly named '
            'exercise, choose a different lever variant, remove specified supports or add '
            'unlisted muscle targets. If the attached scene and exact source cannot be reconciled, '
            'stop this ID and report the concrete conflict rather than inventing a correction.')


def task(record, scene, bid, number):
    eid = record['id']
    version, style_files = style_for(record)
    prompt = prompt_for(record, scene)
    record_hash = sha(canonical(record))
    return {
        'exercise_id': eid, 'name': record['name'], 'batch_id': bid,
        'batch_item_number': number, 'status': 'ready',
        'source_record': copy.deepcopy(record), 'source_english': copy.deepcopy(record['content']['en']),
        'equipment': record['equipment'], 'primary_muscle': record['primary_muscle'],
        'secondary_muscles': copy.deepcopy(record['secondary_muscles']),
        'tracking_type': record['tracking_type'],
        'source_catalog_path': SOURCE_PATH, 'source_catalog_sha256': SOURCE_SHA,
        'source_catalog_record_sha256': record_hash,
        'source_english_sha256': sha(canonical(record['content']['en'])),
        'source_binding': {
            'branch': SOURCE_BRANCH, 'commit': SOURCE_COMMIT, 'path': SOURCE_PATH,
            'selector': f'exercises[id="{eid}"]', 'exercise_id': eid,
            'source_record_sha256': record_hash, 'source_updated_at': record['updated_at'],
            'source_url': 'https://github.com/romanthoruk2008-pixel/lightweight-exercises-photo/blob/' + SOURCE_COMMIT + '/' + SOURCE_PATH,
            'importer_manifest_path': SOURCE_MANIFEST,
            'supabase_table': 'public.catalog_exercise',
            'verification_limit': 'Immutable importer export with matching hashes; no new live Supabase read by preparer.'},
        'scene': copy.deepcopy(scene),
        'technique_resolution': {
            'status': 'resolved_for_illustration', 'decision_kind': 'exact_ID_written_source',
            'source_fields': [f'content.en.{k}' for k in EN_FIELDS],
            'scene_decisions_path': SCENES,
            'scene_selector': f'scenes["{eid}"]',
            'required_equipment_from_instructions': scene['equipment'],
            'illustration_choices': copy.deepcopy(scene['illustration_choices']),
            'external_source_urls': [], 'external_confirmation_claimed': False,
            'source_catalogue_modified': False, 'user_PNG_approval': False},
        'style_version': version, 'approved_style_files': style_files,
        'human_reference': {'path': REFERENCE, 'sha256': REFERENCE_SHA,
                            'role': 'Appearance, proportions and anatomical materials only; never pose, equipment or muscle targets.'},
        'highlight_plan': {
            'primary_muscle': record['primary_muscle'],
            'primary_intensity': None if record['primary_muscle'] in ('full_body', 'cardio', 'other') else 1.0,
            'secondary_muscles': copy.deepcopy(record['secondary_muscles']),
            'secondary_intensity': [0.4, 0.5], 'hex': '#F26445',
            'unlisted_targets_allowed': False},
        'generation_prompt': prompt, 'prompt_sha256': sha(prompt.encode()),
        'planned_png_path': f'/workspace/exercise-image-results/{ROUND}/{bid}/{eid}/attempt-1.png',
        'planned_git_png_path': f'assets/exercises/pending/{ROUND}/{bid}/{eid}/attempt-1.png',
        'manifest_path': manifest_path(bid), 'assignment_registry_path': REGISTRY,
        'execution_owner': None, 'execution_requires_user_dispatch': True,
        'attempts': 0, 'attempt_history': [], 'result_path': None, 'result_sha256': None,
        'user_review': None, 'future_user_review_policy': 'pending until explicit user approval',
        'agent_visual_review': 'not_performed', 'preparation_generation_calls': 0,
        'generation_authorized_now': False,
    }


def prepare():
    assert git('branch', '--show-current').decode().strip() == BRANCH
    exported, source_manifest, by_id, scenes = source()
    snapshot = remote_snapshot(set(by_id))
    created = [QUEUE, REGISTRY, EVIDENCE, VALIDATION, HANDOFF,
               *[batch_path(b) for b in GROUPS], *[manifest_path(b) for b in GROUPS]]
    assert all(not (ROOT / p).exists() for p in created), 'Never overwrite prior preparation'
    reviews = []
    for eid in by_id:
        record = by_id[eid]
        reviews.append({
            'exercise_id': eid, 'source_record_sha256': sha(canonical(record)),
            'all_English_fields_present': True,
            'primary_muscle': record['primary_muscle'],
            'secondary_muscles': copy.deepcopy(record['secondary_muscles']),
            'equipment_category': record['equipment'],
            'required_scene_equipment': scenes[eid]['equipment'],
            'muscle_targets_taken_from_exact_ID': True,
            'technique_taken_from_exact_ID': True,
            'no_external_backfill_required': True,
            'resolved_for_illustration': True,
            'source_note': scenes[eid].get('source_note'),
        })
    save_new(EVIDENCE, {
        'schema_version': 1, 'prepared_at_Kyiv': now(), 'source_branch': SOURCE_BRANCH,
        'source_commit': SOURCE_COMMIT, 'source_catalog_sha256': SOURCE_SHA,
        'source_export_read_at_utc': source_manifest['retrieved_at_utc'],
        'source_count': 28, 'baseline_count': 451, 'combined_count': 479,
        'new_record_languages': ['en'], 'source_only_English_not_eight_languages': True,
        'new_records_reviewed_by_exact_ID': reviews, 'remote_preflight': snapshot,
        'external_research_performed': False,
        'external_research_reason': 'All exact-ID English technique and muscle fields are complete; no missing fields to backfill. Sources are not being claimed as external clinical/biomechanical validation.',
        'generation_calls': 0, 'Supabase_API_calls_by_preparer': 0,
        'baseline_catalog_modified': False, 'shared_progress_modified': False,
    })
    assignments = []
    queue_rows = []
    for bid, ids in GROUPS.items():
        rows = [task(by_id[eid], scenes[eid], bid, i + 1) for i, eid in enumerate(ids)]
        save_new(batch_path(bid), {
            'schema_version': 1, 'batch_id': bid, 'status': 'ready',
            'task_kind': 'new_exact_ID_Supabase_export_exercises',
            'exercise_count': len(rows), 'exercise_ids': ids, 'exercises': rows,
            'source_branch': BRANCH, 'source_catalog_path': SOURCE_PATH,
            'source_catalog_sha256': SOURCE_SHA, 'source_export_commit': SOURCE_COMMIT,
            'assignment_registry_path': REGISTRY, 'manifest_path': manifest_path(bid),
            'handoff_path': HANDOFF, 'generation_calls': 0,
            'dispatch_rule': 'One user-selected worker per batch. User dispatch assigns ownership. Do not take an already claimed batch or duplicate its IDs. Existing agents tasks stay in place.',
        })
        save_new(manifest_path(bid), {
            'schema_version': 1, 'batch_id': bid, 'status': 'ready_for_user_dispatch',
            'execution_owner': None, 'source_batch_path': batch_path(bid),
            'exercise_count': len(rows), 'generation_calls': 0,
            'exercises': [{
                'exercise_id': r['exercise_id'], 'name': r['name'], 'status': 'not_started',
                'attempts': 0, 'attempt_history': [], 'batch_item_number': r['batch_item_number'],
                'prompt_sha256': r['prompt_sha256'], 'source_catalog_sha256': SOURCE_SHA,
                'source_record_sha256': r['source_catalog_record_sha256'],
                'style_version': r['style_version'], 'human_reference': r['human_reference'],
                'planned_png_path': r['planned_png_path'],
                'planned_git_png_path': r['planned_git_png_path'],
                'result_path': None, 'result_sha256': None, 'accepted_path': None,
                'accepted_sha256': None, 'technical_check': None,
                'user_review': None, 'future_user_review_policy': r['future_user_review_policy'],
                'agent_visual_review': 'not_performed', 'last_error': None,
            } for r in rows],
        })
        assignments.append({
            'batch_id': bid, 'batch_path': batch_path(bid), 'exercise_ids': ids,
            'exercise_count': len(rows), 'status': 'ready_for_user_dispatch',
            'execution_owner': None, 'manifest_path': manifest_path(bid),
            'ownership_rule': 'Only the worker explicitly selected by the user may execute this batch; record owner before first call. No automatic dispatch by the preparer.'})
        queue_rows.extend({'exercise_id': r['exercise_id'], 'name': r['name'],
                           'status': 'prompt_prepared_reserved', 'batch_id': bid,
                           'batch_path': batch_path(bid), 'prompt_sha256': r['prompt_sha256']}
                          for r in rows)
    save_new(REGISTRY, {
        'schema_version': 1, 'assignment_id': ROUND, 'source_branch': BRANCH,
        'prepared_at_Kyiv': now(), 'status': 'ready_for_user_dispatch',
        'exercise_count': 28, 'assignments': assignments,
        'existing_assignments_changed': False, 'generation_dispatched_by_preparer': False,
        'source_preflight': snapshot,
    })
    save_new(QUEUE, {
        'schema_version': 1, 'queue_id': ROUND, 'source_path': SOURCE_PATH,
        'source_sha256': SOURCE_SHA, 'total_source_records': 28,
        'prompt_prepared_count': 28, 'blocked_count': 0,
        'unprepared_remaining_count': 0, 'exercises': queue_rows,
        'assignment_registry_path': REGISTRY, 'generation_calls': 0,
    })
    lines = [
        '# 28 нових вправ — передача генераторам', '',
        'Підготовча гілка: `'+BRANCH+'`. Незмінний commit завдань див. у `'+PUBLICATION+'` після публікації.',
        '', 'Усі 28 точних ID із нового Supabase export мають повний англійський опис, instructions, cues, mistakes, safety note та м’язи. Prompts підготовлені; зображення не генерувалися. Інших перекладів у цих нових записах поки немає.',
        '', 'Історичний catalog.json 451/4448 не змінений. Доповнення з 28 ID збережене байт у байт окремо: `'+SOURCE_PATH+'`; SHA256 `'+SOURCE_SHA+'`; джерельний commit `'+SOURCE_COMMIT+'`, гілка `'+SOURCE_BRANCH+'`.',
        '', '| Пакет | Стан | Кількість | Точний файл | Manifest |', '|---|---|---:|---|---|',
    ]
    for bid, ids in GROUPS.items():
        lines.append(f'| {bid} | ready | {len(ids)} | `{batch_path(bid)}` | `{manifest_path(bid)}` |')
    lines += ['', '## Вправи та підсвітка', '',
              '| Пакет / № | exercise_id | Назва | Основні | Допоміжні |', '|---|---|---|---|---|']
    for bid, ids in GROUPS.items():
        for i, eid in enumerate(ids, 1):
            r = by_id[eid]
            lines.append(f'| {bid[-3:]} / {i} | `{eid}` | {r["name"]} | {r["primary_muscle"]} | {", ".join(r["secondary_muscles"]) or "—"} |')
    lines += [
        '', '## Стиль, техніка та обладнання', '',
        'Еталон: `'+REFERENCE+'`, SHA256 `'+REFERENCE_SHA+'`. Тільки зовнішність, пропорції та матеріали. Поза, опори й м’язи визначаються exact-ID English та `scene` кожного запису.',
        'Стиль: `'+STYLE+'` (v1). Для двох muscle-up із primary=full_body додатково `'+NEUTRAL+'`: тіло нейтральне, тільки записані lats/chest/triceps підсвічені #F26445 на 40–50%; не підсвічувати все тіло. Для інших ID — конкретний primary повною інтенсивністю, exact secondary 40–50%.',
        'Категорія machine у нових записах не означає силовий тренажер: exact-ID instructions описують статичний турнік/бруси. Так само none не скасовує явно зазначеної лави, ящика, стіни, кілець або турніка. Перелік опор і обладнання збережений у кожному scene.',
        'Вибір сторони, ракурсу, однієї фази та дозволеної альтернативи (floor/parallettes, bar/rings, bench/box, foot/knee in band) — вибір ілюстрації, а не підміна техніки чи схвалення PNG.',
        'Для advanced-tuck фронт-левера джерело явно задає thighs in line with torso + bent knees. Prompt відтворює саме цю геометрію, а не довільний інший tuck за схожою назвою. Назва/вихідні поля не виправлялися.',
        'Зовнішнє доповнення полів не знадобилося: усі 28 записів заповнені. Це не твердження про незалежну перевірку біомеханіки або якості вихідних описів виробником.',
        '', '## Правила виконання', '',
        'Користувач передає один або кілька пакетів конкретному генератору. Не запускати один пакет двома агентами. Перед першим викликом записати свого власника в окремому registry своєї гілки. Поточні завдання інших агентів не забирати.',
        'Перед КОЖНОЮ генерацією отримати актуальні доступні гілки й звірити exact ID з реальними PNG, approval, manifests, assignments та локальними результатами. Будь-який PNG, включно з pending, або чужий active owner — пропустити ID й повідомити. Невдалий виклик без PNG зберігається в цьому ж пакеті; не створювати дубль.',
        'Використовувати непорожній `generation_prompt`, перевірений за `prompt_sha256`; еталон передавати як reference лише зовнішності. Одна людина, одна фаза, 1024×1024 transparent PNG. Не запускати альтернативний API.',
        'Точні результатні шляхи — `planned_png_path` та `planned_git_png_path`. Окремий manifest для кожного пакета вказано вище. Не перезаписувати вже початий manifest шаблоном; зберігати всі помилки, фактичні спроби й path/SHA256.',
        'Новий PNG має `user_review=pending` до явного рішення користувача, `agent_visual_review=not_performed`. Лише файлові перевірки, без повторного візуального QA й автоматичних корекцій. Підготовка prompt не є спробою генерації.',
        'Після кожного пакета зберегти manifest/результати, закомітити й запушити тільки свою виконавчу гілку, перевірити віддалені файли. За першої quota/rate-limit помилки зберегти checkpoint та зупинитися без повторних викликів.',
        'Не змінювати catalog.json, export, переклади, shared progress, схвалення чи Supabase. Нові pending PNG у Git дозволені лише у точних шляхах цього пакета. Якщо вони ignored, у своїй виконавчій гілці додати тільки вузькі .gitignore винятки для exact planned_git_png_path свого пакета; не дозволяти глобально всі PNG і не force-add сторонні медіа. Після призначених пакетів зупинитися.',
        '', '## Перевірка та межі', '',
        '`python3 -B scripts/prepare_agent03_supabase28.py --check` перевіряє exact-ID поля, повні source records і hashes, відсутність повторів/перетинів, scene/prompt, source/style/reference/output binding, незмінність старих файлів. Результат: `'+VALIDATION+'`.',
        'Preflight охоплює pushed файли актуальних доступних гілок. Незапушені результати/призначення чужих хмарних задач можуть бути недоступні. Supabase напряму не запитувався; використано hash-bound export імпортера. Немає нових схвалень або викликів генератора.', '',
    ]
    (ROOT / HANDOFF).write_text('\n'.join(lines))
    result = validate()
    save_new(VALIDATION, result)
    return result


def validate():
    assert git('branch', '--show-current').decode().strip() == BRANCH
    exported, source_manifest, by_id, scenes = source()
    snapshot = remote_snapshot(set(by_id))
    seen = []
    paths_seen = set()
    for bid, ids in GROUPS.items():
        batch = read(batch_path(bid))
        assert batch['batch_id'] == bid and batch['status'] == 'ready'
        assert batch['exercise_ids'] == ids
        assert batch['exercise_count'] == len(ids)
        assert batch['source_catalog_sha256'] == SOURCE_SHA
        assert batch['source_export_commit'] == SOURCE_COMMIT
        manifest = read(manifest_path(bid))
        assert manifest['batch_id'] == bid and manifest['execution_owner'] is None
        assert len(manifest['exercises']) == len(ids)
        for i, row in enumerate(batch['exercises'], 1):
            eid = ids[i-1]
            expected = task(by_id[eid], scenes[eid], bid, i)
            assert row == expected, ('Task is not bound to exact ID/source/scene/prompt', eid)
            assert row['exercise_id'] == eid and row['source_record']['id'] == eid
            assert row['source_english'] == by_id[eid]['content']['en']
            assert row['generation_prompt'].strip() and row['prompt_sha256'] == sha(row['generation_prompt'].encode())
            assert row['planned_git_png_path'].split('/')[-2] == eid
            assert row['planned_png_path'].split('/')[-2] == eid
            assert row['planned_git_png_path'] not in paths_seen
            paths_seen.add(row['planned_git_png_path'])
            mr = manifest['exercises'][i-1]
            assert mr['exercise_id'] == eid and mr['name'] == by_id[eid]['name']
            assert mr['attempts'] == 0 and mr['attempt_history'] == []
            assert mr['prompt_sha256'] == row['prompt_sha256']
            assert mr['source_record_sha256'] == row['source_catalog_record_sha256']
            for k in ('human_reference', 'style_version', 'planned_png_path', 'planned_git_png_path'):
                assert mr[k] == row[k]
            assert mr['user_review'] is None and mr['result_path'] is None
            seen.append(eid)
    assert len(seen) == len(set(seen)) == 28
    registry = read(REGISTRY)
    assert registry['exercise_count'] == 28 and not registry['generation_dispatched_by_preparer']
    assigned = []
    for assignment in registry['assignments']:
        bid = assignment['batch_id']
        assert assignment['exercise_ids'] == GROUPS[bid]
        assert assignment['execution_owner'] is None
        assert assignment['batch_path'] == batch_path(bid)
        assert assignment['manifest_path'] == manifest_path(bid)
        assigned.extend(assignment['exercise_ids'])
    assert assigned == seen
    queue = read(QUEUE)
    assert queue['prompt_prepared_count'] == 28 and queue['blocked_count'] == 0
    assert [r['exercise_id'] for r in queue['exercises']] == seen
    for row in queue['exercises']:
        batch = read(row['batch_path'])
        task_row = next(t for t in batch['exercises'] if t['exercise_id'] == row['exercise_id'])
        assert row['prompt_sha256'] == task_row['prompt_sha256']
    for line in git('diff', '--name-status', BASE, '--').decode().splitlines():
        status, path = line.split('\t')
        assert status == 'A' and path in own_paths(), ('Old tracked file changed', path)
    return {
        'schema_version': 1, 'validated_at_Kyiv': now(), 'status': 'passed',
        'source_catalog_path': SOURCE_PATH, 'source_catalog_sha256': SOURCE_SHA,
        'source_export_commit': SOURCE_COMMIT, 'source_record_count': 28,
        'batches': [{'batch_id': bid, 'path': batch_path(bid), 'status': 'ready',
                     'exercise_count': len(ids)} for bid, ids in GROUPS.items()],
        'exact_ID_uniqueness': True, 'full_source_records_and_English_fields_equal': True,
        'source_record_hashes_match_importer_manifest': True,
        'muscles_equipment_and_names_equal_exact_ID': True,
        'prompt_scene_reference_style_and_output_binding': True,
        'new_batch_ID_intersections': [], 'existing_PNG_or_assignment_intersections': [],
        'prepared_count': 28, 'blocked_count': 0, 'old_tracked_files_unchanged': True,
        'baseline_catalog_records': 451, 'baseline_language_blocks': 4448,
        'new_language_blocks': 28, 'combined_records': 479,
        'generation_calls': 0, 'Supabase_API_calls': 0, 'new_user_approvals': 0,
        'external_research_performed': False, 'remote_preflight': snapshot,
    }


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--prepare', action='store_true')
    group.add_argument('--check', action='store_true')
    args = parser.parse_args()
    result = prepare() if args.prepare else validate()
    print(json.dumps({k: result[k] for k in ('status', 'prepared_count', 'blocked_count',
                                            'batches', 'generation_calls', 'Supabase_API_calls')},
                     ensure_ascii=False, indent=2))
