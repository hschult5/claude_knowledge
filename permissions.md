---
aliases:
  - "Permissions"
  - "Sandbox"
tags:
  - claude-code
  - claude-code/mechanism
  - security
---

# Permissions & Sandbox

*Part of the [Claude Code knowledge base](README.md). Every topic file uses the same sections: What & when · How it works · Guide · Reference · Examples · Best practices · Security · Checklist.*

## 1. What & when

The two mechanisms that decide **what Claude is allowed to do**:

| Mechanism | Controls | Enforced by |
|---|---|---|
| **Permission modes + rules** | Which tool calls run, ask, or are refused (Bash, Edit, Read, WebFetch, MCP, agents, skills) | Claude Code (pattern matching) |
| **Sandbox** | What Bash/PowerShell commands can touch on disk and network | The operating system |

You always use permissions. Turn the sandbox on when Claude runs commands with little supervision (auto mode, long tasks, unfamiliar repos).

## 2. How it works

- Every tool call is checked against the rules: **deny → ask → allow**, first match wins. A broad deny beats a narrow allow. Nothing matched → the **mode** decides.
- Read-only commands (`ls`, `cat`, `grep`, `git status`, …) run without asking inside the working dirs.
- "Yes, and don't ask again" saves an allow rule to `.claude/settings.local.json`.
- The sandbox wraps each Bash/PowerShell command in an OS-level jail (macOS Seatbelt, Linux/WSL2 bubblewrap) with a filesystem allowlist and a network proxy. Read/Edit/Write/WebFetch tools, hooks and local MCP servers run **outside** it and are governed by permission rules.

## 3. Guide: set up a safe baseline

1. **Pick the mode.** Interactive daily work: `auto` (default) or `acceptEdits`. Unfamiliar repo: `default` (Manual) or `plan`. Switch with Shift+Tab or `--permission-mode`.
2. **Add deny rules for secrets and destructive commands** in `.claude/settings.json` (team) or `~/.claude/settings.json` (you). See the baseline in §5.
3. **Put risky-but-legit commands under `ask`** (`git push`, `npm publish`, `curl`).
4. **Allow the boring stuff** you approve all the time (test, lint, `git log`), so prompts mean something again. `/fewer-permission-prompts` suggests rules from your history.
5. **Turn on the sandbox**: `/sandbox`, or `"sandbox": {"enabled": true}`. On **native Windows there is no sandbox**; run Claude Code in **WSL2** if you want one, and set `failIfUnavailable: true` so it refuses to start unsandboxed.
6. **Restrict reads and network** in the sandbox (`denyRead` for `~/.ssh` etc., `allowedDomains` for your registries).
7. **Audit regularly:** `/permissions` shows all active rules and where they come from; clean out stale "don't ask again" entries.
8. **Teams/orgs:** move the baseline into managed settings so it can't be overridden.

## 4. Reference

### Permission modes

| Mode | Behaviour | Use for |
|---|---|---|
| `default` (Manual) | Asks before edits and non-read-only commands | Unfamiliar or sensitive repos |
| `acceptEdits` | Auto-approves edits and `mkdir/touch/rm/mv/cp/sed` **inside the working dir** | Coding while you watch |
| `plan` | Read-only, proposes a plan | Exploring, designing |
| `auto` | A classifier reviews each action; default for interactive sessions | Daily work |
| `dontAsk` | Denies anything that would prompt | Headless / CI with explicit allowlist |
| `bypassPermissions` | **No prompts at all**, incl. writes to `.git` and `.claude` | **Only** in a throwaway container/VM |

Settings: `permissions.defaultMode`. Lock-outs: `permissions.disableBypassPermissionsMode: "disable"`, `permissions.disableAutoMode: "disable"`. Unattended: `permissions.denyInsteadOfPrompting`.

### Rule syntax

| Rule | Matches |
|---|---|
| `Bash(npm run build)` | Exactly that command |
| `Bash(npm run *)` | Wildcard (put `*` at the end: `Bash(git log *)`, not `Bash(git * main)`) |
| `Bash` / `Bash(*)` in deny | Removes the tool entirely |
| `PowerShell(Remove-Item *)` | PowerShell; aliases canonicalized, case-insensitive |
| `Read(./.env)`, `Read(./secrets/**)` | Files. `//path` absolute, `/path` project-relative, `~/` home. A `Read` deny also blocks `Edit`/`Write` |
| `Edit(src/**)` | Edits |
| `WebFetch(domain:example.com)`, `WebFetch(domain:*.example.com)` | Fetch by domain |
| `mcp__github`, `mcp__github__*`, `mcp__github__create_issue` | MCP server / tools; deny `mcp__*` removes all MCP tools |
| `Agent(Explore)`, `Agent(model:opus)` | Subagents |
| `Skill(deploy)` | Skills |

Compound commands are split on `&& || ; | |& &` and newlines; each part is checked. Wrappers like `timeout`, `nice`, `nohup` are stripped; runners like `npx`, `docker exec` are not.

### Settings files (highest wins)

Managed settings → CLI flags (`--allowedTools`, `--settings`) → `.claude/settings.local.json` → `.claude/settings.json` → `~/.claude/settings.json`. Managed deny can't be overridden by `--allowedTools`. Project **allow** rules apply only after you trust the folder; deny/ask apply always.

### Directories

Working dir + `--add-dir`, `/add-dir`, `permissions.additionalDirectories`. Newer: `permissions.blockReadsOutsideWorkingDirectories`, `permissions.blockWritesOutsideWorkingDirectories`.

### Sandbox settings

| Key | Meaning |
|---|---|
| `sandbox.enabled` | On/off (off by default) |
| `sandbox.failIfUnavailable` | Refuse to start if no sandbox (Windows native!) |
| `sandbox.autoAllowBashIfSandboxed` | Sandboxed commands run without prompts (deny rules still apply) |
| `sandbox.allowUnsandboxedCommands: false` | Remove the "retry outside sandbox" escape hatch |
| `sandbox.excludedCommands` | Commands that run outside (e.g. `"docker compose *"`) |
| `sandbox.filesystem.allowWrite / denyWrite / allowRead / denyRead` | Filesystem. Defaults: write cwd + temp + added dirs; **read almost everything** |
| `sandbox.network.allowedDomains / deniedDomains` | Network allowlist (starts empty); `strictAllowlist`, `allowLocalBinding` |
| `sandbox.credentials.files / envVars` | `"mode": "deny"` or `"mask"` (masked secrets are swapped in by the proxy only for allowed hosts) |

Always write-protected inside the sandbox: `.claude/settings*`, `.claude/hooks`, `.claude/skills`, `.mcp.json`, `.git/hooks`, `.bashrc`, `.gitconfig`, `.vscode`. Path convention differs from rules: in sandbox config `/tmp/x` is absolute, `~/x` is home.

## 5. Examples

**Baseline `.claude/settings.json`:**

```json
{
  "permissions": {
    "defaultMode": "acceptEdits",
    "deny": [
      "Read(./.env)", "Read(./.env.*)", "Read(./secrets/**)", "Read(./**/*.pem)",
      "Read(~/.ssh/**)", "Read(~/.aws/**)",
      "Bash(git push --force *)", "Bash(git reset --hard *)", "Bash(rm -rf *)",
      "PowerShell(Remove-Item * -Recurse *)"
    ],
    "ask": [
      "Bash(git push *)", "Bash(npm publish *)", "Bash(curl *)", "Bash(wget *)",
      "mcp__github__merge_pull_request"
    ],
    "allow": [
      "Bash(npm run test *)", "Bash(npm run lint *)",
      "Bash(git log *)", "Bash(git diff *)",
      "WebFetch(domain:docs.python.org)"
    ]
  },
  "sandbox": {
    "enabled": true,
    "failIfUnavailable": true,
    "allowUnsandboxedCommands": false,
    "filesystem": { "denyRead": ["~/.ssh", "~/.aws", "~/.config/gcloud", "~/.kube"] },
    "network": { "allowedDomains": ["registry.npmjs.org", "pypi.org", "files.pythonhosted.org", "github.com"] },
    "credentials": { "envVars": { "GITHUB_TOKEN": { "mode": "mask" } } }
  }
}
```

**Managed settings for an org** (users can't loosen these):

```json
{
  "permissions": {
    "disableBypassPermissionsMode": "disable",
    "deny": ["Read(~/.ssh/**)", "Read(~/.aws/**)", "Bash(git push --force *)"]
  },
  "allowManagedHooksOnly": true
}
```

**Headless CI run:**

```bash
claude -p "Fix the lint errors" --permission-mode dontAsk \
  --allowedTools "Read,Edit,Bash(npm run lint *),Bash(git add *),Bash(git commit *)" \
  --max-turns 20
```

## 6. Best practices

- Fewer, meaningful prompts beat many: allow the routine, ask for the risky, deny the forbidden. Prompt fatigue makes people click "yes" blindly.
- Keep shared rules in `.claude/settings.json` in git; personal ones in `settings.local.json`.
- Deny by **path** for secrets (`Read(...)`), not by command.
- Use `dontAsk` + explicit allowlist for everything unattended.
- Match isolation to autonomy (see §7 table).
- Review `/permissions` after a few weeks; remove broad allows you added in a hurry.

## 7. Security

**Know the limits:**
- **Bash rules are not a security boundary.** `Bash(curl *)` doesn't catch `/usr/bin/curl`, `sh -c 'curl …'` or a Python script opening a socket. Use the sandbox or a [hook](hooks.md) for real boundaries.
- A `Read` deny doesn't stop `grep -r` over that folder or a script that opens the file. Only the sandbox's `denyRead` stops that.
- `Grep(...)`, `Glob(...)` and `Write(...)` rules are **not enforced**; use `Read(...)` / `Edit(...)`. `.claudeignore` does nothing.
- An approved Bash command can write **anywhere your user can**, unless sandboxed.
- **Native Windows has no sandbox.** Use WSL2, a dev container or a VM for sandboxed work.
- The sandbox doesn't cover Read/Edit/WebFetch tools, hooks, or local MCP servers.
- `excludedCommands` and `dangerouslyDisableSandbox` retries are holes; keep them minimal and set `allowUnsandboxedCommands: false`.

**Never:**
- `bypassPermissions` outside a container/VM (it even allows writes to `.git` and `.claude`). Disable it via managed settings.
- Broad allows like `Bash(*)`, `Bash(python *)`, `Bash(node *)`, `WebFetch(domain:*)`: they're equivalent to "run anything" / "send anywhere".

**Isolation by autonomy:**

| Autonomy | Isolation |
|---|---|
| Watching each step | Manual / acceptEdits on your machine |
| Auto mode, interactive | Sandbox (WSL2 on Windows) + deny rules |
| Unattended / headless / bypass | **Dev container or VM**, no prod credentials, network allowlist, own branch/worktree |
| Cloud sessions (claude.ai/code) | Anthropic-managed VM; GitHub proxy blocks branch deletes and non-branch pushes |

Remote Control runs **locally** with no VM or sandbox. `claude -p` shows neither the trust dialog nor MCP approval prompts.

## 8. Checklist

- [ ] Deny rules for `.env*`, keys, `~/.ssh`, `~/.aws`, force-push, `rm -rf`
- [ ] `ask` for push/publish/network tools
- [ ] Routine commands allowed so prompts stay meaningful
- [ ] Sandbox on with `denyRead` + network allowlist (Windows → WSL2) and `failIfUnavailable`
- [ ] `bypassPermissions` disabled outside containers
- [ ] Headless: `dontAsk` + explicit `--allowedTools`
- [ ] `/permissions` audited regularly

Sources: https://code.claude.com/docs/en/permissions · https://code.claude.com/docs/en/sandboxing · https://code.claude.com/docs/en/security
