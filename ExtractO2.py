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
    data = None
    header = []
    config_file = 'config.cfg'
    night_st = '00:00'
    night_en = '12:00'
    day_st = '12:01'
    day_en = '23:59'

    def __init__(self, data):
        """
        Load the configuration file and initializes the headers
        """
        parser = configparser.RawConfigParser()
        parser.read(self.config_file)
        self.header = [x for x in parser._sections['OUTPUT_HEADER'].values()]
        self.daylight = parser._sections['MISC']['daylight_saving']
        self.date_format = parser._sections['MISC']['date_format']
        self.data = data.set_index(self.header[0])

    def index_date(self, index):
        """
        Returns the date of the index
        """
        return datetime.date(index.year, index.month, index.day).strftime(self.date_format)

    def info(self):
        days, nights = self.compute_days_nights()
        return {
            'total': self.data_info_frame(self.data),
            'dias': self.data_info_frame(days),
            'noches': self.data_info_frame(nights)
        }

    def dates_info(self, data=None):
        data = self.data if data is None else data
        ini, end = self.index_date(data.index.min()), self.index_date(data.index.max())
        return (ini, end, (data.index.max() - data.index.min()).days)

    def num_records(self, data=None):
        data = self.data if data is None else data
        return data.shape[0]

    def data_info_frame(self, data):
        num_records = {'num_registros': data.shape[0]}
        dates = {'Fecha inicio': self.index_date(data.index.min()), 'Fecha fin': self.index_date(data.index.max())}
        spo2 = {'SpO2': self.feature_info(self.header[1], data)}
        lbp = {'Latidos': self.feature_info(self.header[2], data)}
        return [num_records, dates, spo2, lbp]

    def feature_info(self, feature, data=None):
        data = self.data if data is None else data
        return data[feature].groupby(pd.Grouper(freq='d')).describe()

    def compute_days_nights(self):
        days = self.data.between_time(self.day_st, self.day_en)
        nights = self.data.between_time(self.night_st, self.night_en)
        return days, nights
