# Quantum Palloq

A Palloq-inspired quantum multiprogramming simulation project that demonstrates how multiple quantum circuits can be managed, allocated, protected from crosstalk, and executed simultaneously on a simulated quantum processor.

## About the Project

Quantum computers have limited qubits and are affected by noise and interference. Running quantum circuits one by one can leave the available quantum resources underutilized.

This project demonstrates a simplified approach to **quantum multiprogramming**, where multiple quantum circuits can share a quantum processor and execute simultaneously.

The project is implemented using **Python, Qiskit, Qiskit Aer, and Flask**.

## Project Phases

The project is divided into 8 phases:

1. **Basic Quantum Circuits**
   Creates and demonstrates basic quantum circuits.

2. **Job Queue**
   Manages multiple quantum circuit jobs waiting for execution.

3. **Processor Topology**
   Represents the available physical qubits and their connections.

4. **Qubit Allocation**
   Allocates circuit qubits to suitable physical qubits.

5. **Physical Buffer**
   Maintains separation between circuits to reduce possible interference.

6. **Crosstalk Detection**
   Simulates possible interference between simultaneously running circuits.

7. **Simultaneous Execution**
   Executes multiple compatible quantum circuits together using the simulator.

8. **Performance Metrics**
   Calculates and displays execution and performance information.

## Technologies Used

* Python 3.14
* Qiskit 2.5.2
* Qiskit Aer 0.17.2
* Flask
* Flask-CORS
* HTML
* JavaScript
* Quantum circuit simulation

## Requirements

Make sure Python is installed.

Check Python:

```bash
py --version
```

The project uses:

```text
Python 3.14
Qiskit 2.5.2
Qiskit Aer 0.17.2
```

## Installation

### 1. Clone the Repository

Open Command Prompt and run:

```bash

git clone https://github.com/AkshayaSurala/quantum_palloq.git
```

Move into the project folder:

```bash
cd quantum_palloq
```

### 2. Install Required Packages

Install Qiskit:

```bash
py -m pip install qiskit==2.5.2
```

Install Qiskit Aer:

```bash
py -m pip install qiskit-aer==0.17.2
```

Install Flask and Flask-CORS:

```bash
py -m pip install flask flask-cors
```

### 3. Verify Installation

Check Qiskit:

```bash
py -m pip show qiskit
```

Check Qiskit Aer:

```bash
py -m pip show qiskit-aer
```

Check Flask:

```bash
py -m pip show flask
```

## Run the Project

From inside the project folder:

```bash
py app.py
```

The terminal should display:

```text
QUANTUM MULTIPROGRAMMING DASHBOARD
============================================================
Backend: Flask
Processor: 6 simulated qubits
Aer simulator: Enabled
Server: http://127.0.0.1:5000
============================================================
```

Open a web browser and go to:

```text
http://127.0.0.1:5000
```

The Quantum Multiprogramming Dashboard will open.

## Project Structure

```text
quantum_palloq/
│
├── app.py
│
├── templates/
│   └── index.html
│
├── phase1_basic_circuits.py
├── phase2_job_queue.py
├── phase3_processor.py
├── phase4_allocation.py
├── phase5_physical_buffer.py
├── phase6_crosstalk.py
├── phase7_simultaneous_execution.py
└── phase8_performance_metrics.py
```

## How the System Works

```text
Quantum Circuits
       ↓
   Job Queue
       ↓
Processor Topology
       ↓
  Qubit Allocation
       ↓
 Physical Buffer
       ↓
 Crosstalk Detection
       ↓
Simultaneous Execution
       ↓
Performance Metrics
```

## Main Dashboard

The Flask dashboard provides a visual interface for the quantum multiprogramming simulation.

It allows the user to observe the different stages of the system, including circuit processing, qubit allocation, crosstalk handling, simultaneous execution, and performance evaluation.

## Important Note

This project is a **Palloq-inspired software simulation** designed for demonstrating the concepts of quantum multiprogramming.

It uses a simulated quantum processor rather than directly executing the circuits on a real IBM Quantum processor.

## Stopping the Server

To stop the Flask server, press:

```text
CTRL + C
```

## Repository

GitHub:

https://github.com/AkshayaSurala/quantum_palloq.git
