# Deliverable 2: Testing Guide

## Comprehensive Test Suite for Process Scheduling

This document provides step-by-step testing procedures for Deliverable 2.

---

## Table of Contents

1. [Pre-Test Checklist](#pre-test-checklist)
2. [Unit Tests](#unit-tests)
3. [Integration Tests](#integration-tests)
4. [Performance Tests](#performance-tests)
5. [Demonstration Tests](#demonstration-tests)
6. [Comparison Tests](#comparison-tests)
7. [Edge Case Tests](#edge-case-tests)
8. [Expected Results](#expected-results)

---

## Pre-Test Checklist

Before running tests, verify:

- [ ] Python 3.8 or higher installed
- [ ] All files present:
  - [ ] `main.py`
  - [ ] `process_scheduler.py`
  - [ ] `demo_scheduler.py`
  - [ ] `DELIVERABLE_2_REPORT.md`
  - [ ] `QUICKSTART.md`
- [ ] Working directory: `C:\Users\gyan\Desktop\edu\ass\Deliverable2\`
- [ ] No syntax errors in Python files

**Verify Setup:**
```bash
python --version
dir *.py
```

---

## Unit Tests

### Test 1.1: Process Class Initialization

**Objective**: Verify Process dataclass creates correctly

**Manual Test**:
```python
# Create test script: test_process.py
from process_scheduler import Process, ProcessState

p = Process(pid=1, name="P1", arrival_time=0, burst_time=5, priority=1)

assert p.pid == 1
assert p.name == "P1"
assert p.arrival_time == 0
assert p.burst_time == 5
assert p.priority == 1
assert p.remaining_time == 5
assert p.state == ProcessState.NEW
print("✓ Process initialization test passed")
```

**Expected Output**: 
```
✓ Process initialization test passed
```

---

### Test 1.2: Round-Robin Scheduler Initialization

**Objective**: Verify RR scheduler initializes correctly

**Manual Test**:
```python
from process_scheduler import RoundRobinScheduler

scheduler = RoundRobinScheduler(time_quantum=2.0, verbose=False)

assert scheduler.time_quantum == 2.0
assert scheduler.ready_queue == []
assert scheduler.completed_processes == []
assert scheduler.current_time == 0.0
print("✓ RR scheduler initialization test passed")
```

**Expected Output**: 
```
✓ RR scheduler initialization test passed
```

---

### Test 1.3: Priority-Based Scheduler Initialization

**Objective**: Verify PB scheduler initializes correctly

**Manual Test**:
```python
from process_scheduler import PriorityBasedScheduler

scheduler = PriorityBasedScheduler(verbose=False, preemptive=True)

assert scheduler.preemptive == True
assert scheduler.ready_queue == []
assert scheduler.completed_processes == []
assert scheduler.current_time == 0.0
print("✓ PB scheduler initialization test passed")
```

**Expected Output**: 
```
✓ PB scheduler initialization test passed
```

---

### Test 1.4: Process Priority Comparison

**Objective**: Verify process comparison works for heap operations

**Manual Test**:
```python
from process_scheduler import Process

p1 = Process(pid=1, name="P1", arrival_time=0, burst_time=5, priority=2)
p2 = Process(pid=2, name="P2", arrival_time=0, burst_time=5, priority=3)

# Higher priority (3) should be "less than" (execute first)
assert p2 < p1  # p2 has priority 3 > p1's priority 2
print("✓ Process priority comparison test passed")
```

**Expected Output**: 
```
✓ Process priority comparison test passed
```

---

## Integration Tests

### Test 2.1: Round-Robin with Single Process

**Objective**: Verify RR scheduling works with single process

**Manual Test**:
```python
from process_scheduler import Process, RoundRobinScheduler

processes = [
    Process(pid=1, name="P1", arrival_time=0, burst_time=5, priority=0)
]

scheduler = RoundRobinScheduler(time_quantum=2.0, verbose=False)
metrics = scheduler.execute(processes)

assert len(metrics.processes) == 1
assert metrics.total_processes == 1
assert metrics.processes[0].turnaround_time == 5.0
assert metrics.processes[0].wait_time == 0.0
print("✓ Single process RR test passed")
```

**Expected Output**: 
```
✓ Single process RR test passed
```

---

### Test 2.2: Round-Robin with Multiple Processes

**Objective**: Verify RR correctly distributes CPU time

**Manual Test**:
```python
from process_scheduler import Process, RoundRobinScheduler

processes = [
    Process(pid=1, name="P1", arrival_time=0, burst_time=4, priority=0),
    Process(pid=2, name="P2", arrival_time=0, burst_time=4, priority=0),
]

scheduler = RoundRobinScheduler(time_quantum=2.0, verbose=False)
metrics = scheduler.execute(processes)

assert len(metrics.processes) == 2
assert all(p.state.value == "COMPLETED" for p in metrics.processes)
assert metrics.total_time > 0
print("✓ Multiple process RR test passed")
```

**Expected Output**: 
```
✓ Multiple process RR test passed
```

---

### Test 2.3: Priority-Based with Different Priorities

**Objective**: Verify PB executes higher priority first

**Manual Test**:
```python
from process_scheduler import Process, PriorityBasedScheduler

processes = [
    Process(pid=1, name="P1", arrival_time=0, burst_time=3, priority=1),  # Low priority
    Process(pid=2, name="P2", arrival_time=0, burst_time=3, priority=3),  # High priority
]

scheduler = PriorityBasedScheduler(verbose=False, preemptive=False)
metrics = scheduler.execute(processes)

# P2 (higher priority) should start first
p2 = [p for p in metrics.processes if p.pid == 2][0]
p1 = [p for p in metrics.processes if p.pid == 1][0]

assert p2.start_time < p1.start_time
print("✓ Priority-based scheduling test passed")
```

**Expected Output**: 
```
✓ Priority-based scheduling test passed
```

---

### Test 2.4: Metrics Calculation

**Objective**: Verify metrics are calculated correctly

**Manual Test**:
```python
from process_scheduler import Process, RoundRobinScheduler

processes = [
    Process(pid=1, name="P1", arrival_time=0, burst_time=2, priority=0),
    Process(pid=2, name="P2", arrival_time=0, burst_time=2, priority=0),
]

scheduler = RoundRobinScheduler(time_quantum=2.0, verbose=False)
metrics = scheduler.execute(processes)

# Verify metrics are non-zero
assert metrics.average_wait_time >= 0
assert metrics.average_turnaround_time > 0
assert metrics.average_response_time >= 0
assert metrics.cpu_utilization > 0
print("✓ Metrics calculation test passed")
```

**Expected Output**: 
```
✓ Metrics calculation test passed
```

---

## Performance Tests

### Test 3.1: Execution Time Efficiency

**Objective**: Verify scheduling completes in reasonable time

**Test**:
```bash
# In shell:
time schedule-rr 2 5
```

**Expected**: Completes in < 10 seconds

---

### Test 3.2: Scalability - Many Processes

**Objective**: Verify scheduler handles many processes

**Test**:
```bash
# In shell:
schedule-rr 2 20    # 20 processes
```

**Expected**: Executes successfully with all metrics displayed

---

### Test 3.3: Memory Usage

**Objective**: Verify no memory leaks

**Test**:
```bash
# Run multiple times
schedule-rr 2 10
schedule-pb 10
compare-schedulers 10
# (Repeat several times)
```

**Expected**: Memory usage remains stable

---

## Demonstration Tests

### Test 4.1: Shell Integration - RR Command

**Objective**: Verify `schedule-rr` command works from shell

**Steps**:
1. Run: `python main.py`
2. At prompt, type: `schedule-rr 2 3`
3. Verify output displays process information and metrics

**Expected Output**:
```
======================================================================
ROUND-ROBIN SCHEDULING DEMO
Time Quantum: 2.0s, Processes: 3
======================================================================
Process Information:
...
[Execution log]
...
╔════════════════════════════════════════════════════════════════╗
║              ROUND-ROBIN SCHEDULING METRICS                   ║
...
```

---

### Test 4.2: Shell Integration - PB Command

**Objective**: Verify `schedule-pb` command works from shell

**Steps**:
1. In shell, type: `schedule-pb 4`
2. Verify output includes priority information and preemption events

**Expected Output**: Similar to RR but with priority levels and preemption markers (⚡)

---

### Test 4.3: Shell Integration - Comparison

**Objective**: Verify `compare-schedulers` command works

**Steps**:
1. In shell, type: `compare-schedulers 3`
2. Verify comparison table is displayed

**Expected Output**:
```
Comparison Results:
────────────────────────────────────────────────────────────────
Metric                         Round-Robin                 Priority-Based
...
```

---

### Test 4.4: Demo Script - Interactive Mode

**Objective**: Verify demo script interactive menu works

**Steps**:
1. Run: `python demo_scheduler.py`
2. Select each demo (1-7)
3. Verify each runs without errors

**Expected**: All demonstrations complete successfully

---

### Test 4.5: Demo Script - Batch Mode

**Objective**: Verify demo script batch mode

**Steps**:
1. Run: `python demo_scheduler.py --batch`
2. Allow all demos to run (or press Enter to skip)

**Expected**: All 7 demos run successfully

---

## Comparison Tests

### Test 5.1: Same Algorithm, Different Parameters

**Objective**: Verify results differ based on parameters

**Steps**:
```bash
schedule-rr 1 4    # Small quantum
schedule-rr 2 4    # Medium quantum
schedule-rr 4 4    # Large quantum
```

**Expected**: 
- Smaller quantum: Better response time, higher total time
- Larger quantum: Worse response time, lower total time

---

### Test 5.2: Algorithm Performance Comparison

**Objective**: Verify priority-based performs better for high priority

**Steps**:
```bash
compare-schedulers 4
```

**Expected**: 
- Check analysis output
- Priority-Based should have lower wait time for high priority processes

---

### Test 5.3: Different Process Counts

**Objective**: Verify scheduling works with various counts

**Steps**:
```bash
schedule-rr 2 2     # 2 processes
schedule-rr 2 5     # 5 processes
schedule-rr 2 10    # 10 processes
```

**Expected**: All execute successfully with appropriate metrics

---

## Edge Case Tests

### Test 6.1: Single Process

**Test**:
```bash
schedule-rr 2 1
```

**Expected**: 
- Process completes with wait time = 0
- Turnaround time = burst time

---

### Test 6.2: All Same Priority

**Test**:
```bash
schedule-pb 3     # All have different descending priorities
```

**Expected**: Processes execute in priority order

---

### Test 6.3: Very Short Quantum

**Test**:
```bash
schedule-rr 0.5 4
```

**Expected**: Many context switches, short execution times visible

---

### Test 6.4: Very Long Quantum

**Test**:
```bash
schedule-rr 10 4
```

**Expected**: Fewer context switches, longer individual execution times

---

### Test 6.5: Staggered Arrivals

**Test**:
Run demo 2 (Round-Robin with Staggered Arrivals)

**Expected**: Processes arrive at different times, scheduler adapts

---

### Test 6.6: Process Preemption

**Test**:
Run demo 4 (Priority-Based with Preemption)

**Expected**: See ⚡ preemption symbols in output

---

## Expected Results

### Round-Robin Execution Example

Input: `schedule-rr 2 3`

Expected metrics range:
- Average Wait Time: 2.0 - 5.0 seconds
- Average Turnaround Time: 6.0 - 10.0 seconds
- Average Response Time: 0.0 - 2.0 seconds
- CPU Utilization: 90-100%

### Priority-Based Execution Example

Input: `schedule-pb 4`

Expected metrics range:
- Average Wait Time: 1.0 - 4.0 seconds
- Average Turnaround Time: 5.0 - 9.0 seconds
- Average Response Time: 0.0 - 1.0 seconds
- CPU Utilization: 90-100%

### Comparison Output Example

```
Comparison Results:
────────────────────────────────────────────────────
Metric                 Round-Robin    Priority-Based
────────────────────────────────────────────────────
Average Wait Time            4.50            3.25
Average Turnaround Time      10.50           9.25
Average Response Time        1.50            0.75
CPU Utilization              100.00%         100.00%
────────────────────────────────────────────────────
```

---

## Test Results Summary

### Manual Testing Checklist

- [ ] **Unit Tests**: All Process and Scheduler classes initialize correctly
- [ ] **Integration Tests**: Single and multiple process scheduling works
- [ ] **Performance Tests**: Scheduling completes in reasonable time
- [ ] **Shell Commands**: RR, PB, and comparison commands work
- [ ] **Demonstrations**: All 7 demos run successfully
- [ ] **Edge Cases**: Single process, various quantums, staggered arrivals all work
- [ ] **Comparison**: Algorithm comparison produces valid results

### Issues Found & Resolution

Document any issues found during testing:

| Issue | Expected | Actual | Resolution |
|-------|----------|--------|------------|
| Example | Process completes | Process crashes | See log |

---

## Advanced Testing

### Performance Profiling

```python
import time
from process_scheduler import Process, RoundRobinScheduler

processes = [Process(i, f"P{i}", 0, i*2, 0) for i in range(1, 11)]

start = time.time()
scheduler = RoundRobinScheduler(verbose=False)
metrics = scheduler.execute(processes)
elapsed = time.time() - start

print(f"Time for 10 processes: {elapsed:.3f}s")
print(f"Metrics: Wait={metrics.average_wait_time:.2f}, TAT={metrics.average_turnaround_time:.2f}")
```

### Memory Profiling

```python
import tracemalloc
from process_scheduler import Process, RoundRobinScheduler

tracemalloc.start()

processes = [Process(i, f"P{i}", 0, i*2, 0) for i in range(1, 101)]
scheduler = RoundRobinScheduler(verbose=False)
metrics = scheduler.execute(processes)

current, peak = tracemalloc.get_traced_memory()
print(f"Current memory: {current / 1024:.2f} KB")
print(f"Peak memory: {peak / 1024:.2f} KB")
```

---

## Conclusion

All tests should pass for Deliverable 2 to be considered complete. Use this testing guide to validate:
1. Core functionality works
2. Integration is seamless
3. Performance is acceptable
4. Edge cases are handled
5. Output is correctly formatted

**Test Status**: ✓ Ready for comprehensive testing

---

**Document Version**: 1.0  
**Last Updated**: December 2024
