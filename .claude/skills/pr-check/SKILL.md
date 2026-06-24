---
name: pr-check
description: Run the full pre-merge gate for the gin-calculator repo (Django check, unit tests, Playwright UI tests) and report a pass/fail summary. Use before opening or merging a PR.
disable-model-invocation: true
---

# pr-check

Runs every gate AGENTS.md requires before a PR can merge, in the order below,
and reports which passed/failed. Stop and surface the first failure with its
output — do not "fix" anything as part of this check.

## Environment

All commands run from the repo root. Activate the project's pyenv env first
(per AGENTS.md — do NOT create a new `venv/`):

```bash
pyenv activate gin
```

If `pyenv activate gin` is unavailable (e.g. CI or a fresh clone), fall back to
the system Python that has Django + Playwright installed and note that in the
summary.

## Steps

Run each step. Capture output. A non-zero exit = FAIL for that step.

1. **Django system check**
   ```bash
   python manage.py check
   ```

2. **Unit tests** (`calculator/tests.py`)
   Scope to the `calculator` app — a bare `manage.py test` also tries to import
   the Playwright `tests/` package (step 3) and errors on it.
   ```bash
   python manage.py test calculator --verbosity 2
   ```

3. **Playwright UI tests** (`tests/test_ui.py`)
   These need Chromium installed (`python -m playwright install chromium` once)
   and rely on the committed `db.sqlite3` sample data. conftest.py starts its
   own dev server (on port 8000 — make sure nothing else is bound to it), so
   just run (`python -m` form works even when the `pytest` console script
   isn't on PATH in the gin env):
   ```bash
   python -m pytest tests/ --verbosity 2
   ```

4. **Lint** — AGENTS.md requires "no linting errors". No linter is configured in
   the repo yet, so report this step as **N/A (no linter configured)** rather
   than passing or failing it. If a linter (ruff/flake8) gets added later, run
   it here.

## Report

End with a summary block, e.g.:

```
PR check summary
  Django check  : PASS
  Unit tests    : PASS (12 tests)
  UI tests      : PASS (5 tests)
  Lint          : N/A (no linter configured)

Result: READY ✅   (or NOT READY ❌ — first failure: <step>)
```

State `READY` only if steps 1–3 all pass. Quote the failing command's output
verbatim for any FAIL.
