# VibeLign — Development Workflow

Typical workflow

vib init
vib doctor
vib checkpoint
vib anchor
vib patch --preview   # optional but canonical preview path in MVP
AI edit
vib explain
vib guard
vib history / vib undo if needed

Playground workflow for beginners:

1. say the request roughly
2. review the interpretation and CodeSpeak
3. create a checkpoint before editing
4. preview the patch when needed
5. let AI edit only after the target looks correct
6. run explain and guard
7. use history and undo if the result feels wrong

Release-ready checklist for MVP:

- patch target is anchor-bound
- preview output is reviewed when needed
- AI edit stays within requested scope
- explain output is understandable to non-developers
- guard completes without unresolved structural failures
- the workflow suggests a safe next step after each major phase
- rollback is available through checkpoint, history, and undo
