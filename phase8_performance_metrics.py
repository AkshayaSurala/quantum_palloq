from qiskit import QuantumCircuit, transpile
from qiskit_aer import AerSimulator
import time


# ============================================================
# PHASE 8 - PERFORMANCE METRICS
# ============================================================

SHOTS = 1024

TOTAL_PHYSICAL_QUBITS = 6


# ============================================================
# CREATE BELL STATE
# ============================================================

def create_bell_circuit():

    circuit = QuantumCircuit(2, 2)

    circuit.h(0)
    circuit.cx(0, 1)

    circuit.measure(
        [0, 1],
        [0, 1]
    )

    return circuit


# ============================================================
# CREATE GHZ STATE
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

    circuit = QuantumCircuit(
        5,
        5
    )

    # --------------------------------------------------------
    # Circuit B - GHZ
    # Physical qubits Q0, Q1, Q2
    # --------------------------------------------------------

    circuit.h(0)

    circuit.cx(
        0,
        1
    )

    circuit.cx(
        1,
        2
    )

    # --------------------------------------------------------
    # Circuit A - Bell
    # Physical qubits Q3, Q4
    # --------------------------------------------------------

    circuit.h(3)

    circuit.cx(
        3,
        4
    )

    # --------------------------------------------------------
    # Measurements
    # --------------------------------------------------------

    circuit.measure(
        0,
        0
    )

    circuit.measure(
        1,
        1
    )

    circuit.measure(
        2,
        2
    )

    circuit.measure(
        3,
        3
    )

    circuit.measure(
        4,
        4
    )

    return circuit


# ============================================================
# RUN COMBINED EXECUTION
# ============================================================

def run_combined_execution():

    simulator = AerSimulator()

    circuit = create_combined_circuit()

    start_time = time.perf_counter()

    transpiled = transpile(
        circuit,
        simulator
    )

    job = simulator.run(
        transpiled,
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
# RUN SEPARATE EXECUTION
# ============================================================

def run_separate_execution():

    simulator = AerSimulator()

    bell = create_bell_circuit()

    ghz = create_ghz_circuit()

    start_time = time.perf_counter()

    # --------------------------------------------------------
    # Bell
    # --------------------------------------------------------

    bell_transpiled = transpile(
        bell,
        simulator
    )

    bell_job = simulator.run(
        bell_transpiled,
        shots=SHOTS
    )

    bell_result = bell_job.result()

    bell_counts = bell_result.get_counts()

    # --------------------------------------------------------
    # GHZ
    # --------------------------------------------------------

    ghz_transpiled = transpile(
        ghz,
        simulator
    )

    ghz_job = simulator.run(
        ghz_transpiled,
        shots=SHOTS
    )

    ghz_result = ghz_job.result()

    ghz_counts = ghz_result.get_counts()

    end_time = time.perf_counter()

    execution_time = (
        end_time - start_time
    )

    return (
        bell_counts,
        ghz_counts,
        execution_time
    )


# ============================================================
# CALCULATE PST FROM SEPARATE CIRCUITS
# ============================================================

def calculate_bell_pst(counts):

    successful_shots = 0

    for state, count in counts.items():

        if state in ["00", "11"]:

            successful_shots += count

    pst = (
        successful_shots
        / SHOTS
    ) * 100

    return pst


def calculate_ghz_pst(counts):

    successful_shots = 0

    for state, count in counts.items():

        if state in ["000", "111"]:

            successful_shots += count

    pst = (
        successful_shots
        / SHOTS
    ) * 100

    return pst


# ============================================================
# CALCULATE PST FROM COMBINED CIRCUIT
# ============================================================

def calculate_combined_pst(counts):

    bell_successful = 0
    ghz_successful = 0

    for state, count in counts.items():

        # Qiskit count strings are displayed
        # from highest classical bit to lowest.
        #
        # Combined circuit:
        #
        # c0,c1,c2 = GHZ
        # c3,c4    = Bell
        #
        # Displayed string:
        #
        # c4 c3 c2 c1 c0

        if len(state) != 5:
            continue

        # Extract Bell bits
        bell_bits = (
            state[0] + state[1]
        )

        # Extract GHZ bits
        ghz_bits = (
            state[2]
            + state[3]
            + state[4]
        )

        if bell_bits in ["00", "11"]:

            bell_successful += count

        if ghz_bits in ["000", "111"]:

            ghz_successful += count

    bell_pst = (
        bell_successful
        / SHOTS
    ) * 100

    ghz_pst = (
        ghz_successful
        / SHOTS
    ) * 100

    average_pst = (
        bell_pst + ghz_pst
    ) / 2

    return (
        bell_pst,
        ghz_pst,
        average_pst
    )


# ============================================================
# CROSSTALK MODEL
# ============================================================

def calculate_crosstalk_metrics():

    # Simulated values from Phase 6.
    #
    # These are project parameters and are NOT
    # measurements from real quantum hardware.

    penalty_without_buffer = 0.020

    penalty_with_buffer = 0.005

    base_reliability = 0.9923

    adjusted_without = (
        base_reliability
        * (1 - penalty_without_buffer)
    )

    adjusted_with = (
        base_reliability
        * (1 - penalty_with_buffer)
    )

    score_without = (
        1 - penalty_without_buffer
    ) * 100

    score_with = (
        1 - penalty_with_buffer
    ) * 100

    return {
        "penalty_without":
            penalty_without_buffer * 100,

        "penalty_with":
            penalty_with_buffer * 100,

        "score_without":
            score_without,

        "score_with":
            score_with,

        "reliability_without":
            adjusted_without * 100,

        "reliability_with":
            adjusted_with * 100
    }


# ============================================================
# HARDWARE UTILIZATION
# ============================================================

def calculate_hardware_utilization():

    circuit_a_qubits = 2

    circuit_b_qubits = 3

    total_used = (
        circuit_a_qubits
        + circuit_b_qubits
    )

    utilization = (
        total_used
        / TOTAL_PHYSICAL_QUBITS
    ) * 100

    return (
        total_used,
        utilization
    )


# ============================================================
# DISPLAY RESULTS
# ============================================================

def display_results():

    print("\n")
    print("=" * 75)
    print("PHASE 8 - PERFORMANCE METRICS")
    print("=" * 75)

    print("\nRunning combined quantum workload...")

    (
        combined_counts,
        combined_time
    ) = run_combined_execution()

    print(
        "Combined execution completed."
    )

    print("\nRunning separate circuits...")

    (
        bell_counts,
        ghz_counts,
        separate_time
    ) = run_separate_execution()

    print(
        "Separate execution completed."
    )

    # ========================================================
    # PST
    # ========================================================

    (
        combined_bell_pst,
        combined_ghz_pst,
        combined_average_pst
    ) = calculate_combined_pst(
        combined_counts
    )

    separate_bell_pst = (
        calculate_bell_pst(
            bell_counts
        )
    )

    separate_ghz_pst = (
        calculate_ghz_pst(
            ghz_counts
        )
    )

    separate_average_pst = (
        separate_bell_pst
        + separate_ghz_pst
    ) / 2

    # ========================================================
    # CROSSTALK
    # ========================================================

    crosstalk = (
        calculate_crosstalk_metrics()
    )

    # ========================================================
    # HARDWARE
    # ========================================================

    (
        used_qubits,
        hardware_utilization
    ) = calculate_hardware_utilization()

    # ========================================================
    # DISPLAY PST
    # ========================================================

    print("\n")
    print("=" * 75)
    print("PST ANALYSIS")
    print("=" * 75)

    print("\nCombined execution:")

    print(
        f"  Bell State PST: "
        f"{combined_bell_pst:.2f}%"
    )

    print(
        f"  GHZ State PST: "
        f"{combined_ghz_pst:.2f}%"
    )

    print(
        f"  Average PST: "
        f"{combined_average_pst:.2f}%"
    )

    print("\nSeparate execution:")

    print(
        f"  Bell State PST: "
        f"{separate_bell_pst:.2f}%"
    )

    print(
        f"  GHZ State PST: "
        f"{separate_ghz_pst:.2f}%"
    )

    print(
        f"  Average PST: "
        f"{separate_average_pst:.2f}%"
    )

    # ========================================================
    # EXECUTION TIME
    # ========================================================

    print("\n")
    print("=" * 75)
    print("EXECUTION TIME ANALYSIS")
    print("=" * 75)

    print(
        f"\nCombined execution time: "
        f"{combined_time:.6f} seconds"
    )

    print(
        f"Separate execution time: "
        f"{separate_time:.6f} seconds"
    )

    time_difference = (
        separate_time
        - combined_time
    )

    print(
        f"Time difference: "
        f"{time_difference:.6f} seconds"
    )

    if separate_time > 0:

        time_reduction = (
            time_difference
            / separate_time
        ) * 100

    else:

        time_reduction = 0

    print(
        f"Relative time difference: "
        f"{time_reduction:.2f}%"
    )

    # ========================================================
    # CROSSTALK
    # ========================================================

    print("\n")
    print("=" * 75)
    print("CROSSTALK ANALYSIS")
    print("=" * 75)

    print("\nWithout physical buffer:")

    print(
        f"  Crosstalk penalty: "
        f"{crosstalk['penalty_without']:.2f}%"
    )

    print(
        f"  Crosstalk score: "
        f"{crosstalk['score_without']:.2f}%"
    )

    print(
        f"  Adjusted reliability: "
        f"{crosstalk['reliability_without']:.2f}%"
    )

    print("\nWith physical buffer:")

    print(
        f"  Crosstalk penalty: "
        f"{crosstalk['penalty_with']:.2f}%"
    )

    print(
        f"  Crosstalk score: "
        f"{crosstalk['score_with']:.2f}%"
    )

    print(
        f"  Adjusted reliability: "
        f"{crosstalk['reliability_with']:.2f}%"
    )

    penalty_reduction = (
        crosstalk["penalty_without"]
        - crosstalk["penalty_with"]
    )

    reliability_improvement = (
        crosstalk["reliability_with"]
        - crosstalk["reliability_without"]
    )

    print(
        f"\nCrosstalk penalty reduction: "
        f"{penalty_reduction:.2f} percentage points"
    )

    print(
        f"Reliability improvement: "
        f"{reliability_improvement:.2f} percentage points"
    )

    # ========================================================
    # HARDWARE UTILIZATION
    # ========================================================

    print("\n")
    print("=" * 75)
    print("HARDWARE UTILIZATION")
    print("=" * 75)

    print(
        f"\nTotal physical qubits: "
        f"{TOTAL_PHYSICAL_QUBITS}"
    )

    print(
        f"Circuit qubits used: "
        f"{used_qubits}"
    )

    print(
        f"Hardware utilization: "
        f"{hardware_utilization:.2f}%"
    )

    # ========================================================
    # FINAL SUMMARY
    # ========================================================

    print("\n")
    print("=" * 75)
    print("FINAL PERFORMANCE SUMMARY")
    print("=" * 75)

    print(
        f"\nAverage PST: "
        f"{combined_average_pst:.2f}%"
    )

    print(
        f"Combined execution time: "
        f"{combined_time:.6f} seconds"
    )

    print(
        f"Separate execution time: "
        f"{separate_time:.6f} seconds"
    )

    print(
        f"Hardware utilization: "
        f"{hardware_utilization:.2f}%"
    )

    print(
        f"Crosstalk penalty without buffer: "
        f"{crosstalk['penalty_without']:.2f}%"
    )

    print(
        f"Crosstalk penalty with buffer: "
        f"{crosstalk['penalty_with']:.2f}%"
    )

    print(
        f"Adjusted reliability without buffer: "
        f"{crosstalk['reliability_without']:.2f}%"
    )

    print(
        f"Adjusted reliability with buffer: "
        f"{crosstalk['reliability_with']:.2f}%"
    )

    # ========================================================
    # IMPORTANT NOTE
    # ========================================================

    print("\n")
    print("=" * 75)
    print("NOTE")
    print("=" * 75)

    print(
        "\nPST values are obtained from the Aer simulator."
    )

    print(
        "The simulator is ideal/noiseless in this phase."
    )

    print(
        "\nCrosstalk penalties and adjusted reliability"
    )

    print(
        "are simulated project values introduced to"
    )

    print(
        "demonstrate the effect of crosstalk."
    )

    print(
        "\nThey are not measurements from real quantum"
    )

    print(
        "hardware."
    )

    print("\n")
    print("=" * 75)
    print("PHASE 8 COMPLETED")
    print("=" * 75)


# ============================================================
# START
# ============================================================

if __name__ == "__main__":

    display_results()