"""
WikiHow Article Exporter
=========================
Converts parsed WikiHow article data to Markdown or JSON files.
"""

import json
import os
import re
from pathlib import Path

from wikihow.renderer import parse_article


def _sanitize_filename(name: str) -> str:
    """Convert an article title into a safe filename."""
    name = re.sub(r"[^\w\s-]", "", name)
    name = re.sub(r"\s+", "_", name.strip())
    return name


def to_markdown(title: str, article_data: dict, output_dir: str = ".") -> str:
    """
    Export an article as a clean Markdown file.

    Args:
        title: Article title
        article_data: Raw article data from api.get_article()
        output_dir: Directory to write the file

    Returns:
        Path to the written file
    """
    parsed = parse_article(article_data["html"])
    lines = []

    display_title = title.replace("-", " ")
    lines.append(f"# How to {display_title}\n")

    # Categories
    cats = article_data.get("categories", [])
    if cats:
        lines.append(f"*Categories: {', '.join(cats[:8])}*\n")

    # Introduction
    if parsed["intro"]:
        lines.append(f"## Introduction\n")
        lines.append(f"{parsed['intro']}\n")

    # Methods
    for i, method in enumerate(parsed["methods"], 1):
        method_title = method["title"] or f"Method {i}"
        lines.append(f"## {method_title}\n")

        for j, step in enumerate(method["steps"], 1):
            lines.append(f"{j}. {step}\n")

        lines.append("")  # Blank separator

    # Tips
    if parsed["tips"]:
        lines.append("## Tips\n")
        for tip in parsed["tips"]:
            lines.append(f"- 💡 {tip}")
        lines.append("")

    # Warnings
    if parsed["warnings"]:
        lines.append("## Warnings\n")
        for w in parsed["warnings"]:
            lines.append(f"- ⚠️ {w}")
        lines.append("")

    # Source
    lines.append(f"---\n*Source: https://www.wikihow.com/{title}*\n")

    content = "\n".join(lines)
    filename = _sanitize_filename(display_title) + ".md"
    filepath = Path(output_dir) / filename
    filepath.parent.mkdir(parents=True, exist_ok=True)

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)

    return str(filepath)


def to_json(title: str, article_data: dict, output_dir: str = ".") -> str:
    """
    Export an article as a structured JSON file.

    Args:
        title: Article title
        article_data: Raw article data from api.get_article()
        output_dir: Directory to write the file

    Returns:
        Path to the written file
    """
    parsed = parse_article(article_data["html"])
    display_title = title.replace("-", " ")

    export = {
        "title": f"How to {display_title}",
        "url": f"https://www.wikihow.com/{title}",
        "pageid": article_data.get("pageid"),
        "categories": article_data.get("categories", []),
        "introduction": parsed["intro"],
        "methods": parsed["methods"],
        "tips": parsed["tips"],
        "warnings": parsed["warnings"],
    }

    filename = _sanitize_filename(display_title) + ".json"
    filepath = Path(output_dir) / filename
    filepath.parent.mkdir(parents=True, exist_ok=True)

    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(export, f, indent=2, ensure_ascii=False)

    return str(filepath)
