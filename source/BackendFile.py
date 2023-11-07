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
import xcc.commands
import xcc
import xcc.commands
from strawberryfields import RemoteEngine
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
    
class HamiltonionBackend:
    provider = "Local"
    settings = None
    histogramResult = None
    results = None

    def __init__(self, newSettings):
        self.settings = newSettings
    
    def sendAPIToken():
        pass
    
    # Compute the probability of certain qubits being 1, i.e. specific bitstring result
    def returnProbability(self, statevector, qubitsActive):
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
    
    def getAllPossibilities(self, statevector, qubits):
            bin_str = [''.join(p) for p in itertools.product('01', repeat=qubits)]
            possibility = [list(p) for p in itertools.product([0, 1], repeat=qubits)]
            result = []
            for entry in range(len(possibility)):
                dotProduct = self.returnProbability(statevector, possibility[entry])
                probability = np.real(dotProduct * np.conj(dotProduct))
                phase = np.angle(dotProduct)
                if(probability > 0):
                    result.append([bin_str[entry], probability, phase])
            return result

    def sendRequest(self, gridWidth, gridHeight, grid):
        # Get results, store figure, normalize, apply phase scalar map
        # Do similar decomposition process
        instructions = getInstructions(grid, gridWidth, gridHeight)
        numQubits = gridHeight

        # Make qiskit circuit
        circuit = QuantumCircuit(numQubits)
        circuit = makeCircuit(circuit, instructions)     
        circuit.save_statevector()
        
        # Save results
        simulator = Aer.get_backend('aer_simulator')
        circ = transpile(circuit, simulator)

        # Run and get statevector
        result = simulator.run(circ).result()
        sv = result.get_statevector(circ)
        sv = np.array(sv)
        results = self.getAllPossibilities(sv, numQubits)
        self.result = result
        # fig = plt.figure(figsize = (20, 5))
        xVal = []
        yVal = []
        norm = mpl.colors.Normalize(vmin=0, vmax=np.pi)
        cmap = cm.hsv
        m = cm.ScalarMappable(norm=norm, cmap=cmap)

        # Normalize to 100% (show percentages, not decimals)
        for entry in results:
            xVal.append(entry[0][::-1])
            if(hasCupy):
                yVal.append(entry[1].get()*100)
            else:
                yVal.append(entry[1]*100)
        if(hasCupy):
            phases = [m.to_rgba(tnp.angle(results[j][2].get() * 1j)) for j in range(len(results))]
        else:
            phases = [m.to_rgba(tnp.angle(results[j][2] * 1j)) for j in range(len(results))]
            
        # Values are not sorted, do your magic pandas!
        df = pd.DataFrame(
            dict(
                x=xVal,
                y=yVal,
                phase=phases
            )
        )

        df_sorted = df.sort_values('x')
        # Make graph
        plt.bar(df_sorted['x'], df_sorted['y'], width = 0.4, color = df_sorted['phase'])
        plt.xlabel("Computational Result")
        plt.ylabel("Probability")
        # Empirical formula to find rotations
        rotationAmount = math.floor(90/(1 + np.exp(-(((len(xVal))/3)-5))))
        plt.xticks(rotation = rotationAmount)
        cbar = plt.colorbar(m)
        cbar.set_label('Relative Phase of State (Radians)', rotation=-90, labelpad=20)
        plt.title("Probability Distribution of Given Quantum Circuit")
        self.histogramResult = plt
        self.results = results

        plt.clf()

class FeynmanBackend:
    provider = "Local"
    settings = None
    histogramResult = None
    results = None

    def __init__(self, newSettings):
        self.settings = newSettings
    
    def sendAPIToken(api_string):
        pass
    
    def sendRequest(self, gridWidth, gridHeight, grid):
        # Do similar decomposition process
        instructions = getInstructions(grid, gridWidth, gridHeight)
        numQubits = gridHeight

        # Make qiskit circuit
        circuit = QuantumCircuit(numQubits)
        circuit = makeCircuit(circuit, instructions)     
        circuit.measure_all()        
        # Save results
        simulator = Aer.get_backend('aer_simulator_density_matrix')
        self.results = simulator.run(circuit).result().get_counts(circuit)
        xVal = []
        yVal = []
        total = 0
        # Turn into histogram format
        for _, y in self.results.items():
            total += y
        for a, b in self.results.items():
            xVal.append(a)
            yVal.append((b / total) * 100)

        df = pd.DataFrame(
            dict(
                x=xVal,
                y=yVal
            )
        )
        # Same plotting as before
        df_sorted = df.sort_values('x')
        plt.bar(df_sorted['x'], df_sorted['y'], width = 0.4)
        plt.xlabel("Computational Result")
        plt.ylabel("Probability")
        rotationAmount = math.floor(90/(1 + np.exp(-(((len(xVal))/3)-5))))
        plt.xticks(rotation = rotationAmount)
        plt.title("Probability Distribution of Given Quantum Circuit")
        self.histogramResult = plt
        print(self.results)

        plt.clf()
        
class HamiltonionCuQuantumBackend:
    provider = "Local"
    settings = None
    histogramResult = None
    results = None

    def __init__(self, newSettings):
        self.settings = newSettings
    
    def sendAPIToken():
        pass
    
    def sendRequest(self, gridWidth, gridHeight, grid):
        import cuquantum
        from cuquantum import CircuitToEinsum

        # Get results, store figure, normalize, apply phase scalar map
# Do similar decomposition process
        instructions = getInstructions(grid, gridWidth, gridHeight)
        numQubits = gridHeight

        # Make qiskit circuit
        circuit = QuantumCircuit(numQubits)
        circuit = makeCircuit(circuit, instructions)    
                        
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
            self.result = results
        else:
            print("Performing Selective Tensor Network Contraction")
            results = []
            for bitstring in self.settings.bitstringsSample:
                expression, operands = myconverter.amplitude(bitstring)
                amplitude = contract(expression, *operands)
                probability = abs(amplitude) ** 2
                results.append([bitstring, probability, np.angle(amplitude)])
            self.result = results
            print("Finished sampling desired subset of distribution...")
        xVal = []
        yVal = []
        norm = mpl.colors.Normalize(vmin=0, vmax=np.pi)
        cmap = cm.hsv
        m = cm.ScalarMappable(norm=norm, cmap=cmap)
        # Normalize to 100% (show percentages, not decimals)
        for entry in results:
            xVal.append(entry[0][::-1])
            if(hasCupy):
                yVal.append(entry[1].get()*100)
            else:
                yVal.append(entry[1]*100)
        if(hasCupy):
            phases = [m.to_rgba(tnp.angle(results[j][2].get() * 1j)) for j in range(len(results))]
        else:
            phases = [m.to_rgba(tnp.angle(results[j][2] * 1j)) for j in range(len(results))]
        # Values are not sorted, do your magic pandas!
        df = pd.DataFrame(
            dict(
                x=xVal,
                y=yVal,
                phase=phases
            )
        )

        df_sorted = df.sort_values('x')
        # Make graph
        plt.bar(df_sorted['x'], df_sorted['y'], width = 0.4, color = df_sorted['phase'])
        plt.xlabel("Computational Result")
        plt.ylabel("Probability")
        # Empirical formula to find rotations
        rotationAmount = math.floor(90/(1 + np.exp(-(((len(xVal))/3)-5))))
        plt.xticks(rotation = rotationAmount)
        cbar = plt.colorbar(m)
        cbar.set_label('Relative Phase of State (Radians)', rotation=-90, labelpad=20)
        plt.title("Probability Distribution of Given Quantum Circuit")
        self.histogramResult = plt
        self.results = results

        plt.clf()

class DWaveBackend:
    provider = "DWave"
    settings = None
    histogramResult = None
    results = None
    API_Token = "NONE"

    def __init__(self, newSettings):
        self.settings = newSettings
    
    def sendAPIToken(self, api_string):
        self.API_Token = api_string
    
    def sendRequest(self):
        import dimod
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
        if(self.API_Token == "NONE"):
            self.API_Token = get_api_key()
        from dwave.system import LeapHybridCQMSampler
        sampler = LeapHybridCQMSampler(token=self.API_Token)     
        sampleset = sampler.sample_cqm(cqm, label='QuboParsing')
        sampleset = sampleset.filter(lambda row: row.is_feasible)
        self.results = sampleset
        # Get resulting energies and save result
        valuesFound = []
        for energy, in sampleset.data(fields=['energy']):
            valuesFound.append(energy)
        plt.hist(valuesFound)
        plt.xlabel("Minimum Energy of Solutions")
        plt.ylabel("Amount of Occurences")
        self.histogramResult = plt

class XanaduBackend:
    provider = "Xandadu"
    settings = None
    histogramResult = None
    results = None
    API_KEY = "NONE"

    def __init__(self, newSettings):
        self.settings = newSettings
    
    def sendAPIToken(self, api_string):
        self.API_KEY = api_string
    
    def sendRequest(self, gridWidth, gridHeight, grid):
        # Similar decomposition, expanded to support photonic multi-gate
        circuitOperators = [[['-', [j]] for j in range(gridHeight)] for i in range(gridWidth)]
        for widthIdx in range(gridWidth):
            for heightIdx in range(gridHeight):
                if(grid[widthIdx][heightIdx].getName() != '-'):
                    if("PP" not in grid[widthIdx][heightIdx].getName() or len(grid[widthIdx][heightIdx].getName()) >= 3):
                        circuitOperators[widthIdx][heightIdx] = [grid[widthIdx][heightIdx].getName(), grid[widthIdx][heightIdx].gate_qubitsInvolved]
                        circuitOperators[widthIdx][heightIdx+1] = [grid[widthIdx][heightIdx].getName(), grid[widthIdx][heightIdx].gate_qubitsInvolved]
                    else:
                        circuitOperators[widthIdx][heightIdx] = [grid[widthIdx][heightIdx].getName(), grid[widthIdx][heightIdx].gate_qubitsInvolved]
        numQubits = gridHeight
        import strawberryfields as sf
        from strawberryfields import ops

        # Initalize program
        circuit = sf.Program(numQubits)
        with circuit.context as q:
            for widthIdx in range(gridWidth):
                for heightIdx in range(gridHeight):
                    # Load up gates
                    if(grid[widthIdx][heightIdx].getName() != '-'):
                        if(grid[widthIdx][heightIdx].getName() == "PD"):
                            ops.Dgate(self.settings.specialGridSettings[(widthIdx, heightIdx)][0], self.settings.specialGridSettings[(widthIdx, heightIdx)][1]) | q[widthIdx]
                        if(grid[widthIdx][heightIdx].getName() == "PX"):
                            ops.Xgate(self.settings.specialGridSettings[(widthIdx, heightIdx)][0]) | q[widthIdx]
                        if(grid[widthIdx][heightIdx].getName() == "PZ"):
                            ops.Zgate(self.settings.specialGridSettings[(widthIdx, heightIdx)][0]) | q[widthIdx]
                        if(grid[widthIdx][heightIdx].getName() == "PS"):
                            ops.Sgate(self.settings.specialGridSettings[(widthIdx, heightIdx)][0]) | q[widthIdx]
                        if(grid[widthIdx][heightIdx].getName() == "PR"):
                            ops.Rgate(self.settings.specialGridSettings[(widthIdx, heightIdx)][0]) | q[widthIdx]
                        if(grid[widthIdx][heightIdx].getName() == "PP"):
                            ops.Pgate(self.settings.specialGridSettings[(widthIdx, heightIdx)][0]) | q[widthIdx]
                        if(grid[widthIdx][heightIdx].getName() == "PV"):
                            ops.Vgate(self.settings.specialGridSettings[(widthIdx, heightIdx)][0]) | q[widthIdx]
                        if(grid[widthIdx][heightIdx].getName() == "PF"):
                            ops.Fouriergate() | q[widthIdx]
                        if(grid[widthIdx][heightIdx].getName() == "PPV"):
                            ops.Vacuum() | q[widthIdx]
                        if(grid[widthIdx][heightIdx].getName() == "PPC"):
                            ops.Coherent(self.settings.specialGridSettings[(widthIdx, heightIdx)][0], self.settings.specialGridSettings[(widthIdx, heightIdx)][1]) | q[widthIdx]
                        if(grid[widthIdx][heightIdx].getName() == "PPF"):
                            ops.Fock(self.settings.specialGridSettings[(widthIdx, heightIdx)][0]) | q[widthIdx]
                        if(grid[widthIdx][heightIdx].getName() == "PBS"):
                            ops.BSgate(self.settings.specialGridSettings[(widthIdx, heightIdx)][0], self.settings.specialGridSettings[(widthIdx, heightIdx)][1]) | (q[widthIdx], q[widthIdx + 1])
                            heightIdx += 1
                        if(grid[widthIdx][heightIdx].getName() == "PMZ"):
                            ops.MZgate(self.settings.specialGridSettings[(widthIdx, heightIdx)][0], self.settings.specialGridSettings[(widthIdx, heightIdx)][1]) | (q[widthIdx], q[widthIdx + 1])
                            heightIdx += 1
                        if(grid[widthIdx][heightIdx].getName() == "PS2"):
                            ops.S2gate(self.settings.specialGridSettings[(widthIdx, heightIdx)][0], self.settings.specialGridSettings[(widthIdx, heightIdx)][1]) | (q[widthIdx], q[widthIdx + 1])
                            heightIdx += 1
                        if(grid[widthIdx][heightIdx].getName() == "PCX"):
                            ops.CXgate(self.settings.specialGridSettings[(widthIdx, heightIdx)][0]) | (q[widthIdx], q[widthIdx + 1])
                            heightIdx += 1
                        if(grid[widthIdx][heightIdx].getName() == "PCZ"):
                            ops.CZgate(self.settings.specialGridSettings[(widthIdx, heightIdx)][0]) | (q[widthIdx], q[widthIdx + 1])
                            heightIdx += 1
                        if(grid[widthIdx][heightIdx].getName() == "PCK"):
                            ops.CKgate(self.settings.specialGridSettings[(widthIdx, heightIdx)][0]) | (q[widthIdx], q[widthIdx + 1])
                            heightIdx += 1
            ops.MeasureFock() | q # Assume fock measurement technique

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
        
        print("Saved values...")
        # Save relevant infromation
        plt.bar(result.keys(), result.values(), 1, color='b')
        plt.xlabel("Fock Measurement State (binary representation for 'qubit' analysis)")
        plt.ylabel("Occurences")
        print("Saving Values...")
        self.histogramResult = plt
        self.results = result

        plt.clf()

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