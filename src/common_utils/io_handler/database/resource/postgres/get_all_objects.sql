select
    n.nspname as schema_name
    ,c.relname as object_name
    ,r.rolname as object_owner
    ,case c.relkind
        when 'r' then 'table'
        when 'm' then 'materialized_view'
        when 'i' then 'index'
        when 'S' then 'sequence'
        when 'v' then 'view'
        when 'c' then 'type'
        else c.relkind::text
    end as object_type
from pg_class c
join pg_roles r
on r.oid = c.relowner
join pg_namespace n
on n.oid = c.relnamespace
where n.nspname not in ('information_schema', 'pg_catalog')
    and n.nspname not like 'pg_toast%%'