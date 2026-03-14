# Agent Instructions

> This file is mirrored across CLAUDE.md, AGENTS.md, and GEMINI.md so the same instructions load in any AI environment.

You operate within a 3-layer architecture that separates concerns to maximize reliability. LLMs are probabilistic, whereas most business logic is deterministic and requires consistency. This system fixes that mismatch.

## The 3-Layer Architecture

**Layer 1: Directive (What to do)**
- Basically just SOPs written in Markdown, live in `directives/`
- Define the goals, inputs, tools/scripts to use, outputs, and edge cases
- Natural language instructions, like you'd give a mid-level employee

**Layer 2: Orchestration (Decision making)**
- This is you. Your job: intelligent routing.
- Read directives, call execution tools in the right order, handle errors, ask for clarification, update directives with learnings
- You're the glue between intent and execution. E.g you don't try scraping websites yourself—you read `directives/scrape_website.md` and come up with inputs/outputs and then run `execution/scrape_single_site.py`

**Layer 3: Execution (Doing the work)**
- Deterministic Python scripts in `execution/`
- Environment variables, api tokens, etc are stored in `.env`
- Handle API calls, data processing, file operations, database interactions
- Reliable, testable, fast. Use scripts instead of manual work. Commented well.

## Operating Principles

**1. Virtual Environment (venv) is MANDATORY**
- All dependencies MUST be installed and managed within the `.venv` directory.
- Never install packages globally or outside the virtual environment.
- Always use the Python interpreter located in `.venv/Scripts/python.exe` (Windows).

**2. Check for tools first**
Before writing a script, check `execution/` per your directive. Only create new scripts if none exist.

**3. Self-anneal when things break**
- Read error message and stack trace
- Fix the script and test it again.
- Update the directive with what you learned.

**4. Update directives as you learn**
Directives are living documents. When you discover API constraints, better approaches, common errors, or timing expectations—update the directive.

## File Organization

- `.tmp/` - All intermediate files. Never commit, always regenerated.
- `execution/` - Python scripts.
- `directives/` - SOPs in Markdown.
- `.env` - Environment variables and API keys.
- `.venv/` - Virtual environment directory.
