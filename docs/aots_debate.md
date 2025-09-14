# AOTS Debate Pipeline

This example demonstrates running multiple agent roles in a debate using
`POST /api/pipelines/aots_debate`.

## Role Profiles

Store role configuration files in `config/agents/`:

```yaml
# config/agents/proponent.yaml
name: proponent
system_prompt: "Advocate for the proposal."
model: mock
```

```yaml
# config/agents/critic.yaml
name: critic
system_prompt: "Highlight potential issues with the proposal."
model: mock
```

## Invoke the Pipeline

```http
POST /api/pipelines/aots_debate HTTP/1.1
Content-Type: application/json

{
  "prompt": "Evaluate the proposal",
  "roles": ["proponent", "critic"],
  "concurrent": true
}
```

Response:

```json
{
  "prompt": "Evaluate the proposal",
  "responses": {
    "proponent": "<mock response...>",
    "critic": "<mock response...>"
  }
}
```
