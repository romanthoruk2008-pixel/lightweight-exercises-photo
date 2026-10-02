Підготуй зображення для ОДНОГО генератора, лише у хмарному workspace.

Репозиторій: romanthoruk2008-pixel/lightweight-exercises-photo.
Джерельна гілка: agent-03-inventory-2026-10-01.
Коміт завдань: 599a31cd52cee8a34a19b1fb1bc7792438140c2d.
Перед стартом прочитай docs/agent-03-single-generator-2026-10-03-handoff.md з актуальної джерельної гілки. Власна гілка результатів: agent-08-generator-single-2026-10-03; не push у джерельну гілку чи work.

Твоє єдине призначення: data/assignments/agent-03-single-generator-2026-10-03.json — 30 точних ID. Виконуй строго:
1. data/batches/agent-03-others-028.json — 10 вправ без тренажерів.
2. data/batches/agent-03-others-029.json — 10 вправ на обладнанні.
3. data/batches/agent-03-others-030.json — 10 вправ на обладнанні, включно з cardio та статичним Смітом.
Чинні завдання A/B і пакети 001–027 не забирай і не змінюй.

Бери повний generation_prompt точного ID. Каталог, equipment та muscles звіряй тільки за цим ID. Використовуй data/audits/agent-03-single-generator-2026-10-03-technique.json і documented technique_resolution, зберігаючи помилковий вихідний текст без виправлень. Еталон assets/exercises/biceps-curl-dumbbell.png, SHA256 52fef743ba2d7689aa81a8b995df3c6715cbb5d04c4bd688af4ca57b2d20057f, визначає лише зовнішність/матеріали. Прочитай docs/exercise-image-style.md і docs/exercise-image-style-neutral-primary.md; відповідний style_version, hashes і точна сцена є в кожному завданні. Cardio/full_body/other нейтральні; підсвічуй лише конкретні secondary точного ID, #F26445 на 40–50%; порожній список — без підсвітки. Для inverted-row-machine гриф Сміта зафіксований і НЕ рухається.

Перед КОЖНИМ викликом онови Git-інформацію й звір PNG та чинні призначення всіх доступних агентів, власні локальні результати й manifest. Будь-який наявний PNG цього ID, навіть pending, або нове чуже призначення — skip із джерелом причини. Failed виклик без PNG не означає готовий результат; чужі попередні спроби не продовжуй. Тільки вбудований image_gen; одна вправа/одна фаза/одна людина на прозорому PNG 1024×1024. Автоматичних повторів і візуального QA не роби.

Зберігай у точні planned_png_path та planned_git_png_path; папки:
cloud: /workspace/exercise-image-results/agent-03-single-generator-2026-10-03/generator-single/<batch_id>/<exercise_id>/attempt-1.png
Git: assets/exercises/pending/agent-03-single-generator-2026-10-03/generator-single/<batch_id>/<exercise_id>/attempt-1.png
Власний manifest: data/manifests/agent-03-single-generator-2026-10-03/generator-single.json.
Після кожної вправи зберігай attempt/history, prompt/hash, style/reference/catalog hashes, result path/SHA256, технічний статус і помилки. user_review=pending до мого явного схвалення, agent_visual_review=not_performed. Після КОЖНОГО пакета commit/push власної гілки й перевір remote-файли.

При першій помилці квоти/ліміту збережи помилку та історію, push checkpoint і ЗУПИНИСЬ без повторних викликів чи обходу через API. Каталог/переклади, work, shared progress, чужі manifests, схвалення та Supabase не змінюй. Після 030 зупинись і покажи результати, skips і помилки.
