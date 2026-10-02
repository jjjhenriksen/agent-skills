#!/bin/sh
# Copy this pack into one new, grouped OpenClaw workspace skill directory.
set -eu
if [ "$#" -ne 1 ]; then
    echo 'Usage: sh scripts/install-manual.sh /absolute/OpenClaw-workspace' >&2
    exit 2
fi
case "$1" in
    /*) ;;
    *) echo 'Choose an absolute workspace path.' >&2; exit 2 ;;
esac
pack_source=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
pack_dest="$1/skills/jjjhenriksen-pack"
for skill in reflection-weaver signal-detector strategic-reading quality-review citation-fixer; do
    test -f "$pack_source/$skill/SKILL.md"
done
mkdir -p "$1/skills"
# An existing directory, file, or symlink fails here before any copying.
mkdir "$pack_dest"
for skill in reflection-weaver signal-detector strategic-reading quality-review citation-fixer; do
    cp -R "$pack_source/$skill" "$pack_dest/$skill"
done
printf 'Installed pack at %s\n' "$pack_dest"
