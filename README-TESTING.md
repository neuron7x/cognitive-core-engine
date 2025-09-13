# Testing & CI/CD

Use the provided `Makefile` for local workflows:

```
make setup
make lint
make test
make coverage
make security
make fmt
```

GitHub Actions runs on every push and pull request. The pipeline auto-detects the project stack and executes linting, type checking, unit tests with coverage, and security scans. Reports (JUnit, coverage, and security) are uploaded as workflow artifacts.

Container images are built for each branch and commit and published to GHCR with tags matching the branch name and commit SHA; the default branch also receives the `latest` tag. If a Node build outputs a static site, a preview is deployed to GitHub Pages for that branch.
