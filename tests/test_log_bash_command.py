import json
import os
import subprocess
import sys
from pathlib import Path

HOOK_SCRIPT = str(Path(__file__).resolve().parent.parent / "hooks" / "log_bash_command.py")
PLUGIN_ROOT = str(Path(__file__).resolve().parent.parent)


def run_hook(input_data, log_dir):
    """Run the hook script as a subprocess, returning (exit_code, stdout, stderr)."""
    env = {
        **os.environ,
        "CLAUDE_PLUGIN_ROOT": PLUGIN_ROOT,
        "CLAUDE_OBSERVABILITY_LOG_DIR": str(log_dir),
    }
    result = subprocess.run(
        [sys.executable, HOOK_SCRIPT],
        input=json.dumps(input_data),
        capture_output=True,
        text=True,
        env=env,
        timeout=10,
    )
    return result.returncode, result.stdout.strip(), result.stderr.strip()


def test_valid_input_creates_log(tmp_path):
    input_data = {
        "session_id": "sess-001",
        "cwd": "/home/user/project",
        "tool_name": "Bash",
        "tool_input": {
            "command": "git status",
            "description": "Show working tree status",
        },
        "tool_response": "On branch main\nnothing to commit",
    }

    exit_code, stdout, stderr = run_hook(input_data, tmp_path)

    assert exit_code == 0
    assert stdout == "{}"

    log_files = list(tmp_path.glob("bash-commands-*.jsonl"))
    assert len(log_files) == 1

    entry = json.loads(log_files[0].read_text().strip())
    assert entry["command"] == "git status"
    assert entry["session_id"] == "sess-001"
    assert entry["cwd"] == "/home/user/project"
    assert entry["description"] == "Show working tree status"
    assert entry["result_preview"] == "On branch main\nnothing to commit"


def test_invalid_json_input_exits_zero(tmp_path):
    env = {
        **os.environ,
        "CLAUDE_PLUGIN_ROOT": PLUGIN_ROOT,
        "CLAUDE_OBSERVABILITY_LOG_DIR": str(tmp_path),
    }
    result = subprocess.run(
        [sys.executable, HOOK_SCRIPT],
        input="this is not json",
        capture_output=True,
        text=True,
        env=env,
        timeout=10,
    )

    assert result.returncode == 0
    assert result.stdout.strip() == "{}"


def test_missing_fields_exits_zero(tmp_path):
    input_data = {"session_id": "s1"}  # Missing tool_input, tool_response, cwd

    exit_code, stdout, stderr = run_hook(input_data, tmp_path)

    assert exit_code == 0
    assert stdout == "{}"

    # Should still log with empty defaults
    log_files = list(tmp_path.glob("bash-commands-*.jsonl"))
    assert len(log_files) == 1

    entry = json.loads(log_files[0].read_text().strip())
    assert entry["command"] == ""
    assert entry["session_id"] == "s1"


def test_empty_stdin_exits_zero(tmp_path):
    env = {
        **os.environ,
        "CLAUDE_PLUGIN_ROOT": PLUGIN_ROOT,
        "CLAUDE_OBSERVABILITY_LOG_DIR": str(tmp_path),
    }
    result = subprocess.run(
        [sys.executable, HOOK_SCRIPT],
        input="",
        capture_output=True,
        text=True,
        env=env,
        timeout=10,
    )

    assert result.returncode == 0
    assert result.stdout.strip() == "{}"


def test_tool_response_as_dict(tmp_path):
    input_data = {
        "session_id": "s2",
        "cwd": "/tmp",
        "tool_input": {"command": "ls"},
        "tool_response": {"stdout": "file1.txt\nfile2.txt", "exitCode": 0},
    }

    exit_code, stdout, stderr = run_hook(input_data, tmp_path)

    assert exit_code == 0

    log_files = list(tmp_path.glob("bash-commands-*.jsonl"))
    entry = json.loads(log_files[0].read_text().strip())
    assert entry["result_preview"] == "file1.txt\nfile2.txt"


def test_multiple_commands_append(tmp_path):
    for i in range(3):
        input_data = {
            "session_id": "s3",
            "cwd": "/tmp",
            "tool_input": {"command": f"echo {i}"},
            "tool_response": str(i),
        }
        run_hook(input_data, tmp_path)

    log_files = list(tmp_path.glob("bash-commands-*.jsonl"))
    assert len(log_files) == 1

    lines = log_files[0].read_text().strip().split("\n")
    assert len(lines) == 3

    for i, line in enumerate(lines):
        entry = json.loads(line)
        assert entry["command"] == f"echo {i}"
