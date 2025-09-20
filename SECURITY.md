# Security

Report vulnerabilities privately.

## Secret Handling in Logs

Operational logs must never contain plaintext credentials or API tokens. The Redis
rate limiter hashes API keys (using the first 12 characters of a SHA-256 digest)
before logging error messages so that incidents can be debugged without exposing
secrets. Any new logging around secrets should follow the same redaction or
hashing strategy.
