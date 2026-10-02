"""Download the pages listed in sources.yaml and save them as clean Markdown files
under data/web/. Each file starts with a small header (source URL, title, licence,
fetch date) that the ingestion step turns into citation metadata.

Usage:
    python fetch_sources.py                     # everything in sources.yaml
    python fetch_sources.py --license ogl_ontario   # only commercially-usable pages
"""
import argparse
import datetime as dt
import re
import sys
import time
from urllib.parse import urlparse

import requests
import yaml
from bs4 import BeautifulSoup, NavigableString

import config

USER_AGENT = "smallbiz-assistant-prototype/0.1 (personal research; polite crawler)"
DELAY_SECONDS = 2.0  # be gentle with government servers

DROP_TAGS = ["script", "style", "nav", "footer", "aside", "form", "noscript", "header", "svg"]


def html_to_markdown(html: str) -> tuple[str, str]:
    """Return (title, markdown) for the main content of a page."""
    soup = BeautifulSoup(html, "html.parser")
    title = (soup.find("h1") or soup.find("title"))
    title = title.get_text(" ", strip=True) if title else "Untitled"

    root = soup.find("main") or soup.body or soup
    for tag in root.find_all(DROP_TAGS):
        tag.decompose()

    lines: list[str] = []
    seen: set[str] = set()  # ontario.ca repeats headings and lead paragraphs; keep the first copy

    def add_once(text: str) -> bool:
        key = re.sub(r"\s+", " ", text).strip().lower()
        if key in seen:
            return False
        seen.add(key)
        return True

    def walk(node):
        for child in node.children:
            if isinstance(child, NavigableString):
                continue
            name = child.name
            if name and re.fullmatch(r"h[1-6]", name):
                level = int(name[1])
                text = child.get_text(" ", strip=True)
                if text and add_once(text):
                    lines.append("\n" + "#" * level + " " + text + "\n")
            elif name == "p":
                text = child.get_text(" ", strip=True)
                if text and add_once(text):
                    lines.append(text + "\n")
            elif name in ("ul", "ol"):
                for i, li in enumerate(child.find_all("li", recursive=False), 1):
                    text = li.get_text(" ", strip=True)
                    if text:
                        bullet = f"{i}." if name == "ol" else "-"
                        lines.append(f"{bullet} {text}")
                lines.append("")
            elif name == "table":
                for row in child.find_all("tr"):
                    cells = [c.get_text(" ", strip=True) for c in row.find_all(["th", "td"])]
                    if any(cells):
                        lines.append("| " + " | ".join(cells) + " |")
                lines.append("")
            else:
                walk(child)

    walk(root)
    text = "\n".join(lines)
    text = re.sub(r"\n{3,}", "\n\n", text).strip()
    return title, text


def slug_for(url: str) -> str:
    p = urlparse(url)
    slug = re.sub(r"[^a-z0-9]+", "-", (p.netloc + p.path).lower()).strip("-")
    return slug[:120]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--license", help="only fetch sources with this license value")
    args = ap.parse_args()

    sources = yaml.safe_load((config.ROOT / "sources.yaml").read_text())["sources"]
    if args.license:
        sources = [s for s in sources if s["license"] == args.license]

    config.WEB_DIR.mkdir(parents=True, exist_ok=True)
    today = dt.date.today().isoformat()
    ok, failed = 0, []

    for i, src in enumerate(sources):
        url = src["url"]
        try:
            resp = requests.get(url, headers={"User-Agent": USER_AGENT}, timeout=30)
            resp.raise_for_status()
            title, body = html_to_markdown(resp.text)
            if len(body) < 200:
                raise ValueError("page text too short - layout may have changed")
            header = (
                f"---\nsource_url: {url}\ntitle: {title}\n"
                f"license: {src['license']}\nfetched: {today}\n---\n\n"
            )
            if not body.lstrip().startswith("# "):  # page had no h1 inside <main>
                body = f"# {title}\n\n{body}"
            (config.WEB_DIR / f"{slug_for(url)}.md").write_text(header + body + "\n")
            print(f"OK    {url}  ({len(body):,} chars)")
            ok += 1
        except Exception as e:  # keep going; report at the end
            print(f"FAIL  {url}  -> {e}")
            failed.append(url)
        if i < len(sources) - 1:
            time.sleep(DELAY_SECONDS)

    print(f"\nFetched {ok}/{len(sources)} pages into {config.WEB_DIR}")
    if failed:
        print("Failed:\n  " + "\n  ".join(failed))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
