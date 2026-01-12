select
    case c.relkind
        when 'r' then 'table'
        when 'm' then 'materialized_view'
        when 'i' then 'index'
        when 'S' then 'sequence'
        when 'v' then 'view'
        when 'c' then 'type'
        else c.relkind::text
    end as object_type
    ,n.nspname as schema_name
    ,c.relname as object_name
	,coalesce(i.tablename, t.tablename) table_name
from pg_class c
join pg_roles r
on r.oid = c.relowner
join pg_namespace n
on n.oid = c.relnamespace
left join pg_indexes i
on i.schemaname = n.nspname
and i.indexname = c.relname
left join pg_tables t
on t.schemaname = n.nspname 
and t.tablename = c.relname
where n.nspname not in ('information_schema', 'pg_catalog')
    and n.nspname not like 'pg_toast%%'
and left(relname, 6) != 'flyway'
