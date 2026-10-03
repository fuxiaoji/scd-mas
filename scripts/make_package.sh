#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
NAME="${1:?usage: scripts/make_package.sh <name>}"
DOCDIR="${2:-packages/stage1a}"
STAGE="$(mktemp -d)"; DEST="$STAGE/$NAME"; mkdir -p "$DEST"
cd "$ROOT"
for f in AGENT.md HAVEDO.md TODO.md budget_stage1a.yaml; do [ -f "$f" ] && cp "$f" "$DEST"/; done
for d in stage2b stage0 data results cases plots prompts configs scripts tests raw runs/stage1a audits sources; do
  [ -d "$d" ] && cp -r "$d" "$DEST"/
done
for f in "$DOCDIR"/*.md; do [ -f "$f" ] && cp "$f" "$DEST"/; done
{ echo "HEAD: $(git rev-parse HEAD)"; git log --pretty=format:'%h %ad %s' --date=iso; } > "$DEST/git_log.txt"
( cd "$DEST" && find . -type f ! -name SHA256SUMS.txt ! -name PACKAGE_MANIFEST.md | sort | xargs sha256sum > SHA256SUMS.txt
  { echo "# PACKAGE_MANIFEST — $NAME"; echo "files: $(find . -type f | wc -l | tr -d ' ')"; } > PACKAGE_MANIFEST.md )
mkdir -p "$ROOT/packages"; rm -f "$ROOT/packages/$NAME.zip"
( cd "$STAGE" && zip -qr "$ROOT/packages/$NAME.zip" "$NAME" )
unzip -t "$ROOT/packages/$NAME.zip" > /dev/null && echo "integrity: OK"
echo "path: $ROOT/packages/$NAME.zip"
