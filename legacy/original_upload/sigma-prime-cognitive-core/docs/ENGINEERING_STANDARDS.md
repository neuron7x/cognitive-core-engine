# ENGINEERING_STANDARDS.md — Enforceable Quality Gates

This repository adopts the **Expert Coder & Math Architect** protocol. CI enforces:
- Static analysis: ruff, black --check, mypy(strict), pylint.
- Tests: pytest + hypothesis, coverage ≥95%.
- Math validation: SymPy-based checks where feasible.
- Docs: LaTeX snippets in docstrings for formulas.

Use `make all` before pushing. See `docs/SYSTEM_PROMPT_EXPERT.md`.
