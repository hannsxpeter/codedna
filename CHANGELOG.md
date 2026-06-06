# Changelog

All notable changes to codedna are documented in this file. The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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

[1.0.0]: https://github.com/aihxp/codedna/releases/tag/v1.0.0
