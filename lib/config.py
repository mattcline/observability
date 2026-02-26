import os
from pathlib import Path

LOG_DIR = Path(
    os.environ.get("CLAUDE_OBSERVABILITY_LOG_DIR", os.path.expanduser("~/.claude/logs"))
)

LOG_FORMAT_VERSION = 1
