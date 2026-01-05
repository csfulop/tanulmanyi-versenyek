# Országos Általános és Középiskolai Tanulmányi Versenyek - Eredményelemző Rendszer

## Áttekintés

A projekt célja egy átfogó elemző rendszer létrehozása, amely automatikusan letölti, feldolgozza és elemzi a magyarországi tanulmányi versenyek történelmi eredményeit.

**Jelenlegi állapot**: Ez a **v0.4.0** verzió a **Bolyai Anyanyelvi Csapatverseny** eredményeinek feldolgozására koncentrál. A rendszer egy négyfázisú adatfeldolgozó pipeline, amely a verseny weboldaláról gyűjti be az adatokat, normalizálja az iskolaneveket a hivatalos KIR adatbázis alapján, majd Excel formátumban készít belőlük elemzéseket.

A jövőben a rendszer további versenyekkel (OKTV, Zrínyi Ilona, más Bolyai tantárgyak) és interaktív vizualizációval fog bővülni.

## Mit csinál a program?

A program négy lépésben dolgozza fel a versenyeredményeket:

1. **Letöltés**: Automatikusan letölti az összes elérhető versenyév eredményeit a Bolyai verseny hivatalos weboldaláról (jelenleg csak az anyanyelvi kategória)
2. **Feldolgozás**: Kinyeri a strukturált adatokat (iskola neve, város, helyezés, évfolyam, stb.)
3. **KIR adatbázis letöltése**: Letölti a hivatalos magyar iskolaadatbázist (KIR - Köznevelési Információs Rendszer)
4. **Normalizálás és elemzés**: Iskolanevek normalizálása fuzzy matching algoritmussal, vármegyék és régiók hozzáadása, Excel riport készítése

## Milyen adatokat gyűjt?

A program az alábbi információkat gyűjti minden versenyeredményről:

- **Tanév**: Melyik tanévben zajlott a verseny (pl. 2024-25)
- **Tantárgy**: Anyanyelv (jelenleg csak ezt támogatja)
- **Iskola neve**: A versenyző csapat iskolájának hivatalos neve (KIR adatbázis alapján normalizálva)
- **Város**: Az iskola városa (KIR adatbázis alapján normalizálva)
- **Vármegye**: Az iskola vármegyéje (KIR adatbázisból)
- **Régió**: Az iskola régiója (KIR adatbázisból)
- **Helyezés**: A csapat végső helyezése
- **Évfolyam**: Melyik évfolyamon versenyeztek (3-8. osztály)

## Milyen elemzéseket készít?

A program egy Excel fájlt hoz létre három munkalappal:

1. **Data**: Az összes versenyeredmény egy helyen (3200+ sor)
2. **Ranking_by_School**: Iskolák rangsora - melyik iskola hány alkalommal szerepelt az eredmények között
3. **Ranking_by_City**: Városok rangsora - melyik városból hány csapat jutott be a döntőbe

**Megjegyzés az Excel riportról**: Az eredeti elképzelés szerint a program pivot táblákat hozott volna létre, amelyeket a felhasználó dinamikusan tudna szűrni és átrendezni. Technikai korlátok miatt jelenleg statikus összesítő táblákat generál a rendszer. A pivot táblák létrehozását a felhasználónak kell manuálisan elvégeznie az Excel-ben a Data munkalap alapján.

## Lefedett időszak

A program **10 év** versenyeredményét dolgozza fel:
- 2015-16-tól 2024-25-ig
- Minden évfolyam (3-8. osztály)
- Írásbeli és szóbeli döntők eredményei

**Összesen**: 3231 egyedi versenyeredmény, 613 különböző iskolából, 260 városból (iskolanevek normalizálva a KIR adatbázis alapján).

## Hogyan használd?

### Előfeltételek

- Python 3.11 vagy újabb
- Poetry (Python csomagkezelő)

### Telepítés

```bash
# Repository klónozása
git clone <repository-url>
cd tanulmanyi-versenyek

# Függőségek telepítése
poetry install

# Playwright böngésző telepítése (csak első alkalommal)
poetry run playwright install chromium
```

### Futtatás

A teljes pipeline futtatása négy paranccsal:

```bash
# 1. Eredmények letöltése a weboldalról
poetry run python 01_raw_downloader.py

# 2. HTML fájlok feldolgozása CSV formátumba
poetry run python 02_html_parser.py

# 3. KIR adatbázis letöltése (hivatalos magyar iskolaadatbázis)
poetry run python 03_download_helper_data.py

# 4. Iskolanevek normalizálása és Excel riport készítése
poetry run python 04_merger_and_excel.py
```

### Eredmények

A program a `data/` mappában hozza létre az eredményeket:

- `master_bolyai_anyanyelv.csv` - Minden adat egy CSV fájlban (normalizált iskolanevekkel)
- `school_matching_audit.csv` - Iskolanév-párosítások audit fájlja
- `validation_report.json` - Adatminőségi jelentés
- `analysis_templates/Bolyai_Analysis_Report.xlsx` - Excel elemzés

## Notebooks - Adatelemzés

A projekt tartalmaz egy Jupyter notebookot az adatok interaktív elemzéséhez.

### Notebook használata Kaggle-ön

A notebook már elérhető Kaggle-ön, vagy feltöltheted saját verziódat:

- **Notebook Kaggle-ön:** https://www.kaggle.com/code/csfulop/tanulmanyi-versenyek-eredmenyelemzes
- **Dataset Kaggle-ön:** https://www.kaggle.com/datasets/csfulop/tanulmanyi-versenyek

**Saját verzió feltöltéséhez:**
1. Töltsd fel a notebookot (`notebooks/competition_analysis.ipynb`) a Kaggle-re
2. Csatold hozzá a `tanulmanyi-versenyek` adathalmazt
3. Futtasd a cellákat sorban

### Notebook használata lokálisan

**Ajánlott módszer (Poetry - gyors):**
```bash
./run_notebook_with_poetry.sh
# Nyisd meg a böngészőben: http://localhost:8888
```

**Alternatív módszer (Docker - pontos Kaggle környezet, 20GB):**
```bash
./run_notebook_in_docker.sh
# Nyisd meg a böngészőben: http://localhost:8888
```

**Részletek:** Lásd `notebooks/README.md`

## Fontos tudnivalók

### Adatvédelem

A program **nem gyűjt személyes adatokat**. Csak az iskolák nevét, városát és a csapatok helyezéseit tárolja. Tanulók nevei nem kerülnek be az adatbázisba.

### Etikus adatgyűjtés

A program "udvarias" módon gyűjti az adatokat:
- 5 másodperces késleltetés a lekérések között
- Nem terheli túl a szervert
- Csak nyilvánosan elérhető adatokat gyűjt

### Megye és régió információ

A jelenlegi verzió **tartalmazza a vármegye és régió adatokat**, amelyeket a hivatalos KIR (Köznevelési Információs Rendszer) adatbázisból nyerünk ki az iskolanevek normalizálása során.

### Duplikációkezelés

A program intelligensen kezeli az írásbeli és szóbeli döntők eredményeit:
- Az írásbeli döntő előzetes helyezéseket tartalmaz
- A szóbeli döntő végleges helyezéseket tartalmaz (csak a legjobb 6 csapat)
- A program automatikusan a végleges helyezéseket tartja meg

**COVID-19 évek**: 2020-21 és 2021-22 tanévekben nem volt szóbeli döntő, így az írásbeli eredmények számítanak véglegesnek.

## Technikai részletek

### Projekt szerkezete

```
tanulmanyi-versenyek/
├── 01_raw_downloader.py       # Letöltő script
├── 02_html_parser.py           # Feldolgozó script
├── 03_download_helper_data.py  # KIR adatbázis letöltő script
├── 04_merger_and_excel.py      # Összesítő és riport készítő script
├── config.yaml                 # Konfigurációs beállítások
├── templates/                  # Excel sablon
├── data/                       # Generált adatok (nincs verziókezelve)
└── src/                        # Forráskód modulok
```

### Tesztek futtatása

```bash
poetry run pytest tests/ -v
```

Jelenleg 100 teszt van, mind zöld. ✅

### Teljesítmény

A teljes pipeline (4 lépés) futási ideje:
- **Lépés 1**: ~10 perc (versenyeredmények letöltése a weboldalról)
- **Lépés 2**: ~5 perc (HTML feldolgozás CSV formátumba)
- **Lépés 3**: ~5 másodperc (KIR adatbázis letöltése)
- **Lépés 4**: ~10 másodperc (iskolapárosítás és riport készítés)

**Összesen**: ~15 perc

Az iskolapárosítási algoritmus (lépés 4) optimalizált teljesítményre: city-indexed dictionary használatával O(1) keresés, pre-filtering a verseny városaira, és minimális DataFrame iterációk. A v0.4.0 optimalizálás előtt ez a lépés ~9 percet vett igénybe.

## Jövőbeli tervek

A projekt folyamatosan fejlődik. Tervezett fejlesztések:

1. **További versenyek**: OKTV, Zrínyi Ilona, más Bolyai tantárgyak
2. **Részletesebb elemzések**: Évfolyam szerinti bontás, időbeli trendek
3. **Webes felület**: Interaktív vizualizációk böngészőben

## Licenc

### Forráskód
A projekt forráskódja **MIT Licenc** alatt áll. Szabadon használható, módosítható és terjeszthető, csak a forrásmegjelölés kötelező.

### Adathalmaz
A generált adathalmaz **Creative Commons Nevezd meg! 4.0 Nemzetközi (CC BY 4.0)** licenc alatt áll. Szabadon használható bármilyen célra (beleértve a kereskedelmi felhasználást is), amennyiben megfelelő forrásmegjelölést ad.

**Fontos**: Az eredeti versenyeredmények a Bolyai Verseny szervezőinek tulajdonát képezik és nyilvánosan elérhetők a verseny weboldalán. A licenc az adatok összeállítására, feldolgozására és dokumentációjára vonatkozik.

Részletek: lásd a `LICENSE` fájlt a repository gyökerében és a `templates/kaggle/LICENSE` fájlt az adathalmazhoz.

## Kapcsolat

Kérdések, javaslatok esetén:

- **GitHub Repository:** https://github.com/csfulop/tanulmanyi-versenyek
- **Kaggle Dataset:** https://www.kaggle.com/datasets/csfulop/tanulmanyi-versenyek
- **Kaggle Notebook:** https://www.kaggle.com/code/csfulop/tanulmanyi-versenyek-eredmenyelemzes

---

**Utolsó frissítés**: 2026. január 5.
**Verzió**: 0.4.0
**Lefedett adatok**: 2015-16 - 2024-25 tanévek, Bolyai Anyanyelvi Csapatverseny