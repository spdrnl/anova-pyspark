from logging import getLogger

import click
from pyspark.sql import Window, SparkSession
from pyspark.sql import functions as sf
from pyspark.sql.dataframe import DataFrame
from pyspark.sql.functions import col, udf
from pyspark.sql.types import FloatType

logger = getLogger(__name__)


@udf(returnType=FloatType())
def calc_f_probability(f_value, df_between, df_within):
    # Only import on worker
    from scipy.stats import f

    # Calculate the probability
    p_value = 1 - f.cdf(f_value, df_between, df_within).item()

    return p_value


def calc(df: DataFrame, conditions_column: str = 'condition', measurements_col: str = 'measurement') -> DataFrame:
    """
    Calculates one-way ANOVA statistics using PySpark.

    :param df: A DataFrame with the data.
    :param conditions_column: The column that indicates the condition or level.
    :param measurements_col: The column that contains the measurement value.
    :return: a DataFrame containing relevant statistics.
    """

    # Assert conditions that would impede proper calculations
    assert conditions_column in df.columns
    assert measurements_col in df.columns
    assert not df.isEmpty()

    # Calculate the statistics
    stats = (
        df.withColumn('all', sf.lit(1))
        .withColumn('overall_mean', sf.mean(col(measurements_col)).over(Window.partitionBy('all')))
        .withColumn('overall_error', sf.pow(col(measurements_col) - col('overall_mean'), 2))
        .withColumn('group_mean', sf.mean(col(measurements_col)).over(Window.partitionBy(conditions_column)))
        .withColumn('group_error', sf.pow(col(measurements_col) - col('group_mean'), 2))
        .agg(
            sf.sum('overall_error').alias('ss_total'),
            sf.sum('group_error').alias('ss_within'),
            sf.countDistinct(conditions_column).alias('conditions'),
            sf.sum('all').alias('n'),
        )
        .withColumn('df_within', col('n') - col('conditions'))
        .withColumn('ms_within', col('ss_within') / col('df_within'))
        .withColumn('ss_between', col('ss_total') - col('ss_within'))
        .withColumn('df_between', col('conditions') - sf.lit(1))
        .withColumn('ms_between', col('ss_between') / col('df_between'))
        .withColumn('F', col('ms_between') / col('ms_within'))
        .withColumn('p_value', calc_f_probability('F', 'df_between', 'df_within'))
        .select('ss_within', 'df_within', 'ms_within', 'ss_between', 'df_between', 'ms_between', 'F', 'p_value')
    )
    return stats


@click.command()
@click.option('--input-path', required=True, help='The path to the input data.')
@click.option('--input-format', default='parquet', help='The format of the input data (csv or parquet).')
@click.option('--condition-col', default='condition', help='The column containing the conditions.')
@click.option('--measurement-col', default='measurement', help='The column containing the measurements.')
@click.option('--output-path', required=True, help='The path to the output data.')
@click.option('--output-format', default='parquet', help='The format of the output data.')
def main(input_path: str, input_format: str, condition_col: str, measurement_col: str, output_path: str, output_format: str):
    logger.info(f'Calculating a one-way ANOVA using the following parameters:')
    logger.info(f'input_path = {input_path}')
    logger.info(f'input_format = {input_format}')
    logger.info(f'condition_col = {condition_col}')
    logger.info(f'measurement_col = {measurement_col}')
    logger.info(f'output_path = {output_path}')
    logger.info(f'output_format = {output_format}')

    # Perform the calculation
    spark = None
    try:
        # Create a Spark session
        logger.info('Creating Spark session.')
        spark = SparkSession.builder.appName('One-way ANOVA').getOrCreate()

        # Check if the path exists
        # TODO

        # Create a dataframe
        logger.info(f'Reading input data from {input_path} with format {input_format}.')
        if input_format == 'csv':
            logger.info('Reading csv file with header=True and inferSchema=True, which is slow.')
            input_df = spark.read.csv(str(input_path), header=True, inferSchema=True)
        elif input_format == 'parquet':
            input_df = spark.read.parquet(str(input_path))
        else:
            logger.error(f'Found unsupported input format {input_format}. Supported formats are csv and parquet.')
            return

        # Calculate the stats
        logger.info('Performing one-way ANOVA test.')
        output_df = calc(input_df, condition_col, measurement_col)

        # Output the results
        logger.info(f'Writing output data to {output_path} with format {output_format}.')
        (output_df.write.option('header', 'true').mode('overwrite').save(path=output_path, format=output_format))

    except Exception as e:
        logger.error(e)
    finally:
        if spark:
            spark.stop()


if __name__ == '__main__':
    main()
