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

Example output
--------------
```
ss_within,df_within,ms_within,ss_between,df_between,ms_between,F,p_value
13.333333333333334,6,2.2222222222222223,0.2222222222222232,2,0.1111111111111116,0.05000000000000022,0.9516215
```
Installing
----------
The application can be installed locally on a dataframe that provides a column with the conditions and a column with the measurements.
Install the application with Poetry:

```
poetry install
```

Running
-------
Once installed locally the application can be run locally using the command shown below.

```
Usage: one-way-anova [OPTIONS]

  Calculate an one-way ANOVA using PySpark.

Options:
  --input-path TEXT       The path to the input data.  [required]
  --input-format TEXT     The format of the input data (csv or parquet).
  --condition-col TEXT    The column containing the conditions.
  --measurement-col TEXT  The column containing the measurements.
  --output-path TEXT      The path to the output data.  [required]
  --output-format TEXT    The format of the output (csv or parquest, but
                          others could work.).
  --help                  Show this message and exit.

```
Alternatively the application ```anova.one_way``` can be submitted to a cluster.
Note that the required libraries in the .toml file should be provided during submission.
