Recommended smoke tests before publishing:
- python -m compileall vibelign
- vibelign doctor
- vibelign anchor --dry-run
- vibelign patch add progress bar --json
- vibelign explain --json
- vibelign guard --json
- vibelign export claude
- vibelign watch  # after installing watchdog
