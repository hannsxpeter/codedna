# Contributing to codedna

Thanks for your interest in improving codedna. It is a small project with a clear shape, so contributing is straightforward.

## What codedna is

codedna is a portable coding-agent skill installed as a directory for hosts that support `SKILL.md`. The entrypoint lives in [`skill/SKILL.md`](skill/SKILL.md), and executable helpers live beside it under [`skill/scripts/`](skill/scripts/). There is no build step and no runtime dependency to install.

Agent-specific install paths and project wiring are documented in [docs/AGENT_SUPPORT.md](docs/AGENT_SUPPORT.md). Keep target-specific details there rather than scattering them through the skill text.

## Ways to help

- **Sharpen the analysis.** Add a dimension worth capturing, or a language whose conventions are underserved (the config map and the stats helper both have room to grow).
- **Improve the AI-tells catalog.** If you have seen a recognizable tell that is not listed, propose it with a detect-and-fix entry.
- **Tune triggering.** The `description` in the frontmatter decides when the skill fires. If it over- or under-triggers for a real prompt, that is a useful issue.
- **Fix the stats helper.** It is best-effort and stdlib-only by design. Bug reports with a small reproducing snippet are welcome.

## Testing a change

Run the automated checks before opening a pull request:

```sh
python3 -m py_compile skill/scripts/codedna_stats.py
python3 -m py_compile skill/scripts/codedna_wire.py
python3 -m unittest discover -s tests
tmp="$(mktemp -d)"
CLAUDE_SKILLS_DIR="$tmp/claude" CODEX_SKILLS_DIR="$tmp/codex" CURSOR_SKILLS_DIR="$tmp/cursor" WINDSURF_SKILLS_DIR="$tmp/windsurf" ./install.sh all
```

If `shellcheck` is installed, run `shellcheck install.sh` as well.

Then validate the skill behavior manually:

1. Install your working copy with one target such as `./install.sh codex`, or use `./install.sh all` when you intentionally want every supported skill host.
2. In a supported coding-agent session, point it at a real repository: "build the codedna for this repo."
3. Read the generated `CODEDNA.md`. Ask whether each line is specific enough that it would read differently for a different codebase. Generic lines are the most common regression.

To sanity-check the stats helper on its own, run it against any repo. It only reads:

```sh
python3 skill/scripts/codedna_stats.py /path/to/some/repo
```

It should report a language inventory with naming-casing histograms, comment density, indentation, and quote style, and it should disclose capped samples, skipped oversized files, skipped minified files, and unreadable files.

The wiring helper writes files. It always creates or updates `AGENTS.md`, it adds or replaces a codedna block in `CLAUDE.md`, `GEMINI.md`, and `.github/copilot-instructions.md` when those files already exist, and it writes `.cursor/rules/codedna.mdc` or a Windsurf/Cascade `codedna.md` when the corresponding `.cursor/rules`, `.windsurf/rules`, or `.devin/rules` directory exists. Point it at a throwaway copy, not a repo you care about:

```sh
tmp="$(mktemp -d)" && cp -R /path/to/some/repo "$tmp/repo"
python3 skill/scripts/codedna_wire.py "$tmp/repo"
```

It should print one line per file it created or updated, and re-running it should leave those files byte-identical.

## Pull requests

- Keep prompt guidance in `skill/SKILL.md` and executable helper logic under `skill/scripts/`.
- Keep conventions concrete. The skill's whole thesis is specificity, so changes to its guidance should model that.
- Describe what you changed and, ideally, the before-and-after on a real repo.

## Reporting issues

Open an issue with the prompt you used, the repository shape (language, rough size), and what codedna produced versus what you expected. A short reproduction is worth more than a long description.
