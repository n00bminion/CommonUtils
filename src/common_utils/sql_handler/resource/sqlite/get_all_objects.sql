SELECT * 
FROM sqlite_master 
WHERE type IN ('table','view') 
ORDER BY name