# Advanced Shell Simulation (ASH)
## Deliverable 1: Basic Shell Implementation and Process Management

### Project Overview
This project implements a custom Unix-like shell that simulates fundamental operating system concepts including process management, job control, and command execution. The shell is built entirely in Python and demonstrates core OS principles without relying heavily on external OS abstractions.

### Key Features Implemented

#### 1. **Built-in Commands**
- `cd [directory]` - Change working directory
- `pwd` - Print current working directory
- `echo [text]` - Display text to terminal
- `clear` - Clear the terminal screen
- `ls [directory]` - List directory contents
- `cat [filename]` - Display file contents
- `mkdir [directory]` - Create new directory
- `rmdir [directory]` - Remove empty directory
- `rm [filename]` - Remove file
- `touch [filename]` - Create or update file timestamp
- `kill [pid]` - Terminate process by Process ID

#### 2. **Process Management**
- **Foreground Execution**: Commands execute in the foreground, blocking the shell until completion
- **Background Execution**: Commands ending with `&` execute in the background
- **Process Tracking**: The shell maintains a job table tracking all background processes
- **Exit Codes**: Processes return exit codes indicating success/failure

#### 3. **Job Control**
- `jobs` - List all background jobs with their status
- `fg [job_id]` - Bring a background job to the foreground
- `bg [job_id]` - Resume a stopped background job
- Automatic cleanup of completed jobs

#### 4. **Signal Handling**
- `SIGCHLD` handler for detecting child process termination
- `SIGINT` (Ctrl+C) handling for graceful interrupt
- Proper cleanup on shell exit

### Installation & Running

```bash
# Navigate to project directory
cd "d:\Edu\UC\Advanced Operating System\ASS"

# Run the shell
python main.py
```

### Architecture & Design

#### Shell Class Structure
```
Shell
├── Process Management
│   ├── Job tracking (job_counter, jobs dict)
│   ├── Background process execution
│   └── Job status monitoring
├── Built-in Commands (15 commands)
├── Command Parsing
│   ├── Argument parsing with shlex
│   └── Background detection (&)
└── Signal Handlers
    └── SIGCHLD for child process monitoring
```

#### Job Class
- Represents a background job
- Tracks process ID, command, status, and timestamp
- Provides status update mechanism

### OS Concepts Implemented

#### 1. **Process Creation**
- **Fork Simulation**: Python's `subprocess.Popen()` simulates process forking
- **Exec Simulation**: External command execution through subprocess
- **Process Hierarchy**: Shell maintains parent-child relationships

#### 2. **Process Management**
- **Foreground vs Background**: Processes can run in foreground (blocking) or background (non-blocking)
- **Process Tracking**: Job table maintains list of active background processes
- **Process Termination**: Graceful shutdown with signal handling

#### 3. **Job Control**
- **Job IDs**: Sequential numbering for background jobs
- **Job Status**: Tracking running/done/exit codes
- **Process State Transitions**: Jobs move between running and completed states

#### 4. **Memory Management Simulation**
- Each job maintains its own process context
- Command parsing creates argument lists in memory
- Working directory context maintained per shell session

#### 5. **Error Handling**
- File not found errors
- Permission errors
- Invalid command handling
- Process termination errors

### Usage Examples

```bash
# Navigate directories
ash:~$ cd /tmp
ash:/tmp$ pwd
/tmp

# Create and manipulate files
ash:/tmp$ touch myfile.txt
ash:/tmp$ cat myfile.txt
ash:/tmp$ echo "Hello World" > output.txt
ash:/tmp$ ls

# Background execution
ash:~$ sleep 100 &
[1] 12345
ash:~$ jobs
[1] Running             sleep 100

# Foreground job control
ash:~$ fg %1
sleep 100
^C

# Kill processes
ash:~$ kill 12345
```

### Error Handling

The shell implements comprehensive error handling:

1. **Command Not Found**: Displays error message when external command doesn't exist
2. **File Operations**: Handles file not found, permission denied, is a directory errors
3. **Process Errors**: Handles process lookup failures, permission denied for kill
4. **Invalid Input**: Gracefully handles empty input, malformed commands
5. **Signal Handling**: Proper handling of Ctrl+C and child process termination

### Performance Characteristics

- **Command Parsing**: O(n) where n is length of input
- **Job Lookup**: O(1) hash table lookup
- **Process Creation**: Depends on system subprocess overhead
- **Memory Usage**: Minimal, proportional to number of background jobs

### Limitations & Future Improvements

#### Current Limitations
1. No pipe support (|) - single command execution only
2. No I/O redirection (>, <, >>)
3. No wildcard expansion
4. No command history
5. No shell scripting support

#### Possible Improvements
1. **Pipes**: Implement pipeline processing between commands
2. **I/O Redirection**: Support stdin/stdout/stderr redirection
3. **Wildcards**: Implement glob pattern matching
4. **Command History**: Add persistent command history
5. **Environment Variables**: Full environment variable support
6. **Aliases**: Command aliasing support
7. **Advanced Job Control**: Process groups and session management

### Testing Recommendations

1. **Built-in Commands Test**
   - Verify each built-in command works correctly
   - Test error conditions (invalid paths, permissions)
   - Test with special characters and spaces

2. **Process Management Test**
   - Create multiple background processes
   - Verify job tracking and listing
   - Test foreground/background transitions

3. **Signal Handling Test**
   - Test Ctrl+C interruption
   - Verify proper cleanup on exit
   - Test process termination

4. **Stress Testing**
   - Run many background jobs
   - Test with large file operations
   - Verify system stability

### Files Structure
```
.
├── main.py           - Main shell implementation
├── pyproject.toml    - Project configuration
└── README.md         - This documentation
```

### Technical Stack
- **Language**: Python 3.8+
- **Libraries**: os, sys, subprocess, signal, pathlib, shlex
- **Platform**: Cross-platform (Windows/Linux/macOS)

### Author Notes
This implementation demonstrates fundamental OS concepts including process creation, management, and job control. The shell uses Python's subprocess module to simulate Unix-like process management while maintaining a clear separation between built-in commands and external program execution.

---

**Course**: Advanced Operating Systems  
**Deliverable**: 1 - Basic Shell Implementation and Process Management  
**Status**: Complete
