"""
WikiHow CLI Interface
======================
Subcommand-based CLI built with argparse.

Commands:
    wikihow search <query>              — Search WikiHow articles
    wikihow read <title>                — Read an article in the terminal
    wikihow random                      — Read a random article
    wikihow export <title>              — Export article to Markdown or JSON
    wikihow browse <query>              — Interactive search → select → read
    wikihow categories [--prefix]       — List WikiHow categories
    wikihow contributors <title>        — Show article contributors + gender
    wikihow analyze <category>          — Bulk gender analysis of a category
    wikihow clear-cache                 — Clear the article cache
"""

import argparse
import csv
import sys
import io

from rich.console import Console
from rich.table import Table
from rich import box

from wikihow import __version__
from wikihow import api
from wikihow import cache
from wikihow import exporter
from wikihow.renderer import render_article, render_search_results


console = Console()


def _normalise_title(title: str) -> str:
    """Convert user-supplied title to URL-slug format (e.g. 'Tie a Tie' → 'Tie-a-Tie')."""
    return title.strip().replace(" ", "-")


def _fetch_article(title: str, no_cache: bool = False) -> dict:
    """Fetch an article, using cache unless bypassed."""
    slug = _normalise_title(title)
    cache_key = f"article:{slug}"

    if not no_cache:
        cached = cache.get(cache_key)
        if cached:
            return cached

    try:
        data = api.get_article(slug)
    except LookupError as e:
        console.print(f"\n  [bold red]✗[/bold red] {e}\n")
        sys.exit(1)
    except ConnectionError as e:
        console.print(f"\n  [bold red]✗ Network error:[/bold red] {e}\n")
        sys.exit(1)

    cache.put(cache_key, data)
    return data


# ── Reader Commands ───────────────────────────────────────────────────────────

def cmd_search(args):
    """Search WikiHow for articles matching a query."""
    query = " ".join(args.query)
    with console.status("[cyan]Searching WikiHow...[/cyan]"):
        try:
            results = api.search(query, limit=args.limit)
        except ConnectionError as e:
            console.print(f"\n  [bold red]✗ Network error:[/bold red] {e}\n")
            sys.exit(1)

    if not results:
        console.print(f"\n  [yellow]No results found for '{query}'[/yellow]\n")
        return

    render_search_results(results, query)


def cmd_read(args):
    """Fetch and render a WikiHow article."""
    title = " ".join(args.title)
    slug = _normalise_title(title)

    with console.status("[cyan]Fetching article...[/cyan]"):
        data = _fetch_article(title, no_cache=args.no_cache)

    render_article(data.get("title", slug), data)


def cmd_random(args):
    """Fetch and display a random WikiHow article."""
    with console.status("[cyan]Finding a random article...[/cyan]"):
        try:
            randoms = api.get_random(count=1)
        except ConnectionError as e:
            console.print(f"\n  [bold red]✗ Network error:[/bold red] {e}\n")
            sys.exit(1)

    if not randoms:
        console.print("\n  [red]Could not fetch a random article.[/red]\n")
        return

    title = randoms[0]["title"]
    slug = _normalise_title(title)
    console.print(f"\n  [dim]Rolling the dice... got:[/dim] [bold]{title}[/bold]")

    with console.status("[cyan]Fetching article...[/cyan]"):
        data = _fetch_article(slug, no_cache=True)

    render_article(data.get("title", slug), data)


def cmd_export(args):
    """Export a WikiHow article to Markdown or JSON."""
    title = " ".join(args.title)
    slug = _normalise_title(title)

    with console.status("[cyan]Fetching article...[/cyan]"):
        data = _fetch_article(title, no_cache=args.no_cache)

    fmt = args.format.lower()
    output_dir = args.output or "."

    if fmt == "md":
        path = exporter.to_markdown(slug, data, output_dir=output_dir)
    elif fmt == "json":
        path = exporter.to_json(slug, data, output_dir=output_dir)
    else:
        console.print(f"\n  [red]Unknown format: {fmt}. Use 'md' or 'json'.[/red]\n")
        sys.exit(1)

    console.print(f"\n  [bold green]✓[/bold green] Exported to [cyan]{path}[/cyan]\n")


def cmd_browse(args):
    """Interactive search → pick → read flow."""
    query = " ".join(args.query)

    with console.status("[cyan]Searching WikiHow...[/cyan]"):
        try:
            results = api.search(query, limit=args.limit)
        except ConnectionError as e:
            console.print(f"\n  [bold red]✗ Network error:[/bold red] {e}\n")
            sys.exit(1)

    if not results:
        console.print(f"\n  [yellow]No results found for '{query}'[/yellow]\n")
        return

    render_search_results(results, query)

    # Prompt user to pick
    console.print(f"  [bold]Enter a number (1-{len(results)}) to read, or 'q' to quit:[/bold]")
    try:
        choice = input("  > ").strip()
    except (EOFError, KeyboardInterrupt):
        console.print("\n  [dim]Bye![/dim]\n")
        return

    if choice.lower() in ("q", "quit", "exit", ""):
        console.print("  [dim]Bye![/dim]\n")
        return

    try:
        idx = int(choice) - 1
        if not (0 <= idx < len(results)):
            raise ValueError
    except ValueError:
        console.print(f"  [red]Invalid choice: {choice}[/red]\n")
        return

    selected = results[idx]
    slug = _normalise_title(selected["title"])

    with console.status("[cyan]Fetching article...[/cyan]"):
        data = _fetch_article(slug, no_cache=False)

    render_article(data.get("title", slug), data)


def cmd_clear_cache(args):
    """Clear the article cache."""
    cache.clear()
    console.print("\n  [bold green]✓[/bold green] Cache cleared.\n")


# ── Research Commands ─────────────────────────────────────────────────────────

def cmd_history(args):
    """
    Show the full edit history of an article in chronological order.
    Displays who edited, when, size change, and edit comment.
    """
    title = " ".join(args.title)
    slug = _normalise_title(title)
    limit = args.limit

    with console.status(f"[cyan]Fetching edit history for '{title}'...[/cyan]"):
        try:
            revisions = api.get_revisions(slug, limit=limit, oldest_first=True)
        except LookupError as e:
            console.print(f"\n  [bold red]✗[/bold red] {e}\n")
            sys.exit(1)
        except ConnectionError as e:
            console.print(f"\n  [bold red]✗ Network error:[/bold red] {e}\n")
            sys.exit(1)

    if not revisions:
        console.print(f"\n  [yellow]No revisions found for '{title}'[/yellow]\n")
        return

    # Resolve user genders
    registered_users = list({r["user"] for r in revisions if not r.get("anon")})
    user_info = {}
    use_profile_fallback = getattr(args, "profile_gender", False)
    if registered_users:
        with console.status("[cyan]Resolving user profiles...[/cyan]"):
            for i in range(0, len(registered_users), 50):
                batch = registered_users[i:i+50]
                try:
                    user_info.update(api.get_users(batch, fallback_to_profile=use_profile_fallback))
                except ConnectionError:
                    pass

    # Display
    console.print()
    from rich.panel import Panel
    console.print(Panel(
        f"[bold]Edit History:[/bold] {title.replace('-', ' ')}\n"
        f"[dim]Total revisions: {len(revisions)} · Oldest: {revisions[0].get('timestamp', '?')}[/dim]",
        border_style="magenta",
        expand=False,
    ))
    console.print()

    gender_style = {"male": "blue", "female": "magenta", "unknown": "dim", "anon": "dim italic"}

    table = Table(
        title=f"Revisions (chronological)",
        box=box.SIMPLE_HEAVY,
        border_style="cyan",
        show_lines=False,
        pad_edge=True,
    )
    table.add_column("#", width=5, style="dim")
    table.add_column("Date", width=20)
    table.add_column("User", max_width=20, style="bold")
    table.add_column("Gender", width=8, justify="center")
    table.add_column("Δ Size", width=10, justify="right")
    table.add_column("Edit Comment", max_width=60)

    prev_size = 0
    for i, rev in enumerate(revisions, 1):
        user = rev["user"]
        is_anon = rev.get("anon", False)
        size = rev.get("size", 0)
        delta = size - prev_size
        prev_size = size

        # Format delta
        if delta > 0:
            delta_str = f"[green]+{delta}[/green]"
        elif delta < 0:
            delta_str = f"[red]{delta}[/red]"
        else:
            delta_str = "[dim]0[/dim]"

        # Gender
        if is_anon:
            gender = "anon"
        else:
            gender = user_info.get(user, {}).get("gender", "unknown")
        gs = gender_style.get(gender, "dim")

        comment = rev.get("comment", "")
        if len(comment) > 60:
            comment = comment[:57] + "..."

        timestamp = rev.get("timestamp", "")[:16].replace("T", " ")

        table.add_row(
            str(i), timestamp, user,
            f"[{gs}]{gender}[/{gs}]",
            delta_str, comment
        )

    console.print(table)
    console.print()

    # Summary: user contribution counts
    user_edits = {}
    for rev in revisions:
        user = rev["user"]
        user_edits[user] = user_edits.get(user, 0) + 1

    top_editors = sorted(user_edits.items(), key=lambda x: x[1], reverse=True)[:15]
    console.print("  [bold]Top editors for this article:[/bold]")
    for user, count in top_editors:
        info = user_info.get(user, {})
        gender = info.get("gender", "anon" if any(r["user"] == user and r.get("anon") for r in revisions) else "unknown")
        gs = gender_style.get(gender, "dim")
        console.print(f"    {user:<25} [{gs}]{gender:<8}[/{gs}]  {count} edits")
    console.print()

    # CSV export
    if args.csv:
        with open(args.csv, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["revision_num", "timestamp", "user", "is_anon", "gender",
                             "size", "size_delta", "revid", "comment"])
            prev_size = 0
            for i, rev in enumerate(revisions, 1):
                user = rev["user"]
                is_anon = rev.get("anon", False)
                size = rev.get("size", 0)
                delta = size - prev_size
                prev_size = size
                gender = "anon" if is_anon else user_info.get(user, {}).get("gender", "unknown")
                writer.writerow([i, rev.get("timestamp", ""), user, is_anon, gender,
                                 size, delta, rev.get("revid", ""), rev.get("comment", "")])
        console.print(f"  [bold green]✓[/bold green] CSV saved to [cyan]{args.csv}[/cyan]\n")


def cmd_survey(args):
    """
    Bulk survey: for each article in a category, fetch full edit history,
    resolve user genders, and produce cross-article user aggregation.
    Outputs:
      1. Per-article revision table (CSV)
      2. User leaderboard across all articles
    """
    category = " ".join(args.category)
    art_limit = args.limit
    rev_limit = args.rev_limit

    # Step 1: Get articles in the category
    with console.status(f"[cyan]Fetching articles in '{category}'...[/cyan]"):
        try:
            articles = api.get_category_members(category, limit=art_limit)
        except ConnectionError as e:
            console.print(f"\n  [bold red]✗ Network error:[/bold red] {e}\n")
            sys.exit(1)

    if not articles:
        console.print(f"\n  [yellow]No articles found in '{category}'[/yellow]\n")
        return

    console.print(f"\n  [bold]Surveying {len(articles)} articles in [cyan]{category}[/cyan][/bold]")
    console.print(f"  [dim]Fetching up to {rev_limit} revisions per article (oldest first)...[/dim]\n")

    # Step 2: Collect all revisions
    all_revisions = []  # list of (article_title, revision_dict)
    all_users = set()

    for idx, article in enumerate(articles):
        title = article["title"]
        slug = _normalise_title(title)
        console.print(f"  [{idx+1}/{len(articles)}] {title}...", end=" ")

        try:
            revisions = api.get_revisions(slug, limit=rev_limit, oldest_first=True)
        except (LookupError, ConnectionError):
            console.print("[red]error[/red]")
            continue

        for rev in revisions:
            all_revisions.append((title, rev))
            if not rev.get("anon"):
                all_users.add(rev["user"])

        console.print(f"[green]{len(revisions)} revisions[/green]")

    console.print(f"\n  [dim]Total revisions collected: {len(all_revisions)}[/dim]")
    console.print(f"  [dim]Unique registered users: {len(all_users)}[/dim]")

    # Step 3: Batch-resolve user genders
    user_info = {}
    all_users_list = list(all_users)
    use_profile_fallback = getattr(args, "profile_gender", False)
    with console.status(f"[cyan]Resolving {len(all_users_list)} user profiles...[/cyan]"):
        for i in range(0, len(all_users_list), 50):
            batch = all_users_list[i:i+50]
            try:
                user_info.update(api.get_users(batch, fallback_to_profile=use_profile_fallback))
            except ConnectionError:
                pass

    # Step 4: Build user leaderboard
    user_stats = {}  # user → {edits, articles, gender}
    for art_title, rev in all_revisions:
        user = rev["user"]
        if user not in user_stats:
            is_anon = rev.get("anon", False)
            if is_anon:
                gender = "anon"
            else:
                gender = user_info.get(user, {}).get("gender", "unknown")
            user_stats[user] = {
                "edits": 0,
                "articles": set(),
                "gender": gender,
                "total_editcount": user_info.get(user, {}).get("editcount", 0),
                "registration": user_info.get(user, {}).get("registration", ""),
            }
        user_stats[user]["edits"] += 1
        user_stats[user]["articles"].add(art_title)

    # Display user leaderboard
    sorted_users = sorted(user_stats.items(), key=lambda x: x[1]["edits"], reverse=True)

    table = Table(
        title=f"User Leaderboard — {category} ({len(articles)} articles)",
        box=box.ROUNDED,
        border_style="magenta",
    )
    table.add_column("#", width=5, style="dim")
    table.add_column("User", style="bold", max_width=22)
    table.add_column("Gender", width=10, justify="center")
    table.add_column("Edits (this cat)", justify="right", style="cyan")
    table.add_column("Articles touched", justify="right", style="green")
    table.add_column("Total edits (site)", justify="right", style="dim")
    table.add_column("Registered", width=12, style="dim")

    gender_style = {"male": "blue", "female": "magenta", "unknown": "dim", "anon": "dim italic"}

    for i, (user, stats) in enumerate(sorted_users[:30], 1):
        gs = gender_style.get(stats["gender"], "dim")
        reg = (stats["registration"] or "")[:10]
        table.add_row(
            str(i), user,
            f"[{gs}]{stats['gender']}[/{gs}]",
            str(stats["edits"]),
            str(len(stats["articles"])),
            str(stats["total_editcount"]),
            reg,
        )

    console.print()
    console.print(table)

    # Aggregate gender stats
    gender_agg = {"male": 0, "female": 0, "unknown": 0, "anon": 0}
    for user, stats in user_stats.items():
        gender_agg[stats["gender"]] = gender_agg.get(stats["gender"], 0) + 1

    console.print(f"\n  [bold]═══ User Gender Distribution (unique users) ═══[/bold]")
    console.print(f"  [blue]Male: {gender_agg['male']}[/blue]  "
                   f"[magenta]Female: {gender_agg['female']}[/magenta]  "
                   f"[dim]Unknown: {gender_agg['unknown']}[/dim]  "
                   f"[dim]Anonymous: {gender_agg['anon']}[/dim]\n")

    # Step 5: CSV exports
    if args.csv:
        # Revisions CSV
        rev_path = args.csv
        with open(rev_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["category", "article", "revision_num", "timestamp",
                             "user", "is_anon", "gender", "size", "revid", "comment"])
            # Group by article for numbering
            current_art = None
            rev_num = 0
            for art_title, rev in all_revisions:
                if art_title != current_art:
                    current_art = art_title
                    rev_num = 0
                rev_num += 1
                user = rev["user"]
                is_anon = rev.get("anon", False)
                gender = "anon" if is_anon else user_info.get(user, {}).get("gender", "unknown")
                writer.writerow([
                    category, art_title, rev_num, rev.get("timestamp", ""),
                    user, is_anon, gender, rev.get("size", ""),
                    rev.get("revid", ""), rev.get("comment", ""),
                ])
        console.print(f"  [bold green]✓[/bold green] Revisions CSV: [cyan]{rev_path}[/cyan]")

        # Users CSV
        users_path = rev_path.replace(".csv", "_users.csv")
        with open(users_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["user", "gender", "edits_in_category", "articles_touched",
                             "total_editcount_site", "registration", "articles_list"])
            for user, stats in sorted_users:
                writer.writerow([
                    user, stats["gender"], stats["edits"],
                    len(stats["articles"]), stats["total_editcount"],
                    stats["registration"], "; ".join(sorted(stats["articles"])),
                ])
        console.print(f"  [bold green]✓[/bold green] Users CSV:     [cyan]{users_path}[/cyan]\n")


def cmd_diff(args):
    """
    Show the exact content difference between two revisions using the API.
    Bypasses WikiHow's login wall by generating a local HTML file containing
    the API-provided diff, styled similarly to MediaWiki, and opens it locally.
    """
    title = args.title
    slug = _normalise_title(title)
    rev_from = args.rev_from
    rev_to = args.rev_to

    with console.status(f"[cyan]Fetching diff for '{title}' (rev {rev_from} → {rev_to})...[/cyan]"):
        try:
            diff_data = api.get_revision_diff(rev_from, rev_to)
        except LookupError as e:
            console.print(f"\n  [bold red]✗[/bold red] {e}\n")
            sys.exit(1)
        except ConnectionError as e:
            console.print(f"\n  [bold red]✗ Network error:[/bold red] {e}\n")
            sys.exit(1)

    html_diff = diff_data.get("diff_html")
    if not html_diff:
        console.print(f"\n  [yellow]No differences found, or diff could not be generated.[/yellow]\n")
        return

    from_user = diff_data.get("from_user", "Unknown")
    to_user = diff_data.get("to_user", "Unknown")

    from_link = f'<a href="https://www.wikihow.com/User:{from_user}">{from_user}</a>' if from_user else "Unknown"
    to_link = f'<a href="https://www.wikihow.com/User:{to_user}">{to_user}</a>' if to_user else "Unknown"

    html_page = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <title>Diff: {title} ({rev_from} → {rev_to})</title>
        <style>
            body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; margin: 40px; background: #f8f9fa; color: #202122; }}
            .header-box {{ background: white; border: 1px solid #a2a9b1; padding: 20px; border-radius: 4px; margin-bottom: 20px; box-shadow: 0 1px 3px rgba(0,0,0,0.05); }}
            h2 {{ margin-top: 0; border-bottom: 1px solid #a2a9b1; padding-bottom: 5px; font-weight: normal; }}
            .meta {{ font-size: 1.1em; margin-top: 15px; display: flex; justify-content: space-between; }}
            a {{ color: #0645ad; text-decoration: none; }}
            a:hover {{ text-decoration: underline; }}
            
            table.diff {{ width: 100%; border-collapse: collapse; background: white; border: 1px solid #a2a9b1; border-spacing: 0; box-shadow: 0 1px 3px rgba(0,0,0,0.05); }}
            td {{ padding: 0.33em 0.5em; vertical-align: top; }}
            td.diff-marker {{ width: 2%; text-align: right; color: #72777d; font-weight: bold; font-family: monospace; border-right: 1px solid #eaecf0; }}
            td.diff-content {{ width: 48%; font-family: monospace; word-wrap: break-word; white-space: pre-wrap; }}
            
            .diff-context {{ background: #f8f9fa; color: #54595d; }}
            .diff-addedline {{ background: #ddffdd; border-color: #bbffbb; }}
            .diff-deletedline {{ background: #ffe4e1; border-color: #ffcccc; }}
            
            .diffchange {{ font-weight: bold; text-decoration: none; }}
            .diff-addedline .diffchange {{ background: #aaffaa; }}
            .diff-deletedline .diffchange {{ background: #ffaaaa; }}
            .diff-empty {{ background: #eaecf0; }}
        </style>
    </head>
    <body>
        <div class="header-box">
            <h2>Article Difference: <strong>{title}</strong></h2>
            <div class="meta">
                <div>From Revision <strong>{rev_from}</strong> by {from_link}</div>
                <div>To Revision <strong>{rev_to}</strong> by {to_link}</div>
            </div>
            <p style="color: #54595d; font-size: 0.9em; margin-bottom: 0;"><em>Note: WikiHow blocks web diffs for anonymous users. This is an offline reconstruction using the WikiHow API to bypass the login prompt. Click usernames to view their live WikiHow profiles.</em></p>
        </div>
        <table class="diff">
            <colgroup>
                <col class="diff-marker">
                <col class="diff-content">
                <col class="diff-marker">
                <col class="diff-content">
            </colgroup>
            <tbody>
            {html_diff}
            </tbody>
        </table>
    </body>
    </html>
    """

    import tempfile
    import webbrowser
    import os

    # Write to a temp file and open in browser
    fd, path = tempfile.mkstemp(suffix=".html", prefix="wikihow_diff_")
    with os.fdopen(fd, "w", encoding="utf-8") as f:
        f.write(html_page)

    console.print(f"\n  [bold green]✓[/bold green] Opening reconstructed diff in your browser: [cyan]{path}[/cyan]\n")
    webbrowser.open(f"file://{path}")


def cmd_bulk_diff(args):
    """
    Read a CSV generated by `survey` or `history`, filter by a regex pattern
    in the edit comments, fetch all matching diffs, and generate a combined HTML report.
    """
    import re
    from rich.progress import Progress

    csv_path = args.csv_file
    pattern = args.match

    try:
        regex = re.compile(pattern, re.IGNORECASE)
    except re.error as e:
        console.print(f"\n  [bold red]✗ Invalid regex pattern:[/bold red] {e}\n")
        sys.exit(1)

    with console.status(f"[cyan]Reading {csv_path}...[/cyan]"):
        try:
            with open(csv_path, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                rows = list(reader)
        except Exception as e:
            console.print(f"\n  [bold red]✗ Failed to read CSV:[/bold red] {e}\n")
            sys.exit(1)

    previous_revs = {}  # article -> revid
    matches = []  # list of dicts

    for row in rows:
        article = row.get("article", "Unknown Article")
        try:
            revid = int(row.get("revid", 0))
        except ValueError:
            revid = 0

        comment = row.get("comment", "")
        user = row.get("user", "")

        rev_from = previous_revs.get(article)
        if revid:
            previous_revs[article] = revid

        if not rev_from or not revid:
            continue

        if regex.search(comment):
            matches.append({
                "article": article,
                "rev_from": rev_from,
                "rev_to": revid,
                "user": user,
                "comment": comment
            })

    if not matches:
        console.print(f"\n  [yellow]No edits matched the pattern '{pattern}' in {csv_path}[/yellow]\n")
        return

    # Cap to avoid massive API abuse
    if len(matches) > args.limit:
        console.print(f"\n  [yellow]Found {len(matches)} matches, limiting to first {args.limit} to prevent API throttling.[/yellow]")
        console.print(f"  [dim]Use --limit to increase this maximum limit.[/dim]\n")
        matches = matches[:args.limit]
    else:
        console.print(f"\n  [bold green]Found {len(matches)} matching edits.[/bold green] Fetching diffs...\n")

    diff_results = []
    
    with Progress() as progress:
        task = progress.add_task("[cyan]Fetching API diffs...", total=len(matches))
        
        for m in matches:
            try:
                diff_data = api.get_revision_diff(m["rev_from"], m["rev_to"])
                diff_results.append({
                    "meta": m,
                    "html": diff_data.get("diff_html", "")
                })
            except (LookupError, ConnectionError):
                pass
            progress.advance(task)

    if not diff_results:
        console.print(f"\n  [red]Failed to fetch any diff HTML from the API.[/red]\n")
        return

    # Build unified HTML report
    html_blocks = []
    for res in diff_results:
        m = res["meta"]
        from_id, to_id = m["rev_from"], m["rev_to"]
        user_link = f'<a href="https://www.wikihow.com/User:{m["user"]}" target="_blank">{m["user"]}</a>' if m["user"] else "Unknown"
        
        block = f"""
        <div class="diff-block">
            <h3>{m['article']}</h3>
            <div class="meta">
                <div><strong>Revision {to_id}</strong> (diff from <a href="https://www.wikihow.com/index.php?oldid={from_id}" target="_blank">{from_id}</a>)</div>
                <div>Edited by {user_link}</div>
            </div>
            <div class="comment-box"><strong>Comment:</strong> <em>{m['comment']}</em></div>
            <table class="diff">
                <colgroup>
                    <col class="diff-marker"><col class="diff-content">
                    <col class="diff-marker"><col class="diff-content">
                </colgroup>
                <tbody>
                {res['html']}
                </tbody>
            </table>
        </div>
        """
        html_blocks.append(block)

    full_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <title>Bulk Diff Report: {pattern}</title>
        <style>
            body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; margin: 40px; background: #eaecf0; color: #202122; }}
            .page-title {{ text-align: center; margin-bottom: 40px; }}
            .diff-block {{ background: white; border: 1px solid #a2a9b1; padding: 20px; border-radius: 4px; margin-bottom: 40px; box-shadow: 0 1px 3px rgba(0,0,0,0.05); }}
            h3 {{ margin-top: 0; border-bottom: 1px solid #a2a9b1; padding-bottom: 5px; font-weight: bold; font-size: 1.4em; color: #000; }}
            .meta {{ font-size: 1.0em; margin-top: 15px; display: flex; justify-content: space-between; }}
            .comment-box {{ background: #f8f9fa; border-left: 4px solid #36c; padding: 10px 15px; margin: 15px 0; font-size: 1.05em; }}
            a {{ color: #0645ad; text-decoration: none; }}
            a:hover {{ text-decoration: underline; }}
            
            table.diff {{ width: 100%; border-collapse: collapse; background: white; border: 1px solid #a2a9b1; border-spacing: 0; box-shadow: 0 1px 3px rgba(0,0,0,0.05); }}
            td {{ padding: 0.33em 0.5em; vertical-align: top; }}
            td.diff-marker {{ width: 2%; text-align: right; color: #72777d; font-weight: bold; font-family: monospace; border-right: 1px solid #eaecf0; }}
            td.diff-content {{ width: 48%; font-family: monospace; word-wrap: break-word; white-space: pre-wrap; }}
            
            .diff-context {{ background: #f8f9fa; color: #54595d; }}
            .diff-addedline {{ background: #ddffdd; border-color: #bbffbb; }}
            .diff-deletedline {{ background: #ffe4e1; border-color: #ffcccc; }}
            
            .diffchange {{ font-weight: bold; text-decoration: none; }}
            .diff-addedline .diffchange {{ background: #aaffaa; }}
            .diff-deletedline .diffchange {{ background: #ffaaaa; }}
            .diff-empty {{ background: #eaecf0; }}
        </style>
    </head>
    <body>
        <div class="page-title">
            <h1>Bulk Diff Report</h1>
            <p>Filtering comments by regex: <strong>{pattern}</strong> (Matches: {len(diff_results)})</p>
        </div>
        {"<hr>".join(html_blocks)}
    </body>
    </html>
    """

    import tempfile
    import webbrowser
    import os

    fd, path = tempfile.mkstemp(suffix=".html", prefix="wikihow_bulk_diff_")
    with os.fdopen(fd, "w", encoding="utf-8") as f:
        f.write(full_html)

    console.print(f"\n  [bold green]✓[/bold green] Opening bulk diff report in your browser: [cyan]{path}[/cyan]\n")
    webbrowser.open(f"file://{path}")


def cmd_tree(args):
    """
    Recursively scrape WikiHow's category structure from a given root category.
    Saves the full hierarchy (categories, articles, creators) as a JSON file.
    """
    import json
    from rich.progress import Progress, SpinnerColumn, TextColumn, MofNCompleteColumn

    start_cat = " ".join(args.category) if isinstance(args.category, list) else args.category
    max_depth = args.depth
    include_articles = not args.no_articles
    output = args.output or f"{start_cat.replace(' ', '_').lower()}_tree.json"

    categories_visited = [0]

    with Progress(
        SpinnerColumn(),
        TextColumn("[cyan]{task.description}[/cyan]"),
        MofNCompleteColumn(),
        transient=False,
    ) as progress:
        task_id = progress.add_task(f"Crawling from '{start_cat}' (depth {max_depth})...", total=None)

        def on_progress(cat_name, depth):
            categories_visited[0] += 1
            progress.update(
                task_id,
                description=f"[{'cyan' if depth < 2 else 'dim'}]{'  ' * depth}[{depth}] {cat_name}[/]",
                advance=1,
            )

        try:
            tree = api.build_category_tree(
                start_cat,
                max_depth=max_depth,
                include_articles=include_articles,
                progress_callback=on_progress,
            )
        except ConnectionError as e:
            console.print(f"\n  [bold red]✗ Network error:[/bold red] {e}\n")
            sys.exit(1)

    # Write JSON output
    with open(output, "w", encoding="utf-8") as f:
        json.dump(tree, f, indent=2, ensure_ascii=False)
    console.print(f"\n  [bold green]✓[/bold green] Tree saved to [cyan]{output}[/cyan]")
    console.print(f"  [dim]Total categories crawled: {categories_visited[0]}[/dim]\n")

    # Optionally also write a flat Markdown summary
    if args.markdown:
        md_path = output.replace(".json", ".md")

        def _write_md(node, lines, indent=0):
            prefix = "  " * indent
            lines.append(f"{prefix}- **{node['name']}**")
            for art in node.get("articles", []):
                lines.append(f"{prefix}  - {art['title']} *(by {art['creator']})*")
            for child in node.get("subcats", []):
                _write_md(child, lines, indent + 1)

        lines = [f"# WikiHow Category Tree: {start_cat}\n"]
        _write_md(tree, lines)
        with open(md_path, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))
        console.print(f"  [bold green]✓[/bold green] Markdown summary saved to [cyan]{md_path}[/cyan]\n")


def cmd_categories(args):
    """List WikiHow categories with article counts."""
    prefix = args.prefix or ""
    limit = args.limit

    with console.status("[cyan]Fetching categories...[/cyan]"):
        try:
            cats = api.all_categories(prefix=prefix, limit=limit)
        except ConnectionError as e:
            console.print(f"\n  [bold red]✗ Network error:[/bold red] {e}\n")
            sys.exit(1)

    if not cats:
        console.print(f"\n  [yellow]No categories found{' with prefix: ' + prefix if prefix else ''}[/yellow]\n")
        return

    table = Table(
        title=f"WikiHow Categories{' (prefix: ' + prefix + ')' if prefix else ''}",
        box=box.ROUNDED,
        border_style="blue",
        show_lines=False,
    )
    table.add_column("#", style="dim", width=5)
    table.add_column("Category", style="bold")
    table.add_column("Articles", justify="right", style="green")
    table.add_column("Subcats", justify="right", style="cyan")

    for i, cat in enumerate(cats, 1):
        table.add_row(str(i), cat["name"], str(cat["pages"]), str(cat["subcats"]))

    console.print()
    console.print(table)
    console.print(f"\n  [dim]Total: {len(cats)} categories[/dim]\n")

    # Optional CSV export
    if args.csv:
        _export_categories_csv(cats, args.csv)


def cmd_contributors(args):
    """Show contributors for an article with gender info."""
    title = " ".join(args.title)
    slug = _normalise_title(title)
    limit = args.limit

    with console.status("[cyan]Fetching edit history...[/cyan]"):
        try:
            revisions = api.get_revisions(slug, limit=limit)
        except LookupError as e:
            console.print(f"\n  [bold red]✗[/bold red] {e}\n")
            sys.exit(1)
        except ConnectionError as e:
            console.print(f"\n  [bold red]✗ Network error:[/bold red] {e}\n")
            sys.exit(1)

    if not revisions:
        console.print(f"\n  [yellow]No revisions found for '{title}'[/yellow]\n")
        return

    # Collect unique registered usernames
    registered_users = list({r["user"] for r in revisions if not r.get("anon")})

    # Batch-fetch user info with gender
    user_info = {}
    use_profile_fallback = getattr(args, "profile_gender", False)
    if registered_users:
        with console.status("[cyan]Fetching user profiles...[/cyan]"):
            # Process in batches of 50
            for batch_start in range(0, len(registered_users), 50):
                batch = registered_users[batch_start:batch_start + 50]
                try:
                    info = api.get_users(batch, fallback_to_profile=use_profile_fallback)
                    user_info.update(info)
                except ConnectionError:
                    pass

    # Build table
    table = Table(
        title=f"Contributors for: {title.replace('-', ' ')}",
        box=box.ROUNDED,
        border_style="green",
    )
    table.add_column("#", style="dim", width=5)
    table.add_column("User", style="bold")
    table.add_column("Gender", justify="center")
    table.add_column("Edits (total)", justify="right", style="cyan")
    table.add_column("Timestamp", style="dim")
    table.add_column("Comment", max_width=40)

    # Gender color mapping
    gender_style = {"male": "blue", "female": "magenta", "unknown": "dim"}

    for i, rev in enumerate(revisions, 1):
        user = rev["user"]
        is_anon = rev.get("anon", False)

        if is_anon:
            gender = "anon"
            edit_count = "-"
            gender_display = "[dim]anon (IP)[/dim]"
        else:
            info = user_info.get(user, {})
            gender = info.get("gender", "unknown")
            edit_count = str(info.get("editcount", "?"))
            style = gender_style.get(gender, "dim")
            gender_display = f"[{style}]{gender}[/{style}]"

        comment = rev.get("comment", "")[:40]
        table.add_row(str(i), user, gender_display, edit_count, rev.get("timestamp", ""), comment)

    console.print()
    console.print(table)

    # Summary stats
    gender_counts = {"male": 0, "female": 0, "unknown": 0, "anon": 0}
    seen_users = set()
    for rev in revisions:
        user = rev["user"]
        if user in seen_users:
            continue
        seen_users.add(user)
        if rev.get("anon"):
            gender_counts["anon"] += 1
        else:
            g = user_info.get(user, {}).get("gender", "unknown")
            gender_counts[g] += 1

    console.print(f"\n  [bold]Unique Contributors:[/bold] {len(seen_users)}")
    console.print(f"  [blue]Male:[/blue] {gender_counts['male']}  "
                   f"[magenta]Female:[/magenta] {gender_counts['female']}  "
                   f"[dim]Unknown:[/dim] {gender_counts['unknown']}  "
                   f"[dim]Anonymous:[/dim] {gender_counts['anon']}\n")

    # Optional CSV export
    if args.csv:
        _export_contributors_csv(title, revisions, user_info, args.csv)


def cmd_analyze(args):
    """
    Bulk gender analysis for articles in a category.
    For each article: find the creator + all contributors, map gender, output summary.
    """
    category = " ".join(args.category)
    limit = args.limit

    with console.status(f"[cyan]Fetching articles in '{category}'...[/cyan]"):
        try:
            articles = api.get_category_members(category, limit=limit)
        except ConnectionError as e:
            console.print(f"\n  [bold red]✗ Network error:[/bold red] {e}\n")
            sys.exit(1)

    if not articles:
        console.print(f"\n  [yellow]No articles found in category '{category}'[/yellow]\n")
        return

    console.print(f"\n  [bold]Analyzing {len(articles)} articles in [cyan]{category}[/cyan]...[/bold]\n")

    rows = []
    all_users = set()

    for idx, article in enumerate(articles):
        title = article["title"]
        slug = _normalise_title(title)

        console.print(f"  [{idx+1}/{len(articles)}] {title}...", end=" ")

        try:
            creator = api.get_article_creator(slug)
            revisions = api.get_revisions(slug, limit=args.rev_limit)
        except (LookupError, ConnectionError) as e:
            console.print(f"[red]error[/red]")
            continue

        # Unique contributor usernames (non-anon)
        contributors = list({r["user"] for r in revisions if not r.get("anon")})
        anon_count = len({r["user"] for r in revisions if r.get("anon")})
        all_users.update(contributors)

        row = {
            "title": title,
            "creator": creator.get("user", "?") if creator else "?",
            "creator_anon": creator.get("anon", False) if creator else False,
            "created_at": creator.get("timestamp", "") if creator else "",
            "total_revisions": len(revisions),
            "unique_editors": len(contributors),
            "anon_editors": anon_count,
            "contributors": contributors,
        }
        rows.append(row)
        console.print("[green]ok[/green]")

    # Batch-resolve all users for gender
    all_users_list = list(all_users)
    user_info = {}
    use_profile_fallback = getattr(args, "profile_gender", False)
    with console.status("[cyan]Resolving user genders...[/cyan]"):
        for batch_start in range(0, len(all_users_list), 50):
            batch = all_users_list[batch_start:batch_start+50]
            try:
                info = api.get_users(batch, fallback_to_profile=use_profile_fallback)
                user_info.update(info)
            except ConnectionError:
                pass

    # Enrich rows with gender data
    for row in rows:
        creator_name = row["creator"]
        if row["creator_anon"]:
            row["creator_gender"] = "anon"
            row["creator_gender_source"] = "anon"
        else:
            c_info = user_info.get(creator_name, {})
            row["creator_gender"] = c_info.get("gender", "unknown")
            row["creator_gender_source"] = c_info.get("gender_source", "none")

        gender_dist = {"male": 0, "female": 0, "unknown": 0}
        for user in row["contributors"]:
            g = user_info.get(user, {}).get("gender", "unknown")
            gender_dist[g] += 1
        row["editors_male"] = gender_dist["male"]
        row["editors_female"] = gender_dist["female"]
        row["editors_unknown"] = gender_dist["unknown"]

    # Display summary table
    table = Table(
        title=f"Gender Analysis: {category}",
        box=box.ROUNDED,
        border_style="magenta",
    )
    table.add_column("#", width=4, style="dim")
    table.add_column("Article", style="bold", max_width=35)
    table.add_column("Creator", max_width=18)
    table.add_column("Creator Gender", justify="center")
    table.add_column("♂ Male", justify="right", style="blue")
    table.add_column("♀ Female", justify="right", style="magenta")
    table.add_column("? Unknown", justify="right", style="dim")
    table.add_column("Revisions", justify="right", style="cyan")

    gender_style = {"male": "blue", "female": "magenta", "unknown": "dim", "anon": "dim italic"}

    for i, row in enumerate(rows, 1):
        cg = row["creator_gender"]
        gs = gender_style.get(cg, "dim")
        table.add_row(
            str(i),
            row["title"],
            row["creator"],
            f"[{gs}]{cg}[/{gs}]",
            str(row["editors_male"]),
            str(row["editors_female"]),
            str(row["editors_unknown"]),
            str(row["total_revisions"]),
        )

    console.print()
    console.print(table)

    # Aggregate stats
    total_creators = {"male": 0, "female": 0, "unknown": 0, "anon": 0}
    total_editors = {"male": 0, "female": 0, "unknown": 0}
    for row in rows:
        total_creators[row["creator_gender"]] += 1
        total_editors["male"] += row["editors_male"]
        total_editors["female"] += row["editors_female"]
        total_editors["unknown"] += row["editors_unknown"]

    console.print(f"\n  [bold]═══ Aggregate for {category} ({len(rows)} articles) ═══[/bold]")
    console.print(f"  [bold]Article Creators:[/bold]  "
                   f"[blue]Male: {total_creators['male']}[/blue]  "
                   f"[magenta]Female: {total_creators['female']}[/magenta]  "
                   f"[dim]Unknown: {total_creators['unknown']}[/dim]  "
                   f"[dim]Anon: {total_creators['anon']}[/dim]")
    console.print(f"  [bold]All Editors:[/bold]       "
                   f"[blue]Male: {total_editors['male']}[/blue]  "
                   f"[magenta]Female: {total_editors['female']}[/magenta]  "
                   f"[dim]Unknown: {total_editors['unknown']}[/dim]")

    # Experience Stratification
    strata = [
        ("Novice", 1, 100),
        ("Active", 101, 1000),
        ("Power", 1001, 10000),
        ("Elite", 10001, float('inf'))
    ]
    
    strata_counts = {s[0]: {"male": 0, "female": 0, "unknown": 0} for s in strata}
    
    for user, info in user_info.items():
        ec = info.get("editcount", 0)
        gender = info.get("gender", "unknown")
        
        # Find which stratum this user belongs to
        for label, low, high in strata:
            if low <= ec <= high:
                if gender in strata_counts[label]:
                    strata_counts[label][gender] += 1
                break

    strata_table = Table(title="Gender by Experience Stratum", box=box.SIMPLE)
    strata_table.add_column("Level", style="cyan")
    strata_table.add_column("Range", style="dim")
    strata_table.add_column("♂ Male", justify="right", style="blue")
    strata_table.add_column("♀ Female", justify="right", style="magenta")
    strata_table.add_column("? Unknown", justify="right", style="dim")
    strata_table.add_column("F %", justify="right", style="bold")

    for label, low, high in strata:
        counts = strata_counts[label]
        m, f, u = counts["male"], counts["female"], counts["unknown"]
        total_known = m + f
        f_percent = f"{f/total_known:.1%}" if total_known > 0 else "0%"
        range_str = f"{low}-{high if high != float('inf') else '∞'}"
        strata_table.add_row(label, range_str, str(m), str(f), str(u), f_percent)

    console.print()
    console.print(strata_table)

    # Report on pronoun resolution efficacy
    resolved_via_pronouns = len([u for u in user_info.values() if u.get("gender_source") == "profile_pronouns"])
    if resolved_via_pronouns > 0:
        console.print(f"  [green]Note: {resolved_via_pronouns} users had gender resolved via profile pronouns.[/green]\n")
    else:
        console.print()

    # Auto-export CSV if requested
    if args.csv:
        _export_analysis_csv(category, rows, args.csv)


# ── CSV Helpers ───────────────────────────────────────────────────────────────

def _export_categories_csv(cats: list[dict], filepath: str):
    """Write categories list to CSV."""
    with open(filepath, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["name", "pages", "subcats", "size"])
        writer.writeheader()
        writer.writerows(cats)
    console.print(f"  [bold green]✓[/bold green] CSV saved to [cyan]{filepath}[/cyan]\n")


def _export_contributors_csv(title: str, revisions: list, user_info: dict, filepath: str):
    """Write contributor list to CSV."""
    with open(filepath, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["article", "user", "is_anon", "gender", "total_editcount", "timestamp", "comment"])
        for rev in revisions:
            user = rev["user"]
            is_anon = rev.get("anon", False)
            info = user_info.get(user, {})
            gender = "anon" if is_anon else info.get("gender", "unknown")
            edit_count = info.get("editcount", "") if not is_anon else ""
            writer.writerow([title, user, is_anon, gender, edit_count, rev.get("timestamp", ""), rev.get("comment", "")])
    console.print(f"  [bold green]✓[/bold green] CSV saved to [cyan]{filepath}[/cyan]\n")


def _export_analysis_csv(category: str, rows: list[dict], filepath: str):
    """Write bulk analysis to CSV."""
    with open(filepath, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([
            "category", "article", "creator", "creator_gender", "created_at",
            "total_revisions", "unique_editors", "anon_editors",
            "editors_male", "editors_female", "editors_unknown",
        ])
        for row in rows:
            writer.writerow([
                category, row["title"], row["creator"], row["creator_gender"],
                row["created_at"], row["total_revisions"], row["unique_editors"],
                row["anon_editors"], row["editors_male"], row["editors_female"],
                row["editors_unknown"],
            ])
    console.print(f"  [bold green]✓[/bold green] CSV saved to [cyan]{filepath}[/cyan]\n")


# ── Argument Parser ───────────────────────────────────────────────────────────

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="wikihow",
        description="📖  WikiHow CLI — Search, read, analyze, and export WikiHow articles from your terminal.",
        epilog="Examples:\n"
               "  wikihow search how to cook pasta\n"
               "  wikihow read Tie-a-Tie\n"
               "  wikihow random\n"
               "  wikihow export Tie-a-Tie --format md\n"
               "  wikihow browse python programming\n"
               "\n"
               "Research commands:\n"
               "  wikihow categories --prefix Technology --limit 100\n"
               "  wikihow contributors Tie-a-Tie --limit 50\n"
               "  wikihow analyze \"Python\" --limit 20 --csv results.csv\n",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "-v", "--version",
        action="version",
        version=f"%(prog)s {__version__}",
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # ── search ──
    p_search = subparsers.add_parser("search", help="Search WikiHow articles")
    p_search.add_argument("query", nargs="+", help="Search query")
    p_search.add_argument("-l", "--limit", type=int, default=10, help="Max results (default: 10)")
    p_search.set_defaults(func=cmd_search)

    # ── read ──
    p_read = subparsers.add_parser("read", help="Read an article in the terminal")
    p_read.add_argument("title", nargs="+", help="Article title (e.g. 'Tie a Tie' or 'Tie-a-Tie')")
    p_read.add_argument("--no-cache", action="store_true", help="Bypass cache")
    p_read.set_defaults(func=cmd_read)

    # ── random ──
    p_random = subparsers.add_parser("random", help="Read a random WikiHow article")
    p_random.set_defaults(func=cmd_random)

    # ── export ──
    p_export = subparsers.add_parser("export", help="Export article to file")
    p_export.add_argument("title", nargs="+", help="Article title")
    p_export.add_argument("-f", "--format", choices=["md", "json"], default="md",
                          help="Export format (default: md)")
    p_export.add_argument("-o", "--output", default=None, help="Output directory (default: current)")
    p_export.add_argument("--no-cache", action="store_true", help="Bypass cache")
    p_export.set_defaults(func=cmd_export)

    # ── browse ──
    p_browse = subparsers.add_parser("browse", help="Interactive search → read flow")
    p_browse.add_argument("query", nargs="+", help="Search query")
    p_browse.add_argument("-l", "--limit", type=int, default=10, help="Max results (default: 10)")
    p_browse.set_defaults(func=cmd_browse)

    # ── categories (research) ──
    p_cats = subparsers.add_parser("categories", help="List WikiHow categories")
    p_cats.add_argument("--prefix", default="", help="Filter by prefix (e.g. 'Technology')")
    p_cats.add_argument("-l", "--limit", type=int, default=50, help="Max categories (default: 50)")
    p_cats.add_argument("--csv", default=None, help="Export to CSV file")
    p_cats.set_defaults(func=cmd_categories)

    # ── tree (research) ──
    p_tree = subparsers.add_parser("tree", help="Recursively map WikiHow's category structure to JSON")
    p_tree.add_argument("category", nargs="+", help="Root category to start from (e.g. 'Relationships')")
    p_tree.add_argument("-d", "--depth", type=int, default=4, help="Max recursion depth (default: 4)")
    p_tree.add_argument("-o", "--output", default=None, help="Output JSON file path (default: <category>_tree.json)")
    p_tree.add_argument("--no-articles", action="store_true", help="Skip fetching articles per category (faster)")
    p_tree.add_argument("--markdown", action="store_true", help="Also generate a Markdown summary file")
    p_tree.set_defaults(func=cmd_tree)

    # ── contributors (research) ──
    p_contrib = subparsers.add_parser("contributors", help="Show article contributors with gender")
    p_contrib.add_argument("title", nargs="+", help="Article title")
    p_contrib.add_argument("-l", "--limit", type=int, default=50, help="Max revisions to analyze (default: 50)")
    p_contrib.add_argument("--csv", default=None, help="Export to CSV file")
    p_contrib.add_argument("--profile-gender", action="store_true", help="Attempt to infer gender from user profile pronouns (fallback)")
    p_contrib.set_defaults(func=cmd_contributors)

    # ── analyze (research) ──
    p_analyze = subparsers.add_parser("analyze", help="Bulk gender analysis for a category")
    p_analyze.add_argument("category", nargs="+", help="Category name")
    p_analyze.add_argument("-l", "--limit", type=int, default=20, help="Max articles to analyze (default: 20)")
    p_analyze.add_argument("--rev-limit", type=int, default=50, help="Max revisions per article (default: 50)")
    p_analyze.add_argument("--csv", default=None, help="Export results to CSV file")
    p_analyze.add_argument("--profile-gender", action="store_true", help="Attempt to infer gender from user profile pronouns (fallback)")
    p_analyze.set_defaults(func=cmd_analyze)

    # ── history (research) ──
    p_hist = subparsers.add_parser("history", help="Full chronological edit history of an article")
    p_hist.add_argument("title", nargs="+", help="Article title")
    p_hist.add_argument("-l", "--limit", type=int, default=500, help="Max revisions (default: 500)")
    p_hist.add_argument("--csv", default=None, help="Export to CSV file")
    p_hist.add_argument("--profile-gender", action="store_true", help="Attempt to infer gender from user profile pronouns (fallback)")
    p_hist.set_defaults(func=cmd_history)

    # ── survey (research) ──
    p_survey = subparsers.add_parser("survey", help="Bulk edit history survey for a category")
    p_survey.add_argument("category", nargs="+", help="Category name")
    p_survey.add_argument("-l", "--limit", type=int, default=20, help="Max articles (default: 20)")
    p_survey.add_argument("--rev-limit", type=int, default=500, help="Max revisions per article (default: 500)")
    p_survey.add_argument("--csv", default=None, help="Export revisions + users to CSV")
    p_survey.add_argument("--profile-gender", action="store_true", help="Attempt to infer gender from user profile pronouns (fallback)")
    p_survey.set_defaults(func=cmd_survey)

    # ── diff (research) ──
    p_diff = subparsers.add_parser("diff", help="View the content diff between two revisions")
    p_diff.add_argument("title", help="Article title")
    p_diff.add_argument("rev_from", type=int, help="Older revision ID")
    p_diff.add_argument("rev_to", type=int, help="Newer revision ID")
    p_diff.set_defaults(func=cmd_diff)

    # ── bulk-diff (research) ──
    p_b_diff = subparsers.add_parser("bulk-diff", help="Generate a combined diff report from CSV based on edit comments")
    p_b_diff.add_argument("csv_file", help="Path to the CSV file generated by history or survey")
    p_b_diff.add_argument("--match", required=True, help="Regex pattern to match in edit comments (e.g. 'gender|neutral')")
    p_b_diff.add_argument("-l", "--limit", type=int, default=30, help="Max diffs to fetch/display to prevent API abuse (default: 30)")
    p_b_diff.set_defaults(func=cmd_bulk_diff)

    # ── clear-cache ──
    p_clear = subparsers.add_parser("clear-cache", help="Clear the article cache")
    p_clear.set_defaults(func=cmd_clear_cache)

    return parser


def main():
    parser = build_parser()
    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(0)

    args.func(args)


if __name__ == "__main__":
    main()
