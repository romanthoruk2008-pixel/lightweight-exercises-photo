# Авторизований імпорт

Користувач прийняв підготовку й прямо дозволив імпорт у проєкт
`yywyrbhqfavjdgonlzma` через прив'язку `exerciseuploader`:

- усі 451 source record, точні ID, 4448 мовних блоків і архівні статуси;
- не передавати `replaces_ids`, використати SQL DEFAULT [] через
  `Prefer: missing=default`; не вигадувати replacement links;
- наявні source-identical записи пропустити, конфлікти не перезаписувати;
- лише 135 approved PNG із перевіреного плану, без pending/rejected;
- bucket exercise-images; `<exercise_id>/<accepted_sha256>.png`;
- перші три — pilot; після public SHA256 verification продовжити по 10
  без додаткової згоди; image-поля змінювати лише після public verification;
- існуючі objects не перезаписувати; звіряти їхні байти/SHA256;
- не змінювати користувацькі таблиці, схему, RLS/grants або схвалення;
- manifest після кожного пакета, відновлення з пропуском перевіреного;
- publishable-key catalog test тільки якщо ключ уже доступний;
- push тільки `agent-04-supabase-integration`.

Технічне застосування відомого default дозволене користувачем, хоча
семантика replaces_ids залишається невідомою. В імпортері немає цього поля
в insert payload і немає replacement updates.

Цей файл фіксує інструкцію поточного завдання; він не є джерелом секрету,
новою політикою БД чи дозволом на інші майбутні записи.
