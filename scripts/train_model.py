from pyspark.sql import SparkSession
from pyspark.ml.feature import StringIndexer, OneHotEncoder, VectorAssembler, StandardScaler
from pyspark.ml.classification import RandomForestClassifier
from pyspark.ml.evaluation import MulticlassClassificationEvaluator
from pyspark.ml import Pipeline
from pyspark.sql.functions import col

spark = SparkSession.builder \
    .appName("Train Intrusion Model") \
    .config("spark.hadoop.fs.s3a.endpoint", "http://minio:9000") \
    .config("spark.hadoop.fs.s3a.access.key", "minioadmin") \
    .config("spark.hadoop.fs.s3a.secret.key", "minioadmin123") \
    .config("spark.hadoop.fs.s3a.path.style.access", "true") \
    .config("spark.hadoop.fs.s3a.impl", "org.apache.hadoop.fs.s3a.S3AFileSystem") \
    .getOrCreate()

# Lire cleaned depuis MinIO
df = spark.read.csv("s3a://logs/cleaned_network_logs.csv", header=True, inferSchema=True)

# Cast label si besoin
df = df.withColumn("Intrusion", col("Intrusion").cast("double"))  # Pour MLlib, label en double

# Catégorielles et numériques
categorical_cols = ['Request_Type', 'Protocol', 'User_Agent', 'Status', 'Scan_Type', 'src_country', 'dst_country']
numerical_cols = ['Port', 'Payload_Size']

# Stages pipeline
indexers = [StringIndexer(inputCol=c, outputCol=c + "_index", handleInvalid="keep") for c in categorical_cols]
encoders = [OneHotEncoder(inputCol=c + "_index", outputCol=c + "_vec") for c in categorical_cols]
assembler = VectorAssembler(inputCols=[c + "_vec" for c in categorical_cols] + numerical_cols, outputCol="features")
scaler = StandardScaler(inputCol="features", outputCol="scaledFeatures")
rf = RandomForestClassifier(labelCol="Intrusion", featuresCol="scaledFeatures", numTrees=100)

pipeline = Pipeline(stages=indexers + encoders + [assembler, scaler, rf])

# Split
train_data, test_data = df.randomSplit([0.8, 0.2], seed=42)

# Train
model = pipeline.fit(train_data)

# Prédictions
predictions = model.transform(test_data)

# Éval
evaluator = MulticlassClassificationEvaluator(labelCol="Intrusion", predictionCol="prediction", metricName="accuracy")
accuracy = evaluator.evaluate(predictions)
print(f"Accuracy: {accuracy}")

# Sauvegarder prédictions (pour Trino) et model
predictions.write.mode("overwrite").parquet("s3a://logs/predictions.parquet")
model.write().overwrite().save("s3a://logs/random_forest_model")

spark.stop()
