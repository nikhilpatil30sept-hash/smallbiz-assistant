"""Load documents and split them into overlapping, heading-aware chunks."""
import re
from dataclasses import dataclass, field
from pathlib import Path

import config


@dataclass
class Chunk:
    id: str
    text: str
    metadata: dict = field(default_factory=dict)


def clean_title(text: str) -> str:
    """'6. Confirm if you need to charge HST' -> 'Confirm if you need to charge HST'.
    Step numbers made the model talk about 'section 6', so we drop them."""
    return re.sub(r"^\s*\d+\.\s*", "", text).strip()


def parse_front_matter(raw: str) -> tuple[dict, str]:
    """Read the tiny '---\\nkey: value\\n---' header written by fetch_sources.py."""
    if not raw.startswith("---\n"):
        return {}, raw
    end = raw.find("\n---", 4)
    if end == -1:
        return {}, raw
    meta = {}
    for line in raw[4:end].splitlines():
        if ":" in line:
            k, v = line.split(":", 1)
            meta[k.strip()] = v.strip()
    return meta, raw[end + 4 :].lstrip("\n")


def load_file(path: Path) -> tuple[dict, str]:
    suffix = path.suffix.lower()
    if suffix in (".md", ".txt"):
        meta, text = parse_front_matter(path.read_text(encoding="utf-8", errors="ignore"))
    elif suffix == ".pdf":
        from pypdf import PdfReader

        pages = [(p.extract_text() or "") for p in PdfReader(str(path)).pages]
        meta, text = {}, "\n\n".join(pages)
    else:
        raise ValueError(f"unsupported file type: {path.name}")
    meta.setdefault("title", path.stem.replace("-", " ").replace("_", " ").title())
    meta["title"] = clean_title(meta["title"])
    meta.setdefault("source_url", "")
    meta.setdefault("license", "user_supplied")
    meta["file"] = path.name
    return meta, text


def _split_sections(text: str) -> list[tuple[str, str]]:
    """Split on markdown headings -> [(heading_path, body)]."""
    sections: list[tuple[str, str]] = []
    stack: list[tuple[int, str]] = []
    buf: list[str] = []

    def flush():
        body = "\n".join(buf).strip()
        if body:
            sections.append((" > ".join(h for _, h in stack), body))
        buf.clear()

    for line in text.splitlines():
        m = re.match(r"^(#{1,6})\s+(.*)", line)
        if m:
            flush()
            level = len(m.group(1))
            while stack and stack[-1][0] >= level:
                stack.pop()
            stack.append((level, m.group(2).strip()))
        else:
            buf.append(line)
    flush()
    return sections


def _pack(body: str, size: int, overlap: int) -> list[str]:
    """Pack paragraphs into ~size-char pieces, carrying a small overlap forward."""
    paragraphs = [p.strip() for p in re.split(r"\n\s*\n", body) if p.strip()]
    pieces: list[str] = []
    current = ""
    for para in paragraphs:
        # Break up a single huge paragraph on sentence boundaries.
        parts = [para] if len(para) <= size else re.split(r"(?<=[.!?])\s+", para)
        for part in parts:
            if current and len(current) + len(part) + 2 > size:
                pieces.append(current)
                current = current[-overlap:] if overlap else ""
            current = (current + "\n\n" + part).strip() if current else part
    if current:
        pieces.append(current)
    return pieces


def chunk_document(meta: dict, text: str) -> list[Chunk]:
    chunks: list[Chunk] = []
    n = 0
    for heading, body in _split_sections(text):
        for piece in _pack(body, config.CHUNK_CHARS, config.CHUNK_OVERLAP):
            # Don't repeat the page title when the heading path is just that title.
            section = " > ".join(clean_title(p) for p in heading.split(" > "))
            if section == meta["title"]:
                section = ""
            prefix = f"[{meta['title']}" + (f" > {section}" if section else "") + "]\n"
            chunks.append(
                Chunk(
                    id=f"{meta['file']}::{n}",
                    text=prefix + piece,
                    metadata={**meta, "section": section},
                )
            )
            n += 1
    return chunks


def load_all_chunks() -> list[Chunk]:
    files: list[Path] = []
    for d in (config.WEB_DIR, config.DOCS_DIR):
        if d.exists():
            files += [p for p in sorted(d.rglob("*")) if p.suffix.lower() in (".md", ".txt", ".pdf")]
    chunks: list[Chunk] = []
    for path in files:
        try:
            meta, text = load_file(path)
            chunks += chunk_document(meta, text)
        except Exception as e:
            print(f"skipping {path.name}: {e}")
    return chunks
