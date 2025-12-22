# Bolyai Anyanyelvi Csapatverseny Eredmények (2015-2025)

## Adathalmaz leírása

Ez az adathalmaz a **Bolyai Anyanyelvi Csapatverseny** 10 évnyi történelmi eredményét tartalmazza, amely Magyarország egyik legrangosabb általános és középiskolai tanulmányi versenye.

**Mit tartalmaz:**
- 3233 versenyeredmény a 2015-16-os és 2024-25-ös tanévek között
- 766 különböző iskola 264 városból Magyarország-szerte
- Csapat helyezések 3-8. osztályos kategóriákban
- Írásbeli döntő és szóbeli döntő eredményei
- Interaktív Jupyter notebook az adatok feltárásához
- Kétnyelvű dokumentáció (magyar és angol)

**Kontextus:**
A Bolyai Verseny a magyar nyelvi készségeket teszteli csapatmunka alapú feladatokkal, évente megrendezve 3-8. osztályos tanulók számára. Ez az adathalmaz egy évtized versenyteljesítményét reprezentálja a magyar oktatási rendszerben.

**Felhasználási lehetőségek:**
- Iskolák teljesítményének elemzése időben
- Regionális oktatási eredmények összehasonlítása
- Legjobban teljesítő iskolák és városok azonosítása
- Verseny részvételi minták tanulmányozása
- Oktatási adatvizualizációs projektek

## Fájlok az adathalmazban

### `master_bolyai_anyanyelv.csv`
A Bolyai Anyanyelvi Csapatverseny teljes eredményhalmaza (2015-2025). 3233 rekordot tartalmaz iskolanevekkel, városokkal, helyezésekkel, évfolyamokkal és tanévekkel. Pontosvesszővel elválasztott formátum, UTF-8 kódolás. Fő adatfájl az elemzéshez.

### `README.hu.md`
Magyar nyelvű dokumentáció. Tartalmazza az adathalmaz leírását, adatgyűjtési módszertant, oszlopdefiníciókat, használati példákat, ismert adatminőségi korlátozásokat és licencinformációkat. Teljes referencia útmutató magyarul.

### `README.en.md`
Angol nyelvű dokumentáció. Tartalmazza az adathalmaz leírását, adatgyűjtési módszertant, oszlopdefiníciókat, használati példákat, ismert adatminőségi korlátozásokat és licencinformációkat. Teljes referencia útmutató angolul.

### `LICENSE`
Creative Commons Nevezd meg! 4.0 Nemzetközi (CC BY 4.0) licenc. Meghatározza a használati feltételeket, forrásmegjelölési követelményeket és az adathalmaz engedélyeit. Szabadon használható megfelelő forrásmegjelöléssel.

## Adatok eredete és gyűjtése

### Források

A Bolyai Verseny hivatalos weboldala: https://magyar.bolyaiverseny.hu/verseny/archivum/eredmenyek.php

Az adatok a szervezők által nyilvánosan közzétett hivatalos versenyeredményeket reprezentálják.

### Gyűjtési módszertan

Automatizált webgyűjtés Python használatával, Playwright könyvtárral a böngésző automatizáláshoz és BeautifulSoup-pal a HTML feldolgozáshoz.

**Folyamat:**
1. Automatizált navigáció a versenyeredmény oldalakon az összes tanévre (2015-16-tól 2024-25-ig) és évfolyamra (3-8. osztály)
2. Udvarias adatgyűjtés 5 másodperces késleltetéssel a lekérések között a szerver túlterhelésének elkerülése érdekében
3. HTML táblázatok kinyerése és strukturált formátumba alakítása
4. Háromfázisú feldolgozási folyamat: (a) nyers HTML letöltés, (b) adatkinyerés és normalizálás, (c) összevonás és duplikáció-szűrés
5. Minőségellenőrzés: automatikus ellenőrzések a teljesség és konzisztencia biztosítására

**Duplikáció-szűrési logika:** A szóbeli döntő eredményei (végleges helyezések) elsőbbséget élveznek az írásbeli döntő eredményeivel (előzetes helyezések) szemben, ha mindkettő létezik ugyanarra a csapatra.

**Kimenet:** Pontosvesszővel elválasztott CSV fájl UTF-8 kódolással.

**Gyűjtés dátuma:** 2025. december

## Adathalmaz szerkezete

### Fájl: `master_bolyai_anyanyelv.csv`

Pontosvesszővel elválasztott CSV fájl, amely az összes versenyeredményt tartalmazza.

**Oszlopok:**

| Oszlop | Típus | Leírás | Példa |
|--------|-------|--------|-------|
| `ev` | Szöveg | A verseny tanéve | "2024-25" |
| `targy` | Szöveg | Tantárgy (mindig "Anyanyelv") | "Anyanyelv" |
| `iskola_nev` | Szöveg | Az iskola neve | "Budapesti Kölcsey F. Gimnázium" |
| `varos` | Szöveg | Az iskola városa (Budapest esetén kerületszámmal) | "Budapest III." vagy "Debrecen" |
| `megye` | Szöveg | Megye (jelenleg üres - nem elérhető a forrásban) | "" |
| `helyezes` | Egész szám | A csapat végső helyezése | 1 |
| `evfolyam` | Egész szám | Évfolyam (3-8) | 8 |

**Megjegyzés a `megye` oszlophoz**: Ez az oszlop jelenleg üres, mivel a megyeinformáció nem szerepel a forrásadatokban. Jövőbeli verziók tartalmazhatják ezt város-megye leképezés révén.

## Adatgyűjtési módszertan

### Forrás
Az adatok a Bolyai Verseny hivatalos weboldaláról lettek gyűjtve: https://magyar.bolyaiverseny.hu/verseny/archivum/eredmenyek.php

### Gyűjtési folyamat
- **Automatizált webgyűjtés** Playwright használatával (Python)
- **Udvarias adatgyűjtés**: 5 másodperces késleltetés a lekérések között
- **Adatkinyerés**: HTML táblázat feldolgozás BeautifulSoup-pal
- **Adatvalidáció**: Automatikus minőségellenőrzés és duplikáció-szűrés

### Verseny szerkezete

A Bolyai Verseny két fordulóból áll:

1. **Írásbeli döntő**: Minden kvalifikált csapat részt vesz. Az eredmények előzetes helyezéseket mutatnak.
2. **Szóbeli döntő**: Az egyes évfolyam-kategóriák legjobb 6 csapata jut tovább. Az eredmények végleges helyezéseket mutatnak.

**Fontos**: A szóbeli döntőbe jutott csapatok ebben az adathalmazban csak egyszer szerepelnek, a szóbeli fordulóból származó **végleges helyezésükkel**. A tovább nem jutott csapatok az írásbeli döntőből származó helyezésükkel szerepelnek.

**COVID-19 kivétel**: A 2020-21-es és 2021-22-es tanévekben a szóbeli döntőt törölték. Ezekben az években az írásbeli döntő helyezései számítanak véglegesnek.

## Adatminőség

### Teljességi arány
- ✅ **100% teljes**: `ev`, `targy`, `iskola_nev`, `varos`, `helyezes`, `evfolyam`
- ⚠️ **0% teljes**: `megye` (nem elérhető a forrásadatokban)

### Pontosság
- Az adatok közvetlenül a hivatalos versenyeredményekből származnak
- Automatikus validációs ellenőrzések végrehajtva
- Mintavételek manuális ellenőrzése megtörtént

### Duplikáció-szűrés
- Az írásbeli és szóbeli döntőben is szereplő csapatok deduplikálva
- Csak a végleges helyezések kerültek megtartásra
- 0 duplikált rekord a végső adathalmazban

## Felhasználási lehetőségek

Ez az adathalmaz felhasználható:

- **Oktatási kutatás**: A tanulmányi kiválóság földrajzi eloszlásának elemzése
- **Iskolai teljesítményelemzés**: Iskolák versenyszereplésének és sikerességének nyomon követése
- **Trendelemzés**: Minták azonosítása a versenyeredményekben az idő múlásával
- **Földrajzi elemzés**: Regionális különbségek megértése a tanulmányi teljesítményben
- **Adatvizualizáció**: Térképek, grafikonok és dashboardok készítése
- **Gépi tanulás**: Versenyeredmények előrejelzése, iskolák teljesítmény szerinti klaszterezése

## Korlátozások

1. **Megyeadatok nem elérhetők**: A `megye` oszlop üres, mivel ez az információ nem szerepel a forrásadatokban
2. **Nincsenek tanulónevek**: Adatvédelmi okokból az egyéni tanulónevek nem szerepelnek
3. **Csak egy tantárgy**: Ez az adathalmaz csak az anyanyelvi kategóriát tartalmazza. Más tantárgyak (matematika, angol, stb.) nem szerepelnek
4. **Hiányos történelmi adatok**: Csak a 2015-16-os tanévtől kezdődő eredmények érhetők el
5. **Évfolyam alkategóriák**: A 7-8. osztálynak vannak alkategóriái (általános iskola vs. gimnázium), amelyek az alapévfolyam-számokra vannak normalizálva

## Adatvédelem és etika

- **Nincsenek személyes adatok**: Tanulónevek és más személyazonosításra alkalmas információk nem szerepelnek
- **Csak nyilvános adatok**: Minden adat nyilvánosan elérhető versenyeredményekből lett gyűjtve
- **Etikus adatgyűjtés**: Az automatizált gyűjtés udvarias gyakorlatokat követett megfelelő késleltetésekkel
- **Nem kereskedelmi használat**: Ez az adathalmaz oktatási és kutatási célokra készült

## Hivatkozás

Ha ezt az adathalmazt kutatásában vagy projektjében használja, kérjük hivatkozzon rá:

```
Fülöp Csaba (2025). Bolyai Anyanyelvi Csapatverseny Eredmények Adathalmaz (2015-2025). 
Forrás: https://www.kaggle.com/datasets/csfulop/tanulmanyi-versenyek
Licenc: CC BY 4.0
```

**Eredeti adatforrás:** Bolyai Verseny Hivatalos Weboldal (https://magyar.bolyaiverseny.hu)

## Frissítések és karbantartás

- **Jelenlegi verzió**: 0.1.0 (MVP)
- **Utolsó frissítés**: 2025. december 20.
- **Frissítési gyakoriság**: Tervezett éves frissítések minden versenyév után
- **Jövőbeli fejlesztések**: 
  - Megyeadatok gazdagítása
  - További tantárgyak (matematika, angol, stb.)
  - Más magyar tanulmányi versenyek (OKTV, Zrínyi Ilona)

## Kapcsolat és visszajelzés

Kérdések, javítások vagy javaslatok esetén:

- **GitHub Repository:** https://github.com/csfulop/tanulmanyi-versenyek
- **Kaggle Dataset:** https://www.kaggle.com/datasets/csfulop/tanulmanyi-versenyek
- **Kaggle Notebook:** https://www.kaggle.com/code/csfulop/tanulmanyi-versenyek-eredmenyelemzes

## Elemzési Notebook

Az adathalmaz mellett elérhető egy Jupyter notebook is, amely interaktív elemzési példákat tartalmaz. A notebook tartalmazza az iskolák és városok rangsorait, valamint iskola keresési funkciót.

## Ismert adatminőségi korlátozások

### Iskola- és városnevek következetlensége

Az adathalmaz az iskolák és városok neveit **pontosan úgy tartalmazza, ahogy azok a verseny hivatalos weboldalán szerepelnek**. Ez az alábbi következetlenségeket eredményezi:

**1. Városnevek variációi:**
- Ugyanaz az iskola különböző években különböző városnév-változatokkal szerepelhet
- Példák: "Budapest" vs "Budapest VII.", "Debrecen" vs "Debrecen-Józsa", "MISKOLC" vs "Miskolc"
- **Érintett iskolák száma**: 15

**2. Iskolanevek változásai:**
- Az iskolák hivatalos neve idővel változhat (átszervezés, névváltoztatás)
- Kisebb eltérések az írásmódban vagy rövidítésekben
- Példa: "Baár-Madas Református Gimnázium és Általános Iskola" vs "Baár-Madas Református Gimnázium, Általános Iskola és Kollégium"
- **Érintett iskolacsoportok száma**: 70+

**Hatás a rangsorokra:**
- Ugyanaz az iskola több névváltozattal is megjelenhet a rangsorokban
- A rangsorok így **alsó becslést** adnak az iskolák teljesítményére
- A valós helyezések magasabbak lehetnek, ha az összes névváltozatot összesítenénk

**Miért nem javítottuk ki:**
- Az adatok hűen tükrözik a forrást (hitelesség)
- A "helyes" név meghatározása szubjektív lenne
- A jövőbeli verziók tartalmazhatnak normalizálást

**Javaslat felhasználóknak:**
- Használj részleges névkeresést az iskolák megtalálásához
- Vedd figyelembe, hogy a rangsorok konzervatív becslések
- Ellenőrizd az iskola összes névváltozatát a pontos eredményekhez

## Licenc

Ez az adathalmaz **Creative Commons Nevezd meg! 4.0 Nemzetközi (CC BY 4.0)** licenc alatt áll.

Szabadon megoszthatja és feldolgozhatja ezt az adathalmazt bármilyen célra, beleértve a kereskedelmi felhasználást is, amennyiben megfelelő forrásmegjelölést ad.

### Adatforrás és jogi nyilatkozat

A versenyeredmények ebben az adathalmazban nyilvánosan elérhetők a Bolyai Verseny weboldalán (https://www.bolyaiverseny.hu). A verseny adatkezelési tájékoztatója (https://www.bolyaiverseny.hu/adatkezeles.php) szerint a résztvevők adatai (évfolyam, iskola, helyezés) nyilvánosak, és a résztvevők a nevezéskor hozzájárulásukat adják ehhez.

Ez az adathalmaz csak nyilvánosan elérhető információkat tartalmaz. Magán- vagy regisztrációs adatok nem szerepelnek. A CC BY 4.0 licenc az összeállításra, feldolgozásra, dokumentációra és származékos művekre vonatkozik, nem az alapul szolgáló versenyeredményekre, amelyek a Bolyai Verseny szervezőinek tulajdonát képezik.

A hivatkozási információkért lásd a fenti **Hivatkozás** részt.

---

**Kulcsszavak**: Magyarország, oktatás, tanulmányi verseny, anyanyelv, magyar nyelv, általános iskola, középiskola, csapatverseny, oktatási adatok, iskolai rangsorok
