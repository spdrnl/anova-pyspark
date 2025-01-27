from logging import getLogger
from os.path import dirname
from pathlib import Path

import pandas as pd
import pytest
from pyspark.sql import SparkSession
from pyspark.sql.functions import col
from scipy.stats import f_oneway

from anova import one_way

logger = getLogger(__name__)


@pytest.fixture
def data_path_fixture():
    return Path(dirname(__file__)).parent / 'resource_dir' / 'one_way_data.csv'


@pytest.fixture
def spark_fixture():
    spark = SparkSession.builder.appName('One way anova tests').getOrCreate()
    yield spark


def read_test_data(spark_fixture, test_data_path):
    return spark_fixture.read.csv(str(test_data_path), header=True, schema='group int, value int')


def test_calc(spark_fixture, data_path_fixture):
    """
    Test one-way ANOVA with some sample data.

    :param spark_fixture: Spark support from pytest.
    :param test_data_path: Data path support from pytest.
    """
    # Sample data schema: (group, value)
    # data = [(1, 1), (1, 2), (1, 5),
    #         (2, 2), (2, 4), (2, 2),
    #         (3, 2), (3, 3), (3, 4)]

    # Read test data
    df = read_test_data(spark_fixture, data_path_fixture)

    # Calculate statistics
    stats = one_way.calc(df, 'group', 'value').collect()[0]

    # Create scipy reference data
    pandas_df = pd.read_csv(data_path_fixture)
    group1 = pandas_df[pandas_df['group'] == 1]['value'].values
    group2 = pandas_df[pandas_df['group'] == 2]['value'].values
    group3 = pandas_df[pandas_df['group'] == 3]['value'].values
    reference_result = f_oneway(group1, group2, group3)

    # Test assertions
    assert pytest.approx(stats['ss_within'], 0.0001) == 13.33333
    assert stats['df_within'] == 6
    assert pytest.approx(stats['ms_within'], 0.0001) == 2.22222

    assert pytest.approx(stats['ss_between'], 0.0001) == 0.22222
    assert stats['df_between'] == 2
    assert pytest.approx(stats['ms_between'], 0.0001) == 0.11111

    assert pytest.approx(stats['F'], 0.0001) == reference_result.statistic.item()
    assert pytest.approx(stats['p_value'], 0.0001) == reference_result.pvalue.item()


def test_assertions(spark_fixture, data_path_fixture):
    """
    Test the assertions that can impede proper calculation.

    :param spark_fixture: Spark support from pytest.
    """
    # Read test data
    df = read_test_data(spark_fixture, data_path_fixture)

    # Test dataframe not empty assertion
    with pytest.raises(AssertionError):
        one_way.calc(df.filter(col('value') < 0), 'group', 'value').collect()[0]

    # Test measurement column assertion
    with pytest.raises(AssertionError):
        one_way.calc(df.withColumnRenamed('value', 'xyz'), 'group', 'value').collect()[0]

    # Test group column assertion
    with pytest.raises(AssertionError):
        one_way.calc(df.withColumnRenamed('group', 'xyz'), 'group', 'value').collect()[0]
