# VibeLign — `vib anchor` Final Design Spec
Version: Final Draft 1.0

This document defines the design of the `vib anchor` command.

`vib anchor` is one of the three core commands in VibeLign:

- `vib doctor`
- `vib anchor`
- `vib patch`

Its role is to create and validate safe edit zones for AI-assisted coding.

In short:

> `vib anchor` tells AI: “You may edit here, but not outside this boundary.”

---

# 1. Product Role

`vib anchor` exists to reduce uncontrolled AI changes.

Without anchors, AI often:

- rewrites entire files
- edits the wrong section
- mixes unrelated logic
- expands patch scope too broadly

Anchors create explicit boundaries so patches stay predictable.

---

# 2. Primary User Promise

When a user runs:

```bash
vib anchor
```

they should understand:

1. which files need anchors
2. where anchors should go
3. whether anchors are valid
4. whether the project is safe for AI patching

---

# 3. Core Modes

## 3.1 Suggest Mode

```bash
vib anchor --suggest
```

Shows recommended files and anchor targets without modifying code.

Use case:
- first-time setup
- cautious users
- reviewing AI-safe boundaries

---

## 3.2 Auto Mode

```bash
vib anchor --auto
vib anchor --auto src/ui/main_window.py
```

Automatically inserts anchors into recommended files or a specific file.

Use case:
- bootstrap protection quickly
- add anchors after `vib doctor`

---

## 3.3 Validate Mode

```bash
vib anchor --validate
vib anchor --validate src/ui/main_window.py
```

Checks whether anchors are well-formed and safe.

---

## 3.4 List Mode

```bash
vib anchor --list
vib anchor --list src/ui/main_window.py
```

Prints anchors detected in a project or file.

MVP status:
- post-MVP

---

## 3.5 Coverage Mode

```bash
vib anchor --coverage
```

Shows how much of the project is protected by anchors.

MVP status:
- post-MVP

---

# 4. Smart Anchor Recommendation

This is the most important feature.

`vib anchor --suggest` should not randomly insert anchors.
It should recommend boundaries based on project structure.

Anchor recommendations should use:

- project map
- file size
- module role
- code structure
- doctor findings

The goal is to answer:

> “Where should AI be allowed to edit safely?”

---

# 5. Recommendation Rules

## 5.1 Prioritize Important Risk Files

Recommend anchors first for files that are:

- large
- likely to be edited by AI
- UI-heavy
- entry-adjacent
- high-value feature files

Examples:

- `src/ui/main_window.py`
- `src/engine/patch_builder.py`
- `src/services/auth.py`

---

## 5.2 Prefer Natural Code Boundaries

Anchors should be placed around:

- class definitions
- `__init__`
- UI setup methods
- route groups
- command functions
- config blocks
- small logical sections

Avoid placing anchors across unrelated code.

---

## 5.3 Avoid Full-File Anchors by Default

Bad default:

```python
# ANCHOR START everything
... entire file ...
# ANCHOR END everything
```

This is only acceptable as a fallback.

Preferred:
multiple smaller, meaningful anchors.

---

## 5.4 Preserve Readability

Anchors should improve safety without making the file hard to read.

Anchor density should stay reasonable.

Recommended:
- 1 to 5 anchors per file for MVP
- avoid excessive fragmentation

---

# 6. Automatic Naming Rules

Anchor names must be predictable and human-readable.

Examples:

- `main_window_class`
- `main_window_init`
- `setup_ui`
- `toolbar_section`
- `routes_auth`
- `commands_doctor`

Rules:

- snake_case only
- max 64 chars
- file-local uniqueness
- stable across regeneration where possible

---

# 7. File-Type Recommendations

## 7.1 UI Files

High priority for anchors.

Recommended anchor zones:

- main window class
- init method
- setup_ui method
- sidebar section
- toolbar section
- content panel section

## 7.2 CLI Files

Recommended anchor zones:

- command functions
- command groups
- option-parsing blocks

## 7.3 Service Modules

Recommended anchor zones:

- service class
- main public methods
- config/setup sections

## 7.4 Entry Files

Use caution.

Entry files should usually remain thin.
Recommend anchors only if the file is already large and unavoidable.

---

# 8. Default Workflow

Recommended user workflow:

```bash
vib doctor
vib anchor --suggest
vib anchor --auto
vib anchor --validate
```

This keeps anchor insertion transparent and safe.

---

# 9. Suggested Default Output

## 9.1 Suggest Output Example

```text
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
VibeLign Anchor Recommendations
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Recommended files:
1. src/ui/main_window.py
   Reason: UI-heavy file, likely patch target
   Suggested anchors:
   - main_window_class
   - main_window_init
   - setup_ui
   - sidebar_section

2. src/engine/patch_builder.py
   Reason: core patch logic, high-value module
   Suggested anchors:
   - patch_builder_class
   - build_patch
   - validate_patch

3. src/main.py
   Reason: entry file is large (412 lines)
   Suggested anchors:
   - main_bootstrap
   - app_setup

Next step:
vib anchor --auto
```

---

## 9.2 Auto Output Example

```text
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
VibeLign Anchor Insertion Report
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

File: src/ui/main_window.py
Inserted:
- main_window_class
- main_window_init
- setup_ui
- sidebar_section

File: src/engine/patch_builder.py
Inserted:
- patch_builder_class
- build_patch

Summary:
2 files updated
6 anchors inserted
No source logic changed
```

---

## 9.3 Validate Output Example

```text
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
VibeLign Anchor Validation Report
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✓ src/ui/main_window.py
  - 4 valid anchors

⚠ src/main.py
  - 1 anchor crosses a function boundary

✗ src/services/auth.py
  - missing ANCHOR END for auth_routes

Summary:
1 valid file
1 warning
1 error

Run:
vib anchor --auto src/services/auth.py
```

---

# 10. Internal Data

Anchor indexing should be saved as metadata.

Suggested file:

```text
.vibelign/anchor_index.json
```

Example:

```json
{
  "schema_version": 1,
  "src/ui/main_window.py": [
    "main_window_class",
    "main_window_init",
    "setup_ui",
    "sidebar_section"
  ],
  "src/engine/patch_builder.py": [
    "patch_builder_class",
    "build_patch"
  ]
}
```

This helps:

- patch targeting
- validation speed
- coverage reporting
- GUI integration later

Metadata governance:

- `vib anchor` is the only MVP writer of `.vibelign/anchor_index.json`.
- `vib patch`, `vib doctor`, and `vib guard` may read this file in MVP.
- Anchor IDs must use snake_case and match the inserted anchor markers exactly.
- `schema_version` is required for future compatibility.

---

# 11. Safety Rules

`vib anchor` must never:

- rewrite logic
- reorder code behavior
- change imports unless explicitly required for comment placement
- alter runtime semantics

It may only insert anchor markers and metadata.

---

# 12. Recommended Internal Modules

Suggested implementation split:

```text
cli/anchor.py
analysis/anchor_recommender.py
analysis/code_boundary_detector.py
patch/anchor_manager.py
patch/anchor_validator.py
patch/anchor_index.py
engine/human_explainer.py
```

Rule:
CLI orchestrates only.
Logic lives outside the CLI layer.

---

# 13. MVP Scope

The first release of `vib anchor` should include only:

- suggest mode
- auto mode
- validate mode
- file-local anchor insertion
- anchor index generation

Authoritative MVP flags:

- `vib anchor`
- `vib anchor --suggest`
- `vib anchor --dry-run` (alias of `--suggest`)
- `vib anchor --auto`
- `vib anchor --validate`

Do NOT block MVP with:

- `--list`
- `--coverage`
- multi-language support
- advanced refactoring-aware anchoring
- semantic diff merging
- GUI integration

Those can come later.

---

# 14. Versioned Growth Plan

## v1
- suggest anchors
- auto insert anchors
- validate anchors
- anchor coverage

## v1.1
- smarter recommendations using project map
- improved naming stability
- better entry-file rules

## v1.2
- multi-language anchors
- IDE integration
- anchor visualization in GUI

---

# 15. Success Criteria

`vib anchor` is successful if:

1. users understand where AI is allowed to edit
2. anchors are inserted without breaking code
3. patch scope becomes narrower and safer
4. users can trust the recommendation output

---

# 16. One-Sentence Design Principle

> `vib anchor` should make users feel: “Now AI knows exactly where it may edit safely.”
