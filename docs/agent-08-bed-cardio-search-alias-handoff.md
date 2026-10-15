# Bed Cardio search alias

User requested that typing `sex` in exercise search displays Bed Cardio (`bed-cardio`). The alias contract is `data/search-aliases/bed-cardio.json`.

Application integration is still required: no exercise-search implementation or alias consumer exists in this data/image repository or its available branches. This commit does not claim live search behavior or a database update. The app repository is needed to finish integration.

In the existing exercise search flow, trim the query and match `sex` case-insensitively. Include the existing `bed-cardio` exercise in normal results, deduplicating by its exact ID. Keep its localized display name and existing content, tracking and approved illustration. Apply the alias in every locale. Preserve normal name search and existing filters; do not rename the exercise or add the alias to its description.

Acceptance cases: `sex`, `SEX`, and `  Sex  ` include Bed Cardio; existing Bed Cardio/name search still works; the result appears once. An unrelated query does not gain Bed Cardio because of this alias. Exact matching avoids unintended substring matches such as `sextant`. Run these against the actual application search once connected.

Only the scoped alias contract and this handoff are changed. No catalog, translations, image bytes, approvals, shared progress, Supabase fields, schema or RLS changes.
