#!/usr/bin/env bash
# make_package.sh — scd-mas packaging (aove-mad AGENT.md §8.1 rule carried over)
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
NAME="${1:?usage: scripts_make_package.sh <name>}"
STAGE="$(mktemp -d)"
DEST="$STAGE/$NAME"
mkdir -p "$DEST"
cd "$ROOT"
# top-level docs -> package root
for f in docs/00_README.md docs/01_COLLISION_DECISION.md docs/02_CLOSEST_WORK_MATRIX.md \
         docs/03_SCD_FORMALIZATION.md docs/04_COMMIT_GATE_DESIGN_SPACE.md \
         docs/05_RISK_REGISTER.md repo_structure.md; do
  [ -f "$f" ] && cp "$f" "$DEST"/
done
# control + stage0 + audits + sources
for f in AGENT.md HAVEDO.md TODO.md; do [ -f "$f" ] && cp "$f" "$DEST"/; done
for d in stage0 audits sources memory docs; do
  [ -d "$d" ] && cp -r "$d" "$DEST"/
done
rm -rf "$DEST/audits/LITERATURE_AUDIT.md" 2>/dev/null || true
# git log + checksums + manifest
{ echo "# scd-mas git history at packaging time: $(date -u +%Y-%m-%dT%H:%M:%SZ)"; echo
  echo "HEAD: $(git rev-parse HEAD)"; echo
  git log --pretty=format:'%h %ad %s' --date=iso; } > "$DEST/git_log.txt"
( cd "$DEST" && find . -type f ! -name SHA256SUMS.txt ! -name PACKAGE_MANIFEST.md | sort | xargs sha256sum > SHA256SUMS.txt
  { echo "# PACKAGE_MANIFEST — $NAME"; echo
    echo "- built (UTC): $(date -u +%Y-%m-%dT%H:%M:%SZ)"
    echo "- files: $(find . -type f | wc -l | tr -d ' ')"
    echo; echo '```'; find . -type f | sort; echo '```'; } > PACKAGE_MANIFEST.md )
mkdir -p "$ROOT/packages"
rm -f "$ROOT/packages/$NAME.zip"
( cd "$STAGE" && zip -qr "$ROOT/packages/$NAME.zip" "$NAME" )
unzip -t "$ROOT/packages/$NAME.zip" > /dev/null && echo "integrity: OK"
echo "path: $ROOT/packages/$NAME.zip"
ls -la "$ROOT/packages/$NAME.zip"
rm -rf "$STAGE"
