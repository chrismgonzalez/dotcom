#!/usr/bin/env python3
"""
Static site builder: markdown/ -> dist/
Posts:  posts/*.md    -> dist/posts/<slug>/index.html
About:  about/index.md -> dist/about/index.html
Index:  auto-generated  -> dist/index.html
"""

import os
import re
import shutil
from datetime import datetime
from pathlib import Path

import markdown as md_lib

ROOT = Path(__file__).parent
POSTS_DIR = ROOT / "posts"
ABOUT_DIR = ROOT / "about"
CV_DIR = ROOT / "cv"
DIST_DIR = ROOT / "dist"
STYLES_SRC = ROOT / "src" / "styles" / "main.css"
STATIC_SRC = ROOT / "static"

SITE_TITLE = "ChrisDoesCloud"
CV_PUBLISHED = False  # set in build() based on draft flag
SITE_DESC = "Ramblings of a clown architect"
BASE_URL = ""  # empty = relative paths; set to https://chrisdoescloud.com for prod


# ── Frontmatter ──────────────────────────────────────────────────────────────

def parse_frontmatter(text: str) -> tuple[dict, str]:
    """Split YAML-ish frontmatter from body. Returns (meta, body)."""
    meta = {}
    if not text.startswith("---"):
        return meta, text
    end = text.index("---", 3)
    fm_block = text[3:end].strip()
    body = text[end + 3:].lstrip("\n")
    for line in fm_block.splitlines():
        if ":" in line:
            key, _, val = line.partition(":")
            meta[key.strip()] = val.strip().strip('"').strip("'")
    return meta, body


# ── Markdown -> HTML ──────────────────────────────────────────────────────────

_md = md_lib.Markdown(extensions=["fenced_code", "tables", "nl2br"])

def to_html(text: str) -> str:
    _md.reset()
    return _md.convert(text)


# ── Date parsing ──────────────────────────────────────────────────────────────

def parse_date(raw: str) -> datetime:
    for fmt in ("%Y-%m-%dT%H:%M:%S%z", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%d"):
        try:
            return datetime.strptime(raw[:len(fmt) + 2].rstrip("Z"), fmt.rstrip("z"))
        except ValueError:
            continue
    return datetime.min


def fmt_date(dt: datetime) -> str:
    return dt.strftime("%B %-d, %Y")


# ── Templates ─────────────────────────────────────────────────────────────────

def _shell(title: str, canonical: str, body: str, active_nav: str = "") -> str:
    def nav_link(href: str, label: str, key: str) -> str:
        cls = ' class="active"' if key == active_nav else ""
        return f'<a href="{BASE_URL}{href}"{cls}>{label}</a>'

    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{title + " — " + SITE_TITLE if title != SITE_TITLE else SITE_TITLE}</title>
  <meta name="description" content="{SITE_DESC}">
  <link rel="canonical" href="{BASE_URL}{canonical}">
  <link rel="stylesheet" href="{BASE_URL}/styles/main.css">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
</head>
<body>
  <header>
    <div class="site-header-inner">
      <a class="site-title" href="{BASE_URL}/">{SITE_TITLE}</a>
      <nav>
        {nav_link("/", "Writing", "index")}
        {nav_link("/about.html", "About", "about")}
        {nav_link("/cv.html", "CV", "cv") if CV_PUBLISHED else ""}
      </nav>
    </div>
  </header>
  <main class="site-wrapper">
    {body}
  </main>
  <footer>
    <div class="site-footer-inner">
      <p>© 2026 ChrisDoesCloud</p>
      <p>
        <a href="https://github.com/chrismgonzalez" rel="noopener">GitHub</a>
        <a href="https://linkedin.com/in/chrismgonzalez" rel="noopener">LinkedIn</a>
      </p>
    </div>
  </footer>
</body>
</html>"""


def render_index(posts: list[dict]) -> str:
    items = ""
    for p in posts:
        excerpt = p.get("excerpt", "")
        items += f"""
    <li class="post-list-item">
      <p class="post-meta">{p["date_fmt"]}</p>
      <h2 class="post-list-title"><a href="{BASE_URL}/posts/{p["slug"]}.html">{p["title"]}</a></h2>
      {"<p class='post-excerpt'>" + excerpt + "</p>" if excerpt else ""}
    </li>"""

    body = f"""
    <ul class="post-list">{items}
    </ul>"""
    return _shell(SITE_TITLE, "/", body, active_nav="index")


def render_post(meta: dict, html_body: str, slug: str) -> str:
    title = meta.get("title", slug)
    date_fmt = fmt_date(parse_date(meta.get("date", ""))) if meta.get("date") else ""
    date_line = f'<p class="post-meta">{date_fmt}</p>' if date_fmt else ""
    body = f"""
    <a class="back-link" href="{BASE_URL}/">← All posts</a>
    <article>
      <header class="post-header">
        {date_line}
        <h1>{title}</h1>
      </header>
      <div class="prose">
        {html_body}
      </div>
    </article>"""
    return _shell(title, f"/posts/{slug}.html", body)


def render_about(html_body: str) -> str:
    body = f"""
    <p class="page-eyebrow">About</p>
    <h1 class="page-title">Hey, I'm Chris.</h1>
    <div class="prose">
      {html_body}
    </div>"""
    return _shell("About", "/about.html", body, active_nav="about")


def render_cv(html_body: str) -> str:
    body = f"""
    <div class="cv">
      {html_body}
    </div>"""
    return _shell("CV", "/cv.html", body, active_nav="cv")


# ── Excerpt extraction ────────────────────────────────────────────────────────

def make_excerpt(body: str, words: int = 30) -> str:
    text = re.sub(r"#+\s.*", "", body)
    text = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", text)
    text = re.sub(r"`[^`]+`", "", text)
    text = re.sub(r"\*+", "", text)
    tokens = text.split()[:words]
    return " ".join(tokens).rstrip(".,;:") + "…" if tokens else ""


# ── Build ─────────────────────────────────────────────────────────────────────

def build():
    # Clean dist
    if DIST_DIR.exists():
        shutil.rmtree(DIST_DIR)
    DIST_DIR.mkdir()

    # Copy styles
    styles_dir = DIST_DIR / "styles"
    styles_dir.mkdir()
    shutil.copy(STYLES_SRC, styles_dir / "main.css")

    # Copy static assets if present
    if STATIC_SRC.exists():
        for item in STATIC_SRC.iterdir():
            dest = DIST_DIR / item.name
            if item.is_dir():
                shutil.copytree(item, dest)
            else:
                shutil.copy(item, dest)

    posts = []

    # Build posts
    posts_out = DIST_DIR / "posts"
    posts_out.mkdir()

    for md_file in sorted(POSTS_DIR.glob("*.md"), reverse=True):
        text = md_file.read_text(encoding="utf-8")
        meta, body = parse_frontmatter(text)

        if meta.get("draft", "false").lower() == "true":
            continue

        slug = md_file.stem
        html_body = to_html(body)
        dt = parse_date(meta.get("date", ""))

        (posts_out / f"{slug}.html").write_text(
            render_post(meta, html_body, slug), encoding="utf-8"
        )

        posts.append({
            "slug": slug,
            "title": meta.get("title", slug),
            "date": dt,
            "date_fmt": fmt_date(dt) if meta.get("date") else "",
            "excerpt": make_excerpt(body),
        })
        print(f"  post: /posts/{slug}.html")

    # Sort posts newest-first
    posts.sort(key=lambda p: p["date"], reverse=True)

    # Build about
    about_md = ABOUT_DIR / "index.md"
    if about_md.exists():
        text = about_md.read_text(encoding="utf-8")
        _, body = parse_frontmatter(text)
        (DIST_DIR / "about.html").write_text(render_about(to_html(body)), encoding="utf-8")
        print("  page: /about.html")

    # Build CV
    global CV_PUBLISHED
    cv_md = CV_DIR / "index.md"
    if cv_md.exists():
        text = cv_md.read_text(encoding="utf-8")
        meta, body = parse_frontmatter(text)
        if meta.get("draft", "false").lower() != "true":
            CV_PUBLISHED = True
            (DIST_DIR / "cv.html").write_text(render_cv(to_html(body)), encoding="utf-8")
            print("  page: /cv.html")
        else:
            print("  skip: /cv.html (draft)")

    # Build index
    (DIST_DIR / "index.html").write_text(render_index(posts), encoding="utf-8")
    print("  page: /")

    print(f"\nBuild complete -> {DIST_DIR}/")


if __name__ == "__main__":
    build()
