# Пакет 043: три явні продовження без PNG

Оновлено: 2026-10-03T20:02:31Z

Джерельна гілка: `agent-03-inventory-2026-10-01`. Незмінний коміт завдань: `8d17e7a233d7bcd3055c78dd691090cce01a0d5b`.
Один існуючий виконавець: `agent-08-generator-single-2026-10-03`, після всіх уже взятих завдань, включно з 041–042. На етапі підготовки: **ready**, 3 вправи; явного dispatch ще не було, генератор підготовки зробив 0 викликів. Dispatch користувача й фактичне виконання записані нижче. Генерацій під час підготовки: **0**.

| Точний ID | Назва catalog.json | Попередній пакет / причина | Наступна спроба |
|---|---|---|---:|
| `treadmill-machine` | Treadmill | 030 / виклик перервано без PNG | 2 |
| `reverse-grip-lat-pulldown-cable-machine` | Reverse Grip Lat Pulldown (Cable) | 032 / HTTP 429 usage_limit_reached | 2 |
| `leg-press-horizontal-machine` | Leg Press Horizontal (Machine) | agent-02-machines-001 / HTTP 400 empty_string | 2 |

## Файли

- Пакет: `data/batches/agent-03-others-043.json`.
- Одне призначення `data/assignments/agent-03-three-continuation-2026-10-03.json`: dispatched, виконане у worker branch; три спроби збережені в новому manifest.
- Окремий resume-ledger з повними попередніми records, помилками, branch/commit/path/JSON pointers: `data/resumes/agent-03-three-continuation-2026-10-03.json`.
- Новий manifest: `data/manifests/agent-03-three-continuation-2026-10-03/generator-single.json`.
- Точна відповідність вихідним матеріалам: `data/audits/agent-03-three-continuation-2026-10-03-technique.json`.
- Перевірка ID/полів/хешів/історії/незмінності старих файлів: `data/audits/agent-03-three-continuation-2026-10-03-validation.json`.
- Готовий текст користувачу для передачі: `docs/agent-03-three-continuation-2026-10-03-message.md`.

## Продовження й один виконавець

Це три продовження, а не три нові вправи. На початку continuation для кожного ID збережено попередній attempt=1 і заплановано attempt=2. Після одного виклику на ID manifest показує total attempts=2, attempts_in_this_continuation=1 та next_attempt_number=3. Старі 030, 032, agent-02-machines-001, їхні manifests, загальна черга та shared progress залишені незмінними.

Treadmill і reverse-grip pulldown продовжені тим самим agent-08; невдалий leg press передано від agent-02 лише для маршруту 043. Після dispatch старі маршрути для цих точних ID більше не запускаються; їхні записи й помилки не змінені. Пакет не виконувався до явного повідомлення користувача про dispatch, зафіксованого нижче.

Історична інструкція agent-02 "один виклик, без retry" не дозволяла автоматичного повтору. Новий текст передачі користувачем є окремим дорученням на одну наступну спробу; не застосовуй його до решти чужого пакета. За нової спроби/активного виклику поза цим ledger пропусти ID й повідом, не призначай ще один виклик навмання.

## Джерела й конкретні сцени

Єдине джерело ID, назв, англійських description/instructions/form_cues/common_mistakes/safety_note, обладнання та м’язів — точний запис `data/exercises/catalog.json`. SHA256 каталогу: `a7cd78ba174d7277b4acaf95bd46c8a2774698d60a59cb2df6737fa2c7843989`. Збережено 451 ID і 4448 мовних блоків.

- Treadmill: саме ходьба на полотні, одна фаза з передньою п’ятою та задньою передньою частиною стопи на полотні; корпус вертикальний, руки вільні, safety clip на поясі шортів. Вихідний dataset 3666 та той самий catalog ID підтверджують ходьбу, не біг.
- Reverse-grip pulldown: сидячи, стопи на підлозі, супінований хват трохи ширше плечей, один гриф з’єднаний з верхнім кабелем; нижня фаза перед верхом грудей. Точні instructions та bound dataset 0245 підтверджують хват і напрямок, не лише назву/ID.
- Horizontal leg press: сидіння й спинка підтримують таз і поперек; обидві повні стопи на вертикальній платформі на ширині плечей; платформа рухається горизонтально, коліна не блокуються. Запис authored, dataset_id=null — іншої вправи не підставлено. Стандартна сумісна конструкція з нерухомим сидінням і горизонтальними напрямними, пасивними side grips і safety stops є вибором для ілюстрації, а не твердженням про виробника чи модель. Навантаження/бренд не вигадані.

Старі generic слова про band/machine у description pulldown не змінюють чіткі same-ID cable instructions. Каталог не виправляли. Зовнішні manufacturer URL та незалежне підтвердження моделі не заявлені. Поля source_english збережені дослівно; генерується selected_render_scene відповідного ID.

## Еталон і стиль

Еталон `assets/exercises/biceps-curl-dumbbell.png`, SHA256 `52fef743ba2d7689aa81a8b995df3c6715cbb5d04c4bd688af4ca57b2d20057f`. Роль — тільки зовнішність/пропорції/матеріали/деталізація; поза, обладнання та м’язи визначені точним ID.

Основний стиль `docs/exercise-image-style.md` v1: одна непрозора сріблясто-сіра атлетична модель без волосся, чорні шорти, босоніж; одна фаза, повне тіло й потрібне обладнання без обрізання, PNG 1024×1024 з фактично прозорим фоном. Конкретний primary — #F26445; тільки записані secondary — той самий колір на 40–50% інтенсивності.

Для treadmill `v1-neutral-primary-2026-10-02`, файл `docs/exercise-image-style-neutral-primary.md`: primary=cardio, secondary=[] → **жодної підсвітки**. Pulldown: lats, secondary=[upper_back,biceps]. Leg press: quadriceps, secondary=[hamstrings,glutes]. Не додавати м’язи з зовнішніх джерел або еталона.

## Виконання без повторів

1. Продовж наявну хмарну гілку worker, не reset/recreate. З коміту завдань скопіюй тільки нові packet/registry/resume/evidence й новий manifest, якщо його ще не почато. Не checkout всю чергу, каталог, старі manifests або весь .gitignore. Додай лише три точні allowlist-рядки нових PNG; інші правила збережи.
2. Перед КОЖНИМ викликом fetch/read актуальні доступні heads, реальні PNG, actual result/review manifests, включно з `data/batches/*-manifest.json`, і свої локальні файли. Будь-яке approved/accepted захищає весь ID; PNG з будь-яким review, включно з pending, означає skip. Запиши branch/commit/path і причину. Незбережені чужі локальні результати можуть бути недоступні; новий активний виклик/неврахований attempt — skip і report.
3. Зістав exact catalog ID, усі вихідні поля й catalog SHA256; переконайся, що generation_prompt є непорожнім string і його SHA256 правильний. Передай інструменту саме повний exercises[].generation_prompt, а не шлях, metadata чи порожній рядок. Використовуй тільки вбудований image_gen, один виклик на нову спробу, без auto-retry. Якщо реальна історія вже змінилася, запланований attempt-2 не повторювати.
4. Зберігай PNG у `/workspace/exercise-image-results/agent-03-three-continuation-2026-10-03/generator-single/agent-03-others-043/<exercise_id>/attempt-2.png`, Git-копію у `assets/exercises/pending/agent-03-three-continuation-2026-10-03/generator-single/agent-03-others-043/<exercise_id>/attempt-2.png`. Для кожного ID точні шляхи містяться в пакеті.
5. Оновлюй тільки новий manifest після кожної вправи: фактичний attempt, prompt/hash, errors, file path/hash та файлові dimensions/реальний alpha. Старі attempts/помилки залишаються. До PNG review=null; після PNG **pending** до явного рішення користувача. agent_visual_review=not_performed, без візуального QA/автоматичних корекцій. Початий manifest ніколи не перезаписувати initial template.
6. Після пакета commit/push своєї гілки й перевір віддалені файли. При першій quota/rate-limit помилці збережи failure і checkpoint, commit/push та STOP без повтору/іншого API. Після 043 STOP. Supabase, каталог/переклади, чужий shared progress і схвалені PNG не змінювати.

## Перевірка підготовки

Перевірено скриптом `scripts/prepare_agent03_three_continuation.py`: 3 точні унікальні ID, exact source fields, catalog/reference/style/prompt hashes, усі старі фактичні records/помилки, наступні attempt-2, наявні PNG/схвалення й відсутність НЕПОВ’ЯЗАНОГО нового призначення. Повтори цих ID у 030/032/agent-02 є явно дозволеними посиланнями продовження й не означають три незалежні генерації.

Скрипт `--fetch` перевіряє підготовчу гілку agent-03 до початку виконання; не запускай його як mutating validator на робочій гілці генератора й не перезаписуй підготовчий audit. Перевірки перед кожним викликом виконуються read-only на worker.
## User dispatch received — 2026-10-03T19:21:47Z

The user dispatched this continuation to the existing single worker. Generation may proceed only for the three listed IDs, in package order. The former routes in packages 030, 032, and agent-02-machines-001 are retired for these exact IDs; their source records and error histories remain unchanged. No parallel or replacement route is active.

## Execution results — package 043 completed

Generation used one embedded `image_gen.imagegen` call per exact ID; attempt 2 was consumed for each. User review remains pending for all three. No visual QA, resizing or automatic retries were performed. The initial attempt-2 output for treadmill was recovered from the platform's cloud generated-images directory and copied unchanged; no extra generator call was made.

| Exercise ID | Attempt | Technical check | Dimensions / alpha | user_review | SHA256 | Git PNG |
|---|---:|---|---|---|---|---|
| `treadmill-machine` | 2 | failed | [1254, 1254] RGBA; zero-alpha 1043907; corners [0, 0, 0, 0] | pending | `25726ee9ee5aa628e91d88ddc68cc56f6a5b08bb7cc06b78b77df436a52855ab` | `assets/exercises/pending/agent-03-three-continuation-2026-10-03/generator-single/agent-03-others-043/treadmill-machine/attempt-2.png` |
| `reverse-grip-lat-pulldown-cable-machine` | 2 | failed | [1254, 1254] RGBA; zero-alpha 1044965; corners [0, 0, 0, 0] | pending | `99dbd2512372916b3ffb9aa82afaa78a97aece09e7342c171e3a94c840933cab` | `assets/exercises/pending/agent-03-three-continuation-2026-10-03/generator-single/agent-03-others-043/reverse-grip-lat-pulldown-cable-machine/attempt-2.png` |
| `leg-press-horizontal-machine` | 2 | failed | [1254, 1254] RGBA; zero-alpha 840145; corners [0, 0, 0, 0] | pending | `fad59caf27ae38ba25cbe54ddfc369ab3288794f2e5bee5c4b14771b96bdf9aa` | `assets/exercises/pending/agent-03-three-continuation-2026-10-03/generator-single/agent-03-others-043/leg-press-horizontal-machine/attempt-2.png` |

All three returned images are valid transparent RGBA PNG files, but imagegen returned 1254x1254 for each instead of 1024x1024. This is recorded as a technical failure; the image bytes were left unchanged. Earlier attempt-1 failures and their full records remain in the resume ledger and preserved records. No old assignments, manifests, shared progress, approved PNGs, catalog, translations, work branch or Supabase were changed.
