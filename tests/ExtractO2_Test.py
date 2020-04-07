import unittest
from ProcessO2 import ProcessO2
from ExtractO2 import ExtractO2
import pandas as pd
from io import StringIO
import datetime
import configparser

class ExtractO2_Test(unittest.TestCase):
    folder = 'tests/testdir/*.csv'
    config_file = 'config.cfg'
    header_output = []
    date_format = ''
    files = ['tests/testdir/example1.csv', 'tests/testdir/example2.csv']
    model = None

    def __init__(self, *args, **kwargs):
        load_model = ProcessO2(self.folder)
        self.model = ExtractO2(load_model.get_all_data())
        parser = configparser.RawConfigParser()
        parser.read(self.config_file)
        self.header_output = [x for x in parser._sections['OUTPUT_HEADER'].values()]
        self.date_format = parser._sections['MISC']['date_format']
        super(ExtractO2_Test, self).__init__(*args, **kwargs)

    def test_returns_a_correct_date(self):
        computed = self.model.index_date(datetime.datetime(2020, 4, 1))
        expected = datetime.date(2020, 4, 1).strftime(self.date_format)
        self.assertTrue(computed == expected)

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
        col = self.header_output[0]
        computed_days, computed_nights = self.model.compute_days_nights()
        real_nights = self.build_df("""FechaHora,SpO2(%),Pulso(lpm),Movimiento,Vibración
                                            2020-03-28 02:29:16,       96,          77,        0,          0
                                            2020-03-28 02:29:20,       96,         77,         0,          0""" )
        real_days = pd.read_csv(StringIO("""FechaHora,SpO2(%),Pulso(lpm),Movimiento,Vibración
                                            2020-03-29 14:23:45,       94,          83,          33,          0
                                            2020-03-29 14:23:49,       94,          87,          35,          0""" ))
        self.compare(real_days.set_index(col), computed_days)
        self.compare(real_nights.set_index(col), computed_nights)

    def test_returns_correct_groupby_info(self):
        col_index = self.header_output[0]
        col = self.header_output[1]
        computed = self.model.feature_info(col)
        expected = self.build_df("""FechaHora,count,mean,std,min,25%,50%,75%,max
                                2020-03-28,2.0,96.0,0.0,96.0,96.0,96.0,96.0,96.0
                                2020-03-29,2.0,94.0,0.0,94.0,94.0,94.0,94.0,94.0""").set_index(col_index)
        self.compare(expected, computed)
    
    def test_dates_info(self):
        c_ini, c_end, c_days = self.model.dates_info()
        e_ini = datetime.date(2020, 3, 28).strftime(self.date_format)
        e_end = datetime.date(2020, 3, 29).strftime(self.date_format)
        e_days = 1
        self.assertEqual(e_ini, c_ini)
        self.assertEqual(e_end, c_end)
        self.assertEqual(e_days, c_days)

    def test_num_records(self):
        days, nights = self.model.compute_days_nights()
        computed_records = [self.model.num_records(), self.model.num_records(days), self.model.num_records(days)]
        expected_records = [4, 2, 2]
        for expected, computed in zip(expected_records, computed_records):
            self.assertEqual(expected, computed)


