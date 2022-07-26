# Gate Factory + Gates
import numpy as np

class IndividualGate:
    gate_name = "-"
    gate_transformation = np.array([[1, 0], [0, 1]])
    gate_point = [-1, -1]
    gate_qubitsInvolved = []
    gate_totalQubits = 1

    def __init__(self, name, transformation, qubitsInvolved):
        self.gate_name = name
        self.gate_transformation = transformation
        self.gate_qubitsInvolved = qubitsInvolved
    
    def getName(self):
        return self.gate_name;

    def setName(self, newName):
        self.gate_name = newName
    
    def getTransformation(self):
        return self.gate_transformation

    def setTransformation(self, newTransform):
        self.gate_transformation = newTransform

    def getPoint(self):
        if(self.gate_point[0] == -1 and self.gate_point[1] == -1):
            return None
        return self.gate_point
    
    def setPoint(self, newPoint):
        self.gate_point = newPoint

    def getInvolvedQubits(self):
        return self.getInvolvedQubits

    def setInvolvedQubits(self, newInvolved):
        self.gate_totalQubits = len(newInvolved)
        self.gate_qubitsInvolved = newInvolved

    def getNumQubits(self):
        assert(self.gate_totalQubits == 1)
        return self.gate_totalQubits

class MultipleGate(IndividualGate):
    gate_width = 1
    gate_height = 1

    gate_qubitsInvolved = []
    gate_controllingQubits = []

    def getDimensions(self):
        return [self.gate_width, self.gate_height]
    
    def setDimensions(self, newWidth, newHeight):
        self.gate_width = newWidth
        self.gate_height = newHeight

    def addControl(self, qubitIndex=-1):
        if(qubitIndex != -1):
            self.gate_qubitsInvolved.append(qubitIndex)
            self.gate_controllingQubits.append(qubitIndex)
            self.gate_totalQubits += 1

    def addInvolvedQubit(self, qubitIndex=-1):
        if(qubitIndex != -1):
            self.gate_qubitsInvolved.append(qubitIndex)
            self.gate_totalQubits += 1

    def getControllingQubits(self):
        return self.getControllingQubits


class UserGate(MultipleGate):
    gate_title = "UserDefinedGate"
    
    def getTitle(self):
        return self.gate_title
    
    def setTitle(self, newTitle):
        self.gate_title = newTitle

def GateFactory(gateType="Individual", name="-", transformation=np.array([[1, 0], [0, 1]]), qubitsInvolved=[-1]):
    gateTypes = {
        "Individual" : IndividualGate,
        "Multiple" : MultipleGate,
        "UserDefined" : UserGate,
    }
    return gateTypes[gateType](name, transformation, qubitsInvolved)