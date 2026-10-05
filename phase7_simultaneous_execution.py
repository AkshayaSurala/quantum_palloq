from qiskit import QuantumCircuit, transpile
from qiskit_aer import AerSimulator
import time


# ============================================================
# PHASE 7 - SIMULTANEOUS QUANTUM CIRCUIT EXECUTION
# ============================================================

SHOTS = 1024


# ============================================================
# CREATE CIRCUIT A - BELL STATE
# ============================================================

def create_bell_circuit():

    circuit = QuantumCircuit(2, 2)

    circuit.h(0)
    circuit.cx(0, 1)

    circuit.measure([0, 1], [0, 1])

    return circuit


# ============================================================
# CREATE CIRCUIT B - GHZ STATE
# ============================================================

def create_ghz_circuit():

    circuit = QuantumCircuit(3, 3)

    circuit.h(0)
    circuit.cx(0, 1)
    circuit.cx(1, 2)

    circuit.measure(
        [0, 1, 2],
        [0, 1, 2]
    )

    return circuit


# ============================================================
# CREATE COMBINED CIRCUIT
# ============================================================

def create_combined_circuit():

    # --------------------------------------------------------
    # Circuit A uses physical qubits Q3 and Q4
    # --------------------------------------------------------

    circuit_a = create_bell_circuit()

    # --------------------------------------------------------
    # Circuit B uses physical qubits Q0, Q1 and Q2
    # --------------------------------------------------------

    circuit_b = create_ghz_circuit()

    # --------------------------------------------------------
    # Total:
    # Circuit A = 2 qubits
    # Circuit B = 3 qubits
    # Total = 5 physical qubits
    # --------------------------------------------------------

    combined = QuantumCircuit(
        5,
        5
    )

    # ========================================================
    # CIRCUIT A
    # Logical q0 -> Physical Q3
    # Logical q1 -> Physical Q4
    # ========================================================

    combined.h(3)

    combined.cx(
        3,
        4
    )

    # ========================================================
    # CIRCUIT B
    # Logical q0 -> Physical Q0
    # Logical q1 -> Physical Q1
    # Logical q2 -> Physical Q2
    # ========================================================

    combined.h(0)

    combined.cx(
        0,
        1
    )

    combined.cx(
        1,
        2
    )

    # ========================================================
    # MEASURE CIRCUIT A
    # ========================================================

    combined.measure(
        3,
        3
    )

    combined.measure(
        4,
        4
    )

    # ========================================================
    # MEASURE CIRCUIT B
    # ========================================================

    combined.measure(
        0,
        0
    )

    combined.measure(
        1,
        1
    )

    combined.measure(
        2,
        2
    )

    return combined


# ============================================================
# RUN CIRCUIT
# ============================================================

def execute_circuit(
    circuit,
    simulator
):

    start_time = time.perf_counter()

    transpiled_circuit = transpile(
        circuit,
        simulator
    )

    job = simulator.run(
        transpiled_circuit,
        shots=SHOTS
    )

    result = job.result()

    counts = result.get_counts()

    end_time = time.perf_counter()

    execution_time = (
        end_time - start_time
    )

    return counts, execution_time


# ============================================================
# SEPARATE CIRCUIT EXECUTION
# ============================================================

def execute_separately():

    simulator = AerSimulator()

    circuit_a = create_bell_circuit()

    circuit_b = create_ghz_circuit()

    # --------------------------------------------------------
    # Circuit A
    # --------------------------------------------------------

    start_time = time.perf_counter()

    transpiled_a = transpile(
        circuit_a,
        simulator
    )

    job_a = simulator.run(
        transpiled_a,
        shots=SHOTS
    )

    result_a = job_a.result()

    counts_a = result_a.get_counts()

    # --------------------------------------------------------
    # Circuit B
    # --------------------------------------------------------

    transpiled_b = transpile(
        circuit_b,
        simulator
    )

    job_b = simulator.run(
        transpiled_b,
        shots=SHOTS
    )

    result_b = job_b.result()

    counts_b = result_b.get_counts()

    end_time = time.perf_counter()

    total_time = (
        end_time - start_time
    )

    return (
        counts_a,
        counts_b,
        total_time
    )


# ============================================================
# ANALYZE BELL RESULTS
# ============================================================

def calculate_bell_success_rate(
    counts
):

    successful = 0

    for state, count in counts.items():

        # Bell state should produce 00 or 11.
        #
        # Because the combined circuit uses physical
        # qubits Q3 and Q4, their classical results
        # appear in the corresponding positions.

        if state[0:2] in ["00", "11"]:

            successful += count

    return (
        successful / SHOTS
    ) * 100


# ============================================================
# ANALYZE GHZ RESULTS
# ============================================================

def calculate_ghz_success_rate(
    counts
):

    successful = 0

    for state, count in counts.items():

        # GHZ state should produce either
        # 000 or 111 on its three qubits.

        if state[0:3] in ["000", "111"]:

            successful += count

    return (
        successful / SHOTS
    ) * 100


# ============================================================
# DISPLAY COMBINED CIRCUIT
# ============================================================

def display_combined_circuit(
    circuit
):

    print("\n")
    print("=" * 75)
    print("COMBINED QUANTUM CIRCUIT")
    print("=" * 75)

    print()

    print(circuit.draw())


# ============================================================
# MAIN PROGRAM
# ============================================================

def main():

    print("\n")
    print("=" * 75)
    print("PHASE 7 - SIMULTANEOUS QUANTUM CIRCUIT EXECUTION")
    print("=" * 75)

    print("\nExecution configuration:")

    print(
        f"  Shots per execution: {SHOTS}"
    )

    print(
        "  Circuit A: Bell State"
    )

    print(
        "  Circuit B: GHZ State"
    )

    print(
        "  Circuit A physical qubits: Q3, Q4"
    )

    print(
        "  Circuit B physical qubits: Q0, Q1, Q2"
    )

    print(
        "  Reserved buffer: None in this execution test"
    )

    print(
        "\nNote:"
    )

    print(
        "The circuits are placed on separate physical"
    )

    print(
        "qubit regions and executed as one combined"
    )

    print(
        "quantum workload using the Aer simulator."
    )

    # ========================================================
    # CREATE COMBINED CIRCUIT
    # ========================================================

    combined_circuit = create_combined_circuit()

    display_combined_circuit(
        combined_circuit
    )

    # ========================================================
    # SIMULTANEOUS / COMBINED EXECUTION
    # ========================================================

    print("\n")
    print("=" * 75)
    print("COMBINED EXECUTION")
    print("=" * 75)

    simulator = AerSimulator()

    combined_counts, combined_time = (
        execute_circuit(
            combined_circuit,
            simulator
        )
    )

    print(
        "\nCombined execution completed."
    )

    print(
        f"Execution time: "
        f"{combined_time:.6f} seconds"
    )

    print(
        f"Total measurement results: "
        f"{sum(combined_counts.values())}"
    )

    print(
        "\nCombined measurement states:"
    )

    for state, count in sorted(
        combined_counts.items()
    ):

        print(
            f"  {state}: {count}"
        )

    # ========================================================
    # SEPARATE EXECUTION
    # ========================================================

    print("\n")
    print("=" * 75)
    print("SEPARATE CIRCUIT EXECUTION")
    print("=" * 75)

    (
        counts_a,
        counts_b,
        separate_time
    ) = execute_separately()

    print(
        "\nCircuit A - Bell State:"
    )

    for state, count in sorted(
        counts_a.items()
    ):

        print(
            f"  {state}: {count}"
        )

    print(
        "\nCircuit B - GHZ State:"
    )

    for state, count in sorted(
        counts_b.items()
    ):

        print(
            f"  {state}: {count}"
        )

    print(
        f"\nSeparate execution time: "
        f"{separate_time:.6f} seconds"
    )

    # ========================================================
    # PST
    # ========================================================

    # For this noiseless Aer simulation,
    # Bell and GHZ results should ideally have
    # very high success rates.

    bell_pst = calculate_bell_success_rate(
        counts_a
    )

    ghz_pst = calculate_ghz_success_rate(
        counts_b
    )

    average_pst = (
        bell_pst + ghz_pst
    ) / 2

    print("\n")
    print("=" * 75)
    print("CIRCUIT SUCCESS ANALYSIS")
    print("=" * 75)

    print(
        f"\nBell State PST: "
        f"{bell_pst:.2f}%"
    )

    print(
        f"GHZ State PST: "
        f"{ghz_pst:.2f}%"
    )

    print(
        f"Average PST: "
        f"{average_pst:.2f}%"
    )

    # ========================================================
    # TIME COMPARISON
    # ========================================================

    print("\n")
    print("=" * 75)
    print("EXECUTION TIME COMPARISON")
    print("=" * 75)

    print(
        f"\nCombined execution: "
        f"{combined_time:.6f} seconds"
    )

    print(
        f"Separate execution: "
        f"{separate_time:.6f} seconds"
    )

    if separate_time > 0:

        time_difference = (
            separate_time
            - combined_time
        )

        print(
            f"\nTime difference: "
            f"{time_difference:.6f} seconds"
        )

    # ========================================================
    # HARDWARE USAGE
    # ========================================================

    total_physical_qubits = 6

    circuit_qubits = 5

    hardware_usage = (
        circuit_qubits
        / total_physical_qubits
    ) * 100

    print("\n")
    print("=" * 75)
    print("HARDWARE UTILIZATION")
    print("=" * 75)

    print(
        f"\nPhysical processor qubits: "
        f"{total_physical_qubits}"
    )

    print(
        f"Circuit qubits used: "
        f"{circuit_qubits}"
    )

    print(
        f"Hardware utilization: "
        f"{hardware_usage:.2f}%"
    )

    # ========================================================
    # FINAL OBSERVATION
    # ========================================================

    print("\n")
    print("=" * 75)
    print("OBSERVATION")
    print("=" * 75)

    print(
        "\nCircuit A and Circuit B are represented"
    )

    print(
        "inside one combined quantum workload."
    )

    print(
        "\nThe circuits use separate physical"
    )

    print(
        "qubit regions of the simulated processor."
    )

    print(
        "\nThis demonstrates the basic software"
    )

    print(
        "model for concurrent quantum circuit"
    )

    print(
        "execution."
    )

    print(
        "\nThe simulator is currently noiseless."
    )

    print(
        "Crosstalk and other noise effects will"
    )

    print(
        "be incorporated into later experiments."
    )

    # ========================================================
    # COMPLETED
    # ========================================================

    print("\n")
    print("=" * 75)
    print("PHASE 7 COMPLETED")
    print("=" * 75)


if __name__ == "__main__":
    main()