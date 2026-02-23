import json
import re
import urllib.parse
import urllib.request
from functools import lru_cache
from typing import List
from urllib.error import HTTPError, URLError

from .models import ReferenceArticle


USER_AGENT = "News-Intelligence-Analyzer/1.2"


def _fetch_json(url: str, timeout: int = 8) -> dict:
USER_AGENT = "News-Intelligence-Analyzer/1.1"


def _fetch_json(url: str, timeout: int = 10) -> dict:
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode("utf-8"))


@lru_cache(maxsize=128)
def fetch_wikipedia(topic: str) -> List[ReferenceArticle]:
    query = urllib.parse.quote(topic)
    url = f"https://en.wikipedia.org/w/api.php?action=query&list=search&srsearch={query}&format=json&srlimit=4"
    refs: List[ReferenceArticle] = []
    try:
        data = _fetch_json(url)
        for item in data.get("query", {}).get("search", []):
            title = item.get("title", "Unknown")
            snippet = re.sub(r"<.*?>", "", item.get("snippet", "")).replace("&quot;", '"')
            refs.append(
                ReferenceArticle(
                    title=title,
                    source="Wikipedia",
                    summary=snippet,
                    link=f"https://en.wikipedia.org/wiki/{urllib.parse.quote(title.replace(' ', '_'))}",
                    viewpoint="Mainstream/reference",
                )
            )
    except (HTTPError, URLError, TimeoutError, json.JSONDecodeError):
    except Exception:
        return []
    return refs


@lru_cache(maxsize=128)
def fetch_crossref(topic: str) -> List[ReferenceArticle]:
    query = urllib.parse.quote(topic)
    url = f"https://api.crossref.org/works?query.title={query}&rows=4"
    refs: List[ReferenceArticle] = []
    try:
        data = _fetch_json(url)
        for item in data.get("message", {}).get("items", [])[:4]:
            title = (item.get("title") or ["Untitled"])[0]
            source = (item.get("container-title") or ["Academic publication"])[0]
            doi = item.get("DOI", "")
            refs.append(
                ReferenceArticle(
                    title=title,
                    source=source,
                    summary="Academic/technical reference that may support or challenge key claims.",
                    link=f"https://doi.org/{doi}" if doi else "",
                    viewpoint="Academic/independent",
                )
            )
    except (HTTPError, URLError, TimeoutError, json.JSONDecodeError):
    except Exception:
        return []
    return refs


def generate_non_mainstream(topic: str) -> List[ReferenceArticle]:
    return [
        ReferenceArticle(
            title=f"Independent analyses on {topic}",
            source="Independent newsletters and investigative blogs",
            summary="Check whether authors provide raw evidence, primary sources, and transparent methodology.",
            link=f"https://duckduckgo.com/?q={urllib.parse.quote(topic + ' independent analysis')}",
            link="",
            viewpoint="Alternative viewpoint",
        ),
        ReferenceArticle(
            title=f"OSINT discussion threads about {topic}",
            source="Open-source intelligence communities",
            summary="Useful for chronology checks, geolocation, and media provenance verification.",
            link=f"https://duckduckgo.com/?q={urllib.parse.quote(topic + ' osint discussion')}",
            link="",
            viewpoint="Obscure/OSINT",
        ),
        ReferenceArticle(
            title=f"Contrarian commentary clusters: {topic}",
            source="Niche forums and alternative media",
            summary="Use only with corroboration; identify where claims diverge from mainstream or primary-source evidence.",
            link=f"https://duckduckgo.com/?q={urllib.parse.quote(topic + ' alternative viewpoint')}",
            link="",
            viewpoint="Non-mainstream/contrarian",
        ),
    ]


def _offline_fallback(topic: str) -> List[ReferenceArticle]:
    return [
        ReferenceArticle(
            title=f"Mainstream coverage index: {topic}",
            source="News search",
            summary="Fallback index for mainstream reporting when APIs are unavailable.",
            link=f"https://duckduckgo.com/?q={urllib.parse.quote(topic + ' site:reuters.com OR site:apnews.com OR site:bbc.com')}",
            viewpoint="Mainstream/reference",
        ),
        ReferenceArticle(
            title=f"Academic index: {topic}",
            source="Google Scholar",
            summary="Fallback academic search index when Crossref access is unavailable.",
            link=f"https://scholar.google.com/scholar?q={urllib.parse.quote(topic)}",
            viewpoint="Academic/independent",
        ),
    ]


def find_references(topic: str) -> List[ReferenceArticle]:
    wiki_refs = fetch_wikipedia(topic)
    crossref_refs = fetch_crossref(topic)
    refs = wiki_refs + crossref_refs + generate_non_mainstream(topic)
    if not wiki_refs and not crossref_refs:
        refs.extend(_offline_fallback(topic))
def find_references(topic: str) -> List[ReferenceArticle]:
    refs = fetch_wikipedia(topic) + fetch_crossref(topic) + generate_non_mainstream(topic)

    deduped: List[ReferenceArticle] = []
    seen = set()
    for r in refs:
        key = (r.title.lower().strip(), r.source.lower().strip())
        if key in seen:
            continue
        seen.add(key)
        deduped.append(r)
    return deduped[:14]
