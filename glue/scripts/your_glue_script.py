# NOTE: If you edit this file on Windows, ensure your editor saves it with
# Unix-style line endings (LF), not Windows-style (CRLF), to prevent
# script execution errors inside the Linux container.
import sys
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from awsglue.job import Job
from awsglue.utils import getResolvedOptions
from pyspark.sql import SparkSession
import pyspark.sql.functions as F

import os

# Check for an environment variable to determine if we are running locally.
# This is the only change needed to make your script portable.
if os.environ.get('GLUE_ENV') == 'local':
    # In the local environment, we'll write to the default catalog (our Hive simulation).
    CATALOG_NAME = ""
else:
    # In the real AWS environment, we'll use the glue_catalog.
    CATALOG_NAME = "glue_catalog."

# --- Boilerplate AWS Glue Setup ---
# @params: [JOB_NAME, region]
args = getResolvedOptions(sys.argv, ['JOB_NAME', 'region'])

# --- SparkSession Configuration ---
# UPDATED: Added a configuration to name the local Hive catalog 'glue_catalog'.
# This allows the use of 'glue_catalog.database_name' syntax, matching the AWS environment.
spark = (
    SparkSession.builder.appName("LocalGlueJob")
    .config(
        "spark.sql.warehouse.dir", "file:///home/glue_user/spark-warehouse"
    ).config(
        "spark.hadoop.fs.s3a.endpoint", "http://localstack:4566"
    ).config(
        "spark.hadoop.fs.s3a.aws.credentials.provider","org.apache.hadoop.fs.s3a.SimpleAWSCredentialsProvider"
    ).config(
        "park.hadoop.fs.s3a.access.key","test"
    ).config(
        "park.hadoop.fs.s3a.secret.key","test"
    ).config(
        "spark.hadoop.fs.s3a.path.style.access","true"
    ).config(
        "javax.jdo.option.ConnectionURL",
        "jdbc:derby:;databaseName=/home/glue_user/metastore_db;create=true",
    )
    .enableHiveSupport()  # This enables Hive integration
    .getOrCreate()
)

sc = spark.sparkContext
glueContext = GlueContext(sc, region_name=args['region'])
job = Job(glueContext)
job.init(args['JOB_NAME'], args)

print("Spark and Glue contexts initialized successfully.")

# --- Main ETL Logic ---
try:
    # Define database and table names
    database_name = "local_db"
    table_name = "local_table"

    # 1. Create a Database using the 'glue_catalog' syntax to match your AWS script
    print(f"Attempting to create database: {CATALOG_NAME}{database_name}")
    spark.sql(f"CREATE DATABASE IF NOT EXISTS {CATALOG_NAME}{database_name}")
    spark.sql(f"USE {CATALOG_NAME}{database_name}")
    print(f"Successfully created and switched to database '{CATALOG_NAME}{database_name}'.")

    # 2. Create a sample DataFrame
    print("Creating a sample DataFrame...")
    data = [
        (1, "Alice", 34, "2023-01-15"),
        (2, "Bob", 45, "2023-02-20"),
        (3, "Charlie", 29, "2023-03-10"),
    ]
    columns = ["id", "name", "age", "join_date"]
    df = spark.createDataFrame(data, columns)
    df.show()

    # 3. Write the DataFrame to the Local Hive Metastore
    print(f"Writing DataFrame to managed table: {table_name}")
    df.write.mode("overwrite").saveAsTable(table_name)
    print(f"Successfully wrote data to '{CATALOG_NAME}{database_name}.{table_name}'.")

    # 4. Read the data back from the metastore to verify
    print("Verifying data by reading from the metastore table...")
    read_df = spark.sql(f"SELECT * FROM {table_name}")
    read_df.show()
    print("Verification successful!")

except Exception as e:
    print(f"An error occurred during the ETL process: {e}")
    raise e

finally:
    # --- Job Commit ---
    job.commit()
    print("Job committed successfully.")
