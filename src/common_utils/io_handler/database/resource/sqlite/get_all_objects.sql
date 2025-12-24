SELECT 
    sm.type as object_type,
    sm.name as object_name, -- different to tbl_name if it's index or pk
    sm.tbl_name as table_name
    sm.rootpage,
    sm.sql
FROM sqlite_master sm 
