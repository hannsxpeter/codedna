# Contributing to codedna

Thanks for your interest in improving codedna. It is a small project with a clear shape, so contributing is straightforward.

## What codedna is

codedna is a file-only Claude Code skill. The entire skill lives in [`codedna.md`](codedna.md): the frontmatter, the three modes (Map, Match, Check), the analysis dimensions, the AI-tells catalog, the output template, and an inlined stats helper. There is no build step and no dependency to install. Edits to the skill are edits to that one file.

## Ways to help

- **Sharpen the analysis.** Add a dimension worth capturing, or a language whose conventions are underserved (the config map and the stats helper both have room to grow).
- **Improve the AI-tells catalog.** If you have seen a recognizable tell that is not listed, propose it with a detect-and-fix entry.
- **Tune triggering.** The `description` in the frontmatter decides when the skill fires. If it over- or under-triggers for a real prompt, that is a useful issue.
- **Fix the stats helper.** It is best-effort and stdlib-only by design. Bug reports with a small reproducing snippet are welcome.

## Testing a change

The skill has no automated test suite; you validate it by running it.

1. Install your working copy: `./install.sh` (or `cp codedna.md ~/.claude/skills/codedna.md`).
2. In a Claude Code session, point it at a real repository: "build the codedna for this repo."
3. Read the generated `CODEDNA.md`. Ask whether each line is specific enough that it would read differently for a different codebase. Generic lines are the most common regression.

To sanity-check the inlined stats helper on its own, copy the `python` block out of `codedna.md` to a file and run it:

```sh
python3 codedna_stats.py /path/to/some/repo
```

It should report a language inventory with naming-casing histograms, comment density, indentation, and quote style, and it should never crash on a file it cannot parse.

## Pull requests

- Keep the skill a single self-contained file. Resist splitting it into multiple files; the file-only shape is intentional.
- Keep conventions concrete. The skill's whole thesis is specificity, so changes to its guidance should model that.
- Describe what you changed and, ideally, the before-and-after on a real repo.

## Reporting issues

Open an issue with the prompt you used, the repository shape (language, rough size), and what codedna produced versus what you expected. A short reproduction is worth more than a long description.
