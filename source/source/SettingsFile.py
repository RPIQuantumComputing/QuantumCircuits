# Settings class
class Settings:
    # Basically a structure of relevant simulation information
    backend = "HamiltionSimulation"
    num_qubits = 5
    num_width = 8
    shots = -1
    measurement = False
    noise_model = None
    optimization = None
    gate_suggestion = False
    incremental_saving = False
    incremental_simulation = False
    objectiveQUBOS = ""
    variableDeclarationsQUBO = []
    constraintsQUBO = []
    specialGridSettings = {(-1, -1): [-1, -1]}

