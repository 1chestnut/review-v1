# Writing decisions and changes

## 2026-09-16 — Workspace initialization

- Created a double-column `elsarticle` skeleton from the user-supplied template.
- Selected `final,5p,times,twocolumn` for the writing preview.
- Created one file per section; no unapproved paper content has been inserted.
- Set the experiment structure to the user-approved 5.1–5.4 outline.
- Bibliography remains empty until references are verified.

Future entries should record: date, approved section/claim, changed files, compile result and Git commit.

## 2026-09-16 — Approved Chinese experimental setup

- Added the author-approved Chinese draft of the complete experimental setup: datasets, comparison methods, implementation details and evaluation metrics.
- Standardized the manuscript labels to `iKnow\textsuperscript{\dag}` and Audio-Aligned Knowledge Verbalization (AAKV).
- Documented that the 47-relation candidate pool comes from the AKG introduced by iKnow-audio, while the proposed method performs sample-level relation selection.
- Recorded the shared retrieval settings, DCASE development protocol, audio preprocessing, software environment and paired statistical analysis.
- Updated TUT2017 to the 6,300-clip development-plus-evaluation protocol; numerical result tables remain pending the Task 28 rerun.
- Compiled `main.tex` twice with MiKTeX/pdfLaTeX and visually inspected the resulting two-page, two-column PDF; compilation completed without errors or undefined references.
- Simplified the approved evaluation-metrics subsection by removing redundant formulas for the standard Hit@k and MRR metrics while retaining the multi-label evaluation rule and paired statistical protocol.
- Added the approved Chinese Overall Results subsection and the complete five-dataset main table using only the `27-pro` results, including the 6,300-clip TUT2017 evaluation.
- Transposed the main-results table to match the iKnow presentation: metrics in rows and dataset-grouped CLAP/iKnow/proposed-method columns.

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

## 2026-09-16 — PDF shortcut collision

- User reported that `Ctrl+Alt+V` invoked speech-to-text and failed because no microphone was available.
- Enabled LaTeX Workshop's alternate `Ctrl+L`, `Alt+V` keymap and documented the Command Palette route; compilation settings and manuscript content are unchanged.

## 2026-09-16 — PDF beside source, manual build

- Changed LaTeX Workshop output to the manuscript folder and disabled build-on-save at the author's request.
- Verified two successful manual `pdflatex` passes; the current output is `main.pdf` beside `main.tex`.
- Hidden auxiliary compilation files in VS Code's Explorer while keeping `main.pdf` visible.

## 2026-09-16 — Mouse-only compilation

- Enabled LaTeX Workshop's editor context menu, so right-clicking inside `main.tex` exposes its build command.
- Confirmed the extension also contributes a build button to the LaTeX editor title bar; no shortcut is required.

## 2026-09-16 — Right-click build diagnosis

- Reproduced the editor's exact `pdflatex` command and found an accidental full-width semicolon before the first comment in `main.tex`; removed only that character, preserving other user edits.
- Ran MiKTeX's update check without installing updates. The installation warning no longer appears.
- Confirmed the same command now exits successfully and regenerates `main.pdf`.

## 2026-09-16 — Source/PDF mismatch diagnosis

- Found `main.tex` newer than `main.pdf`: its conclusion input had been changed to the nonexistent `sections/06_conclusion1111111111.tex`, causing builds to stop and leave the older PDF in place.
- Restored only the conclusion input path to `sections/06_conclusion`; preserved the author's unrelated source change.
- Recompiled twice with the editor's exact command. `main.pdf` is now newer than `main.tex`, and `main.log` records successful output without a LaTeX error.
# 2026-09-16：调整总体结果至消融与统计分析的衔接顺序

- Overall Results 末尾先引出整体消融、关系选择和知识语言化分析。
- 将五个测试集上的成对 Bootstrap 95\% 置信区间结论移至 Statistical significance 小节，保持“先消融、后统计”的章节顺序。
