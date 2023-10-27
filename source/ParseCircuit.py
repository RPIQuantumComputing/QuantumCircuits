# grid[col][row]

# LL(1) Grammar to parse grid implemented using recursive descent
# S(n, m) := B(n, m)
# B(n, m) := idS B(n, m-1) | idC B(n, m - 1) | * B(n, m-1)
    #        W(n-1, m, 0)  | W(n-1, m, k)    | W(n-1, m, -1)
# W(n, m, k) := idS          | *              | idC(k1)
#               W(n, m-1, k) | W(n, m-1, k-1) | W(n, m-1, k1)

idS = {"H", "S", "T", "X(1/2)", "Y(1/2)", "-", "M"}
idC = {"CNOT": 1, "CCX": 2, "CX": 1}
idI = {"CX": 1}
parsingFlag = False

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
     def add_left(self,node):
         self.left = node
         if node is not None:
             node.parent = self
     def add_middle(self,node):
         self.middle = node
         if node is not None:
             node.parent = self
     def add_right(self,node):
         self.right = node
         if node is not None:
             node.parent = self
     def add_associations(self,associations):
         self.associations = associations
     def get_associations(self):
         return self.associations
     def get_left(self):
        return self.left
     def get_middle(self):
        return self.middle
     def get_right(self):
        return self.right
     def get_parent(self):
        return self.parent
     def get_data(self):
        return self.data
        
def W(grid, n, m, k, associations):
  rootNode = Node("W("+str(n)+","+str(m)+","+str(k)+")")
  global idS, idC, parsingFlag
  if(n == len(grid) or m == len(grid[0])):
    if(k < 0 or k > 0):
      print("Parse Error...")
      parsingFlag = True
    return rootNode, associations
    
  leftNode = Node((grid[n][m], m))
  middleNode = Node(("NotReal", -1))
  if(grid[n][m] == "-"):
    middleNode, associationsNew = W(grid, n, m+1, k, associations)
    leftNode.add_associations(associationsNew)
    rootNode.add_left(leftNode)
    rootNode.add_middle(middleNode)
    return rootNode, associations
  if(grid[n][m] in idS):
    leftNode.add_associations({m: "Actor"})
    middleNode, _ = W(grid, n, m+1, k, {m: "Actor"})
  else:
    if(grid[n][m] in idC):
      if(k == 0):
        middleNode, futureAssociations = W(grid, n, m+1, k+idC[grid[n][m]], dict({}))
        totalAssociations = {m: "Actor"}
        if(futureAssociations != None):
            totalAssociations.update(futureAssociations)
        leftNode.add_associations(totalAssociations)
      else:
        middleNode, futureAssociations = W(grid, n, m+1, k+idC[grid[n][m]], associations)
        totalAssociations = {m: "Actor"}
        if(futureAssociations != None):
            totalAssociations.update(futureAssociations)
        leftNode.add_associations(totalAssociations)
    else:
      if(grid[n][m] == "*"):
        if(k != 0):
            totalAssociations = associations
            totalAssociations[m] = "Control"
        else:
            totalAssociations = {m: "Control"}
        middleNode, futureAssociations = W(grid, n, m+1, k + -1, totalAssociations)
        if(futureAssociations != None):
            totalAssociations.update(futureAssociations)
        leftNode.add_associations(totalAssociations)
      else:
        print("Parse Error...")
        parsingFlag = True
        return rootNode, associations
  rootNode.add_left(leftNode)
  rootNode.add_middle(middleNode)
  return rootNode, associations
  
def B(grid, n, m):
  global idS, idC, parsingFlag
  rootNode = Node("B("+str(n)+","+str(m)+")")
  if(n == len(grid) or m == len(grid[0])):
    return rootNode
  leftNode = Node((grid[n][m], m))
  if(grid[n][m] in idS):
    middleNode, _ = W(grid, n, m+1, 0, dict({}))
    leftNode.add_associations({m: "Actor"})
    rightNode = B(grid, n+1, m)
  else:
    if(grid[n][m] in idC):
      middleNode, associations = W(grid, n, m+1, idC[grid[n][m]], {m: "Actor"})
      leftNode.add_associations(associations)
      rightNode = B(grid, n+1, m)
    else:
      if(grid[n][m] == "*"):
        middleNode, associations = W(grid, n, m+1, -1, {m: "Control"})
        leftNode.add_associations(associations)
        rightNode = B(grid, n+1, m)
      else:
        print("Parse Error...")
        parsingFlag = True
        return rootNode
  rootNode.add_left(leftNode)
  rootNode.add_middle(middleNode)
  rootNode.add_right(rightNode)
  return rootNode 
  
def generateParseTree(grid, n, m):
  rootMain = Node("S("+str(n)+","+str(m)+")")
  rootParse = B(grid, n, m)
  rootMain.add_middle(rootParse)
  if(not parsingFlag):
    print("Valid quantum circuit...")
    return rootMain
  return None

def printTree(root, level=0):
    if(root == None):
        return
    print("  " * (2*level), root, "Associations: ", root.get_associations(), type(root.get_data()))
    if(root.get_left() != None):
        printTree(root.get_left(), level + 1)
    if(root.get_middle() != None):
        printTree(root.get_middle(), level + 1)
    if(root.get_right() != None):
        printTree(root.get_right(), level + 1)
    
def parse(grid):
    print("----------------GENERATING PARSE TREE---------------------------")
    parseTree = generateParseTree(grid, 0, 0)
    return parseTree

def get_instructions(root, level=0, instructions=None):
    # Initialize instructions as an empty list if it's None
    if instructions is None:
        instructions = []

    if root is None:
        return instructions

    # Gather instruction if the node data meets certain conditions
    if isinstance(root.data, tuple) and root.data[0] != "-" and root.data[0] != "*":
        instructions.append((root.data[0], root.get_associations()))

    # Recurse on the left, middle, and right children, if they exist
    if root.get_left() is not None:
        get_instructions(root.get_left(), level + 1, instructions)
    if root.get_middle() is not None:
        get_instructions(root.get_middle(), level + 1, instructions)
    if root.get_right() is not None:
        get_instructions(root.get_right(), level + 1, instructions)

    return instructions  # Return the instructions list
