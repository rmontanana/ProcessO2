"""
__author__ = "Ricardo Montañana Gómez"
__copyright__ = "Copyright 2020, Ricardo Montañana Gómez"
__license__ = "GPLv3"
__version__ = "1.0"
Extracts info from the SpO2 DataFrame
"""
import configparser
import datetime

import pandas as pd


class ExtractO2:
    """Extract relevant information of the DataFrame passed with SpO2 measures


    """
    
    _config_file = 'config.cfg'
    
    def __init__(self, data: pd.DataFrame):
        """Load the configuration file and initializes the headers

        :param data: The dataset to work with
        :type data: pd.DataFrame
        """
        parser = configparser.RawConfigParser()
        parser.read(self._config_file)
        self._header = [x for x in parser._sections['OUTPUT_HEADER'].values()]
        self.daylight = parser._sections['DATETIME']['daylight_saving']
        self.date_format = parser._sections['DATETIME']['date_format']
        self._night_st = parser._sections['DATETIME']['night_start']
        self._night_en = parser._sections['DATETIME']['night_end']
        self._day_st = parser._sections['DATETIME']['day_start']
        self._day_en = parser._sections['DATETIME']['day_end']
        self.data = data.set_index(self._header[0])

    def index_date(self, index: datetime.datetime) -> datetime.date:
        """ Returns the date of an index

        :param index: the datetime index of a row
        :type index: datetime.datetime
        :return: The date of the index passed as argument
        :rtype: datetime.date
        """
        return datetime.date(index.year, index.month, index.day).strftime(self.date_format)

    def info(self) -> dict:
        """ Generate a summary

        :return: Dictionary with keys to acces each section
        :rtype: dict
        """
        days, nights = self.compute_days_nights()
        return {
            'total': self.data_info_frame(self.data),
            'dias': self.data_info_frame(days),
            'noches': self.data_info_frame(nights)
        }

    def dates_info(self, data: pd.DataFrame = None) -> tuple:
        """ Return information of the inital and final date of the dataset

        :param data: The dataset, defaults to None
        :type data: DataFrame, optional
        :return: first date, last date, number of days
        :rtype: tuple
        """
        data = self.data if data is None else data
        ini, end = self.index_date(
            data.index.min()), self.index_date(data.index.max())
        return (ini, end, (data.index.max() - data.index.min()).days)

    def num_records(self, data=None):
        """ Return the number of records of a dataaset

        :param data: the dataset if not set takes the global dataset, defaults to None
        :type data: str, optional
        :return: the number of records
        :rtype: int
        """
        data = self.data if data is None else data
        return data.shape[0]

    def data_info_frame(self, data: pd.DataFrame) -> list:
        num_records = {'num_registros': data.shape[0]}
        dates = {'Fecha inicio': self.index_date(
            data.index.min()), 'Fecha fin': self.index_date(data.index.max())}
        spo2 = {'SpO2': self.feature_info(self._header[1], data)}
        lbp = {'Latidos': self.feature_info(self._header[2], data)}
        return [num_records, dates, spo2, lbp]

    def feature_info(self, feature: str, data=None) -> pd.DataFrame:
        """Generate the statistics of a feature of a dataset

        :param feature: The feature name as a column of the dataset
        :type feature: str
        :param data: The dataset, defaults to None
        :type data: pd.DataFrame, optional
        :return: Count, Min, Percentiles and Max value of the feature in the range
        :rtype: DataFrame
        """
        data = self.data if data is None else data
        return data[feature].groupby(pd.Grouper(freq='d')).describe()

    def compute_days_nights(self) -> tuple:
        """Splits the dataset into two datasets given a range of hours

        :return: DataFrame of the day, DataFrame of the night
        :rtype: tuple of DataFrame
        """
        days = self.data.between_time(self._day_st, self._day_en)
        nights = self.data.between_time(self._night_st, self._night_en)
        return days, nights
