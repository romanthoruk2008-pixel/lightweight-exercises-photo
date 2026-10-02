# Agent-03: затверджений нейтральний primary — передача

Гілка `agent-03-inventory-2026-10-01`. Перевірка 2026-10-02T17:41:56.732149+03:00 (Europe/Kiev); work `f6c8874805203c78d804eb073e1627c6d4ddc78e`.

**45 ready**, **22 blocked**, **0 awaiting_style_decision** щодо нейтрального primary. Генерацію не запускали; style approval не є image approval чи дозволом на запуск.

Чинна для цих пакетів версія `v1-neutral-primary-2026-10-02` = v1 + `docs/exercise-image-style-neutral-primary.md`. Decision: `data/style-decisions/agent-03-neutral-primary-approved.json`. Barefoot/зовнішність/матеріали/решта v1 незмінні.

| Пакет | Статус | Вправ | Точний шлях |
| --- | --- | ---: | --- |
| agent-03-others-019 | ready | 10 | `data/batches/agent-03-others-019.json` |
| agent-03-others-020 | ready | 10 | `data/batches/agent-03-others-020.json` |
| agent-03-others-021 | ready | 10 | `data/batches/agent-03-others-021.json` |
| agent-03-others-022 | ready | 10 | `data/batches/agent-03-others-022.json` |
| agent-03-others-023 | ready | 5 | `data/batches/agent-03-others-023.json` |

Рекомендації: **blocked**, 22 записи, `data/queues/agent-03-remaining-recommendations.json`; коротка таблиця `docs/agent-03-remaining-recommendations.md`. 12 попередніх технічних + 10 додаткових. Жодна рекомендація не стала готовим prompt.

Для Hiking/Walking/Snowboarding — одне окреме рішення про сумісне взуття/кріплення та захист. Для neck extension і unilateral barbell calf raise потрібне підтвердження сумісних опор; пропозиція пози сама їх не розблоковує.

Кожний ready запис самодостатній: exact ID/name, весь source_english description/instructions/form_cues/common_mistakes/safety/provenance, equipment/muscles, конкретні phase/pose/grip/supports/trajectory/camera, full prompt/hash, unchanged appearance-only reference/path/hash, base style/addendum/decision hashes, exact-ID planned PNG path.

Еталон `assets/exercises/biceps-curl-dumbbell.png`, SHA256 `52fef743ba2d7689aa81a8b995df3c6715cbb5d04c4bd688af4ca57b2d20057f`; зовнішність/пропорції/матеріали, без копіювання пози чи підсвітки. Результат `/workspace/exercise-image-results/<batch_id>/<exercise_id>/attempt-1.png` — планований, файла ще немає.

Пакети 001–018 та всі їхні attempts/результати/призначення незмінні. Failed/noPNG залишається в попередньому пакеті. П’ять чужих ID (downward-dog, bear-crawl, jumping-jack, high-knees, mountain-climber) лише у style applicability, не включені в пакети й не перепризначені.

Історичні drafts `data/queues/agent-03-neutral-primary-style-drafts.json` і proposal `docs/agent-03-neutral-primary-style-proposal.md` незмінні як датований snapshot; їхні awaiting_style_decision superseded рішенням `data/style-decisions/agent-03-neutral-primary-approved.json` та queue.neutral_primary_preparation. Попередній blocked research теж історичний; поточні blocked IDs — queue.current_blocked_ids та нова таблиця.

Queue prepared_count=210 включає історичні 165 + нові 45; це НЕ число відсутніх PNG чи вправ для повторного запуску. Нові actionable IDs — queue.neutral_primary_preparation.new_ready_ids.

Перед майбутнім окремо дозволеним запуском: fetch ВСІ актуальні remote heads, перевірити PNG/призначення; не запускати ID з готовим/pending PNG або іншим призначенням. Інструмент перевірки тільки читає Git metadata, не робить візуального/технічного повторного QA PNG й не звертається до Supabase.

```bash
python scripts/prepare_agent03_neutral_primary.py --check
```

Остання перевірка й точні audited commits/source paths: `data/queues/agent-03-neutral-primary-validation.json`. Непушені файли інших cloud задач можуть бути недоступні; перевірка обмежена fetched Git та власними збереженими файлами.

work/каталог/shared progress/Supabase/схвалення PNG не змінені. Рекомендації не є зміною джерел або затвердженням техніки.
