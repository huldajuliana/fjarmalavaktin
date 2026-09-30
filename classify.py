# -*- coding: utf-8 -*-
"""
Flokkun frétta fyrir Fjármálavaktina.

classify(title, summary, default_cat, src) -> dict eða None
  Skilar None ef fréttin telst ekki fjármála-/efnahagslega relevant.
  Annars: {"cat","impact","dir","constr"}
"""
import re, html as _html

# --- Flokkar og leitarorð (lágstafir, án broddstafa-næmni að hluta) ---
CATEGORY_KEYWORDS = {
    "verdbolga":     ["verðbólg", "vísitala neysluverðs", "neysluverð", "verðlag",
                      "verðbólguvænting", "verðtrygg", "dýrtíð"],
    "vextir":        ["stýrivext", "vaxtaákvörð", "vaxtaákvarð", "peningastefnu",
                      "meginvext", "vaxtalækk", "vaxtahækk", "vextir", "vaxta"],
    "vinnumarkadur": ["kjarasamning", "kjaravið", "kjaradeil", "verkfall", "launahækk",
                      "kaupgjald", "kauptaxt", "forsenduákvæð", "vinnumarkað", "verkalýð",
                      "atvinnuleysi", "así", " sa ", "stéttarfélag"],
    "gengi":         ["gengi krón", "gengisvísital", "krónan", "gjaldmiðil", "gengisþróun",
                      "gengisfelling", "evru", "bandaríkjadal"],
    "hagvoxtur":     ["hagvöxt", "hagspá", "landsframleiðsl", "hagkerf", "verg landsframl",
                      "nýskrán", "velta eyk", "hagvísa", "spá um vöxt", "þjóðhags"],
    "rikisfjarmal":  ["bókun 35", "bókunar 35", "ees-samning", "ees-regl", "eftirlitsstofnun efta", "efta-dómstól", "ríkisaðstoð", "fjárlög", "ríkisfjármál", "ríkissjóð", "skatt", "fjáraukalög",
                      "aðhald í rekstri", "fjármálaáætlun", "afkoma ríkis"],
    "markadir":      ["kauphöll", "úrvalsvísital", "hlutabréf", "uppgjör", "ársfjórðung",
                      "hagnað", "tap félag", "arð", "yfirtök", "skráð á markað", "afkom",
                      "kaup á ", "samruni", "samkeppniseftirlit"],
    "gjaldthrot":    ["gjaldþrot", "þrotabú", "greiðslustöðvun", "nauðasamning",
                      "vanskil", "rekstrarvand", "skiptastjóri", "tekið til gjaldþrotaskipta"],
    "husnaedi":      ["fasteignaverð", "íbúðaverð", "húsnæðisverð", "íbúðamarkað",
                      "fasteignamarkað", "leiguverð", "húsnæðisliður", "óseldar íbúð"],
    "eftirlit":      ["fjármálaeftirlit", "fjármálastöðugleik", "eiginfjár", "lausafjár",
                      "könnunar- og matsferl", "srep", "varúðarregl", "bankakerfi"],
}

# Almenn relevans-orð: ef ekkert af þessu finnst (og heimild er ekki "alltaf relevant")
# telst fréttin ekki til fjármála.
RELEVANCE_KEYWORDS = set()
for kws in CATEGORY_KEYWORDS.values():
    RELEVANCE_KEYWORDS.update(kws)
RELEVANCE_KEYWORDS.update(["efnahag", "fjármál", "viðskipti", "atvinnulíf", "seðlabank"])

# --- Hreyfing (dir) ---
UP_WORDS   = ["hækk", "jókst", "eykst", "aukn" , "vex", "þyngist", "dýrar", "hærri",
              "fjölgar", "fjölgun", "þrýstir upp", "versn", "vaxandi"]
DOWN_WORDS = ["lækk", "hjaðn", "dregst saman", "minnk", "fækk", "léttir", "lægri",
              "ódýrar", "batnar", "rénar"]

# --- Byggingageiri (fyrir gjaldþrot/rekstur) ---
CONSTR_WORDS = ["bygging", "verktak", "mannvirk", "íbúð", "fasteign", "húsbyggj",
                "verkframkvæmd", "byggingariðnað"]

# --- Áhrif (impact) sjálfgefið eftir flokki ---
DEFAULT_IMPACT = {
    "verdbolga": "kerfis", "vextir": "kerfis", "vinnumarkadur": "mikil",
    "gengi": "nokkur", "hagvoxtur": "nokkur", "rikisfjarmal": "mikil",
    "markadir": "nokkur", "gjaldthrot": "mikil", "husnaedi": "mikil",
    "eftirlit": "nokkur",
}
# Orð sem lyfta áhrifum upp í "kerfislæg"
SYSTEMIC_WORDS = ["forsenduákvæð", "kjarasamning", "stýrivext", "verðbólg",
                  "peningastefnu", "fjárlög", "fjármálastöðugleik"]


def _norm(s: str) -> str:
    return (s or "").lower()


def clean_summary(raw: str, limit: int = 320) -> str:
    """Hreinsar HTML úr lýsingu og styttir snyrtilega við setningu."""
    if not raw:
        return ""
    txt = re.sub(r"<[^>]+>", " ", raw)
    txt = _html.unescape(txt)
    txt = re.sub(r"\s+", " ", txt).strip()
    if len(txt) <= limit:
        return txt
    cut = txt[:limit]
    # reyndu að klippa við síðasta punkt/bil
    for sep in (". ", "! ", "? "):
        i = cut.rfind(sep)
        if i > limit * 0.5:
            return cut[:i + 1]
    i = cut.rfind(" ")
    return (cut[:i] if i > 0 else cut).rstrip(",;:") + " …"


def _best_category(text: str, default_cat):
    """Velur flokk með flestum/sterkustu samsvörunum."""
    scores = {}
    for cat, kws in CATEGORY_KEYWORDS.items():
        s = sum(1 for kw in kws if kw in text)
        if s:
            scores[cat] = s
    if not scores:
        return default_cat
    # gjaldþrot og verðbólga/vextir hafa forgang ef þau eiga samleið
    best = max(scores, key=lambda c: (scores[c], c in ("gjaldthrot", "vextir", "verdbolga")))
    return best


def _direction(text: str) -> str:
    up = any(w in text for w in UP_WORDS)
    down = any(w in text for w in DOWN_WORDS)
    # "verðbólga hjaðnar/lækkar" -> niður er rétt; ef bæði finnast, veldu það fyrra í texta
    if up and down:
        iu = min((text.find(w) for w in UP_WORDS if w in text), default=10**9)
        idn = min((text.find(w) for w in DOWN_WORDS if w in text), default=10**9)
        return "up" if iu < idn else "down"
    if up:
        return "up"
    if down:
        return "down"
    return "flat"


# --- Ruslsía: villusíður/404 sem geta slæðst inn úr brotnum hlekkjum ---
JUNK_TITLE_PATTERNS = [
    "síða fannst ekki", "síðan fannst ekki", "síða finnst ekki",
    "efnið fannst ekki", "efnið er ekki til", "þessi síða er ekki til",
    "page not found", "not found", "error 404", "404 error",
    "aðgangur bannaður", "access denied", "forbidden",
    "villa kom upp", "þjónusta ekki í boði", "under maintenance",
]


def is_junk(title: str, summary: str = "") -> bool:
    """True fyrir villusíður/404 og tómar færslur sem eiga ekki heima í safninu."""
    t = _norm(title).strip()
    if len(t) < 5:
        return True
    return any(p in t for p in JUNK_TITLE_PATTERNS)


def classify(title: str, summary: str, default_cat=None, src: str = "",
             always_relevant=False):
    if is_junk(title, summary):
        return None
    text = _norm(title + " " + summary)

    relevant = always_relevant or any(kw in text for kw in RELEVANCE_KEYWORDS)
    if not relevant:
        return None

    cat = _best_category(text, default_cat) or "markadir"

    impact = DEFAULT_IMPACT.get(cat, "nokkur")
    if any(w in text for w in SYSTEMIC_WORDS):
        impact = "kerfis"

    direction = _direction(text)

    constr = cat in ("gjaldthrot", "husnaedi") and any(w in text for w in CONSTR_WORDS)

    return {"cat": cat, "impact": impact, "dir": direction, "constr": constr}
