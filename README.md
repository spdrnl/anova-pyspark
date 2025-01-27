ANOVA-PySpark
=============

This package implements a simple one-way ANOVA using Apache PySpark.

The goal of the package is:
- To provide compact PySpark code.
- To provide a dataframe to dataframe transformation that can be used in workflows.

The calculations are tested against scipy.

Data requirements
-----------------
The application can run an ANOVA on any dataframe that has the following type of columns:
```
condition, measurement
c1, 5.0
c1, 6.0
c2, 3.0
c2, 2.0
...

```

The names of these columns are configurable.

Installing
----------
The application can be run locally on a dataframe that provides a column with the conditions and a column with the measurements.
Install the application with Poetry:

```
poetry install
```

Running
-------
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
Note that the required libraries in the .toml file should be provided during submission to a cluster.
