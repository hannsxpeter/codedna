# codedna

> Fingerprint a codebase's style so AI-written code is indistinguishable from the author's own.

[![Release](https://img.shields.io/github/v/release/hannsxpeter/codedna?sort=semver)](https://github.com/hannsxpeter/codedna/releases)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Agent skill](https://img.shields.io/badge/coding%20agents-skill-8A2BE2)](https://agents.md)

codedna is a portable coding-agent skill. It studies a codebase the way you would study a writer's voice, writes the conventions down in a profile, and uses that profile so future contributions read as if the original author wrote them.

## The problem

AI-written code is usually correct but recognizably foreign. It carries tells: a comment on every line, variable names two words longer than you would pick, a `try/catch` you never would have wrapped, a helper extracted where you inline, cheerful comment prose where you are terse. Individually small; together they read as "not written by the person whose name is on the rest of the repo."

The reason most style guides miss this: formatters already enforce surface style. Indentation, quotes, and semicolons get rewritten the moment someone runs Prettier, Black, gofmt, or rustfmt. The fingerprint that actually distinguishes a person lives in the choices no formatter touches, what they name things, how much they comment and in what voice, how big their functions get, how defensively they handle errors, and the small idioms they reuse. codedna spends its attention there.

## What it does

Three modes, one profile:

| Mode | What it does | Say something like |
| --- | --- | --- |
| **Map** | Scan a codebase and write `CODEDNA.md`, the style profile. | "build the codedna for this repo" |
| **Match** | Write new code that follows the profile so it blends in. | "add this in the style of the repo" |
| **Check** | Review a diff or file against the profile and report the tells. | "does this look AI-generated?" |

Map also wires idempotent pointers into agent instruction files, so the profile loads automatically in the tools your repo uses and actually gets used.

## Install

codedna installs as a standard `SKILL.md` directory for supported skill-capable agents:

```sh
git clone https://github.com/hannsxpeter/codedna.git
cd codedna
./install.sh codex
```

Choose the target you use: `./install.sh claude`, `./install.sh codex`, `./install.sh cursor`, or `./install.sh windsurf`. To install into every supported skill host deliberately, run `./install.sh all`.

Or install it by hand for any `SKILL.md` host:

```sh
mkdir -p <skills-dir>/codedna/scripts
cp skill/SKILL.md <skills-dir>/codedna/SKILL.md
cp skill/scripts/codedna_stats.py <skills-dir>/codedna/scripts/codedna_stats.py
cp skill/scripts/codedna_wire.py <skills-dir>/codedna/scripts/codedna_wire.py
chmod +x <skills-dir>/codedna/scripts/codedna_*.py
```

Then restart the target coding agent. It triggers on phrases like "match my coding style", "capture the conventions", "make it look like I wrote it", or an explicit "codedna".

## Agent support

| Agent | How codedna integrates |
| --- | --- |
| Claude Code | Global skill install plus `CLAUDE.md` project wiring. |
| Codex | Global skill install plus `AGENTS.md` project wiring. |
| Gemini CLI | `GEMINI.md` project wiring. |
| GitHub Copilot | `.github/copilot-instructions.md` project wiring. |
| Cursor | Global skill install plus `AGENTS.md` or `.cursor/rules/codedna.mdc` project wiring. |
| Windsurf/Cascade | Global skill install plus `AGENTS.md`, `.devin/rules/`, or `.windsurf/rules/` project wiring. |

See [docs/AGENT_SUPPORT.md](docs/AGENT_SUPPORT.md) for install paths, overrides, and release package install.

## Usage

Map a repository:

```
> build the codedna for this repo
```

codedna reads the linter and formatter configs as ground truth, runs a bundled stdlib-only stats pass for grounded frequencies (naming casing, comment density, indentation, quotes), close-reads a representative sample for voice, then writes `CODEDNA.md` and points the repo's agent instruction files at it.

Write code that blends in:

```
> add a delete endpoint, in the style of the rest of the repo
```

Check code for tells before you commit:

```
> check this diff against the codedna
```

Optional pre-commit hook:

```sh
cat > .git/hooks/pre-commit <<'HOOK'
#!/usr/bin/env sh
# Replace agent-cli with your preferred coding agent command.
agent-cli "check the staged diff against the codedna"
HOOK
chmod +x .git/hooks/pre-commit
```

## What it captures

- **Naming**, casing per identifier kind, verb dialect (`get` vs `fetch` vs `load`), abbreviations, boolean prefixes, file-name style.
- **Comments and documentation**, density, the why-vs-what split, register (terse fragments vs full sentences), doc-comment norms.
- **Structure**, function size, extraction threshold, file organization, paradigm.
- **Control flow and error handling**, early returns vs nesting, async style, how defensive the code is.
- **Types, imports, tests**, and the conventions that govern them.
- **Idioms and vocabulary**, the reused helpers and domain words that make code recognizably one author's.
- **AI tells**, the specific places the author is the opposite of the AI default, so contributions slip there most easily.

## The generated profile

`CODEDNA.md` is human-readable and specific. A TL;DR section looks like this:

```markdown
## TL;DR
1. Functions and variables are camelCase; types PascalCase; constants SCREAMING_SNAKE.
2. Comment only the non-obvious why. Most functions have no comment.
3. Errors are terse `throw new Error("...")`. No custom error classes.
4. Functions are small (median ~9 lines); repetition is tolerated over premature abstraction.
```

Every line is concrete enough that it would read differently for a different codebase. The skill enforces that discipline: if a convention would be true of almost any repo, it gets sharpened or cut.

## How it works

codedna analyzes in layers, cheapest and most authoritative first:

1. **Config files** (`.editorconfig`, Prettier, ESLint, `pyproject.toml`, `rustfmt.toml`, and friends) are enforced, so they settle whole categories up front and are recorded as such.
2. **Bundled stdlib-only helpers** ground the profile in real frequencies and wire `CODEDNA.md` into agent instruction files.
3. **Close reading** of a representative sample captures the voice that numbers cannot.

The skill entrypoint lives at `skill/SKILL.md`, with executable helpers kept as files beside it so they can be run and tested directly. Agents without a global skill mechanism still benefit from the generated `CODEDNA.md` and repo-level instruction files.

## Contributing

Issues and pull requests are welcome. See [CONTRIBUTING.md](CONTRIBUTING.md) for how to test changes to the skill, and [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md) for the ground rules.

## License

[MIT](LICENSE).
