#!/usr/bin/env sh
# Install the codedna skill into supported coding-agent skill directories.
#
# Usage:
#   ./install.sh [all|claude|codex|windsurf]
#
# Override destinations with:
#   CLAUDE_SKILLS_DIR=/path/to/skills ./install.sh
#   CODEX_SKILLS_DIR=/path/to/skills ./install.sh
#   WINDSURF_SKILLS_DIR=/path/to/skills ./install.sh

set -eu

SRC_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
VERSION=$(awk '/^Version: / { print $2; exit }' "$SRC_DIR/skill/SKILL.md")
TARGET="${1:-all}"

install_skill() {
  label=$1
  dest=$2
  stale_file=$3
  skill_dest="$dest/codedna"

  mkdir -p "$skill_dest/scripts"
  cp "$SRC_DIR/skill/SKILL.md" "$skill_dest/SKILL.md"
  cp "$SRC_DIR/skill/scripts/codedna_stats.py" "$skill_dest/scripts/codedna_stats.py"
  chmod +x "$skill_dest/scripts/codedna_stats.py"

  if [ -n "$stale_file" ] && [ -f "$stale_file" ]; then
    rm -f "$stale_file"
    echo "Removed stale bare-file install at $stale_file"
  fi

  echo "Installed codedna v$VERSION for $label to $skill_dest"
}

usage() {
  echo "Usage: ./install.sh [all|claude|codex|windsurf]" >&2
}

case "$TARGET" in
  all)
    claude_dest="${CLAUDE_SKILLS_DIR:-$HOME/.claude/skills}"
    codex_dest="${CODEX_SKILLS_DIR:-${CODEX_HOME:-$HOME/.codex}/skills}"
    windsurf_dest="${WINDSURF_SKILLS_DIR:-$HOME/.codeium/windsurf/skills}"
    install_skill "Claude Code" "$claude_dest" "$claude_dest/codedna.md"
    install_skill "Codex" "$codex_dest" "$codex_dest/codedna.md"
    install_skill "Windsurf/Cascade" "$windsurf_dest" ""
    ;;
  claude)
    claude_dest="${CLAUDE_SKILLS_DIR:-$HOME/.claude/skills}"
    install_skill "Claude Code" "$claude_dest" "$claude_dest/codedna.md"
    ;;
  codex)
    codex_dest="${CODEX_SKILLS_DIR:-${CODEX_HOME:-$HOME/.codex}/skills}"
    install_skill "Codex" "$codex_dest" "$codex_dest/codedna.md"
    ;;
  windsurf | cascade)
    windsurf_dest="${WINDSURF_SKILLS_DIR:-$HOME/.codeium/windsurf/skills}"
    install_skill "Windsurf/Cascade" "$windsurf_dest" ""
    ;;
  *)
    usage
    exit 2
    ;;
esac

echo "Restart the target coding agent to pick it up."
