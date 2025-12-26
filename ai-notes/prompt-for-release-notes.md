# Task: Update Release Notes for v[VERSION] = v0.3.0

You are updating the **user-facing release notes** for version [VERSION] of the Hungarian Academic Competition Results Pipeline project.

## Context

This project is a data pipeline that:
- Downloads competition results from the Bolyai Competition website
- Processes and cleans the data
- Generates analysis reports and datasets
- Provides a Jupyter notebook for interactive exploration

**Target Audience:**
- Data analysts and researchers using the dataset
- Educators analyzing school performance
- Developers integrating the dataset into their projects

**Languages:** Bilingual (Hungarian and English)

## Source Materials

Review the following documents in `dev-history/v[VERSION]/`:
- `step1-requirements.md` - What was planned
- `step4-coding-summary-*.md` - What was implemented
- Any other relevant documentation

Also review:
- Changes to `templates/kaggle/README.*.md` - User-facing documentation
- Changes to `notebooks/competition_analysis.ipynb` - Notebook features
- `data/validation_report.json` - Data quality metrics

## Output Requirements

Update TWO existing files by adding a new version section at the TOP (after the header):

### 1. `RELEASE_NOTES.en.md` (English)

Add this section at the top, right after the file header:

```markdown
---

## Version [VERSION] - [Release Name] ([DATE])

### Summary
[1-2 sentence overview - what's the main focus of this release?]

### What's New
[New features that users can now use - focus on benefits]
- Feature 1: [What it does and why it matters]
- Feature 2: [What it does and why it matters]

### Improvements
[Enhancements to existing features]
- Improvement 1: [What got better]
- Improvement 2: [What got better]

### Data Quality
[Changes to data quality, corrections, cleaning]
- [What data issues were addressed]
- [Statistics: X corrections applied, Y issues resolved]

### Bug Fixes
[Issues that were resolved - if any, otherwise omit this section]
- Fix 1: [What was broken, now fixed]

### Breaking Changes
[Changes that break backward compatibility - if any, otherwise omit this section]
- [What breaks and how to migrate]

### Known Limitations
[What still doesn't work or has limitations]
- [Issue and status]

### Upgrade Instructions
[How to get the new version - if special steps needed, otherwise omit this section]

### Metrics
- Total records: [number]
- Unique schools: [number]
- Cities: [number]
- Tests passing: [number]
```

### 2. `RELEASE_NOTES.hu.md` (Hungarian)

Add the same section structure, translated to Hungarian:

```markdown
---

## Verzió [VERSION] - [Kiadás neve] ([DÁTUM])

### Összefoglaló
[1-2 mondatos áttekintés - mi a kiadás fő fókusza?]

### Újdonságok
[Új funkciók, amiket a felhasználók most már használhatnak - fókusz az előnyökön]
- Funkció 1: [Mit csinál és miért fontos]
- Funkció 2: [Mit csinál és miért fontos]

### Fejlesztések
[Meglévő funkciók javításai]
- Fejlesztés 1: [Mi lett jobb]
- Fejlesztés 2: [Mi lett jobb]

### Adatminőség
[Adatminőségi változások, javítások, tisztítás]
- [Milyen adatproblémák lettek kezelve]
- [Statisztikák: X javítás alkalmazva, Y probléma megoldva]

### Hibajavítások
[Megoldott problémák - ha van, különben hagyd ki ezt a szekciót]
- Javítás 1: [Mi volt elromlva, most javítva]

### Visszafelé nem kompatibilis változások
[Változások, amik megszakítják a visszafelé kompatibilitást - ha van, különben hagyd ki]
- [Mi nem működik és hogyan kell migrálni]

### Ismert korlátozások
[Mi nem működik még vagy korlátozott]
- [Probléma és státusz]

### Frissítési útmutató
[Hogyan lehet megszerezni az új verziót - ha speciális lépések kellenek, különben hagyd ki]

### Statisztikák
- Összes rekord: [szám]
- Egyedi iskolák: [szám]
- Városok: [szám]
- Sikeres tesztek: [szám]
```

## File Structure

The files should maintain this structure:

```markdown
# Release Notes

This document contains user-facing release notes for the Hungarian Academic Competition Results Pipeline project.

---

## Version [LATEST] - [Name] ([Date])
[Latest release content]

---

## Version [PREVIOUS] - [Name] ([Date])
[Previous release content]

---

## Version [OLDER] - [Name] ([Date])
[Older release content]
```

## Writing Guidelines

**DO:**
- Write in **user-centric language** (avoid technical jargon)
- Focus on **benefits** (why it matters to users)
- Use **present tense** ("adds", "improves")
- Be **concise** (bullet points, not paragraphs)
- Include **specific numbers** (X corrections, Y tests)
- Be **honest** about limitations
- Provide **context** for why changes were made
- **Omit empty sections** (if no bug fixes, don't include that section)

**DON'T:**
- List file names or technical implementation details
- Use passive voice
- Include information only relevant to developers
- Hide breaking changes or known issues
- Write long paragraphs
- Include empty sections with "None" or "N/A"

## Example Entry

**Good:**
"✅ **City name cleaning**: All city name variations are now normalized (9 corrections applied). Schools from 'MISKOLC' and 'Miskolc' now appear together in rankings, providing more accurate results."

**Bad:**
"Updated src/tanulmanyi_versenyek/validation/city_checker.py to implement city mapping functionality with 23 entries in config/city_mapping.csv."

## Validation

Before finalizing, verify:
- [ ] New version section added at the TOP of both files (after header)
- [ ] Both language versions have identical structure
- [ ] All statistics are accurate (check validation_report.json)
- [ ] User benefits are clearly stated
- [ ] No technical jargon or file paths
- [ ] Breaking changes are clearly marked (if any)
- [ ] Known limitations are honestly stated
- [ ] Empty sections are omitted (not marked as "None")
- [ ] Separator line (---) added between versions

## Output Location

Update these existing files:
- `RELEASE_NOTES.en.md` (project root)
- `RELEASE_NOTES.hu.md` (project root)

**Important:** Add the new version section at the TOP, right after the file header, so the latest release is always first.
