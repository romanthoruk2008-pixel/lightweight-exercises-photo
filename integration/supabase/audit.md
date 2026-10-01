# Аудит і підготовка Supabase — agent-04

Це зафіксований аудит підготовки **до дозволу на запис**. Пізніше
користувач дозволив імпорт із server default replaces_ids; область дозволу
збережено у `import_authorization.md`. Актуальні результати імпорту,
Storage/public SHA256 і DB links — у `uploads` та `handoff.md`. Історичні
відмітки про відсутність записів/дозволу нижче не є поточним станом апки.

## Виконання й межі

Робота виконана у cloud workspace `/workspace/lightweight-exercises-photo`.
Платформа повідомляє provider=cloud; Debian Linux, Kata Containers overlay,
`systemd-detect-virt=container-other`. Доступу до файлових систем Mac не
виявлено в доступних завданню монтуваннях. Архів джерела містить історичні
`__MACOSX`/README_macos entries; це файли віддаленого ZIP, не host volumes.
Медіа/інструменти з цього ZIP не витягувалися й не виконувалися.

Джерело `work`: `a6f296cbc6737991dd367e929b3e2df25874d4d8`. Нову власну
гілку створено від цього commit без злиття інших гілок. Існуючі каталог,
мовні блоки, PNG, progress, manifests і схвалення залишено незмінними.

## Доступ і фактична порожнеча

Проєкт: `yywyrbhqfavjdgonlzma`; прив'язка `exerciseuploader`.
Запити використовують `apikey` через налаштований HTTPS proxy.
**GET `/auth/v1/admin/users?page=1&per_page=1` повернув HTTP 200** без
передавання окремого Authorization. Це підтверджує фактичний доступ до
серверного Admin endpoint, окремо від успішного Storage read. Значення
ключа, ідентичності чи атрибути користувачів не виводилися й не зберігалися.

GET REST schema, усіх п'яти таблиць і Storage metadata повернули HTTP 200.
`catalog_exercise`, `exercise`, `workout`, `logged_exercise`, `set_entry`
повернули по 0 видимих рядків з Content-Range `*/0`. Перевірено пагінацію
до порожньої сторінки; вона не покладається на максимальний розмір сторінки
сервера. Дублікатів або розірваних зв'язків у видимій вибірці немає, але
порожня вибірка не є доказом їх відсутності в усій БД.

Серверні Admin-права підтверджені. **Фактична порожнеча каталогу на момент
SQL-перевірки підтверджена незалежним SQL-підрахунком**, результати якого
надав користувач: editor_role=postgres, rls_applies_to_editor=false,
catalog_row_count=0. Джерело збережено у `sql_editor_evidence.json`; агент
сам цей SQL не виконував, час виконання не вигадано. Це підтвердження
стосується `public.catalog_exercise`, не всіх таблиць або всієї БД.

Точна роль PostgREST/BYPASSRLS досі не перевірена через role metadata.
`pg_catalog` не експонується (HTTP 406, PGRST106); SQL connection/management
access і код апки недоступні. Не змінювали RLS/grants і не викликали
`rls_auto_enable`. Нове читання REST узгоджується з SQL count=0. Якщо під
час наступного dry-run з'являться рядки, це окреме блокування зміни стану,
а не дозвіл на upsert. Повторювати вже надані SELECT зараз не потрібно.

## Схема, зв'язки й мовні дані

`catalog_exercise.id` — text PK каталогу; `exercise.id` — окрема таблиця
користувацьких вправ із owner_id. Зіставлення імпорту тільки за точним ID.
`content` — JSONB; source містить 451 ID і 4448 блоків 11 мов, включно з
provenance/null. Data equality і hashes мовних блоків можна перевірити після
отримання видимих записів/вставки; зараз всі 451 source ID не мають видимого
DB record.

Image-поля: image_path, image_sha256, image_width, image_height, image_origin,
attribution. FK показані для logged_exercise.workout_id і
set_entry.logged_exercise_id. FK для logged_exercise.exercise_id у REST
metadata не показаний; він може посилатися на catalog/custom exercise і
потребує підтвердження кодом апки.

## `replaces_ids`

SQL Editor підтвердив JSONB, NOT NULL, default `'[]'::jsonb`, comment NULL.
Користувач також надав повні definitions усіх восьми CHECK constraints.
Вони збережені без скорочень у `sql_editor_evidence.json`; REST сам не
надавав цих метаданих. У checkout немає SQL-міграцій/коду апки; поле та
replacement-related ключі відсутні у вихідному каталозі.

Оригінальний `working-manifest.json` із `exercise-source-v1` також
перевірено: SHA256 точно збігається з pinned джерелом
`1b9c3508f23ca476d0e9798bcb8a1f058e925e47cd4a8358fb8cc78c9e168e60`;
replacement-related ключів/`replaces_ids` немає. У ZIP directory немає
SQL/міграцій. Використано HTTP byte ranges для directory/manifest;
повний SHA256 411210021-byte ZIP не перевірявся та не заявляється.

CHECK `catalog_exercise_lists_are_arrays` вимагає масив у replaces_ids,
але не встановлює тип його елементів, напрямок заміни чи валідність ID.
Користувач повідомив, що міграції/код,
призначення й значення йому невідомі, та прямо вказав залишити поле
невідомим без довільного заповнення. Це зафіксовано у `field_mapping.md`;
бізнес-семантику сам default не доводить. Підготовлено тільки чернетку
вставки з пропущеним `replaces_ids`: жодного значення від агента не
підставлено. Для перевірки ефективного рядка локально враховано відомий
SQL default []; це не запис у Supabase і не рішення про заміни.

Усі 451 записи чернетки та 135 повних image patch проходять локальну
перевірку восьми наданих CHECK. Чернетка має всі image-поля NULL; image
patch містить одразу path/hash/width/height/origin, як вимагає правило
all-or-nothing. `image_origin=generated` дозволений без attribution;
`gym_visual_edit` вимагав би непорожнього credit. Усі source ID є slug,
кожний content має English object, secondary_muscles є масивом.
Перевірка Python стосується цього SQL snapshot, не замінює реальний SQL
INSERT і не перевіряє невідомі triggers або поведінку апки. Checksum
definitions не дозволяє тихо застосувати ці правила до змінених CHECK.

## Bucket і 135 прийнятих PNG

`exercise-images`: public=true, allowed_mime_types=[image/png],
file_size_limit=5242880 (5 MiB), type=STANDARD. Read-only root list повернув
0 entries. З'єднання і bucket constraints перевірені; write permission не
тестувалося пробним записом.

Для кожного user_review=approved взято саме accepted SHA256 і repository
path із відповідного manifest. Всі **135/135** файлів у cloud checkout:

- SHA256 байтів точно збігається з прийнятим;
- PNG signature, Pillow verify/load і фактичні dimensions перевірені;
- є реально повністю прозорі пікселі, не лише alpha channel;
- розмір кожного менше 5 MiB; найбільший 1369930 bytes;
- загалом 107196920 bytes; 134 PNG 1254×1254, один 1536×1024.

21 generated/pending виключено; rejected та історичні неприйняті спроби
не включено. Однакові копії approved не створюють повторного exercise_id.
Recorded technical_check=failed збережено для шести ID: ab-wheel,
bench-press-barbell, biceps-curl-dumbbell, cable-fly-crossovers-machine,
pushup-close-grip, seated-shoulder-press-machine. Target 1024×1024,
не-квадратність pushup-close-grip і alpha corner observations не приховані,
схвалення не переглянуті, ресайз/перегенерація не виконувалися.

Повний план: `results/approved_png_plan.json`. Destination:
`<exercise_id>/<accepted_sha256>.png`, bucket `exercise-images`.
Всі 135 `db_record=null` відповідають відсутності видимого DB record;
SQL count=0 без RLS незалежно підтвердив, що каталог на момент тієї
перевірки порожній. Перед зображеннями потрібне наповнення каталогу.

## Апка й блокування

Коду апки, її publishable/anon key та authenticated client session немає.
Права звичайного клієнта на читання catalog і поведінку URL не перевірено.
Public bucket URL передбачає читання objects, не доводить права list/write.
Client має отримувати public URL за image_path, не отримувати admin secret.

Count/default/вісім CHECK тепер підтверджені. Перед імпортом потрібні:
семантичне рішення щодо replaces_ids; перевірка клієнтських policies/коду;
окремий дозвіл на записи
Supabase. Схема вже має image/content-поля, тому міграція для цих полів не
виявлена як необхідна. Не пропонується обхід RLS або сліпий upsert.

## Перевірки підготовки

Live dry-run сформував 135 PNG rows і 451 catalog plan row; вихідний код 2
очікуваний через описані блокування. Supabase writes=0, PNG uploads=0.
Усі 17 тестів пройшли. Негативні тести перевіряють SHA mismatch, непрозорий alpha, truncated PNG,
bucket size limit, mutation/RPC guard і пагінацію зі зменшеними сторінками.
Додані перевірки не приймають RLS-filtered zero count як доказ порожнечі,
не приймають evidence іншого проєкту, не трактують default як семантику,
відхиляють нові невідомі CHECK та часткові image links. Позитивні випадки
підтверджують seed без images і прийнятий не-квадратний generated PNG.
Деталі відтворення у README. Підготовка не означає імпорт або міграцію.
