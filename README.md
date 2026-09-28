# Fjármálavaktin

Sjálfvirkt yfirlit yfir fjármála- og efnahagsfréttir sem móta ytra rekstrarumhverfi
fyrirtækja á Íslandi — verðbólga, vextir, kjarasamningar, gengi, hagspár, gjaldþrot
(með sérstakri merkingu á byggingageiranum) o.fl. Systursíða Framkvæmdavaktarinnar.

Síðan uppfærist sjálfkrafa **þrisvar á dag (kl. 9:15, 14 og 22)** með GitHub Actions:
hún sækir RSS-strauma, flokkar fréttir eftir efni / áhrifum / hreyfingu og endurbyggir
`index.html`. Safnið byggist upp jafnt og þétt (fréttir geymast í 120 daga).

## Skrár

| Skrá | Hlutverk |
|------|----------|
| `index.html` | Birta síðan (það sem GitHub Pages sýnir). Endurbyggð í hverri keyrslu. |
| `templates/page_template.html` | Sniðmát síðunnar með `__DATA__` og `__BUILD__` staðgenglum. |
| `collect.py` | Aðalforritið: sækir, flokkar, geymir, byggir. |
| `feeds.py` | Listi yfir RSS-heimildir. **Yfirfarðu slóðir hér.** |
| `classify.py` | Flokkun: relevans, flokkur, áhrif, hreyfing, byggingageiri. |
| `store.py` | Geymsla og afritavörn (dedup á slóð, geymir í 120 daga). |
| `data/store.json` | Safnið sjálft (býr til sjálfkrafa). |
| `data/seed.json` | Fræ-gögn svo síðan sé aldrei tóm fyrstu keyrslurnar. |
| `.github/workflows/uppfaera.yml` | Tímasetta keyrslan. |

## Uppsetning á GitHub (eins og Framkvæmdavaktin)

1. **Búðu til repo** (t.d. `fjarmalavaktin`) og settu allar þessar skrár í rótina.
   - Annaðhvort: dragðu skrárnar inn á github.com → *Add file* → *Upload files*.
   - Eða gegnum skipanalínu:
     ```bash
     git init
     git add .
     git commit -m "Fjármálavaktin — fyrsta útgáfa"
     git branch -M main
     git remote add origin https://github.com/<notandi>/fjarmalavaktin.git
     git push -u origin main
     ```

2. **Kveiktu á GitHub Pages**: *Settings → Pages → Source: Deploy from a branch →
   Branch: `main` / `(root)`*. Síðan birtist á
   `https://<notandi>.github.io/fjarmalavaktin/`.

3. **Leyfðu Actions að skrifa**: *Settings → Actions → General → Workflow permissions →
   „Read and write permissions"* og vista. (Workflow-ið er líka með `permissions: contents: write`.)

4. **Keyrðu handvirkt í fyrsta sinn**: *Actions-flipinn → „Uppfæra Fjármálavaktina" →
   Run workflow*. Eftir það keyrir hún sjálf kl. 9:15, 14 og 22 á hverjum degi.

## Heimildir — mikilvægt

`feeds.py` inniheldur bestu ágiskanir um RSS-slóðir stofnana og fjölmiðla. **Sumar gætu
þurft staðfestingu** (slóðir breytast). Eftir fyrstu keyrslu skaltu opna log-ið í
Actions: heimildir með `✓` virka, þær með `!` skila engu og þarf að lagfæra. Bilaður
straumur stöðvar ekki keyrsluna — hann er einfaldlega hunsaður.

**Keldan** (keldan.is) er að mestu áskriftarlæst og er því ekki í listanum. Ef opin
veita finnst má bæta henni við í `feeds.py`.

## Stilla flokkun

Allt er stillt í `classify.py`:
- **Flokkar og leitarorð** í `CATEGORY_KEYWORDS`.
- **Hreyfing** (▲▼▬) í `UP_WORDS` / `DOWN_WORDS`.
- **Byggingageira-merking** í `CONSTR_WORDS`.
- **Áhrifaflokkar** í `DEFAULT_IMPACT` og `SYSTEMIC_WORDS`.

## Keyra á eigin vél (til prófunar)

```bash
pip install -r requirements.txt
python collect.py
# opnaðu index.html í vafra
```

Án nets (eða ef allir straumar eru niðri) notar forritið `data/seed.json` svo síðan
verði aldrei tóm.
