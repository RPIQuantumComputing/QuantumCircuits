import numpy as np
import GateFile
import DesignerFile

print("This is an illustration of how to interface with the backend")

# Gate Creation
print("Moving to single qubit")
individualGate = GateFile.GateFactory(gateType="Individual", name="FirstGate", transformation=np.matrix([[1,0], [0, 1]]), qubitsInvolved=[0])
individualGate.setPoint([0, 0]) # Set its location to upper left
individualGate.setName("FirstIndividualGate") # Set its name
print(individualGate.getName())
print(individualGate.getTransformation())
print(individualGate.getPoint())

# Multiple Qubit Gate Creation
print("Moving to multiple qubits v2")
multiGate = GateFile.GateFactory(gateType="Multiple", name="SecondGate", transformation=np.matrix([[1,0], [0, 1]]), qubitsInvolved=[1])

# Let us look at the Designer
designer = DesignerFile.Designer()
designer.gateAddition("H", 0, 0)
designer.gateAddition("H", 0, 1)
designer.gateAddition("H", 0, 2)
designer.gateAddition("H", 0, 3)
designer.gateAddition("T", 1, 3)
designer.gateAddition("S", 1, 2)
designer.gateAddition("CNOT", 2, 0)
#designer.gateRemoval(2, 0)
designer.printDesign()

# Now, one can run the simulation
designer.runSimulation()
designer.saveSimulationToFile()

# We can test loading from file
designer2 = DesignerFile.Designer()
designer2.loadSimulationFromFile()
plt = designer2.getVisualization()
#plt.show()