# Paxos Consensus Algorithm - MPI Implementation

A clean, modular implementation of the Paxos consensus algorithm using MPI (Message Passing Interface) in Python.

## Overview

This implementation demonstrates the basic Paxos consensus algorithm where multiple distributed nodes agree on a single value. The algorithm consists of two phases:

1. **Phase 1 (Prepare)**: A proposer sends a prepare request with a proposal ID to acceptors
2. **Phase 2 (Accept)**: If a majority promises, the proposer sends an accept request with the value

## Features

- Complete Paxos protocol implementation
- Modular design with separate library and driver files
- Color-coded terminal output for easy visualization
- Detailed logging of all messages and communications
- Support for multiple proposers and simultaneous proposals
- Majority-based consensus
- Clear visualization of the protocol phases

## Requirements

- Python 3.6+
- MPI implementation (OpenMPI or MPICH)
- mpi4py

## Installation

1. Install MPI on your system:

**Ubuntu/Debian:**
```bash
sudo apt-get update
sudo apt-get install openmpi-bin openmpi-common libopenmpi-dev
```

**Fedora/RHEL:**
```bash
sudo dnf install openmpi openmpi-devel
```

**macOS:**
```bash
brew install open-mpi
```

2. Install Python dependencies:
```bash
pip install -r requirements.txt
```

## Quick Start

1. **Test your MPI setup** (optional but recommended):
```bash
mpiexec -n 4 python test_mpi.py
```

2. **Run the Paxos demonstration**:
```bash
mpiexec -n 5 python run_paxos.py
```

## Usage

Run the Paxos algorithm with N nodes (minimum 3 required for fault tolerance):

```bash
mpiexec -n 5 python run_paxos.py
```

This will start 5 nodes that will participate in the consensus algorithm and run through multiple scenarios.

### Example Output

```
======================================================================
PAXOS CONSENSUS ALGORITHM - MPI Implementation
======================================================================
Number of nodes: 5
Majority needed: 3
======================================================================

[Node 0] ==================================================
[Node 0] STARTING PROPOSAL
[Node 0] ==================================================
[Node 0] Proposing value: ALPHA with proposal_id: 5
[Node 0] --- Phase 1: PREPARE ---
[Node 0] -> Sending PREPARE to Node 1: {'proposal_id': 5}
[Node 1] <- Received PREPARE from Node 0: {'proposal_id': 5}
[Node 1] [OK] Promising proposal_id=5
...
[Node 0] [OK] Received majority of promises (3/3)
[Node 0] --- Phase 2: ACCEPT ---
...
[Node 0] *** CONSENSUS REACHED: ALPHA ***
```

Note: The actual output will be color-coded for better readability:
- Cyan: PREPARE messages and proposals
- Blue: PROMISE messages
- Yellow: ACCEPT messages
- Green: ACCEPTED messages and successes
- Red: NACK messages and failures
- Magenta: Consensus notifications

## How It Works

### Message Types

- **PREPARE**: Proposer asks acceptors to promise not to accept lower-numbered proposals
- **PROMISE**: Acceptor agrees to the prepare request
- **ACCEPT**: Proposer asks acceptors to accept a specific value
- **ACCEPTED**: Acceptor confirms acceptance of the value
- **NACK**: Negative acknowledgment when a promise/accept is rejected

### Node Roles

Each node can act as both:
- **Proposer**: Proposes values to be agreed upon
- **Acceptor**: Accepts or rejects proposals based on the protocol rules

### Consensus Rules

- A proposal needs acceptance from a **majority** of nodes (⌊N/2⌋ + 1)
- Higher proposal IDs always supersede lower ones
- Once an acceptor accepts a value, it must inform the proposer
- Safety is guaranteed: all nodes that reach consensus will agree on the same value

## Code Structure

```
paxos/
├── paxos.py                 # Core Paxos implementation (library)
│   ├── Colors class         # ANSI color codes for terminal output
│   └── PaxosNode class      # Main Paxos node implementation
│       ├── Acceptor state   # (promised_id, accepted_id, accepted_value)
│       ├── Proposer state   # (proposal_id, proposal_value)
│       ├── handle_prepare() # Process PREPARE messages
│       ├── handle_accept()  # Process ACCEPT messages
│       ├── propose_value()  # Initiate a proposal (2-phase commit)
│       └── run_acceptor()   # Listen for and process messages
│
└── run_paxos.py             # Driver script with example scenarios
    ├── scenario_single_proposer()      # One node proposes
    ├── scenario_sequential_proposers() # Two nodes propose sequentially
    ├── scenario_simultaneous_proposers() # Two nodes propose at the same time
    └── main()                          # Orchestrates all scenarios
```

## Scenarios Demonstrated

1. **Scenario 1**: Single Proposer - Node 0 proposes value "ALPHA"
   - Shows successful consensus when no conflicts exist
   - Demonstrates the basic 2-phase protocol

2. **Scenario 2**: Sequential Proposers - Node 1 tries to propose value "BETA"
   - Demonstrates how Paxos handles sequential proposals
   - Shows that new proposals can succeed with higher proposal IDs

3. **Scenario 3**: Simultaneous Proposers - Node 0 and Node 1 propose at the same time
   - Node 0 proposes "GAMMA" and Node 1 proposes "DELTA" simultaneously
   - Demonstrates conflict resolution in Paxos
   - Shows how one proposal wins based on timing and proposal IDs
   - Illustrates the safety property: only one value is chosen

## Customization

You can easily create your own scenarios by modifying `run_paxos.py`:

```python
# Create a custom scenario function
def my_custom_scenario(node, rank, size):
    if rank == 0:
        node.propose_value("MY_VALUE")
    else:
        node.run_acceptor(duration=5)

# Add it to main()
my_custom_scenario(node, rank, size)
comm.Barrier()
```

You can also use the `paxos.py` module in your own scripts:

```python
from paxos import PaxosNode
from mpi4py import MPI

comm = MPI.COMM_WORLD
node = PaxosNode(comm.Get_rank(), comm.Get_size())
node.propose_value("YOUR_VALUE")
```

## Understanding the Output

- `->` indicates a message being sent
- `<-` indicates a message being received
- `[OK]` indicates success (promise, acceptance)
- `[X]` indicates rejection
- `***` indicates consensus reached
- Colors provide quick visual identification of message types and states

## Troubleshooting

**Error: "Paxos requires at least 3 nodes"**
- Solution: Run with at least 3 processes: `mpiexec -n 3 python run_paxos.py`

**ModuleNotFoundError: No module named 'mpi4py'**
- Solution: Install mpi4py: `pip install mpi4py`
- Or install from requirements: `pip install -r requirements.txt`

**Cannot find mpiexec**
- Solution: Install OpenMPI or MPICH and ensure it's in your PATH

**Colors not appearing in terminal**
- Most modern terminals support ANSI colors by default
- If colors don't appear, your terminal may not support them
- The program will still work, just without colored output

**Want to test MPI installation?**
- Run the test script: `mpiexec -n 4 python test_mpi.py`
- This verifies your MPI setup before running the full Paxos demo

## Further Reading

- [Paxos Made Simple](https://lamport.azurewebsites.net/pubs/paxos-simple.pdf) by Leslie Lamport
- [The Part-Time Parliament](https://lamport.azurewebsites.net/pubs/lamport-paxos.pdf) - Original Paxos paper

## License

See LICENSE file for details.
