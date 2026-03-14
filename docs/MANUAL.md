# VibeLign Manual

This manual explains how to use VibeLign before, during, and after AI-assisted edits.

---

## 1. What VibeLign is for

VibeLign is a safety layer for AI coding workflows.

It does **not** replace your AI tool.
It helps you keep the project stable while using tools like:

- Claude Code
- OpenCode
- Cursor
- Antigravity
- general GPT-based coding workflows

The core idea is simple:

> Let AI generate code, but do not let it freely destroy project structure.
> And always make it easy to save and undo.

---

## 2. The safest workflow

### New project

```bash
vibelign init
```

This sets up everything in one command.

### Ongoing workflow

Use this loop whenever you ask AI to change code:

```bash
vibelign checkpoint "before your task"
vibelign doctor --strict
vibelign anchor
vibelign patch "your request here"
# ask AI using the generated patch request
vibelign explain --write-report
vibelign guard --strict --write-report

# if all good:
vibelign checkpoint "done: your task"

# if something broke:
vibelign undo
```

---

## 3. Command reference

---

## `vibelign init`

One-command project setup for beginners.

```bash
vibelign init
vibelign init --tool claude
vibelign init --tool cursor
vibelign init --tool opencode
vibelign init --tool antigravity
```

What it does:

1. Exports `AI_DEV_SYSTEM_SINGLE_FILE.md` and `AGENTS.md` to the project root
2. Exports tool-specific helper files (`vibelign_exports/<tool>/`)
3. Creates a `.gitignore` if one does not exist
4. Runs `git init` if the project is not a Git repo yet
5. Creates the first checkpoint automatically

After `init`, your project is fully ready for AI-assisted development.

---

## `vibelign checkpoint`

Saves the current project state as a restore point (uses Git under the hood).

```bash
vibelign checkpoint "before login feature"
vibelign checkpoint "added signup validation"
vibelign checkpoint
```

- If no message is given, a timestamp is used automatically.
- Shows a list of changed files before saving.
- Displays the total number of checkpoints saved.

Think of it as a **game save point** for your code.

---

## `vibelign undo`

Restores the project to the last checkpoint.

```bash
vibelign undo
vibelign undo --list
```

Behavior:

- If there are **unsaved changes** → restores to the last commit (like pressing "undo" in a game)
- If the working tree is **already clean** → rolls back to the previous checkpoint commit
- `--list` → shows the list of available checkpoints to choose from

Use this when AI broke something and you want to go back.

---

## `vibelign history`

Shows all saved checkpoints.

```bash
vibelign history
```

Displays:

- checkpoint number
- when it was saved (e.g. "2 hours ago")
- the message you gave it

Also shows:

- total checkpoint count
- most recent save time
- reminder of how to undo or save a new checkpoint

---

## `vibelign protect`

Locks important files so AI cannot accidentally modify them.

```bash
vibelign protect main.py
vibelign protect src/config.py
vibelign protect --list
vibelign protect --remove main.py
```

- Protected files are tracked in `.vibelign_protected`
- `guard` and `watch` will warn you if a protected file was changed
- Use this for files that must never be touched by AI

---

## `vibelign config`

Sets API keys and Gemini model preferences.

```bash
vibelign config
```

What it does:

- Guides you through saving API keys to your shell profile or current session
- If Gemini is selected, shows available Gemini model IDs
- Saves `GEMINI_MODEL` when you choose a Gemini model

Notes:

- When a Gemini API key is available, VibeLign tries to fetch the current official model list from Google AI Studio
- If the live model list cannot be fetched, VibeLign falls back to a built-in recommended Gemini model list
- Press Enter or choose `0` to keep the current Gemini model setting unchanged

---

## `vibelign ask`

Generates a plain-language explanation prompt for a file.

```bash
vibelign ask login.py
vibelign ask login.py "what does the validate function do?"
vibelign ask login.py --write
GEMINI_MODEL=gemini-2.5-flash-lite vibelign ask login.py
```

What it does:

- Reads the file
- Builds a prompt asking an AI to explain it in plain Korean
- With `--write`: saves the prompt to `VIBELIGN_ASK.md`
- Without `--write`: prints the prompt so you can copy it

Use this when you do not understand a file and want to ask AI to explain it before editing.

Notes:

- Files over 300 lines are truncated to the first 300 lines
- The prompt includes the filename, line count, and file content
- If Gemini is the provider that runs, it uses `gemini-3-flash-preview` by default
- You can override the Gemini model for one command by setting `GEMINI_MODEL`

---

## `vibelign doctor`

Checks structural issues.

```bash
vibelign doctor
vibelign doctor --strict
vibelign doctor --json
```

Looks for:

- oversized entry files
- huge files
- catch-all files
- missing anchors
- UI + business logic mixing
- too many definitions in one file

Use `--strict` when you want earlier warnings.

---

## `vibelign anchor`

Adds module-level anchors to source files that do not have them yet.

```bash
vibelign anchor
vibelign anchor --dry-run
vibelign anchor --only-ext .py,.js
```

Important behavior:

- skips docs, tests, GitHub workflow folders, virtualenvs, and dependency folders by default
- does not rewrite files that already contain anchors

Example anchor:

```python
# === ANCHOR: BACKUP_WORKER_START ===
# code
# === ANCHOR: BACKUP_WORKER_END ===
```

Why this matters:
AI can be instructed to edit only inside an anchor instead of rewriting the full file.

---

## `vibelign patch`

Builds a safer AI prompt.

```bash
vibelign patch "add progress indicator to backup worker"
vibelign patch "add progress indicator to backup worker" --json
```

Outputs:

- suggested target file
- suggested target anchor
- confidence
- rationale

It also writes:

```text
VIBELIGN_PATCH_REQUEST.md
```

This file can be pasted directly into your AI coding tool.

Notes:

- files like `__init__.py`, tests, docs, and cache folders are strongly deprioritized
- if the project has no useful source files yet, confidence becomes low

---

## `vibelign explain`

Explains recent changes in human language.

```bash
vibelign explain
vibelign explain --write-report
vibelign explain --json
vibelign explain --since-minutes 30
```

Primary mode:
- uses Git status if available

Fallback mode:
- uses recently modified files
- intentionally avoids overreacting on freshly created repos

Output includes:

- summary
- what changed
- why it matters
- risk level
- rollback hint

When `--write-report` is used, this is saved:

```text
VIBELIGN_EXPLAIN.md
```

---

## `vibelign guard`

Combines `doctor` + `explain`.

```bash
vibelign guard
vibelign guard --strict
vibelign guard --json
vibelign guard --write-report
```

This answers:

> "Is it safe to continue with another AI edit right now?"

Output includes:

- overall level
- whether the session should be considered blocked
- recommendations
- doctor findings
- recent changed files
- protected file violations (if any)

Saved report:

```text
VIBELIGN_GUARD.md
```

---

## `vibelign export`

Creates helper files for tool-specific workflows.

```bash
vibelign export claude
vibelign export opencode
vibelign export cursor
vibelign export antigravity
```

This creates:

```text
vibelign_exports/<tool>/
```

Also creates in the project root:

- `AI_DEV_SYSTEM_SINGLE_FILE.md` — the full ruleset
- `AGENTS.md` — auto-read by Claude Code, OpenCode, and other AI tools

Examples:

- Claude → `RULES.md`, `SETUP.md`, `PROMPT_TEMPLATE.md`
- OpenCode → `RULES.md`, `SETUP.md`, `PROMPT_TEMPLATE.md`
- Cursor → `RULES.md` (`.cursorrules` format), `SETUP.md`, `PROMPT_TEMPLATE.md`
- Antigravity → `TASK_ARTIFACT.md`, `VERIFICATION_CHECKLIST.md`, `SETUP.md`

---

## `vibelign watch`

Real-time monitor while AI or you edit files.

```bash
vibelign watch
vibelign watch --strict
vibelign watch --write-log
vibelign watch --json
vibelign watch --debounce-ms 800
```

Extra dependency required:

```bash
pip install watchdog
```

or

```bash
uv add watchdog
```

Watch detects:

- entry files growing too large
- catch-all filenames
- larger files with no anchors
- likely UI + business logic mixing
- likely business logic inside entry files
- changes to protected files

Log file if enabled:

```text
.vibelign/watch.log
```

State file:

```text
.vibelign/watch_state.json
```

If `watchdog` is missing, only the `watch` command fails gracefully.
All other commands continue to work.

---

## 4. Recommended project rules

Best results come from these conventions:

- run `init` when starting a new project
- save a `checkpoint` before every AI edit
- use `undo` immediately if something looks wrong
- `protect` files that must never change
- keep entry files tiny
- split large files before AI keeps growing them
- add anchors before repeated edits
- prefer patch requests over vague instructions
- run `guard` before another large AI change

---

## 5. Suggested installation strategy

Recommended:

- Python package use: `uv`
- JS helper ecosystem: `pnpm`

Still supported:

- `pip`
- `npm`

Good future distribution option on macOS:

- Homebrew

---

## 6. Troubleshooting

### `watch` says watchdog is missing
Install it:

```bash
pip install watchdog
```

### `patch` suggested the wrong file
Use the JSON output, inspect the rationale, then manually edit the generated markdown request.

### `guard` seems too noisy
Prefer Git repositories.
Fallback mtime mode is intentionally conservative, but calmer than before.

### `anchor` touched files you did not want
Use:

```bash
vibelign anchor --dry-run
vibelign anchor --only-ext .py
```

### `undo` says there are no checkpoints
Run `vibelign checkpoint "initial"` first to create your first save point.

### `protect` list is empty
Run `vibelign protect <filename>` to add files to the protected list.

---

## 7. Typical initial setup

New project:

```bash
vibelign init
```

That's it. Everything else is set up automatically.

Existing project:

```bash
vibelign doctor
vibelign anchor --dry-run
vibelign anchor
vibelign export opencode
vibelign checkpoint "vibelign added"
```

---

## 8. Final advice

The safest pattern is:

> checkpoint first, AI second, guard always

That is exactly what VibeLign is for.
