#!/usr/bin/env python3
"""
Paxos Driver Script

This script demonstrates various scenarios of the Paxos consensus algorithm
using MPI for distributed communication between nodes.
"""

from mpi4py import MPI
import time
from paxos import PaxosNode, Colors


def print_header(rank, size):
    """Print the program header."""
    if rank == 0:
        print(Colors.BOLD + "=" * 70)
        print("PAXOS CONSENSUS ALGORITHM - MPI Implementation")
        print("=" * 70 + Colors.RESET)
        print(f"{Colors.CYAN}Number of nodes: {size}{Colors.RESET}")
        print(f"{Colors.CYAN}Majority needed: {(size // 2) + 1}{Colors.RESET}")
        print(Colors.BOLD + "=" * 70 + Colors.RESET)
        time.sleep(0.5)


def print_scenario_header(node, scenario_num, description):
    """Print a scenario header."""
    node.log("", Colors.WHITE)
    node.log("=" * 60, Colors.CYAN + Colors.BOLD)
    node.log(f"SCENARIO {scenario_num}: {description}", Colors.CYAN + Colors.BOLD)
    node.log("=" * 60, Colors.CYAN + Colors.BOLD)


def print_final_state(rank, size, node):
    """Print the final consensus state of all nodes."""
    if rank == 0:
        print("\n" + Colors.BOLD + "=" * 70)
        print("FINAL CONSENSUS STATE")
        print("=" * 70 + Colors.RESET)
    
    MPI.COMM_WORLD.Barrier()
    time.sleep(0.1 * rank)  # Stagger output so it's readable
    
    node.print_state()
    
    MPI.COMM_WORLD.Barrier()
    if rank == 0:
        print(Colors.BOLD + "=" * 70 + Colors.RESET)


def scenario_single_proposer(node, rank):
    """
    Scenario 1: Single proposer (Node 0) proposes a value.
    This demonstrates the basic case with no conflicts.
    """
    if rank == 0:
        time.sleep(1)
        print_scenario_header(node, 1, "Node 0 proposing value 'ALPHA'")
        node.propose_value("ALPHA")
    else:
        node.run_acceptor(duration=5)


def scenario_sequential_proposers(node, rank, size):
    """
    Scenario 2: Node 1 tries to propose after Node 0.
    This shows how Paxos handles a second proposal after consensus.
    """
    if size > 1:
        if rank == 1:
            time.sleep(1)
            print_scenario_header(node, 2, "Node 1 proposing value 'BETA'")
            node.propose_value("BETA")
        else:
            node.run_acceptor(duration=5)


def scenario_simultaneous_proposers(node, rank, size):
    """
    Scenario 3: Two nodes propose simultaneously.
    This demonstrates conflict resolution - one will win, one may need to retry.
    """
    if size >= 3:
        if rank == 0:
            print_scenario_header(node, 3, "Node 0 and Node 1 proposing SIMULTANEOUSLY")
            time.sleep(0.5)
        
        MPI.COMM_WORLD.Barrier()
        
        if rank == 0:
            # Node 0 proposes GAMMA
            node.log("Attempting to propose 'GAMMA' (simultaneous)", Colors.CYAN + Colors.BOLD)
            time.sleep(0.1)  # Small delay
            node.propose_value("GAMMA")
        elif rank == 1:
            # Node 1 proposes DELTA at nearly the same time
            node.log("Attempting to propose 'DELTA' (simultaneous)", Colors.CYAN + Colors.BOLD)
            time.sleep(0.15)  # Slightly different timing
            node.propose_value("DELTA")
        else:
            # Other nodes act as acceptors
            node.run_acceptor(duration=8)


def main():
    """
    Main driver function that orchestrates the Paxos demonstration.
    """
    comm = MPI.COMM_WORLD
    rank = comm.Get_rank()
    size = comm.Get_size()
    
    # Check minimum requirements
    if size < 3:
        if rank == 0:
            print(f"{Colors.RED}Error: Paxos requires at least 3 nodes for fault tolerance{Colors.RESET}")
            print(f"{Colors.YELLOW}Run with: mpiexec -n <N> python run_paxos.py (where N >= 3){Colors.RESET}")
        return
    
    # Initialize node
    node = PaxosNode(rank, size, verbose=True)
    
    # Print program header
    print_header(rank, size)
    comm.Barrier()
    
    # Run Scenario 1: Single proposer
    scenario_single_proposer(node, rank)
    comm.Barrier()
    time.sleep(1)
    
    # Run Scenario 2: Sequential proposers
    scenario_sequential_proposers(node, rank, size)
    comm.Barrier()
    time.sleep(1)
    
    # Run Scenario 3: Simultaneous proposers
    scenario_simultaneous_proposers(node, rank, size)
    comm.Barrier()
    time.sleep(1)
    
    # Print final state
    print_final_state(rank, size, node)


if __name__ == "__main__":
    main()

