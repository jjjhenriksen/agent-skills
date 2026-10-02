#!/usr/bin/env python3
"""Read-only syntax audit. Source existence/support and uncited claims need review."""
import argparse
import csv
from datetime import date
import json
from pathlib import Path
import re
from urllib.parse import urlsplit

FIELDS = {"user": 3, "web": 4, "paper": 4, "conversation": 4, "synthesis": 2, "ai": 3}


def validate(citation: str) -> list[str]:
    if not citation.startswith("[Source: ") or not citation.endswith("]"):
        return ["Expected [Source: ...]"]
    payload = citation[9:-1]
    if any(char in payload for char in "[]\r\n"):
        return ["Fields cannot contain square brackets or newlines"]
    try:
        fields = next(csv.reader([payload], skipinitialspace=True, strict=True))
    except csv.Error as error:
        return [f"Malformed comma-separated fields: {error}"]
    fields = [field.strip() for field in fields]
    kind = fields[0] if fields else ""
    if kind not in FIELDS:
        return ["Legacy/ambiguous or unknown source type; review evidence before converting"]
    if len(fields) != FIELDS[kind] or any(not field for field in fields):
        return [f"{kind} requires {FIELDS[kind] - 1} nonempty provenance fields"]
    errors = []
    if kind in {"user", "web", "conversation", "ai"}:
        try:
            if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", fields[-1]):
                raise ValueError()
            date.fromisoformat(fields[-1])
        except ValueError:
            errors.append("Expected a real YYYY-MM-DD date")
    elif kind == "paper":
        if not re.fullmatch(r"[0-9]{4}", fields[-1]) or int(fields[-1]) == 0:
            errors.append("Expected a publication year YYYY from 0001 through 9999")
    elif kind == "synthesis":
        prefix = "compiled from "
        if not fields[1].startswith(prefix):
            errors.append("Expected compiled from followed by semicolon-separated source slugs/IDs")
        else:
            sources = [source.strip() for source in fields[1][len(prefix):].split(";")]
            if not sources or any(not source for source in sources):
                errors.append("Synthesis must contain one or more nonempty source slugs/IDs")
    if kind == "web":
        try:
            url = urlsplit(fields[2])
            if url.scheme not in {"http", "https"} or not url.hostname or url.username or url.password:
                raise ValueError()
            url.port  # Reject malformed port numbers as well.
            if any(char.isspace() for char in fields[2]):
                raise ValueError()
        except ValueError:
            errors.append("Expected an HTTP(S) URL without embedded credentials")
    return errors


def audit(path: Path) -> list[dict]:
    findings = []
    for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        for match in re.finditer(r"\[Source:[^\]\n]*(?:\]|$)", line):
            errors = validate(match.group())
            findings.append({"path": str(path), "line": number, "column": match.start() + 1,
                             "valid_syntax": not errors, "issues": errors})
    return findings


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("notes", type=Path, nargs="+")
    args = parser.parse_args()
    results = [finding for path in args.notes for finding in audit(path)]
    print(json.dumps({"scope": "syntax only; uncited claims and source support not verified",
                      "citations": results}, indent=2))
    raise SystemExit(1 if any(not item["valid_syntax"] for item in results) else 0)
