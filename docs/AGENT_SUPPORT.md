# Agent support

codedna has two integration layers:

1. A reusable `SKILL.md` package for agents that support skill directories.
2. Repository instruction files that point every agent at the generated `CODEDNA.md` profile.

## Skill installs

`./install.sh` installs the same canonical skill bundle from `skill/` into each supported skill directory.

| Target | Command | Default destination |
| --- | --- | --- |
| All supported skill hosts | `./install.sh` | Claude Code, Codex, and Windsurf/Cascade |
| Claude Code | `./install.sh claude` | `~/.claude/skills/codedna/` |
| Codex | `./install.sh codex` | `~/.codex/skills/codedna/` |
| Windsurf/Cascade | `./install.sh windsurf` | `~/.codeium/windsurf/skills/codedna/` |

Destination overrides:

```sh
CLAUDE_SKILLS_DIR=/path/to/skills ./install.sh claude
CODEX_SKILLS_DIR=/path/to/skills ./install.sh codex
WINDSURF_SKILLS_DIR=/path/to/skills ./install.sh windsurf
```

## Project wiring

Map mode writes `CODEDNA.md`, then points the repo's agent instruction files at it with idempotent codedna markers.

| Agent | Instruction file |
| --- | --- |
| Portable baseline | `AGENTS.md` |
| Claude Code | `CLAUDE.md` |
| Gemini CLI | `GEMINI.md` |
| GitHub Copilot | `.github/copilot-instructions.md` |
| Cursor | `AGENTS.md` or `.cursor/rules/codedna.mdc` |
| Windsurf/Cascade | `AGENTS.md`, `.devin/rules/codedna.md`, or `.windsurf/rules/codedna.md` |

If a repo already uses one of these files, codedna updates only the block between `<!-- codedna:start -->` and `<!-- codedna:end -->`. If no agent instruction file exists, codedna creates `AGENTS.md` as the portable baseline unless the user asks otherwise.

## Release package install

Release tarballs contain the skill bundle, installer, docs, tests, and license:

```sh
curl -L https://github.com/aihxp/codedna/releases/download/v1.0.1/codedna-v1.0.1.tar.gz | tar xz
cd codedna-1.0.1
./install.sh
```
