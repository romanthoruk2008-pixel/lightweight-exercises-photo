-- Read-only statements for Supabase SQL Editor. No migrations or grant changes.
-- The first result establishes the scope of the count: rls_applies_to_editor
-- must be false before catalog_row_count can confirm physical emptiness.
SELECT current_user AS editor_role,
       row_security_active('public.catalog_exercise'::regclass) AS rls_applies_to_editor,
       count(*) AS catalog_row_count
FROM public.catalog_exercise;

SELECT format_type(a.atttypid, a.atttypmod) AS sql_type,
       a.attnotnull AS not_null,
       pg_get_expr(d.adbin, d.adrelid) AS column_default,
       col_description(a.attrelid, a.attnum) AS description
FROM pg_attribute AS a
LEFT JOIN pg_attrdef AS d ON d.adrelid = a.attrelid AND d.adnum = a.attnum
WHERE a.attrelid = 'public.catalog_exercise'::regclass
  AND a.attname = 'replaces_ids' AND NOT a.attisdropped;

SELECT conname, pg_get_constraintdef(oid) AS definition
FROM pg_constraint
WHERE conrelid = 'public.catalog_exercise'::regclass AND contype = 'c';

-- Full definitions were supplied as JSON and retained in sql_editor_evidence.json.
SELECT jsonb_pretty(jsonb_agg(
    jsonb_build_object('name', conname, 'definition', pg_get_constraintdef(oid))
    ORDER BY conname)) AS checks
FROM pg_constraint
WHERE conrelid = 'public.catalog_exercise'::regclass AND contype = 'c';

SELECT rolname, rolbypassrls,
       has_table_privilege(rolname, 'public.catalog_exercise', 'SELECT') AS can_select
FROM pg_roles WHERE rolname IN ('service_role', 'anon', 'authenticated');

SELECT relrowsecurity, relforcerowsecurity
FROM pg_class WHERE oid = 'public.catalog_exercise'::regclass;

SELECT schemaname, tablename, policyname, roles, cmd, qual, with_check
FROM pg_policies
WHERE (schemaname = 'public' AND tablename IN
       ('catalog_exercise', 'exercise', 'workout', 'logged_exercise', 'set_entry'))
   OR (schemaname = 'storage' AND tablename IN ('objects', 'buckets'));

-- No user identities, credentials, or descriptions are selected.
SELECT count(*) AS rows,
       count(DISTINCT id) AS distinct_ids,
       count(*) FILTER (WHERE image_path IS NOT NULL) AS linked_images
FROM public.catalog_exercise;
