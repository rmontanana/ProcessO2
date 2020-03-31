'''
__author__ = "Ricardo Montañana Gómez"
__copyright__ = "Copyright 2020, Ricardo Montañana Gómez"
__license__ = "GPLv3"
__version__ = "1.0"
Procesa los archivos de mediciones de O2
'''
import glob
import csv
import pandas as pd
import numpy as np
from datetime import datetime
import configparser

class ProcessO2:
    folder = ''  # Folder with csv data files
    config_file = 'config.cfg'
    header_csv = []
    header_output = []

    def __init__(self, folder):
        self.folder = folder
        parser = configparser.RawConfigParser()
        parser.read(self.config_file)
        self.header_csv = [x for x in parser._sections['CSV_HEADER'].values()]
        self.header_output = [x for x in parser._sections['OUTPUT_HEADER'].values()]

    def get_headers(self):
        return (self.header_csv, self.header_output)

    def files(self):
        return glob.glob(self.folder)

    def load_file(self, file_name):
        salida = []
        with open(file_name) as source:
            content = csv.DictReader(source, fieldnames=self.header_csv)
            next(content)
            for row in content:
                line = [x for x in row.values()]
                input_date = line[0]
                # Set Date
                real_date = input_date[-11:]
                # Remove special char ', ' in date
                real_date = real_date[0:6] + ' ' + real_date[-4:]
                temp = datetime.strptime(real_date + ' ' + input_date[0:8], '%b %d %Y %H:%M:%S')
                line[0] = temp
                # añade línea a la salida
                salida.append(line)
        # Change data types and remove null values (come as 255 in 16 bits or -1 in 8)
        num_type, null_value = ('int8', -1)
        #num_type, null_value = ('int32', 255)
        result = pd.DataFrame(salida, columns=self.header_output, dtype=num_type)
        columns_to_change = self.header_output.copy()
        del columns_to_change[0]  # Remove the Time column  
        columns = {x: num_type for x in columns_to_change}
        columns[self.header_output[0]] = 'datetime64[ns]'
        result = result.replace(f"{null_value}", np.nan).dropna()
        result = result.astype(columns)
        return result

        

    