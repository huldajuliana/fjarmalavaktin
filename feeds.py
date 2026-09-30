# -*- coding: utf-8 -*-
"""
Heimildalisti Fjármálavaktarinnar.

Tvær gerðir heimilda:
  RSS  : {"src", "type": "rss",  "url", "cat"}
  HTML : {"src", "type": "html", "url", "base", "path", "cat"}
         Les fréttasíðu beint. "path" = aðeins hlekkir sem innihalda þennan
         textabút teljast greinar (síar burt valmyndir o.þ.h.), t.d. "/frettir/".

ATH: Slóðir geta breyst. Bilaður straumur/síða sleppir bara þeirri heimild og
keyrslan heldur áfram. Yfirfarðu Actions-loggið: ✓ = virkar, ! = skilar engu.

Keldan er áskriftarlæst og því ekki með opinn straum.
"""

FEEDS = [
    # --- Opinberar stofnanir (RSS) ---
    {"src": "Seðlabanki Íslands",    "type": "rss", "url": "https://sedlabanki.is/rss/", "cat": None},
    {"src": "Stjórnarráðið",         "type": "rss", "url": "https://www.stjornarradid.is/rss/frettir/", "cat": None},
    {"src": "Samtök atvinnulífsins", "type": "rss", "url": "https://www.sa.is/rss", "cat": None},
    {"src": "ASÍ",                   "type": "rss", "url": "https://www.asi.is/rss/", "cat": "vinnumarkadur"},

    # --- Fjölmiðlar með RSS ---
    {"src": "mbl.is", "type": "rss", "url": "https://www.mbl.is/feeds/vidskipti/", "cat": None},
    {"src": "Vísir",  "type": "rss", "url": "https://www.visir.is/rss/allt", "cat": None},
    {"src": "RÚV",    "type": "rss", "url": "https://www.ruv.is/rss/vidskipti", "cat": None},

    # --- Heimildir án RSS — lesnar beint af fréttasíðu (HTML) ---
    {"src": "Hagstofan", "type": "html",
     "url": "https://hagstofa.is/utgafur/frettasafn/",
     "base": "https://hagstofa.is", "path": "/frettasafn/", "cat": None},

    {"src": "Viðskiptablaðið", "type": "html",
     "url": "https://vb.is/frettir/",
     "base": "https://vb.is", "path": "/frettir/", "cat": None},

    {"src": "Arion banki", "type": "html",
     "url": "https://www.arionbanki.is/frettir",
     "base": "https://www.arionbanki.is", "path": "/frettir/", "cat": None},
]

# Heimildir sem teljast alltaf fjármála-/efnahagslega relevant.
# (Hagstofan er ekki hér lengur — treyst á leitarorð svo mannfjölda-/heilsutölur
#  slæðist ekki inn; efnahagsútgáfur hennar innihalda fjármálaorð hvort eð er.)
ALWAYS_RELEVANT_SOURCES = {
    "Seðlabanki Íslands", "Samtök atvinnulífsins", "ASÍ",
}
