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
import matplotlib.cm as cm
import matplotlib as mpl
import itertools
import pandas as pd
import xcc
import strawberryfields as sf
import xcc.commands
import dimod
import cuquantum
from cuquantum import CircuitToEinsum
from qiskit_ibm_runtime import QiskitRuntimeService, Sampler
from dwave.system import LeapHybridCQMSampler
from strawberryfields import RemoteEngine, ops
from ParseCircuit import ParseCircuit
from tkinter import simpledialog, Tk
from qiskit import QuantumCircuit
from qiskit import Aer, transpile
from qiskit.compiler import transpile
from qiskit_aer.library.save_instructions.save_statevector import save_statevector


PC = ParseCircuit()

def get_api_key():
    root = Tk()
    root.withdraw()  # Hide the main window
    api_key = simpledialog.askstring("API Key Request", "Please enter your API key:")
    return api_key

def getGrid(grid, gridWidth, gridHeight):
    circuitOperators = [['-' for j in range(gridHeight)] for i in range(gridWidth)]
    for widthIdx in range(gridWidth):
        for heightIdx in range(gridHeight):
            name = grid[widthIdx][heightIdx].getName()
            if('CNOT' in name or 'CX' in name):
                print("Setting")
                circuitOperators[widthIdx][heightIdx+1] = "*"
            if(name != '-'):
                circuitOperators[widthIdx][heightIdx] = name
    return circuitOperators

def getInstructions(object_grid, gridWidth, gridHeight):
    grid = getGrid(object_grid, gridWidth, gridHeight)
    node = PC.parse(grid=grid)
    return PC.get_instructions(node)

def makeCircuit(qc, gate_sequence):
    # Iterate through the gate sequence and add gates to the circuit
    for gate, qubit_dict in gate_sequence:
        # The qubits on which the gate acts
        qubits = list(qubit_dict.keys())
        if gate == 'H':
            # Hadamard gate
            qc.h(qubits[0])
        elif gate.startswith('X'):
            # Pauli-X gate (with optional rotation angle)
            angle = gate.split('(')[1].split(')')[0] if '(' in gate else None
            angle = float(angle) if angle else None
            qc.rx(angle, qubits[0]) if angle else qc.x(qubits[0])
        elif gate.startswith('Y'):
            # Pauli-Y gate (with optional rotation angle)
            angle = gate.split('(')[1].split(')')[0] if '(' in gate else None
            angle = float(angle) if angle else None
            qc.ry(angle, qubits[0]) if angle else qc.y(qubits[0])
        elif gate.startswith('Z'):
            # Pauli-Y gate (with optional rotation angle)
            angle = gate.split('(')[1].split(')')[0] if '(' in gate else None
            angle = float(angle) if angle else None
            qc.rz(angle, qubits[0]) if angle else qc.z(qubits[0])
        elif gate == 'T':
            # T gate
            qc.t(qubits[0])
        elif gate == 'CX':
            # Controlled-X (CNOT) gate
            qc.cx(qubits[1], qubits[0])  # Control qubit, Target qubit
    return qc
    

def get_api_key():
    root = tk.Tk()
    root.withdraw()  # Hide the main window
    api_key = simpledialog.askstring("API Key Request", "Please enter your API key:")
    return api_key

def getGrid(grid, gridWidth, gridHeight):
    circuitOperators = [['-' for j in range(gridHeight)] for i in range(gridWidth)]
    for widthIdx in range(gridWidth):
        for heightIdx in range(gridHeight):
            name = grid[widthIdx][heightIdx].getName()
            if('CNOT' in name or 'CX' in name):
                print("Setting")
                circuitOperators[widthIdx][heightIdx+1] = "*"
            if(name != '-'):
                circuitOperators[widthIdx][heightIdx] = name
    return circuitOperators

def getInstructions(object_grid, gridWidth, gridHeight):
    grid = getGrid(object_grid, gridWidth, gridHeight)
    node = ParseCircuit.parse(grid)
    return ParseCircuit.get_instructions(node)

def makeCircuit(qc, gate_sequence):
    # Iterate through the gate sequence and add gates to the circuit
    for gate, qubit_dict in gate_sequence:
        # The qubits on which the gate acts
        qubits = list(qubit_dict.keys())
        if gate == 'H':
            # Hadamard gate
            qc.h(qubits[0])
        elif gate.startswith('X'):
            # Pauli-X gate (with optional rotation angle)
            angle = gate.split('(')[1].split(')')[0] if '(' in gate else None
            angle = float(angle) if angle else None
            qc.rx(angle, qubits[0]) if angle else qc.x(qubits[0])
        elif gate.startswith('Y'):
            # Pauli-Y gate (with optional rotation angle)
            angle = gate.split('(')[1].split(')')[0] if '(' in gate else None
            angle = float(angle) if angle else None
            qc.ry(angle, qubits[0]) if angle else qc.y(qubits[0])
        elif gate.startswith('Z'):
            # Pauli-Y gate (with optional rotation angle)
            angle = gate.split('(')[1].split(')')[0] if '(' in gate else None
            angle = float(angle) if angle else None
            qc.rz(angle, qubits[0]) if angle else qc.z(qubits[0])
        elif gate == 'T':
            # T gate
            qc.t(qubits[0])
        elif gate == 'CX':
            # Controlled-X (CNOT) gate
            qc.cx(qubits[1], qubits[0])  # Control qubit, Target qubit
    return qc
    
class HamiltonionBackend:
    provider = "Local"
    settings = None
    histogramResult = None
    results = None

    def __init__(self, newSettings):
        self.settings = newSettings
    
    def sendAPIToken(self):
        pass  # Instance method now, fixed missing self parameter
    
    def returnProbability(self, statevector, qubitsActive):
        projectTo = [np.array([0, 1]) if qubit else np.array([1, 0]) for qubit in qubitsActive]
        projectTo = np.array([1]).prod(projectTo)
        return np.dot(projectTo.conj().T, statevector)
    
    def getAllPossibilities(self, statevector, qubits):
        bin_str = [''.join(seq) for seq in itertools.product('01', repeat=qubits)]
        possibility = np.array(list(itertools.product([0, 1], repeat=qubits)))
        projectTo_vectorized = np.vectorize(self.returnProbability, excluded=['statevector'], signature='(n),(n)->()')
        probabilities = projectTo_vectorized(statevector=statevector, qubitsActive=possibility)
        probabilities = np.real(probabilities * np.conj(probabilities))
        phases = np.angle(probabilities)
        return [(bstr, prob, phase) for bstr, prob, phase in zip(bin_str, probabilities, phases) if prob > 0]

    def plot_graph(self, xVal, yVal, phases):
        df = pd.DataFrame({'x': xVal, 'y': yVal, 'phase': phases})
        df_sorted = df.sort_values('x')

        norm = mpl.colors.Normalize(vmin=0, vmax=np.pi)
        cmap = cm.hsv
        m = cm.ScalarMappable(norm=norm, cmap=cmap)
        colors = m.to_rgba(np.angle(phases))
        rotationAmount = math.floor(90 / (1 + np.exp(-((len(xVal) / 3) - 5))))

        plt.bar(df_sorted['x'], df_sorted['y'], width=0.4, color=colors)
        plt.xlabel("Computational Result")
        plt.ylabel("Probability (%)")
        rotationAmount = math.floor(90 / (1 + np.exp(-((len(xVal) / 3) - 5))))
        plt.xticks(rotation=rotationAmount)
        cbar = plt.colorbar(m)
        cbar.set_label('Relative Phase of State (Radians)', rotation=270, labelpad=20)
        plt.title("Probability Distribution of Given Quantum Circuit")
        self.histogramResult = plt
        plt.clf()

    def sendRequest(self, gridWidth, gridHeight, grid):
        instructions = getInstructions(grid, gridWidth, gridHeight)
        numQubits = gridHeight
        circuit = makeCircuit(QuantumCircuit(numQubits), instructions)
        circuit.save_statevector()
        
        simulator = Aer.get_backend('aer_simulator')
        circ = transpile(circuit, simulator)
        result = simulator.run(circ).result()
        statevector = np.array(result.get_statevector(circ))
        
        results = self.getAllPossibilities(statevector, numQubits)
        self.results = results
        self.result = result
        
        xVal, yVal = zip(*[(entry[0][::-1], entry[1]*100) for entry in results])
        phases = [entry[2] for entry in results]

        self.plot_graph(xVal, yVal, phases)
        
class FeynmanBackend:
    provider = "Local"
    settings = None
    histogramResult = None
    results = None

    def __init__(self, newSettings):
        self.settings = newSettings
    
    def sendAPIToken(self, api_string):  # Fixed missing self parameter
        pass  # Placeholder for actual implementation

    def plot_graph(self, xVal, yVal):
        df = pd.DataFrame({'x': xVal, 'y': yVal})
        df_sorted = df.sort_values('x')

        number_of_results = len(xVal)
        rotationAmount = math.floor(90 / (1 + np.exp(-((number_of_results / 3) - 5))))

        plt.bar(df_sorted['x'], df_sorted['y'], width=0.4)
        plt.xlabel("Computational Result")
        plt.ylabel("Probability (%)")
        plt.xticks(rotation=rotationAmount)
        plt.title("Probability Distribution of Given Quantum Circuit")
        self.histogramResult = plt

        plt.clf() 
    
    def sendRequest(self, gridWidth, gridHeight, grid):
        instructions = getInstructions(grid, gridWidth, gridHeight)  # Assuming getInstructions is defined
        numQubits = gridHeight

        circuit = QuantumCircuit(numQubits)
        circuit = makeCircuit(circuit, instructions)  # Assuming makeCircuit is defined
        circuit.measure_all()

        simulator = Aer.get_backend('aer_simulator_density_matrix')
        result = simulator.run(circuit).result()
        self.results = result.get_counts(circuit)

        # List comprehensions are more pythonic and concise
        total = sum(self.results.values())
        xVal = list(self.results.keys())
        yVal = [(count / total) * 100 for count in self.results.values()]

        self.plot_graph(xVal, yVal)
        
class HamiltonionCuQuantumBackend:
    provider = "Local"
    settings = None
    histogramResult = None
    results = None

    def __init__(self, newSettings):
        self.settings = newSettings
    
    def sendAPIToken(self):
        pass
    
    def plot_graph(self, xVal, yVal, phases):
        df = pd.DataFrame({'x': xVal, 'y': yVal, 'phase': phases})
        df_sorted = df.sort_values('x')

        norm = mpl.colors.Normalize(vmin=0, vmax=np.pi)
        cmap = cm.hsv
        m = cm.ScalarMappable(norm=norm, cmap=cmap)
        colors = m.to_rgba(np.angle(phases))
        rotationAmount = math.floor(90 / (1 + np.exp(-((len(xVal) / 3) - 5))))

        plt.bar(df_sorted['x'], df_sorted['y'], width=0.4, color=colors)
        plt.xlabel("Computational Result")
        plt.ylabel("Probability (%)")

        plt.xticks(rotation=rotationAmount)
        cbar = plt.colorbar(m)
        cbar.set_label('Relative Phase of State (Radians)', rotation=270, labelpad=20)
        plt.title("Probability Distribution of Given Quantum Circuit")
        self.histogramResult = plt

        plt.clf()

    def sendRequest(self, gridWidth, gridHeight, grid):
        instructions = getInstructions(grid, gridWidth, gridHeight)  # Assuming getInstructions is defined
        numQubits = gridHeight
        circuit = makeCircuit(QuantumCircuit(numQubits), instructions)  # Assuming makeCircuit is defined
                        
        myconverter = CircuitToEinsum(circuit, dtype='complex128', backend=np)

        # Setting cuQuantum configuration
        cuquantum.cutensornet.GateSplitAlgo = int(self.settings.gateSplit == 1)
        cuquantum.cutensornet.ABS_CUTOFF = self.settings.cuQuantumConfig[0]
        cuquantum.cutensornet.REL_CUTOFF = self.settings.cuQuantumConfig[1]

        # Perform tensor network contraction
        if len(self.settings.bitstringsSample) <= 1:
            print("Performing Tensor Network Contraction")
            expression, operands = myconverter.state_vector()
            sv = cuquantum.contract(expression, *operands)
            sv = sv.reshape(-1)
            print("Statevector found by Tensor Network Contraction")
            results = self.getAllPossibilities(sv, numQubits)
        else:
            print("Performing Selective Tensor Network Contraction")
            results = []
            for bitstring in self.settings.bitstringsSample:
                expression, operands = myconverter.amplitude(bitstring)
                amplitude = cuquantum.contract(expression, *operands)
                probability = abs(amplitude) ** 2
                results.append([bitstring, probability, np.angle(amplitude)])
            print("Finished sampling desired subset of distribution...")
        
        # Plotting
        xVal, yVal, phases = zip(*[(res[0][::-1], res[1] * 100, res[2]) for res in results])
        self.results = results
        self.plot_graph(xVal, yVal, phases)
        

    def getAllPossibilities(self, statevector, qubits):
        bitstrings = [''.join(seq) for seq in itertools.product('01', repeat=qubits)]
        probabilities = np.abs(statevector) ** 2
        phases = np.angle(statevector)
        return [(bitstring, prob, phase) for bitstring, prob, phase in zip(bitstrings, probabilities, phases) if prob > 0]

class DWaveBackend:
    provider = "DWave"
    settings = None
    histogramResult = None
    results = None
    API_Token = None

    def __init__(self, newSettings):
        self.settings = newSettings
        self.API_Token = "NONE"  # It's better to set default values in __init__

    def sendAPIToken(self, api_string):
        self.API_Token = api_string
    
    def plot_graph(self):
        if self.results is None:
            print("No data")
            return
        
        sampleset = self.results
        energies = sampleset.record.energy
        self.histogramResult = plt.hist(energies, bins='auto')
        plt.xlabel("Minimum Energy of Solutions")
        plt.ylabel("Number of Occurrences")
        plt.clf()


    def sendRequest(self):
        cqm = dimod.CQM()

        # Variable declarations should be handled safely without exec
        for var_declaration in self.settings.variableDeclarationsQUBO:
            exec(var_declaration) in {}, locals()

        # The objective function should be handled without eval
        if self.settings.objectiveQUBOS.startswith("max"):
            objective = eval(self.settings.objectiveQUBOS[4:]) * -1
        else:
            objective = eval(self.settings.objectiveQUBOS[4:])
        cqm.set_objective(objective)

        for constraint in self.settings.constraintsQUBO:
            cqm.add_constraint(eval(constraint))
        
        sampler = LeapHybridCQMSampler(token=self.API_Token or get_api_key())  # Use the API token or get a new one
        
        sampleset = sampler.sample_cqm(cqm, label='QuboParsing').filter(lambda row: row.is_feasible)
        self.results = sampleset
        
        self.plot_graph()

class XanaduBackend:
    provider = "Xanadu"
    settings = None
    histogramResult = None
    results = None
    API_KEY = "NONE"

    def __init__(self, newSettings):
        self.settings = newSettings
    
    def sendAPIToken(self, api_string):
        self.API_KEY = api_string
    
    def plot_graph(self):
        result = self.results

        print("Saved values...")
        # Save relevant infromation
        plt.bar(result.keys(), result.values(), 1, color='b')
        plt.xlabel("Fock Measurement State (binary representation for 'qubit' analysis)")
        plt.ylabel("Occurences")
        print("Saving Values...")
        self.histogramResult = plt

        plt.clf()

    def sendRequest(self, gridWidth, gridHeight, grid):
        circuit = sf.Program(gridHeight)

        # Gate mappings
        gate_operations = {
            "PD": lambda p: ops.Dgate(*p),
            "PX": lambda p: ops.Xgate(p[0]),
            "PZ": lambda p: ops.Zgate(p[0]),
            "PS": lambda p: ops.Sgate(p[0]),
            "PR": lambda p: ops.Rgate(p[0]),
            "PP": lambda p: ops.Pgate(p[0]),
            "PV": lambda p: ops.Vgate(p[0]),
            "PF": lambda p: ops.Fouriergate(),
            "PPV": lambda p: ops.Vacuum(),
            "PPC": lambda p: ops.Coherent(*p),
            "PPF": lambda p: ops.Fock(p[0]),
            "PBS": lambda p: ops.BSgate(*p),
            "PMZ": lambda p: ops.MZgate(*p),
            "PS2": lambda p: ops.S2gate(*p),
            "PCX": lambda p: ops.CXgate(p[0]),
            "PCZ": lambda p: ops.CZgate(p[0]),
            "PCK": lambda p: ops.CKgate(p[0]),
        }

        with circuit.context as q:
            for widthIdx in range(gridWidth):
                for heightIdx in range(gridHeight):
                    gate_name = grid[widthIdx][heightIdx].getName()
                    if gate_name != '-':
                        gate_params = self.settings.specialGridSettings.get((widthIdx, heightIdx), [])
                        operation = gate_operations.get(gate_name)
                        if operation:
                            operation(gate_params) | q[widthIdx]
                            if gate_name in ["PBS", "PMZ", "PS2", "PCX", "PCZ", "PCK"]:
                                # Skip the next qubit since it's part of a two-qubit gate
                                heightIdx += 1

        ops.MeasureFock() | q  # Measurement at the end of the circuit

        if(self.API_Token == "NONE"):
            self.API_Token = get_api_key()
        
        # Save API token, ping for request
        xcc.Settings(REFRESH_TOKEN=self.API_KEY).save()
        xcc.commands.ping()

        # Get remote results with Guassian Technique backend
        eng = RemoteEngine("simulon_gaussian")
        results = eng.run(circuit, shots=100)
        print("Got Results")
        print(results)
        result = {}
        # Add results and get fock measurement (modal results)
        for entry in results.samples:
            s = ""
            for item in entry:
                s += str(item) + ","
            if(s[:len(s)-1] not in result):
                result[s[:len(s)-1]] = 1
            else:
                result[s[:len(s)-1]] += 1
        
        self.results = result

class QiskitBackend:
    provider = "Qiskit"
    settings = None
    histogramResult = None
    results = None
    API_KEY = "NONE"


    def __init__(self, newSettings):
        self.settings = newSettings
    
    def sendAPIToken(self, api_string):
        self.API_KEY = api_string

    def plot_graph(self, xVal, yVal):
        xVal = []
        yVal = []
        total = 0
        for _, y in self.results.items():
            total += y
        for a, b in self.results.items():
            xVal.append(str(bin(a))[2:])
            yVal.append((b / total) * 100)

        df = pd.DataFrame(
            dict(
                x=xVal,
                y=yVal
            )
        )

        df_sorted = df.sort_values('x')
        plt.bar(df_sorted['x'], df_sorted['y'], width = 0.4)
        plt.xlabel("Computational Result")
        plt.ylabel("Probability")
        rotationAmount = math.floor(90/(1 + np.exp(-(((len(xVal))/3)-5))))
        plt.xticks(rotation = rotationAmount)
        plt.title("Probability Distribution of Given Quantum Circuit")
        self.histogramResult = plt
        print(self.results)
        
    
    def sendRequest(self, gridWidth, gridHeight, grid):
        # Get results, store figure, normalize, apply phase scalar map
# Do similar decomposition process
        instructions = getInstructions(grid, gridWidth, gridHeight)
        numQubits = gridHeight

        # Make qiskit circuit
        circuit = QuantumCircuit(numQubits)
        circuit = makeCircuit(circuit, instructions)     
        circuit.measure_all()
        if(self.API_KEY == "NONE"):
            self.API_KEY = get_api_key()
        
        service = QiskitRuntimeService(channel="ibm_quantum", instance="ibm-q/open/main", token=self.API_KEY)
        backend = service.least_busy(simulator=True)
        sampler = Sampler(backend) 
        job = sampler.run(circuit) 
        result = job.result() 
        # Produce results
        self.results = result.quasi_dists[0]

        self.plot_graph()


def BackendFactory(backendType="HamiltonionSimulation", settings=SettingsFile.Settings()):
    backendTypes = {
        "HamiltonionSimulation": HamiltonionBackend,
        "FeynmanSimulation": FeynmanBackend,
        "HamiltonionSimulationCuQuantum": HamiltonionCuQuantumBackend,
        "DWaveSimulation": DWaveBackend,
        "Photonic": XanaduBackend,
        "Qiskit": QiskitBackend
    }
    return backendTypes[backendType](settings)
