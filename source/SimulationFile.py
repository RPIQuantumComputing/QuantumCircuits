import SettingsFile
import BackendFile

# Makes a simulation object
class Simulation:
    # Store which backend the user specified
    backend = None
    # Creat a new settings file storing acting simulation settings
    settings = SettingsFile.Settings()

    # Various field elements associated with a simulation
    results = None
    ranBefore = False
    gridWidth = 8
    gridHeight = 5
    grid = None

    # Save the given settings for the simulation
    def __init__(self, newSettings):
        self.settings = newSettings
        self.backend = BackendFile.BackendFactory(self.settings.backend, self.settings)

    # Take the grid information to the Simulation object
    def sendStateInfo(self, newGridWidth, newGridHeight, newGrid):
        self.gridWidth = newGridWidth
        self.gridHeight = newGridHeight
        self.grid = newGrid

    # Runs simulation if results requested or obtains them from prior run
    def get_results(self, rerun=False, show=True):
        if(self.ranBefore == False or rerun == True):
            self.backend.sendRequest(self.gridWidth, self.gridHeight, self.grid)
            if show:
               self.backend.display()
            self.ranBefore = True
        if(self.backend != None):
            return self.backend.results
        return None

    # Runs simulation if results requested or obtains them from prior run
    def get_visualization(self, rerun=False, show=True):
        if(self.ranBefore == False or rerun == True):
            if show:
                self.backend.sendRequest(self.gridWidth, self.gridHeight, self.grid)
            self.ranBefore = True
        if(self.backend != None):
            return self.backend.histogramResult
        return None