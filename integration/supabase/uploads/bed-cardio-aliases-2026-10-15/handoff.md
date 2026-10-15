# Bed Cardio aliases — Supabase data only, 2026-10-15

User clarified that the work should be in Supabase. Stored hidden aliases sex and секс on the existing exact catalog_exercise.id=bed-cardio. No additional exercise, column, table, RPC, RLS/grant change or migration was created.

Data contract: content.<language>.search_aliases is an array containing ["sex", "секс"] for en, uk, es, it, tr, fr, ru, pl. Existing aliases would be preserved. A concurrency-guarded PATCH changed only content on exact bed-cardio; existing localized display names, descriptions, instructions, form_cues, common_mistakes, safety_note, provenance and all other values were compared unchanged. All noncontent columns except the trigger-managed updated_at, including image fields, matched exactly. All 479 unrelated records were compared unchanged.

Script: integration/supabase/add_bed_cardio_aliases.py. Default read-only; --apply enables only a Bed Cardio content PATCH with exact ID, updated_at and previous image predicates. Re-running with identical aliases skips the write.

Verification: 64 direct REST metadata probes across eight languages. JSONB array containment is exact, so sex and секс matched while sexy/asexual/unisex did not inject Bed Cardio. A biceps muscle filter excluded Bed Cardio. The verification client trimmed/casefolded SEX and spaced Sex before issuing the REST filter. This normalization was NOT installed in Supabase and NOT installed in the app.

IMPORTANT: existing normal app search is NOT implemented or verified by this change. We do not have its repository or runtime URL. No claim is made that a user typing sex in the current app now sees Bed Cardio. The app or a server search endpoint must explicitly consume these JSON aliases, normalize input, combine with normal name search, apply existing filters and deduplicate by exercise_id. Ordinary app-client read permissions were not tested; requests used the configured server binding.

All operations ran in the managed cloud workspace through the HTTPS proxy and existing exerciseuploader binding as apikey. No secret values saved, no Mac access, and no generation, image transformations, shared progress or approval changes.
