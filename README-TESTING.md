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

GitHub Actions runs on every push and pull request. The workflow begins with an autodetection step that enables language-specific jobs only when matching tooling is present in the repository. Depending on the detected stacks, the pipeline runs linters, type checkers, unit tests with coverage, and security scans for Python, Node, Go, Java, and Rust projects. Each job uploads its JUnit, coverage, and security reports as workflow artifacts so you can review the results in one place.

When a `Dockerfile` is available, the workflow builds a multi-architecture image with Buildx and pushes it to GHCR. Images are tagged with the branch name and commit SHA; pushes to the default branch also receive the `latest` tag. For Node projects that emit a static site (`dist/` or `build/`), the workflow uploads the assets and publishes a GitHub Pages preview for that branch.
