ANOVA
=====

This package implements a simple one-way ANOVA using Apache Spark.
The goal of the package is to provide compact PySpark code.

The calculations are tested against scipy.

The application can be run locally on a dataframe that provides a column with the conditions and a column with the measurements.
Install the application with Poetry:

```
poetry install
```

Once installed the application can be run locally using the command shown below.

```
Usage: one-way-anova [OPTIONS]

Options:
  --input-path TEXT       The path to the input data  [required]
  --input-format TEXT     The format of the input data
  --condition-col TEXT    The column containing the conditions.
  --measurement-col TEXT  The column containing the measurements.
  --output-path TEXT      The path to the output data  [required]
  --output-format TEXT    The format of the output data
  --help                  Show this message and exit.

```
Note that the libraries should be provided during submission to a cluster.
