# Agent support

codedna has two integration layers:

1. A reusable `SKILL.md` package for agents that support skill directories.
2. Repository instruction files that point every agent at the generated `CODEDNA.md` profile.

## Skill installs

`./install.sh <target>` installs the same canonical skill bundle from `skill/` into the selected supported skill directory.

| Target | Command | Default destination |
| --- | --- | --- |
| All supported skill hosts | `./install.sh all` | Claude Code, Codex, Cursor, and Windsurf/Cascade |
| Claude Code | `./install.sh claude` | `~/.claude/skills/codedna/` |
| Codex | `./install.sh codex` | `~/.codex/skills/codedna/` |
| Cursor | `./install.sh cursor` | `~/.cursor/skills/codedna/` |
| Windsurf/Cascade | `./install.sh windsurf` | `~/.codeium/windsurf/skills/codedna/` |

Destination overrides:

```sh
CLAUDE_SKILLS_DIR=/path/to/skills ./install.sh claude
CODEX_SKILLS_DIR=/path/to/skills ./install.sh codex
CURSOR_SKILLS_DIR=/path/to/skills ./install.sh cursor
WINDSURF_SKILLS_DIR=/path/to/skills ./install.sh windsurf
```

## Project wiring

Map mode writes `CODEDNA.md`, then points the repo's agent instruction files at it with idempotent codedna markers.
The bundled `skill/scripts/codedna_wire.py` helper performs this update and preserves unrelated file content.

| Agent | Instruction file |
| --- | --- |
| Portable baseline | `AGENTS.md` |
| Claude Code | `CLAUDE.md` |
| Gemini CLI | `GEMINI.md` |
| GitHub Copilot | `.github/copilot-instructions.md` |
| Cursor | `AGENTS.md` or `.cursor/rules/codedna.mdc` |
| Windsurf/Cascade | `AGENTS.md`, `.devin/rules/codedna.md`, or `.windsurf/rules/codedna.md` |

If a repo already uses one of these files, codedna updates only the block between `<!-- codedna:start -->` and `<!-- codedna:end -->` and leaves the rest of the file untouched. By default codedna creates or updates `AGENTS.md` as the portable baseline whether or not other instruction files are present, and it updates the tool-specific files or rule directories the repo already has. Run the helper with `--all` to create every supported file, or with `--agent <name>` to select specific targets.

## Release package install

Release tarballs contain the skill bundle, installer, docs, tests, and license:

```sh
curl -L https://github.com/hannsxpeter/codedna/releases/download/v1.1.0/codedna-v1.1.0.tar.gz | tar xz
cd codedna-1.1.0
./install.sh codex
```
