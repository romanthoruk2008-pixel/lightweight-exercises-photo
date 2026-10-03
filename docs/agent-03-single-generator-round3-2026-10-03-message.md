Продовжуй генерацію в тому самому хмарному workspace і своїй existing гілці agent-08-generator-single-2026-10-03. Не reset/recreate її і не втрать попередні results/failed attempts/history.

Repo: romanthoruk2008-pixel/lightweight-exercises-photo.
Source branch: agent-03-inventory-2026-10-01.
Immutable task commit: fec6f45faa15189808e8dfd765916825d4894007.
Спочатку прочитай docs/agent-03-single-generator-round3-2026-10-03-handoff.md з актуальної source branch.
Єдине нове призначення: data/assignments/agent-03-single-generator-round3-2026-10-03.json.
Після вже взятих завдань виконай строго:
1. data/batches/agent-03-others-034.json — 10.
2. data/batches/agent-03-others-035.json — 10.
3. data/batches/agent-03-others-036.json — 9.
Разом 29: невизначені записи не додавати заради 30.

Перенеси лише нові tasks/evidence/errors/окремий manifest з task commit, не перезаписуй старі робочі результати/attempts, catalog/shared progress/чергу/чужі manifests. Full generation_prompt, exact source fields, selected scene, style/reference hashes і planned PNG paths є в кожному ID. Еталон assets/exercises/biceps-curl-dumbbell.png (SHA256 52fef743ba2d7689aa81a8b995df3c6715cbb5d04c4bd688af4ca57b2d20057f) лише для зовнішності/матеріалів: відкрий перед першим викликом. Стиль docs/exercise-image-style.md плюс approved docs/exercise-image-style-neutral-primary.md. cycling-machine і elliptical-trainer-machine: cardio + empty secondary, повністю нейтральні без підсвітки. Інші ID: тільки власні primary/secondary за prompt.

Перед кожним викликом fetch/read актуальні доступні Git гілки, PNG/призначення та власні локальні outputs/manifests. Уже наявний PNG цього ID навіть pending або нове чуже призначення — skip із точним reason/branch/commit/path. Старий failed без PNG лишається у старому пакеті, не переносити. Пакети 001–033 і чинні A/B jobs не змінювати.

Лише вбудований image_gen, одна вправа/людина/фаза, точний prompt; без visual QA/автоповторів. Cloud results: /workspace/exercise-image-results/agent-03-single-generator-round3-2026-10-03/generator-single/<batch>/<exercise_id>/attempt-1.png; Git results: assets/exercises/pending/agent-03-single-generator-round3-2026-10-03/generator-single/<batch>/<exercise_id>/attempt-1.png. Точні paths у tasks; за потреби додай тільки їхні allowlist-рядки, не заміни всю .gitignore.
Окремий manifest data/manifests/agent-03-single-generator-round3-2026-10-03/generator-single.json: оновлюй після кожної вправи, зберігай errors/attempt history і result SHA256. Після PNG user_review=pending, agent_visual_review=not_performed; технічні PNG/size/transparency checks окремо. Після кожного пакета commit/push тільки своєї worker branch, verify remote files і checkpoint handoff. Каталог, переклади, shared progress, схвалення та Supabase не змінюй.
При першій quota/rate-limit помилці збережи failed/history, push checkpoint і STOP без повторного виклику або іншого API. Після 036 STOP і покажи PNG/skips/errors. Не бери blocked.
