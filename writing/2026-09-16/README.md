# KBS manuscript workspace (2026-09-16)

Current local path: `C:/Users/zkx/Desktop/论文修改/写作/latex`. The earlier `任务清单/写作9.16` location was moved here on 2026-09-16.

Chinese experimental prose is drafted first in `drafts_zh/`. It is not yet imported into the English `elsarticle` source; approval and protocol checks come first.

VS Code's official Codex extension is installed on this computer. Open this folder as a VS Code workspace, sign in to Codex if prompted, and invoke `$nature-writing` for the manuscript draft or `$nature-polishing` for approved wording. The skill package is already installed globally under `C:/Users/zkx/.codex/skills/`; the project's `AGENTS.md` preserves writing and evidence rules. The editor extension installation does not sign in on the author's behalf.

The PDF is generated beside `main.tex` as `main.pdf`, so it appears in VS Code's left-hand Explorer. Automatic compilation is off. After editing, run **LaTeX Workshop: Build LaTeX project** from the Command Palette (`Ctrl+Shift+P`), then click `main.pdf` in the Explorer to view the updated paper. You can drag its tab to the right to keep source and PDF side by side. Do not use `Ctrl+Alt+V` here: on this computer it is intercepted by a speech-to-text shortcut. `drafts_zh/*.md` is an unapproved Chinese working draft and is not yet part of the compiled manuscript.

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
