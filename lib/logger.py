import json
from datetime import datetime, timezone
from pathlib import Path

from lib.config import LOG_DIR, LOG_FORMAT_VERSION

RESULT_PREVIEW_MAX_LENGTH = 500


def log_bash_command(
    command: str,
    session_id: str = "",
    description: str = "",
    cwd: str = "",
    result: str = None,
    exit_code: int = None,
    log_dir: Path = None,
) -> Path:
    """Log a bash command execution to a date-partitioned JSONL file.

    Returns the path to the log file written to.
    """
    if log_dir is None:
        log_dir = LOG_DIR

    log_dir.mkdir(parents=True, exist_ok=True)

    result_length = len(result) if result else 0
    result_preview = ""
    if result:
        result_preview = result[:RESULT_PREVIEW_MAX_LENGTH]

    entry = {
        "version": LOG_FORMAT_VERSION,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "session_id": session_id,
        "tool": "Bash",
        "command": command,
        "description": description,
        "cwd": cwd,
        "result_length": result_length,
        "result_preview": result_preview,
        "exit_code": exit_code,
    }

    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    log_file = log_dir / f"bash-commands-{today}.jsonl"

    with open(log_file, "a") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")

    return log_file
