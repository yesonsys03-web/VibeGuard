# VibeLign — CodeSpeak Grammar

Canonical MVP grammar:

CodeSpeak uses this shape:

layer.target.subject.action

Rules:

- lower_snake_case tokens only
- dot-separated hierarchy
- action comes last
- one intent per expression in MVP

Examples:

- ui.layout.sidebar.split
- ui.widget.button.add
- ui.component.progress_bar.add
- ui.theme.dark.apply

Notes:

- Patch System examples must follow this grammar.
- Alternative aliases are post-MVP.
