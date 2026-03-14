# VibeLign — Simulation Engine

Simulation applies patches inside a temporary project clone.

Scope rule:

- Simulation Engine is post-MVP.
- MVP verification is handled by `vib guard` plus direct structural checks.

Steps:

1 clone project
2 apply patch
3 run checks
4 produce risk report

Post-MVP checks may include:

- lint
- tests
- build
- structural regression checks
