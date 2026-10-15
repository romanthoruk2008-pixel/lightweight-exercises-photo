# Bed Cardio — scoped import checkpoint

Execution branch: `agent-08-generator-single-2026-10-03`.
Pinned preparation commit: `d8e01b672a7125790033b2f7a600dd01c3f9427c`.
Target: project `yywyrbhqfavjdgonlzma`, table `public.catalog_exercise`, exact ID `bed-cardio` only.

## Text import

**Not performed: secure connection unavailable in this cloud task.** The managed runtime is cloud/running/connected, but exposes no Supabase connector and no `exerciseuploader` variable. The existing importer documents that exact binding and sends it as `apikey` through the inherited HTTPS proxy. No credentials were read or printed, and no Supabase API requests or mutations were made. Bed Cardio's live existence and current image fields are unknown.

Offline verification passed for the source-file, canonical record and insert-payload hashes against `data/catalog-changes/bed-cardio.json`. All eight complete language blocks (`en`, `uk`, `es`, `it`, `tr`, `fr`, `ru`, `pl`) match between source and payload; localized card names/descriptions/instructions/cues/mistakes/safety notes match too. Exact ID/name, equipment none, primary cardio, empty secondary and duration-only card semantics are verified. The English description is exactly the user-requested pillows/heavy-breathing text. The pinned one-row payload has all five image fields NULL and omits `replaces_ids`/`updated_at` for existing server defaults.

A cloud configuration draft was saved declaring the **existing** `exerciseuploader` requirement for `yywyrbhqfavjdgonlzma.supabase.co`. This adds that hostname to the draft's restricted destinations; it does not provide a credential or activate the runtime. Restore the existing secure binding through environment settings, review/save, and publish before resuming. Never request or place its value in chat, Git or logs.

Once connected, first GET only `bed-cardio`. If absent, insert only the pinned singleton payload without upsert. If text-identical, do nothing. If authorized text differs, patch only changed text/catalog fields with exact-ID, updated_at and prior-value concurrency predicates; preserve unrelated fields and any existing image. A failed/ambiguous write requires fresh exact-row reconciliation, not a blind repeated insert. Read back and compare all eight full blocks, localized names/descriptions and exact tracking/equipment/muscle fields. Do not run the bulk importer.

## Illustration

**Upload/binding not performed.** The current attachment is a Figma screenshot, not the standalone original. Source image decisions explicitly leave original path/hash/MIME/dimensions/provenance unknown; available Bed Cardio image paths and cloud library/shared directories provide no original file. The screenshot was not cropped, uploaded, transformed or regenerated. New generation count is zero.

Request the original standalone illustration file and its creation provenance. Only `generated` and `gym_visual_edit` are documented supported origins; visual appearance is not evidence of either. Keep image fields NULL for a newly inserted text-only row until both original bytes and truthful origin are established. Do not clear a pre-existing image. Once available, retain exact original bytes, use a SHA256-based unique path in `exercise-images` with no overwrite/upsert, verify returned bytes, and bind the actual dimensions/hash/path/origin using a concurrency check.

## Evidence and scope

Manifest: `data/manifests/bed-cardio/agent-08-import-2026-10-15.json`.
All five requested source documents remain pinned in the preparation commit; they were read directly via Git without modifying the source branch. Other exercises, catalogue/export/translations, image links, approvals, shared progress, schema/RLS and user tables are unchanged. Work stayed in `/workspace`; no Mac connection or filesystem was used.
