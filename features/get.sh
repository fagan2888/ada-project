rm ../out.csv/* ../features.csv
hadoop fs -get /user/ahaeflig/out/out.csv/part-00000 ../out.csv
mv ../out.csv/part-00000 ../features.csv
