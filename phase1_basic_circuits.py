from qiskit import QuantumCircuit, transpile
from qiskit_aer import AerSimulator


# Create quantum simulator
simulator = AerSimulator()

SHOTS = 1024


# ---------------------------------------------------------
# 1. X GATE CIRCUIT
# ---------------------------------------------------------
def create_x_circuit():
    circuit = QuantumCircuit(1, 1)

    circuit.x(0)
    circuit.measure(0, 0)

    return circuit


# ---------------------------------------------------------
# 2. HADAMARD CIRCUIT
# ---------------------------------------------------------
def create_hadamard_circuit():
    circuit = QuantumCircuit(1, 1)

    circuit.h(0)
    circuit.measure(0, 0)

    return circuit


# ---------------------------------------------------------
# 3. BELL STATE CIRCUIT
# ---------------------------------------------------------
def create_bell_circuit():
    circuit = QuantumCircuit(2, 2)

    circuit.h(0)
    circuit.cx(0, 1)

    circuit.measure([0, 1], [0, 1])

    return circuit


# ---------------------------------------------------------
# 4. GHZ STATE CIRCUIT
# ---------------------------------------------------------
def create_ghz_circuit():
    circuit = QuantumCircuit(3, 3)

    circuit.h(0)
    circuit.cx(0, 1)
    circuit.cx(1, 2)

    circuit.measure([0, 1, 2], [0, 1, 2])

    return circuit


# ---------------------------------------------------------
# 5. TOFFOLI CIRCUIT
# ---------------------------------------------------------
def create_toffoli_circuit():
    circuit = QuantumCircuit(3, 3)

    circuit.x(0)
    circuit.x(1)

    circuit.ccx(0, 1, 2)

    circuit.measure([0, 1, 2], [0, 1, 2])

    return circuit


# ---------------------------------------------------------
# RUN A CIRCUIT
# ---------------------------------------------------------
def run_circuit(name, circuit):

    print("\n" + "=" * 60)
    print(f"CIRCUIT: {name}")
    print("=" * 60)

    print("\nQuantum Circuit:")
    print(circuit)

    # Convert circuit into simulator-compatible form
    compiled_circuit = transpile(circuit, simulator)

    # Execute
    job = simulator.run(
        compiled_circuit,
        shots=SHOTS
    )

    result = job.result()

    counts = result.get_counts()

    print("\nMeasurement Results:")
    print(counts)

    print(f"\nTotal Shots: {SHOTS}")


# ---------------------------------------------------------
# MAIN PROGRAM
# ---------------------------------------------------------
def main():

    circuits = {
        "X Gate": create_x_circuit(),
        "Hadamard": create_hadamard_circuit(),
        "Bell State": create_bell_circuit(),
        "GHZ State": create_ghz_circuit(),
        "Toffoli": create_toffoli_circuit()
    }

    print("\n")
    print("=" * 60)
    print("QUANTUM CIRCUIT ENGINE - PHASE 1")
    print("=" * 60)

    print("\nAvailable Quantum Circuits:")

    for number, name in enumerate(circuits.keys(), start=1):
        print(f"{number}. {name}")

    # Run every circuit
    for name, circuit in circuits.items():
        run_circuit(name, circuit)

    print("\n")
    print("=" * 60)
    print("PHASE 1 COMPLETED")
    print("=" * 60)


if __name__ == "__main__":
    main()