# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

This is the **observability** project (https://github.com/mattcline/observability.git) — a Claude Code plugin that logs bash commands to JSONL files for analysis and debugging.

## Architecture

- **Plugin type:** Claude Code PostToolUse hook (fires after each `Bash` tool call)
- **Language:** Python 3 (stdlib only for core, pytest for tests)
- **Log format:** JSONL, date-partitioned (`bash-commands-YYYY-MM-DD.jsonl`)
- **Log location:** `~/.claude/logs/` (override with `CLAUDE_OBSERVABILITY_LOG_DIR`)

## File Structure

- `hooks/log_bash_command.py` — Hook entry point (reads stdin JSON, calls logger)
- `hooks/hooks.json` — Hook configuration (PostToolUse, Bash matcher)
- `lib/config.py` — Constants (LOG_DIR, LOG_FORMAT_VERSION)
- `lib/logger.py` — Core logging logic (builds JSONL entries, writes to disk)
- `.claude-plugin/plugin.json` — Plugin manifest

## Development

```bash
# Install dependencies
pip install -r requirements.txt

# Run all tests
python3 -m pytest tests/ -v

# Run only unit tests
python3 -m pytest tests/test_logger.py -v

# Run only integration tests
python3 -m pytest tests/test_log_bash_command.py -v
```

## Dependencies

- **Runtime:** Python 3 stdlib only (no pip packages)
- **Dev:** pytest (managed via `requirements.in` / `pip-compile`)
- Update `requirements.in` then run `pip-compile` to regenerate `requirements.txt`
