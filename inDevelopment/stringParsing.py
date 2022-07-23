# QUBO String Parsing
objectiveFunction = input("Enter objective: ")
variableList = []
typeList = []
boundMap = {"n/a": [None, None]}
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
stop = False
while not stop:
    bounds = [None, None]
    bounding = input("Enter Bounds (_ for n/a and ! for exit)")
    if("!" in bounding):
        stop = True
    else:
        variable = bounding[:bounding.find("|")-1]
        lower = bounding[bounding.find("|")+2:bounding.find(",")]
        if("_" not in lower):
            bounds[1] = float(lower)
        upper = bounding[bounding.find(",")+2:]
        if("_" not in upper):
            bounds[0] = float(upper)
        boundMap[variable] = bounds

maximize = True
if("min" in objectiveFunction):
    maximize = False

objectiveFunction = objectiveFunction[4:]
if(maximize == True):
    print("Maximizing: ", objectiveFunction)
else:
    print("Minimizing: ", objectiveFunction)

for idx in range(len(typeList)):
    print("Variable: ", variableList[idx], " Type: ", typeList[idx])
for variable in variableList:
    if(variable in boundMap):
        print("Variable: ", variable, " has lower bound: ", boundMap[variable][0], " and upper bound: ", boundMap[variable][1])
        
#sum(x[(i * 2)], _, _) <= 10
#sum(x[(i * 2)], _, _) <= sum(y[(j * 2)], _, _)
