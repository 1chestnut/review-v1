# Manuscript collaboration rules

This workspace is the author's KBS manuscript. Use the globally installed `nature-writing` and `nature-polishing` skills for academic prose and layout work; their `SKILL.md` files are at `C:/Users/zkx/.codex/skills/`. The user-supplied skill bundle at `C:/Users/zkx/Desktop/新建文件夹/翻译/7.27全文翻译/自己论文/nature-skills-main/nature-skills-main/skills/` is the source copy; its `nature-writing/SKILL.md` matches the globally installed copy.

For every manuscript-drafting request in this project, invoke `nature-writing` and read its routed experimental-section guidance before writing. For requests to revise wording, use `nature-polishing`; for LaTeX layout problems, use its layout reference and inspect the rendered PDF. Do not treat either skill as authority to invent evidence. In the VS Code Codex sidebar, the author may also invoke `$nature-writing` explicitly.

- Treat the PDFs under `C:/Users/zkx/Desktop/论文修改/写作/模仿学习/` as structural/style references, not sources of the author's results. Do not copy passages.
- Use the frozen output files under `C:/Users/zkx/Desktop/论文修改/任务清单/final_experiment_package/` for experimental numbers. Verify a number and its protocol before inserting it.
- Draft Chinese prose in `drafts_zh/` first. Only move author-approved wording into `sections/*.tex` after the author confirms it. Never alter experimental results to improve the narrative.
- Keep names, dataset roles, metrics, and notation consistent with `drafts_zh/terminology.md`. Flag discrepancies instead of silently resolving them.
- After each approved LaTeX edit: compile, inspect the rendered PDF/log, update `CHANGELOG.md`, make a local Git commit, and sync source files to the existing `review-v1` repository using `sync_to_review_v1.py`.
