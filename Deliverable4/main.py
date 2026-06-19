#!/usr/bin/env python3
"""
Advanced Shell Simulation with Integrated OS Concepts
Deliverable 4: Integration and Security Implementation

This shell integrates all previous deliverables with:
- Command piping (output of one command as input to another)
- User authentication system
- File permissions and access control
- Multi-user support with different roles
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
import getpass

# Import all modules from previous deliverables
from process_scheduler import (
    Process, RoundRobinScheduler, PriorityBasedScheduler,
    SchedulerComparison, ProcessState
)
from memory_management import PagingMemoryManager
from process_synchronization import MutexCounterDemo, ProducerConsumerDemo
from security import UserAuthenticationSystem, UserRole, FilePermissions
from piping import CommandPipeline


class Job:
    """Represents a background job/process"""
    
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
    """Advanced Unix-like shell with integrated OS concepts"""
    
    def __init__(self):
        self.running = True
        self.jobs: Dict[int, Job] = {}
        self.job_counter = 0
        self.current_directory = os.getcwd()
        self.memory_manager = PagingMemoryManager(total_frames=8, algorithm="fifo")
        
        # Initialize security system
        self.auth_system = UserAuthenticationSystem()
        self.current_user = None
        
        # Initialize piping system
        self.pipeline = CommandPipeline(self.current_directory)
        
        # Signal handling
        if hasattr(signal, 'SIGCHLD'):
            signal.signal(signal.SIGCHLD, self._handle_sigchld)

    def authenticate(self) -> bool:
        """Authenticate user at shell startup"""
        print("\n" + "="*70)
        print("Advanced Shell Simulation (ASH) - Deliverable 4")
        print("Integrated: Scheduling + Memory + Sync + Piping + Security")
        print("="*70)
        print("\nDefault Test Credentials:")
        creds = self.auth_system.get_default_credentials()
        for user, pwd in creds.items():
            print(f"  {user}: {pwd}")
        print("="*70 + "\n")
        
        max_attempts = 3
        attempts = 0
        
        while attempts < max_attempts:
            username = input("Username: ").strip()
            password = getpass.getpass("Password: ")
            
            success, message = self.auth_system.login(username, password)
            
            if success:
                print(f"\n✓ {message}\n")
                self.current_user = self.auth_system.get_current_user()
                return True
            else:
                attempts += 1
                print(f"✗ {message}")
                if attempts < max_attempts:
                    print(f"Attempts remaining: {max_attempts - attempts}\n")
        
        print("\nAuthentication failed. Exiting.")
        return False

    # Memory Management Commands
    def cmd_mem_init(self, args: List[str]) -> None:
        """Initialize memory: mem-init [frames] [fifo|lru]"""
        try:
            frames = int(args[0]) if len(args) > 0 else 8
            algorithm = args[1].lower() if len(args) > 1 else "fifo"
            self.memory_manager = PagingMemoryManager(total_frames=frames, algorithm=algorithm)
            print(f"✓ Memory manager initialized: {frames} frames, algorithm={algorithm}")
        except ValueError as e:
            print(f"✗ Error: {e}")

    # Security Commands
    def cmd_whoami(self, args: List[str]) -> None:
        """Display current user"""
        if not self.current_user:
            print("Not logged in")
            return
        print(f"User: {self.current_user.username} (Role: {self.current_user.role.value})")
    
    def cmd_users(self, args: List[str]) -> None:
        """List all users (admin only)"""
        if not self.auth_system.is_admin():
            print("✗ Permission denied. Only admins can list users.")
            return
        
        users = self.auth_system.list_users()
        print("\n" + "─" * 60)
        print(f"{'Username':<15} {'Role':<15} {'Last Login':<30}")
        print("─" * 60)
        for user in users:
            print(f"{user['username']:<15} {user['role']:<15} {user['last_login']:<30}")
        print("─" * 60)

    # Piping Demo
    def cmd_pipe_demo(self, args: List[str]) -> None:
        """Demonstrate piping"""
        print("\nPiping Demo - Command chaining examples:")
        print("─" * 70)
        
        # Create test files if they don't exist
        test_files = ["test1.txt", "test2.log", "data.csv"]
        for f in test_files:
            if not os.path.exists(f):
                Path(f).touch()
        
        examples = [
            ("ls | grep txt", "List and filter for .txt files"),
            ("echo hello world | grep world", "Echo and search for word"),
        ]
        
        for cmd, desc in examples:
            print(f"\nExample: {cmd}")
            print(f"Description: {desc}")
            print("Result:")
            success, output = self.pipeline.execute(cmd)
            if success:
                print(output if output else "(no output)")
            else:
                print(f"Error: {output}")

    # Basic File Commands
    def cmd_ls(self, args: List[str]) -> None:
        """List directory"""
        try:
            target_dir = args[0] if args else "."
            items = sorted(os.listdir(target_dir))
            for item in items:
                item_path = os.path.join(target_dir, item)
                if os.path.isdir(item_path):
                    print(f"{item}/")
                else:
                    print(item)
        except (FileNotFoundError, PermissionError) as e:
            print(f"✗ {e}")
    
    def cmd_pwd(self, args: List[str]) -> None:
        """Print working directory"""
        print(self.current_directory)
    
    def cmd_cd(self, args: List[str]) -> None:
        """Change directory"""
        target_dir = args[0] if args else str(Path.home())
        try:
            os.chdir(target_dir)
            self.current_directory = os.getcwd()
            self.pipeline.working_directory = self.current_directory
        except (FileNotFoundError, NotADirectoryError, PermissionError) as e:
            print(f"✗ {e}")
    
    def cmd_cat(self, args: List[str]) -> None:
        """Display file contents"""
        if not args:
            print("✗ Missing file argument")
            return
        
        for filename in args:
            if not self.auth_system.can_read(filename, self.current_user.username):
                print(f"✗ Permission denied: {filename}")
                continue
            try:
                with open(filename, 'r') as f:
                    print(f.read(), end='')
            except FileNotFoundError:
                print(f"✗ File not found: {filename}")

    # Scheduling Commands
    def cmd_schedule_rr(self, args: List[str]) -> None:
        """Run Round-Robin scheduling"""
        try:
            time_quantum = float(args[0]) if len(args) > 0 else 2.0
            process_count = int(args[1]) if len(args) > 1 else 4
            
            processes = [
                Process(pid=i+1, name=f"P{i+1}", arrival_time=float(i*0.5),
                       burst_time=float((i+1)*2), priority=0)
                for i in range(process_count)
            ]
            
            scheduler = RoundRobinScheduler(time_quantum=time_quantum, verbose=True)
            metrics = scheduler.execute(processes)
            print(f"\n✓ Scheduling complete. Avg Wait: {metrics.average_wait_time:.2f}s")
        except (ValueError, IndexError):
            print("Usage: schedule-rr [time_quantum] [count]")

    # Help
    def cmd_help(self, args: List[str]) -> None:
        """Display help"""
        help_text = """
╔════════════════════════════════════════════════════════════════════════════╗
║                    ASH SHELL - DELIVERABLE 4 HELP                        ║
╚════════════════════════════════════════════════════════════════════════════╝

SECURITY COMMANDS
─────────────────
  whoami                    - Show current user info
  users                     - List all users (admin only)

PIPING & CHAINING
─────────────────
  cmd1 | cmd2 | cmd3        - Chain commands with pipes
  pipe-demo                 - Show piping examples
  
  Example: ls | grep .txt   - List and filter files

FILE COMMANDS
─────────────
  ls [dir]                  - List directory
  pwd                       - Print working directory
  cd [dir]                  - Change directory
  cat [file]                - Display file
  touch [file]              - Create file
  mkdir [dir]               - Create directory
  rm [file]                 - Remove file

MEMORY MANAGEMENT
─────────────────
  mem-init [frames] [algo]  - Initialize memory (fifo or lru)
  
PROCESS SCHEDULING
──────────────────
  schedule-rr [q] [n]       - Round-Robin scheduling
  schedule-pb [n]           - Priority-based scheduling

SPECIAL
───────
  exit                      - Exit shell
  help                      - This help message

PIPING EXAMPLES
───────────────
  $ ls | grep txt           (find .txt files)
  $ cat file | sort         (sort file contents)
  $ echo test | grep test   (search in output)

DEFAULT USERS (for testing)
───────────────────────────
  admin / admin123  (admin role)
  alice / alice123  (user role)
  bob / bob123      (user role)
  guest / guest     (guest role)
"""
        print(help_text)

    def execute_builtin(self, command: str, args: List[str]) -> bool:
        """Execute built-in commands"""
        builtins = {
            'whoami': self.cmd_whoami,
            'users': self.cmd_users,
            'pipe-demo': self.cmd_pipe_demo,
            'ls': self.cmd_ls,
            'pwd': self.cmd_pwd,
            'cd': self.cmd_cd,
            'cat': self.cmd_cat,
            'mem-init': self.cmd_mem_init,
            'schedule-rr': self.cmd_schedule_rr,
            'help': self.cmd_help,
            'exit': self.cmd_exit,
        }
        
        if command in builtins:
            builtins[command](args)
            return True
        return False
    
    def cmd_exit(self, args: List[str]) -> None:
        """Exit shell"""
        self.auth_system.logout()
        self.running = False

    def _handle_sigchld(self, signum, frame):
        """Handle child process termination"""
        pass

    def parse_command(self, user_input: str) -> Tuple[List[str], bool]:
        """Parse user input"""
        user_input = user_input.strip()
        if not user_input:
            return [], False
        
        is_background = user_input.endswith('&')
        if is_background:
            user_input = user_input[:-1].strip()
        
        try:
            return shlex.split(user_input), is_background
        except ValueError:
            return user_input.split(), is_background

    def display_prompt(self) -> None:
        """Display shell prompt"""
        cwd = self.current_directory.replace(os.path.expanduser("~"), "~")
        user_indicator = "# " if self.auth_system.is_admin() else "$ "
        print(f"ash:{cwd}{user_indicator}", end="", flush=True)

    def run(self) -> None:
        """Main shell loop"""
        print("\nType 'help' for commands or 'exit' to quit\n")
        
        while self.running:
            try:
                self.display_prompt()
                user_input = input()
                
                if user_input.lower() == 'help':
                    self.cmd_help([])
                    continue
                
                if CommandPipeline.has_pipe(user_input):
                    success, output = self.pipeline.execute(user_input)
                    if output:
                        print(output, end='')
                    if not success:
                        print(output)
                else:
                    command_list, is_background = self.parse_command(user_input)
                    if command_list:
                        command = command_list[0]
                        args = command_list[1:]
                        if not self.execute_builtin(command, args):
                            print(f"✗ Unknown command: {command}")
            
            except KeyboardInterrupt:
                print("\n")
            except EOFError:
                print("\nexit")
                self.running = False


def main():
    """Main entry point"""
    shell = Shell()
    
    if not shell.authenticate():
        sys.exit(1)
    
    try:
        shell.run()
    except Exception as e:
        print(f"Fatal error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
