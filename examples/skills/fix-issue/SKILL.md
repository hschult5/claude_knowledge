---
name: fix-issue
description: Fix a GitHub issue end to end. Only run when the user explicitly invokes it.
argument-hint: "[issue-number]"
disable-model-invocation: true
---

Fix GitHub issue #$ARGUMENTS:

1. Read the issue with `gh issue view $ARGUMENTS`.
2. Find the relevant code and reproduce the problem with a failing test.
3. Implement the minimal fix.
4. Run the test suite and the linter; fix anything you broke.
5. Commit with message `fix: <summary> (#$ARGUMENTS)`. Do not push.
6. Report what you changed and why, in 5 lines or fewer.

<!--
disable-model-invocation: true  → Claude never starts this on its own (it commits).
Usage: /fix-issue 123
-->
