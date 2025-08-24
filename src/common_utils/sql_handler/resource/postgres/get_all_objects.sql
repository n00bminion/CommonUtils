select
    n.nspname as schema_name
    ,c.relname as object_name
    ,r.rolname as object_owner
    ,case c.relkind
        when 'r' then 'TABLE'
        when 'm' then 'MATERIALIZED_VIEW'
        when 'i' then 'INDEX'
        when 'S' then 'SEQUENCE'
        when 'v' then 'VIEW'
        when 'c' then 'TYPE'
        else c.relkind::text
    end as object_type
from pg_class c
join pg_roles r
on r.oid = c.relowner
join pg_namespace n
on n.oid = c.relnamespace
where n.nspname not in ('information_schema', 'pg_catalog')
    and n.nspname not like 'pg_toast%%'
order by n.nspname, c.relname;