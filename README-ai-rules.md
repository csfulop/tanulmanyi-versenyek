# Project Coding Rules

**Quick Reference:** Essential do's and don'ts for this project.

**Need context?** See `step4-coding-summary-*.md` files for detailed explanations of why these rules exist.

**When in doubt:** Ask! These rules capture lessons learned - if something seems unclear or conflicts with a new situation, request clarification rather than guessing.

## Project Structure & Imports
- ✅ ALWAYS: `from tanulmanyi_versenyek.* import ...`
- ❌ NEVER: `from src.* import ...`
- ✅ ALWAYS: Configure Poetry with `packages = [{include = "tanulmanyi_versenyek", from = "src"}]`
- ✅ ALWAYS: Use `Path` objects for file operations, not strings

## Configuration Management
- ✅ ALWAYS: All file paths in `config['paths']` section
- ❌ NEVER: Duplicate paths in other config sections (DRY principle)
- ✅ ALWAYS: Use `get_config()` function to access configuration
- ✅ ALWAYS: Update `config.yaml` for selectors/URLs, never hardcode

## Logging
- ✅ ALWAYS: Call `setup_logging()` at start of every main script
- ✅ ALWAYS: Log progress, counts, and errors for debugging
- ✅ ALWAYS: Use both console and file handlers

## Playwright & Web Scraping
- ✅ ALWAYS: Use `wait_for_function()` with specific DOM conditions for AJAX content
- ❌ NEVER: Use `time.sleep()` for waiting on dynamic content
- ⚠️ CAUTION: `wait_for_load_state('networkidle')` completes BEFORE DOM updates
- ✅ ALWAYS: Verify selectors against actual HTML, not design documents
- ✅ ALWAYS: Wait for dropdowns to have options: `page.wait_for_function('() => document.querySelectorAll("selector option[value]:not([value=\"\"])").length > 0')`
- ✅ ALWAYS: Use exact strings from website (e.g., "8. osztály - általános iskolai kategória")

## HTML Parsing
- ✅ ALWAYS: Use BeautifulSoup when you need to preserve HTML structure (like `<br>` tags)
- ❌ NEVER: Use `pandas.read_html()` when `<br>` tags matter - it strips them
- ✅ ALWAYS: Replace `<br>` tags with `\n` before extracting text: `br.replace_with('\n')`
- ✅ ALWAYS: Split school/city using newline separator from `<br>` tags
- ❌ NEVER: Use `rsplit(' ', 1)` for school/city - fails for "Budapest IV." and multi-word cities

## Error Handling
- ✅ ALWAYS: Use per-item try-catch in batch operations
- ✅ ALWAYS: Log errors but continue processing remaining items
- ✅ ALWAYS: Raise exceptions for unexpected data formats (fail fast)
- ❌ NEVER: Silently use defaults/empty values for missing data

## Data Processing
- ✅ ALWAYS: Check for existing output files before processing (idempotency)
- ✅ ALWAYS: Use semicolon (`;`) delimiter for CSV files
- ✅ ALWAYS: Use UTF-8 encoding for all file operations
- ✅ ALWAYS: Normalize grade subcategories to base grade number (e.g., "8. osztály - általános..." → 8)
- ✅ ALWAYS: Extract rank number from helyezes strings (e.g., "1. döntős" → 1)

## Testing
- ✅ ALWAYS: Separate unit tests (fast, committed fixtures) from integration tests (slow, live data)
- ✅ ALWAYS: Use pytest fixtures for expensive setup operations (like downloads)
- ❌ NEVER: Use `pytest.skip()` for missing required fixtures - let tests fail
- ✅ ALWAYS: Test with real downloaded data, not just synthetic examples
- ✅ ALWAYS: Test edge cases: Budapest districts, grade categories, both round types

## Dependencies
- ✅ ALWAYS: Run `playwright install` after adding Playwright dependency
- ✅ ALWAYS: Add `lxml` when using `pandas.read_html()`
- ✅ ALWAYS: Add `beautifulsoup4` when parsing HTML with structure preservation

## Known Data Patterns
- ⚠️ INFO: 16 combinations unavailable (Szóbeli rounds during COVID-19 years)
- ⚠️ INFO: Írásbeli files: 60-82 rows (preliminary results)
- ⚠️ INFO: Szóbeli files: 6-7 rows (final results for qualifiers only)
- ⚠️ INFO: `megye` column empty in MVP (HTML doesn't contain county data)
- ⚠️ INFO: Grade values include subcategories for grades 7-8

## Code Style
- ✅ ALWAYS: Use descriptive variable/method/class names (self-documenting code)
- ✅ ALWAYS: Keep methods small and focused (single responsibility)
- ❌ NEVER: Leave trailing whitespace at end of lines
- ❌ NEVER: Use tabs - use spaces for indentation
- ❌ NEVER: Use comments for historical changes - use git
