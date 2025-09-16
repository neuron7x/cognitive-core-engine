import subprocess as sp
import sys

COMMANDS = [
    ["ruff", "check", "."],
    ["black", "--check", "."],
    ["isort", "--check-only", "."],
    ["pytest", "-q"],
]


def main() -> int:
    for command in COMMANDS:
        try:
            sp.run(command, check=True)
        except sp.CalledProcessError as exc:
            print(
                f"Команда {command} завершилася з кодом {exc.returncode}",
                file=sys.stderr,
            )
            return exc.returncode
    return 0


if __name__ == "__main__":
    sys.exit(main())
