#!/usr/bin/env sh
# Install the codedna skill into supported coding-agent skill directories.
#
# Usage:
#   ./install.sh <all|claude|codex|cursor|windsurf>
#
# Override destinations with:
#   CLAUDE_SKILLS_DIR=/path/to/skills ./install.sh claude
#   CODEX_SKILLS_DIR=/path/to/skills ./install.sh codex
#   CURSOR_SKILLS_DIR=/path/to/skills ./install.sh cursor
#   WINDSURF_SKILLS_DIR=/path/to/skills ./install.sh windsurf

set -eu

unset CDPATH
SRC_DIR=$(cd -- "$(dirname -- "$0")" && pwd)
VERSION=$(awk '/^Version: / { print $2; exit }' "$SRC_DIR/skill/SKILL.md")
TARGET="${1:-}"

install_skill() {
  label=$1
  dest=$2
  stale_file=$3
  skill_dest="$dest/codedna"

  mkdir -p "$skill_dest/scripts"
  cp "$SRC_DIR/skill/SKILL.md" "$skill_dest/SKILL.md"
  cp "$SRC_DIR"/skill/scripts/*.py "$skill_dest/scripts/"
  chmod +x "$skill_dest"/scripts/*.py

  if [ -n "$stale_file" ] && [ -f "$dest/$stale_file" ]; then
    rm -f "$dest/$stale_file"
    echo "Removed stale bare-file install at $dest/$stale_file"
  fi

  echo "Installed codedna v$VERSION for $label to $skill_dest"
}

install_claude() {
  install_skill "Claude Code" "${CLAUDE_SKILLS_DIR:-$HOME/.claude/skills}" codedna.md
}

install_codex() {
  install_skill "Codex" "${CODEX_SKILLS_DIR:-${CODEX_HOME:-$HOME/.codex}/skills}" codedna.md
}

install_cursor() {
  install_skill "Cursor" "${CURSOR_SKILLS_DIR:-$HOME/.cursor/skills}" ""
}

install_windsurf() {
  install_skill "Windsurf/Cascade" "${WINDSURF_SKILLS_DIR:-$HOME/.codeium/windsurf/skills}" ""
}

usage() {
  echo "Usage: ./install.sh <all|claude|codex|cursor|windsurf>" >&2
  echo "" >&2
  echo "Targets:" >&2
  echo "  all       Install for Claude Code, Codex, Cursor, and Windsurf/Cascade" >&2
  echo "  claude    Install for Claude Code" >&2
  echo "  codex     Install for Codex" >&2
  echo "  cursor    Install for Cursor" >&2
  echo "  windsurf  Install for Windsurf/Cascade" >&2
}

case "$TARGET" in
  "")
    usage
    exit 0
    ;;
  all)
    install_claude
    install_codex
    install_cursor
    install_windsurf
    ;;
  claude)
    install_claude
    ;;
  codex)
    install_codex
    ;;
  cursor)
    install_cursor
    ;;
  windsurf | cascade)
    install_windsurf
    ;;
  *)
    usage
    exit 2
    ;;
esac

echo "Restart the target coding agent to pick it up."
