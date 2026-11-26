---
aliases:
  - "Skills"
  - "Claude Code Skills"
tags:
  - claude-code
  - claude-code/mechanism
---

# Skills

*Part of the [Claude Code knowledge base](README.md). Every topic file uses the same sections: What & when · How it works · Guide · Reference · Examples · Best practices · Security · Checklist.*

## 1. What & when

A **skill** is a folder with a `SKILL.md` file: YAML frontmatter + Markdown instructions. Claude loads it when the `description` matches what you're doing, or you run it directly with `/skill-name`.

Use a skill when:
- you keep pasting the same instructions ("review like this", "release like that"),
- a CLAUDE.md section has turned into a procedure,
- you want a `/command` for a workflow (deploy, fix-issue, write-changelog).

Custom slash commands (`.claude/commands/foo.md`) have been merged into skills: `.claude/commands/deploy.md` and `.claude/skills/deploy/SKILL.md` both create `/deploy`. Old command files keep working.

Skills are also an open standard ("Agent Skills"), so a simple skill can work in claude.ai, the API and other agents too.

## 2. How it works (progressive disclosure)

1. **Always in context:** only name + description of every skill.
2. **On invocation:** the full rendered SKILL.md enters the conversation as one message.
3. **Supporting files:** only when Claude reads them.
4. It stays in context for the rest of the conversation; after compaction the latest invocation is re-attached (first ~5k tokens per skill).

So: the **description is everything** for automatic triggering, and skill bodies are "free" until used, unlike CLAUDE.md.

## 3. Guide: create a skill

1. Create the folder: `.claude/skills/summarize-changes/` (project) or `~/.claude/skills/summarize-changes/` (all your projects).
2. Write `SKILL.md` with a `description` that says **what** it does and **when** to use it, with concrete trigger words.
3. Write the body as short imperative steps. Put long reference material into extra files and link them.
4. If it has side effects (commits, deploys, sends messages): add `disable-model-invocation: true`.
5. If it needs commands without prompts: add a **narrow** `allowed-tools` (`Bash(git diff *)`, not `Bash`).
6. Test in a **fresh** session: does it trigger when it should, stay quiet when it shouldn't, and produce the right output? Run `/summarize-changes` directly too.
7. Commit it (project) or bundle it in a [plugin](plugins.md) to share across repos.

## 4. Reference

### Locations

| Scope | Path | Applies to |
|---|---|---|
| Enterprise | `.claude/skills/<name>/SKILL.md` in the managed settings dir | All users on managed machines |
| Personal | `~/.claude/skills/<name>/SKILL.md` | All your projects **on this machine** |
| Project | `.claude/skills/<name>/SKILL.md` | This repo (commit to share) |
| Nested | `<subdir>/.claude/skills/<name>/SKILL.md` | Sessions in or below that subdir |
| Plugin | `<plugin>/skills/<name>/SKILL.md` | Where the plugin is enabled, as `/plugin:skill` |

Precedence on name clash: enterprise > personal > project. Your skill replaces a bundled one with the same name. Reserved folder names: `synced`, `anthropic-skills`.

### Anatomy

```text
my-skill/
├── SKILL.md          # required: overview + instructions (keep < 500 lines)
├── reference.md      # detail, loaded only when Claude reads it
├── examples.md
└── scripts/
    └── helper.py     # executed, not loaded into context
```

File must be named exactly `SKILL.md`. Folder name (kebab-case) becomes the `/command`.

### Frontmatter

All fields optional; `description` strongly recommended. Unknown fields are ignored.

| Field | Meaning |
|---|---|
| `name` | `/` command name. Defaults to folder name |
| `description` | What + when. Key use case first. Truncated at ~1,536 chars (with `when_to_use`) |
| `when_to_use` | Extra trigger phrases |
| `argument-hint` | Autocomplete hint, e.g. `[issue-number]` |
| `arguments` | Named positional args for `$name` substitution |
| `disable-model-invocation` | `true` = only *you* can run it |
| `user-invocable` | `false` = hidden from `/` menu, only Claude uses it |
| `allowed-tools` | Tools usable without prompts while the skill runs |
| `disallowed-tools` | Tools removed while the skill is active |
| `model`, `effort` | Overrides for the turn |
| `context: fork` + `agent` | Run the skill in a subagent (fresh context) |
| `background` | With `fork`: `false` waits for the result |
| `hooks` | Hooks registered while the skill runs |
| `paths` | Globs limiting automatic activation |
| `shell` | `bash` (default) or `powershell` for `!` injection |

Portability: outside Claude Code only `name`, `description`, `license`, `compatibility`, `metadata`, `allowed-tools` are allowed.

| Setting | You can run | Claude can run | Description in context |
|---|---|---|---|
| default | yes | yes | yes |
| `disable-model-invocation: true` | yes | no | no |
| `user-invocable: false` | no | yes | yes |

### Substitutions

| Variable | Expands to |
|---|---|
| `$ARGUMENTS` | Everything after `/skill-name` |
| `$0`, `$1`, … / `$ARGUMENTS[N]` | Positional args |
| `$name` | Arg declared in `arguments` |
| `${CLAUDE_SKILL_DIR}` | Folder of this SKILL.md |
| `${CLAUDE_PROJECT_DIR}` | Project root |
| `${CLAUDE_SESSION_ID}` | Session ID |

### Dynamic context injection

`` !`command` `` at line start runs **before** Claude sees the skill; output replaces the placeholder.

````markdown
## Current changes
!`git diff HEAD`

```!
node --version
git status --short
```
````

Non-zero exit aborts the skill (add `|| true` where needed). Commands go through permission rules; pre-approve with `allowed-tools`. Timeout 2 min. Disable globally with `"disableSkillShellExecution": true`.

### Controlling access

- Deny rules: `Skill` (all), `Skill(commit)`, `Skill(review-pr *)`.
- In settings: `{ "skillOverrides": { "legacy-context": "name-only", "deploy": "off" } }` (values `on`, `name-only`, `user-invocable-only`, `off`).

## 5. Examples

**Auto-triggered, read-only** ([examples/skills/summarize-changes/SKILL.md](examples/skills/summarize-changes/SKILL.md)):

```markdown
---
name: summarize-changes
description: Summarizes uncommitted git changes and flags risks. Use when the user asks what changed, wants a review of the diff, or needs a commit message.
allowed-tools: Bash(git diff *) Bash(git status *)
---

## Current changes
!`git status --short`
!`git diff HEAD`

## Instructions
1. Summarize the changes above in 2–3 bullet points.
2. List risks: missing error handling, hardcoded values, tests that need updating.
3. Propose a Conventional Commits message (`type(scope): subject`).
```

**Manual only, has side effects** ([examples/skills/fix-issue/SKILL.md](examples/skills/fix-issue/SKILL.md)):

```markdown
---
name: fix-issue
description: Fix a GitHub issue end to end. Only run when the user explicitly invokes it.
argument-hint: "[issue-number]"
disable-model-invocation: true
---

Fix GitHub issue #$ARGUMENTS:
1. Read the issue with `gh issue view $ARGUMENTS`.
2. Reproduce the problem with a failing test.
3. Implement the minimal fix.
4. Run the test suite and the linter; fix anything you broke.
5. Commit with message `fix: <summary> (#$ARGUMENTS)`. Do not push.
```

Usage: `/fix-issue 123`.

## 6. Best practices

- Write the description like a search-index entry: *what* + *when*, concrete trigger words, key use case first.
- Keep the body imperative and short; move reference material into supporting files.
- `disable-model-invocation: true` for anything with side effects.
- Use `context: fork` only for self-contained tasks (the subagent doesn't see your conversation).
- Include a verification step in the skill ("run the tests, paste the result").
- Test with and without the skill in fresh sessions. The `skill-creator` skill automates evals.
- `/skill-doctor` finds skills that cost context but are never used.

## 7. Security

- **Skills are instructions + code.** `!` commands run on your machine **before** Claude even sees the skill, and `scripts/` can run anything. Read skills from repos, plugins or colleagues before using them.
- **`allowed-tools` bypasses prompts.** Keep it narrow (`Bash(git diff *)`), never `Bash` or `Bash(*)`. A skill from a cloned repo with broad `allowed-tools` is a red flag.
- A project skill in a foreign repo can trigger **automatically** from its description. Check `.claude/skills/` in repos you don't trust, or turn them off via `skillOverrides` / a `Skill(...)` deny rule.
- `disable-model-invocation: true` for side effects, so a prompt injection elsewhere can't make Claude run `/deploy`.
- No secrets in SKILL.md or its files; read them from env vars or a secret store at runtime.
- `!` arguments: don't splice `$ARGUMENTS` unquoted into shell commands (command injection via the argument).
- Orgs that don't want dynamic shell injection at all: `"disableSkillShellExecution": true` in managed settings.
- Skill files under `.claude/skills` are write-protected inside the [sandbox](permissions.md), so the agent can't rewrite its own skills when sandboxing is on.

## 8. Checklist

- [ ] Description says what + when, with trigger words
- [ ] Body < 500 lines, details in supporting files
- [ ] Side effects → `disable-model-invocation: true`
- [ ] `allowed-tools` narrow; `!` commands reviewed, arguments quoted
- [ ] Tested in a fresh session (triggers, doesn't over-trigger, correct output)
- [ ] Foreign skills reviewed before use

Source: https://code.claude.com/docs/en/skills
