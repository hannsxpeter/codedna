# Changelog

All notable changes to codedna are documented in this file. The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.4] - 2026-08-01

Robustness release. One wiring fix restores a guarantee the docs already made. Nothing here changes a measurement, so profiles generated with 1.0.3 report the same numbers.

### Fixed

- Stop the wiring helper from deleting content between an unpaired `<!-- codedna:start -->` marker and the real block below it. A file left carrying a start marker with no matching end marker lost everything in between on the second run, including another tool's block and the user's own prose. `docs/AGENT_SUPPORT.md` already stated that the rest of the file is left untouched; now it is. The unpaired marker is left where it sits rather than absorbed.

### Changed

- Pass the block markers explicitly from `write_target` into `replace_block` instead of letting them fall back to the module constants. Output is byte-identical. The helper no longer assumes the markers it is handed are the ones it was built with.
- Correct `skill/SKILL.md`, which called the TODO/FIXME figure a density. The stats helper reports a count.

### Added

- Add regression tests for the unpaired-marker fix, for a start marker appearing inside the block being replaced, and for `replace_block` with non-default markers. The suite is 36 tests.

## [1.0.3] - 2026-07-31

Accuracy release. Every change below corrects a measurement or a claim that was wrong, so profiles generated with 1.0.2 may report different numbers after upgrading. That is the point.

### Fixed

- Fix comment density and code-line counts for Python files that open a multi-line string mid-line (SQL blobs, templates, prompt constants). The closing triple quote was read as the start of a docstring, so the remainder of the file was counted as comment. On codedna's own repository this reported 13.4% comment density against a true 0.9%.
- Count multi-line JSDoc blocks as documentation. Only single-line `/** ... */` was recognized, understating doc-comment coverage on any codebase that uses conventional JSDoc.
- Stop counting a plain `//` aside as a doc comment outside Go. Go keeps `//`, since that is its documentation convention.
- Measure function length in tab-indented Python. Every function in a tab-indented file was reported as one line long.
- Read files with a UTF-8 byte order mark so the first line is not hidden from every pattern.
- Skip minified and generated files, which dominated naming and identifier-length histograms and could invert the reported dominant convention. Skipped files are disclosed in the output.
- Require a word boundary for boolean prefixes, so `issue` and `island` no longer count as `is`-prefixed.
- Do not count blank lines inside a block comment toward a metric defined as a percentage of non-blank lines.
- Match the `<!-- codedna:start -->` and `<!-- codedna:end -->` markers as a pair when wiring. A stray closing marker earlier in the file made every run append another block.
- Preserve indentation after the wired block, and leave instruction files byte-identical when re-wiring. The second run on a fresh repository previously produced a spurious diff.

### Changed

- Note in the stats output when `UPPER` marks a single-word all-caps constant compatible with `SCREAMING_SNAKE`, mirroring the existing `lower` note.
- Correct `CONTRIBUTING.md`, which presented the wiring helper as a read-only sanity check. It writes files, and the instructions now say so and point at a throwaway copy.
- Correct `docs/AGENT_SUPPORT.md`, which said `AGENTS.md` is created only when no other instruction file exists. It is created or updated either way.

### Added

- Add regression tests for every fix above, doubling the suite from 15 tests to 33.
- Add a test asserting the version in `skill/SKILL.md` matches every other version reference in the skill and the agent support docs, including the release tarball URL.
- Accept `start_marker` and `end_marker` arguments in `replace_block`. Nothing passes them yet; they exist so a sibling skill can reuse the helper without its markers defaulting to codedna's.

## [1.0.2] - 2026-07-13

### Changed

- Make `install.sh` require an explicit target (`all`, `claude`, `codex`, `cursor`, or `windsurf`) instead of installing into every supported agent home by default.
- Update docs and release package examples for the canonical `hannsxpeter/codedna` repository.
- Update generated profile templates to identify codedna v1.0.2.

### Added

- Add `skill/scripts/codedna_wire.py`, a tested helper for idempotently wiring `CODEDNA.md` into `AGENTS.md`, `CLAUDE.md`, `GEMINI.md`, GitHub Copilot instructions, Cursor rules, and Windsurf/Cascade rules.
- Add deeper stats helper metrics for function-size distribution, identifier-length distribution, boolean-prefix share, TODO/FIXME density, and doc-comment coverage.
- Add tests for wiring behavior, safer installer defaults, and the new metrics.

## [1.0.1] - 2026-06-11

### Fixed

- Install codedna as a standard `SKILL.md` directory for Claude Code, Codex, and Windsurf/Cascade instead of a bare markdown file that skill hosts do not load.
- Remove stale bare-file installs from skill directories where applicable.

### Changed

- Move the skill entrypoint to `skill/SKILL.md`.
- Extract the stats helper to `skill/scripts/codedna_stats.py` so it is executed as a bundled script instead of transcribed from markdown.
- Stamp generated profile templates with the codedna version and generation date.
- Weight author-scoped file sampling by touch frequency instead of treating every touched file equally.
- Default Check mode to the current diff when no review target is specified, and warn when a profile looks stale.
- Replace Claude-only Map wiring with portable project wiring for `AGENTS.md`, `CLAUDE.md`, `GEMINI.md`, GitHub Copilot instructions, Cursor rules, and Windsurf/Cascade rules.

### Added

- Add unit tests and GitHub Actions CI for the stats helper and installer.
- Add a local markdown-link test and a README pre-commit hook recipe.
- Add helper safeguards for capped samples, oversized files, context-managed reads, JS arrow-function detection, and language-aware quote reporting.
- Add multi-target installer support for `all`, `claude`, `codex`, and `windsurf`.
- Add an agent support matrix in `docs/AGENT_SUPPORT.md`.

## [1.0.0] - 2026-06-06

Initial release.

### Added

- **Map mode**: scan a codebase and generate `CODEDNA.md`, a specific, evidence-backed profile of its naming, formatting, comment voice, structure, error handling, types, imports, tests, and idioms. Reads linter and formatter configs as enforced ground truth, separated from observed conventions.
- **Match mode**: write new code that follows an existing `CODEDNA.md`, deferring to the local file's dialect on conflicts.
- **Check mode**: review a diff, file, or pasted output against the profile and report deviations by category, with severity and concrete rewrites.
- **CLAUDE.md wiring**: Map writes an idempotent, clearly-marked pointer block into the target repo's `CLAUDE.md` so the profile loads automatically and is actually consulted.
- **AI-tells catalog**: a self-check list and 15 cataloged tells (over-commenting, defensive boilerplate, vocabulary drift, and more) used by Match to avoid and by Check to flag.
- **Inlined stats helper**: a stdlib-only Python script embedded in the skill that reports naming-casing histograms, comment density (including block and doc comments), indentation, and quote style to ground the profile in real frequencies.
- **Profile template**: a fixed `CODEDNA.md` structure that enforces specificity and pairs every convention with a real snippet.
- Packaged as a single self-contained file, `codedna.md`, plus an `install.sh` for one-command installation.

[1.0.4]: https://github.com/hannsxpeter/codedna/releases/tag/v1.0.4
[1.0.3]: https://github.com/hannsxpeter/codedna/releases/tag/v1.0.3
[1.0.2]: https://github.com/hannsxpeter/codedna/releases/tag/v1.0.2
[1.0.1]: https://github.com/hannsxpeter/codedna/releases/tag/v1.0.1
[1.0.0]: https://github.com/hannsxpeter/codedna/releases/tag/v1.0.0
