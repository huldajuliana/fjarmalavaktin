# -*- coding: utf-8 -*-
"""
Heimildalisti Fjármálavaktarinnar.

Hver færsla: {"src": birtingarheiti, "url": RSS-slóð, "cat": sjálfgefinn flokkur eða None}

ATH: Sumar RSS-slóðir geta breyst eða þarfnast staðfestingar. Forritið er
hannað til að þola það — bilaður straumur sleppir bara þeirri heimild og
heldur áfram. Yfirfarðu slóðir sem skila engu og uppfærðu hér.

Keldan (keldan.is) er að mestu áskriftarlæst og er því ekki með opinn straum;
bætist við hér ef/þegar opin veita finnst.
"""

FEEDS = [
    # --- Opinberar stofnanir (allt relevant; cat gefið ef það á alltaf við) ---
    {"src": "Seðlabanki Íslands", "url": "https://sedlabanki.is/rss/", "cat": None},
    {"src": "Hagstofan",          "url": "https://hagstofa.is/utgafur/rss/", "cat": None},
    {"src": "Stjórnarráðið",      "url": "https://www.stjornarradid.is/rss/frettir/", "cat": None},
    {"src": "Samtök atvinnulífsins", "url": "https://www.sa.is/rss", "cat": None},
    {"src": "ASÍ",                "url": "https://www.asi.is/rss/", "cat": "vinnumarkadur"},

    # --- Fjölmiðlar (viðskiptaflokkar) ---
    {"src": "mbl.is",             "url": "https://www.mbl.is/feeds/vidskipti/", "cat": None},
    {"src": "Vísir",              "url": "https://www.visir.is/rss/vidskipti", "cat": None},
    {"src": "Viðskiptablaðið",    "url": "https://vb.is/rss/", "cat": None},
    {"src": "RÚV",                "url": "https://www.ruv.is/rss/vidskipti", "cat": None},

    # --- Til vara: almennur RÚV-straumur (síaður á leitarorðum) ---
    {"src": "RÚV",                "url": "https://www.ruv.is/rss/frettir", "cat": None},
]

# Heimildir sem teljast alltaf fjármála-/efnahagslega relevant,
# jafnvel þótt leitarorð finnist ekki í titli.
ALWAYS_RELEVANT_SOURCES = {
    "Seðlabanki Íslands", "Hagstofan", "Samtök atvinnulífsins", "ASÍ",
}
