"""
__author__ = "Ricardo Montañana Gómez"
__copyright__ = "Copyright 2020, Ricardo Montañana Gómez"
__license__ = "GPLv3"
__version__ = "1.0"
Process folder with O2 measures in csv files
"""
import configparser
import csv
import glob
import io
from datetime import datetime

import numpy as np
import pandas as pd


class ProcessO2:
    _config_file = 'config.cfg'

    def __init__(self, folder, null_data: bool = False):
        """Load the configuration file and initializes the headers

        :param folder: The folder that contains the files with the measures
        :type folder: str
        :param null_data: Wether return or not measures marked as null with a special value, defaults to False
        :type null_data: bool, optional
        """
        self._folder = folder
        parser = configparser.RawConfigParser()
        parser.read(self._config_file)
        self._header_csv = [x for x in parser._sections['CSV_HEADER'].values()]
        self._header_output = [
            x for x in parser._sections['OUTPUT_HEADER'].values()]
        self._null_values = null_data
        self._daylight = parser._sections['DATETIME']['daylight_saving']

    def get_headers(self) -> tuple:
        """ Return a tuple with the headers that the class works with

        :return: lists with the field names that came in csv files and the ones we want to have in the output
        :rtype: tuple
        """
        return (self._header_csv, self._header_output)

    def check_duplicated_data(self, file_name: str) -> bool:
        """ Checks if there is duplicated content in file as it happens sometimes, just counting csv headers

        :param file_name: the name of the file
        :type file_name: str
        :return: `True` if it has duplicated data `False` otherwise
        :rtype: bool
        """
        with open(file_name) as f:
            return f.read().count(self._header_csv[0]) > 1

    def get_file_contents(self, file_name: str) -> str:
        """ Gets the file content removing possibly duplicated content

        :param file_name: the name of the file
        :type file_name: str
        :return: the content of the file
        :rtype: string 
        """
        with open(file_name) as f:
            if self.check_duplicated_data(file_name):
                token = self._header_csv[0]
                content = f.read()
                position = content.find(token, 10)
                return content[0:position]
            else:
                return f.read()

    def get_duplicated_files(self) -> list:
        """ Return a list of files with duplicated data

        :return: File names in folder with (True) or without (False) duplicated data
        :rtype: list
        """
        result = []
        for file_name in self.files():
            num = self.check_duplicated_data(file_name)
            result.append(f"File: [{file_name}] #headers: [{num}]")
        return result

    def files(self) -> list:
        """ Build a list with the files in the folder

        :return: The list of files in the folder
        :rtype: list
        """
        return glob.glob(self._folder)

    def get_all_data(self) -> pd.DataFrame:
        """ Read all the files in the folder

        :return: a Pandas Dataframe with all the measures parsed
        :rtype: pd.DataFrame
        """
        res = None
        for file_name in self.files():
            if res is None:
                res = self.load_file(file_name)
            else:
                res = pd.concat([res, self.load_file(file_name)])
        return res

    def process_date(self, input_date: str) -> datetime:
        """ Extract a datetime object from the Time field received removing special char and 1970's dates

        :param input_date: The date that comes in the csv
        :type input_date: str
        :return: build a datetime object 
        :rtype: datetime
        """
        # Remove special char ', ' in date
        real_date = input_date[0:15] + ' ' + input_date[-4:]
        if input_date[-4:] == '1970':
            # Filter 1970 dates generated on the daylight saving day keeping only the time
            real_date = real_date[0:8] + ' ' + self._daylight
        return datetime.strptime(real_date, '%H:%M:%S %b %d %Y')

    def load_file(self, file_name: str) -> pd.DataFrame:
        """ Read a csv file from the folder and parse its content

        :param file_name: the name of the file
        :type file_name: str
        :return: a DataFrame with the file content
        :rtype: pd.DataFrame
        """
        source = self.get_file_contents(file_name)
        output = []
        content = csv.DictReader(io.StringIO(
            source), fieldnames=self._header_csv)
        next(content)
        for row in content:
            line = [x for x in row.values()]
            line[0] = self.process_date(line[0])
            # add line to output
            output.append(line)
        # Change data types and remove null values (come as 255)
        num_type, null_value = ('int32', 255)
        result = pd.DataFrame(
            output, columns=self._header_output, dtype=num_type)
        columns_to_change = self._header_output.copy()
        del columns_to_change[0]  # Remove the Time column
        columns = {x: num_type for x in columns_to_change}
        columns[self._header_output[0]] = 'datetime64[ns]'
        if not self._null_values:
            result = result.replace(f"{null_value}", np.nan).dropna()
        return result.astype(columns)
