myList = ["ece", "zehra", "busra"]
myTuple=("ece", "zehra", "busra")

len(myTuple)

thistuple= ("nazli")
type(thistuple)

thistuple = ("nazli", 32, True)

for x in myTuple:
    print(x)
print("                  ")

for i in range(len(myTuple)):
    print(myTuple[i])
print("                  ")

i=0
while i< len(myTuple):
    print(myTuple[i])
    i=i+1
print(myTuple)

newTuple = myTuple + thistuple
print(newTuple)

tuple1 = (1,2,3,4,5,3,5,3)
z = tuple1.count(3)
print(z)

print(tuple1.index(3))

mySet = {"apple", "banana", "cherry"}
print(type(mySet))

thisset ={"APPLE", 3, False}
print(thisset)

mySet.add("orange")
print(mySet)

mySet.remove("orange")
print(mySet)

print(mySet.pop())

#clear
#union
