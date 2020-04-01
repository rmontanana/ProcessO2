from ProcessO2 import ProcessO2

model = ProcessO2('../O2Measures/*.csv', null_data=True)
print("========= Files with duplicated data ===========")
[print(i) for i in model.get_duplicated_files()]
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