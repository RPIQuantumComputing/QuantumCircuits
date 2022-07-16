from unittest import result
import SettingsFile
import math
import matplotlib.pyplot as plt
import cupy as np
import numpy as tnp
import random
import matplotlib.cm as cm
import matplotlib as mpl
import itertools
import functools
from numpy.random import choice, rand
from numpy import linalg as LA
import scipy
import pandas as pd
from scipy.optimize import minimize

class HamiltonionBackend:
    provider = "Local"
    settings = None
    histogramResult = None
    results = None

    def __init__(self, newSettings):
        self.settings = newSettings
    
    def sendAPIToken():
        pass
    
    def sendRequest(self, gridWidth, gridHeight, grid):
        circuitOperators = [[['-', [j]] for j in range(gridHeight)] for i in range(gridWidth)]
        for widthIdx in range(gridWidth):
            for heightIdx in range(gridHeight):
                if(grid[widthIdx][heightIdx].getName() != '-'):
                    if(grid[widthIdx][heightIdx].getName() == 'CNOT'):
                        circuitOperators[widthIdx][heightIdx] = [grid[widthIdx][heightIdx].getName(), grid[widthIdx][heightIdx].gate_qubitsInvolved]
                        circuitOperators[widthIdx][heightIdx+1] = [grid[widthIdx][heightIdx].getName(), grid[widthIdx][heightIdx].gate_qubitsInvolved]
                    else:
                        circuitOperators[widthIdx][heightIdx] = [grid[widthIdx][heightIdx].getName(), grid[widthIdx][heightIdx].gate_qubitsInvolved]
        numQubits = gridHeight
        numDepth = gridWidth
        operations = {'H': [np.array([[1/np.sqrt(2) + 0.0j, 1/np.sqrt(2) + 0.0j], [1/np.sqrt(2) + 0.0j, -1/np.sqrt(2) + 0.0j]]),1], '-': [np.array([[1, 0], [0,1]]),1],
             'CNOT': [np.array([[1+ 0.0j,0+ 0.0j,0+ 0.0j,0+ 0.0j],[0+ 0.0j,1+ 0.0j,0+ 0.0j,0+ 0.0j],[0+ 0.0j,0+ 0.0j,0+ 0.0j,1+ 0.0j],[0+ 0.0j,0+ 0.0j,1+ 0.0j,0+ 0.0j]]), 2], 'X': [np.array([[0 + 0.0j, 1+ 0.0j],[1+ 0.0j,0+ 0.0j]]),1], 'Y': [np.array([[0+ 0.0j, 0-1j],[0+1j, 0+ 0.0j]]), 1],
             'Z': [np.array([[1+ 0.0j, 0+ 0.0j],[0+ 0.0j,-1+ 0.0j]]), 1], 'S': [np.array([[1+ 0.0j,0+ 0.0j],[0+ 0.0j,0+1j]]), 1], 'T': [np.array([[1+ 0.0j,0+ 0.0j],[0+ 0.0j,0+tnp.exp(1j*np.pi/4)]]),1]}
        
        qubitToIndex = [j for j in range(numQubits)]
        qubitsInvolvedInIndex = [[j] for j in range(numQubits)]
        decomposedState = [np.transpose(np.array([1+ 0.0j,0 + 0.0j])) for i in range(numQubits)]

        def gram_matrix(Xs):
            temp = tnp.vstack([tnp.ravel(X) for X in Xs],dtype=complex)
            return tnp.dot(temp, temp.T)

        def eig(X):
            vals, vecs = np.linalg.eig(X)
            idx = tnp.argsort(tnp.abs(vals))
            return vals[idx], vecs[...,idx]

        def eig_both(X):
            return eig(X.T)[1], eig(X)[1]

        def nkp_sum(As, Bs):
            GK = tnp.dot(gram_matrix(As), gram_matrix(Bs))
            lvecs, rvecs = eig_both(GK)
            Ahat = tnp.einsum('i,ijk->jk', lvecs[-1], As)
            Bhat = tnp.einsum('i,ijk->jk', rvecs[-1], Bs)
            return Ahat.reshape(As[0].shape), Bhat.reshape(Bs[0].shape)

        def nkp(A, Bshape):
            blocks = map(lambda blockcol: tnp.split(blockcol*(1.0 + 0.0j), Bshape[0], 0),
                                tnp.split(A.get()*(1.0 + 0.0j),        Bshape[1], 1))
            Atilde = tnp.vstack([block.ravel()*(1.0 + 0.0j) for blockcol in blocks
                                    for block in blockcol])
            U, s, V = tnp.linalg.svd(Atilde)
            Cshape = A.shape[0] // Bshape[0], A.shape[1] // Bshape[1]
            idx = tnp.argmax(s)
            B = tnp.sqrt(s[idx]) * U[:,idx].reshape(Bshape).T
            C = tnp.sqrt(s[idx]) * V[idx,:].reshape(Cshape)
            return B, C

        def performDecomp(matrixInput, matricies):
            if(np.shape(matrixInput)[0] < 4):
                matricies.append(matrixInput)
                return
            matrix = np.column_stack((matrixInput.real,matrixInput.imag,np.zeros(np.shape(matrixInput)[0]),np.zeros(np.shape(matrixInput)[0])))
            a, b = nkp(matrix, (2**math.floor(math.log2(np.shape(matrix)[1])/2), 2))
            a = a[:,0] + a[:,1]*(1.0j)
            b = b[:,0] + b[:,1]*(1.0j)
            matricies.append(a)
            performDecomp(b, matricies)
            return
        
        def findDecomposition(matrix):
            matricies = []
            performDecomp(matrix, matricies)
            matricies = np.array(matricies)
            return matricies

        def findNumQubits(matrix):
            return matrix.shape()

        def getTensor(depth):
            initalTensor = np.array([1])
            index = 0
            for entry in circuitOperators[depth]:
                if(min(entry[1]) == index):
                    initalTensor = np.kron(initalTensor, operations[entry[0]][0])
                index += 1
            return initalTensor

        stateProbabilities = []
        initalState = np.zeros(numQubits)
        initalState[0] = 1
        history = ["".join(seq) for seq in itertools.product("01", repeat=numQubits)]
        arrayHistory = [(np.fromstring(entry,'u1') - ord('0'))*(1.0+0.0j) for entry in history]
        for qubit in range(numQubits):
            probabilityTotal = 0.0
        for possiblePrior in arrayHistory:
            pass

        for depthCurrent in range(numDepth):
            for qubit in range(numQubits):
                numActors = operations[circuitOperators[depthCurrent][qubit][0]][1]
                matrix = operations[circuitOperators[depthCurrent][qubit][0]][0]
                if(circuitOperators[depthCurrent][qubit][0] != '-'):
                    indexToCombined = min(circuitOperators[depthCurrent][qubit][1])
                    if(2**numActors == np.shape(decomposedState[qubitToIndex[qubit]])[0]):
                        matrix = operations[circuitOperators[depthCurrent][qubit][0]][0]
                        #print("-----------------------1st-----------------------------------")
                        #print("Operation: ", circuitOperators[depthCurrent][qubit][0])
                        #print("Matrix: ", matrix)
                        #print("State: ", decomposedState[qubitToIndex[indexToCombined]], " of qubit: ", qubit)
                        decomposedState[qubitToIndex[qubit]] = matrix.dot(decomposedState[qubitToIndex[qubit]])
                        #print("Result: ", decomposedState[qubitToIndex[qubit]])
                    else:
                        #print("-----------------------2nd-----------------------------------")
                        #print("Depth: ", depthCurrent, " Qubit: ", qubit)
                        #print("Operation: ", circuitOperators[depthCurrent][qubit][0])
                        #print("Matrix To Apply: ", matrix)
                        #print("Involved Actors: ", circuitOperators[depthCurrent][qubit][1])
                    #for actor in circuitOperators[depthCurrent][qubit][1]:
                        #print("Actor ", actor, ": ", decomposedState[qubitToIndex[actor]])
                        tempStateVec = np.array([1])
                        applyMatrix = np.array([1])
                        tempAppliedMembers = 0
                        newQubitsInvolved = []
                        for actorQubit in circuitOperators[depthCurrent][qubit][1]:
                            tempStateVec = np.kron(tempStateVec, decomposedState[qubitToIndex[actorQubit]])
                            for entry in qubitsInvolvedInIndex[qubitToIndex[actorQubit]]:
                                newQubitsInvolved.append(entry)
                                qubitToIndex[entry] = qubitToIndex[qubit]
                                qubitsInvolvedInIndex[entry] = [-1]
                                decomposedState[entry] = np.array([])
                                if(entry not in circuitOperators[depthCurrent][qubit][1]):
                                    applyMatrix = np.kron(applyMatrix, np.array([[1,0],[0,1]]))
                                else:
                                    if(tempAppliedMembers != numActors):
                                        applyMatrix = np.kron(applyMatrix, matrix)
                                        tempAppliedMembers += numActors
                        qubitsInvolvedInIndex[qubitToIndex[qubit]] = newQubitsInvolved
                        #print("Formed State Vector: ", tempStateVec)
                        #print("Formed Matrix", applyMatrix)
                        decomposedState[qubitToIndex[qubit]] = applyMatrix.dot(tempStateVec)
                        #print("Result: ", decomposedState[qubitToIndex[qubit]])

        temp = []
        for entry in decomposedState:
            if(np.shape(entry)[0] > 0):
                temp.append(entry)
        decomposedState = temp
        temp = []
        tempIndex = 0
        for entry in qubitsInvolvedInIndex:
            if(np.shape(entry)[0] > 0 and entry[0] != -1):
                temp.append(entry)
        else:
            if(np.shape(entry)[0] > 0):
                for idx in range(tempIndex, len(qubitToIndex)):
                    qubitToIndex[idx] -= 1
        tempIndex += 1
        qubitsInvolvedInIndex = temp
        temp = []

        def replace(string, index, newString):
            s = string[:index] + newString + string[index + 1:]
            return s


        def getWeightedProbabilities(saveResults):
            initalString = "0"*numQubits
            shotNum = 2**10
            phase = 0
            results = {}
            resultsPhases = {}
            currentShot = 0
            while(currentShot < shotNum):
                for decision in range(len(decomposedState)):
                    numVal = len(decomposedState[decision])
                currentArray = decomposedState[decision].get()
                probabilities = tnp.zeros((numVal,))
                for index in range(numVal):
                    dotWith = tnp.zeros((numVal,))
                    dotWith[index] = 1.0
                    dotWith = tnp.dot(dotWith, currentArray[index])
                    probabilities[index] = tnp.real(tnp.conj(dotWith).dot(dotWith))
                probabilities = [element/tnp.sum(probabilities) for element in probabilities]
                pickedPossibility = tnp.random.choice(len(currentArray), p=probabilities)
                s = bin(pickedPossibility)
                stringToParse = "0"*(len(qubitsInvolvedInIndex[decision]) - len(s[2:])) + s[2:]
                phase += decomposedState[decision][pickedPossibility]
                index = 0
                for char in stringToParse:
                    if(index < len(qubitsInvolvedInIndex[decision])):
                        truePosition = qubitsInvolvedInIndex[decision][index]
                        initalString = initalString[:truePosition] + char + initalString[truePosition + 1:]
                        index += 1
                    else:
                        break
                if(initalString not in results):
                    results[initalString] = 1
                else:
                    results[initalString] += 1
                resultsPhases[initalString] = phase
                initalString = "0"*numQubits
                phase = 0
                currentShot += 1
                for element in results.keys():
                    saveResults.append([element, results[element]/shotNum, resultsPhases[element]])

        def getAllPossibilities(result):
            a = []
            probabilitiesList = []
            for idx in range(len(decomposedState)):
                temp = []
                currentArray = decomposedState[idx]
                probabilities = np.zeros((len(currentArray),))
                for index in range(len(currentArray)):
                    dotWith = np.zeros((len(currentArray),))
                    dotWith[index] = 1.0
                    dotWith = np.dot(dotWith, currentArray[index])
                    probabilities[index] = np.real(np.conj(dotWith).dot(dotWith))
                probabilities = [element/np.sum(probabilities) for element in probabilities]
                probabilitiesList.append(probabilities)
                for j in range(len(decomposedState[idx])):
                    if(probabilities[j] > 0):
                        temp.append(j)
                a.append(temp)
            combinations = list(itertools.product(*a))
            for decisionSet in combinations:
                decisionNum = 0
                phase = 0
                probability = 1
                initalString = "0"*numQubits
                for collectedState in decisionSet:
                    s = bin(collectedState)
                    stringToParse = "0"*(len(qubitsInvolvedInIndex[decisionNum]) - len(s[2:])) + s[2:]
                    phase += decomposedState[decisionNum][collectedState]
                    probability *= probabilitiesList[decisionNum][collectedState]
                    index = 0
                    for char in stringToParse:
                        if(index < len(qubitsInvolvedInIndex[decisionNum])):
                            truePosition = qubitsInvolvedInIndex[decisionNum][index]
                            initalString = initalString[:truePosition] + char + initalString[truePosition + 1:]
                            index += 1
                        else:
                            break
                    decisionNum += 1
                results.append([initalString, probability, phase])
            
        results = []
        if(self.settings.shots != -1):
            getWeightedProbabilities(results)
        else:
            start = "0"*numQubits
            getAllPossibilities(results)

        fig = plt.figure(figsize = (20, 5))
        xVal = []
        yVal = []
        norm = mpl.colors.Normalize(vmin=0, vmax=np.pi)
        cmap = cm.hsv
        m = cm.ScalarMappable(norm=norm, cmap=cmap)
        for entry in results:
            xVal.append(entry[0][::-1])
            yVal.append(np.asnumpy(entry[1])*100)
        phases = [m.to_rgba(tnp.angle(np.asnumpy(results[j][2]) * 1j)) for j in range(len(results))]

        df = pd.DataFrame(
            dict(
                x=xVal,
                y=yVal,
                phase=phases
            )
        )

        df_sorted = df.sort_values('x')
        plt.bar(df_sorted['x'], df_sorted['y'], width = 0.4, color = df_sorted['phase'])
        plt.xlabel("Computational Result")
        plt.ylabel("Probability")
        rotationAmount = math.floor(90/(1 + np.exp(-(((len(xVal))/3)-5))))
        plt.xticks(rotation = rotationAmount)
        cbar = plt.colorbar(m)
        cbar.set_label('Relative Phase of State (Radians)', rotation=-90, labelpad=20)
        plt.title("Probability Distribution of Given Quantum Circuit")
        self.histogramResult = plt
        self.results = results

def BackendFactory(backendType="HamiltionSimulation", settings=SettingsFile.Settings()):
    backendTypes = {
        "HamiltionSimulation" : HamiltonionBackend,
    }
    return backendTypes[backendType](settings)