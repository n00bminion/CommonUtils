SELECT 
    sm.type as object_type,
    sm.name as object_name,
    sm.tbl_name as table_name,
    pdl.file as db_file
FROM sqlite_master sm 
CROSS JOIN pragma_database_list pdl
where pdl.name = 'main'
