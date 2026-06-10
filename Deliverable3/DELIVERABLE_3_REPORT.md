# Deliverable 3 Report
## Advanced Shell Simulation: Memory Management and Process Synchronization

## 1. Overview
Deliverable 3 extends the existing shell with two core operating-system features:
1. Memory management via paging and page replacement.
2. Process synchronization via mutexes and semaphores.

The implementation is integrated into the same interactive shell used in Deliverables 1 and 2, so users can run memory and synchronization scenarios from shell commands.

## 2. Code Submission Contents
Implementation files added for Deliverable 3:
1. memory_management.py
2. process_synchronization.py
3. test_deliverable3.py
4. demo_deliverable3.py

Integration updates:
1. main.py (new built-in commands for memory and synchronization)
2. test_shell.py (help output assertion updated for new command sections)

## 3. Memory Management Design
### 3.1 Paging System
A PagingMemoryManager class simulates fixed-size physical memory frames:
1. Physical memory is represented as a frame table.
2. Each process is assigned a virtual page range via mem-alloc.
3. Page references are performed with mem-access.
4. If a referenced page is absent, a page fault occurs.

### 3.2 Page Replacement Algorithms
Two algorithms are implemented:
1. FIFO (First-In, First-Out)
   - Replaces the page with the oldest load time when memory is full.
2. LRU (Least Recently Used)
   - Replaces the page with the oldest access time when memory is full.

### 3.3 Memory Overflow and Fault Handling
When all frames are occupied and a fault occurs:
1. The configured replacement algorithm selects a victim frame.
2. The victim page is evicted.
3. The new page is loaded into the freed frame.

### 3.4 Tracked Metrics
The memory subsystem tracks:
1. Page faults
2. Page hits
3. Replacements
4. Fault rate
5. Used/free frame counts
6. Per-process memory usage

### 3.5 Shell Commands for Memory
1. mem-init [frames] [fifo|lru]
2. mem-alloc [pid] [pages]
3. mem-access [pid] [page]
4. mem-free [pid]
5. mem-status
6. mem-sim [algo] [frames] [ref_string]

## 4. Process Synchronization Design
### 4.1 Mutex-Based Shared Resource Protection
MutexCounterDemo uses threading.Lock to protect a shared counter:
1. Multiple threads increment the same counter.
2. Critical section entry is guarded by a mutex.
3. Final counter equals expected value, demonstrating race-condition prevention.

### 4.2 Classical Synchronization Problem: Producer-Consumer
ProducerConsumerDemo implements a bounded buffer using semaphores and a mutex:
1. empty semaphore controls available buffer slots.
2. full semaphore controls available items.
3. mutex protects buffer push/pop critical sections.

This ensures:
1. No simultaneous unsafe buffer access.
2. No buffer overflow or underflow.
3. No item loss/duplication in the simulation.

### 4.3 Shell Commands for Synchronization
1. mutex-demo [threads] [increments]
2. sync-pc [producers] [consumers] [items_per_producer] [buffer_size]

## 5. Demonstration and Screenshot Guide
Use these commands in shell for report screenshots:
1. Memory allocation/deallocation:
   - mem-init 4 fifo
   - mem-alloc 10 6
   - mem-access 10 0
   - mem-access 10 1
   - mem-free 10
   - mem-status
2. FIFO/LRU replacement and faults:
   - mem-sim fifo 3 0,1,2,0,3,0,4,2,3,0,3
   - mem-sim lru 3 0,1,2,0,3,0,4,2,3,0,3
3. Synchronization and classical problem:
   - mutex-demo 4 1000
   - sync-pc 2 2 5 4

## 6. Performance Discussion
### 6.1 Page Replacement Performance
On reference string 0,1,2,0,3,0,4,2,3,0,3 with 3 frames:
1. FIFO page faults: 9
2. LRU page faults: 8

For this workload, LRU performs better than FIFO by reducing faults.

### 6.2 Synchronization Correctness Metrics
1. Mutex demo confirms expected == actual counter value.
2. Producer-consumer confirms:
   - produced == consumed
   - final buffer size == 0
   - no item loss/duplication

## 7. Challenges and Improvements
### 7.1 Challenges
1. Integrating Deliverable 3 while preserving Deliverable 1/2 behavior.
2. Designing testable paging logic with deterministic replacement outcomes.
3. Balancing synchronization realism with concise shell-friendly output.

### 7.2 Solutions
1. Isolated new features into dedicated modules.
2. Added deterministic test scenarios and expected fault counts.
3. Added concise shell commands and sample event logs for screenshots.

### 7.3 Future Improvements
1. Add per-process working set statistics and thrashing detection.
2. Support additional page replacement algorithms (Clock, OPT simulation).
3. Add Dining Philosophers as a second classical synchronization scenario.
4. Add CSV export for experiment metrics.

## 8. Validation
Run the following validation commands:
1. py test_deliverable3.py
2. py test_shell.py
3. py test_process_management.py

Expected result: all tests pass.
