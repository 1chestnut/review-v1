# 原 41 条语言建议的逐项处理状态

日期：2026-10-03。对象：main-4。原清单见 language_audit_original_41_20261003.md。

本轮不是重新翻译全文。保持方法、数值和论证含义，在上轮版本上补齐遗漏的语言修订；新改文字使用 redrevision 标红。原有红字保留。

## 1. 逐项状态

| 原编号 | 对象 | 当前状态 | 处理说明 |
|---|---|---|---|
| 1 | 摘要的 semantic information 与分类对象 | 本轮补齐 | 明确 class 和 audio sample，拆分句子 |
| 2 | 摘要的 omit the relations | 本轮补齐 | 改为 leave the connecting relations implicit，不暗示检索删除关系 |
| 3 | 摘要的逐关系预测 | 本轮补齐，按作者后续要求调整 | 不采用原建议的 predictors；描述逐关系计算的类别预测，同时明确原始 CLAP 分数参与计算 |
| 4 | 摘要末句 | 本轮补齐 | 压缩重复的三项操作，保留结果支持范围 |
| 5 | 引言中的 PAT 动词搭配 | 本轮补齐 | assign weights / combine；引用键不变 |
| 6 | 引言中的 Further use | 本轮补齐 | 指向当前音频样本的知识使用 |
| 7 | 引言中的 affect rankings | 本轮补齐 | alter candidate class rankings，不升级为 distort |
| 8 | 引言中的 fusion 总结 | 本轮补齐 | 明确 knowledge evidence 的分数权重 |
| 9 | Related Work 的路线概括 | 暂缓 | 按作者要求不修改相关工作正文 |
| 10 | Binary Attribute Embeddings 主语 | 暂缓 | 拟加 method，不改作者方法含义 |
| 11 | PAT 的 ensemble 作动词 | 暂缓 | 拟改 assign weights / weighted combination，不改算法 |
| 12 | Related Work 中 AAKV 的文本转换表达 | 暂缓 | 与全文已定表达协调后由作者确认 |
| 13 | 图结构学习与推理检索的区别 | 暂缓 | 不修改相关工作中的归纳句 |
| 14 | iKnow-audio 初始候选的确定来源 | 暂缓 | 拟明确由输入音频的 CLAP 预测确定 |
| 15 | Figure shows 而非 separates | 上轮已完成 | 保留 |
| 16 | tails → tail entities | 上轮已完成 | 保留 |
| 17 | s_final 的类别指代 | 上轮已完成 | 明确是 c_i 的分数 |
| 18 | 三元组 plausibility 的归属 | 上轮已完成 | 合理性属于模型评分下的三元组 |
| 19 | 实体措辞与关系语义的并列 | 本轮补齐 | 分清 head/tail wording 与 relation meaning/direction |
| 20 | AAKV 检查规则 | 上轮已完成且已核对代码 | 保留 lexical/format/predefined prohibited expressions 描述 |
| 21 | we collect 陈述式 | 上轮已完成 | 算法仍保留操作式 |
| 22 | 共识平局规则的比较动作 | 上轮已完成 | 指向 larger sum，再比较较小类别索引 |
| 23 | 最终融合输入的表述 | 本轮补齐 | aggregated knowledge score 与 original CLAP score；公式不变 |
| 24 | iKnow† 的比较角色 | 上轮已完成 | 明确知识增强对照；CLAP 是无外部知识对照 |
| 25 | 标签格式统一 | 上轮已完成 | standardize class label formatting |
| 26 | M 是最大保留数量 | 上轮已完成 | 不误写实际数量恒等于 M |
| 27 | MRR 的正标签定义 | 上轮已完成 | highest-ranked ground-truth label |
| 28 | iKnow† 结果而非方法支持结论 | 本轮补齐 | 直接命名 SAKI 相对 iKnow† 的进一步收益 |
| 29 | FSD50K 的指标变化 | 本轮补齐 | MRR 略增，Hit@1 接近；不补新机制 |
| 30 | Random Top-5 比谁低 | 本轮补齐 | 明确 than those of SAKI |
| 31 | dominant set 的正文表达 | 本轮补齐 | most frequent set；表中指标专名仍保留 |
| 32 | 语言化的两个比较对象 | 本轮补齐 | Hit@1 对两个对照；ESC-50 的 MRR 对 Raw triple |
| 33 | 统计分析开头 | 本轮补齐 | 明确 Hit@1/MRR 与 paired bootstrap confidence intervals |
| 34 | 正向预测转移的方向 | 本轮补齐 | incorrect iKnow† → correct SAKI |
| 35 | 共识与共同匹配偏差 | 上轮已完成 | 保留 may reflect，不升级因果结论 |
| 36 | MRR 打破同分的重复句 | 本轮补齐 | 删除第二次重复说明，其余参数结果保留 |
| 37 | 预热措辞 | 本轮补齐 | processed 20 samples for warm-up |
| 38 | 计算成本的共同参照 | 本轮补齐 | 明确以 CLAP 比较峰值显存与延迟的比例增幅 |
| 39 | Conclusion 动词搭配 | 本轮补齐 | support coordinating，保留 under the evaluated settings |
| 40 | 附录 A 的 greedy decoding 说明句 | 保留，待确认 | 仅涉及作者解释句，不是生成指令，但本轮为保护附录 A 未改 |
| 41 | 附录 A 的检查条件说明句 | 保留，待确认 | 同上；原始指令和模板始终不改 |

合计：原 41 条中，33 条已落实（含上轮完成和按作者后续意见调整的建议），8 条暂缓。33 条中有 21 条本轮补齐，12 条上轮已完成。

## 2. 原清单中需要纠正的判断

原清单另列的“三处缺少 Appendix”不适用于当前模板。aux 中标签值已经是 Appendix A、Appendix B、Appendix D；给 ref 再加 Appendix 会重复。本轮保留正确的引用输出，不将它们记为遗漏。

Table 5 的两条缺冠词缓存文本属于真实输入记录，保留逐字内容，并在表注明确 reproduced verbatim。附录 A 的提示词、修复指令和模板也逐字保留。

## 3. 相关工作待确认的具体建议

以下尚未写入相关工作正文；是对现有含义的语言调整，不是新增文献结论。原文核对资料保留在 work/related_work_audit_20261003/。

1. 第9条：将路线概括句中的分别对应关系改为 concern ... and the incorporation of relational knowledge into classification。属于本文归纳，不是某一原文的直接结论。
2. 第10条：Binary Attribute Embeddings 前加 The，名称后加 method。其原文的属性表示含义不变；这不是修正作者名称。
3. 第11条：PAT 的 weight and ensemble text representations 改为 assign weights to the text representations and compute their weighted combination。与论文 Algorithm 1 / 加权提示集成一致。
4. 第12条：AAKV therefore converts the supplied entities and directed relation into descriptions of sounds under explicit content constraints。保留已定的 descriptions of sounds；这句描述本文而非引用论文的方法。
5. 第13条：retrieving external graph evidence during inference differs from incorporating graph structure into model learning。保留本文对学习与推理的归纳，不声称前文所有研究使用同一种图谱检索机制。
6. 第14条：Its graph scores assess entity--relation compatibility, whereas CLAP predictions for the input audio determine the initial candidate classes。与 iKnow-audio 的先 CLAP 初始预测、再图谱扩展一致，不把初始候选和关系筛选混同。

## 4. 附录 A 待确认的两项说明句

仅建议改作者说明文字，不改任何逐字生成指令：

- Qwen2.5-7B-Instruct is decoded greedily → Text is generated with Qwen2.5-7B-Instruct using greedy decoding。
- a maximum of 30 words, a single line and sentence → a 30-word limit and the requirement for a single sentence on one line。

## 5. 额外一致性处理与核查

- 符号表明确 tail entity set 与 evidence score sequence；不改符号或公式。
- 附录 D 表头明确 Mean Jaccard similarity with FrozenRq；附录 E 使用客观的 Incorrect → correct / Correct → incorrect，与正文一致。
- 更新术语规则与旧 CSV 中的四个过时条目，防止下一轮重新引入 relation expert、classification margin、hierarchical knowledge fusion、controlled reproduction。
- Related Work 源文件与本轮前版本完全相同；附录 A 完全相同。所有编号公式、无编号显示公式、引用键、标签、报告的数值及实验表格正文均通过保护检查。
- 新流程图仍原样使用 图片3.png；没有修改其位图文字或其他图的绘图数据。
