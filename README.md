# TP Détection d'Intrusion

Auteur : Maryvonne

## Objectif du projet

Détecter les tentatives d'intrusion à partir du fichier Network_logs.csv (sans information temporelle).  
Modèle principal : Random Forest sur les features après mapping des adresses IP vers codes pays / 'Private' / 'Invalid'.  
Accuracy obtenue : 100 % (sur set de test).

## Architecture Globale

Le schéma ci-dessous représente le flux de travail :  
[Sources de données : CSVs] ↓  
[Ingestion / Upload dans MinIO] ↓  
[Stockage : MinIO (bucket S3-like)] ↓  
[Processing ETL : Spark (nettoyage + mapping IPs)] ↓  
[Feature Engineering (encoding + scaling)] ↓  
[ML Training : Random Forest (PySpark ML)] ↓  
[Prédictions stockées dans MinIO (Parquet)] ↓  
[Queries SQL & Détection : Trino] ↓  
[Détection des intrusions (prediction = 1.0)]

Explication du schéma :  
C'est un flux linéaire qui montre comment les données passent d'une étape à l'autre.  
* Pas besoin de faire une image ou un dessin avec un logiciel : ce texte est suffisant et très clair sur GitHub (il s'affiche avec les flèches alignées).  
* C'est juste une représentation simple du processus : de haut en bas, chaque flèche signifie "puis".  
* Tu peux le voir comme une liste d'étapes connectées par des flèches.

## Variables aléatoires, features et labels

- **Variables aléatoires discrètes** : Port (entier), Intrusion (binaire 0/1), catégorielles comme Request_Type, Protocol, User_Agent, Status, Scan_Type, src_country, dst_country.  
- **Variables aléatoires continues** : Payload_Size (réel).  
- **Features** : Toutes les colonnes sauf Intrusion (après mapping IPs et drop des IPs originales). Cols inutiles droppées : Source_IP, Destination_IP. Types vérifiés (inférés par Spark, forcés si besoin).  
- **Labels** : Intrusion (valeur cible pour apprentissage supervisé).

## Contenu du repository

* docker-compose.yml : Lance MinIO, Spark et Trino automatiquement.  
* trino-config/ : Configurations pour Trino (catalog MinIO).  
* scripts/preprocess.py : Nettoyage des données et mapping des IP avec PySpark.  
* scripts/train_model.py : Entraînement et évaluation du modèle Random Forest avec PySpark ML.  
* queries.sql : Exemples de requêtes SQL pour Trino (adaptées pour prédictions en Parquet).

## Comment relancer le projet

1. Installer Docker Desktop.  

2. Cloner le repository :  
   `git clone https://github.com/KINOAHng/tp-detection-intrusion.git`  

3. Aller dans le dossier :  
   `cd tp-detection-intrusion`  

4. Lancer les services :  
   `docker-compose up -d`  

5. Accéder à MinIO : http://localhost:9001  
   Login : minioadmin  
   Password : minioadmin123  
   Créer un bucket "logs" et uploader Network_logs.csv + dbip-country-lite-2026-01.csv (récupérés du Google Drive partagé).  

6. Lancer le nettoyage (ETL avec Spark, lit/sauve dans MinIO) :  
   `docker exec -it spark-master python /app/scripts/preprocess.py`  

7. Lancer l'entraînement (ML avec PySpark, sauve prédictions en Parquet dans MinIO) :  
   `docker exec -it spark-master python /app/scripts/train_model.py`  

8. Accéder à Trino : http://localhost:8081  
   Exécuter les requêtes de queries.sql pour détecter les intrusions (basé sur la colonne "prediction").  

## Résultats obtenus

Accuracy : 1.0  
Precision / Recall / F1 pour la classe Intrusion (1) : 1.0  
Le modèle détecte parfaitement les tentatives d'intrusion sur ce dataset.  
(Note : Si accuracy parfaite suspecte, vérifier balance du dataset via Spark.)
