from PyQt5 import QtCore, QtGui, QtWidgets
from pyscf import gto, scf
import sys
from typing import Any
import numpy as np

from openfermion.transforms import jordan_wigner
from openfermion.utils import load_operator

from quri_parts.pyscf.mol import get_spin_mo_integrals_from_mole
from quri_parts.chem.mol import ActiveSpace
from quri_parts.openfermion.mol import get_qubit_mapped_hamiltonian
from quri_parts.openfermion.mol import get_fermionic_hamiltonian
from quri_parts.qulacs.estimator import create_qulacs_vector_estimator
from quri_parts.qulacs.estimator import create_qulacs_vector_concurrent_parametric_estimator
from quri_parts.algo.ansatz import HardwareEfficientReal
from quri_parts.algo.optimizer import Adam, OptimizerStatus
from quri_parts.circuit import LinearMappedUnboundParametricQuantumCircuit
from quri_parts.core.estimator import create_parametric_estimator
from quri_parts.core.estimator.gradient import parameter_shift_gradient_estimates
from quri_parts.core.measurement import bitwise_commuting_pauli_measurement
from quri_parts.core.sampling.shots_allocator import (
    create_equipartition_shots_allocator,
)
from quri_parts.core.state import ParametricCircuitQuantumState, ComputationalBasisState
from quri_parts.openfermion.operator import operator_from_openfermion_op

import matplotlib.pyplot as plt

import mendeleev #this is for getting the various properties of elemntents 
from mendeleev import element

#this will be used for the 3d plotting of the molecule
import plotly

import plotly.express as px
import plotly.graph_objects as go

import webbrowser
import os

costs = []
# This is basically QuriPart's competition code with adjustments, will change to my competition code later
# right now, though, I don't want to add a few dependencies and mess up the docker container
def cost_fn(hamiltonian, parametric_state, param_values, estimator):
    estimate = estimator(hamiltonian, parametric_state, [param_values])
    return estimate[0].value.real

def vqe(hamiltonian, parametric_state, estimator, init_params, optimizer):
    opt_state = optimizer.get_init_state(init_params)

    def c_fn(param_values):
        return cost_fn(hamiltonian, parametric_state, param_values, estimator)

    def g_fn(param_values):
        grad = parameter_shift_gradient_estimates(
            hamiltonian, parametric_state, param_values, estimator
        )
        return np.asarray([i.real for i in grad.values])

    while True:
        if(True):
            opt_state = optimizer.step(opt_state, c_fn, g_fn)
            print(f"iteration {opt_state.niter}")
            print(opt_state.cost)
            global costs
            costs.append(opt_state.cost)

        if opt_state.status == OptimizerStatus.FAILED:
            print("Optimizer failed")
            break
        if opt_state.status == OptimizerStatus.CONVERGED:
            print("Optimizer converged")
            break
    return opt_state


class RunAlgorithm:
    def __init__(self) -> None:
        pass

    def result_for_evaluation(self) -> tuple[Any, float]:
        energy_final = self.get_result()
        return energy_final

    def get_result(self, ham, electrons, orbitals) -> Any:
        import openfermion
        n_qubits = max(electrons, orbitals)*2
        hamiltonian = ham

        # make hf + HEreal ansatz
        hf_circuit = LinearMappedUnboundParametricQuantumCircuit(n_qubits)
        hw_ansatz = HardwareEfficientReal(qubit_count=n_qubits, reps=4)
        hf_circuit.extend(hw_ansatz)

        parametric_state = ParametricCircuitQuantumState(n_qubits, hf_circuit)

        sampling_estimator = create_qulacs_vector_concurrent_parametric_estimator()
        adam_optimizer = Adam(ftol=10e-5)

        init_param = np.random.rand(hw_ansatz.parameter_count) * 2 * np.pi * 0.001

        result = vqe(
            hamiltonian,
            parametric_state,
            sampling_estimator,
            init_param,
            adam_optimizer,
        )
        print(f"iteration used: {result.niter}")
        return result.cost

# The simulation method heavily uses https://quri-parts.qunasys.com/tutorials/quantum_chemistry/mo_eint_and_hamiltonial's
# Example code
class Ui_QuantumSimulationGUI(object):
    user_mol = None
    user_mo_coeff=None
    active_space = None
    active_space_mo_eint_set = None

    def setupUi(self, QuantumSimulationGUI):
        QuantumSimulationGUI.setObjectName("QuantumSimulationGUI")
        self.centralwidget = QtWidgets.QWidget(QuantumSimulationGUI)

        # Left side layout
        left_layout = QtWidgets.QVBoxLayout()

        self.textEdit = QtWidgets.QTextEdit()
        left_layout.addWidget(self.textEdit)
        self.textEdit.setHtml(QtCore.QCoreApplication.translate(
            "QuantumSimulationGUI", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
            "<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
            "p, li { white-space: pre-wrap; }\n"
            "</style></head><body style=\" font-family:\'MS Shell Dlg 2\'; font-size:8.1pt; font-weight:400; font-style:normal;\">\n"
            "<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">\'\'\'</p>\n"
            "<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">H (0,0,0)</p>\n"
            "<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">O (2,0,1)</p>\n"
            "<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">H (0,0,2)</p>\n"
            "<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">\'\'\'</p></body></html>"))

        self.pushButton = QtWidgets.QPushButton("Compute Electronic Integrals")
        self.pushButton.clicked.connect(self.on_compute_integrals_clicked)
        left_layout.addWidget(self.pushButton)


        self.label_3 = QtWidgets.QLabel("Step 2: Specify the number of orbitals and electrons")
        left_layout.addWidget(self.label_3)

        self.spinBox = QtWidgets.QSpinBox()
        left_layout.addWidget(self.spinBox)

        self.spinBox_2 = QtWidgets.QSpinBox()
        left_layout.addWidget(self.spinBox_2)

        # Right side layout
        right_layout = QtWidgets.QVBoxLayout()

        # Label for the ComboBox
        self.mappingLabel = QtWidgets.QLabel("Select Mapping:")
        self.mappingLabel.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        right_layout.addWidget(self.mappingLabel)

        # ComboBox for mapping selection
        self.mappingComboBox = QtWidgets.QComboBox()
        self.mappingComboBox.addItem("Jordan-Wigner")
        self.mappingComboBox.addItem("Bravyi-Kitaev")
        self.mappingComboBox.addItem("Symmetric Bravyi-Kitaev")
        self.mappingComboBox.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        right_layout.addWidget(self.mappingComboBox)

        self.Simulate = QtWidgets.QPushButton("Simulate")
        right_layout.addWidget(self.Simulate)
        self.Simulate.clicked.connect(self.on_simulate_clicked)

        # Combine left and right layouts
        main_layout = QtWidgets.QHBoxLayout()
        main_layout.addLayout(left_layout)
        main_layout.addLayout(right_layout)

        self.centralwidget.setLayout(main_layout)
        QuantumSimulationGUI.setCentralWidget(self.centralwidget)

        self.menubar = QtWidgets.QMenuBar(QuantumSimulationGUI)
        QuantumSimulationGUI.setMenuBar(self.menubar)

        self.statusbar = QtWidgets.QStatusBar(QuantumSimulationGUI)
        QuantumSimulationGUI.setStatusBar(self.statusbar)

        self.retranslateUi(QuantumSimulationGUI)
        QtCore.QMetaObject.connectSlotsByName(QuantumSimulationGUI)

    def retranslateUi(self, QuantumSimulationGUI):
        _translate = QtCore.QCoreApplication.translate
        QuantumSimulationGUI.setWindowTitle(_translate("QuantumSimulationGUI", "MainWindow"))

    def draw_spheres(self, sphere_params):
        sphere_data = []  # List to hold the Surface objects for each sphere
        max_radius = max([params['radius'] for params in sphere_params])  # Determine the max radius for setting axis limits
    
        for params in sphere_params:
        	# Unpack sphere parameters
            x, y, z, radius = params['x'], params['y'], params['z'], params['radius']
        
        	# Create the theta and phi angles for the parametric plot
            phi, theta = np.mgrid[0.0:np.pi:100j, 0.0:2.0*np.pi:50j]
        
        	# Parametric equations for the sphere
            x_sphere = x + radius * np.sin(phi) * np.cos(theta)
            y_sphere = y + radius * np.sin(phi) * np.sin(theta)
            z_sphere = z + radius * np.cos(phi)
        
        	# Create the Surface object for the sphere and append to sphere_data list
            sphere = go.Surface(x=x_sphere, y=y_sphere, z=z_sphere, colorscale='Viridis', showscale=False, title=params['name'])
            sphere_data.append(sphere)
    
        # Define the layout for the plot, including title and axis properties
        layout = go.Layout(
            title="Molecule",
            scene=dict(
                xaxis=dict(nticks=4, range=[-max_radius-5, max_radius+5]),
                yaxis=dict(nticks=4, range=[-max_radius-5, max_radius+5]),
                zaxis=dict(nticks=4, range=[-max_radius-5, max_radius+5]),
                aspectratio=dict(x=1, y=1, z=1)
            )
        )
        # Create and show the figure with the aggregated sphere_data
        fig = go.Figure(data=sphere_data, layout=layout)
        fig.write_html('example_figure.html', auto_open=True)
        filename = 'file:///'+os.getcwd()+'/' + 'example_figure.html'
        webbrowser.open_new_tab(filename)
        try:
           os.system("google-chrome -url ./example_figure.html --no-sandbox")
        except:
           pass

    def generate3dMolecule(self, molecule):
        data = []

        max_radius = 0.0
        for atom in molecule:
            #seperate into element and position
            symbol = atom[0]
            si = element(symbol)
            r = si.atomic_radius
            if(r > max_radius):
                max_radius = r

        for atom in molecule:
            #seperate into element and position
            symbol = atom[0]
            pos = atom[1]

            #find the atomic radius of the element
            si = element(symbol)
            
            r = si.atomic_radius / max_radius

            x, y, z = pos

            entry = dict()
            entry['x'] = x
            entry['y'] = y
            entry['z'] = z
            entry['radius'] = r
            entry['name'] = symbol
            data.append(entry)

        self.draw_spheres(data)
        
    def on_compute_integrals_clicked(self):
        elements = []
        deliniators = [",", "(", ")", " "]
        try:
            user_input = self.textEdit.toPlainText()
            lines = user_input.split("\n")
            for line in lines:
               splited = line.split(" ")
               element, position = splited[0], [int(element) for element in list(splited[1]) if element not in deliniators]
               elements.append([element, position])

            #make a 3d model of the molecule
            self.generate3dMolecule(elements)
            # Guassian-Type Molecule, M defines a molecule object
            self.user_mol = gto.M(atom=elements, verbose=0)
            # This will run a self-consistent field (iterative electronic structure until stabalization is found)
            # This is using restricted Hatree-Fock, molecular orbitrals occupied by 2 electrons with a pairing constraint (i.e. stable molecules)
            mol_mf = scf.RHF(self.user_mol).run()
            # Get the coefficients describing the molecular orbital function
            # Thi implicitly gives a superposition of the atomic orbitals
            self.user_mo_coeff = mol_mf.mo_coeff
            # Now, we need to compute the electron integrals
            self.full_space, self.mo_eint_set = get_spin_mo_integrals_from_mole(self.user_mol, self.user_mo_coeff)
        except:
            print("Error: Material is not physically stable!")
    def on_simulate_clicked(self):
        try:
            # Compute the Active Space
            self.number_of_orbitals = int(self.spinBox.value())
            self.number_of_electrons = int(self.spinBox_2.value())
            self.active_space, self.active_space_mo_eint_set = get_spin_mo_integrals_from_mole(
                self.user_mol,
                self.user_mo_coeff,
                ActiveSpace(self.number_of_electrons, self.number_of_orbitals)
            )
            # Implicitly, the active space is cutting down the ansatz to only consider a smaller problem space
            # Consider the active molecular problem and then the reduced one
            active_space_jw_hamiltonian, active_space_operator_mapper, active_space_state_mapper = get_qubit_mapped_hamiltonian(
                self.active_space, self.active_space_mo_eint_set
            )
            # Let us perform the simulation!
            algo_run = RunAlgorithm()
            print("Final Energy Estimate: ", algo_run.get_result(active_space_jw_hamiltonian, self.number_of_electrons, self.number_of_orbitals))
            global costs
            plt.plot(costs)
            plt.xlabel("Iteration of VQE")
            plt.ylabel("Energy Evaluation (eV)")
            plt.show()
        except:
            print("Error: Invalid Electron/Orbital Configuration or Structure!")

if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    QuantumSimulationGUI = QtWidgets.QMainWindow()
    ui = Ui_QuantumSimulationGUI()
    ui.setupUi(QuantumSimulationGUI)
    QuantumSimulationGUI.show()
    sys.exit(app.exec_())
