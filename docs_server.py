#!/usr/bin/env python3
# =======================================================================#
# Copyright (C) 2020 - 2026 Dominik Willner <th33xitus@gmail.com>       #
#                                                                       #
# This file is part of KIAUH - Klipper Installation And Update Helper   #
# https://github.com/dw-0/kiauh                                         #
#                                                                       #
# This file may be distributed under the terms of the GNU GPLv3 license #
# =======================================================================#
"""
Kalico Documentation Server with i18n support and Material-style UI.

Serves markdown files from the /docs directory as HTML pages.
Supports multiple languages via subdirectories (e.g. docs/zh/, docs/de/)
and via the docs/i18n/ directory (e.g. docs/i18n/simple-chinese/).
Default language content is placed directly in the docs/ root.

Features:
  - Material Design-inspired responsive layout
  - Client-side full-text search
  - Sidebar navigation (parsed from mkdocs.yml)
  - Automatic table-of-contents from page headings
  - Language switcher dropdown
  - Light/dark theme toggle
  - Admonition/callout support

Usage:
    python docs_server.py              # Start on default port 8800
    python docs_server.py --port 9000  # Custom port
    python docs_server.py --host 0.0.0.0  # Listen on all interfaces
"""

from __future__ import annotations

import argparse
import http.server
import json
import mimetypes
import re
import sys
from pathlib import Path
from typing import Any
from urllib.parse import unquote, urlparse

SCRIPT_DIR = Path(__file__).resolve().parent
DOCS_DIR = SCRIPT_DIR / "docs"

# i18n: language codes mapped to display names
KNOWN_LANGS: dict[str, str] = {
    "en": "English",
    "zh": "中文",
    "de": "Deutsch",
    "fr": "Français",
    "es": "Español",
    "pt": "Português",
    "it": "Italiano",
    "ja": "日本語",
    "ko": "한국어",
    "ru": "Русский",
}

# i18n: map subdirectories under docs/i18n/ to language codes
I18N_DIR_MAP: dict[str, str] = {
    "simple-chinese": "zh",
}

# -----------------------------------------------------------------------
# Language detection
# -----------------------------------------------------------------------


def detect_languages() -> tuple[list[str], dict[str, str]]:
    """Detect available languages by scanning docs/ and docs/i18n/ subdirectories."""
    langs: list[str] = []
    lang_dirs: dict[str, str] = {}
    if DOCS_DIR.is_dir():
        for entry in sorted(DOCS_DIR.iterdir()):
            if entry.is_dir() and entry.name in KNOWN_LANGS:
                langs.append(entry.name)
                lang_dirs[entry.name] = entry.name
        i18n_dir = DOCS_DIR / "i18n"
        if i18n_dir.is_dir():
            for entry in sorted(i18n_dir.iterdir()):
                if entry.is_dir() and entry.name in I18N_DIR_MAP:
                    lang_code = I18N_DIR_MAP[entry.name]
                    if lang_code not in langs:
                        langs.append(lang_code)
                        lang_dirs[lang_code] = f"i18n/{entry.name}"
    return langs, lang_dirs


def get_lang_name(code: str) -> str:
    """Get display name for a language code."""
    return KNOWN_LANGS.get(code, code)


# -----------------------------------------------------------------------
# Navigation parser (reads mkdocs.yml)
# -----------------------------------------------------------------------


def parse_nav() -> list[dict[str, Any]]:
    """Parse the nav section from mkdocs.yml into a tree structure.

    Returns a list of nodes, each with:
      - title (str)
      - href (str) for leaf nodes linking to .html pages or external URLs
      - children (list) for section nodes
    """
    mkdocs_path = DOCS_DIR / "_kalico" / "mkdocs.yml"
    if not mkdocs_path.is_file():
        return _fallback_nav()

    text = mkdocs_path.read_text(encoding="utf-8")
    m = re.search(r"^nav:\s*\n((?:\s+-.*\n?)+)", text, re.MULTILINE)
    if not m:
        return _fallback_nav()

    nav_text = m.group(1)
    items: list[dict[str, Any]] = []
    stack: list[tuple[list[dict[str, Any]], int]] = [(items, -1)]

    for line in nav_text.split("\n"):
        if not line.strip():
            continue
        indent = len(line) - len(line.lstrip(" "))
        content = line.lstrip(" -").strip()
        parent, parent_indent = stack[-1]

        while indent <= parent_indent:
            stack.pop()
            parent, parent_indent = stack[-1]

        # Check for "Title: file.md" or "Title: https://..." patterns
        if ": " in content:
            parts = content.split(": ", 1)
            left, right = parts[0].strip(), parts[1].strip()
            if right.startswith("http"):
                parent.append({"title": left, "href": right})
                continue
            if right.endswith(".md"):
                parent.append({
                    "title": left,
                    "href": "/" + right.replace(".md", ".html"),
                })
                continue
            # Section with children
            children: list[dict[str, Any]] = []
            node: dict[str, Any] = {"title": left, "children": children}
            parent.append(node)
            stack.append((children, indent))
            continue

        if content.endswith(".md"):
            name = content.rsplit("/", 1)[-1].replace(".md", "").replace("_", " ")
            parent.append({
                "title": name,
                "href": "/" + content.replace(".md", ".html"),
            })
            continue

        # Bare URL or unknown
        if content.startswith("http"):
            parent.append({"title": content, "href": content})
            continue

        # Section header
        title = content.rstrip(":")
        children: list[dict[str, Any]] = []
        node: dict[str, Any] = {"title": title, "children": children}
        parent.append(node)
        stack.append((children, indent))

    return items


def _fallback_nav() -> list[dict[str, Any]]:
    """Build a simple nav tree from .md files in docs/."""
    items: list[dict[str, Any]] = []
    if DOCS_DIR.is_dir():
        for entry in sorted(DOCS_DIR.iterdir()):
            if entry.suffix == ".md" and not entry.name.startswith("."):
                items.append({
                    "title": entry.stem.replace("_", " "),
                    "href": f"/{entry.stem}.html",
                })
    return items


def build_translated_nav(
    base_nav: list[dict[str, Any]], lang_code: str, lang_dir: str
) -> list[dict[str, Any]]:
    """Translate nav titles using the first heading from translated .md files.

    Section-header nodes keep their English titles (no corresponding .md file).
    External-link nodes are kept as-is.
    """
    if not lang_code or not lang_dir:
        return base_nav

    lang_path = DOCS_DIR / lang_dir

    def _translate(node: dict[str, Any]) -> dict[str, Any]:
        if "href" in node and not str(node["href"]).startswith("http"):
            # Leaf node with local .md file
            stem = node["href"].rsplit("/", 1)[-1].replace(".html", ".md")
            md_file = lang_path / stem
            if md_file.is_file():
                try:
                    text = md_file.read_text(encoding="utf-8")
                    m = _INDEX_TITLE_RE.search(text)
                    if m:
                        return {"title": m.group(1), "href": node["href"]}
                except Exception:
                    pass
            return dict(node)
        if "children" in node:
            return {
                "title": node["title"],
                "children": [_translate(c) for c in node["children"]],
            }
        return dict(node)

    return [_translate(n) for n in base_nav]


# -----------------------------------------------------------------------
# Search index builder
# -----------------------------------------------------------------------

SEARCH_INDEX: list[dict[str, str]] = []
_INDEX_TITLE_RE = re.compile(r"^#\s+(.+)$", re.MULTILINE)


def build_search_index(lang_dirs: dict[str, str]) -> list[dict[str, str]]:
    """Build a search index from all markdown files (English + translations)."""
    index: list[dict[str, str]] = []

    def _add(md_file: Path, prefix: str, lang: str) -> None:
        try:
            text = md_file.read_text(encoding="utf-8")
        except Exception:
            return
        title = md_file.stem.replace("_", " ")
        m = _INDEX_TITLE_RE.search(text)
        if m:
            title = m.group(1)
        # Strip code blocks and markdown symbols for clean search text
        clean = re.sub(r"```.*?```", " ", text, flags=re.DOTALL)
        clean = re.sub(r"^#{1,6}\s+", " ", clean, flags=re.MULTILINE)
        clean = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", clean)
        clean = re.sub(r"[*_~>`|#\-!\[\]()]", " ", clean)
        clean = re.sub(r"\s+", " ", clean).strip()[:800]
        index.append({
            "title": title,
            "text": clean,
            "url": f"/{prefix}{md_file.stem}.html",
            "lang": lang,
        })

    # English (root)
    for md_file in sorted(DOCS_DIR.glob("*.md")):
        if not md_file.name.startswith("."):
            _add(md_file, "", "en")

    # Translations
    for lang_code, rel_dir in lang_dirs.items():
        lang_path = DOCS_DIR / rel_dir
        if lang_path.is_dir():
            for md_file in sorted(lang_path.glob("*.md")):
                _add(md_file, f"{lang_code}/", lang_code)

    return index


# -----------------------------------------------------------------------
# Markdown to HTML converter
# -----------------------------------------------------------------------

_MD_LINK_RE = re.compile(r"\[([^\]]+)\]\(([^)]+)\)")
_MD_IMAGE_RE = re.compile(r"!\[([^\]]*)\]\(([^)]+)\)")
_MD_BOLD_RE = re.compile(r"\*\*(.+?)\*\*")
_MD_ITALIC_RE = re.compile(r"(?<!\*)\*([^*\n]+?)\*(?!\*)")
_MD_INLINE_CODE_RE = re.compile(r"`([^`]+)`")
_MD_HR_RE = re.compile(r"^---$", re.MULTILINE)
_ADMONITION_RE = re.compile(r"^!!!\s+(\w+)(?:\s+\"([^\"]*)\")?\s*$")
_COLLAPSE_RE = re.compile(r"^\?\?\?\s+(\w+)?(?:\s+\"([^\"]*)\")?\s*$")


def _slugify(text: str) -> str:
    """Convert text to a URL-friendly slug for heading IDs."""
    text = re.sub(r"<[^>]+>", "", text)
    text = re.sub(r"[`*_~]", "", text)
    text = re.sub(r"[^a-zA-Z0-9\s-]", "", text.lower())
    return re.sub(r"\s+", "-", text).strip("-")


def md_to_html(text: str, base_path: str = "") -> str:
    """Convert markdown text to HTML with heading IDs and admonition support."""
    stored: dict[str, str] = {}
    text = _extract_admonitions(text, stored)
    html = _md_render(text, base_path)
    for token, replacement in stored.items():
        html = re.sub(
            rf"<p>\s*{re.escape(token)}\s*</p>",
            replacement,
            html,
        )
    return html


def _extract_admonitions(text: str, stored: dict[str, str]) -> str:
    """Extract !!! / ??? admonitions from text, store their HTML, return text with placeholders."""
    lines = text.split("\n")
    out: list[str] = []
    i = 0
    counter = 0
    while i < len(lines):
        line = lines[i]
        am = _ADMONITION_RE.match(line)
        cm = _COLLAPSE_RE.match(line)
        if am:
            kind = am.group(1).lower()
            title = am.group(2) if am.group(2) else kind.capitalize()
            body_lines, i = _gather_indented(lines, i + 1)
            body = _md_render("\n".join(body_lines))
            key = f"<!--ADMON{counter}-->"
            stored[key] = (
                f'<div class="admonition {kind}">'
                f'<p class="admonition-title">{title}</p>{body}</div>'
            )
            if out and out[-1] != "":
                out.append("")
            out.append(key)
            out.append("")
            counter += 1
        elif cm:
            kind = (cm.group(1) or "note").lower()
            title = cm.group(2) if cm.group(2) else kind.capitalize()
            body_lines, i = _gather_indented(lines, i + 1)
            body = _md_render("\n".join(body_lines))
            key = f"<!--ADMON{counter}-->"
            stored[key] = (
                f'<details class="admonition {kind}">'
                f'<summary class="admonition-title">{title}</summary>{body}</details>'
            )
            if out and out[-1] != "":
                out.append("")
            out.append(key)
            out.append("")
            counter += 1
        else:
            out.append(line)
            i += 1
    return "\n".join(out)


def _gather_indented(lines: list[str], start: int) -> tuple[list[str], int]:
    """Gather indented lines (4+ spaces or blank) for admonition bodies."""
    body: list[str] = []
    i = start
    while i < len(lines):
        if lines[i].startswith("    "):
            body.append(lines[i][4:])
        elif lines[i].strip() == "":
            body.append("")
        else:
            break
        i += 1
    while body and body[-1] == "":
        body.pop()
    return body, i


def _md_render(text: str, base_path: str = "") -> str:
    lines = text.split("\n")
    result: list[str] = []
    in_paragraph = False
    in_code_block = False
    code_lang = ""
    code_lines: list[str] = []
    in_list = False
    in_ordered_list = False

    def close_paragraph() -> None:
        nonlocal in_paragraph
        if in_paragraph:
            result.append("</p>")
            in_paragraph = False

    def close_list() -> None:
        nonlocal in_list, in_ordered_list
        if in_list:
            result.append("</ul>")
            in_list = False
        if in_ordered_list:
            result.append("</ol>")
            in_ordered_list = False

    for line in lines:
        # Code block fence
        if line.startswith("```"):
            if in_code_block:
                code_html = "\n".join(code_lines)
                if code_lang:
                    code_html = (
                        f'<pre><code class="language-{code_lang}">'
                        f"{code_html}</code></pre>"
                    )
                else:
                    code_html = f"<pre><code>{code_html}</code></pre>"
                result.append(code_html)
                code_lines = []
                in_code_block = False
                code_lang = ""
            else:
                close_paragraph()
                close_list()
                code_lang = line[3:].strip()
                in_code_block = True
            continue

        if in_code_block:
            code_lines.append(line)
            continue

        # Horizontal rule
        if _MD_HR_RE.fullmatch(line):
            close_paragraph()
            close_list()
            result.append("<hr>")
            continue

        # Headings
        heading = None
        if line.startswith("#### "):
            heading = ("h4", line[5:])
        elif line.startswith("### "):
            heading = ("h3", line[4:])
        elif line.startswith("## "):
            heading = ("h2", line[3:])
        elif line.startswith("# "):
            heading = ("h1", line[2:])
        if heading:
            close_paragraph()
            close_list()
            tag, content = heading
            hid = _slugify(content)
            result.append(f"<{tag} id=\"{hid}\">{_inline_md(content, base_path)}</{tag}>")
            continue

        # Unordered list
        ul_match = re.match(r"^(\s*)[-*]\s+(.*)", line)
        if ul_match:
            close_paragraph()
            if in_ordered_list:
                result.append("</ol>")
                in_ordered_list = False
            if not in_list:
                result.append("<ul>")
                in_list = True
            result.append(f"<li>{_inline_md(ul_match.group(2), base_path)}</li>")
            continue

        # Ordered list
        ol_match = re.match(r"^(\s*)\d+\.\s+(.*)", line)
        if ol_match:
            close_paragraph()
            if in_list:
                result.append("</ul>")
                in_list = False
            if not in_ordered_list:
                result.append("<ol>")
                in_ordered_list = True
            result.append(f"<li>{_inline_md(ol_match.group(2), base_path)}</li>")
            continue

        # Table
        if "|" in line and line.strip().startswith("|"):
            close_paragraph()
            close_list()
            row_html = _table_row(line)
            if row_html:
                result.append(row_html)
            continue

        # Empty line
        if not line.strip():
            close_paragraph()
            close_list()
            continue

        # Regular paragraph
        close_list()
        stripped = line.strip()
        # Pass through block-level HTML without wrapping in <p>
        if stripped.startswith(("<div", "<details", "</div", "</details")):
            close_paragraph()
            result.append(line)
            continue
        if not in_paragraph:
            result.append("<p>")
            in_paragraph = True
        else:
            result.append(" ")
        result.append(_inline_md(line, base_path))

    close_paragraph()
    close_list()
    return "\n".join(result)


def _inline_md(text: str, base_path: str) -> str:
    """Convert inline markdown to HTML."""
    text = _MD_IMAGE_RE.sub(
        lambda m: (
            f'<img src="{_resolve_path(m.group(2), base_path)}"'
            f' alt="{m.group(1)}" loading="lazy">'
        ),
        text,
    )
    text = _MD_LINK_RE.sub(
        lambda m: f'<a href="{_resolve_path(m.group(2), base_path)}">{m.group(1)}</a>',
        text,
    )
    text = _MD_BOLD_RE.sub(r"<strong>\1</strong>", text)
    text = _MD_ITALIC_RE.sub(r"<em>\1</em>", text)
    text = _MD_INLINE_CODE_RE.sub(r"<code>\1</code>", text)
    return text


def _resolve_path(href: str, base: str) -> str:
    """Resolve a relative link path relative to the base path."""
    if href.startswith(("http://", "https://", "#")):
        return href
    if href.endswith(".md"):
        href = href[:-3] + ".html"
    if base:
        return f"/{base}/{href}" if not href.startswith("/") else href
    return f"/{href}" if not href.startswith("/") else href


def _table_row(line: str) -> str:
    """Convert a markdown table row to an HTML table row."""
    if re.match(r"^\|[\s\-:|]+\|$", line):
        return ""  # skip separator row
    cells = [c.strip() for c in line.strip("|").split("|")]
    tag = "th" if "|---" not in line else "td"
    return (
        "<table><tr>"
        + "".join(f"<{tag}>{_inline_md(c, '')}</{tag}>" for c in cells)
        + "</tr></table>"
    )


# -----------------------------------------------------------------------
# Table of contents builder (from rendered HTML)
# -----------------------------------------------------------------------

_HEADING_RE = re.compile(r'<h([2-4])\s+id="([^"]*)"[^>]*>(.*?)</h[2-4]>')


def build_toc_html(html_content: str) -> str:
    """Extract headings from HTML to build a table-of-contents list."""
    headings = _HEADING_RE.findall(html_content)
    if len(headings) < 2:
        return ""
    items: list[str] = []
    for level, hid, htext in headings:
        cls = f"md-nav__link--level{level}"
        items.append(
            f'<li class="md-nav__item">'
            f'<a href="#{hid}" class="md-nav__link {cls}">{htext}</a></li>'
        )
    return '<ul class="md-nav__list">\n' + "\n".join(items) + "\n</ul>"


# -----------------------------------------------------------------------
# Navigation HTML builder
# -----------------------------------------------------------------------


def build_nav_html(nav: list[dict[str, Any]], current_path: str, lang_prefix: str) -> str:
    """Render the navigation tree as nested HTML lists."""

    def _render(items: list[dict[str, Any]], depth: int) -> str:
        parts: list[str] = ['<ul class="md-nav__list">']
        for item in items:
            if "children" in item:
                parts.append(
                    f'<li class="md-nav__item md-nav__item--section">'
                    f'<span class="md-nav__link md-nav__link--section">'
                    f'{item["title"]}</span>'
                )
                parts.append(_render(item["children"], depth + 1))
                parts.append("</li>")
            elif "href" in item:
                href = item["href"]
                if lang_prefix and not href.startswith("http"):
                    href = "/" + lang_prefix + href
                active = ""
                if href.rstrip("/") == current_path or (
                    href.endswith(".html")
                    and current_path.endswith(".html")
                    and href == current_path
                ):
                    active = " md-nav__link--active"
                ext = ' target="_blank" rel="noopener"' if item["href"].startswith("http") else ""
                parts.append(
                    f'<li class="md-nav__item">'
                    f'<a href="{href}" class="md-nav__link{active}"{ext}>'
                    f'{item["title"]}</a></li>'
                )
        parts.append("</ul>")
        return "\n".join(parts)

    return _render(nav, 0)


# -----------------------------------------------------------------------
# Language switcher
# -----------------------------------------------------------------------


def build_lang_switcher(current_lang: str, available: list[str], path: str) -> str:
    """Build HTML for a dropdown language switcher."""
    if len(available) == 0:
        return ""
    options: list[str] = []
    sel = " selected" if current_lang == "" else ""
    options.append(f'<option value="/{path}"{sel}>English</option>')
    for lc in available:
        sel = " selected" if lc == current_lang else ""
        name = get_lang_name(lc)
        options.append(f'<option value="/{lc}/{path}"{sel}>{name}</option>')
    return (
        '<select class="md-lang-select" onchange="if(this.value)window.location=this.value"'
        ' aria-label="Language">'
        + "".join(options)
        + "</select>"
    )


# -----------------------------------------------------------------------
# Breadcrumb
# -----------------------------------------------------------------------


def build_breadcrumb(parts: list[tuple[str, str]]) -> str:
    """Build breadcrumb HTML from (label, url) pairs."""
    items: list[str] = []
    for label, url in parts:
        if url:
            items.append(f'<a href="{url}">{label}</a>')
        else:
            items.append(label)
    return '<nav class="md-breadcrumb">' + " / ".join(items) + "</nav>"


# -----------------------------------------------------------------------
# HTML page template
# -----------------------------------------------------------------------

_PAGE_TEMPLATE = r"""<!DOCTYPE html>
<html lang="{lang}" data-color-scheme="os">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<link rel="icon" type="image/png" href="/logo/kalico-32x32.png">
<title>{title} - Kalico Docs</title>
<style>
  /* ============================================================
     Material-style CSS for Kalico Documentation Server
     ============================================================ */
  :root {{
    --md-primary: #ff6e42;
    --md-primary-fg: #fff;
    --md-primary-dim: #ff8a65;
    --md-default-bg: #fff;
    --md-default-fg: #1a1a1a;
    --md-surface-bg: #f5f5f5;
    --md-surface-fg: #333;
    --md-code-bg: #f0f0f0;
    --md-code-fg: #36464e;
    --md-border: #e0e0e0;
    --md-link: #ff6e42;
    --md-dim: #6e6e6e;
    --md-heading-fg: #222;
    --md-shadow: 0 0 8px rgba(0,0,0,.08);
  }}
  [data-color-scheme="dark"] {{
    --md-default-bg: #1a1a1a;
    --md-default-fg: #cfd8dc;
    --md-surface-bg: #242424;
    --md-surface-fg: #ccc;
    --md-code-bg: #2d2d2d;
    --md-code-fg: #c9d1d9;
    --md-border: #404040;
    --md-link: #ff8a65;
    --md-dim: #999;
    --md-heading-fg: #e0e0e0;
    --md-shadow: 0 0 8px rgba(0,0,0,.3);
  }}
  @media (prefers-color-scheme: dark) {{
    :root[data-color-scheme="os"] {{
      --md-default-bg: #1a1a1a;
      --md-default-fg: #cfd8dc;
      --md-surface-bg: #242424;
      --md-surface-fg: #ccc;
      --md-code-bg: #2d2d2d;
      --md-code-fg: #c9d1d9;
      --md-border: #404040;
      --md-link: #ff8a65;
      --md-dim: #999;
      --md-heading-fg: #e0e0e0;
      --md-shadow: 0 0 8px rgba(0,0,0,.3);
    }}
  }}
  *,*::before,*::after{{box-sizing:border-box;margin:0;padding:0}}
  html{{font-size:16px;scroll-padding-top:64px}}
  body{{
    font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Helvetica,Arial,sans-serif;
    background:var(--md-default-bg);color:var(--md-default-fg);line-height:1.7;
  }}
  a{{color:var(--md-link);text-decoration:none}}
  a:hover{{text-decoration:underline}}

  /* Header */
  .md-header{{
    position:sticky;top:0;z-index:100;height:52px;
    background:var(--md-primary);color:var(--md-primary-fg);
    box-shadow:var(--md-shadow);
  }}
  .md-header__inner{{
    display:flex;align-items:center;height:100%;padding:0 16px;gap:12px;max-width:1440px;margin:0 auto;
  }}
  .md-header__left{{display:flex;align-items:center;gap:8px;flex-shrink:0}}
  .md-header__menu{{
    display:none;background:none;border:none;color:inherit;font-size:1.4em;
    cursor:pointer;padding:4px 6px;border-radius:4px;
  }}
  .md-header__menu:hover{{background:rgba(255,255,255,.15)}}
  .md-header__title{{
    display:flex;align-items:center;gap:8px;font-weight:700;font-size:1.05em;
    color:inherit;text-decoration:none;white-space:nowrap;
  }}
  .md-header__title img{{height:26px;flex-shrink:0}}
  .md-header__right{{display:flex;align-items:center;gap:8px;margin-left:auto;flex-shrink:0}}

  /* Search */
  .md-search{{position:relative;flex:1;max-width:360px;min-width:140px}}
  .md-search__input{{
    width:100%;height:36px;padding:0 12px 0 36px;border:none;border-radius:6px;
    background:rgba(255,255,255,.18);color:#fff;font-size:.88em;outline:none;
    transition:background .2s;
  }}
  .md-search__input::placeholder{{color:rgba(255,255,255,.6)}}
  .md-search__input:focus{{background:rgba(255,255,255,.28)}}
  [data-color-scheme="dark"] .md-search__input:focus{{background:#333}}
  .md-search::before{{
    content:"\1f50d";position:absolute;left:10px;top:50%;transform:translateY(-50%);
    font-size:.9em;opacity:.7;pointer-events:none;
  }}
  .md-search__output{{
    display:none;position:absolute;top:42px;left:0;right:0;
    background:var(--md-default-bg);border:1px solid var(--md-border);
    border-radius:8px;box-shadow:0 8px 24px rgba(0,0,0,.18);z-index:200;
    max-height:60vh;overflow-y:auto;min-width:300px;
  }}
  .md-search__output.active{{display:block}}
  .md-search__item{{
    display:block;padding:10px 16px;border-bottom:1px solid var(--md-border);
    color:var(--md-default-fg);text-decoration:none;transition:background .1s;
  }}
  .md-search__item:hover,.md-search__item:focus{{background:var(--md-surface-bg);text-decoration:none}}
  .md-search__item:last-child{{border-bottom:none}}
  .md-search__title{{display:block;font-weight:600;font-size:.92em;color:var(--md-link)}}
  .md-search__text{{display:block;font-size:.82em;color:var(--md-dim);margin-top:2px;line-height:1.4;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}}
  .md-search__none{{padding:16px;text-align:center;color:var(--md-dim);font-size:.88em}}

  /* Language select */
  .md-lang-select{{
    height:36px;padding:0 8px;border:none;border-radius:6px;
    background:rgba(255,255,255,.15);color:inherit;font-size:.85em;cursor:pointer;outline:none;
    min-width:80px;
  }}
  .md-lang-select option{{color:#1a1a1a;background:#fff}}

  /* Theme toggle */
  .md-theme-btn{{
    background:none;border:none;color:inherit;font-size:1.2em;cursor:pointer;
    padding:4px 8px;border-radius:6px;line-height:1;
  }}
  .md-theme-btn:hover{{background:rgba(255,255,255,.15)}}

  /* Main container */
  .md-container{{display:flex;max-width:1440px;margin:0 auto;min-height:calc(100vh - 52px)}}

  /* Sidebars */
  .md-sidebar{{
    width:260px;flex-shrink:0;position:sticky;top:52px;
    height:calc(100vh - 52px);overflow-y:auto;padding:16px 0 24px;
    background:var(--md-surface-bg);border-right:1px solid var(--md-border);
    scrollbar-width:thin;scrollbar-color:var(--md-border) transparent;
  }}
  .md-sidebar::-webkit-scrollbar{{width:4px}}
  .md-sidebar::-webkit-scrollbar-thumb{{background:var(--md-border);border-radius:4px}}
  .md-sidebar--secondary{{
    border-right:none;border-left:1px solid var(--md-border);
  }}

  /* Nav */
  .md-nav{{font-size:.85em;line-height:1.5}}
  .md-nav__list{{list-style:none;padding:0;margin:0}}
  .md-nav__item{{padding:0}}
  .md-nav__link{{
    display:block;padding:5px 24px;color:var(--md-default-fg);text-decoration:none;
    border-left:3px solid transparent;transition:all .15s;
  }}
  .md-nav__link:hover{{background:var(--md-border);text-decoration:none}}
  .md-nav__link--active{{
    color:var(--md-primary);border-left-color:var(--md-primary);
    font-weight:600;background:rgba(255,110,66,.06);
  }}
  .md-nav__link--section{{
    font-weight:700;color:var(--md-heading-fg);padding:8px 24px 4px;border-left:none;
    font-size:.92em;letter-spacing:.02em;
  }}
  .md-nav__link--section:hover{{background:transparent}}
  .md-nav__item--section > .md-nav__list > .md-nav__item > .md-nav__link{{
    padding-left:32px;font-size:.84em;
  }}
  .md-nav__item--section .md-nav__item--section > .md-nav__list > .md-nav__item > .md-nav__link{{
    padding-left:40px;
  }}
  /* TOC links */
  .md-nav--toc .md-nav__link--level2{{padding-left:20px;font-size:.84em}}
  .md-nav--toc .md-nav__link--level3{{padding-left:32px;font-size:.82em}}
  .md-nav--toc .md-nav__link--level4{{padding-left:44px;font-size:.8em}}

  /* Content */
  .md-content{{
    flex:1;min-width:0;padding:24px 32px 80px;max-width:880px;
  }}
  .md-content__inner{{}}
  .md-content h1{{
    font-size:1.9em;font-weight:700;color:var(--md-heading-fg);
    border-bottom:1px solid var(--md-border);padding-bottom:8px;margin-bottom:20px;
  }}
  .md-content h2{{
    font-size:1.45em;font-weight:600;color:var(--md-heading-fg);
    margin:32px 0 12px;padding-top:8px;
  }}
  .md-content h3{{
    font-size:1.2em;font-weight:600;color:var(--md-heading-fg);
    margin:24px 0 8px;
  }}
  .md-content h4{{font-size:1.05em;font-weight:600;margin:20px 0 6px;color:var(--md-heading-fg)}}
  .md-content p,.md-content li{{margin-bottom:10px}}
  .md-content ul,.md-content ol{{padding-left:28px;margin-bottom:12px}}
  .md-content li > ul,.md-content li > ol{{margin-top:4px;margin-bottom:4px}}
  .md-content pre{{
    background:var(--md-code-bg);border:1px solid var(--md-border);
    border-radius:8px;padding:14px 18px;overflow-x:auto;margin-bottom:16px;
    font-size:.85em;line-height:1.55;color:var(--md-code-fg);
  }}
  .md-content code{{
    background:var(--md-code-bg);padding:2px 6px;border-radius:4px;
    font-size:.88em;color:var(--md-code-fg);
  }}
  .md-content pre code{{background:none;padding:0;font-size:1em}}
  .md-content table{{border-collapse:collapse;margin-bottom:16px;width:100%;font-size:.9em}}
  .md-content th,.md-content td{{
    border:1px solid var(--md-border);padding:8px 14px;text-align:left;
  }}
  .md-content th{{background:var(--md-surface-bg);font-weight:600}}
  .md-content img{{max-width:100%;height:auto;border-radius:4px}}
  .md-content hr{{border:none;border-top:1px solid var(--md-border);margin:24px 0}}
  .md-content blockquote{{
    border-left:4px solid var(--md-primary-dim);padding:8px 16px;
    margin:12px 0;color:var(--md-dim);background:var(--md-surface-bg);
    border-radius:0 6px 6px 0;
  }}
  /* Admonitions */
  .admonition{{
    border-left:4px solid;border-radius:6px;padding:12px 18px;margin:16px 0;
    background:var(--md-surface-bg);font-size:.92em;
  }}
  .admonition-title{{
    font-weight:700;margin-bottom:6px;font-size:.95em;
  }}
  .admonition.note{{border-color:#448aff;background:rgba(68,138,255,.06)}}
  .admonition.note .admonition-title{{color:#448aff}}
  .admonition.warning{{border-color:#ff9100;background:rgba(255,145,0,.06)}}
  .admonition.warning .admonition-title{{color:#ff9100}}
  .admonition.danger,.admonition.error{{border-color:#ff1744;background:rgba(255,23,68,.06)}}
  .admonition.danger .admonition-title,.admonition.error .admonition-title{{color:#ff1744}}
  .admonition.info,.admonition.tip{{border-color:#00bfa5;background:rgba(0,191,165,.06)}}
  .admonition.info .admonition-title,.admonition.tip .admonition-title{{color:#00bfa5}}
  .admonition.success,.admonition.check{{border-color:#00c853;background:rgba(0,200,83,.06)}}
  .admonition.success .admonition-title,.admonition.check .admonition-title{{color:#00c853}}
  details.admonition{{cursor:pointer}}
  details.admonition summary{{font-weight:700;outline:none}}

  /* Breadcrumb */
  .md-breadcrumb{{
    font-size:.82em;color:var(--md-dim);margin-bottom:12px;
  }}
  .md-breadcrumb a{{color:var(--md-dim)}}
  .md-breadcrumb a:hover{{color:var(--md-link)}}

  /* Index page */
  .file-list{{list-style:none;padding:0}}
  .file-list li{{
    border:1px solid var(--md-border);border-radius:8px;margin-bottom:8px;
    transition:all .15s;
  }}
  .file-list li:hover{{border-color:var(--md-primary);box-shadow:0 2px 8px rgba(255,110,66,.12)}}
  .file-list a{{
    display:block;padding:14px 20px;text-decoration:none;color:inherit;
  }}
  .file-list .title{{display:block;font-weight:600;color:var(--md-link);margin-bottom:2px}}
  .file-list .desc{{display:block;font-size:.85em;color:var(--md-dim)}}

  /* No content */
  .no-content{{text-align:center;padding:80px 20px;color:var(--md-dim)}}
  .no-content h2{{border:none;color:var(--md-dim)}}

  /* Mobile overlay */
  .md-overlay{{
    display:none;position:fixed;inset:0;background:rgba(0,0,0,.4);z-index:90;
  }}
  .md-overlay.active{{display:block}}

  /* Responsive */
  @media (max-width: 960px) {{
    .md-header__menu{{display:block}}
    .md-search{{max-width:200px}}
    .md-sidebar{{
      position:fixed;top:52px;left:0;z-index:95;height:calc(100vh - 52px);
      transform:translateX(-100%);transition:transform .25s ease;
      width:280px;
    }}
    .md-sidebar.active{{transform:translateX(0)}}
    .md-sidebar--secondary{{display:none}}
    .md-content{{padding:20px 16px 60px}}
  }}
  @media (max-width: 600px) {{
    .md-header__title span{{display:none}}
    .md-search{{max-width:140px;min-width:100px}}
    .md-lang-select{{font-size:.75em;padding:0 4px}}
  }}
</style>
</head>
<body>
<input type="checkbox" id="md-drawer" style="display:none">
<header class="md-header">
  <div class="md-header__inner">
    <div class="md-header__left">
      <button class="md-header__menu" onclick="document.querySelector('.md-sidebar--primary').classList.toggle('active');document.querySelector('.md-overlay').classList.toggle('active')" aria-label="Menu">&#9776;</button>
      <a href="/{prefix}" class="md-header__title">
        <img src="/logo/kalico-96x96.png" alt="Kalico">
        <span>Kalico Docs</span>
      </a>
    </div>
    <div class="md-header__right">
      <div class="md-search">
        <input class="md-search__input" type="text" placeholder="Search" data-index="/search_index.json" data-lang="{lang_code}" aria-label="Search">
        <div class="md-search__output"></div>
      </div>
      {lang_switcher}
      <button class="md-theme-btn" onclick="toggle_theme()" title="Toggle theme" aria-label="Toggle theme">&#9681;</button>
    </div>
  </div>
</header>
<div class="md-container">
  <aside class="md-sidebar md-sidebar--primary">
    <nav class="md-nav">
      {nav_html}
    </nav>
  </aside>
  <main class="md-content">
    {breadcrumb}
    <article class="md-content__inner">
      {content}
    </article>
  </main>
  <aside class="md-sidebar md-sidebar--secondary">
    <nav class="md-nav md-nav--toc">
      <div class="md-nav__link md-nav__link--section">Table of contents</div>
      {toc_html}
    </nav>
  </aside>
</div>
<div class="md-overlay" onclick="document.querySelector('.md-sidebar--primary').classList.remove('active');this.classList.remove('active')"></div>
<script>
/* Theme toggle */
function toggle_theme() {{
  var h = document.documentElement;
  var cur = h.getAttribute('data-color-scheme');
  var next = (cur === 'dark') ? 'light' : 'dark';
  if (cur === 'os') {{
    var m = window.matchMedia('(prefers-color-scheme: dark)');
    next = m.matches ? 'light' : 'dark';
  }}
  h.setAttribute('data-color-scheme', next);
  localStorage.setItem('kalico-theme', next);
}}

(function() {{
  var saved = localStorage.getItem('kalico-theme');
  if (saved) document.documentElement.setAttribute('data-color-scheme', saved);
}})();

/* Search */
(function() {{
  var inp = document.querySelector('.md-search__input');
  var out = document.querySelector('.md-search__output');
  var idx = [];
  var lang = inp.dataset.lang || '';

  fetch(inp.dataset.index)
    .then(function(r) {{ return r.json(); }})
    .then(function(d) {{ idx = d; }});

  function esc(s) {{
    return s.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');
  }}

  function highlight(s, q) {{
    if (!q) return esc(s);
    var re = new RegExp('(' + q.replace(/[.*+?^${{}}()|[\]\\\\]/g, '\\\\$&') + ')', 'gi');
    return esc(s).replace(re, '<mark>$1</mark>');
  }}

  inp.addEventListener('input', function() {{
    var q = this.value.trim().toLowerCase();
    if (q.length < 2) {{ out.classList.remove('active'); return; }}
    var words = q.split(/\\s+/);
    var results = idx.filter(function(item) {{
      var t = (item.title + ' ' + item.text).toLowerCase();
      return words.every(function(w) {{ return t.indexOf(w) !== -1; }});
    }});
    // Sort: current language first, then by title match quality
    results.sort(function(a, b) {{
      if (a.lang === lang && b.lang !== lang) return -1;
      if (a.lang !== lang && b.lang === lang) return 1;
      var at = a.title.toLowerCase().indexOf(q);
      var bt = b.title.toLowerCase().indexOf(q);
      if (at === 0 && bt !== 0) return -1;
      if (at !== 0 && bt === 0) return 1;
      return 0;
    }});
    results = results.slice(0, 12);
    if (!results.length) {{
      out.innerHTML = '<div class="md-search__none">No results</div>';
    }} else {{
      out.innerHTML = results.map(function(r) {{
        return '<a href="' + r.url + '" class="md-search__item">' +
          '<span class="md-search__title">' + highlight(r.title, q) + '</span>' +
          '<span class="md-search__text">' + highlight(r.text.slice(0,120), q) + '</span>' +
        '</a>';
      }}).join('');
    }}
    out.classList.add('active');
  }});

  // Keyboard navigation
  inp.addEventListener('keydown', function(e) {{
    var items = out.querySelectorAll('.md-search__item');
    if (!items.length) return;
    var cur = out.querySelector('.md-search__item:focus');
    if (e.key === 'ArrowDown') {{
      e.preventDefault();
      if (cur && cur.nextElementSibling) cur.nextElementSibling.focus();
      else items[0].focus();
    }} else if (e.key === 'ArrowUp') {{
      e.preventDefault();
      if (cur && cur.previousElementSibling) cur.previousElementSibling.focus();
      else items[items.length - 1].focus();
    }} else if (e.key === 'Escape') {{
      out.classList.remove('active');inp.blur();
    }}
  }});

  // Close on outside click
  document.addEventListener('click', function(e) {{
    if (!e.target.closest('.md-search')) out.classList.remove('active');
  }});
}})();

/* Close mobile sidebar on nav click */
document.querySelector('.md-sidebar--primary').addEventListener('click', function(e) {{
  if (e.target.tagName === 'A') {{
    this.classList.remove('active');
    document.querySelector('.md-overlay').classList.remove('active');
  }}
}});
</script>
</body>
</html>"""


# -----------------------------------------------------------------------
# Page builder
# -----------------------------------------------------------------------


def build_page(
    content: str,
    title: str,
    lang: str,
    prefix: str,
    breadcrumb: str = "",
    lang_switcher: str = "",
    nav_html: str = "",
    toc_html: str = "",
) -> str:
    return _PAGE_TEMPLATE.format(
        lang=lang or "en",
        lang_code=lang or "en",
        title=title,
        prefix=prefix,
        content=content,
        breadcrumb=breadcrumb,
        lang_switcher=lang_switcher,
        nav_html=nav_html,
        toc_html=toc_html,
    )


# -----------------------------------------------------------------------
# Index page builder
# -----------------------------------------------------------------------

_INDEX_DESC_RE = re.compile(r"^##\s+(.+)$", re.MULTILINE)


def build_index(
    doc_subdir: Path,
    lang: str,
    prefix: str,
    available_langs: list[str],
    nav_html: str,
    lang_dir_map: dict[str, str],
) -> str:
    """Build an index page listing all markdown files in the directory."""
    items: list[str] = []
    if doc_subdir.is_dir():
        for entry in sorted(doc_subdir.iterdir()):
            if entry.suffix != ".md" or entry.name.startswith("."):
                continue
            title = entry.stem.replace("_", " ")
            desc = ""
            try:
                text = entry.read_text(encoding="utf-8")
                m = _INDEX_TITLE_RE.search(text)
                if m:
                    title = m.group(1)
                m = _INDEX_DESC_RE.search(text)
                if m:
                    desc = m.group(1)
            except Exception:
                pass
            url = f"/{prefix}{entry.stem}.html" if prefix else f"/{entry.stem}.html"
            items.append(
                f'<li><a href="{url}"><span class="title">{title}</span>'
                f'<span class="desc">{desc or entry.name}</span></a></li>'
            )

    if not items:
        return build_page(
            content=(
                '<div class="no-content"><h2>No documents found</h2>'
                f"<p>Place .md files in <code>docs/{prefix}</code></p></div>"
            ),
            title="Index",
            lang=lang or "en",
            prefix=prefix,
            lang_switcher=build_lang_switcher(lang, available_langs, prefix),
            nav_html=nav_html,
        )

    return build_page(
        content='<ul class="file-list">' + "".join(items) + "</ul>",
        title="Documentation Index",
        lang=lang or "en",
        prefix=prefix,
        lang_switcher=build_lang_switcher(lang, available_langs, prefix),
        nav_html=nav_html,
    )


# -----------------------------------------------------------------------
# HTTP request handler
# -----------------------------------------------------------------------


class DocsHandler(http.server.BaseHTTPRequestHandler):
    server_docs_dir: Path = DOCS_DIR
    server_languages: list[str] = []
    server_lang_dirs: dict[str, str] = {}
    server_nav: list[dict[str, Any]] = []
    server_lang_navs: dict[str, list[dict[str, Any]]] = {}

    def _get_nav(self, lang: str) -> list[dict[str, Any]]:
        """Get the navigation tree for the given language code."""
        if not lang:
            return self.server_nav
        return self.server_lang_navs.get(lang, self.server_nav)

    def _get_lang_dir(self, lang: str) -> str:
        if not lang:
            return ""
        return self.server_lang_dirs.get(lang, lang)

    def log_message(self, format: str, *args: object) -> None:
        print(f"[{self.address_string()}] {format % args}")

    def do_GET(self) -> None:  # noqa: N802
        parsed = urlparse(self.path)
        path = unquote(parsed.path.lstrip("/"))

        # Search index endpoint
        if path == "search_index.json":
            self._serve_json(SEARCH_INDEX)
            return

        # Serve static assets
        if self._serve_static(path):
            return

        # Root -> index
        if path == "":
            self._serve_index("", "")
            return

        # Language root (e.g., /zh/ or /zh)
        if path in self.server_languages or f"{path}/" in [
            f"{lc}/" for lc in self.server_languages
        ]:
            lang = path.rstrip("/")
            self._serve_index(lang, f"{lang}/")
            return

        # Path under a language subdirectory
        for lang in self.server_languages:
            prefix = f"{lang}/"
            if path.startswith(prefix):
                subpath = path[len(prefix):]
                return self._try_serve_md(subpath, lang, prefix)

        # Default: serve from docs root (English)
        self._try_serve_md(path, "", "")

    def _serve_json(self, data: object) -> None:
        body = json.dumps(data, ensure_ascii=False).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _serve_static(self, path: str) -> bool:
        static_path = self.server_docs_dir / path
        if not static_path.is_file():
            parts = path.split("/", 1)
            if len(parts) > 1 and parts[0] in self.server_lang_dirs:
                alt = self.server_docs_dir / self.server_lang_dirs[parts[0]] / parts[1]
                if alt.is_file():
                    static_path = alt
        if not static_path.is_file():
            parts = path.split("/", 1)
            if len(parts) > 1 and parts[0] in self.server_languages:
                root_path = self.server_docs_dir / parts[1]
                if root_path.is_file():
                    static_path = root_path
        if not static_path.is_file():
            return False
        ctype, _ = mimetypes.guess_type(str(static_path))
        if ctype is None:
            ctype = "application/octet-stream"
        self.send_response(200)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(static_path.stat().st_size))
        self.end_headers()
        with open(static_path, "rb") as f:
            self.wfile.write(f.read())
        return True

    def _try_serve_md(self, subpath: str, lang: str, prefix: str) -> None:
        lang_dir = self._get_lang_dir(lang)
        file_stem = subpath
        if file_stem.endswith(".html"):
            file_stem = file_stem[:-5]
        if file_stem.endswith("/") or file_stem == "":
            sub_dir = self.server_docs_dir / lang_dir / file_stem if lang else self.server_docs_dir / file_stem
            if sub_dir.is_dir():
                self._serve_index(lang, (prefix + file_stem).rstrip("/") + "/", file_stem)
                return
            self._send_404()
            return

        md_file = self.server_docs_dir / lang_dir / f"{file_stem}.md"
        if not md_file.is_file():
            if lang:
                md_file = self.server_docs_dir / f"{file_stem}.md"
            if not md_file.is_file():
                self._send_404()
                return

        try:
            raw = md_file.read_text(encoding="utf-8")
        except Exception:
            self._send_500()
            return

        title = file_stem.replace("_", " ")
        m = _INDEX_TITLE_RE.search(raw)
        if m:
            title = m.group(1)

        body = md_to_html(raw, prefix.rstrip("/"))
        toc_html = build_toc_html(body)
        current_path = self.path.rstrip("/")
        nav_html = build_nav_html(self._get_nav(lang), current_path, prefix.rstrip("/"))
        breadcrumb = build_breadcrumb([("Home", "/" + prefix.rstrip("/")), (title, "")])

        html = build_page(
            content=body,
            title=title,
            lang=lang or "en",
            prefix=prefix,
            breadcrumb=breadcrumb,
            lang_switcher=build_lang_switcher(
                lang, self.server_languages, f"{prefix}{file_stem}.html"
            ),
            nav_html=nav_html,
            toc_html=toc_html,
        )
        self._send_html(html)

    def _serve_index(self, lang: str, prefix: str, subdir: str = "") -> None:
        lang_dir = self._get_lang_dir(lang)
        doc_dir = (
            self.server_docs_dir / lang_dir / subdir
            if lang
            else self.server_docs_dir / subdir
        )
        nav_html = build_nav_html(self._get_nav(lang), self.path.rstrip("/"), prefix.rstrip("/"))
        html = build_index(
            doc_dir, lang, prefix, self.server_languages, nav_html, self.server_lang_dirs
        )
        self._send_html(html)

    def _send_html(self, content: str) -> None:
        data = content.encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def _send_404(self) -> None:
        nav_html = build_nav_html(self.server_nav, self.path.rstrip("/"), "")
        page = build_page(
            content="<h1>404</h1><p>Page not found.</p>",
            title="Not Found",
            lang="en",
            prefix="",
            nav_html=nav_html,
        )
        data = page.encode("utf-8")
        self.send_response(404)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def _send_500(self) -> None:
        self.send_response(500)
        self.send_header("Content-Type", "text/plain")
        self.end_headers()
        self.wfile.write(b"500 Internal Server Error")


# -----------------------------------------------------------------------
# Main
# -----------------------------------------------------------------------

DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 8800


def main() -> None:
    global SEARCH_INDEX

    parser = argparse.ArgumentParser(
        description="Kalico Documentation Server with i18n support"
    )
    parser.add_argument(
        "--host", default=DEFAULT_HOST, help=f"Bind address (default: {DEFAULT_HOST})"
    )
    parser.add_argument(
        "--port", type=int, default=DEFAULT_PORT, help=f"Port (default: {DEFAULT_PORT})"
    )
    args = parser.parse_args()

    if not DOCS_DIR.is_dir():
        print(f"ERROR: docs directory not found at {DOCS_DIR}", file=sys.stderr)
        sys.exit(1)

    languages, lang_dirs = detect_languages()
    nav = parse_nav()
    SEARCH_INDEX = build_search_index(lang_dirs)

    # Build translated navigation for each language
    lang_navs: dict[str, list[dict[str, Any]]] = {}
    for lc, ld in lang_dirs.items():
        lang_navs[lc] = build_translated_nav(nav, lc, ld)

    DocsHandler.server_docs_dir = DOCS_DIR
    DocsHandler.server_languages = languages
    DocsHandler.server_lang_dirs = lang_dirs
    DocsHandler.server_nav = nav
    DocsHandler.server_lang_navs = lang_navs

    server = http.server.HTTPServer((args.host, args.port), DocsHandler)

    print(f"Kalico Docs Server starting at http://{args.host}:{args.port}")
    print(f"   Serving: {DOCS_DIR}")
    print(f"   Search index: {len(SEARCH_INDEX)} pages indexed")
    if languages:
        detected = ", ".join(get_lang_name(lc) for lc in languages)
        print(f"   Languages detected: {detected}")
    else:
        print("   No additional languages detected.")
        print("   Add translations in docs/<lang_code>/ or docs/i18n/ subdirectories.")
    print("   Press Ctrl+C to stop.")

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down.")
        server.server_close()


if __name__ == "__main__":
    main()
