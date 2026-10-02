Генератор B: джерело romanthoruk2008-pixel/lightweight-exercises-photo, гілка agent-03-inventory-2026-10-01, commit 4ed2bafbf0cf690458d25a896275647d8fdf2d20.

Прочитай data/assignments/agent-03-next50-2026-10-02.json і docs/agent-03-next50-2026-10-02-generator-b-handoff.md (handoff у поточній вершині підготовчої гілки; дані/пакети зафіксовані в наведеному source commit).

Твій порядок: немає. Тільки 0 ID з секції generator-b; інші завдання не забирай.

Власна гілка для цього призначення: agent-07-generator-b-2026-10-02, від наведеного source commit.

Еталон assets/exercises/biceps-curl-dumbbell.png, SHA256 52fef743ba2d7689aa81a8b995df3c6715cbb5d04c4bd688af4ca57b2d20057f — лише зовнішність і матеріали. Стиль v1: docs/exercise-image-style.md; також прочитай docs/exercise-image-style-neutral-primary.md. Техніку/обладнання/підсвітку бери з exact-ID batch prompt.

PNG: /workspace/exercise-image-results/agent-03-next50-2026-10-02/generator-b/<batch_id>/<exercise_id>/attempt-1.png; у Git assets/exercises/pending/agent-03-next50-2026-10-02/generator-b/<batch_id>/<exercise_id>/attempt-1.png. Manifest: data/manifests/agent-03-next50-2026-10-02/generator-b.json.

Перед кожним викликом fetch усі агентські гілки й work, звір PNG та призначення. Наявний PNG, включно з pending, пропускай. Історичні 017–018 для цих ID замінені 024–025 в assignments; не запускати обидві версії.

Один виклик на ID через вбудований image_gen.imagegen. user_review=pending до мого явного схвалення; agent_visual_review=not_performed. Не роби автоматичних повторів/ресайзу/корекцій.

Після кожного пакета збережи PNG і власний manifest з exact ID/path/hashes, commit/push власної гілки й перевір віддалені файли. При quota/HTTP429 одразу зупини всі подальші виклики, збережи й запуш checkpoint без повтору.

Каталог, shared progress, чужі manifests, work і підготовчу гілку не змінюй. Supabase не використовуй.

Зараз призначень для B немає: генерацію не запускай і worker-гілку не створюй. Очікуй нового списку, не підбирай вправи самостійно.
