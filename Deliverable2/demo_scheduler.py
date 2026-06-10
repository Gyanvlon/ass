#!/usr/bin/env python3
"""
Scheduling Algorithm Demonstration for Advanced Shell Simulation
Deliverable 2: Process Scheduling

This script demonstrates:
1. Round-Robin Scheduling with different time quantums
2. Priority-Based Scheduling with preemption
3. Performance comparison between algorithms
4. Visual representation of process execution
"""

import sys
import os
from process_scheduler import (
    Process, RoundRobinScheduler, PriorityBasedScheduler,
    SchedulerComparison, SchedulingMetrics
)
from datetime import datetime


def print_header():
    """Print application header"""
    print("\n" + "="*70)
    print("   ADVANCED SHELL SIMULATION - PROCESS SCHEDULING DEMO")
    print("   Deliverable 2: Round-Robin and Priority-Based Scheduling")
    print("="*70 + "\n")


def demo_round_robin_basic():
    """Demo 1: Basic Round-Robin scheduling with different time quantums"""
    print("\n" + "█"*70)
    print("DEMO 1: Basic Round-Robin Scheduling")
    print("█"*70)
    
    # Create sample processes
    processes = [
        Process(pid=1, name="P1", arrival_time=0, burst_time=5, priority=0),
        Process(pid=2, name="P2", arrival_time=0, burst_time=3, priority=0),
        Process(pid=3, name="P3", arrival_time=0, burst_time=4, priority=0),
    ]
    
    # Test with different time quantums
    for quantum in [1, 2, 4]:
        import copy
        test_processes = copy.deepcopy(processes)
        
        print(f"\n{'─'*70}")
        print(f"Time Quantum: {quantum}s")
        print(f"{'─'*70}")
        
        scheduler = RoundRobinScheduler(time_quantum=quantum, verbose=True)
        metrics = scheduler.execute(test_processes)
        
        print("\n" + str(metrics))


def demo_round_robin_arrival():
    """Demo 2: Round-Robin with staggered process arrivals"""
    print("\n" + "█"*70)
    print("DEMO 2: Round-Robin with Staggered Arrivals")
    print("█"*70)
    
    processes = [
        Process(pid=1, name="P1", arrival_time=0, burst_time=8, priority=0),
        Process(pid=2, name="P2", arrival_time=1, burst_time=4, priority=0),
        Process(pid=3, name="P3", arrival_time=2, burst_time=2, priority=0),
        Process(pid=4, name="P4", arrival_time=3, burst_time=3, priority=0),
    ]
    
    scheduler = RoundRobinScheduler(time_quantum=2, verbose=True)
    metrics = scheduler.execute(processes)
    
    print("\n" + str(metrics))
    print("\nProcess Details:")
    for p in metrics.processes:
        print(f"  {p.name}: Wait={p.wait_time:.2f}s, Turnaround={p.turnaround_time:.2f}s, Response={p.response_time:.2f}s")


def demo_priority_based_basic():
    """Demo 3: Basic Priority-Based scheduling"""
    print("\n" + "█"*70)
    print("DEMO 3: Priority-Based Scheduling (Preemptive)")
    print("█"*70)
    
    processes = [
        Process(pid=1, name="P1", arrival_time=0, burst_time=6, priority=3),
        Process(pid=2, name="P2", arrival_time=0, burst_time=4, priority=1),
        Process(pid=3, name="P3", arrival_time=0, burst_time=3, priority=2),
    ]
    
    print("\nProcess Details:")
    for p in processes:
        print(f"  {p.name}: Burst={p.burst_time}s, Priority={p.priority}")
    
    scheduler = PriorityBasedScheduler(verbose=True, preemptive=True)
    metrics = scheduler.execute(processes)
    
    print("\n" + str(metrics))
    print("\nProcess Details:")
    for p in metrics.processes:
        print(f"  {p.name}: Wait={p.wait_time:.2f}s, Turnaround={p.turnaround_time:.2f}s, Response={p.response_time:.2f}s")


def demo_priority_based_preemption():
    """Demo 4: Priority-Based with preemption scenario"""
    print("\n" + "█"*70)
    print("DEMO 4: Priority-Based Scheduling with Preemption")
    print("█"*70)
    
    processes = [
        Process(pid=1, name="P1", arrival_time=0, burst_time=8, priority=1),
        Process(pid=2, name="P2", arrival_time=1, burst_time=4, priority=2),  # Higher priority, arrives later
        Process(pid=3, name="P3", arrival_time=2, burst_time=2, priority=1),
        Process(pid=4, name="P4", arrival_time=4, burst_time=3, priority=3),  # Highest priority
    ]
    
    print("\nProcess Details:")
    for p in processes:
        print(f"  {p.name}: Arrival={p.arrival_time}s, Burst={p.burst_time}s, Priority={p.priority}")
    
    scheduler = PriorityBasedScheduler(verbose=True, preemptive=True)
    metrics = scheduler.execute(processes)
    
    print("\n" + str(metrics))
    print("\nProcess Details:")
    for p in metrics.processes:
        print(f"  {p.name}: Start={p.start_time:.2f}s, End={p.end_time:.2f}s, Response={p.response_time:.2f}s")


def demo_algorithm_comparison():
    """Demo 5: Compare algorithms on the same processes"""
    print("\n" + "█"*70)
    print("DEMO 5: Algorithm Comparison - Same Process Set")
    print("█"*70)
    
    processes = [
        Process(pid=1, name="P1", arrival_time=0, burst_time=5, priority=2),
        Process(pid=2, name="P2", arrival_time=0, burst_time=3, priority=1),
        Process(pid=3, name="P3", arrival_time=1, burst_time=4, priority=3),
        Process(pid=4, name="P4", arrival_time=1, burst_time=2, priority=1),
        Process(pid=5, name="P5", arrival_time=2, burst_time=3, priority=2),
    ]
    
    print("\nProcess Details:")
    for p in processes:
        print(f"  {p.name}: Arrival={p.arrival_time}s, Burst={p.burst_time}s, Priority={p.priority}")
    
    SchedulerComparison.compare_algorithms(processes)


def demo_advanced_scenario():
    """Demo 6: Advanced scenario - Mixed priorities and arrivals"""
    print("\n" + "█"*70)
    print("DEMO 6: Advanced Scenario - Real-world Simulation")
    print("█"*70)
    
    processes = [
        # System processes (high priority)
        Process(pid=1, name="kernel", arrival_time=0, burst_time=2, priority=5),
        Process(pid=2, name="daemon", arrival_time=0.5, burst_time=3, priority=4),
        
        # User applications (medium priority)
        Process(pid=3, name="app1", arrival_time=0, burst_time=6, priority=2),
        Process(pid=4, name="app2", arrival_time=1, burst_time=4, priority=2),
        
        # Background tasks (low priority)
        Process(pid=5, name="backup", arrival_time=1.5, burst_time=5, priority=1),
        Process(pid=6, name="cleaner", arrival_time=2, burst_time=2, priority=1),
    ]
    
    print("\nProcess Details (Priority: 5=highest, 1=lowest):")
    for p in processes:
        print(f"  {p.name:10} Arrival={p.arrival_time:.1f}s, Burst={p.burst_time}s, Priority={p.priority}")
    
    scheduler = PriorityBasedScheduler(verbose=True, preemptive=True)
    metrics = scheduler.execute(processes)
    
    print("\n" + str(metrics))


def demo_comparative_analysis():
    """Demo 7: Detailed comparative analysis"""
    print("\n" + "█"*70)
    print("DEMO 7: Comprehensive Algorithm Analysis")
    print("█"*70)
    
    # Create identical process set for comparison
    import copy
    
    base_processes = [
        Process(pid=1, name="P1", arrival_time=0, burst_time=5, priority=3),
        Process(pid=2, name="P2", arrival_time=1, burst_time=3, priority=1),
        Process(pid=3, name="P3", arrival_time=2, burst_time=4, priority=2),
        Process(pid=4, name="P4", arrival_time=3, burst_time=2, priority=1),
    ]
    
    # Round-Robin with different quantums
    results = {}
    for quantum in [1, 2, 4]:
        rr_processes = copy.deepcopy(base_processes)
        rr_scheduler = RoundRobinScheduler(time_quantum=quantum, verbose=False)
        rr_metrics = rr_scheduler.execute(rr_processes)
        results[f"RR (Q={quantum})"] = rr_metrics
    
    # Priority-Based
    pb_processes = copy.deepcopy(base_processes)
    pb_scheduler = PriorityBasedScheduler(verbose=False)
    pb_metrics = pb_scheduler.execute(pb_processes)
    results["Priority-Based"] = pb_metrics
    
    # Display comparison table
    print("\nComparative Performance Analysis:")
    print("─" * 100)
    print(f"{'Algorithm':<20} {'Avg Wait (s)':<15} {'Avg Turnaround (s)':<20} {'Avg Response (s)':<20} {'CPU Util. (%)':<15}")
    print("─" * 100)
    
    for algo_name, metrics in results.items():
        print(f"{algo_name:<20} {metrics.average_wait_time:<15.2f} {metrics.average_turnaround_time:<20.2f} {metrics.average_response_time:<20.2f} {metrics.cpu_utilization:<15.2f}")
    
    print("─" * 100)
    
    # Analysis summary
    print("\nAnalysis Summary:")
    print("""
1. ROUND-ROBIN SCHEDULING:
   - Fairness: All processes get equal CPU time (time quantum)
   - Time Quantum Impact: Smaller quantum = higher context switching, better responsiveness
   - Use Case: Interactive systems, time-sharing operating systems
   
2. PRIORITY-BASED SCHEDULING:
   - Efficiency: Higher priority tasks execute first, system uses CPU time better
   - Preemption: Lower priority tasks can be interrupted by higher priority arrivals
   - Use Case: Real-time systems, mixed workload environments
   
3. PERFORMANCE INSIGHTS:
   - Round-Robin: Consistent wait times, good for fairness
   - Priority-Based: Reduces wait time for important processes
   - Choice depends on system requirements (fairness vs. efficiency)
""")


def run_interactive_demo():
    """Run interactive demonstration"""
    print("\n" + "="*70)
    print("INTERACTIVE SCHEDULING DEMO")
    print("="*70 + "\n")
    
    while True:
        print("\nSelect a demo to run:")
        print("  1. Basic Round-Robin Scheduling")
        print("  2. Round-Robin with Staggered Arrivals")
        print("  3. Basic Priority-Based Scheduling")
        print("  4. Priority-Based with Preemption")
        print("  5. Algorithm Comparison")
        print("  6. Advanced Real-world Scenario")
        print("  7. Comprehensive Analysis")
        print("  8. Run All Demos")
        print("  9. Exit")
        
        choice = input("\nEnter your choice (1-9): ").strip()
        
        demos = {
            '1': ("Basic Round-Robin", demo_round_robin_basic),
            '2': ("Round-Robin with Arrivals", demo_round_robin_arrival),
            '3': ("Priority-Based Basic", demo_priority_based_basic),
            '4': ("Priority-Based Preemption", demo_priority_based_preemption),
            '5': ("Algorithm Comparison", demo_algorithm_comparison),
            '6': ("Advanced Scenario", demo_advanced_scenario),
            '7': ("Comprehensive Analysis", demo_comparative_analysis),
        }
        
        if choice == '8':
            for demo_func in [demo_round_robin_basic, demo_round_robin_arrival,
                             demo_priority_based_basic, demo_priority_based_preemption,
                             demo_algorithm_comparison, demo_advanced_scenario,
                             demo_comparative_analysis]:
                try:
                    demo_func()
                except Exception as e:
                    print(f"Error running demo: {e}")
        elif choice == '9':
            print("\nExiting demo. Thank you!")
            break
        elif choice in demos:
            demo_name, demo_func = demos[choice]
            print(f"\nRunning: {demo_name}...")
            try:
                demo_func()
            except Exception as e:
                print(f"Error running demo: {e}")
        else:
            print("Invalid choice. Please try again.")


def main():
    """Main entry point"""
    if len(sys.argv) > 1 and sys.argv[1] == '--batch':
        # Run all demos in batch mode
        print_header()
        print("Running all demonstrations...\n")
        
        demos = [
            ("Basic Round-Robin", demo_round_robin_basic),
            ("Round-Robin with Arrivals", demo_round_robin_arrival),
            ("Priority-Based Basic", demo_priority_based_basic),
            ("Priority-Based Preemption", demo_priority_based_preemption),
            ("Algorithm Comparison", demo_algorithm_comparison),
            ("Advanced Scenario", demo_advanced_scenario),
            ("Comprehensive Analysis", demo_comparative_analysis),
        ]
        
        for demo_name, demo_func in demos:
            try:
                demo_func()
                input("\nPress Enter to continue to next demo...")
            except Exception as e:
                print(f"Error in {demo_name}: {e}")
        
        print("\n" + "="*70)
        print("All demonstrations completed!")
        print("="*70)
    else:
        # Run interactive mode
        print_header()
        run_interactive_demo()


if __name__ == "__main__":
    main()
