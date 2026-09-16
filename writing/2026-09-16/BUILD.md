# Build instructions and verification

The build has not yet been verified until a LaTeX distribution is installed and `pdflatex` succeeds.

From this directory, use either:

```powershell
latexmk -pdf -interaction=nonstopmode -halt-on-error -outdir=build main.tex
```

or, if `latexmk` is unavailable:

```powershell
pdflatex -interaction=nonstopmode -halt-on-error -output-directory=build main.tex
pdflatex -interaction=nonstopmode -halt-on-error -output-directory=build main.tex
```

When references are enabled, run BibTeX/latexmk and check undefined citations. After each substantive change, inspect `build/main.pdf` in two-column view and read the log for overfull boxes, missing references and float-placement warnings.
