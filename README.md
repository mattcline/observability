# Observability

Chrome DevTools for Claude Code — a plugin that logs all bash commands executed during Claude Code sessions into JSONL files for analysis and debugging.

## Installation

Add this plugin to Claude Code:

```bash
claude plugins add /path/to/observability
```

## How It Works

The plugin uses a **PostToolUse hook** that fires after every `Bash` tool call. It captures the command, description, working directory, output preview, and session ID, then appends a JSON line to a date-partitioned log file.

Logs are written to `~/.claude/logs/` by default (override with `CLAUDE_OBSERVABILITY_LOG_DIR`).

## Log Format

Each line in `bash-commands-YYYY-MM-DD.jsonl` is a JSON object:

```json
{
  "version": 1,
  "timestamp": "2026-02-26T18:30:45.123456+00:00",
  "session_id": "a1b2c3",
  "tool": "Bash",
  "command": "git status",
  "description": "Show working tree status",
  "cwd": "/Users/you/project",
  "result_length": 142,
  "result_preview": "On branch main\n...",
  "exit_code": null
}
```

## Querying Logs

```bash
# Pretty-print today's logs
cat ~/.claude/logs/bash-commands-$(date +%Y-%m-%d).jsonl | jq .

# List all commands from a session
cat ~/.claude/logs/bash-commands-*.jsonl | jq -r 'select(.session_id == "abc123") | .command'

# Find long-running outputs (truncated)
cat ~/.claude/logs/bash-commands-*.jsonl | jq 'select(.result_length > 500)'

# Count commands per session
cat ~/.claude/logs/bash-commands-*.jsonl | jq -r '.session_id' | sort | uniq -c | sort -rn
```

## Development

```bash
# Install dependencies
pip install -r requirements.txt

# Run tests
python3 -m pytest tests/ -v
```

## Configuration

| Environment Variable | Default | Description |
|---|---|---|
| `CLAUDE_OBSERVABILITY_LOG_DIR` | `~/.claude/logs` | Directory for log files |
