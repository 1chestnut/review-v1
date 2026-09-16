# KBS manuscript workspace (2026-09-16)

This is a double-column `elsarticle` writing workspace. The class option in `main.tex` is `final,5p,times,twocolumn`, which is listed in the user-provided Elsevier template. It is a writing/layout preview; the journal submission system may require a different submission layout.

## Files

- `main.tex`: document class, title/frontmatter, packages and section inputs.
- `sections/`: one file per approved manuscript section.
- `references.bib`: verified references only.
- `figures/`: approved figures (add later).
- `CHANGELOG.md`: decisions and edits agreed with the author.
- `BUILD.md`: local compilation status and commands.
- `source-template/`: copy of the supplied Elsevier template, class source and bibliography style.

## Collaboration rule

Draft text is not silently imported from earlier experiments. For each section, review the claim, comparison, numbers and wording with the author first. After approval, edit the matching `sections/*.tex`, compile, inspect the PDF, record the change in `CHANGELOG.md`, commit locally and synchronize to the existing `review-v1` GitHub repository under `writing/2026-09-16/`.

## Citation style

This workspace begins with Elsevier's numbered bibliography style (`elsarticle-num.bst`), matching the supplied numbered template. Verify the final KBS submission requirements before submission.
