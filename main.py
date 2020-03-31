from ProcessO2 import ProcessO2

print("========= Files with duplicated data ===========")
[print(i) for i in model.get_duplicated_files()]

model = ProcessO2('../MedicionesO2/*.csv', null_data=True)
data = model.get_all_data()
print("================= With Null Data ===============")
print(data.head())
print(data.describe())
print(data.dtypes)

model = ProcessO2('../O2Measures/*.csv')
data = model.get_all_data()
print("================ Without Null Data =============")
print(data.head())
print(data.describe())
print(data.dtypes)