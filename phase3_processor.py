from dataclasses import dataclass


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
        """
        Simple reliability score.

        Lower error means higher reliability.
        """

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

        # ----------------------------------------------------
        # QUBIT CALIBRATION INFORMATION
        # ----------------------------------------------------

        self.qubits = [

            Qubit(
                qubit_id=0,
                readout_error=0.010,
                single_gate_error=0.001,
                two_gate_error=0.010
            ),

            Qubit(
                qubit_id=1,
                readout_error=0.015,
                single_gate_error=0.002,
                two_gate_error=0.012
            ),

            Qubit(
                qubit_id=2,
                readout_error=0.025,
                single_gate_error=0.003,
                two_gate_error=0.020
            ),

            Qubit(
                qubit_id=3,
                readout_error=0.008,
                single_gate_error=0.001,
                two_gate_error=0.008
            ),

            Qubit(
                qubit_id=4,
                readout_error=0.012,
                single_gate_error=0.002,
                two_gate_error=0.011
            ),

            Qubit(
                qubit_id=5,
                readout_error=0.030,
                single_gate_error=0.004,
                two_gate_error=0.025
            )
        ]

        # ----------------------------------------------------
        # PROCESSOR CONNECTIVITY
        # ----------------------------------------------------
        #
        # Q0 ─ Q1 ─ Q2
        #      │
        #      Q4
        #      │
        # Q3 ──┘
        #      │
        #      Q5
        #
        # Each tuple represents a physical connection.
        # ----------------------------------------------------

        self.connections = [

            (0, 1),
            (1, 2),
            (1, 4),
            (3, 4),
            (4, 5)

        ]


# ============================================================
# DISPLAY PROCESSOR
# ============================================================

def display_processor(processor):

    print("\n")
    print("=" * 75)
    print("SIMULATED NISQ QUANTUM PROCESSOR")
    print("=" * 75)

    print(f"Processor: {processor.name}")

    print(f"Number of physical qubits: {processor.num_qubits}")

    print("\n")
    print("QUBIT CALIBRATION INFORMATION")

    print("-" * 75)

    print(
        f"{'Qubit':<10}"
        f"{'Readout Error':<18}"
        f"{'1Q Gate Error':<18}"
        f"{'2Q Gate Error':<18}"
        f"{'Reliability':<15}"
    )

    print("-" * 75)

    for qubit in processor.qubits:

        print(
            f"Q{qubit.qubit_id:<9}"
            f"{qubit.readout_error * 100:.2f}%"
            f"{'':<12}"
            f"{qubit.single_gate_error * 100:.2f}%"
            f"{'':<12}"
            f"{qubit.two_gate_error * 100:.2f}%"
            f"{'':<12}"
            f"{qubit.reliability * 100:.2f}%"
        )

    print("-" * 75)

    print("\nPROCESSOR CONNECTIVITY")

    print("-" * 40)

    for connection in processor.connections:

        q1, q2 = connection

        print(
            f"Q{q1} <──── connected to ────> Q{q2}"
        )


# ============================================================
# FIND CONNECTED QUBITS
# ============================================================

def get_neighbors(processor, qubit_id):

    neighbors = []

    for q1, q2 in processor.connections:

        if q1 == qubit_id:
            neighbors.append(q2)

        elif q2 == qubit_id:
            neighbors.append(q1)

    return neighbors


# ============================================================
# DISPLAY NEIGHBORS
# ============================================================

def display_neighbors(processor):

    print("\n")
    print("=" * 75)
    print("QUBIT CONNECTIVITY")
    print("=" * 75)

    for qubit in processor.qubits:

        neighbors = get_neighbors(
            processor,
            qubit.qubit_id
        )

        neighbor_text = ", ".join(
            f"Q{q}" for q in neighbors
        )

        print(
            f"Q{qubit.qubit_id} → "
            f"Connected qubits: {neighbor_text}"
        )


# ============================================================
# FIND MOST RELIABLE QUBITS
# ============================================================

def find_reliable_qubits(processor):

    sorted_qubits = sorted(
        processor.qubits,
        key=lambda q: q.reliability,
        reverse=True
    )

    print("\n")
    print("=" * 75)
    print("QUBITS SORTED BY RELIABILITY")
    print("=" * 75)

    for position, qubit in enumerate(
        sorted_qubits,
        start=1
    ):

        print(
            f"{position}. "
            f"Q{qubit.qubit_id} → "
            f"Reliability: "
            f"{qubit.reliability * 100:.2f}%"
        )


# ============================================================
# MAIN
# ============================================================

def main():

    processor = QuantumProcessor()

    display_processor(processor)

    display_neighbors(processor)

    find_reliable_qubits(processor)

    print("\n")
    print("=" * 75)
    print("PHASE 3 COMPLETED")
    print("=" * 75)


if __name__ == "__main__":
    main()