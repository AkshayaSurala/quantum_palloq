from dataclasses import dataclass


# ============================================================
# PHASE 6 - CROSSTALK MODEL
# ============================================================

@dataclass
class Qubit:
    qubit_id: int
    readout_error: float
    single_gate_error: float
    two_gate_error: float

    @property
    def reliability(self):
        average_error = (
            self.readout_error
            + self.single_gate_error
            + self.two_gate_error
        ) / 3

        return 1 - average_error


class QuantumProcessor:

    def __init__(self):

        self.name = "Simulated NISQ Processor"
        self.num_qubits = 6

        # Simulated qubit error information
        self.qubits = [
            Qubit(0, 0.010, 0.001, 0.010),
            Qubit(1, 0.015, 0.002, 0.012),
            Qubit(2, 0.025, 0.003, 0.020),
            Qubit(3, 0.008, 0.001, 0.008),
            Qubit(4, 0.012, 0.002, 0.011),
            Qubit(5, 0.030, 0.004, 0.025)
        ]

        # Physical connectivity
        self.connections = [
            (0, 1),
            (1, 2),
            (1, 4),
            (3, 4),
            (4, 5)
        ]


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def are_connected(processor, q1, q2):

    return (
        (q1, q2) in processor.connections
        or (q2, q1) in processor.connections
    )


def get_neighbors(processor, qubit_id):

    neighbors = []

    for q1, q2 in processor.connections:

        if q1 == qubit_id:
            neighbors.append(q2)

        elif q2 == qubit_id:
            neighbors.append(q1)

    return neighbors


def calculate_distance(
    processor,
    start_qubit,
    target_qubit
):

    if start_qubit == target_qubit:
        return 0

    visited = {start_qubit}
    queue = [(start_qubit, 0)]

    while queue:

        current, distance = queue.pop(0)

        for neighbor in get_neighbors(
            processor,
            current
        ):

            if neighbor == target_qubit:
                return distance + 1

            if neighbor not in visited:

                visited.add(neighbor)

                queue.append(
                    (neighbor, distance + 1)
                )

    return None


def find_minimum_circuit_distance(
    processor,
    circuit_a,
    circuit_b
):

    minimum_distance = None
    closest_pair = None

    for q1 in circuit_a:

        for q2 in circuit_b:

            distance = calculate_distance(
                processor,
                q1,
                q2
            )

            if distance is not None:

                if (
                    minimum_distance is None
                    or distance < minimum_distance
                ):

                    minimum_distance = distance
                    closest_pair = (q1, q2)

    return minimum_distance, closest_pair


# ============================================================
# CROSSTALK MODEL
# ============================================================

def calculate_crosstalk_penalty(
    minimum_distance,
    has_buffer
):

    # These are simulated project parameters.
    #
    # They are NOT hardware calibration values.
    #
    # Smaller physical distance means greater
    # possible crosstalk.
    #
    # A physical buffer reduces the penalty.

    if minimum_distance is None:
        return 0.0

    if has_buffer:

        if minimum_distance <= 1:
            penalty = 0.005

        elif minimum_distance == 2:
            penalty = 0.002

        else:
            penalty = 0.001

    else:

        if minimum_distance == 1:
            penalty = 0.020

        elif minimum_distance == 2:
            penalty = 0.010

        else:
            penalty = 0.005

    return penalty


def calculate_crosstalk_score(
    penalty
):

    # Convert penalty into a simple score.
    #
    # 100% means no additional crosstalk penalty.
    # Lower score means greater simulated impact.

    score = (1 - penalty) * 100

    return score


def calculate_adjusted_reliability(
    base_reliability,
    penalty
):

    adjusted_reliability = (
        base_reliability
        * (1 - penalty)
    )

    return adjusted_reliability


# ============================================================
# DISPLAY FUNCTIONS
# ============================================================

def display_processor(processor):

    print("\n")
    print("=" * 75)
    print("SIMULATED NISQ PROCESSOR")
    print("=" * 75)

    print(
        "\nProcessor:",
        processor.name
    )

    print(
        "Physical qubits:",
        processor.num_qubits
    )

    print("\nPhysical topology:")
    print()
    print("Q0 ─── Q1 ─── Q2")
    print("       │")
    print("       Q4")
    print("       │")
    print("Q3 ────┘")
    print("       │")
    print("       Q5")


def display_case(
    title,
    processor,
    circuit_a,
    circuit_b,
    buffer_qubits
):

    print("\n")
    print("=" * 75)
    print(title)
    print("=" * 75)

    print("\nCircuit A:")
    print(
        "  Physical qubits:",
        ", ".join(
            f"Q{q}"
            for q in circuit_a
        )
    )

    print("\nCircuit B:")
    print(
        "  Physical qubits:",
        ", ".join(
            f"Q{q}"
            for q in circuit_b
        )
    )

    if buffer_qubits:

        print("\nPhysical buffer:")
        print(
            "  Reserved qubits:",
            ", ".join(
                f"Q{q}"
                for q in buffer_qubits
            )
        )

    else:

        print("\nPhysical buffer:")
        print("  None")

    # --------------------------------------------------------
    # Find distance between circuits
    # --------------------------------------------------------

    minimum_distance, closest_pair = (
        find_minimum_circuit_distance(
            processor,
            circuit_a,
            circuit_b
        )
    )

    print("\nCircuit separation:")

    if minimum_distance is not None:

        print(
            f"  Minimum physical distance: "
            f"{minimum_distance}"
        )

        print(
            f"  Closest qubits: "
            f"Q{closest_pair[0]} and "
            f"Q{closest_pair[1]}"
        )

    else:

        print(
            "  Circuits are disconnected."
        )

    # --------------------------------------------------------
    # Calculate crosstalk
    # --------------------------------------------------------

    has_buffer = len(buffer_qubits) > 0

    penalty = calculate_crosstalk_penalty(
        minimum_distance,
        has_buffer
    )

    score = calculate_crosstalk_score(
        penalty
    )

    print("\nCrosstalk analysis:")

    print(
        f"  Crosstalk penalty: "
        f"{penalty * 100:.2f}%"
    )

    print(
        f"  Crosstalk score: "
        f"{score:.2f}%"
    )

    # --------------------------------------------------------
    # Base reliability
    # --------------------------------------------------------

    all_qubits = circuit_a + circuit_b

    reliabilities = []

    for qubit_id in all_qubits:

        qubit = processor.qubits[qubit_id]

        reliabilities.append(
            qubit.reliability
        )

    base_reliability = (
        sum(reliabilities)
        / len(reliabilities)
    )

    adjusted_reliability = (
        calculate_adjusted_reliability(
            base_reliability,
            penalty
        )
    )

    print("\nReliability analysis:")

    print(
        f"  Base reliability: "
        f"{base_reliability * 100:.2f}%"
    )

    print(
        f"  Adjusted reliability: "
        f"{adjusted_reliability * 100:.2f}%"
    )

    return {
        "distance": minimum_distance,
        "penalty": penalty,
        "score": score,
        "base_reliability": base_reliability,
        "adjusted_reliability": adjusted_reliability
    }


# ============================================================
# MAIN PROGRAM
# ============================================================

def main():

    processor = QuantumProcessor()

    display_processor(processor)

    # ========================================================
    # CIRCUIT ALLOCATION
    # ========================================================

    circuit_a = [3, 4]

    circuit_b = [0, 1]

    # ========================================================
    # CASE 1 - WITHOUT BUFFER
    # ========================================================

    result_without = display_case(
        "CASE 1 - EXECUTION WITHOUT BUFFER",
        processor,
        circuit_a,
        circuit_b,
        []
    )

    # ========================================================
    # CASE 2 - WITH BUFFER
    # ========================================================

    buffer_qubits = [2]

    result_with = display_case(
        "CASE 2 - EXECUTION WITH PHYSICAL BUFFER",
        processor,
        circuit_a,
        circuit_b,
        buffer_qubits
    )

    # ========================================================
    # COMPARISON
    # ========================================================

    print("\n")
    print("=" * 75)
    print("CROSSTALK COMPARISON")
    print("=" * 75)

    penalty_without = (
        result_without["penalty"] * 100
    )

    penalty_with = (
        result_with["penalty"] * 100
    )

    score_without = result_without["score"]

    score_with = result_with["score"]

    reliability_without = (
        result_without["adjusted_reliability"]
        * 100
    )

    reliability_with = (
        result_with["adjusted_reliability"]
        * 100
    )

    print("\nWithout physical buffer:")

    print(
        f"  Crosstalk penalty: "
        f"{penalty_without:.2f}%"
    )

    print(
        f"  Crosstalk score: "
        f"{score_without:.2f}%"
    )

    print(
        f"  Adjusted reliability: "
        f"{reliability_without:.2f}%"
    )

    print("\nWith physical buffer:")

    print(
        f"  Crosstalk penalty: "
        f"{penalty_with:.2f}%"
    )

    print(
        f"  Crosstalk score: "
        f"{score_with:.2f}%"
    )

    print(
        f"  Adjusted reliability: "
        f"{reliability_with:.2f}%"
    )

    # --------------------------------------------------------
    # Improvement
    # --------------------------------------------------------

    penalty_reduction = (
        penalty_without - penalty_with
    )

    reliability_improvement = (
        reliability_with
        - reliability_without
    )

    print("\nImprovement from physical buffer:")

    print(
        f"  Crosstalk penalty reduction: "
        f"{penalty_reduction:.2f}%"
    )

    print(
        f"  Reliability improvement: "
        f"{reliability_improvement:.2f} percentage points"
    )

    # ========================================================
    # OBSERVATION
    # ========================================================

    print("\n")
    print("=" * 75)
    print("OBSERVATION")
    print("=" * 75)

    print(
        "\nWhen two circuits are physically close,"
    )

    print(
        "the simulated crosstalk penalty increases."
    )

    print(
        "\nA physical buffer creates additional"
    )

    print(
        "separation between circuit allocations."
    )

    print(
        "\nIn this simplified model, the buffer"
    )

    print(
        "reduces the simulated crosstalk penalty"
    )

    print(
        "and improves the adjusted reliability."
    )

    print(
        "\nThe crosstalk values used here are"
    )

    print(
        "simulated project parameters, not"
    )

    print(
        "measurements from real quantum hardware."
    )

    # ========================================================
    # FINAL STATUS
    # ========================================================

    print("\n")
    print("=" * 75)
    print("PHASE 6 COMPLETED")
    print("=" * 75)


if __name__ == "__main__":
    main()