#!/usr/bin/env python3
"""Check the built site for internal links that point at nothing.

Cross-references between posts are the easiest thing for an author to get wrong
and the hardest for a reviewer to spot, so CI resolves every internal href and
src against public/ after the build. External URLs are not fetched.

Usage: python3 scripts/check_links.py [public_dir]
"""

from __future__ import annotations

import html.parser
import pathlib
import sys
import urllib.parse

SKIP_SCHEMES = ("http://", "https://", "mailto:", "tel:", "data:", "javascript:", "#")
ATTRS = {"a": "href", "link": "href", "img": "src", "script": "src", "source": "src", "iframe": "src"}

RED, GREEN, RESET = "\033[31m", "\033[32m", "\033[0m"


class LinkCollector(html.parser.HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.links: list[tuple[str, str]] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        wanted = ATTRS.get(tag)
        if not wanted:
            return
        for name, value in attrs:
            if name == wanted and value:
                self.links.append((tag, value))


def resolve(root: pathlib.Path, page: pathlib.Path, target: str) -> pathlib.Path:
    """Map a URL onto a path inside the output directory. Both root and page are
    absolute, so the result is comparable against root without further work."""
    path = urllib.parse.urlsplit(target).path
    if not path:
        return page
    if path.startswith("/"):
        return (root / path.lstrip("/")).resolve()
    return (page.parent / path).resolve()


def exists(root: pathlib.Path, candidate: pathlib.Path) -> bool:
    try:
        candidate.relative_to(root)
    except ValueError:
        # Escaped the output directory entirely; that is always a broken link.
        return False
    # Hugo emits pretty URLs, so a link to /posts/foo/ is a directory holding an
    # index.html. Anything else must exist as a file.
    if candidate.is_dir():
        return (candidate / "index.html").exists()
    return candidate.exists()


def main() -> int:
    root = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else "public")
    if not root.is_dir():
        print(f"{RED}error{RESET}: {root} not found -- run `hugo` first", file=sys.stderr)
        return 1
    root = root.resolve()

    pages = sorted(root.rglob("*.html"))
    broken: list[str] = []
    checked = 0

    for page in pages:
        collector = LinkCollector()
        collector.feed(page.read_text(encoding="utf-8", errors="replace"))
        for tag, target in collector.links:
            if target.startswith(SKIP_SCHEMES) or not target.strip():
                continue
            checked += 1
            if not exists(root, resolve(root, page, target)):
                broken.append(f"{page.relative_to(root)}: <{tag}> -> {target}")

    print(f"checked {checked} internal links across {len(pages)} pages")
    for item in broken:
        print(f"{RED}broken{RESET}  {item}")

    if broken:
        print(f"\n{RED}{len(broken)} broken internal link(s){RESET}")
        return 1
    print(f"{GREEN}no broken internal links{RESET}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
