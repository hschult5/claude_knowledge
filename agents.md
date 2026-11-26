# Subagents

*Part of the [Claude Code knowledge base](README.md). Every topic file uses the same sections: What & when · How it works · Guide · Reference · Examples · Best practices · Security · Checklist.*

## 1. What & when

A **subagent** is a specialized Claude instance with its **own context window**, system prompt, tool set, model and permissions. Claude delegates a task to it; the subagent works in isolation and returns **only a final summary** to your main conversation.

Use one for:
- **Context hygiene:** big searches, log dumps, test output stay out of your main context.
- **Specialization:** a focused prompt + restricted tools (e.g. a read-only reviewer).
- **Cost/speed:** cheap work on Haiku, hard reasoning on Opus.
- **Unbiased review:** a fresh agent that didn't write the code reviews it.
- **Parallelism:** several subagents work at once.

Don't use one for tight back-and-forth editing, or when the task needs your conversation history. Subagents cost tokens and are **not smarter** by default.

## 2. How it works

What the subagent sees:
- Its system prompt (the file body)
- The delegation message Claude writes for it
- CLAUDE.md files (unless `omitClaudeMd`), a git status snapshot, preloaded skills
- **Not** your conversation history and **not** files read earlier in the main session

Only the final summary comes back. You can resume a subagent (with full history) via its agent id. Subagents can't spawn further subagents by default (max nesting depth 3, env `CLAUDE_CODE_MAX_SUBAGENT_SPAWN_DEPTH`).

Built-in agents:

| Agent | Purpose |
|---|---|
| `Explore` | Fast, read-only codebase search and analysis |
| `Plan` | Read-only research during plan mode |
| `general-purpose` | Multi-step tasks needing exploration *and* action, all tools |
| `claude` | Catch-all |
| `statusline-setup` | Configures the status line |
| `claude-code-guide` | Answers questions about Claude Code itself |

Explore and Plan skip CLAUDE.md and the git snapshot to stay fast.

## 3. Guide: create a subagent

1. Pick **one job** (review, run tests, research docs). One agent = one role.
2. Create `.claude/agents/<name>.md` (project, commit it) or `~/.claude/agents/<name>.md` (all your projects).
3. Frontmatter: `name`, a `description` that says **when** to delegate ("Use proactively after code changes …"), a **minimal** `tools` list, and a `model`.
4. Body = system prompt. Restate the critical rules (the agent doesn't see your conversation) and **spell out the output format** (short, structured; it lands in your context).
5. Try it: "Use the code-reviewer subagent on my changes", or `@code-reviewer`.
6. Tune the description if Claude delegates too often / too rarely.

## 4. Reference

### Locations & priority (higher wins on name clash)

| # | Location | Scope |
|---|---|---|
| 1 | Managed settings `.claude/agents/` | Organization |
| 2 | `--agents '{...json...}'` CLI flag | This session only |
| 3 | `.claude/agents/` | Current project |
| 4 | `~/.claude/agents/` | All your projects on this machine |
| 5 | Plugin `agents/` | Where the plugin is enabled |

Directories are scanned recursively; edits are picked up within seconds. Identity comes from `name`, not the filename.

### Frontmatter

Only `name` and `description` are required.

| Field | Meaning |
|---|---|
| `name` | Unique id (no `:`) |
| `description` | **When** Claude should delegate. "Use proactively …" encourages automatic use |
| `tools` | Allowlist. Omit = inherit all. MCP wildcards OK: `mcp__github__*` |
| `disallowedTools` | Denylist, applied before `tools` |
| `model` | `haiku`, `sonnet`, `opus`, `fable`, full model id, or `inherit` |
| `permissionMode` | `default`, `acceptEdits`, `auto`, `dontAsk`, `bypassPermissions`, `plan` |
| `maxTurns` | Stop after N turns |
| `skills` | Skills preloaded at startup |
| `mcpServers` | MCP servers scoped to this agent |
| `hooks` | `PreToolUse` / `PostToolUse` / `Stop` hooks scoped to this agent |
| `memory` | Persistent memory scope: `user`, `project`, `local` |
| `isolation` | `worktree` = run in a temporary git worktree |
| `background` | Keep running in background |
| `effort` | `low` … `max` |
| `color` | Display color |

Model resolution: per-call `model` → frontmatter `model` → `CLAUDE_CODE_SUBAGENT_MODEL` → main conversation's model.

### Invocation

1. **Automatic:** Claude matches the request against each `description`.
2. **By name:** "Use the test-runner subagent to fix the failing tests."
3. **@-mention:** `@agent-name` guarantees it runs.
4. **As the whole session:** `claude --agent code-reviewer`, or `"agent": "code-reviewer"` in `.claude/settings.json`.

### Subagent vs. skill with `context: fork`

| | Subagent file | Skill with `context: fork` |
|---|---|---|
| Defines | A reusable *role* (prompt + tools + model) | A *task* that runs in a role |
| Triggered by | Delegation / @-mention | `/skill` or skill matching |
| Typical use | `code-reviewer`, `test-runner` | `/deep-research <topic>` running in `Explore` |

## 5. Examples

**Read-only reviewer** ([examples/agents/code-reviewer.md](examples/agents/code-reviewer.md)):

```markdown
---
name: code-reviewer
description: Expert code reviewer. Use proactively right after code has been written or modified, before committing.
tools: Read, Grep, Glob, Bash
model: sonnet
---

You are a senior code reviewer. You do NOT modify files; you only report.

1. Run `git diff HEAD` to see what changed. Focus on those files.
2. Review for: correctness bugs, security (injection, secrets, authz),
   error handling, missing tests. Readability only if it really hurts.

Output:
## Critical (must fix)
- `path/file.ext:line` – problem – suggested fix
## Warnings (should fix)
## Nits (optional)
If a section is empty, write "none". No praise, no diff summary.
```

**Cheap test runner** ([examples/agents/test-runner.md](examples/agents/test-runner.md)): `model: haiku`, `maxTurns: 20`, tools `Read, Grep, Glob, Bash, Edit`, rule "never delete or skip a test to make it pass". The noisy test output stays inside the subagent.

**Security auditor with hard read-only + scoped hook:**

```markdown
---
name: security-auditor
description: Audits changed code for vulnerabilities. Use before merging anything touching auth, payments or user input.
tools: Read, Grep, Glob
disallowedTools: Bash, Edit, Write, WebFetch
model: opus
permissionMode: plan
---
Look for injection, broken authz, secrets in code, unsafe deserialization, SSRF.
Report each finding as `file:line – vulnerability – exploit scenario – fix`.
```

## 6. Best practices

- One clear job per agent; write the description as "when to use me".
- Keep descriptions short (all descriptions together > ~15k tokens triggers a warning). Detail goes in the body.
- Least privilege: reviewers/researchers get `Read, Grep, Glob` only.
- Spell out the **output format** (short, structured).
- Restate critical rules in the prompt; the agent doesn't see what you told the main session.
- Haiku for cheap read-only work, Sonnet/Opus for reasoning-heavy tasks.
- Use a fresh reviewer agent instead of asking the author agent to review its own work.
- Parallel *writers* need `isolation: worktree` so they don't overwrite each other.
- Commit project agents so the team can improve them.

## 7. Security

- **Tools allowlist = blast radius.** An agent with `Bash` can do anything your user can. Give `Bash` only where needed and pair it with [permission rules](permissions.md) / [hooks](hooks.md).
- **Never `permissionMode: bypassPermissions`** in an agent file unless the whole session runs in a container/VM. A shared agent with bypass silently turns off all prompts for whoever uses it.
- Agents that read **untrusted content** (web pages, issues, emails) should have **no write or network-sending tools**. Split "read untrusted" and "act" into different agents; this limits what a prompt injection can do.
- The summary a subagent returns is **model output, not user instruction**. If it says "now run X" or "the user approved Y", treat that as data and check it.
- Agent files in a cloned repo (`.claude/agents/`) are instructions you didn't write. Review them (especially `tools`, `permissionMode`, `hooks`, `mcpServers`) before working in that repo.
- Restrict which agents may run: deny rules like `Agent(Explore)`, `Agent(model:opus)`.
- `maxTurns` caps runaway loops (cost and damage).
- `isolation: worktree` keeps experimental writes off your working tree.

## 8. Checklist

- [ ] One job, "when to use me" description
- [ ] Minimal `tools`; read-only where possible
- [ ] Output format specified
- [ ] No `bypassPermissions`; `maxTurns` set for autonomous agents
- [ ] Untrusted-input agents have no write/send tools
- [ ] Foreign `.claude/agents/` reviewed

Source: https://code.claude.com/docs/en/sub-agents
