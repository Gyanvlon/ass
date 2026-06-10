#!/usr/bin/env python3
"""
Process Scheduling Module for Advanced Shell Simulation
Implements Round-Robin and Priority-Based Scheduling algorithms

This module simulates how an operating system manages process scheduling,
allowing multiple processes to share CPU time according to different algorithms.
"""

import time
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass, field
from enum import Enum
import heapq
from datetime import datetime


class ProcessState(Enum):
    """Enum for process states"""
    NEW = "NEW"
    READY = "READY"
    RUNNING = "RUNNING"
    WAITING = "WAITING"
    COMPLETED = "COMPLETED"


class SchedulingAlgorithm(Enum):
    """Enum for scheduling algorithms"""
    ROUND_ROBIN = "Round-Robin"
    PRIORITY_BASED = "Priority-Based"


@dataclass
class Process:
    """Represents a process in the scheduler"""
    pid: int  # Process ID
    name: str  # Process name
    arrival_time: float  # When process arrives in ready queue
    burst_time: float  # Total CPU time needed
    priority: int = 0  # Priority (higher number = higher priority)
    
    # Tracking metrics
    state: ProcessState = ProcessState.NEW
    start_time: Optional[float] = None
    end_time: Optional[float] = None
    remaining_time: float = field(init=False)
    wait_time: float = 0.0
    turnaround_time: float = 0.0
    response_time: Optional[float] = None
    
    def __post_init__(self):
        """Initialize remaining time after object creation"""
        self.remaining_time = self.burst_time
    
    def __lt__(self, other):
        """Comparison for priority queue (min-heap by priority, then by arrival time)"""
        if self.priority != other.priority:
            return self.priority > other.priority  # Higher priority first (reverse order)
        return self.arrival_time < other.arrival_time
    
    def __str__(self) -> str:
        """String representation of process"""
        return f"P{self.pid}({self.name})"
    
    def get_detailed_info(self) -> str:
        """Get detailed information about the process"""
        return f"""
Process ID: {self.pid}
Name: {self.name}
State: {self.state.value}
Burst Time: {self.burst_time:.2f}s
Remaining Time: {self.remaining_time:.2f}s
Arrival Time: {self.arrival_time:.2f}s
Start Time: {self.start_time:.2f}s if self.start_time else 'Not started'
End Time: {self.end_time:.2f}s if self.end_time else 'Not completed'
Wait Time: {self.wait_time:.2f}s
Turnaround Time: {self.turnaround_time:.2f}s
Response Time: {self.response_time:.2f}s if self.response_time else 'Not started'
Priority: {self.priority}
"""


@dataclass
class SchedulingMetrics:
    """Stores scheduling performance metrics"""
    algorithm: str
    total_processes: int
    total_time: float = 0.0
    average_wait_time: float = 0.0
    average_turnaround_time: float = 0.0
    average_response_time: float = 0.0
    cpu_utilization: float = 0.0
    processes: List[Process] = field(default_factory=list)
    
    def __str__(self) -> str:
        """String representation of metrics"""
        return f"""
╔════════════════════════════════════════════════════════════════╗
║              {self.algorithm} SCHEDULING METRICS                 ║
╚════════════════════════════════════════════════════════════════╝
Total Processes: {self.total_processes}
Total Time: {self.total_time:.2f}s
Average Wait Time: {self.average_wait_time:.2f}s
Average Turnaround Time: {self.average_turnaround_time:.2f}s
Average Response Time: {self.average_response_time:.2f}s
CPU Utilization: {self.cpu_utilization:.2f}%
"""


class RoundRobinScheduler:
    """
    Round-Robin (RR) Scheduling Algorithm
    
    Each process is assigned a fixed time slice (quantum).
    Processes are executed in a circular queue, and after their time slice
    expires, they go to the back of the queue (if not completed).
    """
    
    def __init__(self, time_quantum: float = 2.0, verbose: bool = True):
        """
        Initialize Round-Robin Scheduler
        
        Args:
            time_quantum: Time slice for each process (in seconds)
            verbose: Whether to print execution details
        """
        self.time_quantum = time_quantum
        self.verbose = verbose
        self.ready_queue: List[Process] = []
        self.completed_processes: List[Process] = []
        self.current_time = 0.0
        self.execution_log: List[str] = []
    
    def add_process(self, process: Process) -> None:
        """Add a process to the ready queue"""
        process.state = ProcessState.READY
        self.ready_queue.append(process)
    
    def execute(self, processes: List[Process]) -> SchedulingMetrics:
        """
        Execute scheduling algorithm on given processes
        
        Args:
            processes: List of processes to schedule
            
        Returns:
            SchedulingMetrics with performance analysis
        """
        self.ready_queue = []
        self.completed_processes = []
        self.current_time = 0.0
        self.execution_log = []
        
        # Sort by arrival time
        processes_sorted = sorted(processes, key=lambda p: p.arrival_time)
        
        # Add first process(es) that arrive at time 0
        for process in processes_sorted:
            if process.arrival_time <= 0.0:
                self.add_process(process)
        
        process_idx = 0
        
        if self.verbose:
            print(f"\n{'='*70}")
            print(f"ROUND-ROBIN SCHEDULER (Time Quantum: {self.time_quantum}s)")
            print(f"{'='*70}\n")
        
        while self.ready_queue or process_idx < len(processes_sorted):
            # Add newly arrived processes
            while process_idx < len(processes_sorted):
                if processes_sorted[process_idx].arrival_time <= self.current_time:
                    self.add_process(processes_sorted[process_idx])
                    process_idx += 1
                else:
                    break
            
            if not self.ready_queue:
                if process_idx < len(processes_sorted):
                    # Jump to next arrival time
                    self.current_time = processes_sorted[process_idx].arrival_time
                    continue
                else:
                    break
            
            # Get next process from queue
            current_process = self.ready_queue.pop(0)
            
            # Set response time on first execution
            if current_process.response_time is None:
                current_process.response_time = self.current_time - current_process.arrival_time
            
            # Set start time if first execution
            if current_process.start_time is None:
                current_process.start_time = self.current_time
            
            # Execute for time quantum or until completion
            execution_time = min(self.time_quantum, current_process.remaining_time)
            
            log_msg = f"[{self.current_time:.2f}s] Executing {current_process} for {execution_time:.2f}s"
            self.execution_log.append(log_msg)
            
            if self.verbose:
                print(f"[{self.current_time:6.2f}s] Executing {current_process:15} | Remaining: {current_process.remaining_time:6.2f}s | Queue: {len(self.ready_queue)}")
            
            # Simulate execution
            time.sleep(execution_time * 0.01)  # Scale down for simulation
            
            current_process.remaining_time -= execution_time
            self.current_time += execution_time
            
            # Check if process is completed
            if current_process.remaining_time <= 0:
                current_process.state = ProcessState.COMPLETED
                current_process.end_time = self.current_time
                current_process.turnaround_time = current_process.end_time - current_process.arrival_time
                current_process.wait_time = current_process.turnaround_time - current_process.burst_time
                self.completed_processes.append(current_process)
                
                if self.verbose:
                    print(f"         └─ Process {current_process} COMPLETED")
            else:
                # Process not completed, send back to queue
                current_process.state = ProcessState.READY
                self.ready_queue.append(current_process)
        
        # Calculate metrics
        return self._calculate_metrics()
    
    def _calculate_metrics(self) -> SchedulingMetrics:
        """Calculate scheduling performance metrics"""
        if not self.completed_processes:
            return SchedulingMetrics(
                algorithm=SchedulingAlgorithm.ROUND_ROBIN.value,
                total_processes=0,
                total_time=0.0
            )
        
        total_wait_time = sum(p.wait_time for p in self.completed_processes)
        total_turnaround_time = sum(p.turnaround_time for p in self.completed_processes)
        total_response_time = sum(p.response_time for p in self.completed_processes if p.response_time)
        
        num_processes = len(self.completed_processes)
        burst_time_total = sum(p.burst_time for p in self.completed_processes)
        
        return SchedulingMetrics(
            algorithm=SchedulingAlgorithm.ROUND_ROBIN.value,
            total_processes=num_processes,
            total_time=self.current_time,
            average_wait_time=total_wait_time / num_processes if num_processes > 0 else 0.0,
            average_turnaround_time=total_turnaround_time / num_processes if num_processes > 0 else 0.0,
            average_response_time=total_response_time / num_processes if num_processes > 0 else 0.0,
            cpu_utilization=(burst_time_total / self.current_time * 100) if self.current_time > 0 else 0.0,
            processes=self.completed_processes
        )


class PriorityBasedScheduler:
    """
    Priority-Based Scheduling Algorithm
    
    Process with highest priority is executed first.
    If a higher-priority process arrives while a lower-priority process is running,
    the scheduler preempts the lower-priority process.
    """
    
    def __init__(self, verbose: bool = True, preemptive: bool = True):
        """
        Initialize Priority-Based Scheduler
        
        Args:
            verbose: Whether to print execution details
            preemptive: Whether to allow preemption of lower-priority processes
        """
        self.verbose = verbose
        self.preemptive = preemptive
        self.ready_queue: List[Process] = []
        self.completed_processes: List[Process] = []
        self.current_time = 0.0
        self.execution_log: List[str] = []
    
    def add_process(self, process: Process) -> None:
        """Add a process to the priority queue"""
        process.state = ProcessState.READY
        heapq.heappush(self.ready_queue, process)
    
    def execute(self, processes: List[Process]) -> SchedulingMetrics:
        """
        Execute scheduling algorithm on given processes
        
        Args:
            processes: List of processes to schedule
            
        Returns:
            SchedulingMetrics with performance analysis
        """
        self.ready_queue = []
        self.completed_processes = []
        self.current_time = 0.0
        self.execution_log = []
        
        # Sort by arrival time
        processes_sorted = sorted(processes, key=lambda p: p.arrival_time)
        
        # Add first process(es) that arrive at time 0
        for process in processes_sorted:
            if process.arrival_time <= 0.0:
                self.add_process(process)
        
        process_idx = 0
        current_process: Optional[Process] = None
        
        if self.verbose:
            print(f"\n{'='*70}")
            print(f"PRIORITY-BASED SCHEDULER (Preemptive: {self.preemptive})")
            print(f"{'='*70}\n")
        
        while self.ready_queue or process_idx < len(processes_sorted) or current_process:
            # Add newly arrived processes
            while process_idx < len(processes_sorted):
                if processes_sorted[process_idx].arrival_time <= self.current_time:
                    arriving_process = processes_sorted[process_idx]
                    self.add_process(arriving_process)
                    
                    # Check for preemption
                    if self.preemptive and current_process and arriving_process.priority > current_process.priority:
                        if self.verbose:
                            print(f"[{self.current_time:6.2f}s] ⚡ PREEMPTION: {arriving_process} (priority {arriving_process.priority}) preempts {current_process} (priority {current_process.priority})")
                        current_process.state = ProcessState.READY
                        heapq.heappush(self.ready_queue, current_process)
                        current_process = None
                    
                    process_idx += 1
                else:
                    break
            
            # If no process is currently running, get next from queue
            if not current_process:
                if not self.ready_queue:
                    if process_idx < len(processes_sorted):
                        # Jump to next arrival time
                        self.current_time = processes_sorted[process_idx].arrival_time
                        continue
                    else:
                        break
                
                current_process = heapq.heappop(self.ready_queue)
                
                # Set response time on first execution
                if current_process.response_time is None:
                    current_process.response_time = self.current_time - current_process.arrival_time
                
                # Set start time if first execution
                if current_process.start_time is None:
                    current_process.start_time = self.current_time
                
                current_process.state = ProcessState.RUNNING
            
            # Execute for small time unit (0.5 seconds)
            execution_time = 0.5
            if current_process.remaining_time < execution_time:
                execution_time = current_process.remaining_time
            
            log_msg = f"[{self.current_time:.2f}s] Executing {current_process} for {execution_time:.2f}s"
            self.execution_log.append(log_msg)
            
            if self.verbose:
                print(f"[{self.current_time:6.2f}s] Executing {current_process:15} | Priority: {current_process.priority:2} | Remaining: {current_process.remaining_time:6.2f}s | Queue: {len(self.ready_queue)}")
            
            # Simulate execution
            time.sleep(execution_time * 0.01)
            
            current_process.remaining_time -= execution_time
            self.current_time += execution_time
            
            # Check if process is completed
            if current_process.remaining_time <= 0:
                current_process.state = ProcessState.COMPLETED
                current_process.end_time = self.current_time
                current_process.turnaround_time = current_process.end_time - current_process.arrival_time
                current_process.wait_time = current_process.turnaround_time - current_process.burst_time
                self.completed_processes.append(current_process)
                
                if self.verbose:
                    print(f"         └─ Process {current_process} COMPLETED")
                
                current_process = None
        
        # Calculate metrics
        return self._calculate_metrics()
    
    def _calculate_metrics(self) -> SchedulingMetrics:
        """Calculate scheduling performance metrics"""
        if not self.completed_processes:
            return SchedulingMetrics(
                algorithm=SchedulingAlgorithm.PRIORITY_BASED.value,
                total_processes=0,
                total_time=0.0
            )
        
        total_wait_time = sum(p.wait_time for p in self.completed_processes)
        total_turnaround_time = sum(p.turnaround_time for p in self.completed_processes)
        total_response_time = sum(p.response_time for p in self.completed_processes if p.response_time)
        
        num_processes = len(self.completed_processes)
        burst_time_total = sum(p.burst_time for p in self.completed_processes)
        
        return SchedulingMetrics(
            algorithm=SchedulingAlgorithm.PRIORITY_BASED.value,
            total_processes=num_processes,
            total_time=self.current_time,
            average_wait_time=total_wait_time / num_processes if num_processes > 0 else 0.0,
            average_turnaround_time=total_turnaround_time / num_processes if num_processes > 0 else 0.0,
            average_response_time=total_response_time / num_processes if num_processes > 0 else 0.0,
            cpu_utilization=(burst_time_total / self.current_time * 100) if self.current_time > 0 else 0.0,
            processes=self.completed_processes
        )


class SchedulerComparison:
    """Utility class to compare scheduling algorithms"""
    
    @staticmethod
    def generate_gantt_chart(metrics: SchedulingMetrics) -> str:
        """Generate ASCII Gantt chart from scheduling metrics"""
        if not metrics.processes:
            return "No processes to display"
        
        chart = "\nGantt Chart:\n"
        chart += "┌" + "─" * 70 + "┐\n"
        
        # Create timeline
        for process in sorted(metrics.processes, key=lambda p: p.start_time if p.start_time else 0):
            if process.start_time is None:
                continue
            
            bar_length = int((process.end_time - process.start_time) * 5) if process.end_time else 0
            start_pos = int(process.start_time * 5)
            
            bar = "│" + " " * start_pos + f"[{process.name}]" + "─" * max(0, bar_length - len(process.name) - 2) + " " * max(0, 70 - start_pos - bar_length) + "│"
            chart += bar + "\n"
        
        chart += "└" + "─" * 70 + "┘\n"
        
        return chart
    
    @staticmethod
    def compare_algorithms(processes: List[Process]) -> None:
        """Compare RR and Priority-Based scheduling"""
        print("\n" + "="*70)
        print("SCHEDULING ALGORITHM COMPARISON")
        print("="*70 + "\n")
        
        # Deep copy processes for each algorithm
        import copy
        
        # Round-Robin
        rr_processes = copy.deepcopy(processes)
        rr_scheduler = RoundRobinScheduler(time_quantum=2.0, verbose=False)
        rr_metrics = rr_scheduler.execute(rr_processes)
        
        # Priority-Based
        pb_processes = copy.deepcopy(processes)
        pb_scheduler = PriorityBasedScheduler(verbose=False)
        pb_metrics = pb_scheduler.execute(pb_processes)
        
        # Display results
        print(rr_metrics)
        print(pb_metrics)
        
        # Comparison table
        print("\n" + "─"*70)
        print(f"{'Metric':<30} {'Round-Robin':<20} {'Priority-Based':<20}")
        print("─"*70)
        print(f"{'Average Wait Time':<30} {rr_metrics.average_wait_time:<20.2f} {pb_metrics.average_wait_time:<20.2f}")
        print(f"{'Average Turnaround Time':<30} {rr_metrics.average_turnaround_time:<20.2f} {pb_metrics.average_turnaround_time:<20.2f}")
        print(f"{'Average Response Time':<30} {rr_metrics.average_response_time:<20.2f} {pb_metrics.average_response_time:<20.2f}")
        print(f"{'CPU Utilization':<30} {rr_metrics.cpu_utilization:<19.2f}% {pb_metrics.cpu_utilization:<19.2f}%")
        print("─"*70)
