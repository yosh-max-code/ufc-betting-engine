from pyspark.sql import SparkSession
from pyspark.sql.types import DoubleType,IntegerType




spark = SparkSession.builder.appName("UFC Betting Engine").getOrCreate()

df = spark.read.csv("data/ufc-master.csv", header=True, inferSchema=True)

# Initialize our empty list for base columns shared fight data
base_columns = []
# Loop through all columns to find the shared names like date etc
for column_name in df.columns:
    if not column_name.startswith('R_') and not column_name.startswith('B_'):
        base_columns.append(column_name)
        #print(base_columns)

    #STATS for each fighter side
red_cols = []
blue_cols = []

    #fighter specific stats and creating a single column for both 
clean_columns = []

    # Loop through all columns again to categorize them
for column_name in df.columns:
    if column_name.startswith('R_'):
        red_cols.append(column_name)
        clean_name = column_name.removeprefix('R_')
        clean_columns.append(clean_name)

    elif column_name.startswith('B_'):
        blue_cols.append(column_name)

for column_name in clean_columns:
    red_col = f"R_{column_name}"
    blue_col = f"B_{column_name}"
    
    if df.schema[red_col].dataType == DoubleType() or df.schema[red_col].dataType == IntegerType():
        df = df.withColumn(f"dif_{column_name}", df[blue_col] - df[red_col])

#df.select([c for c in df.columns if c.startswith("dif_")]).show(5)
df.write.mode("overwrite").parquet("data/processed_features")