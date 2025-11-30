# Color Coding Guide

This implementation uses ANSI color codes to make the output more readable and easier to follow.

## Message Type Colors

| Message Type | Color   | Description                                    |
|--------------|---------|------------------------------------------------|
| PREPARE      | Cyan    | Phase 1: Proposer asking for promises         |
| PROMISE      | Blue    | Phase 1: Acceptor promising to a proposal     |
| ACCEPT       | Yellow  | Phase 2: Proposer asking to accept a value    |
| ACCEPTED     | Green   | Phase 2: Acceptor accepting a value           |
| NACK         | Red     | Rejection of a proposal                        |

## Status Indicators

| Indicator | Color   | Meaning                                        |
|-----------|---------|------------------------------------------------|
| [OK]      | Green   | Success, acceptance, or positive acknowledgment|
| [X]       | Red     | Rejection, failure, or negative response       |
| ***       | Magenta | Consensus reached (bold)                       |

## Message Direction

| Symbol | Meaning                    |
|--------|----------------------------|
| ->     | Sending a message          |
| <-     | Receiving a message        |

## Example Color-Coded Output Flow

1. **Cyan**: Node 0 sends PREPARE -> to all acceptors
2. **Blue**: Acceptors send PROMISE <- back to Node 0
3. **Green**: Node 0 shows [OK] - received majority promises
4. **Yellow**: Node 0 sends ACCEPT -> to all acceptors
5. **Green**: Acceptors send ACCEPTED <- back to Node 0
6. **Magenta (Bold)**: *** CONSENSUS REACHED: VALUE ***

## Tips

- If messages appear without colors, your terminal may not support ANSI codes
- Most modern terminals (Linux, macOS, Windows 10+) support colors by default
- Colors make it easy to distinguish between different phases and message types at a glance

