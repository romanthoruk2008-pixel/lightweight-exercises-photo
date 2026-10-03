# Перевірені prompts 037–040 і захист схвалених PNG

**34 нові вправи без PNG**, ready, для одного existing генератора `agent-08-generator-single-2026-10-03`, після його чинних 034–036. Викликів генератора підготовником: 0.
Джерельна гілка: `agent-03-inventory-2026-10-01`. Незмінний коміт завдань: `de7dfb901c4c23072c5b11d3fee6cde7364eeb6a`.
Призначення: `data/assignments/agent-03-common-variants-2026-10-03.json`. Чинні чужі завдання, пакети 001–036, PNG та їхня історія незмінні.

## Пакети

### agent-03-others-037 — ready, 10

Файл: `data/batches/agent-03-others-037.json`.

| exercise_id | Точна назва каталогу |
| --- | --- |
| `bicycle-crunch` | Bicycle Crunch |
| `bicycle-crunch-raised-legs` | Bicycle Crunch Raised Legs |
| `pushup-weighted` | Push Up (Weighted) |
| `side-bend-dumbbell` | Side Bend (Dumbbell) |
| `single-arm-landmine-press-barbell` | Single Arm Landmine Press (Barbell) |
| `nordic-hamstrings-curls` | Nordic Hamstrings Curls |
| `muscle-up-machine` | Muscle Up |
| `back-extension-weighted-hyperextension-machine` | Back Extension (Weighted Hyperextension) |
| `butterfly-pec-deck-machine` | Butterfly (Pec Deck) |
| `calf-extension-machine` | Calf Extension (Machine) |

### agent-03-others-038 — ready, 10

Файл: `data/batches/agent-03-others-038.json`.

| exercise_id | Точна назва каталогу |
| --- | --- |
| `calf-press-machine` | Calf Press (Machine) |
| `chest-fly-machine` | Chest Fly (Machine) |
| `crunch-machine` | Crunch (Machine) |
| `glute-ham-raise-machine` | Glute Ham Raise |
| `glute-kickback-machine` | Glute Kickback (Machine) |
| `hack-squat-machine` | Hack Squat (Machine) |
| `hip-abduction-machine` | Hip Abduction (Machine) |
| `pullup-assisted-machine` | Pull Up (Assisted) |
| `reverse-hyperextension-machine` | Reverse Hyperextension |
| `seated-calf-raise-machine` | Seated Calf Raise |

### agent-03-others-039 — ready, 10

Файл: `data/batches/agent-03-others-039.json`.

| exercise_id | Точна назва каталогу |
| --- | --- |
| `seated-leg-curl-machine` | Seated Leg Curl (Machine) |
| `reverse-curl-cable-machine` | Reverse Curl (Cable) |
| `standing-cable-glute-kickbacks-machine` | Standing Cable Glute Kickbacks |
| `cable-twist-down-to-up-machine` | Cable Twist (Down to up) |
| `cable-twist-up-to-down-machine` | Cable Twist (Up to down) |
| `hip-adduction-cable-machine` | Hip Adduction (Cable) |
| `hip-abduction-cable-machine` | Hip Abduction (Cable) |
| `single-arm-lateral-raise-cable-machine` | Single Arm Lateral Raise (Cable) |
| `behind-the-back-curl-cable-machine` | Behind the Back Curl (Cable) |
| `overhead-curl-cable-machine` | Overhead Curl (Cable) |

### agent-03-others-040 — ready, 4

Файл: `data/batches/agent-03-others-040.json`.

| exercise_id | Точна назва каталогу |
| --- | --- |
| `single-arm-triceps-pushdown-cable-machine` | Single Arm Triceps Pushdown (Cable) |
| `decline-bench-press-machine` | Decline Bench Press (Machine) |
| `chest-dip-assisted-machine` | Chest Dip (Assisted) |
| `ski-erg-machine` | Ski Erg |

## Техніка та джерела

Кожне завдання містить повний English саме свого ID (description, instructions, cues, mistakes, safety), equipment, primary/secondary, SHA256 каталогу/запису/English/prompt, конкретні позу, фазу, хват, опори, траєкторію, ракурс та planned cloud/Git PNG paths. Каталог — єдине джерело ідентичності та м’язів. Його 451 ID і 4448 мовних блоків незмінні; SHA256 `a7cd78ba174d7277b4acaf95bd46c8a2774698d60a59cb2df6737fa2c7843989`.
Рішення та 30 першоджерел з URL/короткими цитатами/checksums: `data/technique-decisions/agent-03-common-variants-2026-10-03.json`. Exact dataset binding і фактичні вихідні steps: `data/audits/agent-03-common-variants-2026-10-03-technique.json`. Неузгоджені вихідні поля збережені окремо: `data/audits/agent-03-common-variants-2026-10-03-source-notes.json`.
Відділено підтвердження техніки, дозволений поширений варіант і вибір сцени. Загальний дозвіл користувача обирати перевірений поширений варіант не є схваленням PNG або індивідуальним підтвердженням кожної вправи. Для reverse-curl-cable-machine джерело з barbell підтверджує лише pronated grip, а cable/straight bar походять із exact English. Для single-arm-triceps-pushdown-cable-machine дворуке джерело підтверджує тільки elbow-extension motion; один handle/high pulley походять з exact English. Не підмінювати їх іншими вправами.
Bicycle crunch: неробоча нога зігнута близько 90° за прямою відповіддю користувача. Raised legs: неробоча нога випрямлена над підлогою. Pushup weighted: закріплений жилет за прямою відповіддю. Side bend нахиляється до робочої гантелі; standing one-arm landmine має split stance та вільний sleeve біля плеча. Calf extension і calf press мають різні опори: leg-press forefoot platform та seated knee pad. Reverse hyperextension використовує підтверджений supported/bodyweight варіант, без вигаданого завантаженого ankle linkage. Decline machine з двома plate-loaded важелями — попередній вибір користувача. Raw каталог не виправляється.

## Еталон і чинний стиль

Еталон зовнішності/матеріалів: `assets/exercises/biceps-curl-dumbbell.png`, SHA256 `52fef743ba2d7689aa81a8b995df3c6715cbb5d04c4bd688af4ca57b2d20057f`. Відкрити перед першим викликом. Позу/обладнання/підсвітку еталона не копіювати.
Основний стиль: `docs/exercise-image-style.md` (v1); approved neutral-primary: `docs/exercise-image-style-neutral-primary.md` (v1-neutral-primary-2026-10-02), рішення `data/style-decisions/agent-03-neutral-primary-approved.json`. Жилет лише для pushup-weighted: `docs/exercise-image-style-weighted-vest.md` (v1-weighted-vest-2026-10-03). Hash усіх застосовних файлів є у кожному task.
Одна сріблясто-сіра лиса анатомічна чоловіча модель, чорні шорти, barefoot, одна фаза, прозорий 1024×1024 PNG, весь figure/equipment. Конкретний primary: #F26445, лише catalog secondary точного ID: 40–50%. Generic full_body/cardio/other: без primary підсвітки. **muscle-up-machine (full_body) та ski-erg-machine (cardio) мають порожній secondary, тому обидва тіла повністю нейтральні.** Opaque жилет не просвічує й не фарбується як м’язи; підсвітка тільки на видимій анатомії.

## Повторна звірка після нового push генератора

Прочитано pushed Git усіх доступних гілок. Checkpoint генератора: `b146f94bf41bd2988b18ac9825452657aeaef9ba`; work: `b0385b7e2f3382d545a6dff5304c81ba3c771096`. На цих commits: **398 ID із PNG, 377 явно approved/accepted, 21 без явного схвалення**. Це перевірка Git-метаданих, без перегляду пікселів.
З попередньої черги переробки вилучено 9 щойно схвалених ID:

- `back-extension-hyperextension-machine`
- `chest-supported-t-bar-row-machine`
- `hip-thrust-machine`
- `iso-lateral-row-machine`
- `leg-press-machine`
- `lying-leg-curl-machine`
- `pendulum-squat-machine`
- `single-leg-press-machine`
- `squat-machine`

Додаткова звірка з імпортером виявила помилку collector: він не читав actual `data/batches/*-manifest.json`. Виправлено; ще 5 раніше схвалених ID із `data/batches/agent-03-others-023-agent-05-manifest.json` вилучені з revision queue: `swimming`, `thruster-barbell`, `thruster-kettlebell`, `wall-ball`, `warm-up`. Усі 377 захищених ID мають explicit user_review=approved/accepted.

Два нові непідтверджені PNG: `rear-delt-reverse-fly-cable-machine`, `triceps-extension-machine`. У 037–040 **0 перетинів** зі схваленнями та наявними PNG. Докази exact branch/commit/path/json_pointer: `data/audits/agent-03-common-variants-2026-10-03-approval-recheck.json` і `data/queues/agent-03-common-variants-2026-10-03-unconfirmed-rework.json`.
Черга переробки містить **21 planning-only** кандидатів `awaiting_prompt_revalidation`: це не нове призначення й не готові revision prompts. Старі PNG/attempts/reviews збережені; їх не відхиляли від імені користувача. Потрібна окрема перевірка exact-ID prompts, завершення/узгодження чинних власних завдань і fresh approval gate перед майбутнім призначенням. Any approved/accepted evidence захищає весь ID, навіть якщо інша копія ще pending. Відсутній approved файл не дозволяє генерувати заміну.
Числа прив’язані до checkpoint. Нові approvals після нього мають пріоритет: перед КОЖНИМ викликом повторити перевірку. Незапушені approvals/результати/активні виклики інших cloud tasks можуть бути недоступні.

## Звірка імпорту Supabase

За integration commit `742c53007eb384141f0602d516f861ec691234a4` незалежно прочитано всі completed upload records: **377 unique ID**, повний збіг зі схваленими IDs, без зайвих або пропущених. Останній importer readback 2026-10-03T13:36:34.707151+00:00 зафіксував 451 рядок, 4448 мовних блоків, 3 архівні та 377 image links. Самостійний live API read заблокований proxy CONNECT 403; Supabase ключа в доступних environment variables також не знайдено. Це перевірка pushed records імпортера, не нове читання DB нами.

Його pending scope містить 12 ID; повний Git union містить 21 = ці 12 + 9 pending із `agent-02-machines-001`. Ці 9 підтверджено actual result manifest і не оголошено схваленими/перенесеними. Докази: `data/audits/agent-03-common-variants-2026-10-03-supabase-reconciliation.json`. Supabase, integration branch і approvals не змінювалися.

## Продовження одним генератором

1. Працювати тільки у своєму cloud checkout та existing `agent-08-generator-single-2026-10-03`. Не reset/recreate гілку. Спочатку завершити чинні 034–036 або зафіксувати їхній блокер; не забирати A/B/чужі роботи. Пуш тільки worker branch.
2. Fetch доступні гілки; прочитати цей handoff з актуальної preparation branch. Із `de7dfb901c4c23072c5b11d3fee6cde7364eeb6a` перенести лише 037–040, їхній new assignment, рішення/evidence/source notes, нове доповнення жилета та new manifest `data/manifests/agent-03-common-variants-2026-10-03/generator-single.json`. Якщо цей manifest уже має спроби, не замінювати стартовим. Не копіювати поверх каталог, shared progress, стару чергу, чужі manifests або весь .gitignore.
3. Перед КОЖНИМ image_gen call перечитати актуальні manifests/approval records усіх доступних гілок, включно з actual `data/batches/*-manifest.json`, свої local outputs/history й assignment registers. Явне approved/accepted (будь-яка версія) — обов’язковий skip із джерелом, навіть якщо accepted PNG відсутній. Для цих нових missing-PNG завдань будь-який існуючий PNG точного ID, включно з pending, теж skip. Нове чуже призначення — skip. Записувати branch/commit/path/reason. Старий failed call без PNG залишається у старому пакеті, не переносити.
4. Виконати 037 → 038 → 039 → 040, тільки exact generation_prompt і його approved style/reference. Лише вбудований image_gen; одна вправа/фаза/людина. Не застосовувати загальну позу й не додавати м’язи з інтернету. Не брати 13 blocked або revision planning queue.
5. Cloud result: `/workspace/exercise-image-results/agent-03-common-variants-2026-10-03/generator-single/<batch_id>/<exercise_id>/attempt-1.png`. Git result: `assets/exercises/pending/agent-03-common-variants-2026-10-03/generator-single/<batch_id>/<exercise_id>/attempt-1.png`. У tasks точні paths. Якщо потрібен .gitignore, додати лише ці 34 точні allowlist рядки. Не перезаписувати файли; при вже використаному номері спроби звірити history й checkpoint, не робити повторний call навмання.
6. Оновлювати тільки новий власний manifest після кожної вправи: повний prompt/hash, source catalog/style/reference hashes, actual attempts/errors/history, result path/SHA256/time. До PNG user_review/result null; після PNG user_review=pending до явного рішення користувача. Agent visual review=not_performed. Лише файлові PNG/dimensions/transparency checks; без visual QA/автоматичних повторів.
7. Після кожного пакета commit/push worker branch, verify remote файли й checkpoint handoff. Каталог/переклади, shared progress, схвалення, старі PNG та Supabase не змінювати.
8. Перша quota/rate-limit помилка: записати failed call/history, push checkpoint і STOP без повторних викликів/іншого API. Недоступний image_gen — конкретний блокер. Після 040 STOP.

## Залишок технічних блокувань

**13 записів** залишилися blocked, без нових призначень. Не просимо користувача вгадувати техніку. Потрібне exact-variant першоджерело; схожа вправа або matching dataset ID не достатні. Поточний ledger: `data/queues/agent-03-common-variants-2026-10-03-blocked.json`.

| exercise_id | Конкретна причина |
| --- | --- |
| `back-extension-machine` | Catalogue hip-supported hinge versus dataset seated lumbar machine/rounded-back start: confirm actual support and moving segment. |
| `belt-squat-machine` | Hip belt is stated, but load attachment/anchor and compatible belt machine mechanism are not defined. |
| `bench-press-cable-machine` | Catalog supine flat bench between low pulleys versus original standing chest-height cable press. This is not merely a construction brand choice. |
| `press-under-barbell` | Overhead press-under receiving stance/depth unspecified: partial squat, full squat or split. Generic overhead press/clean examples do not define this drill. |
| `rear-kick-machine` | Pad-and-foot-or-ankle lever alternatives do not specify exact working contact and torso-support layout. |
| `reverse-fly-single-arm-cable-machine` | Far hand is explicitly supporting; working-hand side and clear side-on cable/support geometry need confirmation without swapping hands. |
| `seated-dip-machine` | Description pushes handles down while instructions/source lower and raise body: moving body versus moving lever conflict. |
| `seated-triceps-press-machine` | Fixed upper arms close to torso combined with forward handle press needs elbow-extension trajectory confirmation; do not substitute chest press or downward seated dip. |
| `shrug-machine` | Previously held: standing English versus seat adjustment in selected dataset does not confirm posture/contact. |
| `single-leg-standing-calf-raise-barbell` | Free bar across upper back needs both hands while safety requires a handhold/machine support; simultaneous support geometry is undefined. No substitution with Smith. |
| `single-leg-standing-calf-raise-machine` | Catalog description other foot on block versus instructions other foot clear; original dataset places Smith bar above ankles and describes bilateral rise. Incompatible support/loading geometry. |
| `squat-row-machine` | Catalog neutral rope grip with partial rise before pull versus original overhand squat row. Combined phase/grip not silently selected. |
| `waiter-curl-dumbbell` | English and selected dataset both describe an ordinary TWO-dumbbell supinated curl; no verified distinctive Waiter Curl grip/quantity. Binding and name do not confirm this variant. Do not replace it with either ordinary curl or a guessed single-dumbbell curl. |

Доступні first-party матеріали StrengthLog прочитані як текст. Повторна перевірка відкрила Concept2: manufacturer standing double-pole instructions і floor-stand specifications розблокували SkiErg, його додано в 040. ATHLEAN-X лишається proxy CONNECT 403, а Technogym повернув HTTP 403; доступна Life Fitness product page без exact technique не знімає суперечності. Загальні Catalyst home/search сторінки не прийняті як підтвердження Press Under. Доповнення allowed_domains збережено в cloud environment configuration draft; runtime застосування не стверджується. Для продовження цих джерел потрібне збереження налаштувань середовища користувачем. Масово фото/відео не завантажувалися; failed URL/search/soft-404 не прийняті як доказ.

## Перевірка підготовки

`python scripts/prepare_agent03_common_variants.py --fetch` — preparation branch, до виконання. Exact-ID source fields, hashes, source binding/quotes, selected scene, 34 unique IDs, відсутність assignment/PNG/approval перетинів, старі routes/пакети/каталог/shared progress перевіряються скриптом. Новий guard також відхиляє будь-який approved ID у revision queue. Це не worker continuation command після появи PNG.
Окремо `python scripts/audit_agent03_unconfirmed.py --fetch` читає актуальні Git approvals без зміни файлів. `--write` дозволений лише на preparation branch і оновлює тільки planning queue. Не використовувати snapshot замість per-call перевірки.
Готове повідомлення: `docs/agent-03-common-variants-2026-10-03-message.md`.
