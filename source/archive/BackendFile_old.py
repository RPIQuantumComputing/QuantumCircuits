import SettingsFile
import math
import matplotlib.pyplot as plt

# Check to ensure cupy support or default to numpy
hasCupy = True
try:
	import cupy as np
except:
	import numpy as np
	hasCupy = False
# Various Imports
import numpy as tnp
import matplotlib.cm as cm
import matplotlib as mpl
import itertools
import pandas as pd
import strawberryfields as sf
import cuquantum
import xcc
import xcc.commands
import dimod
from qiskit import QuantumCircuit
from qiskit import Aer, transpile
from qiskit import IBMQ
from qiskit.compiler import transpile, assemble
from qiskit_aer.library.save_instructions.save_statevector import save_statevector
from BackendInterface import Backend
from strawberryfields import ops
from strawberryfields import RemoteEngine
from cuquantum import contract
from dwave.system import LeapHybridCQMSampler
from cuquantum import CircuitToEinsum


class HamiltonionBackend(Backend):
	provider = "Local"
	settings = None
	histogramResult = None
	results = None
	df = None
	xVal = None
	yVal = None
	
	def __init__(self, newSettings):
		self.settings = newSettings
	
	def sendAPIToken():
		pass
	
	def sendRequest(self, gridWidth, gridHeight, grid):
		# Get results, store figure, normalize, apply phase scalar map
# Do similar decomposition process
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

		# Make qiskit gate
		circuit = QuantumCircuit(numQubits)
		for widthIdx in range(gridWidth):

			for heightIdx in range(gridHeight):
				if(grid[widthIdx][heightIdx].getName() != '-'):
					if(grid[widthIdx][heightIdx].getName() == 'H'):
						circuit.h(heightIdx)
					if(grid[widthIdx][heightIdx].getName() == 'X'):
						circuit.x(heightIdx)
					if(grid[widthIdx][heightIdx].getName() == 'Y'):
						circuit.y(heightIdx)
					if(grid[widthIdx][heightIdx].getName() == 'Z'):
						circuit.z(heightIdx)
					if(grid[widthIdx][heightIdx].getName() == 'S'):
						circuit.s(heightIdx)
					if(grid[widthIdx][heightIdx].getName() == 'T'):
						circuit.t(heightIdx)
					if(grid[widthIdx][heightIdx].getName() == 'CNOT'):
						circuit.cnot(heightIdx, heightIdx + 1)
						heightIdx += 1
		circuit.save_statevector()
		# Compute the probability of certain qubits being 1, i.e. specific bitstring result
		def returnProbabilitiy(statevector, qubitsActive):
			projectTo = np.array([1])
			for entry in range(0, len(qubitsActive)):
				if(qubitsActive[entry] == 1):
					projectTo = np.kron(projectTo, np.array([0, 1]))
				else:
					projectTo = np.kron(projectTo, np.array([1, 0]))
			projectTo = projectTo
			projectTo = np.transpose(projectTo)
			dotProduct = projectTo.dot(statevector)
			return dotProduct
		
		def getAllPossibilities(statevector, qubits):
			bin_str = [''.join(p) for p in itertools.product('01', repeat=qubits)]
			possibility = [list(p) for p in itertools.product([0, 1], repeat=qubits)]
			result = []
			for entry in range(len(possibility)):
				dotProduct = returnProbabilitiy(statevector, possibility[entry])
				probability = np.real(dotProduct * np.conj(dotProduct))
				phase = np.angle(dotProduct)
				if(probability > 0):
					result.append([bin_str[entry], probability, phase])
			return result
		
		# Save results
		simulator = Aer.get_backend('aer_simulator')
		circ = transpile(circuit, simulator)

		# Run and get statevector
		result = simulator.run(circ).result()
		sv = result.get_statevector(circ)
		sv = np.array(sv)
		results = getAllPossibilities(sv, numQubits)
		self.result = result
		self.xVal = []
		self.yVal = []
		norm = mpl.colors.Normalize(vmin=0, vmax=np.pi)
		cmap = cm.hsv
		m = cm.ScalarMappable(norm=norm, cmap=cmap)
		# Normalize to 100% (show percentages, not decimals)
		for entry in results:
			self.xVal.append(entry[0][::-1])
			if(hasCupy):
				self.yVal.append(entry[1].get()*100)
			else:
				self.yVal.append(entry[1]*100)
		if(hasCupy):
			phases = [m.to_rgba(tnp.angle(results[j][2].get() * 1j)) for j in range(len(results))]
		else:
			phases = [m.to_rgba(tnp.angle(results[j][2] * 1j)) for j in range(len(results))]
		# Values are not sorted, do your magic pandas!
		self.df = pd.DataFrame(
			dict(
				x=self.xVal,
				y=self.yVal,
				phase=phases
			)
		)

	def display(self):
		df_sorted = self.df.sort_values('x')
		
		# Make graph
		plt.bar(df_sorted['x'], df_sorted['y'], width = 0.4, color = df_sorted['phase'])
		plt.xlabel("Computational Result")
		plt.ylabel("Probability")
		
		# Empirical formula to find rotations
		rotationAmount = math.floor(90/(1 + np.exp(-(((len(self.xVal))/3)-5))))
		plt.xticks(rotation = rotationAmount)

		norm = mpl.colors.Normalize(vmin=0, vmax=np.pi)
		cmap = cm.hsv
		m = cm.ScalarMappable(norm=norm, cmap=cmap)

		cbar = plt.colorbar(m)
		cbar.set_label('Relative Phase of State (Radians)', rotation=-90, labelpad=20)
		plt.title("Probability Distribution of Given Quantum Circuit")
		self.histogramResult = plt
		plt.show()
		#self.update(show=True)
		#self.results = results

class FeynmanBackend(Backend):
	provider = "Local"
	settings = None
	histogramResult = None
	results = None
	df = None
	xVal = None
	yVal = None


	def __init__(self, newSettings):
		self.settings = newSettings
	
	def sendAPIToken(api_string):
		pass
	
	def sendRequest(self, gridWidth, gridHeight, grid):
		# Do similar decomposition process
		numQubits = gridHeight
		
		# Make qiskit gate
		circuit = QuantumCircuit(numQubits)
		for widthIdx in range(gridWidth):
			for heightIdx in range(gridHeight):
				if(grid[widthIdx][heightIdx].getName() != '-'):
					if(grid[widthIdx][heightIdx].getName() == 'H'):
						circuit.h(heightIdx)
					if(grid[widthIdx][heightIdx].getName() == 'X'):
						circuit.x(heightIdx)
					if(grid[widthIdx][heightIdx].getName() == 'Y'):
						circuit.y(heightIdx)
					if(grid[widthIdx][heightIdx].getName() == 'Z'):
						circuit.z(heightIdx)
					if(grid[widthIdx][heightIdx].getName() == 'S'):
						circuit.s(heightIdx)
					if(grid[widthIdx][heightIdx].getName() == 'T'):
						circuit.t(heightIdx)
					if(grid[widthIdx][heightIdx].getName() == 'CNOT'):
						circuit.cnot(heightIdx, heightIdx + 1)
						heightIdx += 1
		circuit.measure_all()
		# Save results
		simulator = Aer.get_backend('aer_simulator_density_matrix')
		self.results = simulator.run(circuit).result().get_counts(circuit)
		# fig = plt.figure(figsize = (20, 5))
		self.xVal = []
		self.yVal = []
		total = 0
		# Turn into histogram format
		for _, y in self.results.items():
			total += y
		for a, b in self.results.items():
			self.xVal.append(a)
			self.yVal.append((b / total) * 100)

		self.df = pd.DataFrame(
			dict(
				x=self.xVal,
				y=self.yVal
			)
		)
		# Same plotting as before

	def display(self):
		df_sorted = self.df.sort_values('x')
		plt.bar(df_sorted['x'], df_sorted['y'], width = 0.4)
		plt.xlabel("Computational Result")
		plt.ylabel("Probability")
		rotationAmount = math.floor(90/(1 + np.exp(-(((len(self.xVal))/3)-5))))
		plt.xticks(rotation = rotationAmount)
		plt.title("Probability Distribution of Given Quantum Circuit")
		self.histogramResult = plt
		plt.show()
		#self.update(show=True)
		#print(self.results)
		
class HamiltonionCuQuantumBackend(Backend):
	provider = "Local"
	settings = None
	histogramResult = None
	results = None
	df = None
	xVal = None
	yVal = None

	def __init__(self, newSettings):
		self.settings = newSettings
	
	def sendAPIToken():
		pass
	
	def sendRequest(self, gridWidth, gridHeight, grid):
		# Get results, store figure, normalize, apply phase scalar map
		numQubits = gridHeight

		# Make qiskit gate
		circuit = QuantumCircuit(numQubits)
		for widthIdx in range(gridWidth):
			for heightIdx in range(gridHeight):
				if(grid[widthIdx][heightIdx].getName() != '-'):
					if(grid[widthIdx][heightIdx].getName() == 'H'):
						circuit.h(heightIdx)
					if(grid[widthIdx][heightIdx].getName() == 'X'):
						circuit.x(heightIdx)
					if(grid[widthIdx][heightIdx].getName() == 'Y'):
						circuit.y(heightIdx)
					if(grid[widthIdx][heightIdx].getName() == 'Z'):
						circuit.z(heightIdx)
					if(grid[widthIdx][heightIdx].getName() == 'S'):
						circuit.s(heightIdx)
					if(grid[widthIdx][heightIdx].getName() == 'T'):
						circuit.t(heightIdx)
					if(grid[widthIdx][heightIdx].getName() == 'CNOT'):
						circuit.cnot(heightIdx, heightIdx + 1)
						heightIdx += 1
						
		myconverter = CircuitToEinsum(circuit, dtype='complex128', backend=np)
		# Compute the probability of certain qubits being 1, i.e. specific bitstring result
		def returnProbabilitiy(statevector, qubitsActive):
			projectTo = np.array([1])
			for entry in range(0, len(qubitsActive)):
				if(qubitsActive[entry] == 1):
					projectTo = np.kron(projectTo, np.array([0, 1]))
				else:
					projectTo = np.kron(projectTo, np.array([1, 0]))
			projectTo = projectTo
			projectTo = np.transpose(projectTo)
			dotProduct = projectTo.dot(statevector)
			return dotProduct
		
		def getAllPossibilities(statevector, qubits):
			bin_str = [''.join(p) for p in itertools.product('01', repeat=qubits)]
			possibility = [list(p) for p in itertools.product([0, 1], repeat=qubits)]
			result = []
			for entry in range(len(possibility)):
				dotProduct = returnProbabilitiy(statevector, possibility[entry])
				probability = np.real(dotProduct * np.conj(dotProduct))
				phase = np.angle(dotProduct)
				if(probability > 0):
					result.append([bin_str[entry], probability, phase])
			return result
		
		if(self.settings.gateSplit == 1):
			print("Enabling Gate Split...")
			cuquantum.cutensornet.GateSplitAlgo = 1
		else:
			cuquantum.cutensornet.GateSplitAlgo = 0
		cuquantum.cutensornet.ABS_CUTOFF = self.settings.cuQuantumConfig[0]
		cuquantum.cutensornet.REL_CUTOFF = self.settings.cuQuantumConfig[1]
				
		# Save results
		if(len(self.settings.bitstringsSample) <= 1):
			print("Performing Tensor Network Contraction")
			expression, operands = myconverter.state_vector()
			sv = contract(expression, *operands)
			sv = sv.reshape(-1)
			print("Statevector found by Tensor Network Contraction")
			results = getAllPossibilities(sv, numQubits)
			self.results = results
		else:
			print("Performing Selective Tensor Network Contraction")
			results = []
			for bitstring in self.settings.bitstringsSample:
				expression, operands = myconverter.amplitude(bitstring)
				amplitude = contract(expression, *operands)
				probability = abs(amplitude) ** 2
				results.append([bitstring, probability, np.angle(amplitude)])
			self.results = results
			print("Finished sampling desired subset of distribution...")
		# fig = plt.figure(figsize = (20, 5))
		self.xVal = []
		self.yVal = []
		norm = mpl.colors.Normalize(vmin=0, vmax=np.pi)
		cmap = cm.hsv
		m = cm.ScalarMappable(norm=norm, cmap=cmap)
		# Normalize to 100% (show percentages, not decimals)
		for entry in results:
			self.xVal.append(entry[0][::-1])
			if(hasCupy):
				self.yVal.append(entry[1].get()*100)
			else:
				self.yVal.append(entry[1]*100)
		if(hasCupy):
			phases = [m.to_rgba(tnp.angle(results[j][2].get() * 1j)) for j in range(len(results))]
		else:
			phases = [m.to_rgba(tnp.angle(results[j][2] * 1j)) for j in range(len(results))]
		# Values are not sorted, do your magic pandas!
		self.df = pd.DataFrame(
			dict(
				x=self.xVal,
				y=self.yVal,
				phase=phases
			)
		)

	def display(self):
		df_sorted = self.df.sort_values('x')
		# Make graph
		plt.bar(df_sorted['x'], df_sorted['y'], width = 0.4, color = df_sorted['phase'])
		plt.xlabel("Computational Result")
		plt.ylabel("Probability")
		# Empirical formula to find rotations
		rotationAmount = math.floor(90/(1 + np.exp(-(((len(self.xVal))/3)-5))))
		plt.xticks(rotation = rotationAmount)
		norm = mpl.colors.Normalize(vmin=0, vmax=np.pi)
		cmap = cm.hsv
		m = cm.ScalarMappable(norm=norm, cmap=cmap)
		cbar = plt.colorbar(m)
		cbar.set_label('Relative Phase of State (Radians)', rotation=-90, labelpad=20)
		plt.title("Probability Distribution of Given Quantum Circuit")
		self.histogramResult = plt
		plt.show()
		#self.update(show=True)

class DWaveBackend(Backend):
	provider = "DWave"
	settings = None
	histogramResult = None
	results = None
	sampleSet = None
	API_Token = "DEV-2a83ec13135e2944cebbeddf32592573221b3937"

	def __init__(self, newSettings):
		self.settings = newSettings
	
	def sendAPIToken(self, api_string):
		self.API_Token = api_string
	
	def sendRequest(self):
		# Initalize a constraint quadratic model
		cqm = dimod.CQM()
		
		# Execute variable declarations
		for entry in self.settings.variableDeclarationsQUBO:
			if(len(entry) > 1):
				exec(entry)
		# Extract objective function
		objectiveFunction = self.settings.objectiveQUBOS
		print(self.settings.objectiveQUBOS)
		# Set objective
		if("max" in objectiveFunction):
			eval("cqm.set_objective(" + "-1*(" + objectiveFunction[4:] + ")" + ")")
		else:
			eval("cqm.set_objective(" + objectiveFunction[4:] + ")")
		# Add constraints
		for entry in self.settings.constraintsQUBO:
			if(len(entry) > 1):
				eval("cqm.add_constraint(" + entry + ")")
		# Use token to sample solutions and filter out infeasible ones
		sampler = LeapHybridCQMSampler(token=self.API_Token)     
		self.sampleset = sampler.sample_cqm(cqm, label='QuboParsing')
		self.sampleset = self.sampleset.filter(lambda row: row.is_feasible)
		self.results = self.sampleset
		# Get resulting energies and save result
	def display(self):
		valuesFound = []
		for energy, in self.sampleset.data(fields=['energy']):
			valuesFound.append(energy)
		plt.hist(valuesFound)
		plt.xlabel("Minimum Energy of Solutions")
		plt.ylabel("Amount of Occurences")
		self.histogramResult = plt
		plt.show()
		#self.update(show=True)

class XanaduBackend(Backend):
	provider = "Xanadu"
	settings = None
	histogramResult = None
	results = None
	result = {}
	API_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCIgOiAiSldUIiwia2lkIiA6ICIwYTdjOGE5Yi1lMzdkLTQ0MzItOTU2OC0xNzI3YzEwNmYyMzEifQ.eyJpYXQiOjE2NTg2MTU5MzUsImp0aSI6IjE5NDNmYTU5LWYxZmMtNDczZS04ZDliLThjZGE2MGVmOGE5MyIsImlzcyI6Imh0dHBzOi8vcGxhdGZvcm0ueGFuYWR1LmFpL2F1dGgvcmVhbG1zL3BsYXRmb3JtIiwiYXVkIjoiaHR0cHM6Ly9wbGF0Zm9ybS54YW5hZHUuYWkvYXV0aC9yZWFsbXMvcGxhdGZvcm0iLCJzdWIiOiJmMmIwYmJkYi05NzJkLTRiZDgtYjZhOS0xNTU3MWY4NDVlNjMiLCJ0eXAiOiJPZmZsaW5lIiwiYXpwIjoicHVibGljIiwic2Vzc2lvbl9zdGF0ZSI6ImIyNTI4ZmZlLTUwNzUtNDMwYy05YWZkLTdiZDA0MmI1ZTEwYyIsInNjb3BlIjoicHVibGljLXJvbGVzIHByb2ZpbGUgZW1haWwgb2ZmbGluZV9hY2Nlc3MiLCJzaWQiOiJiMjUyOGZmZS01MDc1LTQzMGMtOWFmZC03YmQwNDJiNWUxMGMifQ.c0wXKPXBCqfB9hOoFCe7-Fp-oSJ8wY2Sa_Sgvmn4-Oc"

	def __init__(self, newSettings):
		self.settings = newSettings
		#self.result = {}
	
	def sendAPIToken(self, api_string):
		self.API_KEY = api_string
	
	def sendRequest(self, gridWidth, gridHeight, grid):
		numQubits = gridHeight

		# Assume fock measurement
		# measurementType = ["F" for i in range(numQubits)]
		# Initalize program
		circuit = sf.Program(numQubits)
		with circuit.context as q:
			gate_operations = {
				"PD": (ops.Dgate, 2),
				"PX": (ops.Xgate, 1),
				"PZ": (ops.Zgate, 1),
				"PS": (ops.Sgate, 1),
				"PR": (ops.Rgate, 1),
				"PP": (ops.Pgate, 1),
				"PV": (ops.Vgate, 1),
				"PF": (ops.Fouriergate, 0),
				"PPV": (ops.Vacuum, 0),
				"PPC": (ops.Coherent, 2),
				"PPF": (ops.Fock, 1),
				"PBS": (ops.BSgate, 2, True),
				"PMZ": (ops.MZgate, 2, True),
				"PS2": (ops.S2gate, 2, True),
				"PCX": (ops.CXgate, 1, True),
				"PCZ": (ops.CZgate, 1, True),
				"PCK": (ops.CKgate, 1, True)
			}

			for widthIdx in range(gridWidth):
				heightIdx = 0
				while heightIdx < gridHeight:
					gate_name = grid[widthIdx][heightIdx].getName()
					if gate_name in gate_operations:
						op, num_params, is_dual_qubit = gate_operations[gate_name] + (False,)
						params = self.settings.specialGridSettings[(widthIdx, heightIdx)][:num_params]
						if is_dual_qubit:
							op(*params) | (q[widthIdx], q[widthIdx + 1])
							heightIdx += 1
						else:
							op(*params) | q[widthIdx]
					heightIdx += 1

			ops.MeasureFock() | q  # Assume fock measurement technique


		# Save API token, ping for request
		xcc.Settings(REFRESH_TOKEN=self.API_KEY).save()
		xcc.commands.ping()

		# Get remote results with Guassian Technique backend
		eng = RemoteEngine("simulon_gaussian")
		results = eng.run(circuit, shots=100)
		print("Got Results")
		print(results)
		#result = {}
		# Add results and get fock measurement (modal results)
		for entry in results.samples:
			s = ""
			for item in entry:
				s += str(item) + ","
			if(s[:len(s)-1] not in self.result):
				self.result[s[:len(s)-1]] = 1
			else:
				self.result[s[:len(s)-1]] += 1
		print("Saved values...")
		# Save relevant infromation
		#fig = plt.figure(figsize = (20, 5))
    
	def display(self):
		plt.bar(self.result.keys(), self.result.values(), 1, color='b')
		plt.xlabel("Fock Measurement State (binary representation for 'qubit' analysis)")
		plt.ylabel("Occurences")
		print("Saving Values...")
		self.histogramResult = plt
		plt.show()
		#self.update(show=True)

class QiskitBackend(Backend):
	provider = "Qiskit"
	settings = None
	histogramResult = None
	results = None
	API_KEY = "55b82f2dcb56e1a96a368905f14504a9c229c9cc212ab7b7f46039e087d54e201c3205f07ba1efed86d880fb82635a630803b072669020cd6eb43589f1abaa0d"
	df = None
	xVal = None
	yVal = None

	def __init__(self, newSettings):
		self.settings = newSettings
	
	def sendAPIToken(self, api_string):
		self.API_KEY = api_string
	
	def sendRequest(self, gridWidth, gridHeight, grid):
		# Same as before in Feynman
		numQubits = gridHeight
		circuit = QuantumCircuit(numQubits)
		for widthIdx in range(gridWidth):
			for heightIdx in range(gridHeight):
				if(grid[widthIdx][heightIdx].getName() != '-'):
					if(grid[widthIdx][heightIdx].getName() == 'H'):
						circuit.h(heightIdx)
					if(grid[widthIdx][heightIdx].getName() == 'X'):
						circuit.x(heightIdx)
					if(grid[widthIdx][heightIdx].getName() == 'Y'):
						circuit.y(heightIdx)
					if(grid[widthIdx][heightIdx].getName() == 'Z'):
						circuit.z(heightIdx)
					if(grid[widthIdx][heightIdx].getName() == 'S'):
						circuit.s(heightIdx)
					if(grid[widthIdx][heightIdx].getName() == 'T'):
						circuit.t(heightIdx)
					if(grid[widthIdx][heightIdx].getName() == 'CNOT'):
						circuit.cnot(heightIdx, heightIdx + 1)
						heightIdx += 1
		circuit.measure_all()
		# This time, use the QaSM provider
		IBMQ.save_account(self.API_KEY, overwrite=True)
		provider = IBMQ.load_account()
		backend = provider.get_backend('ibmq_qasm_simulator')
		transpiled = transpile(circuit, backend=backend)
		qobj = assemble(transpiled, backend=backend, shots=1024)
		job = backend.run(qobj)
		print(job.status()) # Tell the user results are pending
		# Produce results
		self.results = job.result().get_counts(circuit)
		self.xVal = []
		self.yVal = []
		total = 0
		for _, y in self.results.items():
			total += y
		for a, b in self.results.items():
			self.xVal.append(a)
			self.yVal.append((b / total) * 100)

		self.df = pd.DataFrame(
			dict(
				x=self.xVal,
				y=self.yVal
			)
		)
	
	def display(self):
		df_sorted = self.df.sort_values('x')
		plt.bar(df_sorted['x'], df_sorted['y'], width = 0.4)
		plt.xlabel("Computational Result")
		plt.ylabel("Probability")
		rotationAmount = math.floor(90/(1 + np.exp(-(((len(self.xVal))/3)-5))))
		plt.xticks(rotation = rotationAmount)
		plt.title("Probability Distribution of Given Quantum Circuit")
		self.histogramResult = plt
		plt.show()
		#self.update(show=True)
		#print(self.results)

# Backend factor to create gates
def BackendFactory(backendType="HamiltionSimulation", settings=SettingsFile.Settings()):
	backendTypes = {
		"HamiltionSimulation" : HamiltonionBackend,
		"FeynmanSimulation" : FeynmanBackend,
		"HamiltionSimulationCuQuantum": HamiltonionCuQuantumBackend,
		"DWaveSimulation" : DWaveBackend,
		"Photonic": XanaduBackend,
		"Qiskit": QiskitBackend
	}
	return backendTypes[backendType](settings)