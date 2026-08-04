#!/usr/bin/env python3
"""Validate blog post front matter.

Runs in CI on every pull request so that a missing summary or a broken image
reference is caught before review rather than after deploy. Run it locally the
same way CI does:

    python3 scripts/check_posts.py

Exits non-zero if any post has an error. Warnings do not fail the build.
"""

from __future__ import annotations

import argparse
import datetime as dt
import pathlib
import re
import sys

try:
    import yaml
except ImportError:  # pragma: no cover
    sys.exit("error: PyYAML is required -- pip install pyyaml")

POSTS = pathlib.Path("content/posts")
DIR_NAME = re.compile(r"^\d{4}-\d{2}-\d{2}-[a-z0-9]+(?:-[a-z0-9]+)*$")
SUMMARY_MAX = 240
TITLE_MAX = 90
REQUIRED = ("title", "date", "authors", "summary")

GREEN, RED, YELLOW, DIM, RESET = "\033[32m", "\033[31m", "\033[33m", "\033[2m", "\033[0m"


class Report:
    def __init__(self) -> None:
        self.errors: list[str] = []
        self.warnings: list[str] = []

    def error(self, where: pathlib.Path, msg: str) -> None:
        self.errors.append(f"{where}: {msg}")

    def warn(self, where: pathlib.Path, msg: str) -> None:
        self.warnings.append(f"{where}: {msg}")


def split_front_matter(text: str) -> str | None:
    if not text.startswith("---"):
        return None
    end = text.find("\n---", 3)
    if end == -1:
        return None
    return text[3:end]


def check_post(index: pathlib.Path, report: Report) -> None:
    directory = index.parent
    rel = index.relative_to(pathlib.Path.cwd()) if index.is_absolute() else index

    if not DIR_NAME.match(directory.name):
        report.error(
            rel,
            f"directory {directory.name!r} should be named YYYY-MM-DD-lowercase-slug",
        )

    raw = split_front_matter(index.read_text(encoding="utf-8"))
    if raw is None:
        report.error(rel, "missing YAML front matter delimited by ---")
        return

    try:
        meta = yaml.safe_load(raw) or {}
    except yaml.YAMLError as exc:
        report.error(rel, f"front matter is not valid YAML: {exc}")
        return

    if not isinstance(meta, dict):
        report.error(rel, "front matter must be a mapping")
        return

    for key in REQUIRED:
        if key not in meta or meta[key] in (None, "", [], {}):
            report.error(rel, f"missing required front matter key {key!r}")

    title = meta.get("title")
    if isinstance(title, str) and len(title) > TITLE_MAX:
        report.warn(rel, f"title is {len(title)} characters; under {TITLE_MAX} reads better in cards")

    summary = meta.get("summary")
    if isinstance(summary, str):
        if len(summary) > SUMMARY_MAX:
            report.error(rel, f"summary is {len(summary)} characters; the limit is {SUMMARY_MAX}")
        if "\n" in summary:
            report.error(rel, "summary must be a single line")
        if summary and not summary.rstrip().endswith((".", "!", "?")):
            report.warn(rel, "summary reads better as a complete sentence ending in punctuation")
    elif summary is not None:
        report.error(rel, "summary must be a string")

    authors = meta.get("authors")
    if authors is not None:
        if not isinstance(authors, list) or not all(isinstance(a, str) and a.strip() for a in authors):
            report.error(rel, "authors must be a non-empty list of names")
        elif any(a.strip().lower() in {"todo", "your name or team", ""} for a in authors):
            report.error(rel, "authors still contains the template placeholder")

    date = meta.get("date")
    if isinstance(date, (dt.date, dt.datetime)):
        prefix = directory.name[:10]
        if prefix != date.strftime("%Y-%m-%d"):
            report.warn(rel, f"date {date} does not match the directory prefix {prefix}")
    elif date is not None:
        report.error(rel, f"date must be an unquoted YYYY-MM-DD value, got {date!r}")

    tags = meta.get("tags")
    if tags is not None:
        if not isinstance(tags, list):
            report.error(rel, "tags must be a list")
        else:
            for tag in tags:
                if not isinstance(tag, str) or not tag.strip():
                    report.error(rel, "tags must not contain empty entries")
                elif tag != tag.lower():
                    report.warn(rel, f"tag {tag!r} should be lowercase so archives do not split")

    image = meta.get("image")
    if isinstance(image, str) and image and not image.startswith(("http://", "https://", "/")):
        if not (directory / image).exists():
            report.error(rel, f"image {image!r} does not exist in {directory.name}/")

    if meta.get("draft") is True:
        report.warn(rel, "still marked draft: true, so it will not publish")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("paths", nargs="*", help="specific index.md files to check")
    args = parser.parse_args()

    if args.paths:
        posts = [pathlib.Path(p) for p in args.paths]
    else:
        if not POSTS.is_dir():
            print(f"{RED}error{RESET}: {POSTS} not found -- run this from the repository root", file=sys.stderr)
            return 1
        posts = sorted(POSTS.glob("*/index.md"))

    stray = sorted(p for p in POSTS.glob("*.md") if p.name != "_index.md") if POSTS.is_dir() else []

    report = Report()
    for path in posts:
        check_post(path, report)
    for path in stray:
        report.error(path, "posts must be a directory with an index.md, not a loose markdown file")

    print(f"checked {len(posts)} post{'s' if len(posts) != 1 else ''}")

    for warning in report.warnings:
        print(f"{YELLOW}warning{RESET} {warning}")
    for error in report.errors:
        print(f"{RED}error{RESET}   {error}")

    if report.errors:
        print(f"\n{RED}{len(report.errors)} error(s){RESET}. See CONTRIBUTING.md for the front matter reference.")
        return 1

    suffix = f" {DIM}({len(report.warnings)} warning(s)){RESET}" if report.warnings else ""
    print(f"{GREEN}all posts valid{RESET}{suffix}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
