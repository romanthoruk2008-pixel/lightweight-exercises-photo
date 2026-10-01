# Supabase імпорт завершено — agent-04

Проєкт `yywyrbhqfavjdgonlzma`; bucket `exercise-images`.
Користувач прямо дозволив 451 source record і 135 approved PNG;
область дозволу зафіксована у `import_authorization.md`.
Виконання: поточний cloud workspace, через HTTPS proxy і наявну
прив'язку `exerciseuploader`; секрет не виводився і не зберігався.

## Фактичний результат

- Вставлено 451 новий catalog_exercise; POST без upsert, по 100 рядків,
  `Prefer: missing=default,return=minimal`.
- `replaces_ids` не передавали. На читанні назад для всіх вставлених ID
  підтверджено server DEFAULT []; replacement links не вигадувалися.
- Повне фінальне читання: точна множина 451 ID, всі source-поля і content
  рівні джерелу, 4448 мовних блоків, 3 архівні записи.
- Завантажено 135 нових PNG без перезапису; для кожного canonical public
  URL без apikey/Authorization повернув image/png і точний accepted SHA256.
- Після public verification оновлено п'ять image-полів точного ID з
  optimistic filters по updated_at і старих image-полях; читання назад
  підтвердило 135 зв'язків і незмінний content.
- Перші 3 — успішний gate. Далі 13 пакетів по 10 і останній із 2;
  разом 15 окремих manifest-файлів.
- 21 pending і rejected/історичні неприйняті спроби не завантажувалися.
- Помилок перенесення немає. Наявні technical exceptions, dimensions,
  PNG bytes, source catalog, progress і схвалення не змінені.
- Користувацькі таблиці, schema, policies/RLS/grants не змінювалися.

Остання повна перевірка: `2026-10-01T21:33:24.591892+00:00`
(2 жовтня 2026, 00:33 за Europe/Kiev). Точні часові позначки в manifests — UTC.
Git-гілка результатів: `agent-04-supabase-integration`; інші гілки не оновлювалися.

## Артефакти і відновлення

- `uploads/catalog_manifest.json`: 5 insert batches, їхні точні ID,
  читання назад і перевірка default. `unique_inserted_ids_recorded=451`.
- `uploads/batch-001.json` … `batch-015.json`: source PNG, exercise_id,
  accepted SHA256, Storage path, public byte verification, DB before/after.
- `uploads/completion.json`: фінальний каталог і всі 135 PNG/DB links.
- `uploads/summary.json`: агреговані фактичні counts і SHA256 manifests.
- `uploads/resume_readonly_check.json`: фактично перевірене відновлення
  для 451 identical catalog records і перших 3 complete PNG, з mutations
  API вимкненими. Нових INSERT/upload/PATCH не було.

`import_catalog_images.py` без flags — тільки preflight. `--apply` вже
авторизований для цієї scope і пропускає complete entries після повторного
читання public bytes і DB. `--verify-only` не дозволяє Supabase mutations.
Не видаляти checkpoints і не перезаписувати інші Storage objects/DB links.
Конфлікт source/content/hash/link зупиняє імпорт. Невизначений результат
після network failure відновлювати читанням, а не сліпим повтором запису.

Усі 28 тестів пройшли, включно з no-overwrite, server-default omission,
public-before-PATCH, resume, concurrency filters і забороною mutations
до користувацьких таблиць/RPC/інших objects.

`data/exercise-image-progress.json`, початковий audit і `results` залишені
як незмінні джерела/історія підготовки. Їхній історичний not_configured
або старі блокування не є поточним статусом Supabase; поточна істина —
live Supabase і `uploads` manifests. Не скидати схвалення/attempts через
ці історичні значення і не запускати generation повторно.

## Межа клієнтської перевірки

Публічне читання PNG підтверджене для всіх 135 об'єктів без секрету.
Читання каталогу звичайним клієнтом **не перевірене**: у доступній
конфігурації/процесі немає publishable/anon key. Admin read не є доказом
клієнтських grants/RLS. Це відсутня передумова перевірки, не встановлена
помилка конкретної policy; policies не змінювалися для обходу.

Якщо стане доступною прив'язка publishable/anon key, виконати
`import_catalog_images.py --verify-only`: скрипт перевірить точні 451 ID,
content/4448 мовних блоків звичайним клієнтом і оновить completion report
без Supabase writes. Сам ключ у чат/файли не копіювати.
