---
name: kb-overview
description: Prints an overview of all topic files in the Claude knowledge base (claude_knowledge) with a summary, template check and example files. Use when the user asks what's in the knowledge base, which topics/Übersichten exist, or wants a table of contents or a health check of the .md files.
allowed-tools: Read Glob Grep
---

# Knowledge base overview

Read-only. Never change files in this skill.

## 1. Locate the knowledge base

- If the current project root contains both `README.md` and `agentic-coding.md`, use it.
- Otherwise use `E:/Work/claude_knowledge`.
- If neither exists, say so and stop.

## 2. Collect

For every `*.md` file directly in the knowledge base root, **except `README.md`**:

1. Title: the first `# ` heading.
2. Summary: the first sentence of the first paragraph under `## 1. What & when` (shorten to ≤ 15 words).
3. Template check: Grep the file for `^## [1-8]\. ` and compare against the 8 required sections:
   `1. What & when` · `2. How it works` · `3. Guide` · `4. Reference` · `5. Examples` · `6. Best practices` · `7. Security` · `8. Checklist`.
   A heading counts if it starts with the number and the name (e.g. `## 3. Guide: set it up` counts as Guide).
4. Line count.
5. Frontmatter: the file must start with `---` and contain `aliases:` and `tags:` (used by the Obsidian vault). Missing → warning.

Then:
- Glob `examples/**/*` (files only) and group them by subfolder (`agents`, `hooks`, `skills`, `plugin`).
- Read the README `## Files` table and collect the linked file names.

## 3. Output

Answer in the user's language. Format:

```
## Wissensbasis: <path>

| Datei | Thema | Kurzbeschreibung | Template | Zeilen |
|---|---|---|---|---|
| [agentic-coding.md](agentic-coding.md) | Agentic Coding (the workflow) | … | 8/8 | 154 |
| …

**Beispiele (`examples/`):** agents: code-reviewer.md, test-runner.md · hooks: … · skills: … · plugin: …

**Hinweise**
- <file>: fehlende Abschnitte: 5. Examples, 7. Security
- <file>: Frontmatter (aliases/tags) fehlt
- <file>: nicht in der README-Tabelle verlinkt
- README verlinkt <file>, die Datei fehlt
```

- Sort the table as in the README `## Files` table; unlisted files at the end.
- Links relative to the knowledge base root (as markdown links, so they're clickable).
- If there are no problems, write "Keine Auffälligkeiten" under **Hinweise**.
- No extra commentary beyond this. Offer `/kb-new-topic <topic>` in one line if the user seems to be looking for a topic that doesn't exist.
