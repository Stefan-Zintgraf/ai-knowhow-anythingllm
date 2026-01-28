#!/usr/bin/env python3
"""
Run a command on the Mac mini via SSH and save output to files.

Usage:
    python run_mac_cmd.py <command> [arg1] [arg2] ...

Example:
    python run_mac_cmd.py hostname
    python run_mac_cmd.py ls -l
    python run_mac_cmd.py echo "Hello" "World"
"""

import subprocess
import sys
import argparse
import uuid


# Mac mini connection details
MAC_IP = "172.17.5.114"
MAC_USER = "rte"
MAC_PASSWORD = "r88te250"
STDOUT_FILE = "mac_cmd_stdout.txt"
STDERR_FILE = "mac_cmd_stderr.txt"


def run_mac_command(command, *args):
    """
    Run a command on the Mac mini via SSH.
    
    Args:
        command: The command to run
        *args: Optional arguments for the command
    
    Returns:
        tuple: (stdout, stderr, return_code)
    """
    # Build the full command string
    if args:
        # Escape arguments properly for shell execution using single quotes
        # Single quotes work better for SSH commands
        def escape_arg(arg):
            # Replace single quotes with '\'' (end quote, escaped quote, start quote)
            return "'" + arg.replace("'", "'\\''") + "'"
        
        cmd_parts = [command] + [escape_arg(str(arg)) for arg in args]
        full_cmd = " ".join(cmd_parts)
    else:
        full_cmd = command
    
    # Create unique delimiter and temp file for stderr separation
    delimiter = f"__MAC_CMD_STDERR_DELIMITER_{uuid.uuid4().hex[:16]}__"
    stderr_file = f"/tmp/mac_cmd_stderr_{uuid.uuid4().hex[:16]}.txt"
    
    # Wrap command to separate stdout and stderr
    # Source shell config first to ensure PATH and other env vars are set (needed for brew, etc.)
    # Try multiple config files and also add common Homebrew paths to PATH
    # Format: source config files; export PATH; { command >stdout 2>stderr_file; echo delimiter; cat stderr_file; rm stderr_file; }
    wrapped_cmd = (
        f"source ~/.zprofile 2>/dev/null || true; "
        f"source ~/.zshrc 2>/dev/null || true; "
        f"source ~/.bash_profile 2>/dev/null || true; "
        f"export PATH=\"/opt/homebrew/bin:/usr/local/bin:$PATH\"; "
        f"{{ {full_cmd}; }} >/dev/stdout 2>{stderr_file}; "
        f"echo '{delimiter}'; "
        f"cat {stderr_file}; "
        f"rm -f {stderr_file}"
    )
    
    # Build plink command
    plink_cmd = [
        "plink",
        "-ssh",
        "-pw", MAC_PASSWORD,
        f"{MAC_USER}@{MAC_IP}",
        wrapped_cmd
    ]
    
    try:
        print(f"Running command on Mac mini: {full_cmd}", file=sys.stderr)
        
        # Run the command and capture output
        result = subprocess.run(
            plink_cmd,
            capture_output=True,
            text=True,
            timeout=30
        )
        
        output = result.stdout
        return_code = result.returncode
        
        # Filter out plink's keyboard-interactive prompts
        if output:
            lines = output.split('\n')
            filtered_lines = []
            skip = False
            for line in lines:
                if 'Keyboard-interactive authentication prompts' in line:
                    skip = True
                elif 'End of keyboard-interactive prompts' in line:
                    skip = False
                    continue
                elif not skip:
                    filtered_lines.append(line)
            output = '\n'.join(filtered_lines)
        
        # Split stdout and stderr using the delimiter
        if delimiter in output:
            parts = output.split(delimiter, 1)
            stdout = parts[0].rstrip('\n')
            # stderr is everything after the delimiter, remove the trailing newline from cat
            stderr = parts[1].rstrip('\n') if len(parts) > 1 else ""
        else:
            # Delimiter not found, treat all as stdout (command may have failed before delimiter)
            stdout = output.rstrip('\n')
            stderr = ""
        
        # If plink_stderr has content (plink diagnostics), we could append it, but typically it's empty
        # after filtering, so we'll just use the remote stderr we captured
        
        return stdout, stderr, return_code
        
    except subprocess.TimeoutExpired:
        error_msg = f"Command timed out after 30 seconds"
        print(error_msg, file=sys.stderr)
        return "", error_msg, -1
    except FileNotFoundError:
        error_msg = "Error: plink.exe not found. Please ensure PuTTY is installed."
        print(error_msg, file=sys.stderr)
        return "", error_msg, -1
    except Exception as e:
        error_msg = f"Error running command: {e}"
        print(error_msg, file=sys.stderr)
        return "", error_msg, -1


def main():
    parser = argparse.ArgumentParser(
        description="Run a command on the Mac mini via SSH",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python run_mac_cmd.py hostname
  python run_mac_cmd.py ls -l
  python run_mac_cmd.py echo "Hello" "World"
  python run_mac_cmd.py date
  python run_mac_cmd.py whoami
        """
    )
    
    parser.add_argument("command", help="The command to run on the Mac mini")
    parser.add_argument("args", nargs="*", help="Optional arguments for the command")
    
    args = parser.parse_args()
    
    # Run the command
    stdout, stderr, return_code = run_mac_command(args.command, *args.args)
    
    # Write stdout to file
    try:
        with open(STDOUT_FILE, 'w', encoding='utf-8') as f:
            f.write(stdout)
        print(f"✓ stdout written to {STDOUT_FILE}", file=sys.stderr)
    except Exception as e:
        print(f"Error writing stdout file: {e}", file=sys.stderr)
        sys.exit(1)
    
    # Write stderr to file
    try:
        with open(STDERR_FILE, 'w', encoding='utf-8') as f:
            f.write(stderr)
        if stderr:
            print(f"✓ stderr written to {STDERR_FILE}", file=sys.stderr)
        else:
            print(f"✓ stderr file created (empty): {STDERR_FILE}", file=sys.stderr)
    except Exception as e:
        print(f"Error writing stderr file: {e}", file=sys.stderr)
        sys.exit(1)
    
    # Print summary
    print(f"\nCommand exit code: {return_code}", file=sys.stderr)
    print(f"stdout length: {len(stdout)} characters", file=sys.stderr)
    print(f"stderr length: {len(stderr)} characters", file=sys.stderr)
    
    # Exit with the command's return code
    sys.exit(return_code if return_code >= 0 else 1)


if __name__ == "__main__":
    main()
