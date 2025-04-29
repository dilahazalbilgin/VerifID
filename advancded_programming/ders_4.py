import pandas as pd

mydataset ={
    'cars':["bmw", "volvo", "ford"],
    'color':["red","white","black"]
}
print(type(mydataset))

myvar= pd.DataFrame(mydataset)
print(myvar)

a =[1,2,3]
myvar2 = pd.Series(a)
print(myvar2)

print(myvar2[0])

myvar3 = pd.Series(a,index=["x", "y", "z"] )
print(myvar3)

print(myvar3["y"])

calories = {"day1":400,"day2":350,"day3":330}
myvar4= pd.Series(calories)

print(myvar4)
#print(myvar["day2"])

data = {
    "calories":[450,300,320],
    "duration":[50,30,40]
    }

df=pd.DataFrame(data)
print(df)


df.loc[2]

print(df.loc[[0,1]])

df1 =pd.DataFrame(data,index=["day1", "day2","day3"])
print(df1)

print(df1.loc["day2"])

df3 =pd.read_csv('exercise_data.csv')
print(df3)

print(df3.to_string())

df4 =pd.read_json('exercise_data.json')
print(df4)

print(df3.head(6))#argüman vermezsen ilk 5
print(df3.tail())#argüman vermezsen son 5 

print(df3.info())

new_df = df3.dropna()
print(new_df)

df3.dropna(inplace=True)
print(df3)

df3.fillna(130,inplace=True)
df3.info()

df3["Calories"].fillna(130,inplace=True)

x =df3["Calories"].mean()#median dersek ortadaki değeri alır, mode dersek en çok gösterilen değerleri gösterir

df3["Calories"].fillna(x,inplace=True)
df3.info()

df5 = pd.read_csv('clean_data.csv')

print(df5)

df5.info()
df5.dropna(subet =["Date"],inplace=True)
df5.info()

df5.loc[7,"Duration"] =45

for x in df5.index:
    if df5.loc[x, "Duuration"]>60:
        df5.loc[x,"duration"]=45


for x in df5.index:
    if df5.loc[x, "Duuration"]>60:
        df5.drop(x,inplace=True)

df5.duplicated()

df5.drop_duplicates(inplace=True)
df5.duplicated()

df5.corr()


