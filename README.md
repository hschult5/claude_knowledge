# Claude Code: Knowledge Base

*Written 2026-11-25/26 from the official docs at code.claude.com. Features move fast; check the docs if something behaves differently.*

**One file per mechanism.** Each file has the same sections, so you always know where to look:

| # | Section | Contains |
|---|---|---|
| 1 | What & when | What it is, when to use it (and when not) |
| 2 | How it works | The mental model |
| 3 | Guide | Step-by-step setup |
| 4 | Reference | Locations, fields, syntax, commands |
| 5 | Examples | Copy-paste examples (full files in [`examples/`](examples/)) |
| 6 | Best practices | How to use it well |
| 7 | Security | Risks and measures specific to this mechanism |
| 8 | Checklist | Quick review before you rely on it |

## Files

| File | Mechanism |
|---|---|
| [`agentic-coding.md`](agentic-coding.md) | **Start here.** The workflow: explore → spec → plan → build → verify → review; context management; parallel & headless; threat model |
| [`claude-md.md`](claude-md.md) | CLAUDE.md memory files: always-on instructions |
| [`skills.md`](skills.md) | Skills: on-demand procedures and `/slash-commands` |
| [`agents.md`](agents.md) | Subagents: separate Claude instances with own context, tools, model |
| [`hooks.md`](hooks.md) | Hooks: deterministic scripts on lifecycle events |
| [`permissions.md`](permissions.md) | Permission modes & rules, sandbox, isolation levels |
| [`mcp.md`](mcp.md) | MCP servers: connecting external tools and data |
| [`plugins.md`](plugins.md) | Plugins & marketplaces: bundle and share all of the above |
| [`obsidian.md`](obsidian.md) | Obsidian + Claude: vault in Claude Code, Obsidian CLI, MCP servers, skills |
| [`examples/`](examples/) | Runnable starter files: agents, skills, hooks, a full plugin marketplace |

## Skills for this knowledge base

| Skill | What it does |
|---|---|
| `/kb-overview` | Table of all topic files with summary, 8-section template check (x/8), line count, example files, and warnings (missing sections, files not in the table above). Also triggers on "what's in the knowledge base?" |
| `/kb-new-topic <topic>` | Researches the topic from official docs, writes `<topic>.md` from the 8-section [template](.claude/skills/kb-new-topic/template.md), adds it to the table above. Manual only (it writes files) |

Source of truth: [`.claude/skills/`](.claude/skills/) in this repo. A copy lives in `~/.claude/skills/` so they work from any folder (personal skills win over project skills on a name clash). After editing a skill here, re-copy it:

```powershell
Copy-Item -Recurse -Force .claude\skills\kb-* $HOME\.claude\skills\
```

---

## The mental model

Ordered from "the model decides" to "code decides":

| Mechanism | Who triggers it | Loaded into context | Deterministic? | Good for |
|---|---|---|---|---|
| **CLAUDE.md** | Always loaded at session start | Every turn | No (guidance) | Facts and conventions: build commands, architecture, gotchas |
| **Skill** | Claude (matches `description`) or you (`/name`) | Name + description until used | No | Repeatable procedures, workflows |
| **Subagent** | Claude (delegation) or you (`@agent`) | Own context window; only a summary returns | No | Noisy work, specialist roles, parallelism, unbiased review |
| **MCP server** | Claude calls its tools | Tool definitions (on demand) | No | Access to external systems |
| **Hook** | The runtime, on an event | Optional (can inject text) | **Yes** | Hard rules: block, format, notify, validate |
| **Permissions / sandbox** | The runtime / the OS, on every tool call | No | **Yes** | What Claude may do at all |

Rules of thumb:

- **"Claude should know X"** → CLAUDE.md (needed nearly every session) or a skill (needed sometimes).
- **"Claude should do X the same way every time"** → skill.
- **"This work floods my context / needs another persona or tool set"** → subagent.
- **"Claude needs to talk to system Y"** → MCP server (or a CLI + permission rule).
- **"X must always / never happen"** → hook + permission rule (+ sandbox).
- **"I want this in every repo / for my team"** → plugin.

They compose: a skill can run inside a subagent (`context: fork`), a subagent can preload skills and own MCP servers, skills and agents can register hooks, and plugins bundle everything.

## Security in one paragraph

An agent has your user account's power. Defend in layers: **permissions** (deny secrets and destructive commands) → **sandbox** (OS-level filesystem/network limits; on Windows only via WSL2) → **hooks** (fail-closed guards) → **isolation** (container/VM for unattended runs) → **human review**. Treat everything the agent reads (issues, web pages, MCP results, foreign `.claude/` folders) as untrusted data. Each file's section 7 has the mechanism-specific measures; [agentic-coding.md](agentic-coding.md#7-security) has the overall threat model.

## Where things live (scopes)

| | User / personal | Project (shared via git) | Project, private |
|---|---|---|---|
| Memory | `~/.claude/CLAUDE.md` | `./CLAUDE.md` or `./.claude/CLAUDE.md` | `./CLAUDE.local.md` |
| Skills | `~/.claude/skills/<name>/SKILL.md` | `.claude/skills/<name>/SKILL.md` | – |
| Subagents | `~/.claude/agents/<name>.md` | `.claude/agents/<name>.md` | – |
| Hooks & permissions | `~/.claude/settings.json` | `.claude/settings.json` | `.claude/settings.local.json` |
| MCP servers | `claude mcp add --scope user` | `.mcp.json` | `claude mcp add` (local, default) |

On Windows `~` is `C:\Users\<you>`. Everything under `~/.claude/` is **local to this machine** and not synced. Cloud sessions and the desktop/web agent mode use skills and connectors from your claude.ai account instead. To have something everywhere, put it in the repo or a plugin.

## Useful commands

| Command | What it does |
|---|---|
| `/init` | Generate a starter CLAUDE.md |
| `/memory` | Open memory files |
| `/context all` | What's loaded into context |
| `/permissions` | Active permission rules and their source |
| `/sandbox` | Configure the sandbox |
| `/hooks` | Registered hooks (read-only) |
| `/mcp` | MCP server status and auth |
| `/plugin` | Browse/install/enable plugins |
| `/clear`, `/compact`, `/rewind` | Context management |
| `/code-review`, `/security-review` | Reviews in a fresh agent |
| `/doctor` | Setup checkup: unused skills, slow hooks, stale CLAUDE.md content |

## Suggested learning path

1. Read [agentic-coding.md](agentic-coding.md) and apply the workflow to one real task.
2. Set the permissions baseline from [permissions.md](permissions.md) (and WSL2 sandbox if you're on Windows).
3. Run `/init` in a real repo, then trim CLAUDE.md to what Claude can't figure out alone.
4. Turn a prompt you keep pasting into a skill.
5. Add a read-only `code-reviewer` subagent.
6. Add a format hook and a guard hook.
7. Connect one MCP server with least-privilege rules.
8. Bundle your set as a plugin to share it.
