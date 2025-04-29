a = 200
b =32
if a>b:
    print("a is greater")
elif a ==b:
    print("a is equal to b")
else:
    print("b is greater than a")


i = 0
while i<6:
    print(i)
    if  i ==3:
        break
    i=i+1
print("                 ")

i = 0
while i<6:
    i=i+1
    if  i ==3:
        continue
    print(i)

print("                 ")
myList = [1,2,3,4,5,6]
for x in myList:
    print(x)

print("                 ")    
for x in "nazli":
    print(x)

print("                 ")    
for x in myList:
    if x==4:
        break
    print(x)

print("                 ")

for i in range(10):
    print(i)

print("                 ")
for i in range(2,6):
    print(i)
print("                 ")

for i in range(2,10,2):
    print(i)
print("                 ")

def myFunction():
    print("hello")

myFunction()
print("                 ")
def function2(fname):
    print("HELLO " + fname)
function2("ece") 

print("                 ")

def my_function(child1,child2,child3):
    print("the youngest one is "+ child3)

my_function(child1 ="emre", child2="nazli", child3 ="zehra")
print("                 ")
def function3(country = "norway"):
    print("i am from "+ country)

function3()
print("                 ")
function3("turkiye")
print("                 ")
def function4(food):
    for x in food:
        print(x)

myfood =["apple", "banana", "cherry"]
function4(myfood)
print("                 ")
def function5(x):
    return 5*x

print(function5(10))

#lambda arguments : expression
x = lambda a,b: a*b

print(x(4,5))
print("                 ")
x = lambda a,b,c : a+b+c
print(x(23,45,3))

def myFunc(n):
    return lambda a:a*n

mydoubler = myFunc(2)
print(mydoubler(5))
mytripler = myFunc(3)
print(mytripler(2))
print("                 ")


import numpy as np

arr = np.array([1,2,3,4,5,6])

print(arr)

print(type(arr))

arr1 = np.array(42)
print(arr1)

arr2 = np.array([1,2,3,4,5,6,7,8])

arr3 = np.array([[2,3,4],[6,8,9]])
print(arr3)
#numpy array çalış



