"""
Quantum-random Levy-style step, direct port of notebook cell 16.
Hadamard-superposes every qubit, measures, maps 0/1 -> -1/+1, scales down.
"""
import numpy as np
from qiskit import QuantumCircuit
from qiskit_aer import AerSimulator

sim = AerSimulator()


def quantum_levy_step(dim: int, scale: float = 0.01) -> np.ndarray:
    qc = QuantumCircuit(dim, dim)
    qc.h(range(dim))
    qc.measure(range(dim), range(dim))
    result = sim.run(qc, shots=1).result()
    bitstring = list(result.get_counts().keys())[0]
    bits = np.array([int(b) for b in bitstring], dtype=float)
    return (bits * 2 - 1) * scale
