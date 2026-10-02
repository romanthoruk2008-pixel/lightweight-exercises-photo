# Передача: generator-a

Джерело: `agent-03-inventory-2026-10-01`, commit `4ed2bafbf0cf690458d25a896275647d8fdf2d20`.
Файл призначень: `data/assignments/agent-03-next50-2026-10-02.json`. Статус `ready`; 12 вправ.

```text
Порядок пакетів: agent-03-others-024, agent-03-others-025
```

Пакет `agent-03-others-024` — `data/batches/agent-03-others-024.json`:

- `front-raise-band-resistance-band` — Front Raise (Band)
- `front-raise-suspension` — Front Raise (Suspension)
- `front-squat-barbell` — Front Squat
- `hack-squat-barbell` — Hack Squat
- `jump-squat` — Jump Squat
- `jumping-lunge` — Jumping Lunge
- `leg-raise-parallel-bars-machine` — Leg Raise Parallel Bars
- `negative-pullup` — Negative Pull Up
- `pullup-weighted-machine` — Pull Up (Weighted)
- `ring-dips` — Ring Dips

Пакет `agent-03-others-025` — `data/batches/agent-03-others-025.json`:

- `ring-pullup` — Ring Pull Up
- `squat-band-resistance-band` — Squat (Band)

Окрема гілка: `agent-06-generator-a-2026-10-02`; почати саме від source commit, не змінювати поточні гілки інших агентів.
Локальні PNG: `/workspace/exercise-image-results/agent-03-next50-2026-10-02/generator-a/<batch_id>/<exercise_id>/attempt-1.png`.
PNG у Git: `assets/exercises/pending/agent-03-next50-2026-10-02/generator-a/<batch_id>/<exercise_id>/attempt-1.png`.
Власний manifest: `data/manifests/agent-03-next50-2026-10-02/generator-a.json`; shared progress не змінювати.

Еталон: `assets/exercises/biceps-curl-dumbbell.png`; SHA256 `52fef743ba2d7689aa81a8b995df3c6715cbb5d04c4bd688af4ca57b2d20057f`. Використовувати лише зовнішність/пропорції/матеріали; поза, обладнання та м’язи — exact-ID prompt.
Стиль цих конкретних primary — `v1`, файл `docs/exercise-image-style.md`, SHA256 `8956307274990bdefd11bcc18e6d6deb2aed35580b5c2ea3ac0061dee708e578`. Загальне затверджене доповнення `docs/exercise-image-style-neutral-primary.md` прочитати також; broad-primary правило не потрібно для цих 12 concrete-primary записів. Не змінювати жоден стиль.

Старі 017–018 є незмінними історичними підготовчими планами. Лише зазначені в assignments ID переадресовано на 024–025; не запускати для них старі пакети паралельно. 009 і чужі черги/завдання не забирати.

Перед КОЖНИМ викликом fetch усі доступні remote heads і звірити actual PNG paths, manifests/queues/assignments. За наявного PNG будь-якого review — skip без повтору. Якщо інший агент уже має active assignment/call/PNG — skip/conflict у власному manifest, без переназначення. Непушені дані інших задач можуть бути невидимі.
Для будь-якого майбутнього результату user_review=pending до явного рішення користувача; agent_visual_review=not_performed. Технічні dimension/alpha/path/hash перевірки записувати окремо; не ресайзити й не виправляти PNG автоматично.
Один виклик на ID цієї передачі. При quota/usage_limit_reached/HTTP429 зупинити ВСІ наступні виклики одразу, записати помилку/resume_at та push checkpoint без повторів. Не переходити до решти ID чи іншого пакета після quota. Failed/noPNG — продовження цього самого batch/manifest лише за наступним прямим дорученням, не нове завдання.
Після кожного пакета зберегти незмінні фактичні PNG, ID/prompt/style/reference/catalog hashes, actual attempt/path/PNG SHA256 у своєму manifest; commit і push лише власну нову worker-гілку, потім fetch/перевірити віддалені файли. Pending PNG paths уже мають вузькі .gitignore винятки. Не пушити work або підготовчу гілку. Supabase, catalogue, shared progress, чужі manifests не змінювати.

Лише вбудований image_gen.imagegen; не платний API. Цей файл не запускає генерацію: почати лише після отримання користувацького повідомлення на виконання.
