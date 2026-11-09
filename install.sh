#!/usr/bin/env sh
# Install the `trainer` skill for a local agent CLI.
#
#   ./install.sh              → Claude Code, all projects   (~/.claude/skills)
#   ./install.sh --project    → Claude Code, this project   (./.claude/skills)
#   ./install.sh --codex      → Codex CLI, all projects     (~/.agents/skills)
#
# For claude.ai or ChatGPT there is nothing to install — see the README.

set -eu

src=$(cd "$(dirname "$0")" && pwd)
name=$(basename "$src")

case "${1:-}" in
  --project) dest="$(pwd)/.claude/skills" ;;
  --codex)   dest="$HOME/.agents/skills" ;;
  --help|-h) sed -n '2,9p' "$0" | sed 's/^# \{0,1\}//'; exit 0 ;;
  "")        dest="$HOME/.claude/skills" ;;
  *)         echo "unknown option: $1  (try --help)" >&2; exit 2 ;;
esac

if [ "$src" = "$dest/$name" ]; then
  echo "already installed at $dest/$name — nothing to do"
  exit 0
fi

mkdir -p "$dest"
rm -rf "$dest/$name"
cp -R "$src" "$dest/$name"
rm -rf "$dest/$name/.git" "$dest/$name/install.sh" "$dest/$name/Makefile"

printf 'installed %s → %s/%s\n\n' "$name" "$dest" "$name"
echo "Restart your agent (or run /reload-skills), then ask:"
echo '  "build me a training program"   or   "/trainer"'

# Optional dependencies, reported rather than installed — the skill degrades
# gracefully without them and says so.
missing=""
python3 -c "import reportlab" 2>/dev/null || missing="$missing reportlab"
python3 -c "import openpyxl"  2>/dev/null || missing="$missing openpyxl"
if [ -n "$missing" ]; then
  printf '\nOptional, for PDF and Excel output:\n  pip install%s\n' "$missing"
  echo "(The mobile HTML plan and the validator work without them.)"
fi
