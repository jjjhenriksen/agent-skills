---
name: signal-detector
description: "Always-on ambient signal capture. Detects original thinking and entity mentions in every inbound message and captures them without blocking the conversation."
tags: [capture, signal, knowledge-management, note-taking]
---

# Signal Detector

Always-on ambient capture that fires on every inbound message from the user to detect TWO things with equal priority:

1. **Original thinking** — ideas, observations, theses, frameworks, opinions. The user's language IS the insight.
2. **Entity mentions** — people, companies, projects, concepts, tools, sources worth tracking in a knowledge base.

This runs in parallel (spawned sub-agent or lightweight background pass), never blocks the main response.

## Contract

- Fires on every substantive message (exceptions for purely operational exchanges)
- Runs in parallel — never delays the user's reply
- Captures original thinking with the user's EXACT phrasing (no paraphrasing)
- Detects entity mentions and notes them for knowledge enrichment
- Logs a one-line summary of what was captured
- Every fact carries provenance: `[Source: user, context, YYYY-MM-DD]`

## Phases

### Phase 1: Idea/Observation Detection

When the user expresses a novel thought, observation, thesis, framework, or opinion:

- If it's **original thinking** they generated → draft a note in the originals directory or log to the daily note
- If it's a **world concept** they're referencing → check existing knowledge base for a concept note; update or queue creation
- If it's a **product, project, or career idea** → log to the relevant project index or career dashboard

**Capture exact phrasing.** The user's language IS the insight. Don't paraphrase. Don't smooth it out.

**Cross-link** every original to related people, projects, concepts, and sources.

### Phase 2: Entity Detection

1. Extract entity mentions (people, companies, projects, tools, sources)
2. For each entity:
   - Search knowledge base — does a note already exist?
   - If NO page → assess notability (will we reference this again? Is it relevant to the user's work/interests?)
   - If notable and missing → queue creation
   - If page exists but thin → queue update
   - If page exists and current → no action
3. For new facts with specific dates → add to entity's timeline section

### What counts as notable

- People the user interacts with or discusses (not random mentions)
- Companies, projects, and institutions relevant to the user's work or interests
- Concepts, frameworks, or tools the user references or creates
- The user's own original thinking — highest value, capture always
- Sources the user shares or recommends

### What to skip

- Pure pleasantries and greeting rituals
- Operational acknowledgements without new conceptual content
- Commands to agents without novel conceptual content
- Random background entities with no connection to the user's work

## Output Format

One-line capture log entry in the daily note:

```
[signal] Captured idea: "{exact phrasing}" → concept/source/note
[signal] Noted entity: {name} → entity page
```

## Anti-Patterns

- Paraphrasing or smoothing the user's language — keep the original voice
- Blocking the main conversation to finish capture — spawn or defer
- Creating knowledge pages for every passing mention — apply the notability gate
- Over-writing existing knowledge base material without checking what's there first
- Capturing purely operational exchanges as signal
