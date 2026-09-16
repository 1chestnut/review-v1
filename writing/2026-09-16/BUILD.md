# Build instructions and verification

Verified on 2026-09-16: MiKTeX 25.12 was installed for the current Windows user; `pdflatex` completed twice with exit code 0 and produced `build/main.pdf` (1 page). The rendered page was visually inspected. The frontmatter spans the page; section headings occupy the left column, and the right column is empty because approved prose has not been added. The `final,5p,times,twocolumn` class option is active.

The current `Author Name`, institution, title and empty abstract are placeholders, not submission-ready content. MiKTeX prints an update-check notice; this is not a LaTeX compilation error.

From this directory, use either:

The current PowerShell session has not refreshed its PATH after MiKTeX installation. If `pdflatex` is not recognized, invoke `C:\Users\zkx\AppData\Local\Programs\MiKTeX\miktex\bin\x64\pdflatex.exe` directly or open a new terminal. The verified command also used `--enable-installer` for missing packages.

```powershell
latexmk -pdf -interaction=nonstopmode -halt-on-error -outdir=build main.tex
```

or, if `latexmk` is unavailable:

```powershell
pdflatex -interaction=nonstopmode -halt-on-error -output-directory=build main.tex
pdflatex -interaction=nonstopmode -halt-on-error -output-directory=build main.tex
```

When references are enabled, run BibTeX/latexmk and check undefined citations. After each substantive change, inspect `build/main.pdf` in two-column view and read the log for overfull boxes, missing references and float-placement warnings.
