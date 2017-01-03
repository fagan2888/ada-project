name := "features"

version := "1.0"

scalaVersion := "2.10.5"

libraryDependencies ++= Seq(
  "org.apache.spark" %% "spark-core" % "1.6.2",
  "org.apache.spark"  %% "spark-sql" % "1.6.2",
  "com.databricks" %% "spark-csv" % "1.4.0" % "provided"
)

scalaSource in Compile := baseDirectory.value / "src"
