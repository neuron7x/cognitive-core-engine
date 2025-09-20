# Security

Report vulnerabilities privately.

## Secret Handling in Logs

Operational logs must never contain plaintext credentials or API tokens. The Redis
rate limiter now fingerprints API keys with the `_token_fingerprint` helper before
logging error messages, emitting only the first 12 characters of a SHA-256 digest.
Empty or missing tokens are rendered as `<empty-token>` so that no raw secret
material is ever written to disk. Any new logging around secrets should follow the
same redaction or hashing strategy.
