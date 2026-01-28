---
name: remote-mac-command
description: Run commands on a remote Mac over SSH from Windows using scripts/run_mac_cmd.py (PuTTY plink). Use when the user says "run on mac", "mac: ", "macrun", "mac run ", "run mac command", or mentions Mac mini, remote Mac, SSH Mac, plink mac, or wants stdout/stderr from MAC captured to files.
---

# Remote Mac Command

## Quick start

Use the repo helper script to run a command on the Mac and capture output to `mac_cmd_stdout.txt` and `mac_cmd_stderr.txt`:

```powershell
python .\scripts\run_mac_cmd.py hostname
python .\scripts\run_mac_cmd.py whoami
python .\scripts\run_mac_cmd.py date
python .\scripts\run_mac_cmd.py ls -la
```

## Workflow

1. Confirm prerequisites on Windows:
   - `python` is available
   - PuTTY `plink` is installed and on `PATH` (the script invokes `plink`)

2. Run the command via the wrapper:
   - Prefer passing the command and each argument as separate CLI tokens:

```powershell
# Good: args passed separately (quoting handled by the script)
python .\scripts\run_mac_cmd.py echo "Hello" "World"
python .\scripts\run_mac_cmd.py bash -lc "echo $HOME && which python3"
```

3. Read results from files (the script writes these in the repo root):
   - `mac_cmd_stdout.txt`
   - `mac_cmd_stderr.txt`
   - Use the process exit code to decide success/failure.

## Safety and credential handling (important)

- Do **not** copy credentials into chat outputs or commit messages.
- If credentials are hardcoded in `scripts/run_mac_cmd.py`, treat that as **sensitive** and do not reproduce them.
- Prefer SSH keys (PuTTY/Pageant) or environment-based secrets over embedding passwords in code.

## Troubleshooting

- **plink.exe not found**: install PuTTY or add `plink` to `PATH`.
- **Auth/host key prompts**: ensure the host key is trusted/accepted for non-interactive runs.
- **Command works in interactive SSH but not here**: run via a login shell:

```powershell
python .\scripts\run_mac_cmd.py bash -lc "source ~/.zprofile; <your command>"
```

## Notes about the repo implementation

- The wrapper sources common shell config files and extends `PATH` (useful for Homebrew) before executing the requested command.
- It separates stdout/stderr and writes them to `mac_cmd_stdout.txt` / `mac_cmd_stderr.txt`.
