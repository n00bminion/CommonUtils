SELECT attrelid::regclass AS tbl
, attname            AS col
, atttypid::regtype  AS datatype
-- more attributes?
FROM   pg_attribute
WHERE  attrelid = '{schema}.{table}'::regclass  -- table name optionally schema-qualified
AND    attnum > 0
AND    NOT attisdropped
ORDER  BY attnum;