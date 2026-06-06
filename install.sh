#!/usr/bin/env sh
# Install the codedna skill into your Claude Code skills directory.
#
# Usage:
#   ./install.sh
#
# Override the destination with CLAUDE_SKILLS_DIR:
#   CLAUDE_SKILLS_DIR=/path/to/skills ./install.sh

set -e

SRC_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
DEST="${CLAUDE_SKILLS_DIR:-$HOME/.claude/skills}"

mkdir -p "$DEST"
cp "$SRC_DIR/codedna.md" "$DEST/codedna.md"

echo "Installed codedna to $DEST/codedna.md"
echo "Start a new Claude Code session to pick it up."
