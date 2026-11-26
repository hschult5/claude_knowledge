---
aliases:
  - "Obsidian + Claude"
  - "Obsidian Claude Integration"
tags:
  - claude-code
  - claude-code/integration
  - obsidian
---

# Obsidian + Claude

*Part of the [Claude Code knowledge base](README.md). Every topic file uses the same sections: What & when · How it works · Guide · Reference · Examples · Best practices · Security · Checklist.*

*Written 2026-11-26 from obsidian.md/help/cli, the READMEs of MCPVault, Obsidian Local REST API and obsidianmd/obsidian-skills, and community comparisons. All MCP servers below are community projects, not official Obsidian or Anthropic products. Check their current README before installing.*

## 1. What & when

An Obsidian **vault is just a folder of Markdown files**. That makes it a natural knowledge base for Claude: notes, research, meeting logs, daily notes, project docs. Typical uses:

- Ask questions across your notes ("What did I decide about X in the last 3 months?")
- Summarize, tag, link and restructure notes; find orphans and duplicates
- Turn meeting transcripts / web clippings into clean notes with properties and wikilinks
- Write daily/weekly reviews from daily notes and tasks
- Use the vault as long-term memory and context for coding work

There are **four ways** to connect them; pick by client and how much power you want to give:

| Way | Works with | Obsidian app must run? | Uses Obsidian's index/search? | Effort |
|---|---|---|---|---|
| **A. Claude Code directly in the vault folder** | Claude Code | No | No (grep/glob) | Lowest |
| **B. Official Obsidian CLI** (`obsidian …`) | Claude Code (via Bash) | Yes | Yes (search, tags, properties, tasks, daily notes) | Low |
| **C. MCP server on the files** (MCPVault, Filesystem MCP) | Claude Code, Claude Desktop, any MCP client | No | No | Low |
| **D. MCP via the Local REST API plugin** | Claude Code, Claude Desktop (via `mcp-remote`) | Yes | Yes, plus atomic heading/frontmatter edits | Medium |

Plus, for all of them: the **official `obsidian-skills`** teach Claude Obsidian-flavoured Markdown (wikilinks, embeds, callouts, properties, Bases, Canvas, the CLI).

Rule of thumb: **Claude Code user → A (+ skills, + B if you want Obsidian's search).** **Claude Desktop / claude.ai user → C (MCPVault, start read-only).** D when you need Obsidian's own search or precise edits from a client other than Claude Code.

## 2. How it works

- **A:** Claude Code's normal tools (Read, Edit, Grep, Glob) work on the `.md` files. Obsidian picks up changes live. A `CLAUDE.md` in the vault root explains your structure and conventions.
- **B:** Since Obsidian 1.12.4 (Feb 2026) there's an official CLI. It talks to the **running** Obsidian app (the first command launches it), so it can use Obsidian's search, tags, properties, tasks, templates and daily notes. Claude calls it through Bash/PowerShell.
- **C:** An MCP server process reads/writes the vault folder and exposes tools like `search_notes`, `read_note`, `write_note`, `update_frontmatter`, `manage_tags`. No Obsidian plugin needed.
- **D:** The community plugin **Local REST API** runs an HTTPS server inside Obsidian (`127.0.0.1:27124`) and serves MCP at `/mcp/`, protected by an API key.
- **Skills:** `obsidianmd/obsidian-skills` is a Claude Code plugin with skills `obsidian-markdown`, `obsidian-bases`, `json-canvas`, `obsidian-cli`, `obsidian-headless`, `defuddle` (web page → clean Markdown), `knap` (templates from JSON/CSV). See [skills.md](skills.md), [plugins.md](plugins.md).

## 3. Guide

### Step 0 (all ways): back up the vault

Make the vault a git repo (or check your backup/Sync version history works) **before** letting an agent write:

```powershell
cd "C:\Users\<you>\Documents\MyVault"
git init; git add -A; git commit -m "baseline before Claude"
```

Add `.obsidian/workspace*.json` and `.trash/` to `.gitignore`.

### A. Claude Code directly in the vault

1. Open a terminal in the vault folder and run `claude`.
2. Run `/init` or write a `CLAUDE.md` in the vault root (template in §5).
3. Add `.claude/settings.json` with the protections from §5 (deny edits to `.obsidian/`, `ask` before deletes).
4. Install the Obsidian skills:
   ```powershell
   claude plugin marketplace add obsidianmd/obsidian-skills
   claude plugin install obsidian@obsidian-skills
   ```
5. Try: "List notes in `Inbox/` older than 30 days and propose where each belongs. Don't move anything yet."

Tip: to use the vault from **another** project (e.g. as reference while coding), add it with `/add-dir "C:\Users\<you>\Documents\MyVault"` or `permissions.additionalDirectories`.

### Bring a git repo of Markdown docs into the vault (junction)

The other direction: a docs repo (like this knowledge base) should show up in your vault and graph **without a second copy**.

1. Create a directory junction inside the vault (no admin rights needed):
   ```powershell
   New-Item -ItemType Junction -Path "<vault>\Claude Knowledge" -Target "E:\Work\claude_knowledge"
   ```
2. Obsidian indexes it like a normal folder. Dot-folders (`.git`, `.claude`) are hidden automatically.
3. Relative Markdown links (`[hooks.md](hooks.md)`) appear as edges in the graph; keep them instead of `[[wikilinks]]` if the repo is also read on GitHub.
4. Add frontmatter `aliases` + `tags` to each file so you can link `[[Hooks]]` from your own notes and filter the graph by tag (`tag:#claude-code`).
5. Git stays in the repo folder: commit/pull there (or with the Obsidian Git plugin pointed at that repo). Don't also sync the junction folder with Obsidian Sync/OneDrive, or you get two sync systems fighting.

Caveats: junctions are Windows-only (on macOS/Linux use a symlink, `ln -s`); Obsidian may notice changes made outside it with a short delay. **Remove only the link** with `cmd /c rmdir "<vault>\Claude Knowledge"`. Deleting the folder from inside Obsidian or with PowerShell 5.1 `Remove-Item -Recurse` can delete the **target's files**. With git + GitHub you can recover, but uncommitted changes would be lost.

### B. Add the official Obsidian CLI

1. Install/update Obsidian (installer **1.12.7+**).
2. Obsidian → Settings → General → enable **Command line interface**, follow the prompt to register it (adds it to your PATH; on Windows via an `Obsidian.com` redirector next to `Obsidian.exe`).
3. **Restart the terminal**, test: `obsidian search query="meeting"`.
4. Allow the read-only commands in `.claude/settings.json` so Claude doesn't ask every time (§5). The `obsidian-cli` skill from step A4 teaches Claude the syntax.

### C. MCP server on the files (MCPVault)

Needs Node.js 22.12+. Obsidian doesn't have to run.

1. **Claude Code**, start read-only:
   ```powershell
   claude mcp add obsidian --scope user -- cmd /c npx -y @bitbonsai/mcpvault@<version> "C:\Users\<you>\Documents\MyVault" --read-only
   ```
   (`cmd /c` is needed for `npx` stdio servers on native Windows. On macOS/Linux drop it.)
2. **Claude Desktop**: edit `%APPDATA%\Claude\claude_desktop_config.json` (§5), restart Claude Desktop.
3. Check: `/mcp` in Claude Code, or the tools icon in Claude Desktop.
4. When you trust the setup, remove `--read-only`, and add `--exclude <folder>` for private subtrees.

Alternative: the official reference server `@modelcontextprotocol/server-filesystem <vault-path>`: generic file tools, no Obsidian features.

### D. MCP via the Local REST API plugin

1. Obsidian → Settings → Community plugins → install and enable **Local REST API**.
2. Copy the **API key** from its settings. Store it as an environment variable, not in a file:
   ```powershell
   [Environment]::SetEnvironmentVariable("OBSIDIAN_API_KEY", "<key>", "User")
   ```
3. Add the server to Claude Code (new terminal so the variable is loaded):
   ```powershell
   claude mcp add --scope user --transport http obsidian https://127.0.0.1:27124/mcp/ --header "Authorization: Bearer $env:OBSIDIAN_API_KEY"
   ```
4. Certificate: the plugin uses its own CA. If the connection fails with a TLS error, download `https://127.0.0.1:27124/obsidian-local-rest-api.crt` and set `NODE_EXTRA_CA_CERTS` to that file. (Enabling the plain-HTTP port 27123 also works but is less secure.)
5. Claude Desktop has no native remote MCP: use `mcp-remote` as a bridge (§5).
6. Obsidian must be running for the tools to work.

## 4. Reference

### Obsidian CLI

Syntax: `obsidian [vault=<name>] <command> [param=value] [flag]` (`vault=` must come first; quote values with spaces; `\n` for newlines; `--copy` copies output).

| Command | What |
|---|---|
| `obsidian search query="…"` | Obsidian's search |
| `obsidian read file=Recipe` / `read path="Folder/Note.md"` | Read a note (`read` alone = active note) |
| `obsidian create name="…" template=Travel` | New note from template (`open`, `overwrite` flags) |
| `obsidian daily`, `daily:append content="- [ ] …"` | Daily note |
| `obsidian properties`, `property:read/set/remove name=… value=… type=…` | Frontmatter properties |
| `obsidian tags counts`, `tag name=<tag> verbose` | Tags |
| `obsidian tasks daily`, `task ref="Note.md:8" toggle` | Tasks |
| `obsidian` | Interactive TUI |
| `devtools`, `plugin:reload id=…`, `dev:screenshot`, `dev:console`, `dev:errors`, `eval code="…"` | Developer commands (for plugin development). **`eval` runs arbitrary JS inside Obsidian** |

Platforms: Windows, macOS (`/usr/local/bin/obsidian`), Linux (`~/.local/bin/obsidian`). Requires the app running. Sync without the app: **Obsidian Headless** (separate tool).

### MCPVault (`@bitbonsai/mcpvault`)

| Flag | Effect |
|---|---|
| `<vault-path>` | Vault root (required) |
| `--read-only` | Write tools hidden and rejected |
| `--exclude <subtree>` (repeatable) | Hides folders from `search_notes` / `list_directory` (**only** those two) |

Tools: `read_note`, `read_multiple_notes`, `read_note_lines`, `get_note_outline`, `search_notes`, `list_directory`, `get_frontmatter`, `get_notes_info`, `get_vault_stats`, `list_all_tags`, `wiki_link`, and the write tools `write_note`, `patch_note`, `delete_note`, `move_note`, `move_file`, `update_frontmatter`, `manage_tags`.

Safety built in: blocks path traversal, symlink escapes, dotfiles, `.obsidian`, `.git`, `node_modules`; only `.md/.markdown/.txt/.base/.canvas`; `delete_note` / `move_file` require the path to be repeated as confirmation.

### Local REST API plugin

| Item | Value |
|---|---|
| HTTPS port | `27124` (default) |
| HTTP port | `27123`, off by default |
| MCP endpoint | `https://127.0.0.1:27124/mcp/` (streamable HTTP) |
| Auth | `Authorization: Bearer <api-key>` |
| CA cert | `https://127.0.0.1:27124/obsidian-local-rest-api.crt` (name-constrained to localhost) |
| `.obsidian/` access | Blocked (403) unless you enable "Allow access to the configuration directory" — don't |
| Brute force | 10 wrong keys/min → 429 |
| Multiple vaults | Each needs its own port |

### Permission rule names

| Way | Tools appear as |
|---|---|
| A | `Read`, `Edit`, `Grep`, `Glob` on vault paths |
| B | `Bash(obsidian …)` / `PowerShell(obsidian …)` |
| C, D | `mcp__obsidian__<tool>` (server name you chose) |

## 5. Examples

### `CLAUDE.md` for a vault

```markdown
# My vault

## Structure
- `Inbox/` – unsorted captures. Process into the folders below.
- `Projects/<name>/` – one folder per active project, `_index.md` as hub note.
- `Areas/`, `Resources/`, `Archive/` – PARA.
- `Daily/YYYY-MM-DD.md` – daily notes (template: `Templates/Daily.md`).
- `Private/` – never read, never summarize, never move.

## Conventions
- Link with [[wikilinks]], not Markdown links. Use existing note names; check before creating new ones.
- Every note has frontmatter: `tags`, `created` (YYYY-MM-DD), `status` (seed|growing|done).
- Tags lowercase, kebab-case, hierarchical: `#project/website`.
- Language of the note stays as written (German notes stay German).

## Rules
- Never delete notes; move them to `Archive/` instead.
- Propose bulk changes (more than 5 files) as a list first, wait for my OK.
- Don't touch `.obsidian/` or `Templates/`.
```

### `.claude/settings.json` in the vault

```json
{
  "permissions": {
    "deny": [
      "Edit(./.obsidian/**)",
      "Read(./Private/**)",
      "Bash(obsidian eval *)",
      "Bash(obsidian dev* *)",
      "mcp__obsidian__delete_note"
    ],
    "ask": [
      "Bash(rm *)", "PowerShell(Remove-Item *)",
      "Bash(obsidian create *)",
      "mcp__obsidian__move_note", "mcp__obsidian__move_file"
    ],
    "allow": [
      "Bash(obsidian search *)", "Bash(obsidian read *)",
      "Bash(obsidian tags *)", "Bash(obsidian properties *)", "Bash(obsidian tasks *)",
      "mcp__obsidian__read_note", "mcp__obsidian__search_notes", "mcp__obsidian__list_directory"
    ]
  }
}
```

### Claude Desktop config (MCPVault, read-only)

`%APPDATA%\Claude\claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "obsidian": {
      "command": "npx",
      "args": ["-y", "@bitbonsai/mcpvault@<version>", "C:\\Users\\<you>\\Documents\\MyVault", "--read-only"]
    }
  }
}
```

### Claude Desktop config (Local REST API via `mcp-remote`)

```json
{
  "mcpServers": {
    "obsidian": {
      "command": "npx",
      "args": ["-y", "mcp-remote@<version>", "https://127.0.0.1:27124/mcp/", "--header", "Authorization:${AUTH_HEADER}"],
      "env": {
        "AUTH_HEADER": "Bearer <api-key>",
        "NODE_EXTRA_CA_CERTS": "C:\\Users\\<you>\\obsidian-local-rest-api.crt"
      }
    }
  }
}
```

`mcp-remote` expands `${AUTH_HEADER}` itself (no space after `Authorization:`, to avoid an argument-splitting bug on Windows). Claude Desktop needs the key in this file, so it's the one place a key sits on disk. The file is in your user profile; don't sync or share it.

### Project `.mcp.json` (REST API, no key in the file)

```json
{
  "mcpServers": {
    "obsidian": {
      "type": "http",
      "url": "https://127.0.0.1:27124/mcp/",
      "headers": { "Authorization": "Bearer ${OBSIDIAN_API_KEY}" }
    }
  }
}
```

### A vault skill: weekly review

`<vault>/.claude/skills/weekly-review/SKILL.md`:

```markdown
---
name: weekly-review
description: Writes the weekly review note from the last 7 daily notes. Use when the user asks for a weekly review or "what happened this week".
allowed-tools: Read Glob Grep Bash(obsidian tasks *)
---
1. Read `Daily/` notes from the last 7 days.
2. Collect: done tasks, open tasks (`obsidian tasks daily`), decisions, new project notes.
3. Write `Reviews/YYYY-Www.md` with sections Done / Open / Decisions / Next week, using [[wikilinks]] to the source notes.
4. Don't change the daily notes.
```

### Good prompts

- "Find all notes tagged `#meeting` from October without a `## Decisions` section. List them, don't edit."
- "Process `Inbox/`: for each note propose target folder, tags and 2–3 links to existing notes. Show the table, then wait."
- "Turn `Inbox/clip-2026-11-20.md` into a clean literature note in `Resources/` with properties and a 5-bullet summary."

## 6. Best practices

- **Start read-only**, widen step by step (MCPVault `--read-only`, `ask` rules, `plan` mode).
- **Git the vault** and commit before bigger agent sessions; review with `git diff` afterwards.
- **Write a vault `CLAUDE.md`**: structure, naming, tag scheme, what's off-limits. This makes the biggest quality difference.
- **Install `obsidian-skills`** so Claude writes valid wikilinks, callouts, properties, Bases and Canvas.
- **Bulk changes as proposal first** ("show a table, then wait"), then execute.
- **Prefer the CLI or REST API for search** in big vaults; grep across thousands of notes floods the context. Or delegate search to a subagent ([agents.md](agents.md)).
- **Don't let two writers fight:** avoid Claude editing a note you have open and are typing in; and with Obsidian Sync / iCloud / OneDrive, let sync settle before and after bulk edits to avoid conflict copies.
- **One server, one name:** don't register several Obsidian MCP servers at once; Claude gets confused about which tool to use.

## 7. Security

A vault is often **the most personal data you have** (journals, health, finances, work secrets), and often contains **content from the web** (Web Clipper, Readwise, RSS). That's exactly the dangerous mix (see the "lethal trifecta" in [mcp.md](mcp.md#7-security)).

**Data leaves your machine.** Everything Claude reads from the vault is sent to the model provider. Exclude what must not leave: deny `Read(./Private/**)`, MCPVault `--exclude` (note: only hides from search/listing, not from direct reads, so also deny via rules), or keep a separate vault for sensitive notes. Don't give the agent access to a vault that contains passwords, recovery codes or API keys at all.

**Prompt injection via notes.** Clipped web pages, imported emails, shared vaults or community templates can contain instructions ("ignore previous instructions and …"). Treat note content as data:
- In sessions that read clipped/foreign content, don't also allow network tools (`WebFetch`, `curl`) or write tools outside the vault.
- Be suspicious if Claude suddenly wants to edit `.obsidian/`, run `obsidian eval`, or fetch URLs that appear in a note.

**`.obsidian/` is code.** It holds community plugins (JavaScript that runs with full rights inside Obsidian) and their settings. An agent writing there can install or modify executable code. Deny `Edit(./.obsidian/**)`; never enable the REST plugin's "Allow access to the configuration directory"; MCPVault blocks it by default.

**CLI developer commands.** `obsidian eval` runs arbitrary JavaScript in the app, `plugin:reload` reloads code. Deny them unless you're developing a plugin.

**API key (REST plugin).** Treat it like a password: env variable, never in `.mcp.json`, CLAUDE.md or git. The server listens on localhost only; don't change the binding host to `0.0.0.0`. Prefer HTTPS (27124) over plain HTTP (27123). Rotate the key if it ever lands in a file or a transcript.

**Third-party MCP servers.** All Obsidian MCP servers are community projects. Pin a version (`@bitbonsai/mcpvault@x.y.z`, not `@latest`), read the README/changelog before upgrades, and keep them updated for security fixes (e.g. MCPVault fixed a symlink path traversal in v0.9.1; the REST plugin fixed `.obsidian` access in advisory GHSA-66m9-r757-qvq7).

**Destructive edits.** Bulk renames break links, bulk "cleanup" can delete content. Backups/git, `ask` for delete/move, "proposal first" rule in CLAUDE.md.

**Windows.** No native sandbox for Claude Code (see [permissions.md](permissions.md)); in way A the agent's Bash commands can reach everything your user can. Keep the deny rules tight, or run Claude Code in WSL2 with the vault mounted.

## 8. Checklist

- [ ] Vault backed up / in git, baseline commit made
- [ ] Chose a way: A (Claude Code), B (CLI), C (MCPVault), D (REST API)
- [ ] Vault `CLAUDE.md` with structure, conventions, off-limits folders
- [ ] `obsidian-skills` plugin installed
- [ ] Deny: `.obsidian/**` edits, private folders, `obsidian eval`/dev commands, deletes
- [ ] MCP server pinned to a version, started `--read-only`
- [ ] REST API key in an env variable, HTTPS, localhost only
- [ ] No sensitive vault + web-clipped content + network tools in the same session
- [ ] Bulk changes proposed first, reviewed with `git diff` afterwards

Sources:
- Obsidian CLI: https://obsidian.md/help/cli · changelog 1.12.4: https://obsidian.md/changelog/2026-02-27-desktop-v1.12.4/
- Obsidian skills: https://github.com/obsidianmd/obsidian-skills
- MCPVault: https://github.com/bitbonsai/mcpvault
- Local REST API: https://github.com/coddingtonbear/obsidian-local-rest-api
- Comparison (vendor blog): https://contextbolt.com/blog/obsidian-mcp-claude/
- Claude Code MCP: https://code.claude.com/docs/en/mcp
