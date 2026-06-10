#!/usr/bin/env python3
"""
Advanced Shell Simulation with Integrated OS Concepts
Deliverable 2: Process Scheduling

This shell extends Deliverable 1 with:
- Round-Robin Process Scheduling
- Priority-Based Process Scheduling
- Process performance metrics
- Scheduling algorithm comparison
"""

import os
import sys
import subprocess
import signal
import time
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import shlex
import copy

# Import scheduling module
from process_scheduler import (
    Process, RoundRobinScheduler, PriorityBasedScheduler,
    SchedulerComparison, ProcessState
)


class Job:
    """Represents a background job/process"""
    
    job_counter = 0
    
    def __init__(self, job_id: int, command: str, process: subprocess.Popen):
        self.job_id = job_id
        self.command = command
        self.process = process
        self.status = "Running"
        self.timestamp = time.time()
    
    def update_status(self) -> str:
        """Update and return the current status of the job"""
        if self.process.poll() is None:
            self.status = "Running"
        elif self.process.returncode == 0:
            self.status = "Done"
        else:
            self.status = f"Done (exit code: {self.process.returncode})"
        return self.status
    
    def __str__(self) -> str:
        return f"[{self.job_id}] {self.status:20} {self.command}"


class Shell:
    """Custom Unix-like shell with process management, job control, and scheduling"""
    
    def __init__(self):
        self.running = True
        self.jobs: Dict[int, Job] = {}
        self.job_counter = 0
        self.background_jobs = {}
        self.current_directory = os.getcwd()
        self.scheduler_processes: Dict[int, Process] = {}
        
        # Signal handling for SIGCHLD (child process termination)
        if hasattr(signal, 'SIGCHLD'):
            signal.signal(signal.SIGCHLD, self._handle_sigchld)
    
    def _handle_sigchld(self, signum, frame):
        """Handle child process termination"""
        for job_id in list(self.jobs.keys()):
            job = self.jobs[job_id]
            if job.process.poll() is not None:
                job.update_status()
    
    def parse_command(self, user_input: str) -> Tuple[List[str], bool]:
        """
        Parse user input into command and arguments.
        Returns tuple of (command_list, is_background)
        """
        user_input = user_input.strip()
        if not user_input:
            return [], False
        
        # Check for background execution
        is_background = user_input.endswith('&')
        if is_background:
            user_input = user_input[:-1].strip()
        
        try:
            command_list = shlex.split(user_input)
        except ValueError:
            command_list = user_input.split()
        
        return command_list, is_background
    
    # Built-in Commands Implementation
    
    def cmd_cd(self, args: List[str]) -> None:
        """Change directory"""
        if not args:
            # Change to home directory
            target_dir = str(Path.home())
        else:
            target_dir = args[0]
        
        try:
            os.chdir(target_dir)
            self.current_directory = os.getcwd()
        except FileNotFoundError:
            print(f"ash: cd: {target_dir}: No such file or directory")
        except NotADirectoryError:
            print(f"ash: cd: {target_dir}: Not a directory")
        except PermissionError:
            print(f"ash: cd: {target_dir}: Permission denied")
    
    def cmd_pwd(self, args: List[str]) -> None:
        """Print working directory"""
        print(self.current_directory)
    
    def cmd_echo(self, args: List[str]) -> None:
        """Print text to terminal"""
        if args:
            print(" ".join(args))
        else:
            print()
    
    def cmd_clear(self, args: List[str]) -> None:
        """Clear the terminal screen"""
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def cmd_ls(self, args: List[str]) -> None:
        """List files in directory"""
        try:
            target_dir = args[0] if args else "."
            items = os.listdir(target_dir)
            
            # Separate files and directories
            files = []
            dirs = []
            
            for item in sorted(items):
                item_path = os.path.join(target_dir, item)
                if os.path.isdir(item_path):
                    dirs.append(f"{item}/")
                else:
                    files.append(item)
            
            # Print directories first, then files
            for d in dirs:
                print(d)
            for f in files:
                print(f)
        
        except FileNotFoundError:
            print(f"ash: ls: cannot access '{target_dir}': No such file or directory")
        except PermissionError:
            print(f"ash: ls: cannot access '{target_dir}': Permission denied")
    
    def cmd_cat(self, args: List[str]) -> None:
        """Display file contents"""
        if not args:
            print("ash: cat: missing file argument")
            return
        
        for filename in args:
            try:
                with open(filename, 'r') as f:
                    print(f.read(), end='')
            except FileNotFoundError:
                print(f"ash: cat: {filename}: No such file or directory")
            except IsADirectoryError:
                print(f"ash: cat: {filename}: Is a directory")
            except PermissionError:
                print(f"ash: cat: {filename}: Permission denied")
    
    def cmd_mkdir(self, args: List[str]) -> None:
        """Create directory"""
        if not args:
            print("ash: mkdir: missing operand")
            return
        
        for dirname in args:
            try:
                os.makedirs(dirname, exist_ok=False)
            except FileExistsError:
                print(f"ash: mkdir: cannot create directory '{dirname}': File exists")
            except PermissionError:
                print(f"ash: mkdir: cannot create directory '{dirname}': Permission denied")
    
    def cmd_rmdir(self, args: List[str]) -> None:
        """Remove empty directory"""
        if not args:
            print("ash: rmdir: missing operand")
            return
        
        for dirname in args:
            try:
                os.rmdir(dirname)
            except FileNotFoundError:
                print(f"ash: rmdir: {dirname}: No such file or directory")
            except OSError as e:
                print(f"ash: rmdir: {dirname}: {e.strerror}")
    
    def cmd_rm(self, args: List[str]) -> None:
        """Remove file"""
        if not args:
            print("ash: rm: missing operand")
            return
        
        for filename in args:
            try:
                os.remove(filename)
            except FileNotFoundError:
                print(f"ash: rm: {filename}: No such file or directory")
            except IsADirectoryError:
                print(f"ash: rm: {filename}: Is a directory")
            except PermissionError:
                print(f"ash: rm: {filename}: Permission denied")
    
    def cmd_touch(self, args: List[str]) -> None:
        """Create empty file or update timestamp"""
        if not args:
            print("ash: touch: missing file argument")
            return
        
        for filename in args:
            try:
                Path(filename).touch()
            except PermissionError:
                print(f"ash: touch: {filename}: Permission denied")
            except Exception as e:
                print(f"ash: touch: {filename}: {e}")
    
    def cmd_kill(self, args: List[str]) -> None:
        """Terminate process by PID"""
        if not args:
            print("ash: kill: missing PID argument")
            return
        
        for pid_str in args:
            try:
                pid = int(pid_str)
                os.kill(pid, signal.SIGTERM)
                print(f"Sent SIGTERM to process {pid}")
            except ValueError:
                print(f"ash: kill: {pid_str}: Invalid PID")
            except ProcessLookupError:
                print(f"ash: kill: {pid_str}: No such process")
            except PermissionError:
                print(f"ash: kill: {pid_str}: Permission denied")
    
    def cmd_exit(self, args: List[str]) -> None:
        """Exit the shell"""
        # Terminate all background jobs
        for job in self.jobs.values():
            try:
                if job.process.poll() is None:
                    job.process.terminate()
                    job.process.wait(timeout=1)
            except (subprocess.TimeoutExpired, ProcessLookupError):
                pass
        
        self.running = False
    
    def cmd_jobs(self, args: List[str]) -> None:
        """List all background jobs"""
        if not self.jobs:
            return
        
        for job_id, job in self.jobs.items():
            job.update_status()
            print(job)
    
    def cmd_fg(self, args: List[str]) -> None:
        """Bring background job to foreground"""
        if not args:
            print("ash: fg: missing job ID")
            return
        
        try:
            job_id = int(args[0].lstrip('%'))
            if job_id not in self.jobs:
                print(f"ash: fg: job {job_id} not found")
                return
            
            job = self.jobs[job_id]
            if job.process.poll() is not None:
                print(f"ash: fg: job {job_id}: already completed")
                del self.jobs[job_id]
                return
            
            # Bring to foreground
            print(job.command)
            job.process.wait()
            job.update_status()
            
            if job.process.returncode == 0:
                del self.jobs[job_id]
        
        except ValueError:
            print("ash: fg: invalid job ID")
    
    def cmd_bg(self, args: List[str]) -> None:
        """Resume stopped job in background"""
        if not args:
            print("ash: bg: missing job ID")
            return
        
        try:
            job_id = int(args[0].lstrip('%'))
            if job_id not in self.jobs:
                print(f"ash: bg: job {job_id} not found")
                return
            
            job = self.jobs[job_id]
            if job.process.poll() is not None:
                print(f"ash: bg: job {job_id}: already completed")
                del self.jobs[job_id]
                return
            
            print(f"[{job_id}] {job.command}")
        
        except ValueError:
            print("ash: bg: invalid job ID")
    
    # ===== NEW SCHEDULING COMMANDS FOR DELIVERABLE 2 =====
    
    def cmd_schedule_rr(self, args: List[str]) -> None:
        """Run Round-Robin scheduling: schedule-rr [time_quantum] [process_count]"""
        if not args:
            print("Usage: schedule-rr [time_quantum] [process_count]")
            print("Example: schedule-rr 2 4")
            return
        
        try:
            time_quantum = float(args[0]) if len(args) > 0 else 2.0
            process_count = int(args[1]) if len(args) > 1 else 4
            
            print(f"\n{'='*70}")
            print(f"ROUND-ROBIN SCHEDULING DEMO")
            print(f"Time Quantum: {time_quantum}s, Processes: {process_count}")
            print(f"{'='*70}\n")
            
            # Generate sample processes
            processes = []
            for i in range(process_count):
                p = Process(
                    pid=i+1,
                    name=f"P{i+1}",
                    arrival_time=float(i * 0.5),
                    burst_time=float((i+1) * 2),
                    priority=0
                )
                processes.append(p)
            
            # Display process information
            print("Process Information:")
            print("─" * 60)
            print(f"{'PID':<5} {'Name':<10} {'Arrival':<10} {'Burst':<10} {'Priority':<10}")
            print("─" * 60)
            for p in processes:
                print(f"{p.pid:<5} {p.name:<10} {p.arrival_time:<10.1f} {p.burst_time:<10.1f} {p.priority:<10}")
            print("─" * 60 + "\n")
            
            # Run scheduler
            scheduler = RoundRobinScheduler(time_quantum=time_quantum, verbose=True)
            metrics = scheduler.execute(processes)
            
            # Display results
            print("\n" + str(metrics))
            self._display_process_results(metrics)
        
        except (ValueError, IndexError):
            print("Error: Invalid arguments")
            print("Usage: schedule-rr [time_quantum] [process_count]")
    
    def cmd_schedule_pb(self, args: List[str]) -> None:
        """Run Priority-Based scheduling: schedule-pb [process_count]"""
        if not args:
            print("Usage: schedule-pb [process_count]")
            print("Example: schedule-pb 5")
            return
        
        try:
            process_count = int(args[0]) if len(args) > 0 else 5
            
            print(f"\n{'='*70}")
            print(f"PRIORITY-BASED SCHEDULING DEMO (Preemptive)")
            print(f"Processes: {process_count}")
            print(f"{'='*70}\n")
            
            # Generate sample processes with different priorities
            processes = []
            for i in range(process_count):
                p = Process(
                    pid=i+1,
                    name=f"P{i+1}",
                    arrival_time=float(i * 0.5),
                    burst_time=float((i+1) * 2),
                    priority=(process_count - i)  # Descending priority
                )
                processes.append(p)
            
            # Display process information
            print("Process Information:")
            print("─" * 70)
            print(f"{'PID':<5} {'Name':<10} {'Arrival':<10} {'Burst':<10} {'Priority':<15}")
            print("─" * 70)
            for p in processes:
                print(f"{p.pid:<5} {p.name:<10} {p.arrival_time:<10.1f} {p.burst_time:<10.1f} {p.priority:<15}")
            print("─" * 70 + "\n")
            
            # Run scheduler
            scheduler = PriorityBasedScheduler(verbose=True, preemptive=True)
            metrics = scheduler.execute(processes)
            
            # Display results
            print("\n" + str(metrics))
            self._display_process_results(metrics)
        
        except (ValueError, IndexError):
            print("Error: Invalid arguments")
            print("Usage: schedule-pb [process_count]")
    
    def cmd_compare_schedulers(self, args: List[str]) -> None:
        """Compare RR and Priority-Based schedulers: compare-schedulers [process_count]"""
        process_count = int(args[0]) if args else 5
        
        print(f"\n{'='*70}")
        print(f"SCHEDULER COMPARISON")
        print(f"Process Count: {process_count}")
        print(f"{'='*70}\n")
        
        # Generate base processes
        base_processes = []
        for i in range(process_count):
            p = Process(
                pid=i+1,
                name=f"P{i+1}",
                arrival_time=float(i * 0.3),
                burst_time=float((i+1) * 2.5),
                priority=(process_count - i)
            )
            base_processes.append(p)
        
        # Run both schedulers
        rr_processes = copy.deepcopy(base_processes)
        rr_scheduler = RoundRobinScheduler(time_quantum=2.0, verbose=False)
        rr_metrics = rr_scheduler.execute(rr_processes)
        
        pb_processes = copy.deepcopy(base_processes)
        pb_scheduler = PriorityBasedScheduler(verbose=False)
        pb_metrics = pb_scheduler.execute(pb_processes)
        
        # Display comparison
        print("\nComparison Results:")
        print("─" * 100)
        print(f"{'Metric':<30} {'Round-Robin':<35} {'Priority-Based':<35}")
        print("─" * 100)
        print(f"{'Average Wait Time':<30} {rr_metrics.average_wait_time:<35.2f} {pb_metrics.average_wait_time:<35.2f}")
        print(f"{'Average Turnaround Time':<30} {rr_metrics.average_turnaround_time:<35.2f} {pb_metrics.average_turnaround_time:<35.2f}")
        print(f"{'Average Response Time':<30} {rr_metrics.average_response_time:<35.2f} {pb_metrics.average_response_time:<35.2f}")
        print(f"{'CPU Utilization':<30} {rr_metrics.cpu_utilization:<34.2f}% {pb_metrics.cpu_utilization:<34.2f}%")
        print(f"{'Total Execution Time':<30} {rr_metrics.total_time:<35.2f} {pb_metrics.total_time:<35.2f}")
        print("─" * 100)
        
        # Analysis
        print("\nAnalysis:")
        if rr_metrics.average_wait_time < pb_metrics.average_wait_time:
            print("✓ Round-Robin has lower average wait time")
        else:
            print("✓ Priority-Based has lower average wait time")
        
        if rr_metrics.average_turnaround_time < pb_metrics.average_turnaround_time:
            print("✓ Round-Robin has lower average turnaround time")
        else:
            print("✓ Priority-Based has lower average turnaround time")
    
    def _display_process_results(self, metrics) -> None:
        """Display detailed process results"""
        print("\nDetailed Process Results:")
        print("─" * 100)
        print(f"{'PID':<5} {'Name':<10} {'Start':<10} {'End':<10} {'Wait':<10} {'Turnaround':<15} {'Response':<12}")
        print("─" * 100)
        
        for p in sorted(metrics.processes, key=lambda x: x.pid):
            start_str = f"{p.start_time:.2f}s" if p.start_time else "N/A"
            end_str = f"{p.end_time:.2f}s" if p.end_time else "N/A"
            
            print(f"{p.pid:<5} {p.name:<10} {start_str:<10} {end_str:<10} {p.wait_time:<10.2f} {p.turnaround_time:<15.2f} {p.response_time:<12.2f}")
        
        print("─" * 100)
    
    def execute_builtin(self, command: str, args: List[str]) -> bool:
        """Execute built-in commands"""
        builtins = {
            'cd': self.cmd_cd,
            'pwd': self.cmd_pwd,
            'echo': self.cmd_echo,
            'clear': self.cmd_clear,
            'ls': self.cmd_ls,
            'cat': self.cmd_cat,
            'mkdir': self.cmd_mkdir,
            'rmdir': self.cmd_rmdir,
            'rm': self.cmd_rm,
            'touch': self.cmd_touch,
            'kill': self.cmd_kill,
            'exit': self.cmd_exit,
            'jobs': self.cmd_jobs,
            'fg': self.cmd_fg,
            'bg': self.cmd_bg,
            'schedule-rr': self.cmd_schedule_rr,
            'schedule-pb': self.cmd_schedule_pb,
            'compare-schedulers': self.cmd_compare_schedulers,
        }
        
        if command in builtins:
            builtins[command](args)
            return True
        
        return False
    
    def execute_external(self, command_list: List[str], is_background: bool) -> None:
        """Execute external commands"""
        if not command_list:
            return
        
        command = command_list[0]
        args = command_list[1:]
        
        try:
            if is_background:
                # Execute in background
                process = subprocess.Popen(
                    command_list,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    cwd=self.current_directory
                )
                self.job_counter += 1
                job = Job(self.job_counter, " ".join(command_list), process)
                self.jobs[self.job_counter] = job
                print(f"[{self.job_counter}] {process.pid}")
            else:
                # Execute in foreground
                process = subprocess.Popen(
                    command_list,
                    cwd=self.current_directory
                )
                process.wait()
        
        except FileNotFoundError:
            print(f"ash: {command}: command not found")
        except PermissionError:
            print(f"ash: {command}: Permission denied")
        except Exception as e:
            print(f"ash: {command}: {e}")
    
    def cleanup_completed_jobs(self) -> None:
        """Remove completed jobs from the jobs list"""
        completed_jobs = []
        for job_id, job in self.jobs.items():
            if job.process.poll() is not None:
                completed_jobs.append(job_id)
        
        for job_id in completed_jobs:
            del self.jobs[job_id]
    
    def display_prompt(self) -> None:
        """Display the shell prompt"""
        cwd = self.current_directory.replace(os.path.expanduser("~"), "~")
        print(f"ash:{cwd}$ ", end="", flush=True)
    
    def run(self) -> None:
        """Main shell loop"""
        print("Advanced Shell Simulation (ASH) - Deliverable 2: Process Scheduling")
        print("Type 'help' for available commands or 'exit' to quit\n")
        
        while self.running:
            try:
                self.cleanup_completed_jobs()
                self.display_prompt()
                
                user_input = input()
                
                if user_input.lower() == 'help':
                    self.display_help()
                    continue
                
                command_list, is_background = self.parse_command(user_input)
                
                if not command_list:
                    continue
                
                command = command_list[0]
                args = command_list[1:]
                
                # Try built-in commands first
                if not self.execute_builtin(command, args):
                    # Execute external command
                    self.execute_external(command_list, is_background)
            
            except KeyboardInterrupt:
                print("\n")
                continue
            except EOFError:
                print("\nexit")
                self.running = False
    
    def display_help(self) -> None:
        """Display help information"""
        help_text = """
╔════════════════════════════════════════════════════════════════════════════╗
║                          ASH SHELL - HELP                                 ║
╚════════════════════════════════════════════════════════════════════════════╝

DELIVERABLE 1: Basic Commands & Job Control
─────────────────────────────────────────────
  cd [dir]          - Change directory
  pwd               - Print working directory
  echo [text]       - Print text
  clear             - Clear screen
  ls [dir]          - List directory contents
  cat [file]        - Display file contents
  mkdir [dir]       - Create directory
  rmdir [dir]       - Remove empty directory
  rm [file]         - Remove file
  touch [file]      - Create/update file
  kill [pid]        - Terminate process
  jobs              - List background jobs
  fg [job_id]       - Bring job to foreground
  bg [job_id]       - Resume job in background
  exit              - Exit shell

DELIVERABLE 2: Process Scheduling
──────────────────────────────────
  schedule-rr [time_quantum] [count]
                    - Run Round-Robin scheduling
                    - Example: schedule-rr 2 4
                    
  schedule-pb [count]
                    - Run Priority-Based (Preemptive) scheduling
                    - Example: schedule-pb 5
                    
  compare-schedulers [count]
                    - Compare Round-Robin vs Priority-Based
                    - Example: compare-schedulers 4

SPECIAL SYNTAX
──────────────
  command &         - Run command in background
  help              - Display this help

EXAMPLE USAGE
─────────────
1. Basic commands:
   $ pwd
   $ echo "Hello World"
   $ ls
   
2. Process scheduling:
   $ schedule-rr 2 4          (4 processes, 2 sec time quantum)
   $ schedule-pb 5            (5 processes with priorities)
   $ compare-schedulers 4     (Compare both algorithms)

3. Background execution:
   $ sleep 10 &               (Run sleep in background)
   $ jobs                     (List background jobs)
   $ fg 1                     (Bring job 1 to foreground)
"""
        print(help_text)


def main():
    """Main entry point"""
    shell = Shell()
    try:
        shell.run()
    except Exception as e:
        print(f"Fatal error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
