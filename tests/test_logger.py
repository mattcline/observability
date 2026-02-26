import json

from lib.logger import RESULT_PREVIEW_MAX_LENGTH, log_bash_command


def test_basic_logging(tmp_path):
    log_file = log_bash_command(
        command="git status",
        session_id="abc123",
        description="Show working tree status",
        cwd="/tmp/project",
        result="On branch main\nnothing to commit",
        exit_code=0,
        log_dir=tmp_path,
    )

    assert log_file.exists()
    assert log_file.name.startswith("bash-commands-")
    assert log_file.suffix == ".jsonl"

    entry = json.loads(log_file.read_text().strip())
    assert entry["version"] == 1
    assert entry["tool"] == "Bash"
    assert entry["command"] == "git status"
    assert entry["session_id"] == "abc123"
    assert entry["description"] == "Show working tree status"
    assert entry["cwd"] == "/tmp/project"
    assert entry["result_preview"] == "On branch main\nnothing to commit"
    assert entry["result_length"] == len("On branch main\nnothing to commit")
    assert entry["exit_code"] == 0
    assert "timestamp" in entry


def test_result_truncation(tmp_path):
    long_result = "x" * 1000
    log_file = log_bash_command(
        command="cat bigfile",
        result=long_result,
        log_dir=tmp_path,
    )

    entry = json.loads(log_file.read_text().strip())
    assert len(entry["result_preview"]) == RESULT_PREVIEW_MAX_LENGTH
    assert entry["result_preview"] == "x" * RESULT_PREVIEW_MAX_LENGTH
    assert entry["result_length"] == 1000


def test_result_exactly_at_limit(tmp_path):
    exact_result = "y" * RESULT_PREVIEW_MAX_LENGTH
    log_file = log_bash_command(
        command="echo",
        result=exact_result,
        log_dir=tmp_path,
    )

    entry = json.loads(log_file.read_text().strip())
    assert len(entry["result_preview"]) == RESULT_PREVIEW_MAX_LENGTH
    assert entry["result_length"] == RESULT_PREVIEW_MAX_LENGTH


def test_empty_result(tmp_path):
    log_file = log_bash_command(
        command="true",
        result="",
        log_dir=tmp_path,
    )

    entry = json.loads(log_file.read_text().strip())
    assert entry["result_preview"] == ""
    assert entry["result_length"] == 0


def test_none_result(tmp_path):
    log_file = log_bash_command(
        command="true",
        result=None,
        log_dir=tmp_path,
    )

    entry = json.loads(log_file.read_text().strip())
    assert entry["result_preview"] == ""
    assert entry["result_length"] == 0


def test_multiple_entries(tmp_path):
    for i in range(3):
        log_bash_command(
            command=f"echo {i}",
            result=str(i),
            log_dir=tmp_path,
        )

    log_files = list(tmp_path.glob("bash-commands-*.jsonl"))
    assert len(log_files) == 1

    lines = log_files[0].read_text().strip().split("\n")
    assert len(lines) == 3

    for i, line in enumerate(lines):
        entry = json.loads(line)
        assert entry["command"] == f"echo {i}"


def test_directory_creation(tmp_path):
    nested = tmp_path / "deep" / "nested" / "dir"
    log_bash_command(command="ls", log_dir=nested)
    assert nested.exists()
    assert any(nested.iterdir())


def test_special_characters_in_command(tmp_path):
    command = 'echo "hello world" && grep -r "foo bar" | head -n 5'
    log_file = log_bash_command(
        command=command,
        log_dir=tmp_path,
    )

    entry = json.loads(log_file.read_text().strip())
    assert entry["command"] == command


def test_special_characters_in_result(tmp_path):
    result = 'line1\n"quoted"\ttab\nуникод\n{"json": true}'
    log_file = log_bash_command(
        command="echo test",
        result=result,
        log_dir=tmp_path,
    )

    entry = json.loads(log_file.read_text().strip())
    assert entry["result_preview"] == result


def test_timestamp_is_utc_iso8601(tmp_path):
    log_file = log_bash_command(command="date", log_dir=tmp_path)
    entry = json.loads(log_file.read_text().strip())

    ts = entry["timestamp"]
    assert "+00:00" in ts or ts.endswith("Z")
    # Verify it's parseable
    from datetime import datetime

    datetime.fromisoformat(ts)


def test_exit_code_none_when_not_provided(tmp_path):
    log_file = log_bash_command(command="ls", log_dir=tmp_path)
    entry = json.loads(log_file.read_text().strip())
    assert entry["exit_code"] is None


def test_nonzero_exit_code(tmp_path):
    log_file = log_bash_command(
        command="false",
        exit_code=1,
        result="",
        log_dir=tmp_path,
    )

    entry = json.loads(log_file.read_text().strip())
    assert entry["exit_code"] == 1
