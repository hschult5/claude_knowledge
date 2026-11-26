# Hooks

*Part of the [Claude Code knowledge base](README.md). Every topic file uses the same sections: What & when · How it works · Guide · Reference · Examples · Best practices · Security · Checklist.*

## 1. What & when

**Hooks** are handlers that the Claude Code runtime runs automatically at fixed points in the lifecycle. Unlike CLAUDE.md or skills, they are **deterministic**: they always run, regardless of what the model "decides".

Use them for things that **must** happen: format after edits, block dangerous commands, protect files, run tests before Claude stops, notify, log, inject fresh context.

Rule of thumb: **if a CLAUDE.md line keeps getting ignored, turn it into a hook.**

## 2. How it works

Event → matcher group → handlers. The runtime sends the event as JSON on **stdin**; the handler answers via exit code and/or JSON on stdout.

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "command",
            "if": "Bash(rm *)",
            "command": "\"$CLAUDE_PROJECT_DIR\"/.claude/hooks/block-rm.sh",
            "timeout": 30
          }
        ]
      }
    ]
  }
}
```

- **Matcher:** `""`, `"*"` or omitted = everything; `Edit|Write` = exact names; other characters = JS regex (`mcp__github__.*`).
- **`if`:** permission-rule syntax for finer filtering (`"Bash(git *)"`, `"Edit(*.ts)"`). Best-effort only, not a security boundary.

Hooks from all sources merge. `/hooks` shows what's registered (read-only).

## 3. Guide: add a hook

1. Write the script in `.claude/hooks/` (Python or Node is easiest on Windows; `jq` isn't installed by default). It reads JSON from stdin.
2. Decide the verdict mechanism: exit `2` + message on stderr (block), or exit `0` + JSON (allow/deny/ask/rewrite).
3. Register it in `.claude/settings.json` (team) or `~/.claude/settings.json` (you). Reference the script via `"$CLAUDE_PROJECT_DIR"`.
4. Guard hooks: add `"onFailure": "block"` so a crash doesn't let things through.
5. Test it by hand: `echo '{"tool_name":"Bash","tool_input":{"command":"rm -rf /"}}' | python .claude/hooks/block_dangerous.py; echo $?`
6. Check with `/hooks`, then trigger it in a session. `/doctor` reports slow hooks.

## 4. Reference

### Where they're configured

| File | Scope |
|---|---|
| `~/.claude/settings.json` | All your projects (this machine) |
| `.claude/settings.json` | Project, committed / shared |
| `.claude/settings.local.json` | Project, just you (gitignored) |
| Managed policy settings | Organization-wide |
| Plugin `hooks/hooks.json` | While the plugin is enabled |
| Skill / subagent frontmatter (`hooks:`) | While that skill/agent is active |

### Events (most useful first)

| Event | Fires when | Matcher on |
|---|---|---|
| `PreToolUse` | Before a tool call. **Can block / rewrite it** | Tool name |
| `PostToolUse` | After a tool call succeeds | Tool name |
| `PostToolUseFailure` | After a tool call fails | Tool name |
| `PermissionRequest` | A tool needs a permission decision | Tool name |
| `UserPromptSubmit` | You send a prompt (can block or add context) | – |
| `Stop` | Claude finishes its response (can force it to continue) | – |
| `SubagentStart` / `SubagentStop` | Subagent spawned / done | Agent type |
| `SessionStart` | Session starts/resumes (inject context!) | `startup`, `resume`, `clear`, `compact` |
| `SessionEnd` | Session ends | Reason |
| `Notification` | Claude Code wants your attention | Notification type |
| `PreCompact` / `PostCompact` | Around context compaction | `manual`, `auto` |
| `InstructionsLoaded` | A CLAUDE.md / rules file loads | Load reason |
| `ConfigChange` | A settings file changes mid-session | Config source |
| `FileChanged`, `CwdChanged`, `WorktreeCreate/Remove`, `TaskCreated/Completed`, … | See reference | |

### Handler types

| `type` | What it does |
|---|---|
| `command` | Runs a shell command; event JSON on stdin |
| `http` | POSTs the event JSON to a URL |
| `mcp_tool` | Calls a tool on a configured MCP server |
| `prompt` | Asks a Claude model for a one-shot decision |
| `agent` | Spawns a subagent that can use tools to verify something (experimental) |

Common fields: `timeout` (default 600 s), `statusMessage`, `once`, `onFailure: "block"`. Command-only: `args` (exec form, no shell), `async`, `shell: "bash" | "powershell"`.

### Input (stdin JSON)

Every event: `session_id`, `transcript_path`, `cwd`, `permission_mode`, `hook_event_name` (+ `agent_id`/`agent_type` in subagents). Tool events add `tool_name`, `tool_input`, `tool_use_id`:

```json
{ "hook_event_name": "PreToolUse", "tool_name": "Bash", "tool_input": { "command": "npm test" }, "cwd": "/home/me/project" }
```

### Output: exit codes

| Exit | Effect |
|---|---|
| `0` | Success. Stdout parsed as JSON if it's one object; on `SessionStart` / `UserPromptSubmit` plain stdout is added to context |
| `2` | **Blocking.** stderr is fed back to Claude as the reason |
| other | Non-blocking error, action proceeds. **Exit 1 does NOT block** |

### Output: JSON

```json
{
  "hookSpecificOutput": {
    "hookEventName": "PreToolUse",
    "permissionDecision": "deny",
    "permissionDecisionReason": "Writes to prod DB are not allowed"
  }
}
```

- `permissionDecision`: `allow` | `deny` | `ask` | `defer`
- `updatedInput` (rewrite tool args), `additionalContext` (inject text), `updatedToolOutput` (PostToolUse)
- Top-level `{"decision": "block", "reason": "..."}` for `UserPromptSubmit`, `PostToolUse`, `Stop`
- Universal: `continue: false` + `stopReason`, `systemMessage`
- A hook returning `allow` does **not** override a deny/ask permission rule.

### Environment variables

`CLAUDE_PROJECT_DIR`, `CLAUDE_PLUGIN_ROOT`, `CLAUDE_PLUGIN_DATA`, `CLAUDE_EFFORT`, `CLAUDE_CODE_REMOTE` (`"true"` in web sessions).

### Windows notes

- Without Git Bash, shell-form commands run in **PowerShell**. Install Git for Windows (or set `CLAUDE_CODE_GIT_BASH_PATH`) for bash scripts.
- `"shell": "powershell"` forces PowerShell for one hook.
- Exec form (`args`) can't run `.cmd`/`.bat` shims; call `node path/to/script.js`.
- Without Git Bash only exit codes `0` and `2` count as a verdict.

## 5. Examples

All copyable from [examples/hooks/](examples/hooks/) ([settings.example.json](examples/hooks/settings.example.json) wires them up).

**Block destructive commands** (`PreToolUse` on `Bash`, exit 2) – [block_dangerous.py](examples/hooks/block_dangerous.py):

```python
import json, re, sys

BLOCKED = [
    (r"\brm\s+-[a-z]*r[a-z]*f\b|\brm\s+-[a-z]*f[a-z]*r\b", "Recursive force delete (rm -rf) is blocked."),
    (r"\bgit\s+push\b.*--force(?!-with-lease)", "Use --force-with-lease instead of --force."),
    (r"\bgit\s+reset\s+--hard\b", "git reset --hard is blocked; stash or commit first."),
    (r"\bDROP\s+(TABLE|DATABASE)\b", "DROP statements are blocked."),
]
command = json.load(sys.stdin).get("tool_input", {}).get("command", "")
for pattern, reason in BLOCKED:
    if re.search(pattern, command, re.IGNORECASE):
        print(f"Blocked by hook: {reason}", file=sys.stderr)
        sys.exit(2)
sys.exit(0)
```

**Protect files** (`PreToolUse` on `Edit|Write`, JSON deny) – [protect_files.py](examples/hooks/protect_files.py): denies edits to `.env*`, `*.pem`, `secrets/`, generated code, lockfiles.

**Auto-format** (`PostToolUse` on `Edit|Write`) – [auto_format.py](examples/hooks/auto_format.py): runs ruff/prettier/csharpier on the edited file, never blocks.

**Tests must pass before Claude stops** (`Stop`):

```json
{
  "hooks": {
    "Stop": [
      { "hooks": [ { "type": "command", "command": "npm test --silent >&2 || exit 2", "timeout": 300 } ] }
    ]
  }
}
```

Exit 2 sends the failing output back and Claude keeps working (capped at 8 consecutive blocks, `CLAUDE_CODE_STOP_HOOK_BLOCK_CAP`).

**Inject fresh context** (`SessionStart`):

```json
{ "matcher": "startup|resume", "hooks": [ { "type": "command", "command": "git branch --show-current && git log --oneline -5" } ] }
```

**Sound on notification (Windows)**:

```json
{ "matcher": "", "hooks": [ { "type": "command", "shell": "powershell", "command": "[System.Media.SystemSounds]::Asterisk.Play()" } ] }
```

## 6. Best practices

- Hooks for *must*, CLAUDE.md/skills for *should*.
- Keep them fast; slow hooks slow every tool call.
- Prefer `PreToolUse` + exit 2 with a clear stderr message: Claude reads it and adapts.
- Use `SessionStart` for dynamic context instead of bloating CLAUDE.md.
- Put scripts in `.claude/hooks/`, reference via `$CLAUDE_PROJECT_DIR`, commit them.
- Non-guard hooks (formatters, notifications) should never block: always exit 0.

## 7. Security

- **Hooks run arbitrary code with your user rights**, automatically, outside the [sandbox](permissions.md). A cloned repo's `.claude/settings.json` can contain hooks: **review them before running Claude Code there** (the workspace trust dialog is your moment to check).
- **Fail closed:** guard hooks get `"onFailure": "block"`; otherwise a crash or timeout lets the action through. Remember exit 1 does *not* block.
- **Pattern hooks are bypassable** (`r''m -rf`, `bash -c "$(echo …)"`, a Python script). They catch accidents, not attackers. Combine with permission deny rules and the sandbox.
- **Injection in your hook:** quote path variables (`"$CLAUDE_PROJECT_DIR"`), prefer exec form `args`, never `eval` tool input, never build shell strings from `tool_input`.
- `if` filters and timeouts are not a security boundary.
- `http` hooks send the full event (including file contents and commands) to a URL: only to endpoints you control, over HTTPS.
- Hook scripts in `.claude/hooks` are write-protected in the sandbox; without the sandbox the agent could edit its own guards. Watch for that in diffs, or use a `ConfigChange` hook to log/block settings changes.
- Admins: `allowManagedHooksOnly` restricts hooks to managed ones.
- `claude --bare` skips **all** hooks, including your guards.

## 8. Checklist

- [ ] Guard hooks: `PreToolUse`, exit 2 / JSON deny, `onFailure: "block"`
- [ ] Formatter / notification hooks never block
- [ ] Scripts quoted, no shell-string building from tool input
- [ ] Tested by piping sample JSON
- [ ] Foreign repos: `.claude/settings.json` hooks reviewed before first run
- [ ] Not relied on as the only security layer

Sources: https://code.claude.com/docs/en/hooks · https://code.claude.com/docs/en/hooks-guide
