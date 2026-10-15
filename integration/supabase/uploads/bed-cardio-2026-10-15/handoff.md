# Bed Cardio — single-record import, 2026-10-15

Project: yywyrbhqfavjdgonlzma. Table: public.catalog_exercise. Exact ID: bed-cardio.
Execution: managed cloud workspace /workspace/lightweight-exercises-photo, provider=cloud, HTTPS proxy and existing exerciseuploader binding, apikey header. No Mac filesystem or remote Mac access used. No secret values saved.

## Completed import

Created exactly one record; no upsert or bulk catalog importer. The source payload omitted replaces_ids/updated_at for server defaults. All 479 unrelated records were read before/after and their full values, including timestamps and image fields, matched exactly. Final count: 480 records.

Text source: agent-03-inventory-2026-10-01 commit d8e01b672a7125790033b2f7a600dd01c3f9427c. Source-file, insert-payload and canonical record SHA256 checked against metadata. Card localized views and all eight description-v2-meme descriptions matched. Languages en, uk, es, it, tr, fr, ru, pl preserved as eight complete content blocks on ONE record, including localized names, descriptions, instructions, form_cues, common_mistakes, safety_note and provenance. Name Bed Cardio, tracking_type duration, equipment none, primary_muscle cardio, secondary_muscles [], archived false verified on live readback.

## Image

Used the actual final generator artifact, not a Figma screenshot. Source branch agent-08-generator-single-2026-10-03 commit 710286ad99a8109145ad60c7c194d1bd80b5eddf. Generation manifest: data/manifests/bed-cardio/agent-08-generation-2026-10-15.json. PNG: assets/exercises/pending/bed-cardio-2026-10-15/bed-cardio/attempt-1.png. Exactly one generated version was available. Source review=approved and matching review_history were observed and left unchanged; generation alone was not treated as approval.

Final SHA256: 010ec1aab966a3baad341f4e33f4c576f3e6c9c7ffec9ed01d22b1ede92e264b. Actual dimensions 1536x1536, RGBA, 2060908 bytes, 1134716 fully transparent pixels; within the bucket limit of 5242880 bytes. The source task had already added transparent space above the original generated 1536x1024 region at the user's request. This task copied the final Git bytes unchanged: no generation, padding, crop, resize or visual QA.

Storage bucket exercise-images, path bed-cardio/010ec1aab966a3baad341f4e33f4c576f3e6c9c7ffec9ed01d22b1ede92e264b.png. Upload used x-upsert=false. Canonical public GET without apikey/Authorization matched the source hash before patching all five image fields with image_origin=generated. Readback confirmed the path/hash/dimensions/origin. A read-only resume rechecked source texts, image fields and public hash without issuing mutations.

## Reproduction and evidence

Script: integration/supabase/import_bed_cardio.py. Default mode is read-only preflight; --apply is scoped to the singleton bed-cardio INSERT or a timestamp/image-guarded PATCH of only authorized text/image columns. Existing identical records skip text writes; existing identical PNG objects are verified without overwrite; a different existing image is a conflict. The six focused tests passed for exact source/languages, write guards, idempotent text behavior and concurrent-change rejection. Manifests: preflight.json, manifest.json, image-transfer.json, read-only-resume.json. No schema, RLS, grants, shared progress, source files or approval decisions changed. Normal-client catalog reading was not tested: no publishable key was exposed.

## App search alias — separate outstanding requirement

The user subsequently requested the hidden whole-query alias sex -> bed-cardio. Required inputs include sex, SEX, and two spaces + Sex + two spaces in every language; trim and casefold, no unrelated substring matching, normal name matching and filters preserved, deduplicate by exercise_id, no localized display/text changes or duplicate exercise.

NOT IMPLEMENTED OR VERIFIED IN THE APP. The connected repository has no app search code; there is no app repository or app URL attached. Asked the user for the app GitHub repository/branch and running app URL. Do not report the Supabase import or a synthetic search demo as implementing this alias. No speculative alias schema/data or search code was written. Actual app search tests remain pending those details.
