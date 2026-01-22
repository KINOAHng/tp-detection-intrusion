-- Liste des catalogues disponibles dans Trino
SHOW CATALOGS;

-- Liste des schémas dans le catalogue MinIO
SHOW SCHEMAS FROM minio;

-- Liste des tables dans le schéma logs de MinIO
SHOW TABLES FROM minio.logs;

-- Affichage des 10 premières intrusions détectées (basé sur la prédiction du modèle)
SELECT * FROM minio.logs.predictions_parquet
WHERE prediction = 1.0
LIMIT 10;

-- Comptage du nombre total d'intrusions détectées (basé sur la prédiction)
SELECT COUNT(*) AS nombre_intrusions
FROM minio.logs.predictions_parquet
WHERE prediction = 1.0;
