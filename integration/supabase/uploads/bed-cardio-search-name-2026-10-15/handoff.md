# Bed Cardio: user-approved name workaround, 2026-10-15

The user approved changing the main searchable name after hidden JSON alias metadata alone did not fix their app search. They explicitly excluded the second Ukrainian word from the proposed visible name. Updated only public.catalog_exercise.name for exact id bed-cardio: Bed Cardio -> Bed Cardio · sex. No Cyrillic секс in the new main name.

A PATCH with exact ID, prior name, updated_at and previous image predicates guarded concurrency. Only name was supplied in the payload; updated_at advanced through the existing trigger. Full before/after reads confirmed every other Bed Cardio field unchanged, including all eight localized names/descriptions/content blocks, existing hidden alias metadata and image fields. All 479 unrelated records matched in full; no duplicate exercise or schema/RLS/grant change.

Direct HTTPS REST queries using name=ilike.*sex*, name=ilike.*SEX*, and name=ilike.*Bed Cardio* each returned the one Bed Cardio ID. This verifies direct Supabase name filtering only. App search code, query path, cache, displayed fallback name and UI behavior remain unavailable and untested. The earlier whole-alias matching specification is not claimed implemented by this name workaround; ordinary substring name search semantics apply.

Script: integration/supabase/set_bed_cardio_search_name.py (read-only by default; --apply permits only the exact name PATCH on bed-cardio). Re-running with the target name skips mutation. Manifest records actual verification, preservation checks and limitations.

Historical pinned Bed Cardio payload still has name Bed Cardio and no search_aliases extension. Do not rerun the original import to undo newer authorized name/metadata changes. No localized fields were edited to force search. Existing JSON aliases sex/секс remain unchanged; the current user instruction removed Ukrainian секс only from the main proposed name.

All work ran in the managed cloud workspace via the existing HTTPS proxy and exerciseuploader binding, without exposing credentials or accessing the user's Mac. Metadata and script are kept only in agent-04-supabase-integration.
