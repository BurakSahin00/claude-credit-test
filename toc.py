#!/usr/bin/env python3
"""Generate a nested table of contents from the headings of a Markdown file."""
import argparse
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


def build_toc(text, max_depth=None, numbered=False):
    """Build a nested Markdown list; depth follows heading nesting, even if levels are skipped.

    max_depth keeps only headings of level <= max_depth; numbered uses "1." markers
    (restarting under each parent) instead of "-" bullets.
    """
    lines = []
    stack = []  # heading levels of the currently open ancestors
    counters = []  # per-depth item counters, used when numbered
    seen = {}
    for level, title in extract_headings(text):
        # Anchors are assigned before filtering so they match the rendered document.
        anchor = slugify(title, seen)
        if max_depth is not None and level > max_depth:
            continue
        while stack and stack[-1] >= level:
            stack.pop()
        stack.append(level)
        depth = len(stack) - 1
        del counters[depth + 1:]
        if depth == len(counters):
            counters.append(0)
        counters[depth] += 1
        marker = f"{counters[depth]}." if numbered else "-"
        indent = ("   " if numbered else "  ") * depth
        lines.append(f"{indent}{marker} [{title}](#{anchor})")
    return "\n".join(lines)


def _positive_int(value):
    try:
        n = int(value)
    except ValueError:
        raise argparse.ArgumentTypeError(f"invalid int value: {value!r}")
    if n < 1:
        raise argparse.ArgumentTypeError("must be >= 1")
    return n


def _parser():
    p = argparse.ArgumentParser(
        prog="toc.py",
        description="Generate a table of contents from the headings of a Markdown file.",
    )
    p.add_argument("file", help="Markdown file to read")
    p.add_argument("--max-depth", type=_positive_int, metavar="N",
                   help="include at most N heading levels")
    p.add_argument("--output", metavar="FILE.md",
                   help="write the result to FILE.md instead of stdout")
    p.add_argument("--numbered", action="store_true",
                   help="emit a numbered list instead of bullets")
    return p


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    try:
        args = _parser().parse_args(argv)
    except SystemExit as e:
        return e.code
    try:
        with open(args.file, encoding="utf-8") as f:
            text = f.read()
    except OSError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    toc = build_toc(text, max_depth=args.max_depth, numbered=args.numbered)
    if args.output:
        try:
            with open(args.output, "w", encoding="utf-8") as f:
                if toc:
                    f.write(toc + "\n")
        except OSError as e:
            print(f"Error: {e}", file=sys.stderr)
            return 1
    elif toc:
        print(toc)
    return 0


if __name__ == "__main__":
    sys.exit(main())
