# Prompt for Updating README-ai-rules.md

Use this prompt when you want to update the README-ai-rules.md file after completing new implementation phases.

---

## Prompt:

```
Please update README-ai-rules.md based on the recent coding summaries.

Review all step4-coding-summary-*.md files that were created since the last rules update.
Extract ONLY the specific, repeatable technical decisions that an AI coding assistant would need to know to work consistently on this project.

IMPORTANT - What to INCLUDE:
- Specific technical algorithms or patterns (e.g., "drop top N rows from Írásbeli where N = Szóbeli count")
- Concrete technical limitations (e.g., "openpyxl cannot create pivot tables programmatically")
- Specific data patterns unique to this project (e.g., "COVID years 2020-21, 2021-22 have no Szóbeli")
- Actionable technical decisions that would be repeated (e.g., "use summary tables instead of pivot tables")
- Project-specific edge cases (e.g., "Budapest districts include Roman numerals")

IMPORTANT - What to EXCLUDE:
- General best practices (e.g., "write clean code", "test your code")
- One-time decisions already made (e.g., "use MIT license", "use Poetry")
- Organizational patterns (e.g., "use folders for organization")
- Generic advice (e.g., "understand business logic first")
- Historical context or explanations of why decisions were made

FORMAT:
- Use the same emoji style as existing rules: ✅ ALWAYS, ❌ NEVER, ⚠️ CAUTION/INFO
- Keep rules concise and actionable (one line per rule)
- Group related rules under clear section headers
- Match the existing tone and detail level in the file

PROCESS:
1. Read the existing README-ai-rules.md to understand the current style and detail level
2. Read the recent step4-coding-summary-*.md files
3. Extract only the specific technical decisions that match the criteria above
4. Add new sections or rules to README-ai-rules.md
5. Show me the diff so I can review before committing
```

---

## Example of Good vs Bad Rules:

### ✅ GOOD (Specific, Repeatable, Technical):
```
- ✅ ALWAYS: When both Írásbeli and Szóbeli exist: drop top N rows from Írásbeli (where N = Szóbeli row count)
- ❌ NEVER: Use `pandas.read_html()` when `<br>` tags matter - it strips them
- ⚠️ CAUTION: `wait_for_load_state('networkidle')` completes BEFORE DOM updates
```

### ❌ BAD (Too General, One-Time, or Obvious):
```
- ✅ ALWAYS: Use MIT License for code (one-time decision, not repeatable)
- ✅ ALWAYS: Write clean, maintainable code (too general)
- ✅ ALWAYS: Understand business logic before coding (generic advice)
- ✅ ALWAYS: Use template folders for multi-file outputs (organizational pattern)
```

---

## Notes:

- The rules file is for an AI coding assistant to produce consistent results on THIS project
- Focus on technical decisions that would need to be repeated in future work
- The file should be concise - quality over quantity
- When in doubt, ask: "Would an AI need to know this specific detail to write correct code for this project?"
