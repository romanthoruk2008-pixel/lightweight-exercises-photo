# Готове повідомлення майбутньому імпортеру

```text
Підготуй окремий імпорт нового Lightweight Easter egg `bed-cardio` з гілки `agent-03-inventory-2026-10-01`, commit `ae10de334e4ef0c952e1a954187282b08be91adf`. Це одна нова cardio activity; попередні 451 записи не змінювати.

Джерело — точний ID у `data/exercises/catalog.json`, SHA256 `7ac04be972d3a36ab357f172184bbe02255a0578f34a0ac2500684a95a126415`. ID не створювати з назви. Canonical name — Bed Cardio; localized names, description, instructions, cues, mistakes й safety у content для en/uk/es/it/tr/fr/ru/pl. tracking_type=duration, equipment=none, primary_muscle=cardio, secondary_muscles=[], archived=false. Картка — звичайна cardio card, тільки duration; без reps/sets/weight/distance. Локалізований заголовок читається з content[locale].name, з fallback на English; не відкидай цей additive JSONB field.

Payload для public.catalog_exercise: `data/imports/bed-cardio/catalog-exercise.insert.json`, рівно один рядок. Перед майбутнім записом звір фактичну схему й існування ID. Якщо вже є — перевір рівність/конфлікт, не перезаписуй навмання. Не запускай повний 452-row upsert та не обходь старий bulk-source pin. Вставку виконувати лише коли користувач доручить імпорт. Після вставки exact readback name/equipment/muscles/tracking/archived/content повинен збігатися з payload; replaces_ids і updated_at пропущені для чинних server defaults.

Користувач прямо вибрав свою ілюстрацію і заборонив її змінювати. Не генеруй, не ретушуй, не обрізай, не перефарбовуй, не змінюй розмір або прозорість. Рішення в `data/image-decisions/bed-cardio.json`; виняток лише для цього asset у `data/style-decisions/bed-cardio-original-image.json`. Наявні помаранчеві ділянки, двоє дорослих і горизонтальна композиція зберігаються; не виводь м’язи з картинки. Базовий стиль інших вправ не змінювати.

Оригінальні байти файла ще недоступні в workspace. Тому всі п’ять image-полів у INSERT є NULL, і SHA256/format/dimensions/provenance не вигадані. Після надання оригіналу — незмінні байти, фактичний SHA256 та параметри; підтверджене image_origin зі списку SQL CHECK. Не підставляй user_provided у SQL enum і не називай generated без підстав. Візуальний вибір користувача вже зафіксовано; для тотожного оригіналу повторного схвалення не потрібно. За відсутності файла чи коректного origin імпортуй тільки текст, коли отримано доручення, а image patch залиш blocked.

Handoff: `docs/bed-cardio-handoff.md`; картка для перегляду: `docs/bed-cardio-card.html`; перевірка: `data/audits/bed-cardio-validation.json`. Новий каталог — 452 ID/4456 мовних блоків, старі 451/4448 збережено. Підготовчий агент виконав 0 генерацій і 0 Supabase writes.
```
