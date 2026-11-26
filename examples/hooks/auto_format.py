"""PostToolUse hook for Edit|Write: run a formatter on the edited file.

Adjust FORMATTERS to your stack. Errors are non-blocking (exit 0 always),
so a missing formatter never stops Claude.
"""
import json
import subprocess
import sys
from pathlib import Path

FORMATTERS = {
    ".py": ["ruff", "format"],
    ".ts": ["npx", "prettier", "--write"],
    ".tsx": ["npx", "prettier", "--write"],
    ".js": ["npx", "prettier", "--write"],
    ".json": ["npx", "prettier", "--write"],
    ".cs": ["dotnet", "csharpier", "format"],
}

event = json.load(sys.stdin)
file_path = event.get("tool_input", {}).get("file_path")
if not file_path:
    sys.exit(0)

cmd = FORMATTERS.get(Path(file_path).suffix.lower())
if cmd:
    try:
        subprocess.run(cmd + [file_path], capture_output=True, timeout=50, shell=sys.platform == "win32")
    except Exception:
        pass

sys.exit(0)
