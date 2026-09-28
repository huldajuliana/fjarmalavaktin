#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Fjármálavaktin — söfnun og birting.

Keyrt af GitHub Actions tvisvar á dag:
  1. Sækir RSS-strauma (feeds.py)
  2. Síar og flokkar fréttir (classify.py)
  3. Geymir í data/store.json og hreinsar gamalt (store.py)
  4. Endurbyggir index.html úr templates/page_template.html

Notkun: python collect.py
"""
import sys, json, html, hashlib
from pathlib import Path
from datetime import datetime, timezone

import feedparser

from feeds import FEEDS, ALWAYS_RELEVANT_SOURCES
from classify import classify, clean_summary
import store as S

ROOT = Path(__file__).parent
TEMPLATE = ROOT / "templates" / "page_template.html"
SEED = ROOT / "data" / "seed.json"
OUT = ROOT / "index.html"
MAX_PER_FEED = 40


def _entry_date(e) -> str:
    for k in ("published_parsed", "updated_parsed"):
        v = getattr(e, k, None)
        if v:
            return datetime(*v[:6], tzinfo=timezone.utc).strftime("%Y-%m-%d")
    return datetime.now(timezone.utc).strftime("%Y-%m-%d")


def _id(url: str) -> str:
    return hashlib.sha1((url or "").encode("utf-8")).hexdigest()[:10]


def fetch():
    items = []
    for f in FEEDS:
        try:
            d = feedparser.parse(f["url"])
            if getattr(d, "bozo", 0) and not d.entries:
                print(f"  ! tómur/ógildur straumur: {f['url']}", file=sys.stderr)
                continue
            for e in d.entries[:MAX_PER_FEED]:
                title = html.unescape(getattr(e, "title", "") or "").strip()
                link = getattr(e, "link", "") or ""
                if not title or not link:
                    continue
                raw = getattr(e, "summary", getattr(e, "description", "")) or ""
                items.append({
                    "title": title,
                    "url": link,
                    "raw": raw,
                    "src": f["src"],
                    "date": _entry_date(e),
                    "default_cat": f.get("cat"),
                    "always": f["src"] in ALWAYS_RELEVANT_SOURCES,
                })
            print(f"  ✓ {f['src']}: {len(d.entries)} færslur  [{f['url']}]")
        except Exception as ex:
            print(f"  ! villa við {f['url']}: {ex}", file=sys.stderr)
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
            "cat": res["cat"],
            "impact": res["impact"],
            "dir": res["dir"],
            "constr": res["constr"],
            "date": it["date"],
            "src": it["src"],
            "url": it["url"],
            "title": it["title"],
            "sum": clean_summary(it["raw"]),
        })
    return out


def render(records):
    tpl = TEMPLATE.read_text(encoding="utf-8")
    data = json.dumps(records, ensure_ascii=False)
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    htmlout = tpl.replace("__DATA__", data).replace("__BUILD__", today)
    OUT.write_text(htmlout, encoding="utf-8")
    print(f"  → index.html skrifað með {len(records)} fréttum.")


def main():
    print("Fjármálavaktin — sæki strauma…")
    items = fetch()
    fresh = to_records(items)
    print(f"Relevant fréttir úr straumum: {len(fresh)}")

    store = S.prune(S.merge(S.load_store(), fresh))
    S.save_store(store)
    recs = S.records(store)

    # Vörn: ef ekkert hefur safnast (t.d. allir straumar niðri), nota fræ-gögn
    # svo síðan verði aldrei tóm.
    if not recs and SEED.exists():
        recs = json.loads(SEED.read_text(encoding="utf-8"))
        print("  (engin lifandi gögn — nota fræ-gögn í bili)")

    render(recs)
    print("Lokið.")


if __name__ == "__main__":
    main()
