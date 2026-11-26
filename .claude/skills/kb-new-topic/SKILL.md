---
name: kb-new-topic
description: Creates a new topic file in the Claude knowledge base (claude_knowledge) following the 8-section template, researched from official docs, and adds it to the README. Only run when the user explicitly invokes it.
argument-hint: "[topic]"
disable-model-invocation: true
allowed-tools: Read Glob Grep
---

# New knowledge base topic: $ARGUMENTS

## 1. Locate and check

- Knowledge base = current project root if it contains `README.md` and `agentic-coding.md`, else `E:/Work/claude_knowledge`.
- If `$ARGUMENTS` is empty, ask for the topic and stop.
- Filename: short kebab-case slug of the topic (`status line` → `status-line.md`, `GitHub Actions` → `github-actions.md`).
- If that file (or an obviously equivalent one, check the README `## Files` table) already exists: stop, say so, and offer to extend the existing file instead.

## 2. Learn the house style

Read `README.md` and two existing topic files, preferably `hooks.md` (a Claude Code mechanism) and `obsidian.md` (an integration). Match their tone, depth, table style and length (roughly 120–230 lines).

## 3. Research

- Official sources first: https://code.claude.com/docs/en/… for Claude Code features, the vendor's own docs/README for tools and integrations. Community blogs only as a supplement, and mark them as such.
- Use WebSearch and fetch the key pages (web-fetch agent if there's no WebFetch tool). Prefer exact commands, settings keys, flags, file paths, version numbers.
- Note what you could **not** verify. Don't invent setting names or flags; leave them out or mark them "unverified".
- Look for: setup steps, Windows specifics (the user is on Windows 10, PowerShell + Git Bash), security risks and mitigations.

## 4. Write the file

Use [template.md](template.md) as the skeleton. Rules:

- **English**, like all other topic files.
- **Frontmatter first** (the knowledge base is linked into an Obsidian vault): 2 `aliases` (short name + alternative) and `tags`: always `claude-code`, plus `claude-code/mechanism` (a Claude Code feature), `claude-code/integration` (an external tool) or `claude-code/workflow`; add `security` if security is a main theme. Check existing aliases with Grep so none clash.
- Links between topic files stay **relative Markdown links** (`[hooks.md](hooks.md)`), not `[[wikilinks]]`: Obsidian's graph picks them up and GitHub still renders them.
- **All 8 sections, numbered exactly**: `## 1. What & when` … `## 8. Checklist` (subtitle after a colon is fine: `## 3. Guide: set it up`).
- Header: the standard italic "Part of the knowledge base" line, plus a "Written <today's date> from <sources>" line.
- Concrete over generic: real commands, JSON/YAML, file paths, copy-paste examples.
- Section 7 = risks **specific to this topic** + concrete measures (permission rules, settings, hooks), linking [permissions.md](permissions.md), [hooks.md](hooks.md), [mcp.md](mcp.md) etc. where they apply. No generic filler.
- Section 8 = `- [ ]` checklist, 5–9 items.
- End with `Source:` / `Sources:` and the URLs used.
- Link related topic files with relative links.
- No secrets, real personal data or the user's paths beyond `C:\Users\<you>` placeholders.

## 5. Register it

- Add one row to the README `## Files` table (before the `examples/` row): `` | [`<slug>.md`](<slug>.md) | <Topic>: <short what it covers> | ``.
- If the topic belongs in the README's mental model, scopes or commands tables, add a row there too.
- Add a cross-link from at most 1–2 closely related topic files, only where a reader would really look for it.

## 6. Report

In the user's language, short:
- File created (link), README updated (what), other files touched.
- What could not be verified / should be checked against the docs.
- Suggest running `/kb-overview` to check the template (should show 8/8).
