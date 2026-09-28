# -*- coding: utf-8 -*-
"""
Geymsla Fjármálavaktarinnar.

Geymir öll söfnuð fréttaskeyti í data/store.json, lykluð á slóð.
Hver færsla: { url: {"first_seen": iso, "record": {...}} }

Þannig byggist safnið upp jafnt og þétt — ekkert eyðist út fyrr en það er
eldra en `days` (sjálfgefið 120 dagar).
"""
import json
from pathlib import Path
from datetime import datetime, timezone, timedelta

STORE_PATH = Path(__file__).parent / "data" / "store.json"


def _key(record: dict) -> str:
    return (record.get("url") or (record.get("title", "") + record.get("date", ""))).strip()


def load_store() -> dict:
    if STORE_PATH.exists():
        try:
            return json.loads(STORE_PATH.read_text(encoding="utf-8"))
        except Exception:
            return {}
    return {}


def save_store(store: dict) -> None:
    STORE_PATH.parent.mkdir(parents=True, exist_ok=True)
    STORE_PATH.write_text(json.dumps(store, ensure_ascii=False, indent=2), encoding="utf-8")


def merge(store: dict, records: list) -> dict:
    """Bætir nýjum fréttum við og uppfærir efni þeirra sem fyrir eru."""
    now = datetime.now(tz=timezone.utc).isoformat()
    for r in records:
        k = _key(r)
        if not k:
            continue
        if k in store:
            store[k]["record"] = r            # uppfæra efni (t.d. lengri útdrátt)
        else:
            store[k] = {"first_seen": now, "record": r}
    return store


def prune(store: dict, days: int = 120) -> dict:
    cutoff = datetime.now(tz=timezone.utc) - timedelta(days=days)
    kept = {}
    for k, v in store.items():
        try:
            ts = datetime.fromisoformat(v.get("first_seen"))
            if ts >= cutoff:
                kept[k] = v
        except Exception:
            kept[k] = v
    return kept


def records(store: dict) -> list:
    """Skilar öllum fréttum, raðað eftir dagsetningu (nýjast fyrst)."""
    out = [v["record"] for v in store.values()]
    out.sort(key=lambda r: r.get("date", ""), reverse=True)
    return out
