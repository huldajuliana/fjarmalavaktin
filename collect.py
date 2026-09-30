#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Fjármálavaktin — söfnun og birting.

Keyrt af GitHub Actions þrisvar á dag:
  1. Sækir heimildir (feeds.py) — bæði RSS-strauma og HTML-fréttasíður.
  2. Síar og flokkar fréttir (classify.py); hendir rusli/villusíðum.
  3. Geymir í data/store.json og hreinsar gamalt (store.py).
  4. Endurbyggir index.html úr templates/page_template.html.

Notkun: python collect.py
"""
import sys, json, html, hashlib
from pathlib import Path
from datetime import datetime, timezone
from urllib.parse import urljoin

import feedparser
import requests
from bs4 import BeautifulSoup

from feeds import FEEDS, ALWAYS_RELEVANT_SOURCES
from classify import classify, clean_summary, is_junk
import store as S

ROOT = Path(__file__).parent
TEMPLATE = ROOT / "templates" / "page_template.html"
SEED = ROOT / "data" / "seed.json"
OUT = ROOT / "index.html"
MAX_PER_FEED = 40
HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; Fjarmalavaktin/1.0)"}


def _today():
    return datetime.now(timezone.utc).strftime("%Y-%m-%d")


def _entry_date(e) -> str:
    for k in ("published_parsed", "updated_parsed"):
        v = getattr(e, k, None)
        if v:
            return datetime(*v[:6], tzinfo=timezone.utc).strftime("%Y-%m-%d")
    return _today()


def _id(url: str) -> str:
    return hashlib.sha1((url or "").encode("utf-8")).hexdigest()[:10]


def _mk(title, url, raw, f, date):
    return {"title": title, "url": url, "raw": raw, "src": f["src"], "date": date,
            "default_cat": f.get("cat"), "always": f["src"] in ALWAYS_RELEVANT_SOURCES}


def fetch_rss(f):
    out = []
    try:
        d = feedparser.parse(f["url"])
        if getattr(d, "bozo", 0) and not d.entries:
            print(f"  ! tómur/ógildur straumur: {f['src']}  [{f['url']}]")
            return out
        for e in d.entries[:MAX_PER_FEED]:
            title = html.unescape(getattr(e, "title", "") or "").strip()
            link = getattr(e, "link", "") or ""
            if not title or not link:
                continue
            raw = getattr(e, "summary", getattr(e, "description", "")) or ""
            out.append(_mk(title, link, raw, f, _entry_date(e)))
        print(f"  ✓ {f['src']} (rss): {len(out)} færslur  [{f['url']}]")
    except Exception as ex:
        print(f"  ! villa við {f['src']} [{f['url']}]: {ex}")
    return out


def fetch_html(f):
    """Les fréttasíðu og tínir út greinahlekki (síaða á f['path'])."""
    out, seen = [], set()
    try:
        r = requests.get(f["url"], headers=HEADERS, timeout=25)
        r.raise_for_status()
        soup = BeautifulSoup(r.text, "html.parser")
        base = f.get("base") or f["url"]
        path = f.get("path")
        for a in soup.select(f.get("item_selector", "a")):
            title = a.get_text(strip=True)
            href = a.get("href")
            if not title or not href or len(title) < 12:
                continue
            url = urljoin(base, href)
            if path and path not in url:
                continue
            if url in seen:
                continue
            seen.add(url)
            out.append(_mk(title, url, "", f, _today()))
            if len(out) >= MAX_PER_FEED:
                break
        print(f"  ✓ {f['src']} (html): {len(out)} greinar  [{f['url']}]")
    except Exception as ex:
        print(f"  ! villa við {f['src']} [{f['url']}]: {ex}")
    return out


def fetch():
    items = []
    for f in FEEDS:
        items += fetch_html(f) if f.get("type") == "html" else fetch_rss(f)
    return items


def to_records(items):
    out, seen_urls = [], set()
    for it in items:
        if it["url"] in seen_urls:
            continue
        res = classify(it["title"], it["raw"], it.get("default_cat"),
                       src=it["src"], always_relevant=it["always"])
        if not res:
            continue
        seen_urls.add(it["url"])
        out.append({
            "id": _id(it["url"]),
            "cat": res["cat"], "impact": res["impact"], "dir": res["dir"],
            "constr": res["constr"], "date": it["date"], "src": it["src"],
            "url": it["url"], "title": it["title"], "sum": clean_summary(it["raw"]),
        })
    return out


def render(records):
    tpl = TEMPLATE.read_text(encoding="utf-8")
    data = json.dumps(records, ensure_ascii=False)
    htmlout = tpl.replace("__DATA__", data).replace("__BUILD__", _today())
    OUT.write_text(htmlout, encoding="utf-8")
    print(f"  → index.html skrifað með {len(records)} fréttum.")


def main():
    print("Fjármálavaktin — sæki heimildir…")
    items = fetch()
    fresh = to_records(items)
    print(f"Relevant fréttir úr heimildum: {len(fresh)}")

    store = S.prune(S.merge(S.load_store(), fresh))

    # Hreinsa út rusl (villusíður/404) sem gæti hafa slæðst inn í fyrri keyrslum
    for _k in list(store.keys()):
        _rec = store[_k].get("record", {})
        if is_junk(_rec.get("title", ""), _rec.get("sum", "")):
            del store[_k]

    S.save_store(store)
    recs = S.records(store)

    if not recs and SEED.exists():
        recs = json.loads(SEED.read_text(encoding="utf-8"))
        print("  (engin lifandi gögn — nota fræ-gögn í bili)")

    render(recs)
    print("Lokið.")


if __name__ == "__main__":
    main()
