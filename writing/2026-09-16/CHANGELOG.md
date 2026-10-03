# Writing decisions and changes

## 2026-10-03 — Approved verbalization and statistical prose cleanup

- Removed the AAKV-internal-contribution future-study sentence without adding it to Limitations.
- Condensed dataset-specific verbalization gains into two blue sentences, retaining all reported values and removing the repeated all-dataset conclusion and ESC-50 summary.
- Replaced the confidence-interval qualification with one blue sentence specifying test-sample resampling under fixed models/inference settings.
- Removed the unsupported future quality-assessment purpose assigned to cached case texts; retained their existing table-caption description. No data, equations, citations, or table bodies changed.

## 2026-10-03 — Approved concise selection-analysis wording

- Deleted the premature Overall Results transition and the repeated FSD50K summary, retaining the quantitative FSD50K analysis.
- Replaced the selection-rule caveat with the approved combined-strategy conclusion; did not add the deferred voting-only/score-gap-only ablations to Limitations. Reserved them in a non-rendered source comment only.
- Replaced the possessive selector wording with an explicit description of relation sets for individual samples and limited the diversity-statistics conclusion to variation across audio samples. New/replacement sentences are blue. Preserved the Sample-level Relation Selector module name and all experimental values.

## 2026-10-03 — Approved reproduction and dataset-mean wording

- Replaced the “uniquely recover” inference-configuration statement with the author-approved distinction between the documented inference procedure and unavailable complete relation subset/classification implementation. Preserved the source citation and controlled-reimplementation status; marked the replacement blue.
- Defined the arithmetic mean separately for each metric across the five datasets in Sec. 4.1.4, explicitly excluding weighting by sample count. Marked the definition blue and removed its repeated definition from the ablation paragraph.
- Left the Overall Results transition unchanged pending approval of its relocation. No numerical values, equations, comparison roles, or figure assets changed.

## 2026-10-03 — Author-supplied Figure 1 version 4

- Replaced Figure 1 in main-4 with the supplied 图片4.png, preserving the original bitmap. This version places the class index below the evidence symbol and the selection marker above it.
- Rechecked iKnow-audio Sec. 3.3, Sec. 5, Appendix A.4, and the official repository. The paper describes the inference procedure, while the public repository lists AKG and KGE-training resources rather than a full classification evaluation pipeline. Proposed removing “uniquely recover” and specifying the missing reproduction details; prose changes await author approval.
- Proposed defining the unweighted arithmetic mean across datasets once in Sec. 4.1.4, with short table notes and no repeated definition in the ablation paragraph. No metric values or prose changed in this update.

## 2026-10-03 — Align relation-selection equation

- Replaced the left-aligned array in Eq. (11) with aligned equations, removing excess space before the first equals sign and aligning both equals signs. Marked this formatting revision blue; mathematical content is unchanged.
- Verified that the final score is associated with each class, with the original CLAP score retained under the stated fallback conditions. The framework notation should use a class-index subscript and selection superscript, `\mathcal U_i^*`; the author-supplied bitmap was not altered.

## 2026-10-03 — Author-corrected Figure 1 (图片3.png)

- Replaced the framework image in main-4 with 图片3.png, preserving the supplied bitmap and all prose, equations, results, and red revision marks.
- Kept the prior image for recovery. Recompiled and checked the Figure 1 page.

## 2026-10-03 — Red-marked main-4 wording and author-supplied framework figure

- Replaced Figure 1 with the author-supplied 图片2.png without altering the bitmap. Its embedded predictor label and “Others votes” remain for author review.
- Replaced standalone predictor terminology in active Method and Experiments prose with class scoring and predictions computed separately for each relation; no independently trained models are implied.
- Distinguished CLAP as the knowledge-free baseline and iKnow† as the knowledge-enhanced baseline; named iKnow† explicitly in the component comparison.
- Matched AAKV checking language to the lexical/format checks imported by the final 31_corrected_aakv_cache/generate.py. Preserved Appendix A verbatim and Related Work prose unchanged; only the method figure caption was synchronized.
- Preserved display equations and experimental table bodies. Compiled the 16-page PDF successfully and visually inspected the figure and revised method page. Previous files and exact language changes are saved under tmp/before_red_20261003/.

## 2026-10-02 — Translate integrated experiments, limitations, and conclusion

- Synchronized main-4 sections 4.2–4.5 and Conclusion with the approved main-5 text; removed the independent Discussion input and updated the roadmap.
- Preserved all nine main-text table/figure environments and all reported numbers. Kept speculation qualified and terminology locked.
- Compiled the 14-page PDF and inspected the affected pages. Translation/source notes: `translation_prep/integrated_discussion_translation_main4.md`.
- Final experiment packaging is audited separately; legacy efficiency measurements are not relabeled as corrected-cache measurements.

## 2026-10-02 — Approved funnel introduction in main-4 and main-5

- Added an independent Chinese introduction for main-5 and translated the approved text into the main-4 introduction.
- Read the CLAP, ReCLAP, PAT, and iKnow-audio PDFs to verify method descriptions and terminology; recorded anchors in translation_prep/introduction_revision_main4_main5.md.
- Kept three distinct methodological contributions, preserved the reported gains, and removed repeated implementation detail from the framework overview.

## 2026-10-02 — Abstract revision in main-5 and main-4

- Created `main-5.tex` from the current Chinese `main-3.tex` and replaced only its abstract with the author-approved version.
- Updated the corresponding English abstract in `main-4.tex`, preserving the reported metrics and locked method terms.
- Compiled both PDFs and checked the abstract pages for visible layout problems.

## 2026-10-02 — Complete main-4 English manuscript

- Added main-4-specific English Experiments, Discussion, Conclusion, and Appendix sources; kept the main-3 Chinese files unchanged.
- Shortened the abstract's method details, standardized terminology and American English, and checked all active chapters, captions, table labels, and appendix wording.
- Preserved raw AAKV prompts/cached case evidence, equations, citation keys, and all numeric table entries. Twelve tables passed ordered numeric-token comparison against their source tables.
- Fixed an overflowing English case table, a duplicated Appendix prefix, and duplicate appendix table hyperlink anchors. Compiled and visually reviewed the 14-page English PDF; final same-page float placement remains a separate layout pass.
- Recorded section-specific style choices, expression examples, audit results, and remaining source/metadata limitations in `translation_prep/full_translation_review_main4.md`.

## 2026-10-02 — Source-checked English Related Work for main-4

- Translated the approved three-part Related Work into `sections/02_related_work_main4.tex` using the locked terminology and preserving all citation keys and the Figure 1 block.
- Checked each cited method against its article PDF; the SINet statement was limited to the publisher abstract because its full PDF was unavailable. The source-to-claim record is `translation_prep/related_work_evidence_main4.md`.
- Distinguished PAT's task-level weighted prompt ensemble, ReCLAP's training-caption and inference-prompt stages, AudioCards' sound-design setting, and iKnow-audio's curated relation retrieval and joint log-sum-exp aggregation.
- Recompiled `main-4.pdf` with BibTeX and inspected the Related Work and Figure 1 pages. No compilation errors, unresolved citations, or overfull boxes were reported.

## 2026-10-02 — Main-4 Method figure and algorithm alignment

- Replaced Figure 1 in the English `main-4` draft with the author-provided `图片2.png`, using a separate asset and caption so `main-3` remains untouched.
- Aligned the Method overview with the figure's offline/online flow, reformatted Eq. (11) as a two-row left-aligned array, and clarified the algorithm's outputs and offline boundary.
- Recompiled `main-4.pdf` twice and checked the figure and algorithm pages visually; no overfull boxes or unresolved references were found.

## 2026-09-30 — Author-approved wording and black-text main-3

- Isolated the introduction as `sections/01_introduction_main3.tex` so the approved wording affects `main-3` only; added the existing iKnow-audio citation at the first sentence of the revised gap paragraph.
- Removed Table 1's repeated dagger footnote because its caption already defines the symbol. Replaced the ESC-50 verbalization discussion with the approved, comparator-specific interpretation; performance numbers were unchanged.
- Rendered all prior purple review text in black by making `\purplerevision` a pass-through macro. Recompiled `main-3.pdf` twice; citations resolved and the output is 13 pages.
- Visual check: Appendix B.2 still reaches into the page-12 number. The author deferred formatting changes, so no pagination or table layout was adjusted in this pass.

## 2026-09-30 — Purple-marked, evidence-checked manuscript revisions

- Updated only the `main-3` review version: its experiment and appendix sources, plus an isolated copy of the Related Work source for the Figure 1 caption. Existing shared sources and `main-2` were not changed in this pass.
- Added bounded interpretations for the ESC-50 verbalization result, paired Bootstrap intervals, and McNemar transitions. Revised captions for Figures 1–4, Tables 1–5, and the appendix tables where the review identified a verifiable ambiguity. Added the efficiency cache-size definition from the final experiment notes; Table 6 caption and all result values remain unchanged.
- Corrected Appendix B.2 to identify RotatE and class–tail concatenation as present in the original iKnow-audio method, identified the controlled aggregation change, and removed the unsupported `Evidence Top-P` comparison row. All new/replaced text is purple.
- Recompiled `main-3.pdf` successfully. Per the author's instruction, no layout adjustment was made; Appendix B.2 still overlaps the page-13 number and needs a later formatting pass.

## 2026-09-30 — KBS two-column layout pass

Layout-only pass on `main-3.tex`; manuscript wording, results, and table contents were left unchanged.

- Kept the official Elsevier `elsarticle` `final,5p,times,twocolumn` class and checked its sample placement convention (`table[t]`, `figure[t]`). Main-text tables remain top floats; the statistical comparison figure now uses top placement so Figures 2–4 appear in numerical order.
- Protected the `Overall ablation` heading from being stranded at the foot of p6. Verified the main result tables appear on p6–p8 with their discussion pages; Table 6 remains at the top of p10, directly after its efficiency-analysis discussion begins on p9.
- Set the bibliography to the template's compact `\small` size with zero extra inter-entry skip; all 23 references now fit on p11, removing a mostly empty reference-only page without changing the entries.
- Kept the appendices after the reference list and preserved the existing compact appendix layout for the wide protocol tables. Appendix table sequence remains B.1–B.2, C.1–C.2, D.1, and E.1.
- Recompiled and visually inspected the final PDF (14 pages); no prose or result values were edited in this pass.

## 2026-09-30 — Wide tables: same page as the paragraph that cites them

Author feedback on the previous attempt: the sentence “表 1 报告了…” was still on a
different page from Table 1, and the dag footnote I had added to Tables 2–4 was not
requested. Both are fixed here. **Layout only; wording, numbers and captions unchanged**
(prose diff against the pre-edit file: 0 differing CJK units).

- **Removed the dag-footnote lines I had added to Tables 2–4.** Table 1 keeps the
  original inline footnote it always had; nothing else changed.
- Root cause of the page split: a double-column wide table cannot be typeset where a
  deeper two-column stack already occupies the page, so declaring it after the citing
  paragraph always defers it to the *next* page — the citing sentence stayed behind.
- Fix: put each of the four wide tables at the **top of the very page that carries its
  citing subsection** (`\clearpage` + `\twocolumn[ ... ]`, table source placed before
  that subsection's paragraphs). Because the argument of `\twocolumn` forms the page's
  top block, the table and the text that discusses it now share one page:
  Table 1 on p7 with §4.2, Table 2 on p8 with §4.3.1, Table 3 on p10 with §4.3.2.
- Reverted the four tables from `table*[tbp]` back to the original
  `\twocolumn[...]` + `\fixedtablecaption` form: converting them to `table*` with
  `\caption` also made `\caption` unusable inside `\twocolumn` ("Argument of
  \@topnewpage has an extra }"), and an inline `minipage` version silently squeezed the
  table into a single column (279.99 pt overfull hbox).
- Table 6 restored to `[!t]` and Figure 4 to `[!t]`, which removed a text/float
  collision and the 69.67 pt overfull vbox that an inline `[H]` table caused.
- Trade-off: honouring "figure/table on the page that mentions it" needs the four
  table pages to start at their owning subsection, so the build is 19 pages instead of
  17 (four table pages carry a table plus the discussion that cites it).
- Verified with three pdfLaTeX passes plus BibTeX: no undefined citations/references,
  no overfull boxes, no blank pages. Rendered page checks in `_qa_pages/main3_final2/`.

## 2026-09-30 — Float placement: every table/figure now follows its first in-text citation

Layout-only edit of `main-3`; no manuscript wording, numbers or captions were changed
(font and prose diff between the previous and new section file is empty).

- Diagnosed `main-3.pdf` by rendering every page and auditing float positions against
  their in-text citations (`scripts/render_pages.py`, `scripts/check_float_order.py`).
  Before the edit, Table 1 sat above its own first mention on page 7 and Tables 2–5
  appeared on a page *before* the paragraph that cited them; Method Figure 1 was
  correctly on the same page as its first mention.
- Replaced the four manual wide-table blocks (`\clearpage` + `\twocolumn[...]` +
  `\fixedtablecaption`, which forced each wide table onto a fresh page regardless of
  where the text cited it) with real double-column floats `\begin{table*}[tbp]` using
  the standard `\caption`. `\fixedtablecaption` is kept defined but is no longer used
  by the experiments section.
- Moved each `table*` / `figure*` / `figure` source block so that it is declared
  *after* the paragraph that first cites it. Declaring a wide float after its citation
  is what makes LaTeX defer it to the top of the following page instead of floating it
  above the sentence that mentions it.
- Moved the four `\subsubsection` bodies so the wide table sits between the paragraph
  containing the first citation and the remaining discussion, keeping the citing text
  and its table on the same page or one page apart.
- Added a uniform `\textsuperscript{\dag}` footnote line to Tables 2–4 (Table 1 already
  had one inline); previously their dag footnote dropped to the page foot, away from
  the table.
- Added `\needspace{4\baselineskip}` before the ablation/relation/verbalization/cost
  subsubsections and loaded `needspace`, which removed a stranded subsubsection
  heading; the previous build had an underfull vbox on the figure page.
- Table 5 (`[H]` → `[!htbp]`) and Figure 4 (`[!t]` → `[!b]`) were re-anchored so that
  their first mention precedes them in reading order.
- Result: 17/17 floats verified to appear after their first in-text mention, 15 pages
  (was 17), no blank pages, and no remaining underfull/overfull vbox in the log.
- Verified with three pdfLaTeX passes plus BibTeX; logged float audit in
  `tmp/audit_before.txt` / `tmp/audit_after3.txt` and rendered checks in
  `_qa_pages/main3_before/` vs `_qa_pages/main3_v6/`.

## 2026-09-29 — Experimental cross-check corrections

- Updated Appendix C relation-selection behavior for FSD50K and AudioSet from the final corrected per-sample selector records; retained the verified results for the other three datasets.
- Corrected the TUT2017 Direct concatenation MRR to 65.93 in the knowledge-verbalization table, matching the unrounded source result and factorial table.
- Clarified how the computational-cost table derives macro-mean latency, relative overhead and throughput, and bounded interpretation of the case-study AAKV texts.
- Recompiled and visually checked the red-marked `main-1-公式.pdf`; left `main.pdf` unchanged as previously requested.

## 2026-09-16 — Workspace initialization

- Created a double-column `elsarticle` skeleton from the user-supplied template.
- Selected `final,5p,times,twocolumn` for the writing preview.
- Created one file per section; no unapproved paper content has been inserted.
- Set the experiment structure to the user-approved 5.1–5.4 outline.
- Bibliography remains empty until references are verified.

Future entries should record: date, approved section/claim, changed files, compile result and Git commit.

## 2026-09-18 — Related Work and bibliography

- Added the approved three-part Related Work section covering audio--language models, structured knowledge and relation selection, and knowledge verbalization and evidence fusion.
- Corrected and included the verified Wav2CLIP source after checking its title, abstract and introduction.
- Added BibTeX records for the cited audio--language, ontology, graph reasoning and knowledge verbalization papers.
- Wrapped the Chinese Related Work section in the existing CJK environment.
- Compiled `main.tex` with MiKTeX/pdfLaTeX and BibTeX; `main.pdf` generated successfully without undefined citations or fatal errors.

## 2026-09-19 — Approved Related Work revision

- Replaced `sections/02_related_work.tex` with the approved three-subsection version: zero-shot audio--language models, textual prompting and sound semantic description, and structured knowledge with evidence-aware candidate ranking.
- Added BibTeX records for CLIP-Adapter and Tip-Adapter used in the approved third subsection.
- Recompiled `main.tex` with MiKTeX/pdfLaTeX and BibTeX; `main.pdf` generated successfully. Remaining BibTeX notices concern empty page fields in pre-existing records only.

## 2026-09-19 — Evidence-bound Related Work wording

- Revised the three evidence-bound statements identified in the source audit: SLAP is described as supporting variable-length audio training; the prompting paragraph is limited to ReCLAP, TSPE, PAT and AudioCards; and ontology/graph work is described as providing semantic information for audio classification, with iKnow-audio specifically linked to CLAP candidate prediction.
- Recompiled `main.tex` with MiKTeX/pdfLaTeX and BibTeX without fatal errors or undefined citations.

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
# 2026-09-16：撰写 Overall ablation 小节

- 基于 27-pro 完整 TUT2017（6,300 条）结果加入三模块完整 $2^3$ 因子消融表。
- 区分单模块效应、双模块组合和完整 TFS，明确完整方法主要改善 Hit@1 与 MRR，而非 Top-5 覆盖率。
- 超参数网格不并入模块消融，保留至 Parameter sensitivity 小节；逐数据集完整消融表预留附录编号。
# 2026-09-16：完善整体消融正文表与附录表

- 正文消融表改为双层表头：第一层为数据集，第二层为 Hit@1 与 MRR，并保留五集宏平均。
- 取消 T/F/S 等单字母方法名，改用 AAKV、Hierarchical Fusion 和 Relation Selection 的完整模块名称。
- 按“单模块—双模块—完整方法”重写消融分析，明确 AAKV 单独不稳定、组合后改善更明显的事实边界。
- 新增附录表，完整报告相同消融分支的 Hit@3 与 Hit@5。
- 本轮仅更新本地 LaTeX 并完成编译核验，未执行 Git 同步。
# 2026-09-16：加入关系选择分析及可复现关系清单

- 5.3.2在固定 AAKV 与 Hierarchical Fusion 的条件下比较 Frequency Top-5、Random Top-5 和 Sample-level Relation Selector。
- 三种策略均保留五种关系，正文报告五个测试集的 Hit@1、MRR 与宏平均结果。
- 删除易与主表 iKnow 复现结果混淆的 Static-Rq 对照。
- 附录新增五个数据集的 Frequency Top-5 具体关系清单，并注明其不使用标签或测试集真值。
- 本轮仅更新本地 LaTeX 并完成编译与页面检查，未执行 Git 同步。
# 2026-09-16：按KBS实验叙述风格重写4.3已完成内容

- 为 Ablation and component analysis 增加章节级证据路线说明。
- Overall ablation 改为“实验目的—单模块—双模块—完整方法—结论边界”的组织顺序。
- Relation selection analysis 改为“公平设置—策略定义—总体结果—关键行间比较—收束结论”的组织顺序。
- 保留既有正文表格与附录表，不改变任何实验数值。
- 本轮仅更新本地 LaTeX 并完成编译检查，未执行 Git 同步。
# 2026-09-20：加入计算开销分析

- 在 Further analysis 中新增 4.4.3 Computational cost analysis；原逐样本案例小节顺延。
- 正文只报告 batch size = 1 的 CLAP、iKnow\textsuperscript{\dag} 与 SAKI 在线延迟、相对开销、吞吐量、平均峰值显存和平均离线缓存。
- 数值来自 29 号实验的串行复测定稿，五个测试集各固定抽取 200 条样本，预热 20 条并重复测量 5 次；TUT2017 的抽样框为最终 6,300 条记录。
- 不在正文引用 batch size = 32 的结果，也不使用性能—效率图；不对尚未单独计时的模块作成本归因。
- 编译检查发现横向双栏表浮动至后一页，遂在不改数值的前提下转置为单栏指标表，使表格紧接其首次引用。

# 2026-09-29：核对 FrozenRq、AAKV 协议与红字审阅稿

- 澄清关系策略表中的 FrozenRq 仅沿用 iKnow† 的固定关系集合，文本与融合采用 AAKV＋分层融合，故不等于主表 iKnow†。
- 按生成代码补入 Appendix D 的完整 AAKV 系统指令、修复指令、规则检查和回退模板；正文仅概述约束并引用附录。
- 将消融表中的“宏平均”明确为“五数据集等权平均”，理顺双模块和完整方法的不同参照关系，并正面说明 Hit@1/MRR 与 Hit@5 的差异。
- 所有本轮正文与附录新增措辞在 `main-1-公式.tex` 审阅稿中显示为红色；仅编译 `main-1-公式.pdf`，未覆盖 `main.pdf`。
- 审核发现旧消融的非 Selector AAKV 分支与关系策略对照在 FSD50K、AudioSet 使用了不同版本的文本缓存；当前未改动数值，提交前需统一缓存后复核完整因子消融。
- 将上一轮保存在服务器的新版方法流程图取回本机，并替换进 `main-1-公式.pdf` 第 3 页；主稿 `main.pdf` 未覆盖。

# 2026-09-29：统一 AAKV 缓存后复算并更新实验结果

- 使用统一的最终 AAKV 文本缓存重新计算 FSD50K（10,231 条）和 AudioSet（17,233 条）的完整因子消融与关系选择对照，并核验 DCASE17-T4 开发集仍选择 $\alpha=0.3$、$N_r=5$。
- 同步更新主结果表、完整因子消融表、关系选择表、知识语言化表、附录 Hit@3/Hit@5 表及逐样本统计图；FSD50K 与 AudioSet 的最终 Hit@1/MRR 分别为 64.46/74.13 和 31.29/42.56。
- 修正结果边界：完整方法取得最高的五数据集等权平均 Hit@1/MRR（66.81/75.08），但 FSD50K 上 AAKV＋Relation Selection 的 Hit@1（64.49）略高于完整方法（64.46）。
- 更新 Bootstrap 置信区间、McNemar 检验和预测转移计数；FSD50K 与 AudioSet 的净正向转移分别修正为 473 和 358。
- 重新生成 `main.pdf` 与红字审阅稿 `main-1-公式.pdf`，完成关键结果页面的视觉核验。
- 进一步核对 FSD50K 的双模块与完整配置：64.49\% 与 64.46\% 仅相差3个样本；配对McNemar检验$p=0.923$，Bootstrap 95\%区间为$[-0.44,0.37]$个百分点。据此将正文解释修正为Hit@1基本持平、完整配置MRR略高，而非双模块具有稳定优势。
- 完善引言末尾的文章结构说明，明确第2--6节分别承担相关工作、方法、实验、讨论和结论的功能。
- 按“任务背景--文本与知识增强进展--三个连续问题--SAKI对应方案”的逻辑重写引言主体，并压缩三项贡献表述。
- 重排Table 6为栏宽自适应的四列格式，将案例名称统一为单行的“错误纠正、排名改善、预测退化”；删除关系选择正文中关于FrozenRq与主表iKnow†差异的冗长说明。
# 2026-09-30 — Evidence-verified Related Work and PAT citation

- Replaced the Related Work section with the author-approved, evidence-verified three-part review covering audio--language models, sound semantic description and prompting, and structured knowledge for audio classification.
- Corrected the description of PAT to reflect task-level prompt weighting and frame-level cross-modal alignment, and clarified the task boundary of AudioCards.
- Distinguished ontology/graph-based audio modeling from inference-time external knowledge retrieval and positioned SAKI's sample-level relation selection relative to iKnow-audio and SINet.
- Replaced the incorrect PAT arXiv entry with the NAACL 2025 proceedings record (pp. 12376--12394; DOI: 10.18653/v1/2025.naacl-long.616).
- Marked the revised Related Work prose in blue and rebuilt `main-2.pdf` successfully.

# 2026-09-30 — Black-text layout edition (`main-3`)

- Created an independent `main-3.tex` edition from `main-2`, with all revision markup rendered in black and manuscript wording unchanged.
- Created layout-only copies of the experiments and appendix sources so the approved `main-2` source and PDF remain reproducible.
- Repositioned Tables 1 and 2 at the top of page 6, kept Tables 3 and 4 with their component-analysis discussion, and retained Figures 2--4 on the corresponding further-analysis pages.
- Reflowed the appendices into a continuous one-column layout: Appendix A tables, reproduction tables, selector statistics, AAKV protocol, and paired-test table now follow their textual order without the former sparse float-only appendix page.
- Added fixed double-column float-page spacing and verified the final 15-page PDF visually; compilation reports no overfull boxes, oversized floats, or undefined references/citations.

# 2026-10-02 — English translation starts (`main-4`)

- Created `main-4.tex` and `sections/01_introduction_main4.tex` without changing the Chinese `main-3` edition.
- Translated the approved abstract and Introduction into academic English, preserving citation keys, evaluation figures, and the controlled-reimplementation boundary.
- Applied the locked terminology for SAKI, AAKV, relation-specific predictors, top-1 voting, top-two score gap, and Hierarchical Fusion; explicitly stated that AAKV generation is not conditioned on the test audio.
- Kept the remaining sections linked to the main-3 sources for sequential translation. Built `main-4.pdf` with pdfLaTeX and BibTeX; no undefined citations or references were reported.

# 2026-10-02 — Method translated for main-4

- Added an English Method source at `sections/03_method_main4.tex` and linked it from `main-4.tex`; the approved Chinese `sections/03_method.tex` remains untouched.
- Preserved the existing equations, parameters, citation keys, cross-references, and online algorithm while applying the locked English terminology.
- Made the offline/online boundary, AAKV validation, relation voting and tie-breaking, and two-step evidence aggregation/score fusion explicit without adding new experimental claims.
- Rebuilt the 13-page `main-4.pdf` and checked the Method pages visually; no compilation errors, overfull boxes, or undefined references were reported.
# 2026-10-02 — main-5 Chinese results: blue-marked interpretation revision

- Added independent `sections/04_experiments_main5.tex`; rewrote 4.2–4.4 around findings, representative comparisons, and bounded interpretations using the supplied KBS examples. New prose is blue.
- Preserved Experimental setup and all nine experiment figure/table environments byte-for-byte (after newline normalization). Corrected the case-study wording and distinction between random and static relation selection.
- Removed the repeated parameter-grid equation from Results, referring to Implementation details instead; parameter values remain unchanged.
- Recompiled main-5.pdf (13 pages) and visually checked pp.6–9. No overfull boxes or undefined citations/references; existing font/bookmark/template warnings remain.
- Logged the unresolved efficiency-cache-version provenance in `drafts_zh/04_results_main5_blue_20261002.md`; no timing or storage numbers were remeasured or altered.
- Kept main-3/main-4 and shared experiment sources unchanged. Remote sync deferred because the existing sync script includes unrelated working-tree edits.
# 2026-10-02 — main-5 red evidence additions

- Added six red-marked evidence interpretations to combination ablation, relation selection, knowledge verbalization, prediction transitions/cases, and cost analysis; preserved the remaining blue revision.
- Checked new numbers against the current tables and extracted figure labels. All nine experiment figure/table environments are unchanged. No new experiments or statistical tests were performed.
- Replaced the repeated case-study call for a separate evidence ablation with a direct explanation of Hit@1 versus reciprocal rank.
- Rebuilt the 13-page main-5.pdf and inspected red/blue rendering. No overfull boxes or undefined references/citations. Existing efficiency-cache provenance caveat remains in the revision notes.
- Local-only revision; automatic remote sync deferred because its script uploads unrelated dirty working-tree files.

# 2026-10-03 — Cost analysis wording synchronized in main-4 and main-5

- Replaced the repeated cost discussion with one green sentence in each language, limited to the online operations and the measured latency; left Table 6 and all experimental values unchanged.
- Removed manuscript wording about unmeasured module-level timing and a future cache-version remeasurement. The measurement-version check remains an internal submission task, not a claim of new results.
- Rebuilt main-4.pdf (14 pages) and main-5.pdf (13 pages) and inspected the revised pages. Remote sync deferred because the existing script would also upload unrelated working-tree changes.

# 2026-10-03 — Complete authorized main-4 language audit items

- Recovered the original 41 numbered suggestions and recorded individual dispositions. Twelve had already been addressed; this revision addresses 21 further numbered suggestions in red. Six Related Work suggestions and two Appendix A explanatory sentences remain pending author confirmation.
- Clarified abstract, introduction, methods, comparison references, prediction transitions, timing wording, and conclusion without changing reported results or scoring rules. Updated the terminology policy to avoid naming independently trained predictors.
- Preserved Related Work and Appendix A verbatim. Protected reported decimal values, all table numbers, displayed equations, citation keys, labels, and experimental table bodies with automated checks.
- Rebuilt the 16-page main-4.pdf twice and inspected revised pages. No compilation errors, overfull boxes, or unresolved citations/references. The author-supplied framework image and existing analysis figures were not edited.
- The earlier suggestion to add Appendix prefixes was rejected: current cross-references already supply them. Existing unrelated working-tree edits are preserved.

# 2026-10-03 — Reduce whitespace on main-4 pages 8 and 10

- Retained the Elsevier 5p two-column class, margins, manuscript text, data, and revision colors. Enabled ragged-bottom columns and reduced in-text float separation to avoid stretched internal gaps.
- Replaced the forced page-start wrapper for Table 4/Figure 2 with a top double-column float, allowing the verbalization introduction to continue on page 8 while Table 4 and its first citation remain on page 9.
- Removed oversized space reservations in the prediction-transition/case blocks and reduced the reservation before parameter sensitivity. Adjusted display widths without editing figure assets or data.
- Relocated existing figure-introduction text, without rewriting it, so Figures 3 and 4 and Table 5 have their numbered prose references on page 10; Table 6 and its discussion remain on page 11.
- Recompiled and inspected pp.8–11. Page 10 now holds the transition plot, case table, and parameter plot with their discussion, rather than leaving a large empty right-column tail. The document remains 16 pages.

# 2026-10-03 — Source-checked blue Related Work and opening revisions

- Unified the abstract/introduction wording around dependence on labeled audio; clarified the cross-modal pretraining transition and replaced the unsupported additive connector in the class-description bridge.
- Checked TSPE Sections III.B/C, PAT Sections 4.2/4.3 and Algorithm 1, and AudioCards Abstract/Sections 2–4 against local original PDFs. Preserved TSPE's manual filtering and averaging, PAT's task-level prompt weighting and parameter-free attention, and AudioCards' model-training context.
- Split AudioCards into an adjacent-domain paragraph instead of placing it under zero-shot prompting. Added no new references, experimental values, or method claims. Only these approved changes are blue; previous red revisions remain.
- Evidence anchors and short excerpts are recorded in `translation_prep/relatedwork_blue_evidence_20261003.md`.

# 2026-10-03 — Equation 7 and analysis-figure legibility

- Reformatted Eq. (7) as a two-line aligned expression in both language versions; stated its eligibility and original-score fallback immediately in prose without changing the scoring rule. The affected text and equation are green.
- Increased final-size labels in the paired-difference and prediction-transition figures; retained the parameter-sensitivity figure's already legible type size. Re-exported the three vector and raster formats from the existing Python source without changing plotted values.
- Rebuilt and visually inspected main-4.pdf (14 pages) and main-5.pdf (13 pages). No overfull boxes, LaTeX errors, or unresolved citations/references were found.
- Reviewed Section 4.1 without changing its scientific content. Dataset source citations, redundant test-label statements, and the exact seven-second crop rule remain editorial checks. The existing remote sync script would include unrelated dirty files, so this revision has not been pushed remotely.
