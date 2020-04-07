from ExtractO2 import ExtractO2
from ProcessO2 import ProcessO2


def header(string):
    num = (80 - len(string)) // 2
    eqs = '=' * num
    print(f"{eqs} {string} {eqs}")


model = ProcessO2('../O2Measures/*.csv', null_data=True)
print(header('Files with duplicated data'))
[print(i) for i in model.get_duplicated_files()]
data = model.get_all_data()
print(header('With Null Data'))
print(data.head())
print(data.describe())
print(data.dtypes)

model = ProcessO2('../O2Measures/*.csv')
data = model.get_all_data()
print(header('Without Null Data'))
print(data.head())
print(data.describe())
print(data.dtypes)

summary = ExtractO2(data)
days, nights = summary.compute_days_nights()
print(header('Nights'))
print(summary.data_info_frame(nights))
print(header('Days'))
print(summary.data_info_frame(days))
