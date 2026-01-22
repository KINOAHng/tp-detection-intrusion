-- Liste des catalogues disponibles dans Trino
SHOW CATALOGS;

-- Liste des schémas dans le catalogue MinIO
SHOW SCHEMAS FROM minio;

-- Liste des tables dans le schéma logs de MinIO
SHOW TABLES FROM minio.logs;

-- Affichage des 10 premières intrusions détectées
SELECT * FROM minio.logs.predictions 
WHERE Intrusion = 1 
LIMIT 10;

-- Comptage du nombre total d'intrusions détectées
SELECT COUNT(*) AS nombre_intrusions 
FROM minio.logs.predictions 
WHERE Intrusion = 1;
