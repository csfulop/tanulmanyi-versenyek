# Országos Általános és Középiskolai Tanulmányi Versenyek - Eredményelemző Rendszer

## Áttekintés

A projekt célja egy átfogó elemző rendszer létrehozása, amely automatikusan letölti, feldolgozza és elemzi a magyarországi tanulmányi versenyek történelmi eredményeit.

**Jelenlegi állapot**: Ez az első MVP (Minimum Viable Product) verzió, amely a **Bolyai Anyanyelvi Csapatverseny** eredményeinek feldolgozására koncentrál. A rendszer egy háromfázisú adatfeldolgozó pipeline, amely a verseny weboldaláról gyűjti be az adatokat, majd Excel formátumban készít belőlük elemzéseket.

A jövőben a rendszer további versenyekkel (OKTV, Zrínyi Ilona, más Bolyai tantárgyak) és interaktív vizualizációval fog bővülni.

## Mit csinál a program?

A program három lépésben dolgozza fel a versenyeredményeket:

1. **Letöltés**: Automatikusan letölti az összes elérhető versenyév eredményeit a Bolyai verseny hivatalos weboldaláról (jelenleg csak az anyanyelvi kategória)
2. **Feldolgozás**: Kinyeri a strukturált adatokat (iskola neve, város, helyezés, évfolyam, stb.)
3. **Elemzés**: Összesített Excel riportot készít rangsorokkal és statisztikákkal

## Milyen adatokat gyűjt?

A program az alábbi információkat gyűjti minden versenyeredményről:

- **Tanév**: Melyik tanévben zajlott a verseny (pl. 2024-25)
- **Tantárgy**: Anyanyelv (jelenleg csak ezt támogatja)
- **Iskola neve**: A versenyző csapat iskolájának neve
- **Város**: Az iskola városa
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

**Összesen**: 3233 egyedi versenyeredmény, 766 különböző iskolából, 264 városból.

## Hogyan használd?

### Előfeltételek

- Python 3.11 vagy újabb
- Poetry (Python csomagkezelő)

### Telepítés

```bash
# Repository klónozása
git clone <repository-url>
cd tanulmanyi_versenyek

# Függőségek telepítése
poetry install

# Playwright böngésző telepítése (csak első alkalommal)
poetry run playwright install chromium
```

### Futtatás

A teljes pipeline futtatása három paranccsal:

```bash
# 1. Eredmények letöltése a weboldalról
poetry run python 01_raw_downloader.py

# 2. HTML fájlok feldolgozása CSV formátumba
poetry run python 02_html_parser.py

# 3. Összesítés és Excel riport készítése
poetry run python 03_merger_and_excel.py
```

### Eredmények

A program a `data/` mappában hozza létre az eredményeket:

- `master_bolyai_anyanyelv.csv` - Minden adat egy CSV fájlban
- `validation_report.json` - Adatminőségi jelentés
- `analysis_templates/Bolyai_Analysis_Report.xlsx` - Excel elemzés

## Fontos tudnivalók

### Adatvédelem

A program **nem gyűjt személyes adatokat**. Csak az iskolák nevét, városát és a csapatok helyezéseit tárolja. Tanulók nevei nem kerülnek be az adatbázisba.

### Etikus adatgyűjtés

A program "udvarias" módon gyűjti az adatokat:
- 5 másodperces késleltetés a lekérések között
- Nem terheli túl a szervert
- Csak nyilvánosan elérhető adatokat gyűjt

### Megye információ

A jelenlegi verzió **nem tartalmaz megyeadatokat**, mert ezek nem szerepelnek a forrás weboldalon. A `megye` oszlop üres marad. Jövőbeli verzióban tervezzük egy város-megye adatbázis integrálását.

### Duplikációkezelés

A program intelligensen kezeli az írásbeli és szóbeli döntők eredményeit:
- Az írásbeli döntő előzetes helyezéseket tartalmaz
- A szóbeli döntő végleges helyezéseket tartalmaz (csak a legjobb 6 csapat)
- A program automatikusan a végleges helyezéseket tartja meg

**COVID-19 évek**: 2020-21 és 2021-22 tanévekben nem volt szóbeli döntő, így az írásbeli eredmények számítanak véglegesnek.

## Technikai részletek

### Projekt szerkezete

```
tanulmanyi_versenyek/
├── 01_raw_downloader.py      # Letöltő script
├── 02_html_parser.py          # Feldolgozó script
├── 03_merger_and_excel.py     # Összesítő és riport készítő script
├── config.yaml                # Konfigurációs beállítások
├── templates/                 # Excel sablon
├── data/                      # Generált adatok (nincs verziókezelve)
└── src/                       # Forráskód modulok
```

### Tesztek futtatása

```bash
poetry run pytest tests/ -v
```

Jelenleg 16 teszt van, mind zöld. ✅

## Jövőbeli tervek

A projekt MVP (Minimum Viable Product) állapotban van. Tervezett fejlesztések:

1. **Megyeadatok hozzáadása**: Város-megye adatbázis integrálása
2. **További versenyek**: OKTV, Zrínyi Ilona, más Bolyai tantárgyak
3. **Részletesebb elemzések**: Évfolyam szerinti bontás, időbeli trendek
4. **Webes felület**: Interaktív vizualizációk böngészőben

## Licenc

### Forráskód
A projekt forráskódja **MIT Licenc** alatt áll. Szabadon használható, módosítható és terjeszthető, csak a forrásmegjelölés kötelező.

### Adathalmaz
A generált adathalmaz **Creative Commons Nevezd meg! 4.0 Nemzetközi (CC BY 4.0)** licenc alatt áll. Szabadon használható bármilyen célra (beleértve a kereskedelmi felhasználást is), amennyiben megfelelő forrásmegjelölést ad.

**Fontos**: Az eredeti versenyeredmények a Bolyai Verseny szervezőinek tulajdonát képezik és nyilvánosan elérhetők a verseny weboldalán. A licenc az adatok összeállítására, feldolgozására és dokumentációjára vonatkozik.

Részletek: lásd a `LICENSE` fájlt a repository gyökerében és a `templates/kaggle/LICENSE` fájlt az adathalmazhoz.

## Kapcsolat

Kérdések, javaslatok esetén nyiss egy issue-t a GitHub repository-ban.

---

**Utolsó frissítés**: 2025. december 20.
**Verzió**: 0.1.0 (MVP)
**Lefedett adatok**: 2015-16 - 2024-25 tanévek, Bolyai Anyanyelvi Csapatverseny