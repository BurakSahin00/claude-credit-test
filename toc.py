#!/usr/bin/env python3
"""Generate a nested table of contents from the headings of a Markdown file."""
import re
import sys

HEADING_RE = re.compile(r"^ {0,3}(#{1,3})[ \t]+(.+?)(?:[ \t]+#+)?[ \t]*$")
FENCE_RE = re.compile(r"^ {0,3}(`{3,}|~{3,})")


def extract_headings(text):
    """Return a list of (level, title) for #, ## and ### headings outside code fences."""
    headings = []
    fence = None
    for line in text.splitlines():
        m = FENCE_RE.match(line)
        if m:
            marker = m.group(1)
            if fence is None:
                fence = marker
            elif marker[0] == fence[0] and len(marker) >= len(fence):
                fence = None
            continue
        if fence is not None:
            continue
        m = HEADING_RE.match(line)
        if m:
            headings.append((len(m.group(1)), m.group(2).strip()))
    return headings


def slugify(title, seen):
    """GitHub-style anchor; duplicates get a -1, -2, ... suffix."""
    slug = re.sub(r"[^\w\- ]", "", title.lower()).replace(" ", "-")
    n = seen.get(slug, 0)
    seen[slug] = n + 1
    return slug if n == 0 else f"{slug}-{n}"


def build_toc(text):
    """Build a nested Markdown list; depth follows heading nesting, even if levels are skipped."""
    lines = []
    stack = []  # heading levels of the currently open ancestors
    seen = {}
    for level, title in extract_headings(text):
        while stack and stack[-1] >= level:
            stack.pop()
        stack.append(level)
        lines.append(f"{'  ' * (len(stack) - 1)}- [{title}](#{slugify(title, seen)})")
    return "\n".join(lines)


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    if len(argv) != 1:
        print("Usage: python toc.py dosya.md", file=sys.stderr)
        return 2
    try:
        with open(argv[0], encoding="utf-8") as f:
            text = f.read()
    except OSError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    toc = build_toc(text)
    if toc:
        print(toc)
    return 0


if __name__ == "__main__":
    sys.exit(main())
