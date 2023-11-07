import random
import matplotlib.pyplot as plt
import numpy as np
import DataDiagram
import ParseCircuit
import TensorContractionGeneration
import networkx as nx

# Import files
from PartialSimulationTab import PartialSimulationTab
from DesignerGUI import GraphicsManager, GateManager, SimulatorSettings, GridManager, EmailManager

class GUIHelper:
    # For field elements that complete change layout
    def forceUpdate():
        from Window import Window
        window = Window()
        window.show()

    def initial(GateM: GateManager, SS: SimulatorSettings, row, col):
        gate_dict = {}
        if (SS.photonicMode):
            gate_dict = {
                (0, 0): "PX",
                (0, 1): "PZ",
                (0, 2): "PS",
                (0, 3): "PS2",
                (1, 0): "PMZ",
                (1, 1): "PCX",
                (1, 2): "PD",
                (1, 3): "PF",
                (2, 0): "PBS",
                (2, 1): "PCK",
                (2, 2): "PPC",
                (2, 3): "PPF",
                (3, 0): "PPV",
                (3, 1): list(GateM.customGates.keys())[0] if len(GateM.customGates) != 0 else " ",
                (3, 2): list(GateM.customGates.keys())[1] if len(GateM.customGates) > 1 else " ",
                (3, 3): list(GateM.customGates.keys())[2] if len(GateM.customGates) > 2 else " ",
            }
        else:
            gate_dict = {
                (0, 0): "H",
                (0, 1): "X",
                (1, 0): "Y",
                (1, 1): "Z",
                (2, 0): "S",
                (2, 1): "T",
                (3, 0): "CNOT",
                (3, 1): list(GateM.customGates.keys())[0] if len(GateM.customGates) != 0 else " ",
                (4, 0): list(GateM.customGates.keys())[1] if len(GateM.customGates) > 1 else " ",
                (4, 1): list(GateM.customGates.keys())[2] if len(GateM.customGates) > 2 else " ",
            }
        return gate_dict.get((row, col), " ")

    # This runs the simulation
    def runSimulation(GraphM: GraphicsManager, GridM: GridManager, SS: SimulatorSettings):
        print("---------------------Running Simulation-------------------------------------")
        # PENDING upon which BACKEND is selected, the control flow is different [might need other GUI settings]
        # run simulation with Dwave ocean
        if (GridM.designer.settings.backend == "DWaveSimulation"):
            # get user's input variables as plain text and split
            # then add each unique line to backend
            print("User Variables added: \n")
            variables = list(set(SS.DWaveVar.strip().split("\n")))

            for variable in variables:
                GridM.designer.addVariable(variable)
                print(variable)

            # get user's input constraint as plain text and split
            # then add each unique line to backend
            print("User constraint added: \n")
            constraints = list(set(SS.DWaveCon.strip().split("\n")))
            for constraint in constraints:
                GridM.designer.addConstraint(constraint)
                print(constraint)

            # get user's input objective
            print(f"Objective set to: \n{SS.DWaveObjective}")
            GridM.designer.setObjective(SS.DWaveObjective)
            GridM.designer.runSimulation()
            plt = GridM.designer.getVisualization()
            plt.show()
        else:
            numDepth, numQubits = GraphM.currentWidth, GraphM.currentHeight
            entry = "-" * 3 *(numDepth+1)

            if (GridM.designer.settings.backend == "HamiltionSimulationCuQuantum"):
                for e in SS.cuQuantumBitStrings.strip().split("\n"):
                    GridM.designer.addBitstring(e)
                GridM.designer.settings.gateSplit = SS.cuQuantumGateSplit
                GridM.designer.settings.cuQuantumConfig = SS.cuQuantumConfig

            # If not qubo optimization, it is a circuit problem, so display it
            print(f"Quantum Circuit Printout: \n{GridM.grid}")
            print(entry)

            starredPositions = {(-1, -1)}
            for qubit in range(numQubits):
                tempStr = ""
                for depth in range(GraphM.offSetHorizontal, numDepth):
                    if ((qubit, depth) in starredPositions):
                        tempStr += "[*]"
                    else:
                        GridM.designer.gateAddition(
                            GridM.grid[qubit][depth], depth-GraphM.offSetHorizontal, qubit)
                        tempStr += "[" + GridM.grid[qubit][depth] + "]"
                    if (len(GridM.grid[qubit][depth]) >= 3 and "PP" not in GridM.grid[qubit][depth]):
                        starredPositions.add((qubit + 1, depth))
                    tempStr += "[M]"
                print(tempStr)

            print(entry)
            print("------------------------BACKEND GOT-------------------------------------")

            # Have the designer confirm the board (for debugging)
            GridM.designer.printDesign()
            GridM.designer.runSimulation()
            plt = GridM.designer.getVisualization()
            plt.show()


    ######## Could make a new file for this ########

    # changes settingfile based on user choice
    def changeSimulationTechniqueHamiltonian(GridM: GridManager):
        GridM.designer.setBackend("HamiltionSimulation")
        print("Changed backend to Hamiltion Simulation")


    def changeSimulationTechniqueHamiltonianCuQuantum(GridM: GridManager, cuQuantumTab: PartialSimulationTab):
        cuQuantumTab.show()
        GridM.designer.setBackend("HamiltionSimulationCuQuantum")
        print("Changed backend to Hamiltion CuQuantum Simulation")


    def changeSimulationTechniqueFeynman(GridM: GridManager):
        GridM.designer.setBackend("FeynmanSimulation")
        print("Changed backend to Feynman Simulation")


    def changeSimulationTechniqueDWave(GridM: GridManager):
        GridM.designer.setBackend("DWaveSimulation")
        print("Changed backend to DWave Ocean")


    def changeSimulationTechniqueIBM(GridM: GridManager):
        GridM.designer.setBackend("IBMSimulation")
        print("Changed backend to IBM Xanadu")


    def changeSimulationTechniqueQiskit(GridM: GridManager):
        GridM.designer.setBackend("Qiskit")
        print("Changed to Qiskit Backend")


    def changeSimulationTechniqueXanadu(GridM: GridManager):
        GridM.designer.setBackend("Photonic")
        print("Changed to Xanadu Photonic Backend")

    # Change Various settings based on click events, self-explanatory
    def changeMeasurement(GridM: GridManager, checked):
        GridM.designer.settings.measurement = checked
        print("Set measurement to " + str(checked))


    def changeSuggestion(GridM: GridManager, checked):
        GridM.designer.settings.gate_suggestion = checked
        GridM.designer.suggestSimplifications(GridM.grid)
        print("Set gate suggestion to " + str(checked))


    def changeIncresav(GridM: GridManager, checked):
        GridM.designer.settings.incremental_saving = checked
        print("Set incremental saving to " + str(checked))


    def changeIncresim(GridM: GridManager, checked):
        GridM.designer.settings.incremental_simulation = checked
        print("Set incremental simulation to " + str(checked))


    def updateNumQubit(GraphM: GraphicsManager, GridM: GridManager,  val):
        GridM.designer.settings.num_qubits = val
        GraphM.currentHeight = val
        print("Set number of qubits to " + str(val))

    # This is a less forceful update that changes whenever the GUI is interacted with
    def updateGrid(GridM: GridManager, SS: SimulatorSettings):
        GridM.grid = GridM.designer.getGUIGrid()
        SS.needToUpdate = True

    # Changes Width of Quantum Circuit
    def updateNumWidth(GraphM: GraphicsManager, GridM: GridManager, val):
        GridM.designer.settings.num_width = val
        GraphM.currentWidth = val
        print("Set width to " + str(val))


    def dataDiagramVisualization(GridM: GridManager, GraphM: GraphicsManager):
        histogram = GridM.designer.getStatistics()
        if (type(histogram) == type(list())):
            histogramNew = dict()
            for entry in histogram:
                histogramNew[entry[0]] = entry[1]
            histogram = histogramNew

        print("Button press for Data Diagram...")

        if (not histogram):
            print("No data stored, please run the simulation before making the data model.")
            return

        sumHistogram = sum(histogram.values())

        # Looks like a possible bug.
        v = np.zeros((1,  GraphM.currentHeight) )

        for entry, value in histogram.items():
            v[0][int(entry, 2)] = value / sumHistogram
        print(v)

        root = DataDiagram.makeDataDiagram(v[0], 0, False)
        G = nx.Graph()
        GUIHelper.createGraph(root, root, G)
        pos = nx.get_node_attributes(G, 'pos')
        nx.draw(G, pos, with_labels=True)
        
        # Currently, the implementation is buggy...to say the least, works with amplitudes, just don't show the user :P
        # labels = nx.get_edge_attributes(G,'weight')
        # nx.draw_networkx_edge_labels(G,pos,edge_labels=labels)
        plt.show()

    def followSelf(root, prior):
        finalValue = prior
        while (True):
            left = root.get_left() and str(root) == str(root.get_left())
            right = root.get_right() and str(root) == str(root.get_right())

            if (not (left or right)):
                break

            if left:
                finalValue = max(root.get_left().get_amplitude(), finalValue)
                root = root.get_left()
            if right:
                finalValue = max(root.get_right().get_amplitude(), finalValue)
                root = root.get_right()
        return finalValue

    def createGraph(root, parent, G, index=0, level=0):
        s = str(root)
        left = root and root.get_left() and s == str(root.get_left())
        right = root and root.get_right() and s == str(root.get_right())
        if (not G.has_node(s)):
            G.add_node(s, pos=(index, -level))

        if (s != "DD"):
            if left:
                G.add_edge(str(parent), s, weight=round(
                    GUIHelper.followSelf(root, root.get_left().get_amplitude()), 2))
            elif right:
                G.add_edge(str(parent), s, weight=round(
                    GUIHelper.followSelf(root, root.get_right().get_amplitude()), 2))
            elif (root and str(parent) != s):
                G.add_edge(str(parent), s, weight=round(root.get_amplitude(), 2))

        if (root):
            print("  " * (2*level), root, "| Amplitude: ", root.get_amplitude())
            if (root.get_left()):
                GUIHelper.createGraph(root.get_left(), root, G, (index), level + 1)
            if (root.get_right()):
                GUIHelper.createGraph(root.get_right(), root, G, (index+1), level + 1)

    def showParseGrid(self):
        tempGrid = [["H", "H", "S", "-", "-"], ["CNOT", "*", "-", "-", "-"], ["-", "CNOT", "*", "-",
                                                                            "-"], ["CNOT", "*", "CCX", "*", "*"], ["CCX", "*", "*", "S", "-"], ["S", "-", "-", "-", "-"]]
        print("---------------------------PARSER IMPLEMENTATION IN PROGRESS-------------------------------------")
        for entry in tempGrid:
            print(entry)
        print("---------------------------------LL(1) PARSER---------------------------------------------")
        ParseCircuit.parse(tempGrid)

    def showTensorNetwork(self):
        gridA = [["H", "H", "S", "-", "-"], ["CNOT", "*", "-", "-", "-"], ["-", "CNOT", "*", "-", "-"],
                ["CNOT", "*", "CCX", "*", "*"], ["CCX", "*", "*", "S", "-"], ["S", "-", "-", "-", "-"]]
        gridB = [["H", "H", "H", "H"], ["CX", "*", "X(1/2)", "T"], ["X(1/2)", "CX", "*", "Y(1/2)"], [
            "T", "X(1/2)", "CX", "*"], ["CX", "-", "-", "*"], ["H", "H", "H", "H"]]
        print("---------------------------PARSER IMPLEMENTATION IN PROGRESS-------------------------------------")
        if (random.random() >= 0.5):
            print("EXAMPLE NETWORK 1: (GRID A)")
            array = np.array(gridA)

            for entry in (array.T).tolist():
                print(entry)
            print("---------------------------------------------------")

            tree = TensorContractionGeneration.parse(gridA)
            layers = TensorContractionGeneration.getComputationLayers(tree)
            G = TensorContractionGeneration.generateTensorNetworkGraph(layers, 5)
            TensorContractionGeneration.drawTensorNetworkGraph(G)
            plt.show()
        else:
            print("EXAMPLE NETWORK 2: (GRID B)")
            array = np.array(gridB)

            for entry in (array.T).tolist():
                print(entry)
            print("---------------------------------------------------")

            tree = TensorContractionGeneration.parse(gridB)
            layers = TensorContractionGeneration.getComputationLayers(tree)
            G = TensorContractionGeneration.generateTensorNetworkGraph(layers, 4)
            TensorContractionGeneration.drawTensorNetworkGraph(G)
            plt.show()