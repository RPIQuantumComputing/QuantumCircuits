# QUBO String Parsing
objectiveFunction = input("Enter objective: ")
variableList = []
typeList = []
stop = False
while(not stop):
    user = input("Enter Variable (n/a to exit): ")
    if(user == "n/a"):
        stop = True
    else:
        index = 0
        if("arr" in user):
            name = user[:user.find(" ")]
            typeVal = user[user.find("arr["):user.find(",")][4:]
            num = int(user[user.find(",")+2:user.find("]")])
            for i in range(num):
                variableList.append(name + str(i))
                typeList.append(typeVal)
        else:
            name = user[:user.find(":")-1]
            typeVal = user[user.find(":")+2:]
            variableList.append(name)
            typeList.append(typeVal)


maximize = True
if("min" in objectiveFunction):
    maximize = False

objectiveFunction = objectiveFunction[4:]
if(maximize == True):
    print("Maximizing: ", objectiveFunction)
    for idx in range(len(typeList)):
        print("Variable: ", variableList[idx], " Type: ", typeList[idx])
else:
    print("Minimizing: ", objectiveFunction)
    for idx in range(len(typeList)):
        print("Variable: ", variableList[idx], " Type: ", typeList[idx])
