import configparser
import datetime
import unittest
from io import StringIO

import pandas as pd

from ExtractO2 import ExtractO2
from ProcessO2 import ProcessO2

class ExtractO2_test(unittest.TestCase):
    _folder = 'tests/testdir/*.csv'
    _config_file = 'config.cfg'
    _files = ['tests/testdir/example1.csv', 'tests/testdir/example2.csv']

    def __init__(self, *args, **kwargs):
        load_model = ProcessO2(self._folder)
        self._model = ExtractO2(load_model.get_all_data())
        parser = configparser.RawConfigParser()
        parser.read(self._config_file)
        self._header_output = [
            x for x in parser._sections['OUTPUT_HEADER'].values()]
        self._date_format = parser._sections['DATETIME']['date_format']
        super(ExtractO2_test, self).__init__(*args, **kwargs)

    def test_returns_a_correct_date(self):
        computed = self._model.index_date(datetime.datetime(2020, 4, 1))
        expected = datetime.date(2020, 4, 1).strftime(self._date_format)
        self.assertEqual(computed, expected)

    def compare(self, expected, computed):
        # Compare two DataFrames
        for col in expected.columns:
            test = expected[col].values == computed[col].values
            result = test.all()
            if not result:
                print(expected[col].values, ' != ', computed[col].values)
                print("=============Expected=================")
                print(expected.head())
                print("=============Computed=================")
                print(computed.head())
                print("======================================")
            self.assertTrue(result)

    def build_df(self, string):
        return pd.read_csv(StringIO(string))

    def test_returns_correct_days_nights(self):
        col = self._header_output[0]
        computed_days, computed_nights = self._model.compute_days_nights()
        real_nights = self.build_df("""FechaHora,SpO2(%),Pulso(lpm),Movimiento,Vibración
                                            2020-03-28 02:29:16,       96,          77,        0,          0
                                            2020-03-28 02:29:20,       96,         77,         0,          0""")
        real_days = pd.read_csv(StringIO("""FechaHora,SpO2(%),Pulso(lpm),Movimiento,Vibración
                                            2020-03-29 14:23:45,       94,          83,          33,          0
                                            2020-03-29 14:23:49,       94,          87,          35,          0"""))
        self.compare(real_days.set_index(col), computed_days)
        self.compare(real_nights.set_index(col), computed_nights)

    def test_returns_correct_groupby_info(self):
        col_index = self._header_output[0]
        col = self._header_output[1]
        computed = self._model.feature_info(col)
        expected = self.build_df("""FechaHora,count,mean,std,min,25%,50%,75%,max
                                2020-03-28,2.0,96.0,0.0,96.0,96.0,96.0,96.0,96.0
                                2020-03-29,2.0,94.0,0.0,94.0,94.0,94.0,94.0,94.0""").set_index(col_index)
        self.compare(expected, computed)

    def test_dates_info(self):
        c_ini, c_end, c_days = self._model.dates_info()
        e_ini = datetime.date(2020, 3, 28).strftime(self._date_format)
        e_end = datetime.date(2020, 3, 29).strftime(self._date_format)
        e_days = 1

        self.assertEqual(e_ini, c_ini)
        self.assertEqual(e_end, c_end)
        self.assertEqual(e_days, c_days)

    def test_num_records(self):
        days, nights = self._model.compute_days_nights()
        computed_records = [self._model.num_records(), self._model.num_records(
            days), self._model.num_records(days)]
        expected_records = [4, 2, 2]
        for expected, computed in zip(expected_records, computed_records):
            self.assertEqual(expected, computed)
