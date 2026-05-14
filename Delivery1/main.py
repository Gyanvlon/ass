#!/usr/bin/env python3
"""
Advanced Shell Simulation with Integrated OS Concepts
Deliverable 1: Basic Shell Implementation and Process Management

This shell simulates a Unix-like operating system environment with:
- Process management (foreground/background execution)
- Built-in commands (cd, pwd, echo, clear, ls, cat, mkdir, rmdir, rm, touch, kill)
- Job control (jobs, fg, bg commands)
- Process tracking and status management
"""

import os
import sys
import subprocess
import signal
import time
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import shlex


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
    """Custom Unix-like shell with process management and job control"""
    
    def __init__(self):
        self.running = True
        self.jobs: Dict[int, Job] = {}
        self.job_counter = 0
        self.background_jobs = {}
        self.current_directory = os.getcwd()
        
        # Signal handling for SIGCHLD (child process termination)
        # Note: SIGCHLD is not available on Windows
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
    
    def execute_builtin(self, command: str, args: List[str]) -> bool:
        """Execute built-in commands. Returns True if command was built-in."""
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
        print("Advanced Shell Simulation (ASH)")
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
Built-in Commands:
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
  help              - Display this help

Special Syntax:
  command &         - Run command in background
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
