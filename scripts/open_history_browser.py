import csv
import tempfile
import webbrowser
import os
import sys

csv_file = sys.argv[1]

with open(csv_file, "r", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    rows = list(reader)

html = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>WikiHow Article Edit History</title>
    <style>
        body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; margin: 40px; background: #eaecf0; color: #202122; }
        .header-box { background: white; border: 1px solid #a2a9b1; padding: 20px; border-radius: 4px; margin-bottom: 20px; box-shadow: 0 1px 3px rgba(0,0,0,0.05); }
        h1 { margin-top: 0; padding-bottom: 5px; font-weight: bold; }
        table { width: 100%; border-collapse: collapse; background: white; border: 1px solid #a2a9b1; box-shadow: 0 1px 3px rgba(0,0,0,0.05); }
        th, td { padding: 10px; border: 1px solid #eaecf0; text-align: left; }
        th { background: #f8f9fa; font-weight: bold; }
        .male { color: blue; }
        .female { color: magenta; }
        .unknown { color: gray; }
        .anon { color: gray; font-style: italic; }
        .delta-pos { color: green; font-weight: bold; }
        .delta-neg { color: red; font-weight: bold; }
        .delta-zero { color: gray; }
    </style>
</head>
<body>
    <div class="header-box">
        <h1>Edit History for "Clean a Kitchen"</h1>
        <p>Showing all {count} revisions over time.</p>
    </div>
    <table>
        <thead>
            <tr>
                <th>#</th>
                <th>Date</th>
                <th>Editor</th>
                <th>Gender</th>
                <th>Δ Size</th>
                <th>Comment</th>
            </tr>
        </thead>
        <tbody>
{tbody}
        </tbody>
    </table>
</body>
</html>
"""

tbody_lines = []
for row in rows:
    size_delta = row.get("size_delta", "0")
    try:
        delta_val = int(size_delta)
        if delta_val > 0:
            delta_cls = "delta-pos"
            delta_str = f"+{delta_val}"
        elif delta_val < 0:
            delta_cls = "delta-neg"
            delta_str = f"{delta_val}"
        else:
            delta_cls = "delta-zero"
            delta_str = "0"
    except:
        delta_cls = "delta-zero"
        delta_str = size_delta
        
    gender = row.get("gender", "unknown")
    if gender == "male": g_cls = "male"
    elif gender == "female": g_cls = "female"
    elif gender == "anon": g_cls = "anon"
    else: g_cls = "unknown"
    
    tbody_lines.append(f"""
        <tr>
            <td>{row.get('revision_num', '')}</td>
            <td>{row.get('timestamp', '').replace('T', ' ')[:16]}</td>
            <td class="{g_cls}"><strong>{row.get('user', '')}</strong></td>
            <td class="{g_cls}">{gender}</td>
            <td class="{delta_cls}">{delta_str}</td>
            <td>{row.get('comment', '')}</td>
        </tr>
    """)

html = html.replace("{count}", str(len(rows)))
html = html.replace("{tbody}", "".join(tbody_lines))

fd, path = tempfile.mkstemp(suffix=".html", prefix="wikihow_history_")
with os.fdopen(fd, "w", encoding="utf-8") as f:
    f.write(html)

print(f"Opening history table in your browser: {path}")
webbrowser.open(f"file://{path}")
