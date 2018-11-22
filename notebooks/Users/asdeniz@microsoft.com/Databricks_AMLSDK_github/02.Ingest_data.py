# Databricks notebook source
# MAGIC %md
# MAGIC Azure ML & Azure Databricks notebooks by Parashar Shah.
# MAGIC 
# MAGIC Copyright (c) Microsoft Corporation. All rights reserved.
# MAGIC 
# MAGIC Licensed under the MIT License. 

# COMMAND ----------

# MAGIC %md Please ensure you have run all previous notebooks in sequence before running this.

# COMMAND ----------

# MAGIC %md #Data Ingestion

# COMMAND ----------

import os
import urllib

# COMMAND ----------

# Download AdultCensusIncome.csv from Azure CDN. This file has 32,561 rows.
basedataurl = "https://amldockerdatasets.azureedge.net"
datafile = "AdultCensusIncome.csv"
datafile_dbfs = os.path.join("/dbfs", datafile)

if os.path.isfile(datafile_dbfs):
    print("found {} at {}".format(datafile, datafile_dbfs))
else:
    print("downloading {} to {}".format(datafile, datafile_dbfs))
    urllib.request.urlretrieve(os.path.join(basedataurl, datafile), datafile_dbfs)

# COMMAND ----------

# Create a Spark dataframe out of the csv file.
data_all = sqlContext.read.format('csv').options(header='true', inferSchema='true', ignoreLeadingWhiteSpace='true', ignoreTrailingWhiteSpace='true').load(datafile)
print("({}, {})".format(data_all.count(), len(data_all.columns)))
data_all.printSchema()

# COMMAND ----------

#renaming columns
columns_new = [col.replace("-", "_") for col in data_all.columns]
data_all = data_all.toDF(*columns_new)
data_all.printSchema()

# COMMAND ----------

display(data_all.limit(5))

# COMMAND ----------

# MAGIC %md #Data Preparation

# COMMAND ----------

# Choose feature columns and the label column.
label = "income"
xvals_all = set(data_all.columns) - {label}

#dbutils.widgets.remove("xvars_multiselect")
dbutils.widgets.removeAll()

dbutils.widgets.multiselect('xvars_multiselect', 'hours_per_week', xvals_all)
xvars_multiselect = dbutils.widgets.get("xvars_multiselect")
xvars = xvars_multiselect.split(",")

print("label = {}".format(label))
print("features = {}".format(xvars))

data = data_all.select([*xvars, label])

# Split data into train and test.
train, test = data.randomSplit([0.75, 0.25], seed=123)

print("train ({}, {})".format(train.count(), len(train.columns)))
print("test ({}, {})".format(test.count(), len(test.columns)))

# COMMAND ----------

# MAGIC %md #Data Persistence

# COMMAND ----------

# Write the train and test data sets to intermediate storage
train_data_path = "AdultCensusIncomeTrain"
test_data_path = "AdultCensusIncomeTest"

train_data_path_dbfs = os.path.join("/dbfs", "AdultCensusIncomeTrain")
test_data_path_dbfs = os.path.join("/dbfs", "AdultCensusIncomeTest")

train.write.mode('overwrite').parquet(train_data_path)
test.write.mode('overwrite').parquet(test_data_path)
print("train and test datasets saved to {} and {}".format(train_data_path_dbfs, test_data_path_dbfs))

# COMMAND ----------

dbutils.notebook.exit("success")

# COMMAND ----------

