Це наступне доручення ОДНОМУ генератору: 30 нових вправ, 3 пакети по 10. Генеруй лише у поточному хмарному workspace.

Репозиторій: romanthoruk2008-pixel/lightweight-exercises-photo.
Джерельна гілка: agent-03-inventory-2026-10-01.
Коміт завдань: 77cd54d73b1f2546d29e7f17bd816faf9ec14f5e.
Спочатку прочитай docs/agent-03-single-generator-next30-2026-10-03-handoff.md з актуальної джерельної гілки.
Продовжуй у власній гілці agent-08-generator-single-2026-10-03, зберігши її старі результати та history; не reset/recreate її від джерельної гілки.

Єдине нове призначення: data/assignments/agent-03-single-generator-next30-2026-10-03.json.
Виконуй строго:
1. data/batches/agent-03-others-031.json — 10.
2. data/batches/agent-03-others-032.json — 10.
3. data/batches/agent-03-others-033.json — 10.
Пакети 001–030, старі failed спроби, чинні A/B задачі та попередній manifest не змінюй і не перепризначай.

Перенеси тільки нові файли завдань/джерел/окремого manifest із коміту завдань, зберігши свої робочі спроби, якщо вони вже існують. Не замінюй каталог або shared progress. Повний prompt, точні English/equipment/muscles, source/style/reference hashes і selected scene є в кожному записі. Source evidence: data/audits/agent-03-single-generator-next30-2026-10-03-technique.json; питання blocked не генеруй. Еталон assets/exercises/biceps-curl-dumbbell.png, SHA256 52fef743ba2d7689aa81a8b995df3c6715cbb5d04c4bd688af4ca57b2d20057f, тільки для зовнішності та матеріалів. Стиль docs/exercise-image-style.md (v1); затверджене neutral-primary доповнення збережене. У цих 30 primary конкретні: підсвічуй точний primary #F26445, лише secondary цього ID на 40–50%; не додавай muscle targets за власним знанням. Еталон не визначає позу/обладнання/підсвітку.

Перед КОЖНИМ викликом отримай актуальні Git-дані й звір PNG та призначення всіх доступних агентів, власні локальні результати і manifests/progress читанням. Будь-який PNG точного ID, навіть pending, або нове чуже призначення — skip із branch/commit/path/reason. Failed виклик без PNG не є результатом і залишається у початковому пакеті. Тільки вбудований image_gen: 1 людина, 1 фаза, прозорий квадратний PNG 1024×1024; візуального QA й автоматичних повторів не роби.

Точні planned_png_path та planned_git_png_path беруться з задачі:
cloud: /workspace/exercise-image-results/agent-03-single-generator-next30-2026-10-03/generator-single/<batch_id>/<exercise_id>/attempt-1.png
Git: assets/exercises/pending/agent-03-single-generator-next30-2026-10-03/generator-single/<batch_id>/<exercise_id>/attempt-1.png
НОВИЙ окремий manifest: data/manifests/agent-03-single-generator-next30-2026-10-03/generator-single.json.
До .gitignore за потреби додай тільки точні allowlist шляхи цих 30, зберігши старі правила.

Після кожної вправи збережи actual attempts/history, prompt/hash, source/style/reference/result SHA256, path, час і помилки. user_review=pending до мого явного схвалення; agent_visual_review=not_performed. Після КОЖНОГО пакета commit/push лише власної гілки й перевір віддалені результати.

При першій помилці квоти/ліміту збережи помилку/history, push checkpoint і ЗУПИНИСЬ без повторних викликів чи обходу через API. work, підготовчу гілку, каталог/переклади, shared progress, чужі manifests, схвалення та Supabase не змінюй. Після 033 зупинися й покажи результати/skips/помилки.
