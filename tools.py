"""
Defining logical qubit surface codes from 'Entangling logical qubits with lattice surgery'
Code distance is hard coded, not designed to be scalable.
"""

import numpy as np

from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister
from qiskit.opflow import PauliSumOp
code_distance = 2
num_qubits = code_distance*2
num_stabilisers = 3 #number of one-qubit stabilisers

def X_l(l_circ: QuantumCircuit):
    """
    Logical X gate

    l_circ: circuit representing a logical qubit
    """
    l_circ.x(0)
    l_circ.x(1)

def Z_l(l_circ: QuantumCircuit):
    """
    Logical Z gate

    l_circ: circuit representing a logical qubit
    """
    l_circ.z(0)
    l_circ.z(2)

def apply_random_noise(l_circ: QuantumCircuit):
    """
    Apply a random one-qubit noise (Z, X) to a logical qubit circuit
    """
    random_gate = int(np.random.choice(2, 1))
    random_qubit = int(np.random.choice(4,1))

    if random_gate == 0: l_circ.z(random_qubit)
    else: l_circ.x(random_qubit)

def measure_stabiliser(stabiliser, circuit, meas_qubit_id, meas_clbit_id):
    circuit.h(meas_qubit_id)
    #needs to be cast to a list from np array otherwise throws error in .append()
    list_for_gate = list(np.concatenate([[meas_qubit_id], stabiliser.qubit_list]))
    circuit.append(stabiliser.gate(), list_for_gate)
    circuit.h(meas_qubit_id)
    if stabiliser.pauli.lower() == 'z':
        circuit.x(meas_qubit_id)
    circuit.measure(meas_qubit_id, meas_clbit_id)

class Stabiliser():
    def __init__(self, qubit_list, pauli, name):
        self.qubit_list = qubit_list #which qubit it acts on
        #this not very general but the simplest way I could think of
        self.circ = QuantumCircuit(len(self.qubit_list), name = name)
        self.pauli = pauli
        if pauli.lower() == 'x':
            self.circ.x(range(len(self.qubit_list)))
        elif pauli.lower() == 'z':
            self.circ.z(range(len(self.qubit_list)))
        else: 
            raise ValueError('Only support x- and z- like strings in this example!')
    def gate(self):
        gate = self.circ.to_gate()
        c_gate = gate.control()
        return c_gate


class L_qubit():
    """
    Can create circuits representing logical qubits.
    """
    def __init__(self, circ = None, nq = num_qubits , ns = num_stabilisers):
        self.nq = nq
        self.ns = ns
        if circ is None:
            code_qubits = QuantumRegister(nq, 'code_q')
            meas_qubits = QuantumRegister(ns, 'aux_q')
            meas_clbits = ClassicalRegister(ns, 'classical')
            self.lq_circ = QuantumCircuit(code_qubits, meas_qubits, meas_clbits)
            #initialises in logical 0 state
            #NOTE: might not be optimal way of initialising this state
            self.lq_circ.h(3)
            self.lq_circ.cx(3,1)
            self.lq_circ.x(3)
            self.lq_circ.cx(3,0)
            self.lq_circ.cx(3,2)
            self.lq_circ.x(3)
            self.lq_circ.barrier()
        elif isinstance(circ, QuantumCircuit):
            self.lq_circ = circ
            self.lq_circ.barrier()

    def merge(self, other) -> QuantumCircuit:
        """
        Creates a merged, transitional one-qubit logical system which can be split to create entanglement.

        another: instance of L_qubit

        return: instance of L_qubit
        """
        merged_circuit = QuantumCircuit(QuantumRegister(2*(self.nq+self.ns)), ClassicalRegister(2*self.ns))
        #make a circuit containing two logical qubits
        merged_circuit.compose(self.lq_circ, qubits = [k for k in range(self.nq+self.ns)], 
                               clbits = [k for k in range(self.ns)], inplace=True)
        merged_circuit.compose(other.lq_circ, qubits = [k for k in range(self.nq+self.ns, 2*(self.nq+self.ns))], inplace=True)
    

        merged_L_qubit = L_qubit(merged_circuit)
        return merged_L_qubit


