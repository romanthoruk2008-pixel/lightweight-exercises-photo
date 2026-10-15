# Copyable importer handoff — Bed Cardio

```text
Add only the user-requested Bed Cardio Easter egg, exact ID bed-cardio, when the user dispatches this import task.

Source branch: agent-03-inventory-2026-10-01. Fetch it and pin its current commit before reading files. Source: data/exercises/bed-cardio-addition.json. Verify its exact SHA256 and the single-row payload SHA256 against data/catalog-changes/bed-cardio.json.

Full handoff: docs/bed-cardio-handoff.md.
Payload: data/imports/bed-cardio/catalog-exercise.insert.json.
Card data: data/cards/bed-cardio.json.
Run read-only checks: python3 -B scripts/check_bed_cardio_addition.py.

Keep all eight localized names, descriptions, instructions, form cues, mistakes and safety notes. This is duration-only cardio, not a reps/sets exercise. Localized title lookup: content[locale].name -> content.en.name -> name. Check the actual app renderer; its implementation is not verified by this repository.

First read public.catalog_exercise for the exact ID. Insert the one row only if absent. Equal existing row means no-op. A different existing row means stop and report, not overwrite. Do not bulk-import the catalogue, change the other 479 records, overwrite image links, modify schema/RLS or touch shared progress and approvals. Read back exact content and tracking values after import.

This is a text-only addition in the cloud/GitHub; do not download or write anything to the user's Mac. Image binding is deferred. If the user requests image binding later, reuse only the original illustration unchanged through an authorized cloud attachment. No image generation, edits, resize, crop or recoloring. Do not invent a hash, dimensions, MIME type, alpha status or origin. Until genuine bytes/provenance are known, all five image fields stay NULL. Do not set unsupported image_origin=user_provided or infer generated from appearance. Existing visual highlights are an explicit asset-only exception, not new muscle data.

Do not add Bed Cardio to batches 044–046. Do not count the text record as a generated image. Report text import and image binding as separate outcomes.
```
