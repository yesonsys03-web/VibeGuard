# VibeLign — Configuration System

Config file:

.vibelign/config.yaml

Example:

schema_version: 1
llm_provider: anthropic
api_key: ENV
preview_format: ascii

MVP schema:

- `schema_version`: required integer
- `llm_provider`: required string
- `api_key`: required string or `ENV`
- `preview_format`: required string, `ascii` only in MVP

Ownership rules:

- `vib init` creates the file if missing
- `vib config` is the post-MVP interactive writer
- other commands may read but must not silently rewrite config
