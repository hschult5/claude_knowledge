"""PreToolUse hook for Edit|Write: deny edits to protected paths.

Shows the JSON-output style instead of exit code 2.
"""
import json
import sys
from fnmatch import fnmatch

PROTECTED = [".env", ".env.*", "*.pem", "*/secrets/*", "*/Generated/*", "package-lock.json"]

event = json.load(sys.stdin)
path = event.get("tool_input", {}).get("file_path", "").replace("\\", "/")

if any(fnmatch(path, p) or fnmatch(path.split("/")[-1], p) for p in PROTECTED):
    print(json.dumps({
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "deny",
            "permissionDecisionReason": f"{path} is protected. Ask the user before changing it.",
        }
    }))

sys.exit(0)
