import unittest
from ProcessO2 import ProcessO2
import pandas as pd
from datetime import datetime
import configparser

class ProcessO2_Test(unittest.TestCase):
    folder = 'tests/testdir/*.csv'
    config_file = 'config.cfg'
    header_csv = []
    header_output = []
    files = ['tests/testdir/example2.csv', 'tests/testdir/example1.csv']
    model = None

    def __init__(self, *args, **kwargs):
        self.model = ProcessO2(self.folder)
        parser = configparser.RawConfigParser()
        parser.read(self.config_file)
        self.header_csv = [x for x in parser._sections['CSV_HEADER'].values()]
        self.header_output = [x for x in parser._sections['OUTPUT_HEADER'].values()]
        super(ProcessO2_Test, self).__init__(*args, **kwargs)

    def test_returns_a_file_list(self):
        file_set = self.model.files()
        for file_name in self.files:
            self.assertIn(file_name, file_set)
    
    def test_use_proper_headers(self):
        head_csv, head_output = self.model.get_headers()
        self.assertEqual(self.header_csv, head_csv)
        self.assertEqual(self.header_output, head_output)
    
    def data_example1(self):
        first = datetime(2020, 3, 27, 2, 29, 16)
        second = datetime(2020, 3, 27, 2, 29, 20)
        data = [[first, 96, 77, 0, 0], [second, 96, 77, 0, 0]]
        return pd.DataFrame(data, columns=self.header_output)
    
    def data_example2(self):
        first = datetime(2020, 3, 28, 14, 23, 45)
        second = datetime(2020, 3, 28, 14, 23, 49)
        data = [[first, 94, 83, 33, 0], [second, 94, 87, 35, 0]]
        return pd.DataFrame(data, columns=self.header_output)

    def test_loads_correct_data_from_file(self):
        expected = self.data_example1()
        computed = self.model.load_file(self.files[1])
        self.compare(expected, computed)

    def compare(self, expected, computed):
        # sort DataFrames to make a more robust the comparison and create a deterministic result
        col = self.header_output[0]
        expected.sort_values(by=[col], inplace=True)
        computed.sort_values(by=[col], inplace=True)
        # Compare two DataFrames
        for col in expected.columns:
            test = expected[col].values == computed[col].values
            if not test.all():
                print(expected[col].values, ' != ', computed[col].values)
            self.assertTrue(test.all())

    def test_loads_correct_data_from_folder(self):
        expected = pd.concat([self.data_example1(), self.data_example2()])
        computed = self.model.get_all_data()
        self.compare(expected, computed)
