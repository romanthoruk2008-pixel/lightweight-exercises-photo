# Agent-03: черга «Інші» — тільки підготовка

Власна гілка: `agent-03-inventory-2026-10-01`. Work-зріз: `fe78b35c7f67a987c0a816cfc97f05f2bc6691bd`; agent-02: `2c27f90d8e2be0c1f349b81231897fd204d543b5`. Каталог SHA256: `a7cd78ba174d7277b4acaf95bd46c8a2774698d60a59cb2df6737fa2c7843989`. У робочій гілці збережено попередній shared progress; актуальні дані читалися через Git із origin/work, не переносилися й не редагувалися.

Доступно **127** вправ. Підготовлено **30** (3×10); **97** лишаються у черзі без prompts. Повний впорядкований список ID: [`data/queues/agent-03-other-queue.json`](../data/queues/agent-03-other-queue.json). Усі інші ID мають конкретну причину виключення й джерела в цьому ж файлі.

## Відбір та уточнення

Лише активні ID з inventory other, без PNG у work/agent-02/власній гілці; без спроб, result/accepted hashes та reviewed/uploaded результатів; без записів у старих batch/manifest/index/clarification файлах. Категорія machine сама по собі не визначає конструкцію: статичні турніки/бруси залишаються other за інвентаризацією, але тренажери/блоки/Сміт відкладено. Untouched not_started + attempts=0 + порожня історія й відсутній result при raw pending — не поданий на перегляд результат; це legacy default, effective unknown у попередній інвентаризації. Подані pending результати виключено.

Виключення взаємовиключні за першою причиною:

- Other із уже збереженим PNG: **73**.
- Нові уточнення техніки/стилю: **105**.
- Відкладені тренажери/блоки/Сміт: **123**.
- У старих пакетах/списках уточнень: **15**.
- Архівні з other: **2**.
- Неоднозначне обладнання в інвентаризації: **6**.

Нові уточнення: **105**; попередні не перепризначені: **15**. Детальні питання й незмінний англійський текст за кожним ID: [`data/queues/agent-03-other-clarifications.json`](../data/queues/agent-03-other-clarifications.json). Загальні primary full_body/cardio/other відкладені до правила локальної підсвітки v1; це не автоматична оцінка техніки як помилкової. Не вигадувати м’язові групи, пози, ваги чи анкери.

## Перший запуск — лише підготовлені пакети

### [agent-03-others-001](../data/batches/agent-03-others-001.json)

- `standing-calf-raise` — Standing Calf Raise
- `single-leg-standing-calf-raise` — Single Leg Standing Calf Raise
- `spiderman` — Spiderman
- `plank-pushup` — Plank Pushup
- `wall-sit` — Wall Sit
- `l-sit-hold` — L-Sit Hold
- `decline-pushup` — Decline Push Up
- `decline-crunch` — Decline Crunch
- `frog-pumps-dumbbell` — Frog Pumps (Dumbbell)
- `standing-calf-raise-dumbbell` — Standing Calf Raise (Dumbbell)

### [agent-03-others-002](../data/batches/agent-03-others-002.json)

- `sumo-squat-dumbbell` — Sumo Squat (Dumbbell)
- `curtsy-lunge-dumbbell` — Curtsy Lunge (Dumbbell)
- `lunge-dumbbell` — Lunge (Dumbbell)
- `reverse-lunge-dumbbell` — Reverse Lunge (Dumbbell)
- `walking-lunge-dumbbell` — Walking Lunge (Dumbbell)
- `deadlift-dumbbell` — Deadlift (Dumbbell)
- `single-leg-romanian-deadlift-dumbbell` — Single Leg Romanian Deadlift (Dumbbell)
- `upright-row-dumbbell` — Upright Row (Dumbbell)
- `zottman-curl-dumbbell` — Zottman Curl (Dumbbell)
- `overhead-press-dumbbell` — Overhead Press (Dumbbell)

### [agent-03-others-003](../data/batches/agent-03-others-003.json)

- `dumbbell-row` — Dumbbell Row
- `hip-thrust-dumbbell` — Hip Thrust (Dumbbell)
- `rear-delt-reverse-fly-dumbbell` — Rear Delt Reverse Fly (Dumbbell)
- `chest-supported-incline-row-dumbbell` — Chest Supported Incline Row (Dumbbell)
- `chest-supported-reverse-fly-dumbbell` — Chest Supported Reverse Fly (Dumbbell)
- `chest-supported-y-raise-dumbbell` — Chest Supported Y Raise (Dumbbell)
- `spider-curl-dumbbell` — Spider Curl (Dumbbell)
- `good-morning-barbell` — Good Morning (Barbell)
- `deadlift-barbell` — Deadlift (Barbell)
- `romanian-deadlift-barbell` — Romanian Deadlift (Barbell)

## Відповідність ID → джерело → prompt → PNG

Єдине джерело даних вправ — catalog.json. Кожен повний запис отримано через словник exact ID; не через назву, схожість чи номер у масиві. У batch збережено точні name, весь en-блок (description/instructions/cues/mistakes/safety/provenance), equipment, primary/secondary muscles та SHA256 повних байтів каталогу. Додатково зафіксовано SHA256 конкретного запису, en-блока і prompt. Payload prompt містить ті самі поля; окремий scene вибрано за точним ID, із цитатами конкретних instructions, однією фазою й явними опорами. Каталог/старі пакети не виправлялися.

Перед записом скрипт перевірив: кожен ID у каталозі рівно один раз; усі вихідні поля точно рівні своєму запису; 30 ID унікальні між пакетами; немає перетину з виконаними або старими призначеними ID; prompt/hash і планований шлях містять відповідний ID. Результат — [`validation.json`](../data/queues/agent-03-other-validation.json). Повторна read-only перевірка:

```bash
git fetch --no-tags origin '+refs/heads/work:refs/remotes/origin/work' '+refs/heads/agent-02-machines-001:refs/remotes/origin/agent-02-machines-001'
python scripts/prepare_agent03_other_queue.py --check
```

Скрипт --check нічого не записує. Якщо будь-який ID став виконаним/призначеним, source/style hash змінився чи поля не збігаються — зупинити його, виключити та повідомити; не копіювати сусідній запис, не заміняти ID автоматично й не виправляти англійську техніку здогадкою. Перед новим запуском перевірити також нові agent-гілки, якщо вони з’являться.

## Правила майбутнього виконання — зараз не запускати

Підготовка не є дозволом на генерацію; attempts=0, результатів і user_review немає. Чекати окремої команди користувача на цей запуск. Не створювати worktree й не працювати з локальним Mac. Перед кожним дозволеним викликом fetch/read актуальні work та agent-гілки, перевірити progress, batches і наявні PNG; пропускати approved, submitted pending, вже виконане або чужі призначення.

Стиль v1 з current work, SHA256 `8956307274990bdefd11bcc18e6d6deb2aed35580b5c2ea3ac0061dee708e578`. Human-appearance reference: `assets/exercises/biceps-curl-dumbbell.png`, SHA256 `52fef743ba2d7689aa81a8b995df3c6715cbb5d04c4bd688af4ca57b2d20057f`. Під час підготовки еталон не відкривали для візуальної оцінки; перед майбутньою генерацією окремо перевірити файл/hash/доступність пікселів. Роль тільки зовнішність/пропорції/матеріали; не поза, обладнання чи м’язова підсвітка. Не отримувати референси з інших сервісів або старих вихідних 48 PNG.

Після дозволу — тільки вбудований image_gen, точний непорожній generation_prompt із record, отриманого за exercise_id. Не брати prompt за позицією в масиві. Журнал фактичного виклику має містити exercise_id, batch_id, source_catalog_sha256, source_catalog_record_sha256, generation_prompt_sha256, tool-call identity, фактичний attempt, result_path і result_sha256. Планований шлях: `/workspace/exercise-image-results/<batch_id>/<exercise_id>/attempt-1.png`; він ще не існує і не видається за збережений результат. Записувати фактичний PNG від саме цього виклику під саме цим ID; звірити поля журналу й SHA256, не перейменовувати чужий output за схожістю.

Файлова відповідність та provenance не доводять візуальної правильності картинки. У цьому етапі ні генерації, ні візуального QA немає. Не підміняти рішення користувача агентською оцінкою. Не робити автоматичних повторів/ресайзу, не працювати із Supabase чи платним API, не міняти каталог/shared progress. Майбутній журнал вести у власному окремому manifest, лише після окремого дозволу на виконання.

**Межа:** незапушені файли/бронювання інших хмарних завдань можуть бути недоступні. Черга є перевіреним Git-зрізом, а не гарантією відсутності прихованих паралельних завдань. Зображення не генерувалися; наступний етап не розпочато.

Кінцева read-only звірка перед commit: `origin/work` fcc2cf3227cbe8e52932c0c56b7ca89018cd0a10; `--check` пройшов. Нове схвалення вже наявного `pushup-close-grip` не змінює жодного з 127 придатних ID; цей ID лишається виключеним за наявністю PNG. Зріз початкової підготовки й кінцеву перевірку окремо збережено в queue/validation.
