SELECT TOP (1000) [LineaID]
      ,[BegAutor]
      ,[EndAutor]
      ,[FechaInicial]
      ,[FechaFinal]
      ,[Longevidad]
      ,[Linea]
  FROM [TFG_Codigo].[dbo].[DL_Git]
  WHERE FechaFinal is NULL
  ORDER BY LineaID


  --Cuento cantidad de filas que no se eliminaron
SELECT count(*) FROM [TFG_Codigo].[dbo].[DL_Git] WHERE FechaFinal IS NULL

--Cuento cantidad de filas que se eliminaron
SELECT count(*) FROM [TFG_Codigo].[dbo].[DL_Git] WHERE FechaFinal IS NOT NULL

-- Agrupar por longevidad el numero de lineas
SELECT Longevidad, COUNT(*)
FROM [TFG_Codigo].[dbo].[DL_Git]
GROUP BY Longevidad

-- Localizar 'fors' de lineas que no se eliminan
SELECT *
FROM [TFG_Codigo].[dbo].[DL_Git]
WHERE FechaFinal is NULL
AND Linea like '%for%'