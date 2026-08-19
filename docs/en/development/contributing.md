# Contributing and Verification

## Change Principles

- Keep changes small and easy to review; do not refactor unrelated files along the way.
- Automation must continue to interact with the game only through the UI, OCR, system audio, and ordinary input.
- Do not commit user logs, screenshots, configuration, account information, secrets, or personal paths.
- For changes involving the combat planner, combat state, audio capture, or user-data compatibility, add the relevant tests and document the risks.

## Documentation Contributions

- Put user-facing instructions under "Getting started", "Features", or "Guides".
- Put API, architecture, and implementation notes under "Development".
- Add every new page to the `nav` section in the root `mkdocs.yml`; otherwise it will not appear in the website navigation.
- Use relative Markdown links. Before submitting, run a strict build to check for broken links and configuration errors.

```powershell
.\.venv\Scripts\python.exe -m mkdocs build --strict
```

## Code Verification

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -p "*.py"
```

State which checks you ran in the submission description, along with any checks that could not be run because of environment limitations.
