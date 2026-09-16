# Writing decisions and changes

## 2026-09-16 — Workspace initialization

- Created a double-column `elsarticle` skeleton from the user-supplied template.
- Selected `final,5p,times,twocolumn` for the writing preview.
- Created one file per section; no unapproved paper content has been inserted.
- Set the experiment structure to the user-approved 5.1–5.4 outline.
- Bibliography remains empty until references are verified.

Future entries should record: date, approved section/claim, changed files, compile result and Git commit.

## 2026-09-16 — Setup verification

- Copied the author-supplied `elsarticle` source into `source-template/` without changing it.
- Installed user-scoped MiKTeX 25.12 from the official installer after SHA-256 verification.
- Compiled `main.tex` twice and visually checked the rendered double-column skeleton.
- Created a separate local Git history and synchronized the manuscript sources to `1chestnut/review-v1` under `writing/2026-09-16/`.
- No substantive manuscript text or experimental numbers have been inserted yet.

## 2026-09-16 — Writing path and Chinese experiment preparation

- Moved the complete local workspace and `.git` history to `C:/Users/zkx/Desktop/论文修改/写作/latex`.
- Confirmed the author's Nature skill bundle includes the same `nature-writing/SKILL.md` already installed globally for Codex; added project guidance for VS Code/Codex editing.
- Prepared a Chinese working draft, terminology ledger and claim-evidence map without altering the approved LaTeX section.
- Flagged TUT2017's `development/meta.txt` source and the conflicting DCASE parameter-selection descriptions for author review before final prose.
- Installed and verified the official VS Code Codex extension; confirmed the moved LaTeX source still compiles.

## 2026-09-16 — Side-by-side editor setup

- Installed LaTeX Workshop for VS Code and configured the manuscript PDF viewer to open in the right editor group.
- Configured a two-pass MiKTeX `pdflatex` build on save; tested that it produces both PDF and SyncTeX files.
- Marked the experiments section with `main.tex` as its LaTeX root and made Nature-writing usage explicit in the project instructions.
