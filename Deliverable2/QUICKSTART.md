# Deliverable 2: Quick Start Guide

## Advanced Shell Simulation - Process Scheduling

This guide helps you quickly get started with Deliverable 2.

---

## Files Overview

### Core Implementation Files

| File | Purpose | Lines |
|------|---------|-------|
| `process_scheduler.py` | Scheduler module with RR and Priority-Based algorithms | 750+ |
| `main.py` | Extended shell with scheduling commands | 600+ |
| `demo_scheduler.py` | 7 different scheduling demonstrations | 500+ |
| `DELIVERABLE_2_REPORT.md` | Comprehensive technical report | 1000+ |

### Files from Deliverable 1 (Still Supported)

| File | Purpose |
|------|---------|
| `test_shell.py` | Test suite for shell commands |
| `test_process_management.py` | Process management tests |
| `demo_shell.py` | Original shell demo |

---

## Quick Start

### 1. Run the Shell

```bash
python main.py
```

You should see:
```
Advanced Shell Simulation (ASH) - Deliverable 2: Process Scheduling
Type 'help' for available commands or 'exit' to quit

ash:C:\path\to\dir$ 
```

### 2. Try Scheduling Commands

**Example 1: Round-Robin Scheduling**
```bash
ash:~$ schedule-rr 2 4
```

This runs Round-Robin with:
- Time quantum: 2 seconds
- Number of processes: 4

**Example 2: Priority-Based Scheduling**
```bash
ash:~$ schedule-pb 5
```

This runs Priority-Based with:
- Number of processes: 5
- With preemptive support

**Example 3: Algorithm Comparison**
```bash
ash:~$ compare-schedulers 4
```

This compares both algorithms on the same 4 processes and shows performance metrics.

### 3. View Help

```bash
ash:~$ help
```

Shows all available commands from Deliverable 1 and 2.

### 4. Run Demonstrations

```bash
python demo_scheduler.py
```

This launches interactive mode where you can select different demonstrations.

---

## Scheduling Commands Reference

### `schedule-rr [time_quantum] [process_count]`

**Purpose:** Execute Round-Robin scheduling algorithm

**Parameters:**
- `time_quantum`: Time slice for each process (default: 2.0 seconds)
- `process_count`: Number of processes to schedule (default: 4)

**Examples:**
```bash
schedule-rr 1 3      # 3 processes, 1 second time slice
schedule-rr 2 5      # 5 processes, 2 second time slice
schedule-rr 4 6      # 6 processes, 4 second time slice
```

**What You'll See:**
- Process information table
- Real-time execution log showing which process runs when
- Performance metrics (wait time, turnaround time, response time)
- Detailed process results

---

### `schedule-pb [process_count]`

**Purpose:** Execute Priority-Based (preemptive) scheduling algorithm

**Parameters:**
- `process_count`: Number of processes to schedule (default: 5)

**Examples:**
```bash
schedule-pb 3       # 3 processes with different priorities
schedule-pb 5       # 5 processes
schedule-pb 10      # 10 processes
```

**What You'll See:**
- Process information with priority levels
- Real-time execution log
- Preemption events marked with ⚡
- Performance metrics
- Detailed results

---

### `compare-schedulers [process_count]`

**Purpose:** Compare Round-Robin vs Priority-Based scheduling

**Parameters:**
- `process_count`: Number of processes (default: 5)

**Examples:**
```bash
compare-schedulers 3
compare-schedulers 5
compare-schedulers 8
```

**What You'll See:**
- Side-by-side comparison table
- Average wait time, turnaround time, response time
- CPU utilization comparison
- Analysis of which algorithm performs better

---

## Understanding the Output

### Process Information Table

```
Process Information:
────────────────────────────────────────────────────
PID   Name       Arrival    Burst      Priority
────────────────────────────────────────────────────
1     P1         0.0        2.0        0
2     P2         0.5        4.0        0
3     P3         1.0        6.0        0
────────────────────────────────────────────────────
```

- **PID**: Process ID
- **Name**: Process name (P1, P2, etc.)
- **Arrival**: Time when process arrives in ready queue
- **Burst**: Total CPU time needed
- **Priority**: Process priority (higher = more important)

### Execution Log

```
[  0.00s] Executing P1             | Remaining:   2.00s | Queue: 1
         └─ Process P1 COMPLETED
[ 2.00s] Executing P2             | Remaining:   4.00s | Queue: 1
```

- **Time**: Current time in simulation
- **Process**: Which process is running
- **Remaining**: CPU time still needed
- **Queue**: Processes waiting in ready queue

### Preemption Event

```
[ 2.50s] ⚡ PREEMPTION: P3 (priority 3) preempts P2 (priority 1)
```

Indicates a higher priority process interrupted lower priority process.

### Metrics Summary

```
╔════════════════════════════════════════════════════════════════╗
║              ROUND-ROBIN SCHEDULING METRICS                   ║
╚════════════════════════════════════════════════════════════════╝
Total Processes: 3
Total Time: 14.00s
Average Wait Time: 4.00s
Average Turnaround Time: 9.33s
Average Response Time: 0.67s
CPU Utilization: 100.00%
```

- **Total Processes**: Number of processes scheduled
- **Total Time**: Total simulation time
- **Average Wait Time**: Average time in ready queue
- **Average Turnaround Time**: Average time from arrival to completion
- **Average Response Time**: Average time to first execution
- **CPU Utilization**: Percentage of time CPU was active

### Detailed Process Results

```
PID   Name       Start      End        Wait       Turnaround     Response
────────────────────────────────────────────────────────────────────────
1     P1         0.00s      2.00s      0.00       2.00           0.00
2     P2         2.00s      8.00s      1.50       7.50           1.50
3     P3         4.00s      12.00s     3.00       11.00          3.00
```

Individual process performance data.

---

## Demonstrations

### Interactive Mode

```bash
$ python demo_scheduler.py
```

Menu:
```
Select a demo to run:
  1. Basic Round-Robin Scheduling
  2. Round-Robin with Staggered Arrivals
  3. Basic Priority-Based Scheduling
  4. Priority-Based with Preemption
  5. Algorithm Comparison
  6. Advanced Real-world Scenario
  7. Comprehensive Analysis
  8. Run All Demos
  9. Exit
```

### Demo Descriptions

1. **Basic Round-Robin**: Simple RR with 3 equal processes
2. **RR with Arrivals**: Shows how RR handles processes arriving at different times
3. **Basic Priority**: Simple priority scheduling
4. **PB Preemption**: Demonstrates preemption when high priority arrives
5. **Comparison**: Same process set with both algorithms
6. **Real-world**: Simulates system processes, daemons, and apps
7. **Analysis**: Comprehensive comparison of multiple scenarios
8. **All Demos**: Runs all demonstrations

---

## Common Tasks

### Task 1: Compare Time Quantum Effects

Run Round-Robin with different time quantums on same process set:

```bash
schedule-rr 1 4     # Fast switching
schedule-rr 2 4     # Medium switching
schedule-rr 4 4     # Slow switching
```

Compare the metrics - smaller quantum should have better response time but higher overhead.

### Task 2: Understand Preemption

Run Priority-Based and watch for preemption events:

```bash
schedule-pb 6
```

Look for ⚡ symbols in the output - these show when higher priority processes interrupt lower priority ones.

### Task 3: Compare Algorithms

See how different algorithms perform on same workload:

```bash
compare-schedulers 5
```

Check the analysis - which algorithm is better for your scenario?

### Task 4: Simulate Real System

Run the real-world scenario demo:

```bash
python demo_scheduler.py
# Select option 6
```

This simulates kernel processes, daemons, and applications.

---

## Troubleshooting

### Issue: "command not found" for schedule-rr

**Solution**: Make sure you're in the shell. Commands like `schedule-rr` only work inside the ASH shell:

```bash
$ python main.py
ash:~$ schedule-rr 2 4
```

### Issue: "cannot import process_scheduler"

**Solution**: Make sure `process_scheduler.py` is in the same directory as `main.py`:

```bash
C:\path\to\Deliverable2\
├── main.py
├── process_scheduler.py
└── demo_scheduler.py
```

### Issue: Slow execution

**Solution**: The simulation uses `time.sleep()` for accuracy. To speed up, edit `demo_scheduler.py` line with:
```python
time.sleep(execution_time * 0.01)  # Change multiplier to smaller value
```

### Issue: Can't run Python files

**Solution**: Ensure Python 3.8+ is installed:

```bash
python --version     # or python3 --version
```

If not installed, download from python.org

---

## Performance Expectations

### Typical Execution Times (Wall Clock)

- `schedule-rr 2 3`: ~2-3 seconds
- `schedule-pb 4`: ~3-4 seconds
- `compare-schedulers 4`: ~8-10 seconds
- `demo_scheduler.py --batch`: ~60 seconds total

Times vary based on system performance and time quantum values.

### Memory Usage

- Base shell: ~10-20 MB
- During scheduling: ~20-50 MB (temporary)
- After completion: Returns to base

---

## Next Steps

1. **Read the Report**: See [DELIVERABLE_2_REPORT.md](DELIVERABLE_2_REPORT.md) for detailed technical information
2. **Explore Different Scenarios**: Try various process counts and time quantums
3. **Compare Algorithms**: Run `compare-schedulers` multiple times with different parameters
4. **Understand Metrics**: Learn what wait time, turnaround time, and response time mean
5. **Run Demonstrations**: Use `demo_scheduler.py` to see real-world scenarios
6. **Prepare for Deliverable 3**: Memory management and synchronization

---

## Support

For detailed technical information:
- See [DELIVERABLE_2_REPORT.md](DELIVERABLE_2_REPORT.md)
- Review inline code comments in `process_scheduler.py`
- Check `test_scheduler.py` for additional examples

For issues:
- Check the troubleshooting section above
- Review the code comments
- Verify Python 3.8+ is installed
- Ensure all files are in the correct directory

---

**Deliverable 2 Complete!** ✓

Ready to test. Use the commands above to explore process scheduling.
