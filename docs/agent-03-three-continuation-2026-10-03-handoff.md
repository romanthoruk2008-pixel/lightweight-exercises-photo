# Пакет 043: три явні продовження без PNG

Джерельна гілка: `agent-03-inventory-2026-10-01`. Незмінний коміт завдань: `8d17e7a233d7bcd3055c78dd691090cce01a0d5b`.
Один існуючий виконавець: `agent-08-generator-single-2026-10-03`, після всіх уже взятих завдань, включно з 041–042. Статус: **ready**, 3 вправи; передача користувачем ще не виконана підготовчим агентом. Генерацій під час підготовки: **0**.

| Точний ID | Назва catalog.json | Попередній пакет / причина | Наступна спроба |
|---|---|---|---:|
| `treadmill-machine` | Treadmill | 030 / виклик перервано без PNG | 2 |
| `reverse-grip-lat-pulldown-cable-machine` | Reverse Grip Lat Pulldown (Cable) | 032 / HTTP 429 usage_limit_reached | 2 |
| `leg-press-horizontal-machine` | Leg Press Horizontal (Machine) | agent-02-machines-001 / HTTP 400 empty_string | 2 |

## Файли

- Пакет: `data/batches/agent-03-others-043.json`.
- Одне призначення, ready_for_user_dispatch: `data/assignments/agent-03-three-continuation-2026-10-03.json`.
- Окремий resume-ledger з повними попередніми records, помилками, branch/commit/path/JSON pointers: `data/resumes/agent-03-three-continuation-2026-10-03.json`.
- Новий manifest: `data/manifests/agent-03-three-continuation-2026-10-03/generator-single.json`.
- Точна відповідність вихідним матеріалам: `data/audits/agent-03-three-continuation-2026-10-03-technique.json`.
- Перевірка ID/полів/хешів/історії/незмінності старих файлів: `data/audits/agent-03-three-continuation-2026-10-03-validation.json`.
- Готовий текст користувачу для передачі: `docs/agent-03-three-continuation-2026-10-03-message.md`.

## Продовження й один виконавець

Це три продовження, а не три нові вправи. Початкові ID і всі записи attempts=1 збережені. У новому manifest: attempts=1 успадковано, attempts_in_this_continuation=0, next_attempt_number=2. Старі 030, 032, agent-02-machines-001, їхні manifests, загальна черга та shared progress залишені незмінними.

Treadmill і reverse-grip pulldown залишаються тому самому agent-08. Для leg press поточне прохання користувача готує передачу невдалої задачі agent-02 цьому одному виконавцю. Передача користувачем активує тільки маршрут 043; у новому ledger зафіксуй, що відповідні старі маршрути більше не виконуються. Не запускати ID одночасно з двох пакетів або гілок. Пакет не вважається розісланим і не запускається підготовчим агентом.

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
