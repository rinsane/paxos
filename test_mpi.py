#!/usr/bin/env python3
"""
Simple MPI Test Script

Run this to verify your MPI setup is working correctly before running Paxos.
Usage: mpiexec -n 4 python test_mpi.py
"""

from mpi4py import MPI
import sys

def main():
    comm = MPI.COMM_WORLD
    rank = comm.Get_rank()
    size = comm.Get_size()
    
    print(f"Hello from process {rank} of {size}")
    
    if rank == 0:
        print("\n" + "="*50)
        print("MPI Setup Test Results")
        print("="*50)
        print(f"Total processes: {size}")
        print(f"MPI version: {MPI.Get_version()}")
        print("="*50)
        
        if size >= 3:
            print("\033[92m[OK] MPI is working correctly!\033[0m")
            print("You can now run: mpiexec -n 5 python run_paxos.py")
        else:
            print("\033[93m[WARNING] Running with less than 3 processes.\033[0m")
            print("Paxos requires at least 3 nodes for fault tolerance.")
            print("Try: mpiexec -n 5 python test_mpi.py")
        print("="*50)

if __name__ == "__main__":
    try:
        main()
    except ImportError as e:
        print(f"\033[91m[ERROR] Failed to import mpi4py: {e}\033[0m")
        print("Please install it with: pip install mpi4py")
        sys.exit(1)

