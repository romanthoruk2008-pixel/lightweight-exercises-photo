# Bed Cardio — restored Easter egg

Restored as a text-only addition at the user's explicit request on 2026-10-15 (Europe/Kiev), on branch `agent-03-inventory-2026-10-01`. The user reiterated that all work belongs in the cloud/GitHub; no downloads or writes to their Mac.

`bed-cardio` is the previously prepared, non-explicit adult Easter egg. Its original names and full text are restored unchanged in all eight languages: en, uk, es, it, tr, fr, ru, pl. English description: “Cardio, good company, and a comfortable pace. Log the duration — no personal best required.”

## Source and card

- Exact one-record addition: `data/exercises/bed-cardio-addition.json`.
- Card: `data/cards/bed-cardio.json`; preview: `docs/bed-cardio-card.html`.
- Import delta: `data/imports/bed-cardio/catalog-exercise.insert.json`.
- Source/record/payload hashes and counts: `data/catalog-changes/bed-cardio.json`.
- Reproducible read-only checks: `python3 -B scripts/check_bed_cardio_addition.py`; evidence: `data/audits/bed-cardio-validation.json`.

This is a standard cardio card with `tracking_type=duration`, seconds formatted as mm:ss, and no sets, reps, weight or distance. Read translated titles from `content[locale].name`, falling back to `content.en.name`, then top-level `name`. Descriptions, instructions, cues, mistakes and the consenting-adults safety note are localized too.

No application renderer is present here. The JSON card and standalone preview define the data contract; they do not prove that the actual app already consumes duration cards or localized titles correctly.

The existing 451-record catalogue and separate 28-record Supabase export remain byte-identical. This additional record makes 480 unique prepared records in Git (477 active, 3 archived), with 4484 language blocks. It does **not** claim that Supabase now has 480 rows: no database writes or live database checks were performed. Do not rewrite count/hash pins in the old bulk import pipeline to import this one record.

## Original illustration — still missing as a file

The user selected the existing illustration of two adults resting side by side under a blanket. Keep it unchanged: no new generation, crop, resize, recoloring, retouching, transparency processing or replacement. The illustration's existing appearance, materials, highlights and proportions are retained as an exception scoped only to `bed-cardio`.

The original bytes are not available in this workspace. A chat rendering is not a downloadable source file. No actual image has been added; path/SHA256, MIME type, dimensions, transparency and creation provenance remain unknown/null. Image binding is deferred and does not block this text-only addition. If the user later requests image binding, obtain the original through an authorized cloud attachment and preserve its exact bytes. The planned `.png` filename is provisional until the real format is known; do not convert another format silently.

The selected visual was already approved by the user. Identical original bytes do not need another aesthetic approval, but they must first be bound to a real file and SHA256. Do not fabricate a hash or mark a nonexistent asset imported.

`primary_muscle=cardio`, `secondary_muscles=[]`. Do not infer muscle targets from the orange regions in the existing illustration. The unchanged-image exception is in `data/style-decisions/bed-cardio-original-image.json`; global styles are untouched. Do not insert this ID into generation batches 044–046 or create another generation assignment.

## Later single-row import

The included payload preserves existing SQL-compatible cardio/duration fields and the complete eight-language content. All five image fields are NULL pending the actual file and a supported, truthful origin. `replaces_ids` and `updated_at` are omitted to use the existing server defaults. The read-only validator checks the effective row against the importer's eight SQL CHECK rules.

An authorized importer should fetch and pin this preparation branch's commit, verify hashes, then read exact ID `bed-cardio` from `public.catalog_exercise` before any write. If absent, insert this single record. If present and equal, report a no-op; if different, stop and report the conflict rather than overwrite it. Never whole-catalog upsert, change other exercises, modify RLS/schema, alter approvals or regenerate images. Read back all eight content blocks and tracking fields after an authorized import. Preserve image NULLs until the genuine file and provenance can be bound correctly.

Supabase accepts image origins `generated` or `gym_visual_edit` in the documented schema; visual appearance alone does not establish either. `user_provided` is not a supported SQL enum value. Unknown provenance must remain unknown until resolved.
