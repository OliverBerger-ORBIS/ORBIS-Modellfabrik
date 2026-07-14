#!/usr/bin/env python3
"""Export Markdown how-to docs to standalone HTML (tables, tasks, optional Mermaid)."""

from __future__ import annotations

import html
import re
import sys
from pathlib import Path


def escape_inline(text: str) -> str:
    text = html.escape(text, quote=False)
    text = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", text)
    text = re.sub(r"`([^`]+)`", r"<code>\1</code>", text)

    def link_repl(match: re.Match[str]) -> str:
        label = match.group(1)
        url = html.escape(match.group(2), quote=True)
        return f'<a href="{url}">{html.escape(label, quote=False)}</a>'

    return re.sub(r"\[([^\]]+)\]\(([^)]+)\)", link_repl, text)


def is_table_row(line: str) -> bool:
    stripped = line.strip()
    return stripped.startswith("|") and stripped.endswith("|")


def is_table_separator(line: str) -> bool:
    stripped = line.strip().strip("|")
    if not stripped:
        return False
    cells = [cell.strip() for cell in stripped.split("|")]
    return all(re.fullmatch(r":?-{3,}:?", cell or "") for cell in cells)


def parse_table_row(line: str) -> list[str]:
    return [cell.strip() for cell in line.strip().strip("|").split("|")]


def render_table(rows: list[list[str]]) -> str:
    if not rows:
        return ""
    header = rows[0]
    body = rows[1:]
    parts = ["<table>", "<thead><tr>"]
    for cell in header:
        parts.append(f"<th>{escape_inline(cell)}</th>")
    parts.append("</tr></thead>")
    if body:
        parts.append("<tbody>")
        for row in body:
            parts.append("<tr>")
            for cell in row:
                parts.append(f"<td>{escape_inline(cell)}</td>")
            parts.append("</tr>")
        parts.append("</tbody>")
    parts.append("</table>")
    return "".join(parts)


def convert_markdown(md: str) -> str:
    lines = md.splitlines()
    out: list[str] = []
    index = 0

    while index < len(lines):
        line = lines[index]

        if line.strip() == "---":
            out.append("<hr>")
            index += 1
            continue

        if line.startswith("```mermaid"):
            block: list[str] = []
            index += 1
            while index < len(lines) and not lines[index].startswith("```"):
                block.append(lines[index])
                index += 1
            index += 1
            out.append(f'<pre class="mermaid">\n{chr(10).join(block)}\n</pre>')
            continue

        if is_table_row(line):
            table_rows: list[list[str]] = []
            while index < len(lines) and is_table_row(lines[index]):
                if not is_table_separator(lines[index]):
                    table_rows.append(parse_table_row(lines[index]))
                index += 1
            out.append(render_table(table_rows))
            continue

        heading = re.match(r"^(#{1,6})\s+(.*)$", line)
        if heading:
            level = len(heading.group(1))
            out.append(f"<h{level}>{escape_inline(heading.group(2))}</h{level}>")
            index += 1
            continue

        list_match = re.match(r"^(- \[[ xX]\]|-)\s+(.*)$", line)
        if list_match:
            items: list[str] = []
            while index < len(lines):
                current = lines[index]
                checkbox = re.match(r"^- \[([ xX])\]\s+(.*)$", current)
                bullet = re.match(r"^- (?!\[)(.*)$", current)
                if checkbox:
                    checked = checkbox.group(1).lower() == "x"
                    checked_attr = " checked" if checked else ""
                    items.append(
                        f"<li class='task'><label><input type='checkbox' disabled{checked_attr}> "
                        f"{escape_inline(checkbox.group(2))}</label></li>"
                    )
                    index += 1
                    continue
                if bullet:
                    items.append(f"<li>{escape_inline(bullet.group(1))}</li>")
                    index += 1
                    continue
                break
            out.append(f"<ul>{''.join(items)}</ul>")
            continue

        if line.strip() == "":
            index += 1
            continue

        paragraph_lines = [line.strip()]
        index += 1
        while index < len(lines) and lines[index].strip() and not lines[index].startswith("#"):
            if is_table_row(lines[index]) or lines[index].startswith("```"):
                break
            if re.match(r"^- ", lines[index]):
                break
            paragraph_lines.append(lines[index].strip())
            index += 1
        out.append(f"<p>{escape_inline(' '.join(paragraph_lines))}</p>")

    return "\n".join(out)


HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="de">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{title}</title>
  <style>
    :root {{
      color-scheme: light dark;
      --text: #1a1a1a;
      --muted: #555;
      --border: #d0d7de;
      --bg: #fff;
      --code-bg: #f6f8fa;
    }}
    @media (prefers-color-scheme: dark) {{
      :root {{
        --text: #e6edf3;
        --muted: #9da7b3;
        --border: #30363d;
        --bg: #0d1117;
        --code-bg: #161b22;
      }}
    }}
    body {{
      margin: 0;
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif;
      line-height: 1.55;
      color: var(--text);
      background: var(--bg);
    }}
    main {{
      max-width: 960px;
      margin: 0 auto;
      padding: 2rem 1.25rem 4rem;
    }}
    h1, h2, h3 {{ line-height: 1.25; }}
    h1 {{ font-size: 1.75rem; margin-top: 0; }}
    h2 {{ margin-top: 2rem; border-bottom: 1px solid var(--border); padding-bottom: 0.35rem; }}
    h3 {{ margin-top: 1.5rem; }}
    p, ul {{ margin: 0.75rem 0; }}
    a {{ color: #0969da; word-break: break-word; }}
    code {{
      background: var(--code-bg);
      padding: 0.1em 0.35em;
      border-radius: 4px;
      font-size: 0.92em;
      word-break: break-all;
    }}
    table {{
      width: 100%;
      border-collapse: collapse;
      margin: 1rem 0;
      font-size: 0.95rem;
    }}
    th, td {{
      border: 1px solid var(--border);
      padding: 0.45rem 0.6rem;
      vertical-align: top;
      text-align: left;
    }}
    th {{ background: var(--code-bg); }}
    pre.mermaid {{
      background: transparent;
      border: 1px solid var(--border);
      border-radius: 8px;
      padding: 1rem;
      overflow-x: auto;
      margin: 1rem 0;
    }}
    .footer {{
      margin-top: 2.5rem;
      padding-top: 1rem;
      border-top: 1px solid var(--border);
      color: var(--muted);
      font-size: 0.85rem;
    }}
    li.task {{ list-style: none; margin-left: -1.2rem; }}
    @media print {{
      body {{ background: #fff; color: #000; }}
      main {{ max-width: none; padding: 0.4in 0.55in; }}
      a {{ color: #000; }}
      .no-print {{ display: none; }}
      h2, h3 {{ page-break-after: avoid; }}
      table, ul {{ page-break-inside: avoid; }}
      table {{ font-size: 0.82rem; }}
      th {{ background: #f0f0f0; }}
    }}
  </style>
</head>
<body>
  <main>
    {body}
    <p class="footer no-print">Generated from <code>{source}</code> — re-run <code>{rerun_cmd}</code> after edits.</p>
  </main>
  {mermaid_script}
</body>
</html>
"""

MERMAID_SCRIPT = """
  <script src="https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.min.js"></script>
  <script>
    mermaid.initialize({ startOnLoad: true, theme: "neutral", securityLevel: "loose" });
  </script>
"""


def main() -> int:
    if len(sys.argv) < 3:
        print(
            "Usage: export_markdown_html.py <input.md> <output.html> [rerun_cmd] [--mermaid]",
            file=sys.stderr,
        )
        return 1

    source = Path(sys.argv[1])
    target = Path(sys.argv[2])
    rerun_cmd = "bash scripts/export-markdown-html.sh"
    include_mermaid = False

    for arg in sys.argv[3:]:
        if arg == "--mermaid":
            include_mermaid = True
        else:
            rerun_cmd = arg

    md = source.read_text(encoding="utf-8")
    title_match = re.search(r"^# (.+)$", md, re.MULTILINE)
    title = title_match.group(1) if title_match else source.stem
    body = convert_markdown(md)
    mermaid_script = MERMAID_SCRIPT if include_mermaid else ""
    target.write_text(
        HTML_TEMPLATE.format(
            title=html.escape(title),
            body=body,
            source=source.name,
            rerun_cmd=rerun_cmd,
            mermaid_script=mermaid_script,
        ),
        encoding="utf-8",
    )
    print(f"Wrote {target}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
