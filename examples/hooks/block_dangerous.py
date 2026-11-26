"""PreToolUse hook for Bash: block obviously destructive commands.

Reads the event JSON from stdin. Exit 2 + message on stderr = block,
and Claude sees the message and can choose another approach.
Exit 0 = allow.
"""
import json
import re
import sys

BLOCKED = [
    (r"\brm\s+-[a-z]*r[a-z]*f\b|\brm\s+-[a-z]*f[a-z]*r\b", "Recursive force delete (rm -rf) is blocked."),
    (r"\bgit\s+push\b.*--force(?!-with-lease)", "Use --force-with-lease instead of --force."),
    (r"\bgit\s+reset\s+--hard\b", "git reset --hard is blocked; stash or commit first."),
    (r"\bDROP\s+(TABLE|DATABASE)\b", "DROP statements are blocked."),
]

event = json.load(sys.stdin)
command = event.get("tool_input", {}).get("command", "")

for pattern, reason in BLOCKED:
    if re.search(pattern, command, re.IGNORECASE):
        print(f"Blocked by hook: {reason}", file=sys.stderr)
        sys.exit(2)

sys.exit(0)
