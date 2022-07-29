import DesignerFile
import matplotlib.pyplot as plt

designer = DesignerFile.Designer()
designer.setBackend("DWaveSimulation")
designer.addVariable("a = Binary(\"a\")")
designer.addVariable("b = Binary(\"b\")")
designer.addVariable("c = Binary(\"c\")")
designer.addVariable("d = Binary(\"d\")")
designer.addVariable("e = Binary(\"e\")")
designer.setObjective("max ((a + b)*e + (c + d))")
designer.runSimulation()
plt = designer.getVisualization()
plt.show()