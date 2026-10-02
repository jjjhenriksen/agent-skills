---
name: citation-fixer
description: "Audit and fix provenance in knowledge base notes using type-specific source fields. Flag unsupported claims without inventing their provenance."
tags: [provenance, citation, audit, knowledge-management, quality]
---

# Citation Fixer

Provenance audit for knowledge base notes. Check the authorized notes against
the type-specific contract below, then draft repairs backed by actual sources.

## Contract

- Scan the notes in the user's authorized audit scope
- Missing citations flagged with specific location and suggested fix
- Malformed citations fixed to the standard format
- Results reported with counts (scanned, fixed, remaining gaps)
- Read-only by default: draft fix suggestions unless the user approves batch apply
- Never fabricate a citation for an uncited claim — flag it

## Citation Standard

Use an explicit source type and the required fields for that type. Fields are
comma-separated; quote a field containing a comma, and escape an embedded
double quote by doubling it. Fields cannot contain newlines or square brackets.

| Type | Canonical format | Required provenance |
|---|---|---|
| User | `[Source: user, {context}, YYYY-MM-DD]` | Nonempty context and date of statement |
| Web | `[Source: web, {publication}, {URL}, YYYY-MM-DD]` | Publication, HTTP(S) source URL, retrieval date |
| Paper | `[Source: paper, {authors}, "{title}", YYYY]` | Authors, title, publication year; a full date is not required |
| Conversation | `[Source: conversation, {participant}, {topic}, YYYY-MM-DD]` | Participant, topic, conversation date |
| Synthesis | `[Source: synthesis, compiled from {slug-a}; {slug-b}]` | One or more nonempty source slugs/IDs, separated by semicolons; no date required |
| AI | `[Source: ai, {model}, YYYY-MM-DD]` | Model identity and generation date |

Dates must be real calendar dates in the displayed format. Synthesis carries
lineage rather than a new source-event date: resolve every listed source in the
authorized knowledge base and check its own provenance. A syntactically valid
source list is insufficient if a source is missing or does not support the
claim. Likewise, valid web syntax does not prove that the page exists or that
it supports a claim. An AI citation labels model output, not an independent
source establishing its truth. Keep participant details within the authorized
audience; flag a privacy conflict instead of copying private identifiers.

Earlier web, paper, conversation, synthesis, and model examples omitted the
explicit type. Report these as **legacy/ambiguous format requiring review**,
not as a claim proven false or a missing date by default. Identify the source
from evidence before proposing a canonical replacement. Preserve the existing
citation if required information is unavailable; flag the gap instead of
guessing a date, author, model, or source type. Existing explicit user citations
already match the contract.

Read [citation-fixtures.json](references/citation-fixtures.json) for valid and
invalid examples of every type. The read-only helper
[validate_citations.py](scripts/validate_citations.py) checks **citation syntax**
in explicitly named Markdown files. It does not detect every factual claim,
verify source support, fetch URLs, or edit notes:

```sh
python3 {baseDir}/scripts/validate_citations.py /authorized/path/note.md
```

## Phases

1. **Scan.** Within the authorized scope, check factual claims for inline citations. The syntax helper is optional; review uncited claims separately.
2. **Identify issues:**
   - Facts without any citation
   - Required fields absent for the declared type (dates only where required; paper year and synthesis lineage have their own rules)
   - Invalid calendar dates, publication years, URLs, or empty synthesis entries
   - Legacy/ambiguous citations whose type cannot yet be established
   - Missing local sources, wrong slugs, unavailable web references, or sources that do not support the claim; distinguish unavailable verification from a confirmed broken source
3. **Draft fixes.** For each issue, show the current text and the proposed fix. Group by note.
4. **Report.** Count: notes scanned, citations found, issues fixed, remaining gaps. Surface as a queue item for user review.

## Output Format

```
Citation Audit — YYYY-MM-DD
────────────────────────────
Notes scanned:       X
Citations found:     X total (X valid, X issues)
Issues by type:
  Missing citation:     X
  Missing required field: X
  Legacy/ambiguous:      X
  Malformed format:     X
  Broken reference:     X
────────────────────────────
Top notes to fix: [paths]
```

## Anti-Patterns

- Fabricating a citation for an uncited claim — flag it as missing, don't invent
- Overwriting a claim citation without checking the source still exists
- Being too aggressive with ad-hoc conversational facts that don't need formal provenance (preference, opinion, speculation clearly marked as such)
- Running the full audit on the entire knowledge base without prioritizing — start with high-traffic pages
- Editing notes directly without the user's approval on the proposed changes
