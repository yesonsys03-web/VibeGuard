# VibeLign — Engine API Specification

Core modules expose functions used by CLI and GUI.

Canonical API contracts:

All structured responses use this envelope:

```json
{
  "ok": true,
  "error": null,
  "data": {}
}
```

Error envelope:

```json
{
  "ok": false,
  "error": {
    "code": "invalid_input",
    "message": "Human-readable error",
    "hint": "Suggested next step"
  },
  "data": null
}
```

Core APIs:

`analyze_project(root_path, strict=false)`

- input: project root path, strict flag
- output: project analysis report plus structural findings

`detect_anchors(root_path, target_path=null, mode="suggest")`

- input: project root path, optional target path, mode
- output: anchor recommendation or validation report

`build_patch(request_text, target_path=null, preview=false)`

- input: natural-language request, optional target path, preview flag
- output: patch prompt, selected target, confidence score, constraints

`build_patch` data example:

```json
{
  "schema_version": 1,
  "request": "add progress bar",
  "interpretation": "Add a progress bar to the pipeline worker UI",
  "target_file": "src/ui/pipeline_panel.py",
  "target_anchor": "ui_pipeline_worker",
  "confidence": 0.82,
  "codespeak": "ui.component.progress_bar.add",
  "constraints": [
    "patch only",
    "keep file structure",
    "no unrelated edits"
  ],
  "preview_available": true,
  "clarifying_questions": []
}
```

`patch_plan` required fields:

- `schema_version`
- `request`
- `interpretation`
- `target_file`
- `target_anchor`
- `codespeak`
- `constraints`
- `confidence`

`patch_plan` optional fields:

- `preview_available`
- `reason`
- `clarifying_questions`

`generate_preview(patch_plan, format="ascii")`

- input: patch plan object, preview format
- output: preview summary and renderable payload

`patch_plan` contract:

```json
{
  "schema_version": 1,
  "request": "add progress bar",
  "target_file": "src/ui/pipeline_panel.py",
  "target_anchor": "ui_pipeline_worker",
  "codespeak": "ui.component.progress_bar.add",
  "constraints": ["patch only"],
  "confidence": 0.82
}
```

Preview payload required fields:

- `schema_version`
- `format`
- `target_file`
- `target_anchor`
- `before_summary`
- `after_summary`
- `confidence`

`generate_preview` data example:

```json
{
  "schema_version": 1,
  "format": "ascii",
  "target_file": "src/ui/pipeline_panel.py",
  "target_anchor": "ui_pipeline_worker",
  "before_summary": "UI has no progress bar",
  "after_summary": "UI shows progress bar in pipeline worker",
  "confidence": 0.82
}
```

`run_guard(root_path, strict=false)`

- input: project root path, strict flag
- output: verification report with pass/fail status and findings

`run_guard` data example:

```json
{
  "status": "warn",
  "strict": false,
  "checks": {
    "structural_damage": "pass",
    "anchor_regression": "warn",
    "oversized_file_regression": "pass"
  },
  "blocking_failures": 0,
  "warnings": 1
}
```

Contract rules:

- CLI commands reuse these shapes for `--json` output.
- `vib patch --json` returns the envelope with `data.patch_plan`.
- `vib patch --preview --json` returns the envelope with both `data.patch_plan` and `data.preview`.
- `format="html"` is post-MVP for preview generation.
- unsupported schema or missing metadata must return a structured error envelope.
- low-confidence patch requests may include `clarifying_questions` instead of a fully actionable target
