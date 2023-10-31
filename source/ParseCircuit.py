
class Node:
    def __init__(self,data):
        self.data = data
        self.parent = None
        self.left = None
        self.middle = None
        self.right = None
        self.associations = None

    def __repr__(self):
        return repr(self.data)

class ParseCircuit:
    idS = {"H", "S", "T", "X(1/2)", "Y(1/2)", "-", "M"}
    idC = {"CNOT": 1, "CCX": 2, "CX": 1}
    idI = {"CX": 1}

    def __init__(self):
        self.parsingFlag = False

    def W(self, grid, n, m, k, associations):
        rootNode = Node("W(" + str(n) + "," + str(m) + "," + str(k) + ")")
        if n == len(grid) or m == len(grid[0]):
            if k < 0 or k > 0:
                print("Parse Error...")
                self.parsingFlag = True
                return rootNode, associations

        leftNode = Node((grid[n][m], m))
        middleNode = Node(("NotReal", -1))
        if grid[n][m] == "-":
            middleNode, associationsNew = self.W(grid, n, m + 1, k, associations)
            leftNode.associations = associationsNew
            rootNode.left = leftNode
            rootNode.middle = middleNode
            return rootNode, associations
        if grid[n][m] in ParseCircuit.idS:
            leftNode.associations = {m: "Actor"}
            middleNode = self.W(grid, n, m + 1, k, {m: "Actor"})[0]
        else:
            if grid[n][m] in ParseCircuit.idC:
                if k == 0:
                    middleNode, futureAssociations = self.W(grid, n, m + 1, k + ParseCircuit.idC[grid[n][m]], dict({}))
                    totalAssociations = {m: "Actor"}
                    if futureAssociations is not None:
                        totalAssociations.update(futureAssociations)
                    leftNode.associations = totalAssociations
                else:
                    middleNode, futureAssociations = self.W(grid, n, m + 1, k + ParseCircuit.idC[grid[n][m]], associations)
                    totalAssociations = {m: "Actor"}
                    if futureAssociations is not None:
                        totalAssociations.update(futureAssociations)
                    leftNode.associations = totalAssociations
            else:
                if grid[n][m] == "*":
                    if k != 0:
                        totalAssociations = associations
                        totalAssociations[m] = "Control"
                    else:
                        totalAssociations = {m: "Control"}
                    middleNode, futureAssociations = self.W(grid, n, m + 1, k - 1, totalAssociations)
                    if futureAssociations is not None:
                        totalAssociations.update(futureAssociations)
                    leftNode.associations = totalAssociations
                else:
                    print("Parse Error...")
                    self.parsingFlag = True
                    return rootNode, associations
        rootNode.left = leftNode
        rootNode.middle = middleNode
        return rootNode, associations

    def B(self, grid, n, m):
        rootNode = Node("B("+str(n)+","+str(m)+")")
        if(n == len(grid) or m == len(grid[0])):
            return rootNode
        leftNode = Node((grid[n][m], m))
        if(grid[n][m] in self.idS):
            middleNode, _ = self.W(grid, n, m+1, 0, dict({}))
            leftNode = {m: "Actor"}
            rightNode = self.B(grid, n+1, m)
        else:
            if(grid[n][m] in self.idC):
                middleNode, associations = self.W(grid, n, m+1, self.idC[grid[n][m]], {m: "Actor"})
                leftNode = associations
                rightNode = self.B(grid, n+1, m)
            else:
                if(grid[n][m] == "*"):
                    middleNode, associations = self.W(grid, n, m+1, -1, {m: "Control"})
                    leftNode = associations
                    rightNode = self.B(grid, n+1, m)
                else:
                    print("Parse Error...")
                    self.parsingFlag = True
                    return rootNode
        rootNode.left = leftNode
        rootNode.middle = middleNode
        rootNode.right = rightNode
        return rootNode 

    def generateParseTree(self, grid, n, m):
        rootMain = Node("S(" + str(n) + "," + str(m) + ")")
        rootParse = self.B(grid, n, m)
        rootMain.middle = rootParse  # changed from add_middle to direct attribute assignment
        if not self.parsingFlag:
            print("Valid quantum circuit...")
            return rootMain
        return None

    def printTree(self, root, level=0):
        if root is None:
            return
        print("  " * (2 * level), root, "Associations: ", root.get_associations(), type(root.get_data()))
        self.printTree(root.get_left(), level + 1)
        self.printTree(root.get_middle(), level + 1)
        self.printTree(root.get_right(), level + 1)

    def parse(self, grid):
        print("----------------GENERATING PARSE TREE---------------------------")
        parseTree = self.generateParseTree(grid, 0, 0)
        return parseTree

    def get_instructions(self, root, level=0, instructions=None):
        if instructions is None:
            instructions = []
        if root is None:
            return instructions
        if isinstance(root.data, tuple) and root.data[0] != "-" and root.data[0] != "*":
            instructions.append((root.data[0], root.get_associations()))
        self.get_instructions(root.get_left(), level + 1, instructions)
        self.get_instructions(root.get_middle(), level + 1, instructions)
        self.get_instructions(root.get_right(), level + 1, instructions)
        return instructions