#!/usr/bin/env python3
"""
Piping Module for Advanced Shell Simulation
Implements command piping functionality

This module enables chaining of commands where the output of one command
becomes the input of another, simulating Unix-like pipe functionality.
"""

import subprocess
import os
import shlex
from typing import List, Tuple, Optional, Any
from dataclasses import dataclass


@dataclass
class PipeOperation:
    """Represents a single pipe operation"""
    command: str
    input_data: Optional[bytes] = None
    output_data: Optional[bytes] = None
    return_code: int = 0
    error_output: Optional[bytes] = None


class CommandPipeline:
    """Handles command piping and chaining"""
    
    def __init__(self, working_directory: str = "."):
        """Initialize pipeline with working directory"""
        self.working_directory = working_directory
        self.operations: List[PipeOperation] = []
        self.last_output: Optional[bytes] = None
    
    @staticmethod
    def has_pipe(command: str) -> bool:
        """Check if command contains pipe operator"""
        return "|" in command
    
    @staticmethod
    def parse_pipeline(command: str) -> List[str]:
        """
        Parse command string into individual commands
        Handles quoted strings properly
        
        Example: "ls | grep txt" -> ["ls", "grep txt"]
        """
        # Handle escaped pipes and quoted strings
        commands = []
        current = ""
        in_quotes = False
        quote_char = None
        
        for i, char in enumerate(command):
            if char in ('"', "'") and (i == 0 or command[i-1] != '\\'):
                if not in_quotes:
                    in_quotes = True
                    quote_char = char
                elif char == quote_char:
                    in_quotes = False
                    quote_char = None
                current += char
            elif char == "|" and not in_quotes:
                if current.strip():
                    commands.append(current.strip())
                current = ""
            else:
                current += char
        
        if current.strip():
            commands.append(current.strip())
        
        return commands
    
    def execute(self, command: str, timeout: Optional[float] = None) -> Tuple[bool, str]:
        """
        Execute piped command sequence
        Returns: (success: bool, output: str)
        """
        self.operations = []
        self.last_output = None
        
        # Parse the command into individual commands
        commands = self.parse_pipeline(command)
        
        if len(commands) == 1:
            return False, "No pipes detected. Use execute_single() for single commands."
        
        try:
            processes: List[subprocess.Popen] = []
            
            # Create all processes with pipes connecting them
            for i, cmd in enumerate(commands):
                try:
                    cmd_args = shlex.split(cmd)
                except ValueError:
                    cmd_args = cmd.split()
                
                if i == 0:
                    # First command: no input pipe
                    process = subprocess.Popen(
                        cmd_args,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        stdin=None,
                        cwd=self.working_directory,
                        text=False  # Work with bytes for proper piping
                    )
                else:
                    # Subsequent commands: connect to previous command's stdout
                    process = subprocess.Popen(
                        cmd_args,
                        stdin=processes[i-1].stdout,
                        stdout=subprocess.PIPE if i < len(commands) - 1 else subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        cwd=self.working_directory,
                        text=False
                    )
                    # Allow previous process to write to this process's stdin
                    # and close the pipe in the parent
                    if i > 0:
                        processes[i-1].stdout.close()
                
                processes.append(process)
            
            # Get output from the last process
            output, error = processes[-1].communicate(timeout=timeout)
            
            # Record operations
            for i, (cmd, proc) in enumerate(zip(commands, processes)):
                operation = PipeOperation(
                    command=cmd,
                    return_code=proc.returncode,
                    error_output=error if i == len(processes) - 1 else None
                )
                self.operations.append(operation)
            
            # Wait for all processes to complete
            for proc in processes:
                proc.wait()
            
            # Check if all processes succeeded
            all_success = all(proc.returncode == 0 for proc in processes)
            output_str = output.decode('utf-8', errors='replace') if output else ""
            error_str = error.decode('utf-8', errors='replace') if error else ""
            
            self.last_output = output
            
            if all_success:
                return True, output_str
            else:
                return False, f"Output:\n{output_str}\nError:\n{error_str}"
        
        except subprocess.TimeoutExpired:
            return False, f"Pipeline execution timed out after {timeout} seconds"
        except FileNotFoundError as e:
            return False, f"Command not found: {e}"
        except Exception as e:
            return False, f"Pipeline execution error: {str(e)}"
    
    def execute_single(self, command: str, input_data: Optional[str] = None,
                      timeout: Optional[float] = None) -> Tuple[bool, str]:
        """
        Execute a single command (without pipes)
        Returns: (success: bool, output: str)
        """
        try:
            try:
                cmd_args = shlex.split(command)
            except ValueError:
                cmd_args = command.split()
            
            input_bytes = input_data.encode('utf-8') if input_data else None
            
            process = subprocess.Popen(
                cmd_args,
                stdin=subprocess.PIPE if input_data else None,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                cwd=self.working_directory,
                text=False
            )
            
            output, error = process.communicate(input=input_bytes, timeout=timeout)
            
            output_str = output.decode('utf-8', errors='replace') if output else ""
            error_str = error.decode('utf-8', errors='replace') if error else ""
            
            success = process.returncode == 0
            result = output_str if success else error_str
            
            return success, result
        
        except subprocess.TimeoutExpired:
            process.kill()
            return False, f"Command timed out after {timeout} seconds"
        except FileNotFoundError:
            return False, f"Command not found: {command.split()[0]}"
        except Exception as e:
            return False, f"Execution error: {str(e)}"
    
    def get_statistics(self) -> dict:
        """Get statistics about the pipeline execution"""
        return {
            "commands_count": len(self.operations),
            "successful": sum(1 for op in self.operations if op.return_code == 0),
            "failed": sum(1 for op in self.operations if op.return_code != 0),
            "operations": [
                {
                    "command": op.command,
                    "return_code": op.return_code,
                    "has_error": op.error_output and len(op.error_output) > 0
                }
                for op in self.operations
            ]
        }
    
    def __str__(self) -> str:
        """String representation showing pipeline details"""
        if not self.operations:
            return "Pipeline: No operations executed"
        
        lines = ["Pipeline Operations:"]
        lines.append("-" * 60)
        
        for i, op in enumerate(self.operations):
            status = "✓ SUCCESS" if op.return_code == 0 else f"✗ FAILED ({op.return_code})"
            lines.append(f"[{i+1}] {op.command:<40} {status}")
        
        lines.append("-" * 60)
        
        return "\n".join(lines)


class BuiltinPipeSupport:
    """Support for piping with built-in shell commands"""
    
    def __init__(self):
        """Initialize builtin command registry"""
        self.builtins = {}
    
    def register_builtin(self, name: str, func) -> None:
        """Register a built-in command"""
        self.builtins[name] = func
    
    def is_builtin(self, command: str) -> bool:
        """Check if command is a registered built-in"""
        cmd_name = command.split()[0]
        return cmd_name in self.builtins
    
    def execute_builtin(self, command: str, stdin_data: Optional[bytes] = None) -> Tuple[bool, bytes, bytes]:
        """
        Execute a built-in command with optional stdin
        Returns: (success: bool, stdout: bytes, stderr: bytes)
        """
        try:
            cmd_parts = shlex.split(command)
            cmd_name = cmd_parts[0]
            args = cmd_parts[1:]
            
            if cmd_name not in self.builtins:
                return False, b"", f"Unknown command: {cmd_name}".encode()
            
            # For built-ins, we would need to capture output
            # This is a simplified version - in practice, we'd redirect stdout
            result = self.builtins[cmd_name](args, stdin_data)
            
            if isinstance(result, tuple):
                return True, result[0], result[1]
            else:
                return True, str(result).encode(), b""
        
        except Exception as e:
            return False, b"", str(e).encode()


# Utility functions for common piped operations

def pipe_commands(command1: str, command2: str, working_dir: str = ".") -> Tuple[bool, str]:
    """
    Quick utility to pipe two commands together
    Example: pipe_commands("ls", "grep .txt")
    """
    pipeline = CommandPipeline(working_dir)
    full_command = f"{command1} | {command2}"
    return pipeline.execute(full_command)


def pipe_multiple(commands: List[str], working_dir: str = ".") -> Tuple[bool, str]:
    """
    Quick utility to pipe multiple commands together
    Example: pipe_multiple(["ls", "grep .txt", "sort"])
    """
    pipeline = CommandPipeline(working_dir)
    full_command = " | ".join(commands)
    return pipeline.execute(full_command)
