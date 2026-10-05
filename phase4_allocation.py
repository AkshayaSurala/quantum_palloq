from dataclasses import dataclass
from itertools import combinations


# ============================================================
# QUBIT INFORMATION
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


# ============================================================
# QUANTUM PROCESSOR
# ============================================================

class QuantumProcessor:

    def __init__(self):

        self.name = "Simulated NISQ Processor"

        self.num_qubits = 6

        self.qubits = [

            Qubit(0, 0.010, 0.001, 0.010),

            Qubit(1, 0.015, 0.002, 0.012),

            Qubit(2, 0.025, 0.003, 0.020),

            Qubit(3, 0.008, 0.001, 0.008),

            Qubit(4, 0.012, 0.002, 0.011),

            Qubit(5, 0.030, 0.004, 0.025)
        ]

        # Physical connections

        self.connections = [

            (0, 1),
            (1, 2),
            (1, 4),
            (3, 4),
            (4, 5)
        ]


# ============================================================
# GET QUBIT OBJECT
# ============================================================

def get_qubit(processor, qubit_id):

    for qubit in processor.qubits:

        if qubit.qubit_id == qubit_id:

            return qubit

    return None


# ============================================================
# CHECK CONNECTIVITY
# ============================================================

def are_connected(processor, q1, q2):

    return (
        (q1, q2) in processor.connections
        or
        (q2, q1) in processor.connections
    )


# ============================================================
# FIND POSSIBLE ALLOCATIONS
# ============================================================

def find_two_qubit_allocations(processor):

    allocations = []

    for q1, q2 in combinations(
        range(processor.num_qubits),
        2
    ):

        if are_connected(
            processor,
            q1,
            q2
        ):

            qubit1 = get_qubit(
                processor,
                q1
            )

            qubit2 = get_qubit(
                processor,
                q2
            )

            average_reliability = (
                qubit1.reliability
                + qubit2.reliability
            ) / 2

            average_two_gate_error = (
                qubit1.two_gate_error
                + qubit2.two_gate_error
            ) / 2

            allocations.append({

                "qubits": (q1, q2),

                "reliability":
                    average_reliability,

                "two_gate_error":
                    average_two_gate_error
            })

    return allocations


# ============================================================
# DISPLAY POSSIBLE ALLOCATIONS
# ============================================================

def display_allocations(allocations):

    print("\n")
    print("=" * 75)
    print("POSSIBLE TWO-QUBIT ALLOCATIONS")
    print("=" * 75)

    print(
        f"{'Physical Qubits':<25}"
        f"{'Avg Reliability':<20}"
        f"{'Avg 2Q Error':<20}"
    )

    print("-" * 75)

    for allocation in allocations:

        q1, q2 = allocation["qubits"]

        reliability = (
            allocation["reliability"] * 100
        )

        two_gate_error = (
            allocation["two_gate_error"] * 100
        )

        print(
            f"Q{q1} + Q{q2:<20}"
            f"{reliability:.2f}%"
            f"{'':<14}"
            f"{two_gate_error:.2f}%"
        )


# ============================================================
# SELECT BEST ALLOCATION
# ============================================================

def select_best_allocation(allocations):

    if not allocations:

        return None

    best = max(
        allocations,
        key=lambda allocation:
            allocation["reliability"]
    )

    return best


# ============================================================
# THREE-QUBIT CONNECTED ALLOCATIONS
# ============================================================

def is_fully_connected(processor, qubits):

    for q1, q2 in combinations(qubits, 2):

        if not are_connected(
            processor,
            q1,
            q2
        ):

            return False

    return True


# ============================================================
# FIND THREE-QUBIT ALLOCATIONS
# ============================================================

def find_three_qubit_allocations(processor):

    allocations = []

    for qubits in combinations(
        range(processor.num_qubits),
        3
    ):

        # A three-qubit circuit does not necessarily
        # need every pair to be directly connected.
        #
        # For this first version we accept a connected
        # chain of three physical qubits.

        connected_edges = 0

        for q1, q2 in combinations(qubits, 2):

            if are_connected(
                processor,
                q1,
                q2
            ):

                connected_edges += 1

        if connected_edges >= 2:

            qubit_objects = [

                get_qubit(
                    processor,
                    q
                )

                for q in qubits
            ]

            average_reliability = sum(
                q.reliability
                for q in qubit_objects
            ) / 3

            allocations.append({

                "qubits": qubits,

                "reliability":
                    average_reliability
            })

    return allocations


# ============================================================
# DISPLAY THREE-QUBIT ALLOCATIONS
# ============================================================

def display_three_qubit_allocations(
    allocations
):

    print("\n")
    print("=" * 75)
    print("POSSIBLE THREE-QUBIT ALLOCATIONS")
    print("=" * 75)

    for number, allocation in enumerate(
        allocations,
        start=1
    ):

        qubits = allocation["qubits"]

        reliability = (
            allocation["reliability"]
            * 100
        )

        formatted_qubits = ", ".join(
            f"Q{q}"
            for q in qubits
        )

        print(
            f"{number}. "
            f"{formatted_qubits}"
            f" → Average reliability: "
            f"{reliability:.2f}%"
        )


# ============================================================
# MAIN
# ============================================================

def main():

    processor = QuantumProcessor()

    print("\n")
    print("=" * 75)
    print("PHASE 4 - CIRCUIT TO PHYSICAL-QUBIT ALLOCATION")
    print("=" * 75)

    print(
        "\nProcessor:",
        processor.name
    )

    print(
        "Available physical qubits:",
        processor.num_qubits
    )

    # --------------------------------------------------------
    # TWO-QUBIT CIRCUIT
    # --------------------------------------------------------

    print("\n")
    print("TARGET CIRCUIT: Bell State")

    print(
        "Required physical qubits: 2"
    )

    allocations = find_two_qubit_allocations(
        processor
    )

    display_allocations(
        allocations
    )

    best_allocation = select_best_allocation(
        allocations
    )

    if best_allocation:

        q1, q2 = best_allocation["qubits"]

        print("\n")
        print("=" * 75)
        print("BEST ALLOCATION FOR BELL STATE")
        print("=" * 75)

        print(
            f"Selected physical qubits: "
            f"Q{q1}, Q{q2}"
        )

        print(
            f"Average reliability: "
            f"{best_allocation['reliability'] * 100:.2f}%"
        )

        print(
            f"Average 2-qubit gate error: "
            f"{best_allocation['two_gate_error'] * 100:.2f}%"
        )

    # --------------------------------------------------------
    # THREE-QUBIT CIRCUIT
    # --------------------------------------------------------

    print("\n")
    print("TARGET CIRCUIT: GHZ State")

    print(
        "Required physical qubits: 3"
    )

    three_qubit_allocations = (
        find_three_qubit_allocations(
            processor
        )
    )

    display_three_qubit_allocations(
        three_qubit_allocations
    )

    print("\n")
    print("=" * 75)
    print("PHASE 4 COMPLETED")
    print("=" * 75)


# ============================================================
# PROGRAM START
# ============================================================

if __name__ == "__main__":

    main()