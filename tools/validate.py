import subprocess
import sys

COMMANDS = [
    ["ruff", "check", "."],
    ["black", "--check", "."],
    ["isort", "--check-only", "."],
    ["pytest", "-q"],
]

for command in COMMANDS:
    result = subprocess.run(command)
    if result.returncode != 0:
        sys.exit(result.returncode)

sys.exit(0)
