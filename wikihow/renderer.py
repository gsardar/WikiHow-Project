"""
WikiHow Article Renderer
=========================
Parses WikiHow article HTML and renders it beautifully in the terminal
using the Rich library.
"""

import re
import textwrap
from bs4 import BeautifulSoup, NavigableString, Tag
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.markdown import Markdown
from rich.rule import Rule
from rich.columns import Columns
from rich import box


console = Console()


# ── HTML → Structured Data ────────────────────────────────────────────────────

def _clean_text(text: str) -> str:
    """Collapse whitespace and strip."""
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def _extract_step_text(step_el) -> str:
    """Extract the text content of a step, stripping images and sub-elements we don't need."""
    # The main step text is usually inside a <div class="step"> or <b class="whb">
    bold = step_el.find("b", class_="whb")
    rest_parts = []

    if bold:
        rest_parts.append(bold.get_text())

    # Get remaining text after the bold summary
    for child in step_el.children:
        if isinstance(child, Tag):
            if child.name == "b" and "whb" in (child.get("class") or []):
                continue
            if child.name in ("script", "noscript", "style", "img"):
                continue
            rest_parts.append(child.get_text())
        elif isinstance(child, NavigableString):
            rest_parts.append(str(child))

    return _clean_text(" ".join(rest_parts))


def parse_article(html: str) -> dict:
    """
    Parse WikiHow article HTML into structured data.

    Returns:
        {
            "intro": str,
            "methods": [
                {
                    "title": str,
                    "steps": [str, ...],
                }
            ],
            "tips": [str, ...],
            "warnings": [str, ...],
        }
    """
    soup = BeautifulSoup(html, "html.parser")

    result = {
        "intro": "",
        "methods": [],
        "tips": [],
        "warnings": [],
    }

    # ── Introduction ──
    intro_div = soup.find("div", class_="mf-section-0")
    if intro_div:
        intro_p = intro_div.find("p")
        if intro_p:
            result["intro"] = _clean_text(intro_p.get_text())
    else:
        # Fallback: first <p> in the article
        first_p = soup.find("p")
        if first_p:
            result["intro"] = _clean_text(first_p.get_text())

    # ── Methods / Steps ──
    # WikiHow uses <div class="steps"> wrapping each method
    methods_divs = soup.find_all("div", class_="steps")
    for method_div in methods_divs:
        method_title = ""
        # The method headline is usually a preceding <span class="mw-headline">
        headline = method_div.find_previous("span", class_="mw-headline")
        if headline:
            method_title = _clean_text(headline.get_text())

        steps = []
        step_elements = method_div.find_all("div", class_="step")
        if not step_elements:
            # Fallback: look for <li> inside ordered lists
            step_elements = method_div.find_all("li")

        for step_el in step_elements:
            text = _extract_step_text(step_el)
            if text:
                steps.append(text)

        if steps:
            result["methods"].append({
                "title": method_title,
                "steps": steps,
            })

    # If no methods found, try a flat approach — just grab all ordered list items
    if not result["methods"]:
        all_ols = soup.find_all("ol")
        flat_steps = []
        for ol in all_ols:
            for li in ol.find_all("li", recursive=False):
                text = _clean_text(li.get_text())
                if text and len(text) > 10:
                    flat_steps.append(text)
        if flat_steps:
            result["methods"].append({
                "title": "Steps",
                "steps": flat_steps,
            })

    # ── Tips ──
    tips_div = soup.find("div", id="tips")
    if not tips_div:
        tips_div = soup.find("div", class_="tips")
    if tips_div:
        for li in tips_div.find_all("li"):
            text = _clean_text(li.get_text())
            if text:
                result["tips"].append(text)
    else:
        # Fallback: look for the tips section by header
        tips_header = soup.find("span", id="Tips")
        if tips_header:
            tips_ul = tips_header.find_parent().find_next_sibling("ul")
            if tips_ul:
                for li in tips_ul.find_all("li"):
                    text = _clean_text(li.get_text())
                    if text:
                        result["tips"].append(text)

    # ── Warnings ──
    warnings_div = soup.find("div", id="warnings")
    if not warnings_div:
        warnings_div = soup.find("div", class_="warnings")
    if warnings_div:
        for li in warnings_div.find_all("li"):
            text = _clean_text(li.get_text())
            if text:
                result["warnings"].append(text)
    else:
        warnings_header = soup.find("span", id="Warnings")
        if warnings_header:
            warn_ul = warnings_header.find_parent().find_next_sibling("ul")
            if warn_ul:
                for li in warn_ul.find_all("li"):
                    text = _clean_text(li.get_text())
                    if text:
                        result["warnings"].append(text)

    return result


# ── Terminal Rendering ────────────────────────────────────────────────────────

def render_article(title: str, article_data: dict, categories: list[str] | None = None):
    """
    Render a parsed article beautifully in the terminal.
    """
    parsed = parse_article(article_data["html"])

    # ── Title banner ──
    console.print()
    title_text = Text(f"  📖  How to {title.replace('-', ' ')}  ", style="bold white on dark_green")
    console.print(Panel(title_text, box=box.DOUBLE, border_style="green", expand=False))

    # ── Categories ──
    cats = categories or article_data.get("categories", [])
    if cats:
        cat_str = " · ".join(cats[:6])
        console.print(f"  [dim]Categories: {cat_str}[/dim]")

    # ── Introduction ──
    if parsed["intro"]:
        console.print()
        console.print(Panel(
            parsed["intro"],
            title="[bold cyan]Introduction[/bold cyan]",
            border_style="cyan",
            padding=(1, 2),
        ))

    # ── Methods ──
    for i, method in enumerate(parsed["methods"], 1):
        console.print()
        method_title = method["title"] or f"Method {i}"
        console.print(Rule(f"[bold yellow]» {method_title}[/bold yellow]", style="yellow"))
        console.print()

        for j, step in enumerate(method["steps"], 1):
            # Separate bold summary from detail if present
            # WikiHow steps often start with a bold sentence followed by detail
            step_text = textwrap.fill(step, width=90)
            console.print(f"  [bold green]{j}.[/bold green] {step_text}")
            console.print()

    # ── Tips ──
    if parsed["tips"]:
        console.print()
        tips_text = "\n".join(f"  💡 {tip}" for tip in parsed["tips"])
        console.print(Panel(
            tips_text,
            title="[bold green]Tips[/bold green]",
            border_style="green",
            padding=(1, 2),
        ))

    # ── Warnings ──
    if parsed["warnings"]:
        console.print()
        warnings_text = "\n".join(f"  ⚠️  {w}" for w in parsed["warnings"])
        console.print(Panel(
            warnings_text,
            title="[bold red]Warnings[/bold red]",
            border_style="red",
            padding=(1, 2),
        ))

    console.print()
    console.print(f"  [dim]Source: https://www.wikihow.com/{title}[/dim]")
    console.print()


def render_search_results(results: list[dict], query: str):
    """
    Render search results as a clean numbered list.
    """
    console.print()
    console.print(Panel(
        f"[bold]Search results for:[/bold] [cyan]{query}[/cyan]  ({len(results)} found)",
        box=box.ROUNDED,
        border_style="blue",
        expand=False,
    ))
    console.print()

    for i, r in enumerate(results, 1):
        title = r.get("title", "Untitled")
        # Clean snippet HTML
        snippet_raw = r.get("snippet", "")
        snippet = BeautifulSoup(snippet_raw, "html.parser").get_text()
        snippet = _clean_text(snippet)
        if len(snippet) > 120:
            snippet = snippet[:117] + "..."

        slug = title.replace(" ", "-")
        console.print(f"  [bold green]{i:>2}.[/bold green]  [bold]{title}[/bold]")
        console.print(f"       [dim]{snippet}[/dim]")
        console.print(f"       [dim italic]wikihow.com/{slug}[/dim italic]")
        console.print()


def render_preview(title: str, article_data: dict):
    """Render a short preview of an article — intro + first method steps only."""
    parsed = parse_article(article_data["html"])

    console.print()
    console.print(f"  [bold green]📖  {title.replace('-', ' ')}[/bold green]")
    console.print()

    if parsed["intro"]:
        intro = parsed["intro"]
        if len(intro) > 300:
            intro = intro[:297] + "..."
        console.print(f"  {intro}")
        console.print()

    if parsed["methods"]:
        first = parsed["methods"][0]
        console.print(f"  [yellow]» {first['title'] or 'Steps'}[/yellow]")
        for j, step in enumerate(first["steps"][:3], 1):
            step_short = step if len(step) < 100 else step[:97] + "..."
            console.print(f"    [green]{j}.[/green] {step_short}")
        remaining = len(first["steps"]) - 3
        if remaining > 0:
            console.print(f"    [dim]... and {remaining} more steps[/dim]")
    console.print()
