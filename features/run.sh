hadoop fs -rm -R /user/ahaeflig/out/out.csv
spark-submit --packages com.databricks:spark-csv_2.10:1.4.0 --class "main.scala.Features" --master yarn-client  --num-executors 20  features_2.10-1.0.jar
# spark-submit --packages com.databricks:spark-csv_2.10:1.4.0 --class "main.scala.Features" --master yarn-cluster  --num-executors 20  features_2.10-1.0.jar
