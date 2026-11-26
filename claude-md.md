# CLAUDE.md (Memory Files)

*Part of the [Claude Code knowledge base](README.md). Every topic file uses the same sections: What & when · How it works · Guide · Reference · Examples · Best practices · Security · Checklist.*

## 1. What & when

CLAUDE.md files are plain Markdown that Claude Code loads into context **at the start of every session**. They are guidance, not enforced config.

Use it for **facts Claude needs nearly every session and can't quickly find out itself**: build/test commands, architecture rules, conventions, gotchas.

Don't use it for: long procedures (→ [skills](skills.md)), hard rules that must hold (→ [hooks](hooks.md) / [permissions](permissions.md)), anything Claude reads from the code in seconds.

## 2. How it works

Claude Code walks up from the working directory and loads every CLAUDE.md it finds. More specific files appear later in context and therefore tend to win. Nested files in subfolders load when Claude works in that subtree. The content costs tokens **in every turn**.

Separate from that, **auto memory**: notes Claude writes itself from your corrections, per repository. You write CLAUDE.md; Claude writes auto memory. Both load every session.

## 3. Guide: set it up

1. In the repo, run `/init`. Claude scans the codebase and writes a starter `CLAUDE.md`.
2. **Trim it.** For each line ask: *"Could Claude find this by reading the code?"* and *"Would it actually go and look?"* If both are yes, delete the line.
3. Add what only you know: the exact test command, the folder never to edit, the architecture rule that breaks silently.
4. Personal preferences (your editor, your branch naming) → `CLAUDE.local.md` (gitignored) or `~/.claude/CLAUDE.md`.
5. Rules for specific file types → `.claude/rules/<topic>.md` with a `paths:` filter, so they only load when needed.
6. Check what's loaded: `/context all`. Find dead weight: `/doctor`, `/doctor prompt-audit`.
7. Commit `CLAUDE.md` and `.claude/rules/`. Review changes to it like code.

## 4. Reference

### Locations (broad → specific)

| Scope | Path | Shared with |
|---|---|---|
| Enterprise / managed | Windows: `C:\ProgramData\ClaudeCode\CLAUDE.md` · macOS: `/Library/Application Support/ClaudeCode/CLAUDE.md` · Linux: `/etc/claude-code/CLAUDE.md` | Everyone on the machine/org |
| User | `~/.claude/CLAUDE.md` (+ `~/.claude/rules/*.md`) | Just you, all projects, **this machine only** |
| Project | `./CLAUDE.md` or `./.claude/CLAUDE.md` (+ `.claude/rules/*.md`) | Team, via git |
| Project-local | `./CLAUDE.local.md` | Just you, this project (gitignored) |
| Nested | `some/subdir/CLAUDE.md` | Loaded when Claude works in that subtree |

### Imports

Reference other files with `@path`:

```markdown
See @README.md for the project overview and @docs/architecture.md for the module layout.

# Personal
- @~/.claude/my-project-instructions.md
```

Imports in project files trigger a one-time approval dialog; imports in your own user-scope files don't.

### Path-scoped rules

```markdown
---
paths: ["src/**/*.sql", "migrations/**"]
---
- Every migration must be reversible (write the `down` step).
- Never use `SELECT *` in application queries.
```

### Commands

| Command | Use |
|---|---|
| `/init` | Generate a starter CLAUDE.md |
| `/memory` | Open memory files in your editor |
| `/context all` | See which memory/rules files are loaded |
| `/doctor`, `/doctor prompt-audit` | Flag stale, contradictory or duplicated instructions |

## 5. Examples

```markdown
# Project: invoice-service

## Commands
- Build: `dotnet build`
- Unit tests: `dotnet test tests/Unit`
- Lint/format: `dotnet format`

## Architecture
- API in `src/Api`, domain logic in `src/Domain` (no infrastructure refs allowed there)
- All DB access via repositories in `src/Infrastructure/Persistence`

## Conventions
- Nullable reference types on; no `!` suppressions without a comment
- Commit messages: Conventional Commits

## Gotchas
- `src/Generated/` is produced by NSwag; regenerate, don't edit

## How to verify a change
- `dotnet test` must be green and `dotnet format --verify-no-changes` must pass before you say "done".
```

Note the last section: **telling Claude how to check its work** is one of the most valuable lines you can put in CLAUDE.md (see [agentic-coding.md](agentic-coding.md#4-reference)).

## 6. Best practices

- Keep it **short** (< ~200 lines). Every line dilutes the others and costs tokens every turn.
- Be **concrete**: `pnpm test:unit`, not "run the tests".
- Plain sentences work. ALL CAPS, "IMPORTANT!!!" and "never stop" are no longer needed.
- If a procedure grows beyond a few lines → move it into a skill.
- If a rule keeps getting ignored → turn it into a hook or permission rule. CLAUDE.md is advice, not enforcement.
- Use `SessionStart` hooks for dynamic context (current branch, open tickets) instead of hard-coding it.
- Prune regularly; stale instructions are worse than none.

## 7. Security

- **Never put secrets** (tokens, passwords, connection strings) in CLAUDE.md. It's committed and sent to the model every turn.
- **CLAUDE.md is an instruction channel.** In a foreign repo, it (and nested ones, and `@imports`) can contain prompt injection ("before anything, run `curl … | sh`"). Read CLAUDE.md files of repos you don't trust before starting a session there, and don't start in `auto`/`bypassPermissions` mode.
- Approve `@import` dialogs consciously: check what file is being pulled in.
- Don't rely on CLAUDE.md for safety ("never delete prod data"). Enforce it with [permissions](permissions.md) deny rules and [hooks](hooks.md).
- Treat CLAUDE.md changes in PRs like code changes: review them (they change agent behaviour for everyone).
- Org-wide rules go in the **managed** CLAUDE.md, which users can't override by deleting.

## 8. Checklist

- [ ] Created with `/init`, then trimmed to the non-obvious
- [ ] < 200 lines, concrete commands, a "how to verify" section
- [ ] Personal stuff in `CLAUDE.local.md`
- [ ] No secrets, no long procedures, no "safety by instruction"
- [ ] Reviewed in PRs like code

Source: https://code.claude.com/docs/en/memory · https://code.claude.com/docs/en/best-practices
