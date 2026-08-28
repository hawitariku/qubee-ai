"""
Afaan Oromo Corpus Expansion — News & Wikipedia Sources
========================================================
Scrapes Afaan Oromo text from:
  1. BBC Afaan Oromo   (bbc.com/afaanoromoo)
  2. VOA Afaan Oromo   (voanews.com/z/490)
  3. Oromo Wikipedia   (om.wikipedia.org)

Usage
-----
    # Expand from all sources (recommended first run):
    python scripts/expand_corpus_news.py --all

    # Individual sources:
    python scripts/expand_corpus_news.py --bbc
    python scripts/expand_corpus_news.py --voa
    python scripts/expand_corpus_news.py --wiki

    # Dry-run (scrape but don't write to corpus):
    python scripts/expand_corpus_news.py --all --dry-run

    # Limit pages per source (useful for testing):
    python scripts/expand_corpus_news.py --all --limit 5

Output
------
Text is appended to ../oromo_corpus.txt (relative to this script's directory).
A timestamped report is printed to stdout and optionally saved with --report.

Requirements
------------
    pip install requests beautifulsoup4 lxml
"""

import argparse
import re
import sys
import time
import shutil
from datetime import datetime
from pathlib import Path
from typing import Optional
from urllib.parse import urljoin, urlparse

try:
    import requests
    from bs4 import BeautifulSoup
except ImportError:
    print("ERROR: Install required packages first:")
    print("    pip install requests beautifulsoup4 lxml")
    sys.exit(1)

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

CORPUS_PATH = Path(__file__).parent.parent / "oromo_corpus.txt"

# Polite delay between requests (seconds)
REQUEST_DELAY = 1.5

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (compatible; AfaanOromoCorpusBuilder/1.0; "
        "+https://github.com/qubeessaa-ai)"
    ),
    "Accept-Language": "om, en;q=0.5",
}

# Minimum length of a paragraph to be included (chars)
MIN_PARA_LEN = 60

# Afaan Oromo function words — used to filter out non-Oromo paragraphs
OROMO_MARKERS = {
    "akka", "jedhe", "inni", "isheen", "dha", "kan", "fi", "hin",
    "ni", "jira", "deeme", "dhufe", "mana", "bishaan", "afaan",
    "oromoo", "isin", "isaan", "nuti", "garuu", "yookaan",
}


# ---------------------------------------------------------------------------
# Shared utilities
# ---------------------------------------------------------------------------

def _is_oromo(text: str) -> bool:
    """Heuristic: return True if text looks like Afaan Oromo."""
    words = set(re.findall(r"[a-z']+", text.lower()))
    overlap = words & OROMO_MARKERS
    # At least 2 marker words OR text contains doubled vowels (aa, ee, oo, ii, uu)
    return len(overlap) >= 2 or bool(re.search(r"[aeiou]\1", text.lower()))


def _clean(text: str) -> str:
    """Normalise whitespace and remove reference markers like [1]."""
    text = re.sub(r"\[\d+\]", "", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def _get(url: str, session: requests.Session, retries: int = 3) -> Optional[requests.Response]:
    """GET with retry logic and polite delay."""
    for attempt in range(1, retries + 1):
        try:
            time.sleep(REQUEST_DELAY)
            resp = session.get(url, headers=HEADERS, timeout=20)
            resp.raise_for_status()
            return resp
        except requests.RequestException as exc:
            print(f"    ⚠ Attempt {attempt}/{retries} failed for {url}: {exc}")
            if attempt == retries:
                return None
            time.sleep(REQUEST_DELAY * attempt)
    return None


def _extract_paragraphs(soup: BeautifulSoup, container_selectors: list) -> list[str]:
    """Extract clean Oromo paragraphs from a BeautifulSoup tree."""
    container = None
    for sel in container_selectors:
        container = soup.select_one(sel)
        if container:
            break
    if container is None:
        container = soup

    # Remove non-content elements
    for tag in container.select("script, style, nav, aside, footer, .ad, .advertisement"):
        tag.decompose()

    paragraphs = []
    for p in container.find_all(["p", "li"]):
        text = _clean(p.get_text())
        if len(text) >= MIN_PARA_LEN and _is_oromo(text):
            paragraphs.append(text)
    return paragraphs


# ---------------------------------------------------------------------------
# BBC Afaan Oromo
# ---------------------------------------------------------------------------

BBC_BASE = "https://www.bbc.com"
BBC_INDEX_URL = "https://www.bbc.com/afaanoromoo"
BBC_ARTICLE_SELECTORS = ["article", "#main-content", ".article__body"]


def _bbc_article_links(session: requests.Session, limit: int) -> list[str]:
    """Collect article URLs from BBC Afaan Oromo front page and navigation."""
    links = set()
    pages_to_check = [BBC_INDEX_URL]

    for page_url in pages_to_check:
        resp = _get(page_url, session)
        if not resp:
            continue
        soup = BeautifulSoup(resp.text, "lxml")
        for a in soup.find_all("a", href=True):
            href = a["href"]
            if "/afaanoromoo/" in href and not href.endswith("/afaanoromoo/"):
                full = urljoin(BBC_BASE, href)
                # Only article pages (not tag/topic pages)
                if full.count("/") >= 5:
                    links.add(full.split("?")[0])  # Strip query strings
        if len(links) >= limit:
            break

    return list(links)[:limit]


def scrape_bbc(session: requests.Session, limit: int = 100) -> list[str]:
    """Scrape BBC Afaan Oromo articles. Returns list of paragraph strings."""
    print(f"\n{'─'*55}")
    print(f"📡 BBC Afaan Oromo (limit={limit} articles)")
    print(f"{'─'*55}")

    article_urls = _bbc_article_links(session, limit)
    print(f"   Found {len(article_urls)} article links")

    all_paragraphs: list[str] = []
    seen_paragraphs: set[str] = set()

    for i, url in enumerate(article_urls, 1):
        print(f"   [{i:3d}/{len(article_urls)}] {url}")
        resp = _get(url, session)
        if not resp:
            continue
        soup = BeautifulSoup(resp.text, "lxml")
        paras = _extract_paragraphs(soup, BBC_ARTICLE_SELECTORS)
        new = [p for p in paras if p not in seen_paragraphs]
        seen_paragraphs.update(new)
        all_paragraphs.extend(new)

    print(f"   ✅ BBC total: {len(all_paragraphs)} paragraphs")
    return all_paragraphs


# ---------------------------------------------------------------------------
# VOA Afaan Oromo
# ---------------------------------------------------------------------------

VOA_BASE = "https://www.voanews.com"
# VOA Afaan Oromo section
VOA_INDEX_URLS = [
    "https://www.voanews.com/z/490",
    "https://www.voanews.com/z/490?p=1",
    "https://www.voanews.com/z/490?p=2",
]
VOA_ARTICLE_SELECTORS = [".article-content", ".story-body", "article", "#content"]


def _voa_article_links(session: requests.Session, limit: int) -> list[str]:
    """Collect article URLs from VOA Afaan Oromo section pages."""
    links = set()
    for index_url in VOA_INDEX_URLS:
        resp = _get(index_url, session)
        if not resp:
            continue
        soup = BeautifulSoup(resp.text, "lxml")
        for a in soup.find_all("a", href=True):
            href = a["href"]
            # VOA article URLs typically look like /a/title/N.html
            if re.match(r"^/a/[^/]+/\d+\.html$", href):
                full = urljoin(VOA_BASE, href)
                links.add(full)
        if len(links) >= limit:
            break
    return list(links)[:limit]


def scrape_voa(session: requests.Session, limit: int = 100) -> list[str]:
    """Scrape VOA Afaan Oromo articles. Returns list of paragraph strings."""
    print(f"\n{'─'*55}")
    print(f"📡 VOA Afaan Oromo (limit={limit} articles)")
    print(f"{'─'*55}")

    article_urls = _voa_article_links(session, limit)
    print(f"   Found {len(article_urls)} article links")

    all_paragraphs: list[str] = []
    seen_paragraphs: set[str] = set()

    for i, url in enumerate(article_urls, 1):
        print(f"   [{i:3d}/{len(article_urls)}] {url}")
        resp = _get(url, session)
        if not resp:
            continue
        soup = BeautifulSoup(resp.text, "lxml")
        paras = _extract_paragraphs(soup, VOA_ARTICLE_SELECTORS)
        new = [p for p in paras if p not in seen_paragraphs]
        seen_paragraphs.update(new)
        all_paragraphs.extend(new)

    print(f"   ✅ VOA total: {len(all_paragraphs)} paragraphs")
    return all_paragraphs


# ---------------------------------------------------------------------------
# Oromo Wikipedia
# ---------------------------------------------------------------------------

WIKI_API = "https://om.wikipedia.org/api/rest_v1/page/summary/{title}"
WIKI_HTML = "https://om.wikipedia.org/api/rest_v1/page/html/{title}"
WIKI_SEARCH = "https://om.wikipedia.org/w/api.php"
WIKI_ARTICLE_SELECTORS = ["#mw-content-text", ".mw-parser-output"]

# Seed topics — the scraper will also follow links within Wikipedia
WIKI_SEED_TOPICS = [
    "Afaan_Oromoo", "Oromoo", "Itoophiyaa", "Finfinnee", "Oromiyaa",
    "Gadaa", "Seenaa_Oromoo", "Aadaa_Oromoo", "Barnoota", "Fayyaa",
    "Siyaasa", "Dimokraasii", "Teeknooloojii", "Saayinsii", "Atileetiksii",
    "Kubbaa_miilaa", "Amantii", "Hawaasummaa", "Dinagdee", "Lafa",
    "Bishaan", "Rooba", "Qilleensa", "Warra", "Maatii",
    "Magaalaa", "Baadiyyaa", "Hojii", "Giddu_gala", "Yaaliif",
]


def _wiki_article_titles(session: requests.Session, limit: int) -> list[str]:
    """Get Wikipedia article titles via the search API."""
    titles = list(WIKI_SEED_TOPICS)
    if len(titles) >= limit:
        return titles[:limit]

    # Expand via Wikipedia allpages API
    params = {
        "action": "query",
        "list": "allpages",
        "aplimit": min(limit - len(titles), 200),
        "apfilterredir": "nonredirects",
        "format": "json",
    }
    try:
        resp = _get(WIKI_SEARCH + "?" + "&".join(f"{k}={v}" for k, v in params.items()), session)
        if resp:
            data = resp.json()
            for page in data.get("query", {}).get("allpages", []):
                title = page["title"].replace(" ", "_")
                if title not in titles:
                    titles.append(title)
    except Exception as exc:
        print(f"   ⚠ Wikipedia API error: {exc}")

    return titles[:limit]


def scrape_wikipedia(session: requests.Session, limit: int = 50) -> list[str]:
    """Scrape Oromo Wikipedia articles. Returns list of paragraph strings."""
    print(f"\n{'─'*55}")
    print(f"📡 Oromo Wikipedia (limit={limit} articles)")
    print(f"{'─'*55}")

    titles = _wiki_article_titles(session, limit)
    print(f"   Found {len(titles)} articles to fetch")

    all_paragraphs: list[str] = []
    seen_paragraphs: set[str] = set()

    for i, title in enumerate(titles, 1):
        url = WIKI_HTML.format(title=title)
        print(f"   [{i:3d}/{len(titles)}] {title}")
        resp = _get(url, session)
        if not resp:
            continue
        soup = BeautifulSoup(resp.text, "lxml")
        paras = _extract_paragraphs(soup, WIKI_ARTICLE_SELECTORS)
        new = [p for p in paras if p not in seen_paragraphs]
        seen_paragraphs.update(new)
        all_paragraphs.extend(new)

    print(f"   ✅ Wikipedia total: {len(all_paragraphs)} paragraphs")
    return all_paragraphs


# ---------------------------------------------------------------------------
# Corpus writer
# ---------------------------------------------------------------------------

def _deduplicate(paragraphs: list[str], existing_corpus: str) -> list[str]:
    """Remove paragraphs already present verbatim in the existing corpus."""
    existing_lines = set(existing_corpus.splitlines())
    return [p for p in paragraphs if p not in existing_lines]


def append_to_corpus(paragraphs: list[str], source: str, dry_run: bool = False) -> int:
    """
    Append paragraphs to the corpus file.
    Returns the number of paragraphs actually written.
    """
    if not paragraphs:
        print(f"   ℹ  No new paragraphs from {source}.")
        return 0

    # Load existing corpus for dedup
    existing = CORPUS_PATH.read_text(encoding="utf-8") if CORPUS_PATH.exists() else ""
    new_paragraphs = _deduplicate(paragraphs, existing)

    if not new_paragraphs:
        print(f"   ℹ  All {len(paragraphs)} paragraphs from {source} already in corpus.")
        return 0

    if dry_run:
        print(f"   [DRY RUN] Would append {len(new_paragraphs)} new paragraphs from {source}.")
        return len(new_paragraphs)

    with open(CORPUS_PATH, "a", encoding="utf-8") as f:
        f.write(f"\n\n# ── Source: {source} — {datetime.now().isoformat()} ──\n")
        for para in new_paragraphs:
            f.write(para + "\n")

    print(f"   ✅ Appended {len(new_paragraphs)} new paragraphs from {source}.")
    return len(new_paragraphs)


# ---------------------------------------------------------------------------
# Report
# ---------------------------------------------------------------------------

def print_report(stats: dict) -> None:
    width = 55
    print(f"\n{'═'*width}")
    print(f"  Corpus Expansion Report — {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print(f"{'═'*width}")
    total = 0
    for source, count in stats.items():
        print(f"  {source:<25} {count:>6} paragraphs")
        total += count
    print(f"  {'─'*35}")
    print(f"  {'Total new paragraphs':<25} {total:>6}")
    if CORPUS_PATH.exists():
        size_kb = CORPUS_PATH.stat().st_size / 1024
        word_count = len(re.findall(r"[a-z']+", CORPUS_PATH.read_text(encoding="utf-8").lower()))
        print(f"  {'Corpus file size':<25} {size_kb:>5.0f} KB")
        print(f"  {'Total word tokens':<25} {word_count:>6,}")
    print(f"{'═'*width}\n")


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Expand the Afaan Oromo corpus from news and Wikipedia sources."
    )
    parser.add_argument("--bbc",      action="store_true", help="Scrape BBC Afaan Oromo")
    parser.add_argument("--voa",      action="store_true", help="Scrape VOA Afaan Oromo")
    parser.add_argument("--wiki",     action="store_true", help="Scrape Oromo Wikipedia")
    parser.add_argument("--all",      action="store_true", help="Scrape all sources")
    parser.add_argument("--limit",    type=int, default=100,
                        help="Max articles per source (default: 100)")
    parser.add_argument("--dry-run",  action="store_true",
                        help="Scrape and report but do NOT write to corpus")
    parser.add_argument("--backup",   action="store_true",
                        help="Create corpus backup before writing")
    parser.add_argument("--report",   type=str, default=None, metavar="FILE",
                        help="Save report to FILE")
    args = parser.parse_args()

    if not any([args.bbc, args.voa, args.wiki, args.all]):
        parser.print_help()
        sys.exit(0)

    if args.backup and CORPUS_PATH.exists() and not args.dry_run:
        backup = CORPUS_PATH.with_suffix(".txt.bak")
        shutil.copy2(CORPUS_PATH, backup)
        print(f"✅ Backup saved to {backup}")

    session = requests.Session()
    session.headers.update(HEADERS)

    stats: dict[str, int] = {}

    if args.bbc or args.all:
        paragraphs = scrape_bbc(session, limit=args.limit)
        stats["BBC Afaan Oromo"] = append_to_corpus(paragraphs, "BBC Afaan Oromo", args.dry_run)

    if args.voa or args.all:
        paragraphs = scrape_voa(session, limit=args.limit)
        stats["VOA Afaan Oromo"] = append_to_corpus(paragraphs, "VOA Afaan Oromo", args.dry_run)

    if args.wiki or args.all:
        paragraphs = scrape_wikipedia(session, limit=args.limit)
        stats["Oromo Wikipedia"] = append_to_corpus(paragraphs, "Oromo Wikipedia", args.dry_run)

    print_report(stats)

    if args.report:
        report_path = Path(args.report)
        with open(report_path, "w", encoding="utf-8") as f:
            f.write(f"Corpus expansion report — {datetime.now().isoformat()}\n")
            for source, count in stats.items():
                f.write(f"{source}: {count} paragraphs\n")
        print(f"Report saved to {report_path}")


if __name__ == "__main__":
    main()
