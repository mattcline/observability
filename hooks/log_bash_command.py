#!/usr/bin/env python3
"""PostToolUse hook for logging Bash commands to JSONL files.

Reads hook input JSON from stdin, logs the command, prints {} to stdout.
Always exits 0 so it never blocks Claude Code.
"""
import json
import os
import sys


def main():
    try:
        raw = sys.stdin.read()
        data = json.loads(raw)

        tool_input = data.get("tool_input", {})
        command = tool_input.get("command", "")
        description = tool_input.get("description", "")

        # tool_response can be a string or an object
        tool_response = data.get("tool_response", "")
        if isinstance(tool_response, dict):
            result = tool_response.get("stdout", tool_response.get("output", ""))
        else:
            result = str(tool_response) if tool_response else ""

        session_id = data.get("session_id", "")
        cwd = data.get("cwd", "")

        # Import lib from the plugin root
        plugin_root = os.environ.get(
            "CLAUDE_PLUGIN_ROOT", os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        )
        sys.path.insert(0, plugin_root)

        from lib.logger import log_bash_command

        log_bash_command(
            command=command,
            session_id=session_id,
            description=description,
            cwd=cwd,
            result=result,
        )
    except Exception:
        pass  # Never fail — observability must not block the user

    print("{}")
    sys.exit(0)


if __name__ == "__main__":
    main()
