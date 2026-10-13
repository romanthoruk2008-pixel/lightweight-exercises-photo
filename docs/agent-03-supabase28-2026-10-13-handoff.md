# 28 нових вправ — передача генераторам

Підготовча гілка: `agent-03-inventory-2026-10-01`. Незмінний commit завдань див. у `data/assignments/agent-03-supabase28-2026-10-13-publication.json` після публікації.

Усі 28 точних ID із нового Supabase export мають повний англійський опис, instructions, cues, mistakes, safety note та м’язи. Prompts підготовлені; зображення не генерувалися. Інших перекладів у цих нових записах поки немає.

Історичний catalog.json 451/4448 не змінений. Доповнення з 28 ID збережене байт у байт окремо: `data/exercises/supabase-additions-2026-10-13.json`; SHA256 `907950559a5bf4be84a791deb73fcd03d502a48ec8b936296df8a3e42651bf0f`; джерельний commit `f64538a37d63f7512527ab2a57cb195645a4a354`, гілка `agent-04-supabase-integration`.

| Пакет | Стан | Кількість | Точний файл | Manifest |
|---|---|---:|---|---|
| agent-03-others-044 | ready | 10 | `data/batches/agent-03-others-044.json` | `data/manifests/agent-03-supabase28-2026-10-13/agent-03-others-044.json` |
| agent-03-others-045 | ready | 10 | `data/batches/agent-03-others-045.json` | `data/manifests/agent-03-supabase28-2026-10-13/agent-03-others-045.json` |
| agent-03-others-046 | ready | 8 | `data/batches/agent-03-others-046.json` | `data/manifests/agent-03-supabase28-2026-10-13/agent-03-others-046.json` |

## Вправи та підсвітка

| Пакет / № | exercise_id | Назва | Основні | Допоміжні |
|---|---|---|---|---|
| 044 / 1 | `archer-pushup` | Archer Push Up | chest | triceps, shoulders |
| 044 / 2 | `bulgarian-split-squat-body-weight` | Bulgarian Split Squat (Bodyweight) | quadriceps | glutes, hamstrings |
| 044 / 3 | `crow-pose` | Crow Pose | shoulders | triceps, abdominals |
| 044 / 4 | `hollow-body-hold` | Hollow Body Hold | abdominals | — |
| 044 / 5 | `pseudo-planche-lean` | Pseudo Planche Lean | shoulders | chest, abdominals |
| 044 / 6 | `pseudo-planche-pushup` | Pseudo Planche Push Up | chest | shoulders, triceps |
| 044 / 7 | `shrimp-squat` | Shrimp Squat | quadriceps | glutes |
| 044 / 8 | `single-leg-romanian-deadlift-body-weight` | Single Leg Romanian Deadlift (Bodyweight) | hamstrings | glutes, lower_back |
| 044 / 9 | `pike-pushup-feet-elevated` | Pike Pushup (Feet Elevated) | shoulders | triceps, chest |
| 044 / 10 | `handstand-hold-chest-to-wall` | Handstand Hold (Chest to Wall) | shoulders | triceps, abdominals |
| 045 / 1 | `dragon-flag-negative` | Dragon Flag (Negative) | abdominals | — |
| 045 / 2 | `handstand-pushup-negative` | Handstand Push Up (Negative) | shoulders | triceps |
| 045 / 3 | `l-sit-hold-tuck` | L-Sit Hold (Tuck) | abdominals | triceps |
| 045 / 4 | `parallel-bar-support-hold` | Parallel Bar Support Hold | triceps | chest, shoulders |
| 045 / 5 | `flexed-arm-hang` | Flexed-Arm Hang | lats | upper_back, biceps, forearms |
| 045 / 6 | `front-lever-hold-tuck` | Front Lever Hold (Tuck) | lats | abdominals, upper_back |
| 045 / 7 | `front-lever-hold-advanced-tuck` | Front Lever Hold (Advanced Tuck) | lats | abdominals, upper_back |
| 045 / 8 | `front-lever-hold-one-leg` | Front Lever Hold (One Leg) | lats | abdominals, upper_back |
| 045 / 9 | `front-lever-hold-straddle` | Front Lever Hold (Straddle) | lats | abdominals, upper_back |
| 045 / 10 | `skin-the-cat` | Skin the Cat | lats | shoulders, abdominals |
| 046 / 1 | `archer-pullup-machine` | Archer Pull Up | lats | upper_back, biceps |
| 046 / 2 | `chest-to-bar-pullup-machine` | Chest to Bar Pull Up | lats | upper_back, biceps, forearms |
| 046 / 3 | `explosive-pullup-machine` | Explosive Pull Up | lats | upper_back, biceps |
| 046 / 4 | `inverted-row-feet-elevated-machine` | Inverted Row (Feet Elevated) | upper_back | lats, biceps |
| 046 / 5 | `muscle-up-band-resistance-band` | Muscle Up (Band) | full_body | lats, chest, triceps |
| 046 / 6 | `muscle-up-negative-machine` | Muscle Up (Negative) | full_body | lats, chest, triceps |
| 046 / 7 | `straight-bar-dip-machine` | Straight Bar Dip | chest | triceps, shoulders |
| 046 / 8 | `triceps-dip-negative-machine` | Triceps Dip (Negative) | triceps | chest, shoulders |

## Стиль, техніка та обладнання

Еталон: `assets/exercises/biceps-curl-dumbbell.png`, SHA256 `52fef743ba2d7689aa81a8b995df3c6715cbb5d04c4bd688af4ca57b2d20057f`. Тільки зовнішність, пропорції та матеріали. Поза, опори й м’язи визначаються exact-ID English та `scene` кожного запису.
Стиль: `docs/exercise-image-style.md` (v1). Для двох muscle-up із primary=full_body додатково `docs/exercise-image-style-neutral-primary.md`: тіло нейтральне, тільки записані lats/chest/triceps підсвічені #F26445 на 40–50%; не підсвічувати все тіло. Для інших ID — конкретний primary повною інтенсивністю, exact secondary 40–50%.
Категорія machine у нових записах не означає силовий тренажер: exact-ID instructions описують статичний турнік/бруси. Так само none не скасовує явно зазначеної лави, ящика, стіни, кілець або турніка. Перелік опор і обладнання збережений у кожному scene.
Вибір сторони, ракурсу, однієї фази та дозволеної альтернативи (floor/parallettes, bar/rings, bench/box, foot/knee in band) — вибір ілюстрації, а не підміна техніки чи схвалення PNG.
Для advanced-tuck фронт-левера джерело явно задає thighs in line with torso + bent knees. Prompt відтворює саме цю геометрію, а не довільний інший tuck за схожою назвою. Назва/вихідні поля не виправлялися.
Зовнішнє доповнення полів не знадобилося: усі 28 записів заповнені. Це не твердження про незалежну перевірку біомеханіки або якості вихідних описів виробником.

## Правила виконання

Користувач передає один або кілька пакетів конкретному генератору. Не запускати один пакет двома агентами. Перед першим викликом записати свого власника в окремому registry своєї гілки. Поточні завдання інших агентів не забирати.
Перед КОЖНОЮ генерацією отримати актуальні доступні гілки й звірити exact ID з реальними PNG, approval, manifests, assignments та локальними результатами. Будь-який PNG, включно з pending, або чужий active owner — пропустити ID й повідомити. Невдалий виклик без PNG зберігається в цьому ж пакеті; не створювати дубль.
Використовувати непорожній `generation_prompt`, перевірений за `prompt_sha256`; еталон передавати як reference лише зовнішності. Одна людина, одна фаза, 1024×1024 transparent PNG. Не запускати альтернативний API.
Точні результатні шляхи — `planned_png_path` та `planned_git_png_path`. Окремий manifest для кожного пакета вказано вище. Не перезаписувати вже початий manifest шаблоном; зберігати всі помилки, фактичні спроби й path/SHA256.
Новий PNG має `user_review=pending` до явного рішення користувача, `agent_visual_review=not_performed`. Лише файлові перевірки, без повторного візуального QA й автоматичних корекцій. Підготовка prompt не є спробою генерації.
Після кожного пакета зберегти manifest/результати, закомітити й запушити тільки свою виконавчу гілку, перевірити віддалені файли. За першої quota/rate-limit помилки зберегти checkpoint та зупинитися без повторних викликів.
Не змінювати catalog.json, export, переклади, shared progress, схвалення чи Supabase. Нові pending PNG у Git дозволені лише у точних шляхах цього пакета. Якщо вони ignored, у своїй виконавчій гілці додати тільки вузькі .gitignore винятки для exact planned_git_png_path свого пакета; не дозволяти глобально всі PNG і не force-add сторонні медіа. Після призначених пакетів зупинитися.

## Перевірка та межі

`python3 -B scripts/prepare_agent03_supabase28.py --check` перевіряє exact-ID поля, повні source records і hashes, відсутність повторів/перетинів, scene/prompt, source/style/reference/output binding, незмінність старих файлів. Результат: `data/audits/agent-03-supabase28-2026-10-13-validation.json`.
Preflight охоплює pushed файли актуальних доступних гілок. Незапушені результати/призначення чужих хмарних задач можуть бути недоступні. Supabase напряму не запитувався; використано hash-bound export імпортера. Немає нових схвалень або викликів генератора.
