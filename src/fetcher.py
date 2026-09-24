import json
import logging
import re
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)

USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"

def strip_html_tags(text: str) -> str:
    """Remove HTML tags and extra whitespace from raw RSS text."""
    if not text:
        return ""
    clean = re.sub(r"<[^>]+>", " ", text)
    clean = re.sub(r"&nbsp;|&amp;|&quot;|&#39;|&lt;|&gt;", lambda m: {
        "&nbsp;": " ",
        "&amp;": "&",
        "&quot;": '"',
        "&#39;": "'",
        "&lt;": "<",
        "&gt;": ">"
    }.get(m.group(0), " "), clean)
    clean = re.sub(r"\s+", " ", clean).strip()
    return clean

def parse_rss_or_atom(xml_content: bytes, source_name: str, category: str) -> List[Dict]:
    """Parse RSS 2.0 or Atom feeds using xml.etree.ElementTree."""
    articles = []
    try:
        root = ET.fromstring(xml_content)
    except Exception as e:
        logger.warning(f"XML parse error for source {source_name}: {e}")
        return articles

    # Atom feed has root tag with 'feed'
    is_atom = root.tag.endswith("feed")

    if is_atom:
        # Atom namespaces
        ns = {"atom": "http://www.w3.org/2005/Atom"}
        entries = root.findall("atom:entry", ns) or root.findall("entry")
        for entry in entries[:8]:
            title_el = entry.find("atom:title", ns) or entry.find("title")
            title = title_el.text if title_el is not None and title_el.text else "Untitled"

            link = ""
            link_el = entry.find("atom:link[@rel='alternate']", ns) or entry.find("atom:link", ns) or entry.find("link")
            if link_el is not None:
                link = link_el.attrib.get("href", "") or (link_el.text or "")

            summary_el = entry.find("atom:summary", ns) or entry.find("atom:content", ns) or entry.find("summary") or entry.find("content")
            summary = summary_el.text if summary_el is not None and summary_el.text else ""

            published_el = entry.find("atom:published", ns) or entry.find("atom:updated", ns) or entry.find("published") or entry.find("updated")
            published = published_el.text if published_el is not None and published_el.text else ""

            articles.append({
                "title": strip_html_tags(title),
                "link": link.strip(),
                "summary": strip_html_tags(summary)[:400],
                "source": source_name,
                "category": category,
                "published": published
            })
    else:
        # Standard RSS 2.0
        channel = root.find("channel")
        items = (channel.findall("item") if channel is not None else root.findall(".//item"))[:8]
        for item in items:
            title_el = item.find("title")
            title = title_el.text if title_el is not None and title_el.text else "Untitled"

            link_el = item.find("link")
            link = link_el.text if link_el is not None and link_el.text else ""

            desc_el = item.find("description")
            desc = desc_el.text if desc_el is not None and desc_el.text else ""

            pub_date_el = item.find("pubDate")
            pub_date = pub_date_el.text if pub_date_el is not None and pub_date_el.text else ""

            articles.append({
                "title": strip_html_tags(title),
                "link": link.strip(),
                "summary": strip_html_tags(desc)[:400],
                "source": source_name,
                "category": category,
                "published": pub_date
            })

    return articles

def fetch_feed(url: str, source_name: str, category: str, timeout: int = 10) -> List[Dict]:
    """Fetch and parse a single RSS/Atom feed."""
    req = urllib.request.Request(
        url,
        headers={"User-Agent": USER_AGENT, "Accept": "application/rss+xml, application/atom+xml, application/xml, text/xml"}
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as response:
            content = response.read()
            return parse_rss_or_atom(content, source_name, category)
    except Exception as e:
        logger.warning(f"Could not fetch {source_name} ({url}): {e}")
        return []

def fetch_all_sources(config_path: Optional[Path] = None) -> List[Dict]:
    """Fetch news from all curated sources listed in config/sources.json."""
    if config_path is None:
        config_path = Path(__file__).resolve().parent.parent / "config" / "sources.json"

    if not config_path.is_file():
        logger.error(f"Sources configuration not found at {config_path}")
        return []

    with open(config_path, "r", encoding="utf-8") as f:
        config = json.load(f)

    all_articles: List[Dict] = []
    seen_titles = set()

    for src in config.get("sources", []):
        url = src.get("url")
        name = src.get("name", "Unknown Source")
        category = src.get("category", "General Tech")
        logger.info(f"Fetching: {name} ({url})")
        items = fetch_feed(url, name, category)
        for item in items:
            norm_title = re.sub(r"[^a-zA-Z0-9]", "", item["title"].lower())
            if norm_title and norm_title not in seen_titles:
                seen_titles.add(norm_title)
                all_articles.append(item)

    logger.info(f"Successfully collected {len(all_articles)} unique articles across sources.")
    return all_articles

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    articles = fetch_all_sources()
    print(f"Fetched {len(articles)} articles.")
    for i, a in enumerate(articles[:5], 1):
        print(f"\n{i}. [{a['source']}] {a['title']}\n   {a['summary'][:120]}...\n   {a['link']}")
