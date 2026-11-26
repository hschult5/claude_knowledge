# Example marketplace with one plugin (`dev-kit`)

```text
my-marketplace/
├── .claude-plugin/marketplace.json
└── plugins/dev-kit/
    ├── .claude-plugin/plugin.json
    ├── skills/summarize-changes/SKILL.md   -> /dev-kit:summarize-changes
    ├── agents/code-reviewer.md             -> agent dev-kit:code-reviewer
    ├── hooks/hooks.json                    -> blocks rm -rf etc., formats after edits
    └── scripts/*.py                        -> called by the hooks (needs Python on PATH)
```

Try it:

```bash
# 1. just this session, no install
claude --plugin-dir E:/Work/claude_knowledge/examples/plugin/my-marketplace/plugins/dev-kit

# 2. or install via the local marketplace
claude plugin validate E:/Work/claude_knowledge/examples/plugin/my-marketplace
claude plugin marketplace add E:/Work/claude_knowledge/examples/plugin/my-marketplace
claude plugin install dev-kit@my-marketplace
claude plugin list
```

To share it: push `my-marketplace/` to a GitHub repo, then others run
`claude plugin marketplace add <you>/<repo>` and `claude plugin install dev-kit@my-marketplace`.
