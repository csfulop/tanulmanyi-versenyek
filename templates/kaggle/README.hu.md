# Bolyai Anyanyelvi Csapatverseny Eredmények (2015-2025)

## Adathalmaz leírása

Ez az adathalmaz a **Bolyai Anyanyelvi Csapatverseny** 10 évnyi történelmi eredményét tartalmazza, amely Magyarország egyik legrangosabb általános és középiskolai tanulmányi versenye.

**Mit tartalmaz:**
- 3231 versenyeredmény a 2015-16-os és 2024-25-ös tanévek között
- 613 különböző iskola 260 városból Magyarország-szerte
- Csapat helyezések 3-8. osztályos kategóriákban
- Írásbeli döntő és szóbeli döntő eredményei
- Iskolanevek normalizálva a hivatalos magyar iskolaadatbázis (KIR) alapján
- Vármegye és régió adatok minden iskolához
- Interaktív Jupyter notebook az adatok feltárásához
- Kétnyelvű dokumentáció (magyar és angol)

**Kontextus:**
A Bolyai Verseny a magyar nyelvi készségeket teszteli csapatmunka alapú feladatokkal, évente megrendezve 3-8. osztályos tanulók számára. Ez az adathalmaz egy évtized versenyteljesítményét reprezentálja a magyar oktatási rendszerben.

**Felhasználási lehetőségek:**
- Iskolák teljesítményének elemzése időben
- Regionális oktatási eredmények összehasonlítása
- Legjobban teljesítő iskolák, városok, vármegyés és régiók azonosítása
- Verseny részvételi minták tanulmányozása
- Oktatási adatvizualizációs projektek

## Fájlok az adathalmazban

### `master_bolyai_anyanyelv.csv`
A Bolyai Anyanyelvi Csapatverseny teljes eredményhalmaza (2015-2025). 3231 rekordot tartalmaz a hivatalos magyar iskolaadatbázis (KIR) alapján normalizált iskolanevekkel, városokkal, vármegyékkel, régiókkal, helyezésekkel, évfolyamokkal és tanévekkel. Pontosvesszővel elválasztott formátum, UTF-8 kódolás. Fő adatfájl az elemzéshez.

### `README.hu.md`
Magyar nyelvű dokumentáció. Tartalmazza az adathalmaz leírását, adatgyűjtési módszertant, oszlopdefiníciókat, használati példákat, ismert adatminőségi korlátozásokat és licencinformációkat. Teljes referencia útmutató magyarul.

### `README.en.md`
Angol nyelvű dokumentáció. Tartalmazza az adathalmaz leírását, adatgyűjtési módszertant, oszlopdefiníciókat, használati példákat, ismert adatminőségi korlátozásokat és licencinformációkat. Teljes referencia útmutató angolul.

### `LICENSE`
Creative Commons Nevezd meg! 4.0 Nemzetközi (CC BY 4.0) licenc. Meghatározza a használati feltételeket, forrásmegjelölési követelményeket és az adathalmaz engedélyeit. Szabadon használható megfelelő forrásmegjelöléssel.

## Adatok eredete és gyűjtése

### Források

**Versenyeredmények:** Bolyai Verseny hivatalos weboldala - https://magyar.bolyaiverseny.hu/verseny/archivum/eredmenyek.php

**Iskolaadatok:** KIR (Köznevelési Információs Rendszer) hivatalos adatbázis - https://kir.oktatas.hu/kirpub/index

Az adatok a szervezők által nyilvánosan közzétett hivatalos versenyeredményeket és iskolainformációkat reprezentálják.

### Gyűjtési módszertan

Automatizált webgyűjtés Python használatával, Playwright könyvtárral a böngésző automatizáláshoz és BeautifulSoup-pal a HTML feldolgozáshoz.

**Folyamat:**
1. Automatizált navigáció a versenyeredmény oldalakon az összes tanévre (2015-16-tól 2024-25-ig) és évfolyamra (3-8. osztály)
2. Udvarias adatgyűjtés 5 másodperces késleltetéssel a lekérések között a szerver túlterhelésének elkerülése érdekében
3. HTML táblázatok kinyerése és strukturált formátumba alakítása
4. Iskolanevek normalizálása a hivatalos magyar iskolaadatbázis (KIR - Köznevelési Információs Rendszer) alapján
5. Fuzzy matching algoritmus (token_set_ratio) a verseny iskolanevek és hivatalos KIR nevek párosításához
6. Négyfázisú feldolgozási folyamat: (a) nyers HTML letöltés, (b) adatkinyerés, (c) KIR adatbázis letöltés, (d) iskolapárosítás és összevonás
7. Minőségellenőrzés: automatikus ellenőrzések a teljesség és konzisztencia biztosítására

**Duplikáció-szűrési logika:** A szóbeli döntő eredményei (végleges helyezések) elsőbbséget élveznek az írásbeli döntő eredményeivel (előzetes helyezések) szemben, ha mindkettő létezik ugyanarra a csapatra.

**Kimenet:** Pontosvesszővel elválasztott CSV fájl UTF-8 kódolással.

**Gyűjtés dátuma:** 2026. január

## Adathalmaz szerkezete

### Fájl: `master_bolyai_anyanyelv.csv`

Pontosvesszővel elválasztott CSV fájl, amely az összes versenyeredményt tartalmazza.

**Oszlopok:**

| Oszlop | Típus | Leírás | Példa |
|--------|-------|--------|-------|
| `ev` | Szöveg | A verseny tanéve (formátum: "YYYY-YY") | "2024-25" |
| `targy` | Szöveg | Tantárgy (mindig "Anyanyelv") | "Anyanyelv" |
| `iskola_nev` | Szöveg | Az iskola hivatalos neve (KIR adatbázisból) | "Abádszalóki Kovács Mihály Általános Iskola" |
| `varos` | Szöveg | Az iskola városa, Budapest esetén tartalmazza a kerületet is (KIR-ből normalizálva) | "Budapest III." vagy "Debrecen" |
| `varmegye` | Szöveg | Az iskola vármegyéje (KIR adatbázisból) | "Jász-Nagykun-Szolnok" |
| `regio` | Szöveg | Az iskola régiója (KIR adatbázisból) | "Észak-Alföld" |
| `helyezes` | Egész szám | Végső helyezés | 1 |
| `evfolyam` | Egész szám | Évfolyam (3-8) | 8 |

**Megjegyzés az iskolanevekhez**: Minden iskolanév a hivatalos magyar iskolaadatbázis (KIR - Köznevelési Információs Rendszer) alapján lett normalizálva fuzzy matching használatával. Ez biztosítja a konzisztenciát az évek között, még akkor is, ha az iskolák nevet változtatnak vagy kisebb eltérések vannak a versenyeredményekben.

**Megjegyzés a földrajzi adatokhoz**: A vármegye és régió adatok a KIR adatbázisból származnak és az egyes iskolák hivatalos közigazgatási helyét reprezentálják.

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
- ✅ **100% teljes**: `ev`, `targy`, `iskola_nev`, `varos`, `varmegye`, `regio`, `helyezes`, `evfolyam`

### Pontosság
- Iskolanevek normalizálva a hivatalos KIR adatbázis (Köznevelési Információs Rendszer) alapján
- Fuzzy matching algoritmus 80%+ megbízhatósági küszöbbel
- Manuális felülírási rendszer speciális esetekre
- Automatikus validációs ellenőrzések végrehajtva
- Átfogó audit nyomvonal minden párosítási döntésről

### Iskolanév-normalizálás
- **Automatikus párosítás**: 724 iskola (93%) automatikusan párosítva magas megbízhatósággal (≥90%)
- **Manuális felülírások**: 54 iskola (7%) manuális mapping fájl alapján párosítva
- **Eldobott iskolák**: 1 iskola eldobva (nem található a KIR adatbázisban, bezárt)
- **Audit fájl**: Minden párosítási döntés teljes nyilvántartása elérhető a forráskód repository-ban

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

1. **Nincsenek tanulónevek**: Adatvédelmi okokból az egyéni tanulónevek nem szerepelnek
2. **Csak egy tantárgy**: Ez az adathalmaz csak az anyanyelvi kategóriát tartalmazza. Más tantárgyak (matematika, angol, stb.) nem szerepelnek
3. **Hiányos történelmi adatok**: Csak a 2015-16-os tanévtől kezdődő eredmények érhetők el
4. **Évfolyam alkategóriák**: A 7-8. osztálynak vannak alkategóriái (általános iskola vs. gimnázium), amelyek az alapévfolyam-számokra vannak normalizálva
5. **Iskolanév-változások**: Történelmi névváltozások nincsenek követve - az iskolák a KIR adatbázisból származó aktuális hivatalos nevükkel jelennek meg
6. **Bezárt iskolák**: A jelenlegi KIR adatbázisban nem található iskolák ki vannak zárva az adathalmazból

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

- **Jelenlegi verzió**: 0.4.0
- **Utolsó frissítés**: 2026. január 5.
- **Frissítési gyakoriság**: Tervezett éves frissítések minden versenyév után
- **Jövőbeli fejlesztések**: 
  - További tantárgyak (matematika, angol, stb.)
  - Más magyar tanulmányi versenyek (OKTV, Zrínyi Ilona)

## Kapcsolat és visszajelzés

Kérdések, javítások vagy javaslatok esetén:

- **GitHub Repository:** https://github.com/csfulop/tanulmanyi-versenyek
- **Kaggle Dataset:** https://www.kaggle.com/datasets/csfulop/tanulmanyi-versenyek
- **Kaggle Notebook:** https://www.kaggle.com/code/csfulop/tanulmanyi-versenyek-eredmenyelemzes

## Elemzési Notebook

Az adathalmaz mellett elérhető egy Jupyter notebook is, amely interaktív elemzési példákat tartalmaz. A notebook tartalmazza az iskolák és városok rangsorait, valamint iskola keresési funkciót.

## Adatminőség-javítási folyamat

### Iskolanevek normalizálása

Az adathalmaz minden iskolaneve a hivatalos magyar iskolaadatbázis (KIR - Köznevelési Információs Rendszer) alapján lett normalizálva:

- **Automatikus párosítás**: Fuzzy string matching algoritmus (token_set_ratio) párosítja a verseny iskolaneveit a hivatalos KIR nevekkel
- **Megbízhatósági küszöbök**: 
  - Magas megbízhatóság (≥90%): Automatikusan alkalmazva (661 iskola, 85%)
  - Közepes megbízhatóság (≥80%): Automatikusan alkalmazva (63 iskola, 8%)
  - Alacsony megbízhatóság (<80%): Eldobva az adathalmazból (0 iskola)
- **Manuális felülírások**: 54 iskola (7%) manuális mapping fájl alapján párosítva speciális esetekre
- **Manuális eldobások**: 1 iskola (0,1%) manuálisan kizárva (nincs a KIR-ben, bezárt)
- **Földrajzi adatok**: Vármegye és régió információk kinyerve a KIR adatbázisból

A normalizálási folyamat biztosítja a konzisztenciát az évek között, még akkor is, ha az iskolák nevet változtatnak vagy kisebb eltérések vannak a versenyeredményekben.

### Városnevek normalizálása

A városnevek az iskolapárosítási folyamat részeként normalizálódnak:

- **Forrás**: Hivatalos városnevek a KIR adatbázisból
- **Budapesti kerületek**: Megőrizve a KIR-ből (pl. "Budapest III.")
- **Előfeldolgozás**: Egyszerű javítások alkalmazva párosítás előtt (pl. "Debrecen-Józsa" → "Debrecen")

A tisztítási módszertan és audit nyomvonal részleteiért lásd a projekt repository-ját.

## Ismert adatminőségi korlátozások

### Iskolanév-változatok

**Állapot**: ✅ **Kezelve a 0.4.0-ban**

Minden iskolanév a hivatalos KIR adatbázis alapján lett normalizálva fuzzy matching használatával:
- Az iskolák 93%-a automatikusan párosítva magas megbízhatósággal
- 7% manuális mapping fájl alapján párosítva
- A KIR adatbázisban nem található iskolák (valószínűleg bezártak) ki vannak zárva

**Történelmi névváltozások**: Az iskolák a KIR adatbázisból származó aktuális hivatalos nevükkel jelennek meg. A történelmi névváltozatok nincsenek követve ebben a verzióban.

### Városnév-változatok

**Állapot**: ✅ **Kezelve a 0.4.0-ban**

Minden városnév a KIR adatbázis párosítási folyamatán keresztül normalizálódott. A városnevek konzisztensek és megbízhatóak.

## Licenc

Ez az adathalmaz **Creative Commons Nevezd meg! 4.0 Nemzetközi (CC BY 4.0)** licenc alatt áll.

Szabadon megoszthatja és feldolgozhatja ezt az adathalmazt bármilyen célra, beleértve a kereskedelmi felhasználást is, amennyiben megfelelő forrásmegjelölést ad.

### Adatforrás és jogi nyilatkozat

A versenyeredmények ebben az adathalmazban nyilvánosan elérhetők a Bolyai Verseny weboldalán (https://www.bolyaiverseny.hu). A verseny adatkezelési tájékoztatója (https://www.bolyaiverseny.hu/adatkezeles.php) szerint a résztvevők adatai (évfolyam, iskola, helyezés) nyilvánosak, és a résztvevők a nevezéskor hozzájárulásukat adják ehhez.

Ez az adathalmaz csak nyilvánosan elérhető információkat tartalmaz. Magán- vagy regisztrációs adatok nem szerepelnek. A CC BY 4.0 licenc az összeállításra, feldolgozásra, dokumentációra és származékos művekre vonatkozik, nem az alapul szolgáló versenyeredményekre, amelyek a Bolyai Verseny szervezőinek tulajdonát képezik.

A hivatkozási információkért lásd a fenti **Hivatkozás** részt.

---

**Kulcsszavak**: Magyarország, oktatás, tanulmányi verseny, anyanyelv, magyar nyelv, általános iskola, középiskola, csapatverseny, oktatási adatok, iskolai rangsorok
