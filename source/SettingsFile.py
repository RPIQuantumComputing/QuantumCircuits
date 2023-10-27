# Settings class
class Settings:
    # Basically a structure of relevant simulation information
    backend = "HamiltionSimulation"
    num_qubits = 5
    num_width = 8
    shots = -1
    measurement = False
    gate_error = False
    readout_error = False
    temperature = 0
    optimization = None
    gate_suggestion = False
    incremental_saving = False
    incremental_simulation = False
    objectiveQUBOS = ""
    variableDeclarationsQUBO = []
    constraintsQUBO = []
    bitstringsSample = []
    gateSplit = 0
    cuQuantumConfig = [0,1,2,3]
    specialGridSettings = {(-1, -1): [-1, -1]}

