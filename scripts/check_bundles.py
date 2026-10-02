#!/usr/bin/env python3
"""Check loadable skill identity and packaged local Markdown references.

Structural checks only: this does not execute or prove an agent's behavior.
"""
from pathlib import Path
import re
import sys
from urllib.parse import unquote, urlsplit

import yaml


def check(root: Path) -> list[str]:
    errors = []
    skills = sorted(root.glob("*/SKILL.md"))
    if not skills:
        return ["No skill bundles found"]
    for skill in skills:
        content = skill.read_text(encoding="utf-8")
        parts = content.split("---", 2)
        try:
            if len(parts) != 3 or parts[0].strip():
                raise ValueError("missing YAML frontmatter")
            metadata = yaml.safe_load(parts[1])
            if not isinstance(metadata, dict):
                raise ValueError("frontmatter must be a mapping")
            name = metadata.get("name")
            if name != skill.parent.name or not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", name or ""):
                raise ValueError("name must match its folder and use lowercase hyphenated words")
            description = metadata.get("description")
            if not isinstance(description, str) or not description.strip():
                raise ValueError("description must be a nonempty string")
        except (ValueError, yaml.YAMLError) as error:
            errors.append(f"{skill.relative_to(root)}: {error}")
        for document in sorted(skill.parent.rglob("*.md")):
            for target in re.findall(r"\[[^\]\n]+\]\(([^)\s]+)\)", document.read_text(encoding="utf-8")):
                url = urlsplit(target)
                if url.scheme or url.netloc or not url.path:
                    continue
                path = (document.parent / unquote(url.path)).resolve()
                if not path.is_relative_to(root.resolve()) or not path.exists():
                    errors.append(f"{document.relative_to(root)}: missing/outside local reference {target}")
    return errors


if __name__ == "__main__":
    repository = Path(__file__).resolve().parents[1]
    failures = check(repository)
    for failure in failures:
        print(failure, file=sys.stderr)
    if failures:
        sys.exit(1)
    print("Skill identities and packaged local references checked; agent behavior not executed.")
