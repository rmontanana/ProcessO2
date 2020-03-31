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

    def test_loads_correct_data_from_file(self):
        first = datetime(2020, 3, 27, 2, 29, 16)
        second = datetime(2020, 3, 27, 2, 29, 20)
        data = [[first, 96, 77, 0, 0], [second, 96, 77, 0, 0]]
        output = pd.DataFrame(data, columns=self.header_output)
        computed = self.model.load_file(self.files[1])
        # Compare the data
        for col in output.columns:
            test = output[col].values == computed[col].values
            if not test.all():
                print(output[col].values, ' != ', computed[col].values)
            self.assertTrue(test.all())