# VibeLign — Preview Engine

Preview types:

ASCII preview
HTML preview (post-MVP)
Screenshot preview (future)

Purpose:

Show expected changes before applying patches.

Canonical MVP exposure:

- `vib patch --preview`
- no standalone `vib preview` command in MVP

MVP preview input:

- user request
- selected target file
- selected anchor
- generated patch constraints

MVP preview output:

- target summary
- expected before/after description
- confidence score
- machine-readable JSON when preview is requested with JSON output

Preview payload shape is defined by the Engine API specification.

JSON rule in MVP:

- `vib patch --json` returns `data.patch_plan`
- `vib patch --preview --json` returns `data.patch_plan` plus `data.preview`
