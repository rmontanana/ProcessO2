'''
__author__ = "Ricardo Montañana Gómez"
__copyright__ = "Copyright 2020, Ricardo Montañana Gómez"
__license__ = "GPLv3"
__version__ = "1.0"
Process folder with O2 measures in csv files
'''
import glob
import csv
import pandas as pd
import numpy as np
from datetime import datetime
import configparser
import io

class ProcessO2:
    folder = ''  # Folder with csv data files
    config_file = 'config.cfg'
    header_csv = []
    header_output = []
    null_values = False
    daylight = ''

    def __init__(self, folder, null_data=False):
        """
        Load the configuration file and initializes the headers
        """
        self.folder = folder
        parser = configparser.RawConfigParser()
        parser.read(self.config_file)
        self.header_csv = [x for x in parser._sections['CSV_HEADER'].values()]
        self.header_output = [x for x in parser._sections['OUTPUT_HEADER'].values()]
        self.null_values = null_data
        self.daylight = parser._sections['MISC']['daylight_saving']

    def get_headers(self):
        """
        Return a tuple with the headers that the class works with
        @return: tuple
        """
        return (self.header_csv, self.header_output)

    def check_duplicated_data(self, file_name):
        """
        Checks if there is duplicated content in file as it happens sometimes, just counting csv headers
        @param: string file_name
        @return: bool
        """
        with open(file_name) as f:
            return f.read().count(self.header_csv[0]) > 1
    
    def get_file_contents(self, file_name):
        """
        Gets the file content removing possibly duplicated content
        @param: string file_name
        @return: string content of the file
        """
        with open(file_name) as f:
            if self.check_duplicated_data(file_name):
                token = self.header_csv[0]
                content = f.read()
                position = content.find(token, 10)
                return content[0:position]
            else:
                return f.read()
        
    def get_duplicated_files(self):
        """
        Return a list of files with duplicated data
        @return: list
        """
        result = []
        for file_name in self.files():
            num = self.check_duplicated_data(file_name)
            result.append(f"File: [{file_name}] #headers: [{num}]")
        return result

    def files(self):
        """
        Return list of files in folder
        """
        return glob.glob(self.folder)
    
    def get_all_data(self):
        """
        Return a DataFrame with all the data in the folder
        @return: DataFrame
        """
        res = None
        for file_name in self.files():
            if res is None:
                res = self.load_file(file_name)
            else:
                res = pd.concat([res, self.load_file(file_name)])
        return res
    
    def process_date(self, input_date):
        """
        Extract a datetime object from the Time field received removing special char and 1970's dates
        @param: string input_data
        @return: datetime object   
        """
        # Remove special char ', ' in date
        real_date = input_date[0:15] + ' ' + input_date[-4:]
        if input_date[-4:] == '1970':
            # Filter 1970 dates generated on the daylight saving day keeping only the time            
            real_date = real_date[0:8] + ' ' + self.daylight
        return datetime.strptime(real_date, '%H:%M:%S %b %d %Y')

    def load_file(self, file_name):
        """
        Return a DataFrame with the file content
        @return: DataFrame
        """
        source = self.get_file_contents(file_name)
        output = []
        content = csv.DictReader(io.StringIO(source), fieldnames=self.header_csv)
        next(content)
        for row in content:
            line = [x for x in row.values()]
            line[0] = self.process_date(line[0])
            # add line to output
            output.append(line)
        # Change data types and remove null values (come as 255)
        num_type, null_value = ('int32', 255)
        result = pd.DataFrame(output, columns=self.header_output, dtype=num_type)
        columns_to_change = self.header_output.copy()
        del columns_to_change[0]  # Remove the Time column  
        columns = {x: num_type for x in columns_to_change}
        columns[self.header_output[0]] = 'datetime64[ns]'
        if not self.null_values:
            result = result.replace(f"{null_value}", np.nan).dropna()
        return  result.astype(columns)