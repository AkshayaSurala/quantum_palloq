from dataclasses import dataclass


# ============================================================
# PHASE 5 - PHYSICAL BUFFER
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


def calculate_circuit_utilization(
    total_qubits,
    circuit_a,
    circuit_b
):

    used_qubits = len(circuit_a) + len(circuit_b)

    return (used_qubits / total_qubits) * 100


def calculate_effective_utilization(
    circuit_a,
    circuit_b,
    buffer_qubits,
    total_qubits
):

    useful_qubits = len(circuit_a) + len(circuit_b)

    available_qubits = total_qubits - len(buffer_qubits)

    if available_qubits == 0:
        return 0

    return (useful_qubits / available_qubits) * 100


def find_buffer_qubits(
    processor,
    circuit_a,
    circuit_b
):

    candidates = []

    used_qubits = set(circuit_a + circuit_b)

    for qubit in range(processor.num_qubits):

        if qubit in used_qubits:
            continue

        neighbors = get_neighbors(processor, qubit)

        connected_to_a = any(
            neighbor in circuit_a
            for neighbor in neighbors
        )

        connected_to_b = any(
            neighbor in circuit_b
            for neighbor in neighbors
        )

        if connected_to_a or connected_to_b:
            candidates.append(qubit)

    return candidates


def check_buffer_validity(
    processor,
    circuit_a,
    circuit_b,
    buffer_qubits
):

    if not buffer_qubits:
        return False

    used_qubits = set(circuit_a + circuit_b)

    # Buffer must not be part of either circuit
    for buffer in buffer_qubits:

        if buffer in used_qubits:
            return False

    # Check that the buffer is physically adjacent
    # to at least one circuit.
    for buffer in buffer_qubits:

        neighbors = get_neighbors(
            processor,
            buffer
        )

        touches_circuit_a = any(
            neighbor in circuit_a
            for neighbor in neighbors
        )

        touches_circuit_b = any(
            neighbor in circuit_b
            for neighbor in neighbors
        )

        if touches_circuit_a or touches_circuit_b:
            return True

    return False


def display_topology():

    print("\nPhysical topology:")
    print()
    print("Q0 ─── Q1 ─── Q2")
    print("       │")
    print("       Q4")
    print("       │")
    print("Q3 ────┘")
    print("       │")
    print("       Q5")


def display_allocation(
    title,
    circuit_a,
    circuit_b,
    buffer_qubits,
    processor
):

    print("\n")
    print("=" * 75)
    print(title)
    print("=" * 75)

    print("\nCircuit A:")
    print(
        "  Physical qubits:",
        ", ".join(f"Q{q}" for q in circuit_a)
    )

    print("\nBuffer:")

    if buffer_qubits:

        print(
            "  Reserved qubits:",
            ", ".join(
                f"Q{q}"
                for q in buffer_qubits
            )
        )

    else:

        print("  No physical buffer")

    print("\nCircuit B:")
    print(
        "  Physical qubits:",
        ", ".join(f"Q{q}" for q in circuit_b)
    )

    circuit_qubits = len(circuit_a) + len(circuit_b)

    buffer_count = len(buffer_qubits)

    available_qubits = (
        processor.num_qubits
        - buffer_count
    )

    circuit_utilization = (
        circuit_qubits
        / processor.num_qubits
    ) * 100

    effective_utilization = (
        circuit_qubits
        / available_qubits
    ) * 100

    print("\nHardware information:")

    print(
        f"  Total physical qubits: "
        f"{processor.num_qubits}"
    )

    print(
        f"  Circuit qubits in use: "
        f"{circuit_qubits}"
    )

    print(
        f"  Buffer qubits reserved: "
        f"{buffer_count}"
    )

    print(
        f"  Remaining non-buffer qubits: "
        f"{available_qubits}"
    )

    print(
        f"  Circuit utilization: "
        f"{circuit_utilization:.2f}%"
    )

    print(
        f"  Effective utilization: "
        f"{effective_utilization:.2f}%"
    )

    print("\nBuffer status:")

    if buffer_count == 0:

        print(
            "  No buffer is being used."
        )

    else:

        valid = check_buffer_validity(
            processor,
            circuit_a,
            circuit_b,
            buffer_qubits
        )

        if valid:

            print(
                "  VALID - Reserved physical qubit "
                "is available as a buffer."
            )

        else:

            print(
                "  INVALID - Buffer configuration "
                "needs adjustment."
            )


# ============================================================
# MAIN PROGRAM
# ============================================================

def main():

    processor = QuantumProcessor()

    print("\n")
    print("=" * 75)
    print("PHASE 5 - PHYSICAL BUFFER")
    print("=" * 75)

    print(
        "\nProcessor:",
        processor.name
    )

    print(
        "Available physical qubits:",
        processor.num_qubits
    )

    display_topology()

    # ========================================================
    # CIRCUIT ALLOCATIONS
    # ========================================================

    # Circuit A
    circuit_a = [3, 4]

    # Circuit B
    circuit_b = [0, 1]

    # ========================================================
    # CASE 1 - WITHOUT BUFFER
    # ========================================================

    buffer_without = []

    display_allocation(
        "ALLOCATION 1 - WITHOUT PHYSICAL BUFFER",
        circuit_a,
        circuit_b,
        buffer_without,
        processor
    )

    # ========================================================
    # CASE 2 - WITH BUFFER
    # ========================================================

    # Q2 is unused by either circuit.
    # It is reserved as the physical buffer.
    buffer_with = [2]

    display_allocation(
        "ALLOCATION 2 - WITH PHYSICAL BUFFER",
        circuit_a,
        circuit_b,
        buffer_with,
        processor
    )

    # ========================================================
    # BUFFER CANDIDATES
    # ========================================================

    candidates = find_buffer_qubits(
        processor,
        circuit_a,
        circuit_b
    )

    print("\n")
    print("=" * 75)
    print("AVAILABLE BUFFER CANDIDATES")
    print("=" * 75)

    if candidates:

        print(
            "\nPossible unused buffer qubits:"
        )

        for qubit in candidates:

            print(
                f"  Q{qubit}"
            )

    else:

        print(
            "\nNo suitable buffer candidates found."
        )

    # ========================================================
    # COMPARISON
    # ========================================================

    total_qubits = processor.num_qubits

    circuit_qubits = (
        len(circuit_a)
        + len(circuit_b)
    )

    utilization_without = (
        circuit_qubits
        / total_qubits
    ) * 100

    available_with_buffer = (
        total_qubits
        - len(buffer_with)
    )

    effective_utilization_with = (
        circuit_qubits
        / available_with_buffer
    ) * 100

    print("\n")
    print("=" * 75)
    print("BUFFER COMPARISON")
    print("=" * 75)

    print("\nWITHOUT BUFFER")

    print(
        f"  Circuit qubits: "
        f"{circuit_qubits}"
    )

    print(
        f"  Buffer qubits: "
        f"0"
    )

    print(
        f"  Circuit utilization: "
        f"{utilization_without:.2f}%"
    )

    print("\nWITH BUFFER")

    print(
        f"  Circuit qubits: "
        f"{circuit_qubits}"
    )

    print(
        f"  Buffer qubits: "
        f"{len(buffer_with)}"
    )

    print(
        f"  Remaining non-buffer qubits: "
        f"{available_with_buffer}"
    )

    print(
        f"  Circuit utilization: "
        f"{utilization_without:.2f}%"
    )

    print(
        f"  Effective utilization of "
        f"non-buffer qubits: "
        f"{effective_utilization_with:.2f}%"
    )

    print("\n")
    print("OBSERVATION")

    print(
        "The physical buffer reserves an unused"
    )

    print(
        "physical qubit between circuit allocations."
    )

    print(
        "This reduces the number of physical qubits"
    )

    print(
        "available for other circuit allocations."
    )

    print(
        "The buffer is introduced to provide physical"
    )

    print(
        "separation before applying the crosstalk model."
    )

    # ========================================================
    # FINAL STATUS
    # ========================================================

    print("\n")
    print("=" * 75)
    print("PHASE 5 COMPLETED")
    print("=" * 75)


if __name__ == "__main__":
    main()