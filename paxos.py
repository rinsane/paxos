#!/usr/bin/env python3
"""
Paxos Consensus Algorithm Implementation

This module provides a clean implementation of the Paxos consensus algorithm
for distributed systems. Each node can act as both a proposer and an acceptor.
"""

from mpi4py import MPI
import time

# Message tags for MPI communication
PREPARE = 1
PROMISE = 2
ACCEPT = 3
ACCEPTED = 4
NACK = 5

# ANSI color codes for terminal output
class Colors:
    RESET = '\033[0m'
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    BOLD = '\033[1m'


class PaxosNode:
    """
    Represents a node in the Paxos consensus protocol.
    Each node can propose values and accept proposals from others.
    """
    
    def __init__(self, rank, size, verbose=True):
        """
        Initialize a Paxos node.
        
        Args:
            rank: The unique identifier for this node
            size: Total number of nodes in the system
            verbose: Whether to print detailed logs
        """
        self.rank = rank
        self.size = size
        self.comm = MPI.COMM_WORLD
        self.verbose = verbose
        
        # Acceptor state variables
        self.promised_id = -1  # Highest proposal ID we have promised to
        self.accepted_id = -1  # ID of the proposal we accepted
        self.accepted_value = None  # The value we accepted
        
        # Proposer state variables
        self.proposal_id = rank  # Our current proposal ID (starts with our rank)
        self.proposal_value = None  # The value we are proposing
        
        # Consensus tracking
        self.consensus_reached = False
        self.consensus_value = None
    
    def log(self, message, color=Colors.WHITE):
        """
        Print a log message with this node's identifier.
        
        Args:
            message: The message to log
            color: ANSI color code for the message
        """
        if self.verbose:
            print(f"{color}[Node {self.rank}] {message}{Colors.RESET}", flush=True)
    
    def generate_proposal_id(self):
        """
        Generate a unique, monotonically increasing proposal ID.
        Uses round-robin scheme with node rank as tiebreaker.
        
        Returns:
            A new unique proposal ID
        """
        self.proposal_id += self.size
        return self.proposal_id
    
    def send_message(self, dest, msg_type, data):
        """
        Send a message to another node.
        
        Args:
            dest: Destination node rank
            msg_type: Type of message (PREPARE, PROMISE, etc.)
            data: Message payload dictionary
        """
        message = {'type': msg_type, 'data': data, 'from': self.rank}
        msg_name = self.get_msg_type_name(msg_type)
        msg_color = self.get_msg_color(msg_type)
        self.log(f"-> Sending {msg_name} to Node {dest}: {data}", msg_color)
        self.comm.send(message, dest=dest, tag=msg_type)
    
    def receive_message(self, source=MPI.ANY_SOURCE, tag=MPI.ANY_TAG):
        """
        Receive a message from another node.
        
        Args:
            source: Source node rank (or MPI.ANY_SOURCE)
            tag: Message tag (or MPI.ANY_TAG)
            
        Returns:
            Tuple of (message dict, message type)
        """
        status = MPI.Status()
        message = self.comm.recv(source=source, tag=tag, status=status)
        msg_type = status.Get_tag()
        msg_name = self.get_msg_type_name(msg_type)
        msg_color = self.get_msg_color(msg_type)
        self.log(f"<- Received {msg_name} from Node {message['from']}: {message['data']}", msg_color)
        return message, msg_type
    
    def get_msg_type_name(self, msg_type):
        """
        Get a human-readable name for a message type.
        
        Args:
            msg_type: The message type constant
            
        Returns:
            String name of the message type
        """
        names = {
            PREPARE: "PREPARE",
            PROMISE: "PROMISE",
            ACCEPT: "ACCEPT",
            ACCEPTED: "ACCEPTED",
            NACK: "NACK"
        }
        return names.get(msg_type, "UNKNOWN")
    
    def get_msg_color(self, msg_type):
        """
        Get the appropriate color for a message type.
        
        Args:
            msg_type: The message type constant
            
        Returns:
            ANSI color code
        """
        colors = {
            PREPARE: Colors.CYAN,
            PROMISE: Colors.BLUE,
            ACCEPT: Colors.YELLOW,
            ACCEPTED: Colors.GREEN,
            NACK: Colors.RED
        }
        return colors.get(msg_type, Colors.WHITE)
    
    def handle_prepare(self, proposal_id, from_node):
        """
        Handle a PREPARE request as an acceptor.
        
        This is Phase 1 of Paxos. We promise not to accept any proposals
        with IDs lower than this one.
        
        Args:
            proposal_id: The proposal ID from the proposer
            from_node: The rank of the proposing node
        """
        self.log(f"Processing PREPARE with proposal_id={proposal_id}", Colors.CYAN)
        
        if proposal_id > self.promised_id:
            # We can promise to this proposal
            self.promised_id = proposal_id
            response = {
                'promised': True,
                'accepted_id': self.accepted_id,
                'accepted_value': self.accepted_value
            }
            self.log(f"[OK] Promising proposal_id={proposal_id}", Colors.GREEN)
            self.send_message(from_node, PROMISE, response)
        else:
            # We already promised a higher ID, so reject this one
            self.log(f"[X] Rejecting proposal_id={proposal_id} (already promised={self.promised_id})", Colors.RED)
            self.send_message(from_node, NACK, {'promised_id': self.promised_id})
    
    def handle_accept(self, proposal_id, value, from_node):
        """
        Handle an ACCEPT request as an acceptor.
        
        This is Phase 2 of Paxos. We accept the value if we haven't
        promised a higher proposal ID.
        
        Args:
            proposal_id: The proposal ID from the proposer
            value: The value to accept
            from_node: The rank of the proposing node
        """
        self.log(f"Processing ACCEPT with proposal_id={proposal_id}, value={value}", Colors.YELLOW)
        
        if proposal_id >= self.promised_id:
            # Accept this proposal
            self.accepted_id = proposal_id
            self.accepted_value = value
            self.log(f"[OK] Accepted proposal_id={proposal_id}, value={value}", Colors.GREEN)
            self.send_message(from_node, ACCEPTED, {
                'accepted': True,
                'proposal_id': proposal_id,
                'value': value
            })
            
            # Mark that we have reached consensus
            if not self.consensus_reached:
                self.consensus_reached = True
                self.consensus_value = value
                self.log(f"*** CONSENSUS REACHED: {value} ***", Colors.MAGENTA + Colors.BOLD)
        else:
            # We promised a higher proposal, so reject
            self.log(f"[X] Rejecting ACCEPT for proposal_id={proposal_id}", Colors.RED)
            self.send_message(from_node, NACK, {'promised_id': self.promised_id})
    
    def propose_value(self, value):
        """
        Propose a value for consensus as a proposer.
        
        This runs the full 2-phase Paxos protocol:
        Phase 1: Send PREPARE and collect PROMISE responses
        Phase 2: Send ACCEPT and collect ACCEPTED responses
        
        Args:
            value: The value to propose
            
        Returns:
            True if consensus was reached, False otherwise
        """
        self.proposal_value = value
        proposal_id = self.generate_proposal_id()
        
        self.log("=" * 50, Colors.CYAN + Colors.BOLD)
        self.log(f"STARTING PROPOSAL", Colors.CYAN + Colors.BOLD)
        self.log("=" * 50, Colors.CYAN + Colors.BOLD)
        self.log(f"Proposing value: {value} with proposal_id: {proposal_id}", Colors.CYAN)
        
        # Phase 1: Send PREPARE to all other nodes
        self.log(f"--- Phase 1: PREPARE ---", Colors.CYAN)
        for i in range(self.size):
            if i != self.rank:
                self.send_message(i, PREPARE, {'proposal_id': proposal_id})
        
        # Collect PROMISE responses from acceptors
        promises = []
        nacks = 0
        majority = (self.size // 2) + 1
        responses_needed = self.size - 1
        
        for _ in range(responses_needed):
            msg, msg_type = self.receive_message()
            
            if msg_type == PROMISE:
                promises.append(msg['data'])
                # Check if we have a majority
                if len(promises) >= majority - 1:  # -1 because we count ourselves
                    break
            elif msg_type == NACK:
                nacks += 1
        
        # Check if we got enough promises
        if len(promises) < majority - 1:
            self.log(f"[X] PROPOSAL FAILED: Not enough promises ({len(promises)}/{majority-1})", Colors.RED)
            return False
        
        self.log(f"[OK] Received majority of promises ({len(promises)}/{majority-1})", Colors.GREEN)
        
        # Check if any acceptor already accepted a value
        # If so, we must use that value instead of our own
        max_accepted_id = -1
        accepted_value = None
        for promise in promises:
            if promise['accepted_id'] > max_accepted_id:
                max_accepted_id = promise['accepted_id']
                accepted_value = promise['accepted_value']
        
        # Use the previously accepted value if it exists, otherwise use our proposal
        final_value = accepted_value if accepted_value is not None else value
        if accepted_value is not None:
            self.log(f"Using previously accepted value: {accepted_value}", Colors.YELLOW)
        
        # Phase 2: Send ACCEPT to all other nodes
        self.log(f"--- Phase 2: ACCEPT ---", Colors.YELLOW)
        for i in range(self.size):
            if i != self.rank:
                self.send_message(i, ACCEPT, {
                    'proposal_id': proposal_id,
                    'value': final_value
                })
        
        # Collect ACCEPTED responses
        accepted = []
        for _ in range(responses_needed):
            msg, msg_type = self.receive_message()
            
            if msg_type == ACCEPTED:
                accepted.append(msg['data'])
                # Check if we have a majority
                if len(accepted) >= majority - 1:
                    break
        
        # Check if we got enough acceptances
        if len(accepted) >= majority - 1:
            self.log(f"[OK] Value accepted by majority ({len(accepted)}/{majority-1})", Colors.GREEN)
            if not self.consensus_reached:
                self.consensus_reached = True
                self.consensus_value = final_value
                self.log(f"*** CONSENSUS REACHED: {final_value} ***", Colors.MAGENTA + Colors.BOLD)
            return True
        else:
            self.log(f"[X] PROPOSAL FAILED: Not enough acceptances", Colors.RED)
            return False
    
    def run_acceptor(self, duration=5):
        """
        Run as an acceptor, listening for incoming messages.
        
        This method processes PREPARE and ACCEPT messages from proposers
        and responds according to the Paxos protocol.
        
        Args:
            duration: How long to listen for messages (in seconds)
        """
        start_time = time.time()
        
        while time.time() - start_time < duration:
            # Check if there's a message waiting
            if self.comm.Iprobe(source=MPI.ANY_SOURCE, tag=MPI.ANY_TAG):
                msg, msg_type = self.receive_message()
                
                if msg_type == PREPARE:
                    self.handle_prepare(msg['data']['proposal_id'], msg['from'])
                elif msg_type == ACCEPT:
                    self.handle_accept(
                        msg['data']['proposal_id'],
                        msg['data']['value'],
                        msg['from']
                    )
            
            # Small sleep to prevent busy waiting
            time.sleep(0.01)
    
    def print_state(self):
        """Print the current state of this node."""
        self.log(f"Consensus reached: {self.consensus_reached}", Colors.WHITE)
        if self.consensus_reached:
            self.log(f"Consensus value: {self.consensus_value}", Colors.MAGENTA)
        self.log(f"Promised ID: {self.promised_id}", Colors.WHITE)
        self.log(f"Accepted ID: {self.accepted_id}, Accepted value: {self.accepted_value}", Colors.WHITE)

