-- Test kontrollib, et regional_manager rollil pole SELECT-oigust email veeru peale.
-- Tagastab 0 rida -> test läbib (email on veerutasemel keelatud).
-- Tagastab 1+ rida -> test ebaõnnestub (regional_manager näeks emaili).

SELECT grantee, column_name, privilege_type
FROM information_schema.column_privileges
WHERE table_schema  = 'secured'
  AND table_name    = 'dim_users_regional_base'
  AND column_name   = 'email'
  AND grantee       = 'regional_manager'
  AND privilege_type = 'SELECT'
