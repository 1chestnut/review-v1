# Writing decisions and changes

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
