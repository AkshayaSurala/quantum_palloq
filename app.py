from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import time
import math

from qiskit import QuantumCircuit, transpile
from qiskit_aer import AerSimulator


# ============================================================
# FLASK APP
# ============================================================

app = Flask(__name__)
CORS(app)


# ============================================================
# PROJECT CONFIGURATION
# ============================================================

PROCESSOR_QUBITS = 6

# Simulated NISQ processor
QUBIT_RELIABILITY = {
    0: 99.30,
    1: 99.03,
    2: 98.40,
    3: 99.43,
    4: 99.17,
    5: 98.03
}

# Simulated processor topology
#
#        Q0 ----- Q1 ----- Q2
#                  |
#                  Q4
#                 /  \
#               Q3    Q5
#
TOPOLOGY = [
    (0, 1),
    (1, 2),
    (1, 4),
    (3, 4),
    (4, 5)
]


# ============================================================
# CIRCUIT DEFINITIONS
# ============================================================

CIRCUITS = {
    "bell": {
        "name": "Bell State",
        "short_name": "Bell",
        "qubits": 2,
        "description": "Creates an entangled Bell state.",
        "color": "blue"
    },

    "ghz": {
        "name": "GHZ State",
        "short_name": "GHZ",
        "qubits": 3,
        "description": "Creates a 3-qubit GHZ entangled state.",
        "color": "purple"
    },

    "hadamard": {
        "name": "Hadamard",
        "short_name": "H",
        "qubits": 1,
        "description": "Applies a Hadamard gate to create superposition.",
        "color": "green"
    },

    "toffoli": {
        "name": "Toffoli",
        "short_name": "Toffoli",
        "qubits": 3,
        "description": "Three-qubit controlled-controlled-X operation.",
        "color": "orange"
    }
}


# ============================================================
# AER SIMULATOR
# ============================================================

SIMULATOR = AerSimulator()


# ============================================================
# UTILITY FUNCTIONS
# ============================================================

def normalize_selection(selected):
    """
    Makes sure the selected circuit list is valid.
    Removes duplicates while preserving order.
    """

    if not isinstance(selected, list):
        return []

    result = []

    for item in selected:
        if item in CIRCUITS and item not in result:
            result.append(item)

    return result


def circuit_qubit_count(selected):
    return sum(CIRCUITS[name]["qubits"] for name in selected)


def neighbors(qubit):
    result = []

    for a, b in TOPOLOGY:
        if a == qubit:
            result.append(b)
        elif b == qubit:
            result.append(a)

    return result


def shortest_distance(start, end):
    """
    Calculates shortest graph distance between two physical qubits.
    """

    if start == end:
        return 0

    visited = {start}
    queue = [(start, 0)]

    while queue:
        current, distance = queue.pop(0)

        for nxt in neighbors(current):

            if nxt == end:
                return distance + 1

            if nxt not in visited:
                visited.add(nxt)
                queue.append((nxt, distance + 1))

    return 999


def allocation_score(qubits):
    """
    Score an allocation using simulated qubit reliability.
    Higher is better.
    """

    if not qubits:
        return 0

    values = [QUBIT_RELIABILITY[q] for q in qubits]

    return sum(values) / len(values)


def find_best_connected_qubits(required):
    """
    Finds a connected group of physical qubits.

    This is a simplified Palloq-inspired allocation strategy.
    """

    if required <= 0:
        return []

    if required > PROCESSOR_QUBITS:
        return None

    best = None
    best_score = -1

    # Try every combination
    from itertools import combinations

    for combo in combinations(range(PROCESSOR_QUBITS), required):

        combo_set = set(combo)

        # Check connectivity
        if required > 1:

            visited = {combo[0]}
            queue = [combo[0]]

            while queue:

                current = queue.pop(0)

                for nxt in neighbors(current):

                    if nxt in combo_set and nxt not in visited:
                        visited.add(nxt)
                        queue.append(nxt)

            if len(visited) != required:
                continue

        score = allocation_score(combo)

        if score > best_score:
            best_score = score
            best = list(combo)

    return best


def allocate_circuits(selected):
    """
    Allocates selected logical circuits to physical qubits.
    """

    allocation = {}
    used = []
    remaining = set(range(PROCESSOR_QUBITS))

    # Larger circuits first
    ordered = sorted(
        selected,
        key=lambda x: CIRCUITS[x]["qubits"],
        reverse=True
    )

    for circuit_name in ordered:

        required = CIRCUITS[circuit_name]["qubits"]

        # Try to find allocation among currently unused qubits
        candidates = []

        from itertools import combinations

        for combo in combinations(sorted(remaining), required):

            if required > 1:

                combo_set = set(combo)

                visited = {combo[0]}
                queue = [combo[0]]

                while queue:

                    current = queue.pop(0)

                    for nxt in neighbors(current):

                        if nxt in combo_set and nxt not in visited:
                            visited.add(nxt)
                            queue.append(nxt)

                if len(visited) != required:
                    continue

            candidates.append(list(combo))

        if candidates:

            best = max(
                candidates,
                key=lambda x: allocation_score(x)
            )

        else:
            # Fallback: use any available qubits
            available = sorted(remaining)

            if len(available) < required:
                return None

            best = available[:required]

        allocation[circuit_name] = best

        for q in best:
            used.append(q)
            remaining.discard(q)

    return allocation


def choose_physical_buffer(allocation):
    """
    Chooses an unused qubit as a physical buffer.

    In this simplified model the buffer does not change graph
    distance. Instead, it reduces the simulated crosstalk penalty.
    """

    if not allocation:
        return None

    used = set()

    for qubits in allocation.values():
        used.update(qubits)

    available = [
        q for q in range(PROCESSOR_QUBITS)
        if q not in used
    ]

    if not available:
        return None

    # Prefer Q2 because it is between common regions in our
    # simplified demonstration topology.
    if 2 in available:
        return 2

    return available[0]


def minimum_inter_circuit_distance(allocation):
    """
    Finds the minimum physical distance between qubits belonging
    to different simultaneously running circuits.
    """

    names = list(allocation.keys())

    if len(names) < 2:
        return None

    minimum = 999

    for i in range(len(names)):
        for j in range(i + 1, len(names)):

            for q1 in allocation[names[i]]:
                for q2 in allocation[names[j]]:

                    distance = shortest_distance(q1, q2)

                    if distance < minimum:
                        minimum = distance

    return minimum


def calculate_crosstalk(allocation, buffer):
    """
    Simplified crosstalk model inspired by the project concept.

    Important:
    This is a software simulation, not measured IBM hardware
    crosstalk.
    """

    if not allocation or len(allocation) < 2:
        return {
            "distance": None,
            "without_buffer": 0.0,
            "with_buffer": 0.0,
            "base_reliability": allocation_score(
                [q for values in allocation.values() for q in values]
            ),
            "adjusted_without": allocation_score(
                [q for values in allocation.values() for q in values]
            ),
            "adjusted_with": allocation_score(
                [q for values in allocation.values() for q in values]
            )
        }

    all_qubits = [
        q
        for values in allocation.values()
        for q in values
    ]

    base_reliability = allocation_score(all_qubits)

    distance = minimum_inter_circuit_distance(allocation)

    # Simplified project penalty
    if distance is None:
        without_buffer = 0.0
    elif distance <= 1:
        without_buffer = 2.0
    elif distance == 2:
        without_buffer = 1.0
    else:
        without_buffer = 0.5

    # Buffer reduces simulated penalty
    if buffer is not None:
        with_buffer = max(0.5, without_buffer - 1.5)
    else:
        with_buffer = without_buffer

    adjusted_without = max(
        0,
        base_reliability - without_buffer
    )

    adjusted_with = max(
        0,
        base_reliability - with_buffer
    )

    return {
        "distance": distance,
        "without_buffer": round(without_buffer, 2),
        "with_buffer": round(with_buffer, 2),
        "base_reliability": round(base_reliability, 2),
        "adjusted_without": round(adjusted_without, 2),
        "adjusted_with": round(adjusted_with, 2)
    }


# ============================================================
# QUANTUM CIRCUIT CREATION
# ============================================================

def create_circuit(name):
    """
    Creates the actual Qiskit circuit.
    """

    if name == "bell":

        qc = QuantumCircuit(2)

        qc.h(0)
        qc.cx(0, 1)

        return qc

    if name == "ghz":

        qc = QuantumCircuit(3)

        qc.h(0)
        qc.cx(0, 1)
        qc.cx(0, 2)

        return qc

    if name == "hadamard":

        qc = QuantumCircuit(1)

        qc.h(0)

        return qc

    if name == "toffoli":

        qc = QuantumCircuit(3)

        # Put controls into |1>
        qc.x(0)
        qc.x(1)

        # Toffoli
        qc.ccx(0, 1, 2)

        return qc

    raise ValueError(f"Unknown circuit: {name}")


def execute_circuit(name, shots=1024):
    """
    Executes a circuit using Qiskit Aer.
    """

    qc = create_circuit(name)

    qc.measure_all()

    start = time.perf_counter()

    compiled = transpile(qc, SIMULATOR)

    job = SIMULATOR.run(
        compiled,
        shots=shots
    )

    result = job.result()

    counts = result.get_counts()

    elapsed = time.perf_counter() - start

    total = sum(counts.values())

    # For these ideal circuits every measured shot is considered
    # successful in the noiseless Aer simulation.
    successful = total

    pst = (
        successful / total * 100
        if total > 0
        else 0
    )

    return {
        "counts": counts,
        "time": round(elapsed, 6),
        "pst": round(pst, 2),
        "shots": shots
    }


# ============================================================
# PARALLEL EXECUTION
# ============================================================

def execute_selected(selected, allocation):
    """
    Executes each selected logical circuit independently using
    Aer while reporting them as a simultaneous allocation.

    This represents the project simulation. It does not claim
    real hardware parallel execution.
    """

    results = {}

    total_start = time.perf_counter()

    for name in selected:

        result = execute_circuit(name)

        results[name] = result

    total_time = time.perf_counter() - total_start

    return results, total_time


# ============================================================
# API: HEALTH
# ============================================================

@app.route("/api/health", methods=["GET"])
def health():

    return jsonify({
        "status": "ok",
        "backend": "Flask",
        "processor_qubits": PROCESSOR_QUBITS,
        "aer": True
    })


# ============================================================
# API: PROCESSOR
# ============================================================

@app.route("/api/processor", methods=["GET"])
def processor():

    return jsonify({
        "qubits": PROCESSOR_QUBITS,
        "reliability": QUBIT_RELIABILITY,
        "topology": TOPOLOGY
    })


# ============================================================
# API: CIRCUITS
# ============================================================

@app.route("/api/circuits", methods=["GET"])
def get_circuits():

    return jsonify(CIRCUITS)


# ============================================================
# API: COMPOSE
# ============================================================

@app.route("/api/compose", methods=["POST"])
def compose():

    try:

        data = request.get_json(silent=True) or {}

        selected = normalize_selection(
            data.get("circuits", [])
        )

        if not selected:

            return jsonify({
                "success": False,
                "error": "Please select at least one circuit."
            }), 400

        total_qubits = circuit_qubit_count(selected)

        if total_qubits > PROCESSOR_QUBITS:

            return jsonify({
                "success": False,
                "error": (
                    f"Selected circuits require {total_qubits} "
                    f"qubits, but the processor has only "
                    f"{PROCESSOR_QUBITS} qubits."
                )
            }), 400

        allocation = allocate_circuits(selected)

        if allocation is None:

            return jsonify({
                "success": False,
                "error": "Unable to find a valid physical allocation."
            }), 400

        buffer = choose_physical_buffer(allocation)

        crosstalk = calculate_crosstalk(
            allocation,
            buffer
        )

        used = sorted([
            q
            for values in allocation.values()
            for q in values
        ])

        used_count = len(used)

        utilization = (
            used_count / PROCESSOR_QUBITS * 100
        )

        if buffer is not None:
            non_buffer = PROCESSOR_QUBITS - 1
        else:
            non_buffer = PROCESSOR_QUBITS

        effective_utilization = (
            used_count / non_buffer * 100
            if non_buffer > 0
            else 0
        )

        return jsonify({
            "success": True,
            "selected": selected,
            "total_qubits": total_qubits,
            "allocation": allocation,
            "used_qubits": used,
            "buffer": buffer,
            "utilization": round(utilization, 2),
            "effective_utilization": round(
                effective_utilization,
                2
            ),
            "crosstalk": crosstalk
        })

    except Exception as e:

        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


# ============================================================
# API: RUN
# ============================================================

@app.route("/api/run", methods=["POST"])
def run_simulation():

    try:

        data = request.get_json(silent=True) or {}

        selected = normalize_selection(
            data.get("circuits", [])
        )

        if not selected:

            return jsonify({
                "success": False,
                "error": "Please compose at least one circuit."
            }), 400

        total_qubits = circuit_qubit_count(selected)

        if total_qubits > PROCESSOR_QUBITS:

            return jsonify({
                "success": False,
                "error": (
                    f"Selected circuits require {total_qubits} "
                    f"qubits, but only {PROCESSOR_QUBITS} "
                    f"physical qubits are available."
                )
            }), 400

        allocation = allocate_circuits(selected)

        if allocation is None:

            return jsonify({
                "success": False,
                "error": "Allocation failed."
            }), 400

        buffer = choose_physical_buffer(allocation)

        crosstalk = calculate_crosstalk(
            allocation,
            buffer
        )

        results, parallel_time = execute_selected(
            selected,
            allocation
        )

        separate_time = sum(
            results[name]["time"]
            for name in selected
        )

        if separate_time > 0:

            estimated_reduction = (
                (separate_time - parallel_time)
                / separate_time
                * 100
            )

        else:
            estimated_reduction = 0

        average_pst = (
            sum(
                results[name]["pst"]
                for name in selected
            )
            / len(selected)
        )

        used_qubits = sorted([
            q
            for values in allocation.values()
            for q in values
        ])

        utilization = (
            len(used_qubits)
            / PROCESSOR_QUBITS
            * 100
        )

        return jsonify({
            "success": True,

            "selected": selected,

            "allocation": allocation,

            "buffer": buffer,

            "used_qubits": used_qubits,

            "total_qubits": total_qubits,

            "utilization": round(
                utilization,
                2
            ),

            "crosstalk": crosstalk,

            "results": results,

            "performance": {
                "parallel_time": round(
                    parallel_time,
                    6
                ),

                "separate_time": round(
                    separate_time,
                    6
                ),

                "estimated_reduction": round(
                    estimated_reduction,
                    2
                ),

                "average_pst": round(
                    average_pst,
                    2
                )
            }
        })

    except Exception as e:

        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


# ============================================================
# MAIN DASHBOARD
# ============================================================

@app.route("/")
def index():

    return render_template(
        "index.html",

        # IMPORTANT:
        # These variables are passed to Jinja so the old
        # "circuits.items()" error cannot occur.
        circuits=CIRCUITS,

        processor_qubits=PROCESSOR_QUBITS,

        topology=TOPOLOGY,

        reliability=QUBIT_RELIABILITY
    )


# ============================================================
# ERROR HANDLER
# ============================================================

@app.errorhandler(404)
def not_found(error):

    return jsonify({
        "success": False,
        "error": "Endpoint not found."
    }), 404


@app.errorhandler(500)
def server_error(error):

    return jsonify({
        "success": False,
        "error": "Internal server error."
    }), 500


# ============================================================
# START SERVER
# ============================================================

if __name__ == "__main__":

    print()
    print("=" * 60)
    print("QUANTUM MULTIPROGRAMMING DASHBOARD")
    print("=" * 60)
    print("Backend: Flask")
    print("Processor: 6 simulated qubits")
    print("Aer simulator: Enabled")
    print("Server: http://127.0.0.1:5000")
    print("=" * 60)
    print()

    app.run(
        host="127.0.0.1",
        port=5000,
        debug=True
    )