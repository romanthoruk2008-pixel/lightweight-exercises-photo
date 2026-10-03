#!/usr/bin/env python3
"""Add one user-authored Easter egg and prepare a one-row future import.

No image generation, conversion, Supabase writes or edits to previous exercises.
The actual original image must be attached before its bytes can be bound.
"""
import argparse
import copy
import datetime
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[1]
ID = 'bed-cardio'
BASE_COMMIT = 'bf2c36432a654c74db852c7823ccfd6910a0b121'
IMPORTER_COMMIT = '2087b33346a4347a6fb65a6dfaff30981d147180'
CATALOG = 'data/exercises/catalog.json'
CHANGE = 'data/catalog-changes/bed-cardio.json'
CARD = 'data/cards/bed-cardio.json'
PAYLOAD = 'data/imports/bed-cardio/catalog-exercise.insert.json'
IMAGE = 'data/image-decisions/bed-cardio.json'
STYLE = 'data/style-decisions/bed-cardio-original-image.json'
CHECK = 'data/audits/bed-cardio-validation.json'
LANGUAGES = ['en', 'uk', 'es', 'it', 'tr', 'fr', 'ru', 'pl']

# Each block has the same meaning and structure. Names are localized inside
# content; the top-level canonical English name and ID remain stable.
TEXT = {
    'en': {
        'name': 'Bed Cardio',
        'description': 'Cardio, good company, and a comfortable pace. Log the duration — no personal best required.',
        'instructions': ['Agree on the activity and a comfortable pace together.', 'Start the timer when the activity begins.', 'Communicate throughout and pause whenever either person wants.', 'Stop the timer when you finish and save the duration.'],
        'form_cues': ['Keep it comfortable.', 'Communicate and respect each other’s boundaries.', 'Take breaks whenever needed.'],
        'common_mistakes': ['Treating the timer as a competition.', 'Ignoring discomfort or a request to stop.', 'Continuing when either person wants a break.'],
        'safety_note': 'For consenting adults. Either person can pause or stop at any time. Stop if you experience discomfort, pain, or dizziness.',
    },
    'uk': {
        'name': 'Кардіо в ліжку',
        'description': 'Кардіо, приємна компанія та комфортний темп. Записуйте тривалість — особисті рекорди необов’язкові.',
        'instructions': ['Разом домовтеся про активність і комфортний темп.', 'Запустіть таймер на початку активності.', 'Спілкуйтеся протягом активності та робіть паузу, коли цього хоче хтось із вас.', 'Після завершення зупиніть таймер і збережіть тривалість.'],
        'form_cues': ['Зберігайте комфортний темп.', 'Спілкуйтеся та поважайте межі одне одного.', 'Робіть перерви за потреби.'],
        'common_mistakes': ['Перетворювати таймер на змагання.', 'Ігнорувати дискомфорт або прохання зупинитися.', 'Продовжувати, коли хтось із вас хоче перепочити.'],
        'safety_note': 'Для дорослих за взаємною згодою. Кожен може зробити паузу або зупинитися будь-коли. Зупиніться в разі дискомфорту, болю чи запаморочення.',
    },
    'es': {
        'name': 'Cardio en la cama',
        'description': 'Cardio, buena compañía y un ritmo cómodo. Registra la duración: no hace falta batir récords personales.',
        'instructions': ['Acuerda la actividad y un ritmo cómodo con la otra persona.', 'Inicia el temporizador cuando comience la actividad.', 'Mantén la comunicación y haz una pausa si cualquiera de los dos lo desea.', 'Al terminar, detén el temporizador y guarda la duración.'],
        'form_cues': ['Mantén un ritmo cómodo.', 'Comunícate y respeta los límites de la otra persona.', 'Descansa cuando sea necesario.'],
        'common_mistakes': ['Convertir el temporizador en una competición.', 'Ignorar las molestias o una petición de parar.', 'Continuar cuando uno de los dos quiere descansar.'],
        'safety_note': 'Para adultos que dan su consentimiento. Cualquiera puede pausar o parar en cualquier momento. Detente si sientes molestias, dolor o mareo.',
    },
    'it': {
        'name': 'Cardio a letto',
        'description': 'Cardio, buona compagnia e un ritmo confortevole. Registra la durata: non serve battere record personali.',
        'instructions': ['Concorda l’attività e un ritmo confortevole con l’altra persona.', 'Avvia il timer quando inizia l’attività.', 'Comunica durante l’attività e fai una pausa quando uno dei due lo desidera.', 'Al termine, ferma il timer e salva la durata.'],
        'form_cues': ['Mantieni un ritmo confortevole.', 'Comunica e rispetta i limiti dell’altra persona.', 'Fai delle pause quando necessario.'],
        'common_mistakes': ['Trasformare il timer in una gara.', 'Ignorare il disagio o una richiesta di fermarsi.', 'Continuare quando uno dei due vuole riposare.'],
        'safety_note': 'Per adulti consenzienti. Ciascuno può fare una pausa o fermarsi in qualsiasi momento. Fermati in caso di disagio, dolore o capogiri.',
    },
    'tr': {
        'name': 'Yatakta Kardiyo',
        'description': 'Kardiyo, keyifli bir beraberlik ve rahat bir tempo. Süreyi kaydedin; kişisel rekor kırmanız gerekmiyor.',
        'instructions': ['Aktiviteye ve ikiniz için de rahat bir tempoya birlikte karar verin.', 'Aktivite başladığında zamanlayıcıyı başlatın.', 'Aktivite boyunca iletişim kurun ve ikinizden biri istediğinde ara verin.', 'Bitirdiğinizde zamanlayıcıyı durdurun ve süreyi kaydedin.'],
        'form_cues': ['Rahat bir tempoda kalın.', 'İletişim kurun ve birbirinizin sınırlarına saygı gösterin.', 'Gerektiğinde mola verin.'],
        'common_mistakes': ['Zamanlayıcıyı bir yarışa dönüştürmek.', 'Rahatsızlığı veya durma isteğini görmezden gelmek.', 'İkinizden biri mola vermek istediğinde devam etmek.'],
        'safety_note': 'Karşılıklı rıza gösteren yetişkinler içindir. Her iki kişi de istediği zaman ara verebilir veya durabilir. Rahatsızlık, ağrı veya baş dönmesi hissederseniz durun.',
    },
    'fr': {
        'name': 'Cardio au lit',
        'description': 'Du cardio, de la bonne compagnie et un rythme confortable. Enregistrez la durée : aucun record personnel à battre.',
        'instructions': ['Mettez-vous d’accord sur l’activité et sur un rythme confortable pour vous deux.', 'Démarrez le minuteur au début de l’activité.', 'Communiquez tout au long de l’activité et faites une pause dès que l’un de vous le souhaite.', 'À la fin, arrêtez le minuteur et enregistrez la durée.'],
        'form_cues': ['Gardez un rythme confortable.', 'Communiquez et respectez les limites de chacun.', 'Faites des pauses si nécessaire.'],
        'common_mistakes': ['Transformer le minuteur en compétition.', 'Ignorer un inconfort ou une demande d’arrêt.', 'Continuer alors que l’un de vous souhaite faire une pause.'],
        'safety_note': 'Pour des adultes consentants. Chacun peut faire une pause ou s’arrêter à tout moment. Arrêtez-vous en cas d’inconfort, de douleur ou de vertiges.',
    },
    'ru': {
        'name': 'Кардио в постели',
        'description': 'Кардио, приятная компания и комфортный темп. Записывайте длительность — личные рекорды необязательны.',
        'instructions': ['Вместе договоритесь об активности и комфортном темпе.', 'Запустите таймер в начале активности.', 'Общайтесь во время активности и делайте паузу, когда этого хочет кто-то из вас.', 'После завершения остановите таймер и сохраните длительность.'],
        'form_cues': ['Сохраняйте комфортный темп.', 'Общайтесь и уважайте границы друг друга.', 'Делайте перерывы при необходимости.'],
        'common_mistakes': ['Превращать таймер в соревнование.', 'Игнорировать дискомфорт или просьбу остановиться.', 'Продолжать, когда кто-то из вас хочет отдохнуть.'],
        'safety_note': 'Для взрослых по взаимному согласию. Каждый может сделать паузу или остановиться в любой момент. Остановитесь при дискомфорте, боли или головокружении.',
    },
    'pl': {
        'name': 'Cardio w łóżku',
        'description': 'Cardio, dobre towarzystwo i komfortowe tempo. Zapisuj czas trwania — rekordy osobiste nie są wymagane.',
        'instructions': ['Uzgodnij aktywność i komfortowe tempo z drugą osobą.', 'Uruchom minutnik na początku aktywności.', 'Utrzymuj komunikację i zrób przerwę, gdy którekolwiek z was tego chce.', 'Po zakończeniu zatrzymaj minutnik i zapisz czas trwania.'],
        'form_cues': ['Utrzymuj komfortowe tempo.', 'Komunikuj się i szanuj granice drugiej osoby.', 'Rób przerwy w razie potrzeby.'],
        'common_mistakes': ['Traktowanie minutnika jak rywalizacji.', 'Ignorowanie dyskomfortu lub prośby o zatrzymanie.', 'Kontynuowanie, gdy któreś z was chce odpocząć.'],
        'safety_note': 'Dla dorosłych za obopólną zgodą. Każda osoba może w dowolnej chwili zrobić przerwę lub zakończyć aktywność. Przerwij w razie dyskomfortu, bólu lub zawrotów głowy.',
    },
}


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def canonical(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':')).encode()


def git(*args):
    return subprocess.check_output(['git', *args], cwd=ROOT)


def save(path, value):
    target = ROOT/path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(value, ensure_ascii=False, indent=2)+'\n')


def load(path):
    return json.loads((ROOT/path).read_bytes())


def record():
    content = {lang: {**copy.deepcopy(TEXT[lang]), 'provenance': 'authored'} for lang in LANGUAGES}
    return {'id': ID, 'hevy_reference_id': None, 'name': 'Bed Cardio', 'equipment': 'none',
            'primary_muscle': 'cardio', 'secondary_muscles': [], 'tracking_type': 'duration', 'archived': False,
            'match': {'classification': 'generated', 'confidence': None,
                      'rationale': 'User-authored Lightweight Easter egg; no external dataset or Hevy exercise is claimed.', 'synonym_group': None},
            'source': {'dataset_id': None, 'image_path': None, 'attribution': None},
            'image': {'filename': 'bed-cardio.png', 'origin': None, 'qa_status': 'awaiting_original_file'},
            'content': content}


def prepare():
    assert git('branch', '--show-current').decode().strip() == 'agent-03-inventory-2026-10-01'
    raw = (ROOT/CATALOG).read_bytes()
    assert raw == git('show', BASE_COMMIT+':'+CATALOG), 'Preserve any unrelated catalogue change'
    old = json.loads(raw)
    assert all(e['id'] != ID for e in old['exercises'])
    for path in [CHANGE, CARD, PAYLOAD, IMAGE, STYLE, CHECK]:
        assert not (ROOT/path).exists(), ('Never overwrite', path)
    entry = record()
    suffix = b'\n  ]\n}\n'
    assert raw.endswith(suffix)
    serialized = '\n'.join('    '+line for line in json.dumps(entry, ensure_ascii=False, indent=2).splitlines()).encode()
    # Keep all previous record bytes untouched, inserting only the array comma
    # and this final record before the catalogue's closing delimiters.
    (ROOT/CATALOG).write_bytes(raw[:-len(suffix)]+b',\n'+serialized+suffix)
    catalogue = load(CATALOG)
    by_id = {e['id']: e for e in catalogue['exercises']}
    entry = by_id[ID]  # All downstream fields come from this exact catalogue ID.
    digest = sha((ROOT/CATALOG).read_bytes())
    save(CHANGE, {'schema_version': 1, 'exercise_id': ID, 'operation': 'append_one_user_authored_record',
                  'source_branch': 'agent-03-inventory-2026-10-01', 'baseline_commit': BASE_COMMIT,
                  'baseline_catalog_sha256': sha(raw), 'new_catalog_sha256': digest,
                  'previous_record_count': 451, 'new_record_count': 452,
                  'previous_language_blocks': 4448, 'new_language_blocks': 4456,
                  'languages_added': LANGUAGES, 'localized_name_field': 'content[locale].name',
                  'catalog_record_sha256': sha(canonical(entry)),
                  'explicit_user_authorization': 'Додай у каталог одну жартівливу вправу Bed Cardio; duration замість reps/sets; перекласти також назву; залишити надіслану ілюстрацію без змін.',
                  'source_archive_scope': 'Original release metadata applies to the unchanged legacy 451 records. This additional record is user-authored and is not falsely bound to the old working-manifest or dataset.',
                  'legacy_records_and_progress_unchanged': True, 'shared_progress_modified': False})
    save(CARD, {'schema_version': 1, 'exercise_id': ID, 'source_catalog_sha256': digest,
                'source_catalog_record_sha256': sha(canonical(entry)), 'renderer': 'standard_exercise_card',
                'category': 'cardio', 'tracking_type': entry['tracking_type'],
                'metric_fields': ['duration'], 'duration_unit': 'seconds', 'display_format': 'mm:ss',
                'show_reps': False, 'show_sets': False, 'show_weight': False, 'show_distance': False,
                'localized_title_lookup': 'content[locale].name -> content.en.name -> name',
                'localized_views': {lang: {'title': entry['content'][lang]['name'],
                                         'description': entry['content'][lang]['description'],
                                         'instructions': entry['content'][lang]['instructions'],
                                         'form_cues': entry['content'][lang]['form_cues'],
                                         'common_mistakes': entry['content'][lang]['common_mistakes'],
                                         'safety_note': entry['content'][lang]['safety_note']} for lang in LANGUAGES},
                'image_decision_path': IMAGE, 'image_binding_status': 'awaiting_original_file',
                'application_implementation_status': 'data_contract_only_application_repository_not_available'})
    direct = ['id', 'name', 'equipment', 'primary_muscle', 'secondary_muscles', 'tracking_type', 'archived', 'content']
    payload = {key: copy.deepcopy(entry[key]) for key in direct}
    payload.update(attribution=None, image_path=None, image_sha256=None, image_width=None, image_height=None, image_origin=None)
    # Replaces_ids is deliberately omitted; the existing approved importer
    # mapping uses the confirmed server default, not invented replacements.
    save(PAYLOAD, [payload])
    save(IMAGE, {'schema_version': 1, 'exercise_id': ID, 'status': 'awaiting_original_file',
                 'user_selected_visual': 'The attached adult couple resting side-by-side under a blanket in the anatomical library style.',
                 'user_decision': 'Залишаємо ілюстрацію, яку надіслав користувач; її не змінюємо.',
                 'selected_visual_approved_by_user': True, 'exact_original_bytes_bound': False,
                 'accepted_path': None, 'accepted_sha256': None, 'actual_mime_type': None,
                 'actual_width': None, 'actual_height': None, 'alpha_check': None,
                 'image_origin_for_supabase': None, 'original_image_creator_provenance': 'unknown',
                 'planned_repository_path': 'assets/exercises/bed-cardio.png',
                 'generation_allowed': False, 'transformations_allowed': [],
                 'no_resize_crop_retouch_recolor_or_transparency_processing': True,
                 'binding_rule': 'Once the original is available, preserve its exact bytes and bind path/SHA256 to the existing user selection. No new image approval is required for identical original bytes.',
                 'scope_limit': 'The chat rendering is visible; an original downloadable file ID or cloud-local image file was not supplied. Do not fabricate its bytes, hash, format, dimensions, transparency or generation origin.'})
    save(STYLE, {'schema_version': 1, 'exercise_id': ID, 'version': 'bed-cardio-user-original-2026-10-04',
                 'scope': 'Only this user-selected existing illustration; no global exercise style change.',
                 'authorization': 'User explicitly requests unchanged reuse of the supplied illustration.',
                 'preserve_original_people_pose_materials_highlights_aspect_ratio': True,
                 'catalogue_primary_muscle': entry['primary_muscle'], 'catalogue_secondary_muscles': entry['secondary_muscles'],
                 'neutral_primary_rule_for_future_standard_renders': 'Cardio with empty secondary would have no highlights. This existing user-selected asset is retained unchanged, including its visual highlights; no anatomical targets are inferred from those colors.',
                 'exceptions': ['Two adults in a resting scene instead of a single moving figure.',
                                'Preserve existing highlights without changing catalogue muscles.',
                                'Preserve original aspect ratio/dimensions; no square crop or 1024 resize.',
                                'Preserve the original appearance of both adults.'],
                 'rendered_content_scope': 'Non-explicit, covered adult couple; no new sexual actions or explicit illustration requested.',
                 'image_decision_path': IMAGE})
    return validate()


def validate():
    old_raw = git('show', BASE_COMMIT+':'+CATALOG)
    old = json.loads(old_raw)
    new_raw = (ROOT/CATALOG).read_bytes()
    new = json.loads(new_raw)
    assert new['exercises'][:-1] == old['exercises'], 'An old record was changed'
    assert {k:v for k,v in new.items() if k!='exercises'} == {k:v for k,v in old.items() if k!='exercises'}
    assert new_raw.startswith(old_raw[:-len(b'\n  ]\n}\n')]+b',\n'), 'Original catalogue bytes rewritten'
    counts = {eid: sum(e['id']==eid for e in new['exercises']) for eid in [e['id'] for e in new['exercises']]}
    assert len(counts) == len(new['exercises']) == 452 and all(n==1 for n in counts.values())
    entry = next(e for e in new['exercises'] if e['id']==ID)
    assert entry == record(), 'Exact-ID authored fields or localization differ'
    assert list(entry['content']) == LANGUAGES
    required = {'name', 'description', 'instructions', 'form_cues', 'common_mistakes', 'safety_note', 'provenance'}
    for lang, block in entry['content'].items():
        assert set(block) == required and block['provenance']=='authored'
        assert all(isinstance(block[k],str) and block[k].strip() for k in ['name','description','safety_note'])
        assert len(block['instructions'])==4 and len(block['form_cues'])==len(block['common_mistakes'])==3
        assert all(isinstance(s,str) and s.strip() for k in ['instructions','form_cues','common_mistakes'] for s in block[k])
    assert sum(len(e['content']) for e in new['exercises']) == 4456
    assert sum(e['archived'] for e in new['exercises']) == 3
    card=load(CARD);payload=load(PAYLOAD);image=load(IMAGE);style=load(STYLE);change=load(CHANGE)
    assert card['metric_fields']==['duration'] and not any(card[k] for k in ['show_reps','show_sets','show_weight','show_distance'])
    for lang in LANGUAGES:
        assert card['localized_views'][lang] == {k:entry['content'][lang]['name' if k=='title' else k] for k in card['localized_views'][lang]}
    assert len(payload)==1
    for k in ['id','name','equipment','primary_muscle','secondary_muscles','tracking_type','archived','content']:
        assert payload[0][k]==entry[k]
    assert 'replaces_ids' not in payload[0] and 'updated_at' not in payload[0]
    assert all(payload[0][k] is None for k in ['image_path','image_sha256','image_width','image_height','image_origin'])
    assert entry['source']=={'dataset_id':None,'image_path':None,'attribution':None}
    assert image['accepted_sha256'] is None and image['exact_original_bytes_bound'] is False
    assert image['generation_allowed'] is False and image['transformations_allowed']==[]
    assert style['exercise_id']==ID and style['preserve_original_people_pose_materials_highlights_aspect_ratio'] is True
    assert sha(new_raw)==change['new_catalog_sha256']==card['source_catalog_sha256']
    assert sha(canonical(entry))==change['catalog_record_sha256']==card['source_catalog_record_sha256']
    for path in ['data/exercise-image-progress.json','docs/exercise-image-style.md','docs/exercise-image-style-neutral-primary.md']:
        assert (ROOT/path).read_bytes()==git('show',BASE_COMMIT+':'+path),('Protected file changed',path)
    # Execute the existing importer constraint validator locally, without
    # REST calls, secrets or copying its hardcoded whole-catalog source pin.
    importer=Path('/tmp/bed-cardio-importer-evidence/dry_run.py')
    importer.parent.mkdir(parents=True,exist_ok=True)
    validator_bytes=git('show',IMPORTER_COMMIT+':integration/supabase/dry_run.py')
    importer.write_bytes(validator_bytes)
    spec=importlib.util.spec_from_file_location('bed_cardio_sql_checks',importer)
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    effective={**payload[0],'replaces_ids':[]}
    violations=module.constraint_violations(effective)
    assert violations==[],violations
    result={'schema_version':1,'status':'passed','exercise_id':ID,
            'checked_at_Kyiv':datetime.datetime.now(ZoneInfo('Europe/Kiev')).isoformat(),
            'baseline_commit':BASE_COMMIT,'catalog_sha256':sha(new_raw),'catalog_record_sha256':sha(canonical(entry)),
            'catalog_ID_count':452,'active_ID_count':449,'archived_ID_count':3,'language_blocks':4456,
            'old_records_unchanged':451,'old_language_blocks_unchanged':4448,'new_language_blocks':8,
            'localized_names':{lang:entry['content'][lang]['name'] for lang in LANGUAGES},
            'all_import_fields_match_exact_ID':True,'existing_SQL_CHECK_rules_passed':8,'SQL_violations':violations,
            'SQL_validator_origin_commit':IMPORTER_COMMIT,
            'SQL_validator_sha256':sha(importer.read_bytes()),'replaces_ids_server_default_used_only_for_local_check':True,
            'PNG_status':'awaiting_original_file','visual_selection_approved_by_user':True,
            'PNG_file_bound_or_uploaded':False,'PNG_origin_verified':False,
            'application_renderer_verified':False,'Supabase_writes':0,'generation_calls':0,'errors':[]}
    save(CHECK,result)
    return result


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--prepare',action='store_true')
    args=parser.parse_args()
    print(json.dumps(prepare() if args.prepare else validate(),ensure_ascii=False,indent=2))
