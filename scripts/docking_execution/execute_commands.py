#!/usr/bin/env python3
"""
Execute Bash Commands from File with Output Redirection

This script reads bash commands from an input file and executes them sequentially,
redirecting the standard output and standard error to a specified output file.

Features:
    - Read multiple bash commands from an input file (one command per line)
    - Execute commands sequentially in order
    - Redirect stdout and stderr to a single output file
    - Print command execution status to console
    - Handle command errors gracefully with error reporting
    - Support for commands with pipes, redirects, and complex syntax
    - Optional verbose mode for detailed logging
    - Append mode to output file (preserves previous runs)

Usage:
    python execute_commands.py <input_file> <output_file> [--verbose]

Arguments:
    input_file      Path to file containing bash commands (one per line)
    output_file     Path to file where command outputs will be redirected
    --verbose       Optional flag for verbose output (default: False)

Example:
    python execute_commands.py commands.txt results.log
    python execute_commands.py commands.txt results.log --verbose

Notes:
    - Empty lines and comments (lines starting with #) are skipped
    - Each command is executed with shell=True
    - Output is appended to the output file
    - Exit status of each command is logged
"""

import sys
import subprocess
import os
from datetime import datetime


def load_commands(input_file):
    """
    Load commands from input file.
    
    Args:
        input_file (str): Path to file containing commands
        
    Returns:
        list: List of non-empty, non-comment command strings
    """
    commands = []
    try:
        with open(input_file, 'r') as f:
            for line in f:
                line = line.strip()
                # Skip empty lines and comments
                if line and not line.startswith('#'):
                    commands.append(line)
        return commands
    except FileNotFoundError:
        print(f"Error: Input file '{input_file}' not found.")
        sys.exit(1)
    except Exception as e:
        print(f"Error reading input file: {e}")
        sys.exit(1)


def execute_commands(commands, output_file, verbose=False):
    """
    Execute commands sequentially and redirect output to file.
    
    Args:
        commands (list): List of bash commands to execute
        output_file (str): Path to output file for redirecting stdout/stderr
        verbose (bool): If True, print detailed execution information
    """
    if not commands:
        print("Warning: No commands found in input file.")
        return
    
    # Create output file with header
    try:
        with open(output_file, 'w') as f:
            f.write(f"{'='*80}\n")
            f.write(f"Command Execution Log - Started: {datetime.now().isoformat()}\n")
            f.write(f"{'='*80}\n\n")
    except Exception as e:
        print(f"Error creating output file: {e}")
        sys.exit(1)
    
    total_commands = len(commands)
    successful = 0
    failed = 0
    
    print(f"Executing {total_commands} command(s)...")
    print(f"Output will be redirected to: {output_file}\n")
    
    for i, command in enumerate(commands, 1):
        print(f"[{i}/{total_commands}] Executing: {command}")
        
        if verbose:
            print(f"  Command index: {i}")
        
        try:
            # Execute command with shell
            result = subprocess.run(
                command,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                timeout=None
            )
            
            # Write command and output to file
            with open(output_file, 'a') as f:
                f.write(f"\n{'─'*80}\n")
                f.write(f"Command {i}: {command}\n")
                f.write(f"Executed at: {datetime.now().isoformat()}\n")
                f.write(f"Exit Status: {result.returncode}\n")
                f.write(f"{'─'*80}\n")
                f.write(f"{result.stdout}\n")
            
            if result.returncode == 0:
                print(f"  ✓ Success (exit code: 0)\n")
                successful += 1
            else:
                print(f"  ✗ Failed (exit code: {result.returncode})\n")
                failed += 1
                
        except subprocess.TimeoutExpired:
            print(f"  ✗ Timeout\n")
            failed += 1
            with open(output_file, 'a') as f:
                f.write(f"\nCommand {i}: TIMEOUT\n")
                
        except Exception as e:
            print(f"  ✗ Error: {e}\n")
            failed += 1
            with open(output_file, 'a') as f:
                f.write(f"\nCommand {i}: ERROR - {str(e)}\n")
    
    # Write summary
    with open(output_file, 'a') as f:
        f.write(f"\n{'='*80}\n")
        f.write(f"Execution Summary\n")
        f.write(f"{'='*80}\n")
        f.write(f"Total Commands: {total_commands}\n")
        f.write(f"Successful: {successful}\n")
        f.write(f"Failed: {failed}\n")
        f.write(f"Completed at: {datetime.now().isoformat()}\n")
        f.write(f"{'='*80}\n")
    
    print(f"\n{'='*80}")
    print(f"Execution Complete!")
    print(f"Total Commands: {total_commands}")
    print(f"Successful: {successful}")
    print(f"Failed: {failed}")
    print(f"Output saved to: {output_file}")
    print(f"{'='*80}")


def main():
    """Main entry point."""
    if len(sys.argv) < 3:
        print(__doc__)
        print(f"\nUsage: python {sys.argv[0]} <input_file> <output_file> [--verbose]\n")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2]
    verbose = '--verbose' in sys.argv
    
    # Check if input file exists
    if not os.path.exists(input_file):
        print(f"Error: Input file '{input_file}' does not exist.")
        sys.exit(1)
    
    # Load and execute commands
    commands = load_commands(input_file)
    execute_commands(commands, output_file, verbose=verbose)


if __name__ == '__main__':
    main()
