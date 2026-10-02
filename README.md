# ClawHub Skill Pack

Agent skills for the OpenClaw ecosystem — evidence-tiered review, strategic reading, signal capture, reflection weaving, and citation provenance.

## Skills

| Skill | Description |
|-------|-------------|
| [reflection-weaver](reflection-weaver/) | Preserve reflections as voice-bearing writing while extracting stable concepts and weaving backlinks |
| [signal-detector](signal-detector/) | Scoped, authorized capture of original thinking and notable entity facts |
| [strategic-reading](strategic-reading/) | Read a source through the lens of a specific problem — applied playbook, not summary |
| [quality-review](quality-review/) | Evidence-first structured review with source-tiered claims — for code, notes, and research |
| [citation-fixer](citation-fixer/) | Audit and fix provenance in knowledge base notes — every fact gets a source |

## Manual installation in OpenClaw

Choose the **configured workspace of the intended agent**, not the OpenClaw
program checkout. This pack supports OpenClaw's grouped workspace discovery
under `<workspace>/skills/`. It does not install plugins, hooks, dependencies,
or change host configuration. Installing signal-detector grants no capture
permission; its explicit conversation/destination contract still applies.

Clone a revision you have reviewed, then run from the pack checkout:

```sh
git clone https://github.com/jjjhenriksen/agent-skills.git
cd agent-skills
git rev-parse HEAD
sh scripts/install-manual.sh "/absolute/path/to/chosen-workspace"
```

The source is each of the five individual folders in this repository. The
helper copies their entire contents, including references and scripts, into
one new folder. It refuses an existing pack destination instead of merging or
overwriting it. No other skill folders are copied or removed.

```text
<workspace>/skills/jjjhenriksen-pack/
  reflection-weaver/SKILL.md
  signal-detector/SKILL.md
  signal-detector/references/capture-examples.md
  strategic-reading/SKILL.md
  quality-review/SKILL.md
  citation-fixer/SKILL.md
```

Do not put a `SKILL.md` directly in `jjjhenriksen-pack/`: discovery stops at a
skill and would hide the five nested folders. If copying fails, inspect the
partial folder and move it outside skill roots before retrying. There is no
automatic cleanup or update of existing installations.

## Verify discovery

With the intended OpenClaw agent selected (add `--agent <id>` for a nondefault
agent), run:

```sh
openclaw skills list --json
openclaw skills info signal-detector --json
openclaw skills check --json
```

Check all five names in the list, and use `skills info <name> --json` for each
to confirm its file path resolves to the chosen workspace's pack folder.
An identical name elsewhere may win by precedence; a listing alone does not
prove this copy was selected. Readiness and agent visibility/allowlists are
separate from presence. Start a new agent session after installing to receive
the refreshed skill list; a Gateway restart is unnecessary.

Local bundle checks and isolated copy/collision tests use Python 3.10+:

```sh
python3 -m pip install PyYAML==6.0.3 markdown-it-py==3.0.0
python3 scripts/check_bundles.py
python3 -m unittest discover -s tests -v
```

## Remove or update this copy

Inspect `skills info` to identify the actual installed copy first. Move only
`<workspace>/skills/jjjhenriksen-pack` to a **new backup path outside all
OpenClaw skill roots**. Preserve that backup, including local edits. Do not
remove `<workspace>/skills`, another pack, or a different winning copy.

```sh
# Set these to the verified installed folder and a new backup destination.
pack_path="/absolute/path/to/chosen-workspace/skills/jjjhenriksen-pack"
backup_path="/absolute/path/outside-skill-roots/pack-backup"
test ! -e "$backup_path" && test ! -L "$backup_path" && mv "$pack_path" "$backup_path"
```

Repeat discovery and inspect paths: a lower-precedence copy may now appear.
For an update, review/diff the backup against the new revision, install into
the now-absent pack folder, and explicitly reapply desired local edits.

OpenClaw does not discover Codex's native `$CODEX_HOME/skills` directory.
These instructions target OpenClaw workspace skills; they do not claim that
copying the repository into a Codex root installs the five skills there.

## Author

Published by [jjjhenriksen](https://github.com/jjjhenriksen).
