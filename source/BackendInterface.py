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