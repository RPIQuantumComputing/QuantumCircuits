from abc import ABC, abstractmethod 

class Backend(ABC):
	@abstractmethod
	def sendAPIToken(self):
		pass

	@abstractmethod
	def sendRequest(self, gridWidth, gridHeight, grid):
		pass

	@abstractmethod
	def display(self):
		pass
	
	def findCircuitOperators(self, gridWidth, gridHeight, grid):
		circuitOperators = [[['-', [j]] for j in range(gridHeight)] for i in range(gridWidth)]
		for widthIdx in range(gridWidth):
			for heightIdx in range(gridHeight):
				if(grid[widthIdx][heightIdx].getName() != '-'):
					circuitOperators[widthIdx][heightIdx] = [grid[widthIdx][heightIdx].getName(), grid[widthIdx][heightIdx].gate_qubitsInvolved]
					if(grid[widthIdx][heightIdx].getName() == 'CNOT'):
						circuitOperators[widthIdx][heightIdx+1] = [grid[widthIdx][heightIdx].getName(), grid[widthIdx][heightIdx].gate_qubitsInvolved]
		
		return circuitOperators