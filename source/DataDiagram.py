# -*- coding: utf-8 -*-
"""DataDiagram.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1VVNyNd9KfhKgTO2v8opSxmJ4nYYvQiiR
"""

import numpy as np
import math

vector = np.random.rand(1,1024)[0] * (0.5j + 0.5)
vector = vector / np.linalg.norm(vector)

print(vector)

class DataDiagram:
     def __init__(self,data):
          self.data = data
          self.parent = None
          self.left = None
          self.right = None
          self.amplitude = 0
          self.fft = False
     def __repr__(self):
          return repr(self.data)
     def change_fft(self):
        self.fft = not(self.fft)
     def add_left(self,node):
         self.left = node
         if node is not None:
             node.parent = self
     def add_right(self,node):
         self.right = node
         if node is not None:
             node.parent = self
     def get_left(self):
        return self.left
     def get_right(self):
        return self.right
     def get_parent(self):
        return self.parent
     def get_data(self):
        return self.data
     def set_data(self, data):
        self.data = data
     def get_amplitude(self):
       return self.amplitude
     def set_amplitude(self, amp):
       self.amplitude = amp

def getProbability(value):
  return np.conjugate(value)*value
def printTree(root, level=0):
    print("  " * (2*level), root, "| Amplitude: ", root.get_amplitude())
    if(root.get_left() != None):
        printTree(root.get_left(), level + 1)
    if(root.get_right() != None):
        printTree(root.get_right(), level + 1)

def findLevels(root, currentLevel):
    if(root == None):
      return currentLevel
    return max(findLevels(root.get_left(), currentLevel + 1), findLevels(root.get_right(), currentLevel + 1))
def correctNonterminalAmplitudesLevelN(root, currentLevel, endLevel, approximation):
    if(root == None or currentLevel > endLevel):
      return
    if(currentLevel == endLevel):
      left = 0
      if(root.get_left() != None):
        left = getProbability(root.get_left().get_amplitude())
      right = 0
      if(root.get_right() != None):
        right = getProbability(root.get_right().get_amplitude())
      root.set_amplitude(left + right)
      return False
    else:
      if(root.get_left() != None):
          return correctNonterminalAmplitudesLevelN(root.get_left(), currentLevel + 1, endLevel, approximation)
      if(root.get_right() != None):
          return correctNonterminalAmplitudesLevelN(root.get_right(), currentLevel + 1, endLevel, approximation)
      return False
def correctNonterminalAmpltiudes(root, approximation):
    levels = findLevels(root, 0)
    while(levels != 0):
      correctNonterminalAmplitudesLevelN(root, levels, 0, approximation)
      levels = levels - 1


def correctEntries(root, level, unitCorrection):
    if(root == None):
      return
    if(root.get_data() != None and len(root.get_data()) < int(math.log2(len(vector))) and root.get_data() != "DD"):
      root.set_data(root.get_data() + ("0" * (int(math.log2(len(vector))) - len(root.get_data()))))
    if(root.get_left() == None and root.get_right() == None):
      root.set_amplitude(root.get_amplitude() * unitCorrection)
    if(root.get_left() != None):
        correctEntries(root.get_left(), level + 1, unitCorrection)
    if(root.get_right() != None):
        correctEntries(root.get_right(), level + 1, unitCorrection)
def countEntries(root, level=0):
    if(root == None):
      return 1
    return countEntries(root.get_left(), level + 1) + countEntries(root.get_right(), level + 1)
def getSummation(root, level=0):
    if(root == None):
      return 0
    if(root.get_data() != None and root.get_left() == None and root.get_right() == None):
      return getProbability(root.get_amplitude())
    return getSummation(root.get_left(), level + 1) + getSummation(root.get_right(), level + 1)

def constructData(root, vector, history, approximation, qubits):
  partialNorm = np.dot(np.transpose(vector.conjugate()), vector)
  if(root.get_data() != "DD"):
    root.set_data(history)
  if(len(vector) == 1):
    root.set_data(history)
    root.set_amplitude(vector[0])
    return (getProbability(vector[0]) > approximation/qubits)
  leftNode = DataDiagram(history)
  rightNode = DataDiagram(history)
  middle_index = len(vector)//2
  if(constructData(leftNode, vector[:middle_index], history + str(0), approximation, qubits)):
    root.add_left(leftNode)
  if(constructData(rightNode, vector[middle_index:], history + str(1), approximation, qubits)):
     root.add_right(rightNode)
  if(root.get_right() != None and (root.get_left() == None or getProbability(root.get_left().get_amplitude()) < approximation/qubits)
      and root.get_data() != "DD"):
    root.set_amplitude(rightNode.get_amplitude())
    root.set_data(str(rightNode.get_data()))
    root.add_right(None)
  else:
    if(root.get_left() != None and (root.get_right() == None or getProbability(root.get_right().get_amplitude()) < approximation/qubits)
        and root.get_data() != "DD"):
        root.set_amplitude(leftNode.get_amplitude())
        root.set_data(str(leftNode.get_data()))
        root.add_left(None)
    else:
        if((root.get_right() == None and root.get_left() == None) or (getProbability(root.get_right().get_amplitude()) < approximation/qubits) and 
           getProbability(root.get_left().get_amplitude()) <= approximation/qubits):
          root.set_data(None)
          return False
        else:
           root.set_amplitude(partialNorm)
  return (partialNorm*partialNorm > 0)

def correctTree(root):
  correction = getSummation(root, 0)
  unitCorrection = 1/(np.sqrt(correction))
  correctEntries(root, 0, unitCorrection)
def makeDataDiagram(vector, approximation, fftAllowed):
  root = DataDiagram("DD")
  qubits = math.ceil(math.log2(len(vector))) + 0.01
  constructData(root, vector, "", approximation, qubits)
  correctTree(root)
  correctNonterminalAmpltiudes(root, approximation)
  vector = np.fft.fft(vector)
  vector = vector/np.linalg.norm(vector)
  if(fftAllowed):
    rootFFT = DataDiagram("DD")
    constructData(rootFFT, vector, "", approximation, qubits)
    correctTree(rootFFT)
    correctNonterminalAmpltiudes(rootFFT, approximation)
    rootFFT.change_fft()
    prior = countEntries(root, 0)
    now = countEntries(rootFFT, 0)
    return rootFFT
  return root

root = makeDataDiagram(vector, 0.005/100, True)
countEntries(root)

print(root)
vector = np.random.rand(1,1024)[0] * np.exp(1.j * np.random.uniform(0, 2 * np.pi, 1024))
vector = vector / np.linalg.norm(vector)
print(vector)

exactStatevector = []
exactDD = []
approximateDDNoFFT = []
approximateDDFFT = []
exactDDFFT = []
values = []
for i in range(2, 22):
  vector = np.random.rand(1,2**i)[0] * np.exp(1.j * np.random.uniform(0, 2 * np.pi, 2**i))
  vector = vector / np.linalg.norm(vector)
  values.append(i)
  print("Run: ", i)
  print("Exact...")
  exactStatevector.append(2**i)
  print("Exact Data Diagram...")
  root = makeDataDiagram(vector, 0, False)
  exactDD.append(countEntries(root))
  print("Exact Data Diagram FFT...")
  root = makeDataDiagram(vector, 0, True)
  exactDDFFT.append(countEntries(root))
  print("Approximate Data Diagram No FFT...")
  root = makeDataDiagram(vector, 1/(2**i), False)
  approximateDDNoFFT.append(countEntries(root))
  print("Approximate Data Diagram FFT...")
  root = makeDataDiagram(vector, 1/(2**i), True)
  approximateDDFFT.append(countEntries(root))





import matplotlib.pyplot as plt
fig = plt.figure(1)	#identifies the figure 
plt.plot(values, [exactStatevector[i]**3/5500000000 for i in range(len(exactDD))], label="Statevector")	#plot the points
plt.plot(values, [exactDD[i]**3/5500000000 for i in range(len(exactDD))], label="Data Diagram")	#plot the points
plt.plot(values, [exactDDFFT[i]**3/5500000000 for i in range(len(exactDD))], label="Data Diagram (FFT)")	#plot the points
plt.plot(values, [approximateDDNoFFT[i]**3/5500000000 for i in range(len(exactDD))], label="Data Diagram (Approx.)")	#plot the points
plt.plot(values, [approximateDDFFT[i]**3/5500000000 for i in range(len(exactDD))], label="Data Diagram (Approx., FFT)")	#plot the points
plt.xlabel("Qubits",fontsize='13')	#adds a label in the x axis
plt.ylabel("Estimated Runtime (s)",fontsize='13')	#adds a label in the y axis
plt.yscale("log")
plt.legend()
plt.show()

print(exactStatevector)

print(exactDD)

