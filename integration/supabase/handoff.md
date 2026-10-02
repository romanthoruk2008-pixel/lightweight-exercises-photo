# Supabase імпорт завершено — agent-04

Проєкт `yywyrbhqfavjdgonlzma`; bucket `exercise-images`.
Користувач прямо дозволив 451 source record і 135 approved PNG;
область дозволу зафіксована у `import_authorization.md`.
Виконання: поточний cloud workspace, через HTTPS proxy і наявну
прив'язку `exerciseuploader`; секрет не виводився і не зберігався.

## Фактичний результат

- Вставлено 451 новий catalog_exercise; POST без upsert, по 100 рядків,
  `Prefer: missing=default,return=minimal`.
- `replaces_ids` не передавали. На читанні назад для всіх вставлених ID
  підтверджено server DEFAULT []; replacement links не вигадувалися.
- Повне фінальне читання: точна множина 451 ID, всі source-поля і content
  рівні джерелу, 4448 мовних блоків, 3 архівні записи.
- Завантажено 135 нових PNG без перезапису; для кожного canonical public
  URL без apikey/Authorization повернув image/png і точний accepted SHA256.
- Після public verification оновлено п'ять image-полів точного ID з
  optimistic filters по updated_at і старих image-полях; читання назад
  підтвердило 135 зв'язків і незмінний content.
- Перші 3 — успішний gate. Далі 13 пакетів по 10 і останній із 2;
  разом 15 окремих manifest-файлів.
- 21 pending і rejected/історичні неприйняті спроби не завантажувалися.
- Помилок перенесення немає. Наявні technical exceptions, dimensions,
  PNG bytes, source catalog, progress і схвалення не змінені.
- Користувацькі таблиці, schema, policies/RLS/grants не змінювалися.

Остання повна перевірка: `2026-10-01T21:33:24.591892+00:00`
(2 жовтня 2026, 00:33 за Europe/Kiev). Точні часові позначки в manifests — UTC.
Git-гілка результатів: `agent-04-supabase-integration`; інші гілки не оновлювалися.

## Артефакти і відновлення

- `uploads/catalog_manifest.json`: 5 insert batches, їхні точні ID,
  читання назад і перевірка default. `unique_inserted_ids_recorded=451`.
- `uploads/batch-001.json` … `batch-015.json`: source PNG, exercise_id,
  accepted SHA256, Storage path, public byte verification, DB before/after.
- `uploads/completion.json`: фінальний каталог і всі 135 PNG/DB links.
- `uploads/summary.json`: агреговані фактичні counts і SHA256 manifests.
- `uploads/resume_readonly_check.json`: фактично перевірене відновлення
  для 451 identical catalog records і перших 3 complete PNG, з mutations
  API вимкненими. Нових INSERT/upload/PATCH не було.

`import_catalog_images.py` без flags — тільки preflight. `--apply` вже
авторизований для цієї scope і пропускає complete entries після повторного
читання public bytes і DB. `--verify-only` не дозволяє Supabase mutations.
Не видаляти checkpoints і не перезаписувати інші Storage objects/DB links.
Конфлікт source/content/hash/link зупиняє імпорт. Невизначений результат
після network failure відновлювати читанням, а не сліпим повтором запису.

Усі 28 тестів пройшли, включно з no-overwrite, server-default omission,
public-before-PATCH, resume, concurrency filters і забороною mutations
до користувацьких таблиць/RPC/інших objects.

`data/exercise-image-progress.json`, початковий audit і `results` залишені
як незмінні джерела/історія підготовки. Їхній історичний not_configured
або старі блокування не є поточним статусом Supabase; поточна істина —
live Supabase і `uploads` manifests. Не скидати схвалення/attempts через
ці історичні значення і не запускати generation повторно.

## Межа клієнтської перевірки

Публічне читання PNG підтверджене для всіх 135 об'єктів без секрету.
Читання каталогу звичайним клієнтом **не перевірене**: у доступній
конфігурації/процесі немає publishable/anon key. Admin read не є доказом
клієнтських grants/RLS. Це відсутня передумова перевірки, не встановлена
помилка конкретної policy; policies не змінювалися для обходу.

Якщо стане доступною прив'язка publishable/anon key, виконати
`import_catalog_images.py --verify-only`: скрипт перевірить точні 451 ID,
content/4448 мовних блоків звичайним клієнтом і оновить completion report
без Supabase writes. Сам ключ у чат/файли не копіювати.

<!-- continuation:continuation-2026-10-02 -->

## Продовження схвалених PNG — continuation-2026-10-02

Поточна контрольна точка: `2026-10-02T15:53:01.770498+00:00`.
Нових Storage uploads: 57; завершених перенесень: 57; заміни прийнятих версій: 0.
Попередніх перевірено: 135; pending пропущено: 27.
Артефакти: `uploads/continuation-2026-10-02/plan.json`, `batch-*.json`, `summary.json`.
Каталог не імпортувався повторно. Використано `continue_images.py` і перевірений `import_catalog_images.transfer_one`; лише Storage POST без upsert і п’ять image-полів із concurrency filters. Старі PNG не видаляються; content/451 ID/4448 мовних блоків незмінні.
PNG staging поза Git: `/workspace/supabase-image-staging/<source_commit>/<source_png>`.

### Фінальне звіряння продовження

Завершено `2026-10-02T15:56:11.448484+00:00` UTC. Усі 57 нових PNG і попередні 135 зв’язків підтверджені; разом 192 точних ID із зображеннями. Каталог: 451 ID, 4448 мовних блоків, 3 архівні; усі source-поля незмінні.
Нових завантажень — 57; замін попередньої прийнятої версії — 0; pending пропущено — 27; блокувань/помилок — 0. Усі нові PNG 1254×1254, декодуються й мають фактичні прозорі пікселі; збережено 10 явно прийнятих technical_check=failed через ціль 1024×1024.
Фінальні докази: `uploads/continuation-2026-10-02/completion.json` і `resume_readonly_check.json` (3 complete transfers повторно перевірені з API mutations disabled; жодного запису).
Відновлення саме цієї scope: `python3 -B integration/supabase/continue_images.py --run-id continuation-2026-10-02 --apply`. Нові схвалення потребують нового run-id; не замінювати frozen plan.
Перевірені джерела:
- `agent-02-machines-001`: `2c27f90d8e2be0c1f349b81231897fd204d543b5`.
- `agent-03-inventory-2026-10-01`: `91a80cd9c0cfbb33088f24488af24c781ab2bbf3`.
- `agent-05-parallel-generation`: `8fdae08adeaa14f4b9721ce164053634bda5b13f`.
- `work`: `f6c8874805203c78d804eb073e1627c6d4ddc78e`.

### Оновлені джерела після перенесення

Повторна перевірка `2026-10-02T15:59:59.481559+00:00` UTC: додаткових approved немає; pending з фактичними PNG — 57 унікальних ID. Перший frozen plan мав 27 pending; після нових комітів з’явилися ще 30 у пакетах 019, 020 і 021. Shared progress навмисно не містить цих результатів; звірено manifests, Git trees і SHA256 усіх доступних pending blobs. Їх не завантажували.
Точні ID і commits: `uploads/continuation-2026-10-02/final_source_review.json`. Frozen import plan та approval evidence не змінені.
- `agent-02-machines-001`: `2c27f90d8e2be0c1f349b81231897fd204d543b5`.
- `agent-03-inventory-2026-10-01`: `91a80cd9c0cfbb33088f24488af24c781ab2bbf3`.
- `agent-05-parallel-generation`: `c69fd600f81d24116167ac4b936c3e194fbbba4f`.
- `work`: `46fa5a197f6bb7d6611ea67e64707b4293422ef5`.

<!-- continuation:continuation-2026-10-02-02 -->

## Продовження схвалених PNG — continuation-2026-10-02-02

Поточна контрольна точка: `2026-10-02T19:35:55.237421+00:00`.
Нових Storage uploads: 52; завершених перенесень: 52; заміни прийнятих версій: 0.
Попередніх перевірено: 192; pending пропущено: 32.
Артефакти: `uploads/continuation-2026-10-02-02/plan.json`, `batch-*.json`, `summary.json`.
Каталог не імпортувався повторно. Використано `continue_images.py` і перевірений `import_catalog_images.transfer_one`; лише Storage POST без upsert і п’ять image-полів із concurrency filters. Старі PNG не видаляються; content/451 ID/4448 мовних блоків незмінні.
PNG staging поза Git: `/workspace/supabase-image-staging/<source_commit>/<source_png>`.

### Фінальний результат другого продовження

Завершено `2026-10-02T19:39:02.666562+00:00` UTC. Нових PNG завантажено й прив’язано — 52; замін прийнятих версій — 0; попередніх перенесень перевірено — 192; разом — 244 точних ID із зображеннями. Pending із фактичними PNG пропущено — 32; помилок і блокувань — 0.
Усі 451 source record, 4448 мовних блоків і 3 архівні статуси звірені без змін. Нові PNG: 20 із work (019/020), 20 із agent-05 (021/022), 12 із agent-06 (024/025). Handstand Hold — саме явно прийнята attempt-2.
Додані адаптери accepted_result_path/accepted_result_sha256, явного рішення accepted, nested manifest і approval_record без shared progress. Джерельні схвалення/технічні винятки не редагувалися; accepted path/hash/рішення збережені у frozen plan. Механізм Storage POST без upsert → public SHA256 → image-only PATCH лишився тим самим.
Фінальні докази: `uploads/continuation-2026-10-02-02/completion.json`, `final_source_review.json`, `resume_readonly_check.json`; 42 offline tests пройшли. Три complete transfers повторно перевірені з API mutations disabled; записів не було.
Відновлення цієї scope: `python3 -B integration/supabase/continue_images.py --run-id continuation-2026-10-02-02 --apply`. Для нових схвалень створювати новий run-id.
- `agent-02-machines-001`: `2c27f90d8e2be0c1f349b81231897fd204d543b5`.
- `agent-03-inventory-2026-10-01`: `2ee4c3f612aa3e2d62935f5e0dab0100be37935f`.
- `agent-05-parallel-generation`: `172ea1052d0a1be125d79fb8a3d4ab18283b5bee`.
- `agent-06-generator-a-2026-10-02`: `8b4e4d7de0572909b8e0f3591d60c87192194338`.
- `work`: `bc67b32e93322bac86b7a31264cd0f8b2ab3f6eb`.

<!-- continuation:continuation-2026-10-02-03 -->

## Продовження схвалених PNG — continuation-2026-10-02-03

Поточна контрольна точка: `2026-10-02T20:48:57.987507+00:00`.
Нових Storage uploads: 31; завершених перенесень: 32; заміни прийнятих версій: 0.
Попередніх перевірено: 244; pending пропущено: 0.
Артефакти: `uploads/continuation-2026-10-02-03/plan.json`, `batch-*.json`, `summary.json`.
Каталог не імпортувався повторно. Використано `continue_images.py` і перевірений `import_catalog_images.transfer_one`; лише Storage POST без upsert і п’ять image-полів із concurrency filters. Старі PNG не видаляються; content/451 ID/4448 мовних блоків незмінні.
PNG staging поза Git: `/workspace/supabase-image-staging/<source_commit>/<source_png>`.

### Фінальний результат третього продовження

Завершено `2026-10-02T20:51:07.080159+00:00` UTC. Нових прийнятих PNG перевірено й прив’язано — 32; замін версій — 0; попередніх перенесень звірено — 244; разом — 276 точних ID із зображеннями. Pending — 0; додаткових approved після перенесення — 0; незавершених помилок/блокувань — 0.
Пакети: 10, 10, 10, 2. Нові версії: 27 із work і 5 із agent-05; є точні accepted path/SHA256 та явні рішення користувача. Scalar approval_decision сам собою не є доказом схвалення; використано точні записи user_review_history. Адаптер лише читає новий формат джерела; схвалення не редагувалися.
Усі PNG 1254×1254, RGBA, декодуються та містять прозорі пікселі; найбільший 1194670 байтів, bucket limit 5242880. П’ять історичних technical_check=failed та явно прийняті технічні винятки збережені.
Зафіксовано 31 успішний Storage POST без upsert. На chinup-machine скрипт один раз зупинився з HTTP 401 після появи PNG у Storage й до зміни image-полів. Читання apikey каталогу/buckets знову дало 200; публічний SHA256 об’єкта підтверджено, рядок був незмінний. Після звіряння стану відновлено через ту саму контрольну точку; існуючий файл не перезаписано. Цей перенесений файл має storage_action=existing_bytes_verified_no_overwrite. Причина одноразової 401 не встановлена; докази та відновлення збережено в access_recheck.json.
Повторне читання підтвердило точні 451 ID, source-поля, 4448 мовних блоків і 3 архівні записи без змін та всі 276 поточних image links. Public URL/SHA256 підтверджені; звичайний клієнтський доступ до каталогу лишається неперевіреним без publishable/anon key. RLS, grants, схему й користувацькі таблиці не змінено.
Фінальні докази: `uploads/continuation-2026-10-02-03/completion.json`, `catalog_final_readback.json`, `final_source_review.json`, `resume_readonly_check.json`; 43 offline tests пройшли. Три complete transfers повторно перевірені з API mutations disabled.
Відновлення цієї scope: `python3 -B integration/supabase/continue_images.py --run-id continuation-2026-10-02-03 --apply`. Для нових схвалень використовувати новий run-id і не змінювати frozen plan.
- `agent-02-machines-001`: `2c27f90d8e2be0c1f349b81231897fd204d543b5`.
- `agent-03-inventory-2026-10-01`: `2ee4c3f612aa3e2d62935f5e0dab0100be37935f`.
- `agent-05-parallel-generation`: `058e4810f858b5f0cca1d27384c8e36d525b24fa`.
- `agent-06-generator-a-2026-10-02`: `8b4e4d7de0572909b8e0f3591d60c87192194338`.
- `work`: `b0385b7e2f3382d545a6dff5304c81ba3c771096`.

<!-- continuation:continuation-2026-10-03 -->

## Продовження схвалених PNG — continuation-2026-10-03

Поточна контрольна точка: `2026-10-02T22:55:52.403105+00:00`.
Нових Storage uploads: 26; завершених перенесень: 26; заміни прийнятих версій: 0.
Попередніх перевірено: 276; pending пропущено: 0.
Артефакти: `uploads/continuation-2026-10-03/plan.json`, `batch-*.json`, `summary.json`.
Каталог не імпортувався повторно. Використано `continue_images.py` і перевірений `import_catalog_images.transfer_one`; лише Storage POST без upsert і п’ять image-полів із concurrency filters. Старі PNG не видаляються; content/451 ID/4448 мовних блоків незмінні.
PNG staging поза Git: `/workspace/supabase-image-staging/<source_commit>/<source_png>`.

### Фінальний результат четвертого продовження

Завершено `2026-10-02T22:57:33.577330+00:00` UTC. Нових PNG завантажено й прив’язано — 26; замін версій — 0; попередніх перенесень звірено — 276; разом — 302 точних ID із зображеннями. Pending — 0; додаткових approved після перенесення — 0; помилок і блокувань — 0.
Пакети: 10, 10, 6. Усі нові файли з agent-07-generator-b-2026-10-02: manifest містить явне user_approval (accepted_by=user), accepted_path/SHA256 та однаковий user_approved_at для кожного з 26 ID. Shared progress не змінювався генератором; старі package summary pending_user_review не використовуються як актуальні рішення. Адаптер читає цей формат без змін схвалень; перевіряє actor/decision/count/timestamp і точну пару accepted path/hash.
Механізм перенесення незмінний: Storage POST без upsert → public URL/SHA256 → лише п’ять image-полів з concurrency filters. Усі PNG декодуються, 1254×1254, RGBA, мають фактичні прозорі пікселі; найбільший 1013780 байтів при bucket limit 5242880. Усі 26 historical technical_check=failed через розміри збережено разом із явно прийнятим technical_issue_accepted_by_user; без ресайзу, візуального QA або генерації.
Фінальне читання підтвердило точні 451 ID, усі source-поля, 4448 мовних блоків і 3 архівні статуси без змін та всі 302 image links. Публічне читання PNG підтверджене; клієнтське читання каталогу лишається неперевіреним без publishable/anon key. Каталог повторно не імпортувався; користувацькі таблиці, RLS, grants і схема не змінені.
Фінальні докази: `uploads/continuation-2026-10-03/completion.json`, `catalog_final_readback.json`, `final_source_review.json`, `resume_readonly_check.json`; 46 offline tests пройшли. Три завершені перенесення повторно перевірені з API mutations disabled.
Відновлення цієї scope: `python3 -B integration/supabase/continue_images.py --run-id continuation-2026-10-03 --apply`. Для наступних схвалень — новий run-id; frozen plan не змінювати.
- `agent-02-machines-001`: `2c27f90d8e2be0c1f349b81231897fd204d543b5`.
- `agent-03-inventory-2026-10-01`: `6d2871c8d1ef7d6430257f19c8d25587fab9ca0f`.
- `agent-05-parallel-generation`: `058e4810f858b5f0cca1d27384c8e36d525b24fa`.
- `agent-06-generator-a-2026-10-02`: `8b4e4d7de0572909b8e0f3591d60c87192194338`.
- `agent-07-generator-b-2026-10-02`: `9dfc775a57ff6856995addbaf28f303661a7b5de`.
- `work`: `b0385b7e2f3382d545a6dff5304c81ba3c771096`.
