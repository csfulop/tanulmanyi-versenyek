# Kiadási Megjegyzések

Ez a dokumentum a Magyar Tanulmányi Versenyek Eredményelemző Rendszer felhasználói kiadási megjegyzéseit tartalmazza.

---

## Verzió 0.4.0 - Iskolanév-normalizálás (2026. január 5.)

### Összefoglaló
Normalizálja az összes iskolanevet a hivatalos magyar iskolaadatbázis (KIR) alapján, hozzáadja a vármegye és régió adatokat, és drámaian javítja az adatminőséget. Az iskolanevek most konzisztensek az évek között, és lehetővé válik a földrajzi elemzés vármegye és régió szerint.

### Újdonságok
- **Automatikus iskolanév-normalizálás**: Minden iskolanév párosításra kerül a hivatalos KIR (Köznevelési Információs Rendszer) adatbázissal fuzzy matching használatával. Az idővel nevet változtató iskolák most az aktuális hivatalos nevükkel jelennek meg, így a rangsorok pontosak és konzisztensek.
- **Vármegye és régió adatok**: Minden iskola most rendelkezik vármegye és régió információval a KIR adatbázisból. Elemezheted a versenyeredményeket földrajzi régió szerint és összehasonlíthatod az oktatási eredményeket Magyarország-szerte.
- **Vármegye és régió rangsorok**: Az elemzési notebook most tartalmaz vármegye és régió rangsorokat (darabszám és súlyozott alapon), így láthatod, hogy Magyarország mely területei teljesítenek a legjobban a versenyen.
- **Átfogó audit nyomvonal**: Minden iskolapárosítási döntés dokumentálva van egy audit fájlban, amely megmutatja a megbízhatósági pontszámokat, párosítási módszereket (automatikus vs manuális) és magyarázatokat. Teljes átláthatóság az adatminőség-javításokba.
- **Manuális felülírási rendszer**: A speciális esetek és alacsony megbízhatóságú párosítások manuálisan javíthatók egy egyszerű CSV mapping fájl segítségével, így te irányítod az adatminőséget.

### Fejlesztések
- **Konzisztens iskolanevek**: 724 iskola (93%) automatikusan párosítva magas megbízhatósággal. Az iskolanév-változatok mint "AMI" vs "Alapfokú Művészeti Iskola" most egyesítve vannak a hivatalos nevek alatt.
- **Jobb városnevek**: A városnevek normalizálva vannak a KIR-ből (pl. "Budapest III. kerület" → "Budapest III."), biztosítva a konzisztenciát a hivatalos közigazgatási határokkal.
- **Továbbfejlesztett szűrés**: Az iskola és város rangsorok most támogatják a vármegye és régió szerinti szűrést a meglévő szűrők (év, évfolyam, város) mellett.
- **50x gyorsabb feldolgozás**: Az iskolapárosítás optimalizálva 9 percről 10 másodpercre city-indexed keresés és előszűrés használatával. A teljes pipeline idő csökkent ~24 percről ~15 percre.

### Adatminőség
- **Iskolanév-konszolidáció**: 779 egyedi iskola-város kombináció párosítva 613 hivatalos iskolához. A több név alatt megjelenő iskolák most egyesítve vannak, pontos teljesítménykövetést biztosítva.
- **Földrajzi adatok teljesek**: Az iskolák 100%-a most rendelkezik vármegye és régió információval (korábban 0%). Minden adat hivatalos kormányzati adatbázisból származik.
- **Magas párosítási megbízhatóság**: Az iskolák 93%-a automatikusan párosítva ≥90% megbízhatósággal. 7% manuális mapping fájl alapján párosítva speciális esetekre. Nulla alacsony megbízhatóságú iskola maradt az adathalmazban.
- **Bezárt iskolák kizárva**: 1 iskola nem található a KIR adatbázisban (bezárt) és ki lett zárva az adathalmazból, biztosítva hogy csak aktív iskolák szerepelnek.

### Visszafelé nem kompatibilis változások
- **Séma változás**: A `megye` oszlop (üres) eltávolítva. Új `varmegye` (vármegye) és `regio` (régió) oszlopok hozzáadva. Ha van kódod ami a `megye` oszlopra hivatkozik, frissítsd `varmegye`-re.
- **Script átszámozás**: A 03-as lépés most a KIR adatbázis letöltés. A korábbi 03-as lépés (összevonás) most 04-es. Frissítsd az automatizálási scripteket ennek megfelelően.
- **Statisztikák változtak**: Az adathalmaz most 3231 rekordot tartalmaz (3233-ról), 613 iskolát (766-ról), 260 várost (261-ről). Ez az iskolanév-konszolidáció és a bezárt iskolák kizárása miatt van.

### Ismert korlátozások
- **Történelmi névváltozások nem követettek**: Az iskolák az aktuális hivatalos nevükkel jelennek meg a KIR-ből. Ha egy iskola 2020-ban nevet változtatott, minden történelmi eredmény az új nevet mutatja.
- **Bezárt iskolák kizárva**: A jelenlegi KIR adatbázisban nem szereplő iskolák ki vannak zárva. Ez befolyásolhatja a történelmi elemzést, ha iskolák bezártak a versenyévek között.
- **Manuális mapping karbantartás**: A manuális iskolapárosítási fájl időszakos felülvizsgálatot igényel, ahogy az iskolák nevet változtatnak vagy bezárnak.

### Frissítési útmutató
1. Legfrissebb kód letöltése: `git pull`
2. Függőségek telepítése: `poetry install` (hozzáadja a rapidfuzz, beautifulsoup4 csomagokat)
3. KIR adatbázis letöltése: `poetry run python 03_download_helper_data.py`
4. Pipeline újrafuttatása: `poetry run python 04_merger_and_excel.py`

### Statisztikák
- Összes rekord: 3231 (3233-ról)
- Egyedi iskolák: 613 (766-ról a névkonszolidáció után)
- Városok: 260 (261-ről)
- Automatikusan párosított iskolák (magas megbízhatóság): 661 (85%)
- Automatikusan párosított iskolák (közepes megbízhatóság): 63 (8%)
- Manuálisan párosított iskolák: 54 (7%)
- Kizárt iskolák: 1 (0,1%)
- Sikeres tesztek: 100/100

---

## Verzió 0.3.0 - Adatminőség és használhatóság (2025. december 26.)

### Összefoglaló
Javítja az adatminőséget városnév-tisztítással és fejleszti a notebook használhatóságát navigációs és szűrési funkciókkal. A városnevek most konzisztensek az adathalmazban, így a rangsorok pontosabbak és megbízhatóbbak.

### Újdonságok
- **Városnév-tisztító rendszer**: Automatikusan javítja a városnév-variációkat egy manuális leképezési fájl segítségével. A kis/nagybetű inkonzisztenciák (MISKOLC → Miskolc), külterületek (Debrecen-Józsa → Debrecen) és hiányzó budapesti kerületek (Budapest → Budapest II.) most normalizálva vannak, biztosítva, hogy az azonos városból származó iskolák együtt jelenjenek meg a rangsorokban.
- **Önálló városellenőrző**: Futtasd a `python -m tanulmanyi_versenyek.validation.city_checker` parancsot a le nem képezett városvariációk észleléséhez és az adatminőség ellenőrzéséhez a teljes folyamat futtatása nélkül.
- **Notebook tartalomjegyzék**: Gyorsan navigálj bármelyik elemzési szekcióhoz kattintható linkekkel. Egy jól látható figyelmeztetés biztosítja, hogy végrehajtsd az előkészítő szekciókat (importok, adatbetöltés, segédfüggvények) mielőtt az elemzéshez ugranál.
- **Városszűrő az iskolai rangsorokhoz**: Szűrd az iskolai rangsorokat város szerint, hogy konkrét régiókra fókuszálj. Támogatja az egyetlen várost ("Budapest II."), több várost (["Budapest II.", "Debrecen"]), vagy az összes várost (alapértelmezett).
- **Jobb táblázatmegjelenítés**: A rangsorok most a teljes kért sormennyiséget mutatják (DISPLAY_TOP_N) ahelyett, hogy 5 felső + 5 alsó sorra csonkolnák. Az iskolakeresés minden eredményt megjelenít csonkítás nélkül.

### Fejlesztések
- **Konzisztens városnevek**: 30 javítás alkalmazva az adathalmazban. A "MISKOLC" és "Miskolc" iskolái most együtt jelennek meg, pontosabb városi és iskolai rangsorokat biztosítva.
- **Átlátható adattisztítás**: Minden városjavítás dokumentálva van egy ember által olvasható CSV fájlban (`config/city_mapping.csv`) minden változtatás magyarázatával. Az érvényes variációk (azonos iskolanév különböző városokban) megőrzésre és szándékosként megjelölésre kerülnek.
- **Továbbfejlesztett validációs jelentés**: A validációs jelentések most városleképezési statisztikákat is tartalmaznak (alkalmazott javítások, érvényes variációk, le nem képezett variációk), teljes rálátást adva az adatminőség-javításokra.

### Adatminőség
- **Városvariációk teljesen kezelve**: 9 városnév-probléma javítva (kis/nagybetű normalizálás, külterület-leképezés, budapesti kerület hozzáadások). 13 érvényes variáció dokumentálva és megőrizve (azonos nevű iskolák különböző városokban). Nulla le nem képezett variáció maradt.
- **Javított rangsor-pontosság**: A városi rangsorok most 261 várost mutatnak (264-ről csökkent), mert az olyan variációk, mint "MISKOLC" és "Miskolc" összevonásra kerültek. Az iskolai rangsorok pontosabbak, mivel az iskolák már nem oszlanak meg városnév-variációk között.
- **Ellenőrizhető javítások**: Minden városjavítás dokumentálva van iskolanévvel, eredeti várossal, javított várossal és emberi magyarázattal. Áttekintheted vagy módosíthatod a leképezési fájlt az elemzési igényeidnek megfelelően.

### Ismert korlátozások
- **Iskolanév-variációk még nem kezelve**: Az iskolák még mindig több név alatt jelennek meg a hivatalos névváltozások miatt az idő során (pl. "Baár-Madas Református Gimnázium és Általános Iskola" vs "Baár-Madas Református Gimnázium, Általános Iskola és Kollégium"). Ez egy jövőbeli kiadásra tervezett.
- **Manuális leképezési fájl karbantartás**: A városjavítások manuális áttekintést és a CSV fájl frissítését igénylik. Az automatizált városnév-észlelés külső adatbázisok használatával még nincs implementálva.
- **Nincsenek interaktív widgetek**: A notebook paramétereket még mindig kódcellákban kell szerkeszteni. Legördülő menük és csúszkák jövőbeli kiadásokra tervezettek.

### Statisztikák
- Összes rekord: 3 233
- Egyedi iskolák: 766
- Városok: 261 (264-ről csökkent a tisztítás után)
- Alkalmazott városjavítások: 30
- Érvényes városvariációk: 13
- Le nem képezett variációk: 0
- Sikeres tesztek: 84/84

---

## Verzió 0.2.0 - Interaktív Elemzés (2025. december 22.)

### Összefoglaló
Jupyter notebook hozzáadása az interaktív adatfelfedezéshez iskolai és városi rangsorokkal, keresési funkcióval és kétnyelvű támogatással. A notebook futtatható Kaggle-ön vagy helyben, így az adathalmaz hozzáférhetővé válik elemzők és kutatók számára.

### Újdonságok
- **Jupyter notebook interaktív elemzéshez**: Fedezd fel a versenyeredményeket használatra kész kódcellákkal. Módosítsd a paramétereket (évfolyam, időszak, top-N) és futtasd újra a frissített eredményekért.
- **Iskolai rangsorok két módszerrel**: Nézd meg a legjobban teljesítő iskolákat részvételi darabszám (hányszor helyeztek) vagy súlyozott pontszám (konfigurálható küszöb, pl. top-3: 1. helyezés = 3 pont, 2. = 2 pont, 3. = 1 pont) alapján. Szűrhető évfolyam és időszak szerint.
- **Városi rangsorok két módszerrel**: Fedezd fel, mely városok adják a legtöbb döntős csapatot, ugyanazokkal a darabszám és súlyozott pontozási módszerekkel, mint az iskolai rangsoroknál.
- **Iskola keresési funkció**: Találj meg konkrét iskolákat részleges névegyezés alapján és tekintsd meg teljes versenyhistóriájukat minden éven és évfolyamon keresztül.
- **Kétnyelvű támogatás**: Minden magyarázat és eredmény megjelenik magyarul és angolul is, így az adathalmaz hozzáférhető nemzetközi kutatók számára.
- **Többféle futtatási lehetőség**: Futtasd Kaggle platformon (ajánlott), helyben Poetry-vel (gyors), vagy Docker-rel (pontos Kaggle környezet, 20GB letöltés).

### Fejlesztések
- **Helyes iskolaszámlálás**: Az iskolák most egyetlen entitásként számítanak, még akkor is, ha a városnevek változnak az évek során (pl. "Budapest" vs "Budapest II."). Korábban ugyanaz az iskola többször is megjelenhetett a rangsorokban.
- **Magyar ábécé szerinti rendezés**: Az iskola- és városnevek most helyesen rendeznek a magyar nyelvtan szabályai szerint (az á az 'a' változataként kezelve, nem külön karakterként a 'z' után).
- **Determinisztikus holtverseny-kezelés**: Amikor több iskolának vagy városnak azonos a darabszáma vagy pontszáma, most konzisztens ábécé sorrendben jelennek meg minden futtatáskor.

### Adatminőség
- **Városnév-normalizálás tudatosítása**: Dokumentálva, hogy 15 iskola esetében városnév-variációk vannak a forrásadatokban (pl. "Budapest" vs "Budapest VII."). A rangsorok most helyesen kezelik ezt úgy, hogy csak név szerint csoportosítanak.
- **Iskolanév-variációk dokumentálása**: Azonosítva 70+ iskolacsoport, amelyet hivatalos névváltozások érintenek az idő során. "Ismert adatminőségi korlátozások" szekció hozzáadva az adathalmaz dokumentációjához felhasználói ajánlásokkal.
- **Adatautenticitás megőrzése**: Minden adat pontosan úgy marad, ahogy a verseny weboldalán publikálva van. Nincs szubjektív normalizálás alkalmazva, biztosítva az átláthatóságot és reprodukálhatóságot.

### Hibajavítások
- Javítva a rangsorolási logika, amely helytelenül külön bejegyzésekre osztotta az iskolákat több városnévvel
- Javítva a nem-determinisztikus sorrend, amikor iskoláknak vagy városoknak azonos darabszáma vagy pontszáma volt
- Javítva a helytelen magyar ábécé sorrend, amely az ékezetes karaktereket az összes ASCII betű után helyezte

### Ismert korlátozások
- **Adatminőségi variációk**: Néhány iskola több név alatt jelenik meg a hivatalos névváltozások miatt az idő során (pl. "Baár-Madas Református Gimnázium és Általános Iskola" vs "Baár-Madas Református Gimnázium, Általános Iskola és Kollégium"). A rangsorok ezeket külön iskolákként számolják. Részletekért és ajánlásokért lásd az adathalmaz dokumentációját.
- **Nincsenek interaktív widgetek**: A paramétereket kódcellákban kell szerkeszteni és újrafuttatni. Jövőbeli verziók legördülő menüket és csúszkákat adhatnak hozzá a könnyebb interakcióért.
- **Nincsenek vizualizációk**: Az eredmények csak táblázatként jelennek meg. Diagramok és grafikonok tervezve vannak jövőbeli kiadásokra.
- **Manuális paraméter-konfiguráció**: Minden elemzési szekció konfigurációs változók szerkesztését igényli. Még nincs egyetlen vezérlőpanel.

### Statisztikák
- Összes rekord: 3 233
- Egyedi iskolák: 766
- Városok: 264
- Sikeres tesztek: 22/22
- Notebook cellák: 31
- Támogatott nyelvek: 2 (magyar, angol)

---

## Verzió 0.1.0 - Kezdeti MVP Kiadás (2025. december 20.)

### Összefoglaló
Kezdeti MVP kiadás, amely automatizált adatgyűjtést és elemzést biztosít a Bolyai Anyanyelvi Csapatverseny számára. Ez a kiadás 10 év versenytörténetét (2015-16-tól 2024-25-ig) dolgozza fel egy teljes háromfázisú folyamattal a webes adatgyűjtéstől az Excel riportokig.

### Újdonságok
- **Automatizált adatgyűjtés**: Letölti az összes elérhető versenyeredményt a hivatalos Bolyai weboldalról kézi beavatkozás nélkül. A rendszer kíméli a szervert 5 másodperces késleltetésekkel a lekérések között.
- **Intelligens eredményfeldolgozás**: Automatikusan kezeli a kétfordulós versenyszerkezetet (írásbeli és szóbeli döntő), biztosítva, hogy minden iskola csak egyszer szerepeljen a végleges helyezésével. Speciális kezelés a COVID-19 évekre, amikor nem volt szóbeli döntő.
- **Excel elemzési riportok**: Használatra kész Excel fájlokat készít három munkalappal: teljes adathalmaz, iskolák rangsora (részvételek száma szerint), és városok rangsora (döntős csapatok száma szerint).
- **Adatminőség-ellenőrzés**: Részletes validációs riportokat készít az adatok teljességéről, duplikációkezelésről és minőségi mutatókról az átláthatóság érdekében.
- **Teljes történelmi lefedettség**: Feldolgozza mind a 6 évfolyamot (3-8. osztály) 10 tanéven keresztül, átfogó történelmi perspektívát nyújtva.

### Adatminőség
- **Okos duplikációmegelőzés**: Az összefésülési logika érti a versenyszerkezetet - az írásbeli döntő előzetes helyezéseit automatikusan felülírják a szóbeli döntő végleges helyezései azoknál a csapatoknál, amelyek továbbjutottak. Ez megakadályozza, hogy ugyanaz az iskola kétszer szerepeljen különböző helyezésekkel.
- **Nulla duplikáció**: Az intelligens összefésülés után egyetlen duplikált rekord sem marad az adathalmazban. Minden iskola-év-évfolyam kombináció pontosan egyszer szerepel a helyes végleges helyezéssel.
- **Teljes adatlefedettség**: Minden alapvető mező (év, tantárgy, iskola neve, város, helyezés, évfolyam) teljesen kitöltött, hiányzó értékek nélkül. Csak a megye mező üres, mivel ez az információ nem érhető el a forrás weboldalon.

### Ismert korlátozások
- **Csak egy verseny**: Ez az MVP csak a Bolyai Anyanyelvi Versenyt fedi le. Más tantárgyak (matek, angol, stb.) és más versenyek (OKTV, Zrínyi Ilona) még nem támogatottak.
- **Nincs megyeinformáció**: Az adathalmaz nem tartalmaz megyeadatokat, mert ezek nem érhetők el a forrás weboldalon. Egy jövőbeli verzió hozzáadhatja ezt egy város-megye leképező adatbázison keresztül.
- **Statikus Excel táblák**: Az Excel riport előre kiszámított rangsor táblákat tartalmaz interaktív pivot táblák helyett. A felhasználók saját pivot táblákat készíthetnek az Adatok munkalapból egyedi elemzésekhez.
- **Csak parancssori felület**: A folyamat három különálló Python scriptként fut. Grafikus felület vagy webes irányítópult még nem érhető el.

### Frissítési útmutató
Ez az első kiadás. Telepítés:

```bash
# Repository klónozása
git clone <repository-url>
cd tanulmanyi-versenyek

# Függőségek telepítése
poetry install

# Böngésző telepítése webes adatgyűjtéshez (egyszeri beállítás)
poetry run playwright install chromium

# Folyamat futtatása
poetry run python 01_raw_downloader.py
poetry run python 02_html_parser.py
poetry run python 03_merger_and_excel.py
```

### Statisztikák
- Összes rekord: 3 233
- Egyedi iskolák: 766
- Városok: 264
- Lefedett tanévek: 10 (2015-16-tól 2024-25-ig)
- Évfolyamok: 6 (3-8. osztály)
- Sikeres tesztek: 16/16
