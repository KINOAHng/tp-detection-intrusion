from pyspark.sql import SparkSession
from pyspark.sql.functions import udf, col
from pyspark.sql.types import StringType, LongType
import ipaddress

spark = SparkSession.builder \
    .appName("Preprocess Logs") \
    .config("spark.hadoop.fs.s3a.endpoint", "http://minio:9000") \
    .config("spark.hadoop.fs.s3a.access.key", "minioadmin") \
    .config("spark.hadoop.fs.s3a.secret.key", "minioadmin123") \
    .config("spark.hadoop.fs.s3a.path.style.access", "true") \
    .config("spark.hadoop.fs.s3a.impl", "org.apache.hadoop.fs.s3a.S3AFileSystem") \
    .getOrCreate()

# Lire les fichiers depuis MinIO
df_logs = spark.read.csv("s3a://logs/Network_logs.csv", header=True, inferSchema=True)
df_geo = spark.read.csv("s3a://logs/dbip-country-lite-2026-01.csv", header=False, schema="start_ip STRING, end_ip STRING, country_code STRING")

# Convertir IPs en long pour comparaison (IPv4/6 mix, mais assume IPv4 pour simplicité ; adapte si IPv6)
df_geo = df_geo.withColumn("start_ip", col("start_ip").cast(LongType())) \
               .withColumn("end_ip", col("end_ip").cast(LongType()))

def ip_to_country(ip_str):
    try:
        ip = ipaddress.ip_address(ip_str)
        if ip.is_private:
            return 'Private'
        if ip.version != 4:  # Skip IPv6 pour l'instant
            return 'Unknown'
        ip_int = int(ip)
        matching = df_geo.filter((col("start_ip") <= ip_int) & (ip_int <= col("end_ip"))).select("country_code").first()
        return matching["country_code"] if matching else 'Unknown'
    except:
        return 'Invalid'

udf_ip_to_country = udf(ip_to_country, StringType())

# Appliquer mapping
df_logs = df_logs.withColumn("src_country", udf_ip_to_country(col("Source_IP"))) \
                 .withColumn("dst_country", udf_ip_to_country(col("Destination_IP"))) \
                 .drop("Source_IP", "Destination_IP")

# Vérifier types (inférés, mais force si besoin ; ex. Port int, Payload_Size double)
df_logs = df_logs.withColumn("Port", col("Port").cast("int")) \
                 .withColumn("Payload_Size", col("Payload_Size").cast("double"))

# Sauvegarder cleaned dans MinIO (CSV, mais partitionné si gros)
df_logs.write.mode("overwrite").csv("s3a://logs/cleaned_network_logs.csv", header=True)

print("Preprocessing terminé ! Fichier cleaned sauvegardé dans MinIO.")
spark.stop()
