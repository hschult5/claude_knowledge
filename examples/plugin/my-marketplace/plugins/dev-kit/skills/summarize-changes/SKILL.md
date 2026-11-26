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

<!--
Install: copy this folder to ~/.claude/skills/summarize-changes/ (all projects)
or to <repo>/.claude/skills/summarize-changes/ (this repo).
Run with /summarize-changes, or just ask "what did I change?".
-->
