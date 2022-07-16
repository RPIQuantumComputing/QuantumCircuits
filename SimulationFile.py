import SettingsFile
import BackendFile

class Simulation:
    backend = None
    settings = SettingsFile.Settings()
    results = None
    ranBefore = False
    gridWidth = 8
    gridHeight = 5
    grid = None

    def __init__(self, newSettings):
        self.settings = newSettings
        self.backend = BackendFile.BackendFactory(self.settings.backend)

    def sendStateInfo(self, newGridWidth, newGridHeight, newGrid):
        self.gridWidth = newGridWidth
        self.gridHeight = newGridHeight
        self.grid = newGrid
    
    def get_results(self, rerun=False):
        if(self.ranBefore == False or rerun == True):
            self.backend.sendRequest(self.gridWidth, self.gridHeight, self.grid)
            self.ranBefore = True
        if(self.backend != None):
            return self.backend.results
        return None
    
    def get_visualization(self, rerun=False):
        if(self.ranBefore == False or rerun == True):
            self.backend.sendRequest(self.gridWidth, self.gridHeight, self.grid)
            self.ranBefore = True
        if(self.backend != None):
            return self.backend.histogramResult
        return None