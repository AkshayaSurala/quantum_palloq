from dataclasses import dataclass
from itertools import combinations

from qiskit import QuantumCircuit, transpile
from qiskit_aer import AerSimulator


# ============================================================
# CONFIGURATION
# ============================================================

PROCESSOR_QUBITS = 6
SHOTS = 1024

simulator = AerSimulator()


# ============================================================
# QUANTUM JOB
# ============================================================

@dataclass
class QuantumJob:
    job_id: str
    circuit_name: str
    circuit: QuantumCircuit
    qubits_required: int


# ============================================================
# CIRCUIT CREATION
# ============================================================

def create_hadamard_circuit():
    circuit = QuantumCircuit(1, 1)

    circuit.h(0)
    circuit.measure(0, 0)

    return circuit


def create_bell_circuit():
    circuit = QuantumCircuit(2, 2)

    circuit.h(0)
    circuit.cx(0, 1)

    circuit.measure([0, 1], [0, 1])

    return circuit


def create_ghz_circuit():
    circuit = QuantumCircuit(3, 3)

    circuit.h(0)
    circuit.cx(0, 1)
    circuit.cx(1, 2)

    circuit.measure([0, 1, 2], [0, 1, 2])

    return circuit


def create_toffoli_circuit():
    circuit = QuantumCircuit(3, 3)

    circuit.x(0)
    circuit.x(1)

    circuit.ccx(0, 1, 2)

    circuit.measure([0, 1, 2], [0, 1, 2])

    return circuit


# ============================================================
# CREATE JOB QUEUE
# ============================================================

def create_job_queue():

    jobs = [

        QuantumJob(
            job_id="JOB-001",
            circuit_name="Bell State",
            circuit=create_bell_circuit(),
            qubits_required=2
        ),

        QuantumJob(
            job_id="JOB-002",
            circuit_name="GHZ State",
            circuit=create_ghz_circuit(),
            qubits_required=3
        ),

        QuantumJob(
            job_id="JOB-003",
            circuit_name="Hadamard",
            circuit=create_hadamard_circuit(),
            qubits_required=1
        ),

        QuantumJob(
            job_id="JOB-004",
            circuit_name="Toffoli",
            circuit=create_toffoli_circuit(),
            qubits_required=3
        )
    ]

    return jobs


# ============================================================
# DISPLAY JOB QUEUE
# ============================================================

def display_job_queue(jobs):

    print("\n")
    print("=" * 70)
    print("QUANTUM JOB QUEUE")
    print("=" * 70)

    print(
        f"{'JOB ID':<12}"
        f"{'CIRCUIT':<20}"
        f"{'QUBITS':<10}"
    )

    print("-" * 70)

    for job in jobs:

        print(
            f"{job.job_id:<12}"
            f"{job.circuit_name:<20}"
            f"{job.qubits_required:<10}"
        )

    print("-" * 70)

    print(f"Processor capacity: {PROCESSOR_QUBITS} qubits")


# ============================================================
# CIRCUIT COMPOSER
# ============================================================

def find_combinations(jobs):

    valid_combinations = []

    # Try combinations containing 1, 2, 3 ... jobs
    for size in range(1, len(jobs) + 1):

        for combination in combinations(jobs, size):

            total_qubits = sum(
                job.qubits_required
                for job in combination
            )

            if total_qubits <= PROCESSOR_QUBITS:

                valid_combinations.append(
                    (combination, total_qubits)
                )

    return valid_combinations


# ============================================================
# DISPLAY COMBINATIONS
# ============================================================

def display_combinations(valid_combinations):

    print("\n")
    print("=" * 70)
    print("VALID CIRCUIT COMBINATIONS")
    print("=" * 70)

    for number, (combination, total_qubits) in enumerate(
        valid_combinations,
        start=1
    ):

        job_names = [
            job.job_id
            for job in combination
        ]

        circuit_names = [
            job.circuit_name
            for job in combination
        ]

        print(
            f"\nCombination {number}"
        )

        print(
            f"Jobs: {', '.join(job_names)}"
        )

        print(
            f"Circuits: {', '.join(circuit_names)}"
        )

        print(
            f"Total qubits required: "
            f"{total_qubits}/{PROCESSOR_QUBITS}"
        )


# ============================================================
# SELECT BEST COMBINATION
# ============================================================

def select_best_combination(valid_combinations):

    if not valid_combinations:
        return None

    # Select the combination using the largest
    # number of available qubits.
    best = max(
        valid_combinations,
        key=lambda item: item[1]
    )

    return best


# ============================================================
# EXECUTE SELECTED CIRCUITS
# ============================================================

def execute_selected_combination(combination):

    jobs, total_qubits = combination

    print("\n")
    print("=" * 70)
    print("SELECTED CONCURRENT JOB GROUP")
    print("=" * 70)

    print(
        f"Total processor capacity: "
        f"{PROCESSOR_QUBITS} qubits"
    )

    print(
        f"Total qubits required: "
        f"{total_qubits} qubits"
    )

    print("\nSelected jobs:")

    for job in jobs:

        print(
            f"  {job.job_id} → "
            f"{job.circuit_name} → "
            f"{job.qubits_required} qubits"
        )

    print("\nExecuting selected circuits...")

    for job in jobs:

        compiled_circuit = transpile(
            job.circuit,
            simulator
        )

        quantum_job = simulator.run(
            compiled_circuit,
            shots=SHOTS
        )

        result = quantum_job.result()

        counts = result.get_counts()

        print("\n" + "-" * 50)

        print(
            f"{job.job_id} - {job.circuit_name}"
        )

        print(
            f"Measurement results: {counts}"
        )

        print(
            f"Shots: {SHOTS}"
        )


# ============================================================
# MAIN PROGRAM
# ============================================================

def main():

    print("\n")
    print("=" * 70)
    print("PHASE 2 - QUANTUM JOB QUEUE + CIRCUIT COMPOSER")
    print("=" * 70)

    # Create jobs
    jobs = create_job_queue()

    # Display queue
    display_job_queue(jobs)

    # Find valid combinations
    valid_combinations = find_combinations(jobs)

    # Display combinations
    display_combinations(valid_combinations)

    # Select best combination
    best_combination = select_best_combination(
        valid_combinations
    )

    if best_combination is None:

        print("\nNo valid combination found.")

        return

    # Execute selected group
    execute_selected_combination(
        best_combination
    )

    print("\n")
    print("=" * 70)
    print("PHASE 2 COMPLETED")
    print("=" * 70)


# ============================================================
# PROGRAM START
# ============================================================

if __name__ == "__main__":
    main()