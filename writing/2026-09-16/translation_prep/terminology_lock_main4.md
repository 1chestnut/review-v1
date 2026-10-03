# SAKI main-4 统一术语表（已采纳的翻译规范）

2026-10-02 对 `main-3.tex` **实际 `\input` 的七个正文文件及附录、摘要、关键词、算法、图表标题和实际插入的 `figures/method_overview_main3.png`** 做了全稿核查。本表是后续 main-4 英文稿的唯一措辞基准。**“全文统一”指一个概念固定一个英文名称；允许语法需要的单复数和句首大写，但不允许同义词轮换。**方法专名、算法动作和数学符号应分别保持一致。当前未改动 main-3 的任何论文内容或图片。

## 2026-10-03 作者确认后的术语修订（优先于下方历史条目）

- 不再将本文逐关系评分分支命名为 `relation-specific predictor`。正文采用动作句：`For each relation, we compute class scores ...`；其结果称 `class predictions computed separately for each relation`。图中短标签为 `Predictions for 47 relations`。共享冻结的 CLAP，不增加或训练独立模型。
- 保留 `relation-specific class score`、`top-1 prediction`、`top-two score gap`，三者分别指分数、预测类别和前两名分数差。
- `CLAP` 是 `knowledge-free baseline`；`iKnow†` 是 `knowledge-enhanced baseline`。结果段优先直接写比较方法名，不使用无明确指代的 baseline。
- 介绍 iKnow-audio 原文时允许并保留其 `enriched prompts` 和 `curated subset of informative relations`；不为词汇统一改写已经核实的原文用语。
- 附录 A、缓存文本逐字记录、文献原题不适用一般语言改写；以下旧进度说明是历史记录，不代表当前完成状态。

## 全文执行规则

1. 摘要和正文可各自独立定义缩写；同一阅读单元内首次写英文全称加缩写，后续只用缩写。图题、表题如需独立阅读，可再展开一次，但全称拼写必须完全相同。
2. 正式模块名固定为 `Audio-Aligned Knowledge Verbalization (AAKV)`、`Sample-level Relation Selector` 和 `Hierarchical Fusion`；描述处理过程时才分别使用小写的 `knowledge verbalization`、`sample-level relation selection` 和 `evidence aggregation/score fusion`。正式名称不可在章节间变形。
3. 中文“关系专家”固定译为 **relation-specific predictor**，首次说明它是由一类关系的缓存证据构成的评分分支，**不是单独训练的模型**。它的输出分开称为 `relation-specific class scores`、`top-1 prediction` 和 `top-two score gap`。图、算法、摘要与正文均遵守这个区分。
4. `iKnow-audio`（原论文方法）、`iKnow†`（本文受控复现）和 `FrozenRq`（固定关系集合对照）不是同义词，绝不替换使用。
5. 数学变量保持 `s_{\mathrm{base}}`、`s_{\mathrm{final}}`、`\Delta_r`、`N_r`、`A_\lambda` 与正文一致；英译不得重新命名变量。指标固定写 `Hit@1`、`Hit@3`、`Hit@5`、`MRR`，差值单位写 `percentage points`。

## 1. 方法与核心机制

| 中文概念 | 全文固定英文 | 首次定义／使用边界 | 不再交替使用 |
|---|---|---|---|
| 本文方法 | Sample-Adaptive Knowledge Integration (SAKI) | 摘要和正文首次出现均写全称；后文 `SAKI` | `our method` 可作语法指代，但不另造框架名；标题目前多了 `Relational`，属描述性论文标题，见下方核查项 |
| 音频对齐知识语言化 | Audio-Aligned Knowledge Verbalization (AAKV) | 作者专名保留；紧跟说明：按声音导向的文本形式语言化三元组，以供 CLAP 音频–文本匹配；**不以当前音频作为生成条件** | 不把 `audio-aligned` 写成 learned alignment 或 audio-conditioned generation |
| 样本级关系选择（过程） | sample-level relation selection | 依据每条音频的关系特异性预测选关系 | `instance-wise relation adaptation`、`dynamic relation filtering` 等变体 |
| 样本级关系选择器（模块／消融标签） | Sample-level Relation Selector | 消融表及正式模块首次定义；并非训练得到的独立选择网络 | `relation selector` 可以泛指，但正式模块名只用这一项 |
| 关系专家（计算角色） | relation-specific predictor | 每种关系使用本关系缓存证据构成一条评分分支，共享 CLAP，不分别训练 | 把 `expert` 当作独立模型；与 `relation-specific class scores` 混为一词 |
| 单种关系的类别评分 | relation-specific class scores | 每种关系仅用本关系证据得到全类别评分向量 `s_r` | `expert logits`（不是 logits）、`independently trained expert scores` |
| 单种关系的首位预测 | top-1 prediction | 每种关系的评分向量对应一个 `\hat y_r` | `expert vote`（可描述投票动作，但不可替代输出名） |
| 共识类别 | consensus class | 最多 Top-1 票；并列按支持者分数差之和、固定类别索引打破 | `majority class`（无需过半） |
| 逐关系 Top-1 投票 | top-1 voting | 具体动作写 `the class receiving the most top-1 votes` | 单独的 `prediction consensus`、`majority voting` |
| 前两名分数差 | top-two score gap | `Δ_r=s_r^(1)-s_r^(2)`；属于分数差，不是概率或几何间隔 | `classification margin`、`confidence margin` |
| 关系排序 | relation ranking | 先排列支持共识类别的关系，组内按 gap 降序；不足 `N_r` 时从其他关系补足；同分按固定关系名称顺序 | “仅从支持共识类别的关系中选足五种” |
| 所选关系 | selected relations | 推理中是有优先级的前 `N_r` 项；Jaccard 和“组合数”统计时转为无序集合 | 在同一处把 ordered list 与 unordered set 混同 |
| 分层融合（正式模块） | Hierarchical Fusion | **作者既定消融模块名**；首次定义“两步”：先类别内聚合知识证据分数，再与 original CLAP score 融合；不涉及类别本体层级 | `Hierarchical evidence fusion` 若作为第二正式名称；`class-hierarchy fusion` |
| 第一阶段 | evidence aggregation for each class | 对选定关系中去重后的全部有效证据分数应用 `A_λ` | `fuse all classes`、仅聚合单条最优证据 |
| 第二阶段 | score fusion with the original CLAP score | `α s_base+(1−α)A_λ(U)`；无证据或非初始 Top-K 保留原分数 | `knowledge and CLAP jointly pooled by one LogSumExp`（这是另一配置） |

说明：`relation-specific predictor` 是本文对计算角色的**工作定义**，不是声称它是已有领域专名或单独训练的网络。翻译正文时优先使用动作句，如 “For each relation, we compute class scores using only its evidence”。图中角色可写 `Relation-specific predictors`，输出列写 `Relation / Top-1 class / Top-two score gap`。

## 2. 模型、图谱、文本与评分

| 中文概念 | 全文固定英文 | 边界 |
|---|---|---|
| 零样本音频分类 | zero-shot audio classification | 标准任务名；标题、关键词、正文统一大小写规则 |
| 对比语言–音频预训练模型 | Contrastive Language-Audio Pretraining (CLAP) | 摘要与正文可各自独立首次定义；原论文全称 |
| 音频–语言模型 | audio-language model | 不与 CLAP 专名全称互换 |
| 音频中心知识图谱 | Audio-centric Knowledge Graph (AKG) | iKnow-audio 原文专名 |
| 知识图谱嵌入 | knowledge graph embedding (KGE) | 普通类别名，不等于 RotatE 专名 |
| 图谱三元组 | knowledge graph triple | `(head entity, relation, tail entity)` |
| 头实体、关系、尾实体 | head entity, relation, tail entity | 分别对应 `h_i,r,t` |
| 类别–实体映射 | class-to-entity mapping | 不是跨模态 embedding alignment |
| 尾实体检索 | tail entity retrieval | RotatE 按三元组合理性评分，离线执行 |
| 有效尾实体 | retained tail entities | 指过滤并去重后保留者；若强调规则，再明确具体规则 |
| 知识文本／AAKV输出 | verbalized knowledge text | 本文产物；必要时解释为 `graph-derived textual evidence` |
| 知识增强提示 | knowledge-augmented prompt | **仅在描述 iKnow-audio 原文做法时**用该术语 |
| 原始 CLAP 分数 | original CLAP score | 对应 `s_base`；不译成 `base CLAP score`、`initial score`（后者可指初始排序状态） |
| 关系特异性分数 | relation-specific class score | 对应 `s_r` |
| 聚合后的知识分数 | aggregated graph-evidence score | 对应 `A_λ(U)`，尚不是最终分数 |
| 最终类别分数 | final class score | 对应 `s_final`，全部类别最终排名依据 |
| 归一化缩放 LogSumExp | normalized scaled log-sum-exp aggregation | `A_λ=(1/λ)log[(1/n)Σexp(λu_j)]`；与 iKnow 原公式不可误称完全一致 |
| 类别重排序 | class reranking | spelling 全文选 `reranking`；引用原文标题 `Re-ranking` 可照其原题 |
| 离线知识准备 | offline knowledge preparation | 类别–实体映射、尾检索、AAKV、文本向量缓存 |
| 在线推理 | online inference | 当前音频编码、逐关系评分、选择、融合及排序 |
| 文本向量缓存 | cached CLAP text embeddings | 不笼统写 `text cache`，以免误解只缓存字符串 |
| 跨关系去重 | deduplication across selected relations | 以规定的尾实体键去重，优先级高的文本保留 |

## 3. 实验配置、数据集与指标

| 中文概念 | 全文固定英文 | 边界 |
|---|---|---|
| 受控复现 | controlled reimplementation | 首次写 `iKnow† denotes our controlled reimplementation of iKnow-audio`；不是原系统逐项复刻；附录现存 `controlled-reproduction` 待 main-4 统一 |
| 数据集级固定关系集合 | dataset-specific fixed relation set | 本文 iKnow†/FrozenRq 配置；不要归为 iKnow 原文直接措辞 |
| 固定集合对照 | FrozenRq | 实验配置专名不翻译，首次定义 |
| 高频关系对照 | Frequency Top-5 | 专名原样保留 |
| 随机关系对照 | Random Top-5 | 专名原样保留 |
| 直接拼接 | Direct concatenation | 知识文本对照专名 |
| 原始三元组字段文本 | Raw triple | 知识文本对照专名 |
| 五数据集等权平均 | unweighted mean across five datasets | 先求每数据集指标，再对五个值取算术平均；不说 sample-weighted mean |
| Hit@1 / Hit@3 / Hit@5 | Hit@1 / Hit@3 / Hit@5 | 大小写、`@`、`k` 一致 |
| 平均倒数排名 | mean reciprocal rank (MRR) | 摘要和正文首次出现视独立阅读需要定义 |
| 百分点 | percentage points | 不写成 percent 的相对提升 |
| 成对 Bootstrap | paired bootstrap resampling | 统计图、正文和附录保持同一写法 |
| 精确 McNemar 检验 | exact McNemar test | 仅对应成对 Hit@1 正误 |
| Holm 校正 | Holm adjustment | 对五个 McNemar p 值的多重比较校正 |
| 在线推理延迟 | online inference latency | 单位 `ms/sample` |
| 吞吐量 | throughput | 单位 `samples/s` |
| 峰值 GPU 显存 | peak GPU memory usage | 与离线 cache size 分开 |
| 离线缓存规模 | offline cache size | 不包含模型权重、源 KG 或原始音频，按当前实验口径 |
| 五个最终测试集 | ESC-50; UrbanSound8K; FSD50K; AudioSet; TUT2017 | 名称照数据源与主表固定；排序尽量与主表一致 |
| 开发集 | DCASE17-T4 development set | 不列入五个最终测试集 |

## 4. 目前 main-3 尚存的同名冲突／同步点

这部分是**待翻译时统一的定位清单**，不是已经修改的内容：

1. `main-3.tex:100` 的“知识增强分类专家”，以及引言、Related Work、Method、Discussion、Conclusion 中“关系专家”，统一为 `relation-specific predictor`，首次定义其是评分分支；描述计算结果时分别用 `relation-specific class scores`、`top-1 prediction` 和 `top-two score gap`。`sections/03_method.tex:76–123` 应保留真实算法规则，不可只机械替换单词。
2. `sections/03_method.tex:98–123` 的“分类间隔”翻为 `top-two score gap`；`sections/01_introduction_main3.tex:10`、`sections/02_related_work_main3.tex:27,35`、`sections/05_discussion.tex:8` 和摘要也同步。公式符号 `Δ_r` 不变。
3. `sections/03_method.tex:105–123` 的“预测共识”写为 `top-1 voting` 的**过程**与 `consensus class` 的**结果**；不要同时用多个英文名称指同一投票规则。
4. `sections/03_method.tex:125,139` 使用 `Hierarchical evidence fusion`；消融表及正文多处写 `Hierarchical Fusion`。正式模块名统一为后者；两阶段动作分别写 `evidence aggregation` 和 `score fusion`。图中的 `(c) Hierarchical fusion` 可按标题大小写处理。
5. 实际插图由 `main-3.tex:32` 指向 `figures/method_overview_main3.png`，**不是**旧的 `figures/saki_framework.png`。现图仍有 `47 relation experts`、`Base class scores`、`Ranking by Consensus and Margin`；后续图文同步时分别改为 `47 relation-specific predictors`、`Original CLAP scores`、`Relation ranking by consensus class and top-two score gap`（如空间不足可简写 `Relation ranking`，并在图注解释规则）。图式中的 `s_KG` 也应先在方法中对应 `A_λ(U_i*)`，不宜仅替换标签。
6. `sections/07_appendix_main3.tex:153` 标题为 `Sample-Adaptive Relation Selection Behavior`，而正式选择模块叫 `Sample-level Relation Selector`；可统一为 `Sample-level Relation Selection Behavior`。这是同一选择行为，不是另一个模块。
7. `sections/07_appendix_main3.tex:62,66` 的 `controlled-reproduction` 与本表锁定的 `controlled reimplementation` 不同；在 main-4 一并统一。
8. `main-3.tex:62` 论文标题写 `Sample-Adaptive Relational Knowledge Integration`，方法首次定义为 `Sample-Adaptive Knowledge Integration (SAKI)`。标题可以作为**描述性论文题名**保留，但不可在正文把带 `Relational` 的版本又称为 SAKI 的全称。
9. 数学符号全文用 `λ` 表示 LogSumExp 固定尺度；最终服务器代码中的配置键 `kappa=100` 指同一数值。若代码及其协议作为补充材料公开，应给出 `paper λ = implementation kappa` 的对应关系或统一配置字段，不应在论文里混用两个符号。
10. `iKnow†`、`iKnow-audio`、`FrozenRq` 是**三个不同指代**：本文受控复现、原作者方法、固定关系集合对照。翻译不能为了词汇变化而互换。

## 5. 使用规则与完成状态

- **已核定**：上表的概念区分、英文固定措辞、首字母大小写原则，以及用户采纳的 AAKV/关系特异性预测/前两名分数差/投票/两步融合的解释方式。
- **翻译进度**：main-4 的摘要和引言已按本表翻译；其他章节仍沿用 main-3 的中文源码，因此尚不能声称“英文全文已经统一”。图像文字尚未修改；`tang2023sinet` 全文 PDF 仍缺，不将其归入已全文核实的来源。
- 每翻译一个小节，都对照本表；翻译全部完成后再扫一次摘要、正文、图、表、算法、附录和参考文献中的缩写与大小写。新的作者专名只有经作者同意后才能加入本表。
