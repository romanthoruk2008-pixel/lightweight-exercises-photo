# Генератор B: продовження 009 і нові перевірені записи

Джерельна гілка `agent-03-inventory-2026-10-01`, commit `d2e58cdaae2502f54022fe32bc37b526baa5a1de`.
Призначення `data/assignments/agent-03-generator-b-continuation-2026-10-02.json`; 26 вправ (9 продовжень + 17 нових prompts).
Власна нова гілка генератора `agent-07-generator-b-2026-10-02` від джерельного commit. Поточні чужі задачі/гілки не забирати. A: 12 вправ 024–025 незмінні.

## `agent-03-others-009` — 9, `ready`

Точний файл: `data/resumes/agent-03-others-009-generator-b.json`. Порядок — як у registry.

- `hanging-knee-raise` — Hanging Knee Raise
- `hanging-leg-raise` — Hanging Leg Raise
- `jack-knife-suspension` — Jack Knife (Suspension)
- `kipping-pullup-machine` — Kipping Pull Up
- `knee-raise-parallel-bars-machine` — Knee Raise Parallel Bars
- `kneeling-pulldown-band-machine` — Kneeling Pulldown (band)
- `lat-pulldown-band-resistance-band` — Lat Pulldown (Band)
- `lateral-band-walks-resistance-band` — Lateral Band Walks
- `lateral-raise-band-resistance-band` — Lateral Raise (Band)

## `agent-03-others-026` — 7, `ready`

Точний файл: `data/batches/agent-03-others-026.json`. Порядок — як у registry.

- `downward-dog` — Downward Dog
- `bear-crawl` — Bear Crawl
- `jumping-jack` — Jumping Jack
- `high-knees` — High Knees
- `mountain-climber` — Mountain Climber
- `diamond-pushup` — Diamond Push Up
- `chest-fly-dumbbell` — Chest Fly (Dumbbell)

## `agent-03-others-027` — 10, `ready`

Точний файл: `data/batches/agent-03-others-027.json`. Порядок — як у registry.

- `hiit` — HIIT
- `pilates` — Pilates
- `stretching` — Stretching
- `yoga` — Yoga
- `walking` — Walking
- `hiking` — Hiking
- `snowboarding` — Snowboarding
- `cross-body-hammer-curl-dumbbell` — Cross Body Hammer Curl
- `concentration-curl-dumbbell` — Concentration Curl
- `clean-barbell` — Clean

009 — продовження того самого пакета, не нова генерація тих самих ID. Читати sidecar, НЕ весь історичний 009: dead-hang виключено через наявний PNG. Оригінальний 009 та всі попередні помилки/спроби зберегти. hanging-knee-raise починає з attempt-3, решта восьми — attempt-1. Ці номера нижня межа: перед викликом врахувати новішу опубліковану історію.

026: сім із перших восьми нічних записів. Waiter Curl лишається blocked: два джерела повторюють звичайний двогантельний curl, а не підтверджують його відмінний варіант.
027: сім затверджених загальних сцен/взуття + Cross-body Hammer Curl, Concentration Curl та Clean. Це джерельно підтверджені технічні рішення або явно названі вибори ілюстрації; не автоматичне схвалення PNG.

Еталон: `assets/exercises/biceps-curl-dumbbell.png`, SHA256 `52fef743ba2d7689aa81a8b995df3c6715cbb5d04c4bd688af4ca57b2d20057f`. Лише зовнішність/матеріали; не копіювати позу, обладнання або підсвітку.

Файли стилю: `docs/exercise-image-style.md`, `docs/exercise-image-style-neutral-primary.md`, `docs/exercise-image-style-illustration-footwear.md`. Дотримуватись конкретного style_version кожного рядка: v1, v1-neutral-primary-2026-10-02 або v1-neutral-primary-footwear-2026-10-02.
Broad primary full_body/cardio/other — сріблясто-сірий нейтральний; лише явно зазначені secondary #F26445 на 40–50%. Порожній secondary — без підсвітки. Взуття дозволено тільки для walking/hiking/snowboarding.

Локальна окрема папка: `/workspace/exercise-image-results/agent-03-generator-b-continuation-2026-10-02/generator-b/<batch_id>/<exercise_id>/attempt-N.png`.
Git PNG: `assets/exercises/pending/agent-03-generator-b-continuation-2026-10-02/generator-b/<batch_id>/<exercise_id>/attempt-N.png`.
Власний manifest: `data/manifests/agent-03-generator-b-continuation-2026-10-02/generator-b.json`. Дописувати історію, не скидати лічильники й не стирати старі помилки. Source-task path, prompt/catalog SHA256, фактичний PNG path/SHA256, час, виклик/помилку зберігати для exact ID.

Перед КОЖНИМ викликом fetch усі доступні гілки; звірити PNG, manifests і активні призначення. Будь-який PNG, зокрема pending/rejected — skip без повторної генерації. Нове стороннє призначення/спроба — conflict і skip; цей registry дозволяє тільки явно описане продовження старого 009. Незапушені файли інших хмарних задач можуть бути невидимі.
Генерація тільки у хмарі вбудованим imagegen; не зовнішні paid API. user_review=pending для кожного нового PNG до явного рішення користувача. Агентський технічний QA не є схваленням.
Після кожного пакета зберегти PNG та manifest, commit і push власної гілки, перевірити віддалені файли. При quota/usage_limit_reached/HTTP429 — зберегти помилку й ЗУПИНИТИСЯ без повторних викликів; ID залишаються в поточному пакеті. Інші помилки записати, без автоматичних повторів.
Каталог, усі переклади, work, shared progress, наявні PNG/схвалення, чужі результати й Supabase не змінювати. Тренажери/троси/Сміт — наступний етап; жодних 114 завдань тут немає.

Технічні джерела: `data/audits/agent-03-generator-b-continuation-2026-10-02-technique.json`. Помилки вихідних описів: `data/audits/agent-03-source-description-errors-2026-10-02.json`. Решта 20 blocked: `data/queues/agent-03-generator-b-continuation-2026-10-02-blocked.json`. Не вгадувати їхню техніку й не включати до цього доручення.
