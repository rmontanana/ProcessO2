from ProcessO2 import ProcessO2

model = ProcessO2('../MedicionesO2/*.csv')
data = model.load_file('../MedicionesO2/Checkme_20200327022916_OXIRecord.csv')
print(data.head())
print(data.describe())
print(data.dtypes)