# Plugins & Marketplaces

*Part of the [Claude Code knowledge base](README.md). Every topic file uses the same sections: What & when · How it works · Guide · Reference · Examples · Best practices · Security · Checklist.*

## 1. What & when

A **plugin** is a folder that bundles Claude Code extensions so you can install, share and version them as **one unit**. Think "npm package for your Claude setup". A **marketplace** is a git repo/folder that lists plugins so others can install them.

What plugins add on top of loose files in `.claude/`:
- **Distribution**: one command installs it on any machine, for the whole team.
- **Versioning & updates** from the marketplace.
- **Namespacing**: `/deploy-tools:deploy`, agent `deploy-tools:reviewer`, no clashes.
- **Enable/disable as a whole**, per user or per project.
- **User config**: the plugin prompts for settings and secrets (`userConfig`).

> Start with loose files in `.claude/` or `~/.claude/`. Turn them into a plugin once you want to reuse them across repos/machines or share them.

## 2. How it works

Everything from the other pages can live in a plugin:

| Component | Location in the plugin | See |
|---|---|---|
| Skills | `skills/<name>/SKILL.md` | [skills.md](skills.md) |
| Commands (legacy) | `commands/*.md` | [skills.md](skills.md) |
| Subagents | `agents/*.md` | [agents.md](agents.md) |
| Hooks | `hooks/hooks.json` | [hooks.md](hooks.md) |
| MCP servers | `.mcp.json` | [mcp.md](mcp.md) |
| LSP servers | `.lsp.json` | code intelligence |
| Output styles | `output-styles/` | response formatting |
| Executables | `bin/` | on the Bash tool's `PATH` while enabled |
| Monitors (experimental) | `monitors/monitors.json` | background watchers |
| Default settings | `settings.json` | only `agent` and `subagentStatusLine` apply |
| Manifest | `.claude-plugin/plugin.json` | metadata, config (optional) |

A `CLAUDE.md` at the plugin root is **not** loaded; put instructions in a skill.

The same format is used by Claude's agent mode in the desktop/web app and by org plugin catalogs on claude.ai. Restriction there: no plugins with a top-level `bin/`.

## 3. Guide: build, test, share

1. **Create the layout** (components at the plugin root, only `plugin.json` inside `.claude-plugin/`):

   ```text
   deploy-tools/
   ├── .claude-plugin/plugin.json
   ├── skills/deploy/SKILL.md
   ├── agents/reviewer.md
   ├── hooks/hooks.json
   ├── scripts/format.sh
   ├── .mcp.json
   └── README.md
   ```

2. **Test without installing:** `claude --plugin-dir ./deploy-tools`. Edit, then `/reload-plugins`.
3. **Validate:** `claude plugin validate ./deploy-tools` (`--strict` in CI).
4. **Create a marketplace** repo with `.claude-plugin/marketplace.json` listing the plugin.
5. **Install:** `claude plugin marketplace add your-org/my-marketplace`, then `claude plugin install deploy-tools@my-marketplace`.
6. **Share with the team:** run `claude plugin marketplace add your-org/my-marketplace --scope project` in the repo and commit `.claude/settings.json`; add `enabledPlugins` there to turn plugins on for the repo.
7. **Release:** bump `version`, update CHANGELOG, users pull with `/plugin marketplace update`.

## 4. Reference

### Manifest `.claude-plugin/plugin.json`

Optional; without it, default locations are loaded.

```json
{
  "name": "deploy-tools",
  "displayName": "Deploy Tools",
  "version": "1.2.0",
  "description": "Deployment skills, a review agent and safety hooks",
  "author": { "name": "Your Name" },
  "repository": "https://github.com/you/deploy-tools",
  "license": "MIT",
  "dependencies": ["secrets-vault"],
  "userConfig": {
    "api_token": { "type": "string", "title": "API token", "description": "Token for the deployment API", "sensitive": true }
  }
}
```

| Field | Notes |
|---|---|
| `name` | **Only required field.** kebab-case, namespace for all components. `claude-`, `anthropic-` prefixes reserved |
| `version` | Pins users to that version until you bump it. Use semver |
| `description`, `author`, `homepage`, `repository`, `license`, `keywords` | Metadata |
| `defaultEnabled` | Default `true` |
| `dependencies` | Other plugins that must be enabled |
| `userConfig` | Prompted values; `sensitive: true` stores them in the OS credential store |
| `skills`, `agents`, `commands`, `hooks`, `mcpServers`, `lspServers`, `outputStyles` | Override paths (must start with `./`, stay inside the plugin) or define inline |

### Path variables

| Variable | Points to | Use for |
|---|---|---|
| `${CLAUDE_PLUGIN_ROOT}` | Installed plugin version | Bundled scripts. **Changes on update, don't write here** |
| `${CLAUDE_PLUGIN_DATA}` | `~/.claude/plugins/data/<id>/` | State, caches, `node_modules` |
| `${CLAUDE_PROJECT_DIR}` | Project root | Project files |

User config: `${user_config.KEY}` (MCP/LSP config, exec-form hook `args`, skill/agent text) or `$CLAUDE_PLUGIN_OPTION_<KEY>` (env var in hooks). Shell-form hook commands reject `${user_config.*}` on purpose (injection risk).

### Marketplace `.claude-plugin/marketplace.json`

```json
{
  "name": "my-marketplace",
  "owner": { "name": "Your Name" },
  "plugins": [
    { "name": "deploy-tools", "source": "./plugins/deploy-tools", "description": "Deployment skills, review agent, safety hooks" },
    { "name": "lint-kit", "source": { "source": "github", "repo": "your-org/lint-kit" } }
  ]
}
```

- Required: `name`, `owner`, `plugins`; each entry `name` + `source` (same name as in `plugin.json`).
- `source` types: relative path (no `..`), `github`, `git-subdir`, `url`, `archive`, `npm`, `command`.

### Commands

```bash
claude --plugin-dir ./deploy-tools                     # load for one session
claude plugin validate ./deploy-tools --strict
claude plugin marketplace add ./my-marketplace         # or your-org/repo
claude plugin install deploy-tools@my-marketplace
claude plugin list
claude plugin details deploy-tools
claude plugin marketplace remove my-marketplace        # also uninstalls its plugins
```

In a session: `/plugin` (browse, install, enable/disable, errors), `/reload-plugins`.

## 5. Examples

Full working example in [examples/plugin/my-marketplace/](examples/plugin/my-marketplace/): a marketplace with one plugin `dev-kit` that bundles the `summarize-changes` skill, the `code-reviewer` agent and the format/guard hooks.

Plugin hook (`hooks/hooks.json`):

```json
{
  "hooks": {
    "PostToolUse": [
      { "matcher": "Edit|Write", "hooks": [ { "type": "command", "command": "\"${CLAUDE_PLUGIN_ROOT}\"/scripts/format.sh" } ] }
    ]
  }
}
```

## 6. Best practices

- One plugin = one coherent purpose ("dotnet-dev", "release-tools"), not a grab bag.
- `README.md` explaining every skill/agent/hook and **what it runs**.
- Prefer `skills/` over `commands/`.
- `claude plugin validate --strict` in CI for your marketplace repo.
- Bump `version` on every release; keep a CHANGELOG.
- State in `${CLAUDE_PLUGIN_DATA}`, never `${CLAUDE_PLUGIN_ROOT}`.

## 7. Security

A plugin is **code you run with your user rights**: hooks fire automatically, MCP servers start as processes, `bin/` executables land on `PATH`, skills can run `!` commands. Installing a plugin ≈ running `npm install` + a postinstall script from that author.

- **Only install from sources you trust.** Before enabling, read `hooks/hooks.json`, `.mcp.json`, `bin/`, scripts and every skill's `allowed-tools` / `!` lines.
- **Pin versions** for anything important; review the diff before bumping. A marketplace update can change what runs.
- **Project-scoped marketplaces** in a cloned repo's `.claude/settings.json` get registered when you trust the folder; check `extraKnownMarketplaces` / `enabledPlugins` there.
- **Secrets:** use `userConfig` with `sensitive: true`; never hardcode tokens (the validator warns about literal credentials in MCP headers).
- Don't splice `${user_config.*}` into shell strings; use exec-form `args` or env vars.
- **Orgs:** managed settings can restrict allowed marketplaces/plugins, require specific ones, and set `allowManagedHooksOnly`.
- Your own marketplace repo: branch protection + review, because a merge there ships code to every teammate's machine.

## 8. Checklist

- [ ] Components at plugin root, only `plugin.json` in `.claude-plugin/`
- [ ] Tested with `--plugin-dir`, validated with `--strict`
- [ ] README lists everything that executes
- [ ] Secrets via `userConfig` `sensitive: true`
- [ ] Third-party plugins reviewed and version-pinned
- [ ] Marketplace repo protected and reviewed

Sources: https://code.claude.com/docs/en/plugins/manifest-reference · https://code.claude.com/docs/en/plugin-marketplaces · https://code.claude.com/docs/en/plugins-reference
