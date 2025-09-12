import subprocess, sys

def run_sanitize(path):
    proc = subprocess.run([sys.executable, ".github/scripts/zipci_sanitize.py", path],
                          capture_output=True, text=True)
    out = proc.stdout + proc.stderr
    return proc.returncode, out
