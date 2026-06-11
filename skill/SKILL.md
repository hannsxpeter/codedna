---
name: codedna
description: Generate a "DNA profile" of a codebase's coding style (naming conventions, formatting, comment voice, structural habits, error-handling philosophy, and idioms), then use it so new or AI-written code is indistinguishable from the existing author's code. Use this skill whenever the user wants to match a codebase's existing style, make AI contributions "blend in", "mimic" or "fingerprint" a coding style, capture house conventions, build a style guide from existing code, onboard to an unfamiliar repo's conventions, or check whether code "looks AI-generated" / has tells. Triggers on phrases like "match my coding style", "make it look like I wrote it", "codedna", "capture the conventions", "style guide from the code", "why does this read as AI-generated", "genetic map of the code", "mimic the codebase", and on any request to contribute significant code to an existing repo where matching house style matters.
allowed-tools: Read, Glob, Grep, Bash, Write, Edit
---

# CodeDNA

Version: 1.0.1

## What this is, and why it matters

AI-written code is usually correct but recognizably foreign. It carries tells: a comment on every line, variable names two words longer than the human would pick, a try/catch the author never would have wrapped, a helper extracted where the author inlines, cheerful comment prose where the author is terse. Individually small; together they read as "not written by the person whose name is on the rest of the repo."

CodeDNA closes that gap. It studies a codebase the way you would study a writer's voice, writes the conventions down in a profile, and uses that profile so future contributions match. The goal is not "good code in the abstract"; it is code that reads as if the original author wrote it.

One idea runs through everything: **most surface formatting is already enforced by tooling, so it is not where the fingerprint lives.** Indentation, quotes, and semicolons get rewritten the moment someone runs Prettier, Black, gofmt, or rustfmt. The fingerprint that distinguishes a person is in the choices no formatter touches: what they name things, how much they comment and in what voice, how big their functions get, early returns versus nested conditionals, how defensively they handle errors, and the small idioms they reuse. Spend your attention there.

## Three modes

Read the user's intent and pick one.

- **Map** (default): scan a codebase and produce `CODEDNA.md`. Triggered by "capture the style", "build the codedna", "map this repo".
- **Match**: write new code that follows an existing `CODEDNA.md` so it blends in. Triggered by "add X in the style of this repo", "write this so it looks like I wrote it".
- **Check**: review code (a diff, a file, pasted output) against `CODEDNA.md` and report where it betrays a different author. Triggered by "does this look AI-generated", "check this against the codedna".

If a repo has no `CODEDNA.md` yet and the user wants Match or Check, run Map first.

---

## Mode: Map

Work in layers, cheapest and most authoritative first.

**1. Scope.** Confirm what you are profiling (repo, subdir, or one language). Default to the repo root; in a polyglot repo, produce one section per significant language. Sample representative files (entry points, core modules, a few tests), do not read everything. Skip vendored and generated code (`node_modules`, `dist`, `build`, lockfiles, migrations, anything in `.gitignore`).

**2. Read ground truth.** Config files are enforced, so they settle whole categories before you read source. Find and read whatever exists (see the [config map](#config-map) below), record each rule as **enforced**, and note the command that applies it (`npm run format`, `ruff format .`, `gofmt -w .`). Code that passes the formatter inherits these for free, so the profile says "run X" rather than re-deriving them.

**3. Measure.** Run the bundled [stats helper](#stats-helper) to get histograms the eye cannot estimate (naming casing per kind, comment density, indentation, quote style). Treat its output as evidence to interpret, not as the profile. If it disagrees with the code, trust the code.

**4. Close-read for voice.** Numbers cannot capture voice. Read your sample against [What to look for](#what-to-look-for) and note especially where the author is the opposite of an [AI tell](#ai-tells), because those are the spots contributions slip.

**5. Optional: focus on one author.** To mimic a specific person in a multi-contributor repo, isolate their files first, then sample from those and note the profile is author-scoped:
```
git log --author="<name-or-email>" --pretty=format: --name-only | sort | uniq -c | sort -rn | head -30
```
For heavily-shared files, spot-check `git blame` before treating them as representative.

**6. Write CODEDNA.md.** Synthesize into the target repo's `CODEDNA.md` using the [template](#codednamd-template). Hold to these standards, a profile that fails them will not change how code gets written:
- **Specific, not generic.** "Uses descriptive names" is worthless. "Functions are verb-first camelCase (`loadUser`); booleans are `is`/`has`-prefixed; collections are plural" is usable. If a line would be true of any repo, sharpen or cut it.
- **Show, do not just tell.** Pair each convention with a real two-to-four-line snippet from the codebase.
- **Note the dominant pattern and its real exceptions.** Characteristic inconsistencies are part of the fingerprint ("named exports, but components are default-exported").
- **Separate enforced from observed**, so a reader knows what is load-bearing.

**7. Wire it in.** A profile no agent loads changes nothing. After writing `CODEDNA.md`, add or replace an idempotent codedna block in the agent instruction files the repo uses. Always create or update `AGENTS.md` as the portable baseline unless the user asks otherwise. Also update tool-specific files when they already exist or when the user asks for all-agent wiring:
- `CLAUDE.md` for Claude Code.
- `GEMINI.md` for Gemini CLI.
- `.github/copilot-instructions.md` for GitHub Copilot.
- `.cursor/rules/codedna.mdc` for Cursor project rules.
- `.devin/rules/codedna.md` or `.windsurf/rules/codedna.md` for Windsurf/Cascade rules.

Use this markdown block for plain instruction files (`AGENTS.md`, `CLAUDE.md`, `GEMINI.md`, and Copilot instructions):
```
<!-- codedna:start -->
## Code style

When writing or editing code in this repo, match the conventions in [CODEDNA.md](CODEDNA.md): naming, formatting, comment voice, structure, and idioms, so new code is indistinguishable from existing code. Before finishing, self-check against the "AI tells" section of that file.
<!-- codedna:end -->
```
When creating a Cursor rule, prepend:
```
---
description: Apply the codedna style profile for this repository.
alwaysApply: true
---
```
When creating a Windsurf/Cascade rule, prepend:
```
---
trigger: always_on
---
```
Tell the user which files you added or updated and that they can delete the codedna block or rule file. Do not silently rewrite unrelated parts of any agent instruction file.

**8. Report.** Summarize the headline conventions, anything surprising, and where the codebase is inconsistent enough that "matching" means picking the locally-dominant choice per file.

---

## Mode: Match

1. Load the repo's `CODEDNA.md` (run Map first if absent).
2. Read two or three real files next to where your code will live. The profile is the general law; neighbors are the local dialect, and local wins on conflicts.
3. Write the code following the profile: naming, comment density and voice, structure, error-handling posture, idioms. Reuse existing helpers and vocabulary instead of inventing parallel ones.
4. Before presenting, self-check against [AI tells](#ai-tells). Run the formatter if the repo has one.

The bar: if the author scrolled past your code in review, would anything make them think "I did not write this"? Remove it.

---

## Mode: Check

1. Load `CODEDNA.md`. Identify the code under review: named file, pasted text, `git diff --staged`, or `git diff`. If the user does not specify a target and the repo has a diff, default to the diff because pre-commit review is where Check mode is most useful.
2. Check profile freshness. If the generated date in `CODEDNA.md` predates significant style churn in recent commits, say so and recommend re-running Map before relying on fine-grained tells.
3. Compare against the profile and [AI tells](#ai-tells), category by category.
4. Report findings grouped by category. For each: quote the snippet, name the deviation, rate it (high = clearly flags a different author; low = minor), and give a concrete rewrite in house style. End with the top three giveaways and whether it would pass as the author's own work. Do not flag correct code that already matches; a false tell is as unhelpful as a missed one.

---

## What to look for

For every dimension: find the dominant pattern, capture a real example, note the characteristic exceptions. Skip what does not apply.

- **Naming** (highest signal, unenforced). Casing per kind (functions, methods, types/classes, constants, variables, files, CSS classes). Word choice: terse or descriptive, abbreviations (`cfg`, `ctx`) or full words, length. Verb dialect (`get` vs `fetch` vs `load`, stay consistent with theirs). Booleans (`is`/`has`/`should` prefix). Collections (plural?). Privates (leading `_`? `#`?). Event handlers (`onClick` vs `handleClick`).
- **Comments and docs** (high signal, unenforced). Density. The *why* (intent, gotchas) or the *what* (narration). Register: terse fragments or full sentences, lowercase or capitalized, impersonal or first-person. Doc comments (JSDoc/docstrings on everything, or only public API; which format). Markers (`TODO`/`FIXME`). Banners and dividers (present, or absent so contributions do not add them).
- **Structure.** Function size. Eager extraction or inline-heavy; where helpers live. File organization and ordering. Module shape (flat or nested, barrel files, feature vs layer folders). Paradigm (OO, functional, procedural; composition vs inheritance).
- **Control flow.** Early returns or nested conditionals. Ternary tolerance. Loops vs higher-order functions. `switch` vs lookup maps. Async style (`async`/`await` vs `.then`; `Promise.all`).
- **Error handling** (strong fingerprint, common AI tell). try/catch vs error-return vs Result vs let-it-throw. How defensive (validate at boundaries only, or everywhere). Custom error types or generic throws; message tone. Logging on error.
- **Types.** Explicit return types or inferred. `interface` vs `type`. `any`/`unknown` tolerance, non-null assertions. Generics naming. Enums vs union literals. Nullability conventions.
- **Imports.** Default vs named. Ordering and grouping (often enforced, check configs first). Relative vs alias paths. Barrel re-exports.
- **Tests.** Framework. Location and naming (`*.test.ts` co-located vs `tests/`). `describe`/`it` vs flat. Case naming ("returns null when empty" vs `test_x_y`). Mocking and fixtures.
- **Idioms and vocabulary** (hardest to fake, most identifying). Reused helpers (a `cn()`, a custom assert) to reuse not reinvent. Characteristic patterns (the standard shape of a component/handler). Domain nouns and verbs, match them exactly. Accepted abbreviations. Logging style. Small tics (template literals vs concat, default params, guard-clause style).

### Config map

Read these first; they are enforced.

| Language | Config files | Mainly settles |
| --- | --- | --- |
| All | `.editorconfig` | indent, line endings, final newline |
| JS / TS | `.prettierrc*`, `.eslintrc*`, `eslint.config.*`, `biome.json`, `tsconfig.json` | quotes, semicolons, trailing commas, width, import rules, strictness |
| Python | `pyproject.toml` (`[tool.black]`, `[tool.ruff]`, `[tool.isort]`), `setup.cfg`, `.flake8` | line length, quotes, import order, lint |
| Go | gofmt/gofumpt (implicit), `.golangci.yml` | formatting fixed by gofmt; lint |
| Rust | `rustfmt.toml`, `clippy.toml` | formatting, clippy |
| Ruby | `.rubocop.yml` | layout, cops |
| Java / Kotlin | `checkstyle.xml`, `.ktlint`, spotless | layout, naming |
| C / C++ | `.clang-format`, `.clang-tidy` | brace style, column limit |
| C# | `.editorconfig` (Roslyn), `*.ruleset` | naming, layout |
| Swift | `.swiftformat`, `.swiftlint.yml` | formatting, lint |

Also check `package.json` scripts, `Makefile`, `.pre-commit-config.yaml`, and CI files for the actual format/lint commands; those belong in the profile.

---

## AI tells

AI defaults to maximally explicit, maximally defensive, uniformly consistent, and eager to explain. Real authors are selectively terse, selectively defensive, characteristically inconsistent, and sparing with explanation. Match the author, not the default.

**Quick self-check** before presenting code as the author's own:
- [ ] Comment density matches neighbors (not heavier); no comment narrates what the code plainly says.
- [ ] Names are the house length and dialect (not longer, not more "descriptive").
- [ ] No try/catch, null check, or validation the author would not write.
- [ ] No helper extracted that the author would inline (and vice versa).
- [ ] Comment voice matches (casing, punctuation, terseness, person).
- [ ] Reuses existing helpers and vocabulary; no parallel utilities.
- [ ] No section banners, decorative dividers, or emoji unless the repo uses them.
- [ ] No leftover scaffolding (example-usage blocks, debug logs, restated-prompt comments).
- [ ] Formatter has been run if the repo has one.

**The catalog** (during Check, for each: snippet, which tell, severity, rewrite):
1. **Over-commenting**: a comment above nearly every block. Delete those that restate the code.
2. **Narrating the obvious**: `// increment counter`. Remove; or improve the name.
3. **Names longer than the house norm**: `responseData`/`handleButtonClickEvent` where the author writes `res`/`onClick`. Rename to their length and dialect.
4. **Defensive boilerplate**: try/catch and null checks the author would not write. Match the codebase's actual defensiveness.
5. **Over-abstraction** (or under): a one-line helper, a factory/interface the repo does not warrant. Match the author's extraction threshold.
6. **Uniform consistency**: every rule applied perfectly. Match the local dialect of the file, including its quirks.
7. **Docstrings on everything**: boilerplate `@param`/`@returns` that restate the signature. Document what the author documents.
8. **Explainer voice**: "Now we iterate...", first-person-plural, full sentences in a terse repo. Match their register exactly.
9. **Section banners and dividers** unless the repo uses them. Remove.
10. **Emoji and decorative unicode** where the codebase has none. Remove.
11. **Restating the prompt or plan** in comments. Delete; the code is the artifact.
12. **Leftover scaffolding**: `if __name__ == "__main__"` demos, debug `print`/`console.log`, done TODOs. Remove.
13. **Parallel utilities and vocabulary drift**: a new `formatDate` when one exists; `fetch`/`load` used interchangeably. Reuse the helper; use the house term.
14. **Belt-and-suspenders typing**: explicit return types everywhere in an inferring repo, redundant casts. Match the typing posture.
15. **Verbose logging and error messages** in a repo that logs sparingly. Match the density and style of neighbors.

---

## CODEDNA.md template

Adapt: drop sections that do not apply, split by language in a polyglot repo, never pad with generic filler. Mark **enforced** vs **observed**. Pair conventions with real snippets.

```markdown
# CodeDNA: <repo or scope>

> Scope: <whole repo | path | language>. <If author-scoped: "Matched to <author>.">
> Generated by codedna v1.0.1 on <date>. Re-run after deliberate style changes.

## TL;DR
The ten rules that matter most for blending in, scannable and specific.

## Enforced by tooling
- Format: `<command>`   Lint: `<command>`
- <config file> sets: <indent, quotes, semicolons, width, import order, ...>

## Naming
- Functions/vars/types/constants/booleans/files: <casing + habit + real example>
- Verb dialect / accepted abbreviations / exceptions.

## Formatting (beyond enforced)
- Line length observed; blank-line habits; anything the formatter does not cover.

## Comments and documentation
- Density; why vs what; register; doc-comment norms; markers; banners.
- Example (verbatim from the repo).

## Structure and decomposition
- Function size; extraction threshold; file organization; module shape; paradigm.

## Control flow and error handling
- Control-flow habits; async style; error posture and defensiveness; custom errors; logging.
- Example (a real error-handling snippet).

## Types
- Return types; interface vs type; any tolerance; generics; nullability.

## Imports and modules
- Default vs named; ordering; relative vs alias.

## Tests
- Framework; location/naming; structure; case naming; mocking.

## Idioms and vocabulary
- Reused helpers; characteristic patterns; domain vocabulary; logging; small tics.

## Known inconsistencies
- Where the codebase disagrees with itself; match the local file, not a global rule.

## AI tells to avoid here
- The specific places this author is the opposite of the AI default.
```

---

## Stats helper

A best-effort, stdlib-only fingerprint. Run:

```sh
python3 "<skill-dir>/scripts/codedna_stats.py" <target-dir>
```

Resolve `<skill-dir>` to the directory containing this `SKILL.md`. If the host exposes a skill-directory environment variable, use that path. If `python3` is unavailable, try `python`. The helper grounds the profile in real frequencies; read the sampled source as well to capture voice. It reports when a language sample is capped, when oversized files are skipped, and when `lower` means single-word names compatible with both snake_case and camelCase.

## Keeping the profile fresh

`CODEDNA.md` is a snapshot. After a deliberate style shift (new linter, framework migration, a refactor that changes conventions), re-run Map to refresh it.
