# TP Détection d'Intrusion

**Auteur** : Maryvonne

## Objectif du projet
Détecter les tentatives d'intrusion à partir du fichier Network_logs.csv (sans information temporelle).  
Modèle principal : Random Forest sur les features après mapping des adresses IP vers codes pays / 'Private' / 'Invalid'.  
Accuracy obtenue : 100 % (sur set de test).

## Architecture Globale

Le schéma ci-dessous représente le flux de travail  :
[Sources de données : CSVs]
↓
[Ingestion / Upload dans MinIO]
↓
[Stockage : MinIO (bucket S3-like)]
↓
[Processing ETL : Spark (nettoyage + mapping IPs)]
↓
[Feature Engineering (encoding + scaling)]
↓
[ML Training : Random Forest (PySpark ML)]
↓
[Prédictions stockées dans MinIO]
↓
[Queries SQL & Détection : Trino]
↓
[Détection des intrusions (Intrusion = 1)]

**Explication du schéma** :  
C'est un flux linéaire qui montre comment les données passent d'une étape à l'autre.  
- Pas besoin de faire une image ou un dessin avec un logiciel : ce texte est suffisant et très clair sur GitHub (il s'affiche avec les flèches alignées).  
- C'est juste une représentation simple du processus : de haut en bas, chaque flèche signifie "puis".  
- Tu peux le voir comme une liste d'étapes connectées par des flèches.

## Contenu du repository
- docker-compose.yml : Lance MinIO, Spark et Trino automatiquement
- scripts/preprocess.py : Nettoyage des données et mapping des IP
- scripts/train_model.py : Entraînement et évaluation du modèle Random Forest
- queries.sql : Exemples de requêtes SQL pour Trino

## Comment relancer le projet
1. Installer Docker Desktop[](https://www.docker.com/products/docker-desktop).
2. Cloner le repository :  
   git clone https://github.com/KINOAHng/tp-detection-intrusion.git
3. Aller dans le dossier :  
   cd tp-detection-intrusion
4. Lancer les services :  
   docker-compose up -d
5. Accéder à MinIO : http://localhost:9001  
   Login : minioadmin  
   Password : minioadmin123  
   Créer un bucket "logs" et uploader Network_logs.csv + dbip-country-lite-2026-01.csv
6. Lancer le nettoyage :  
   docker exec -it spark-master python /app/scripts/preprocess.py
7. Lancer l'entraînement :  
   docker exec -it spark-master python /app/scripts/train_model.py
8. Accéder à Trino : http://localhost:8081  
   Exécuter les requêtes de queries.sql

## Résultats obtenus
Accuracy : 1.0  
Precision / Recall / F1 pour la classe Intrusion (1) : 1.0  
Le modèle détecte parfaitement les tentatives d'intrusion sur ce dataset.
