我已对照当前 [main-4.pdf](C:/Users/zkx/Desktop/论文修改/写作/latex/main-4.pdf) 及其 LaTeX 源码完成这一轮语言审核，范围包括摘要、正文、算法、图表文字和附录。**本轮没有修改文件、实验数据、公式或引用键。**以下区分“明确需要修正”和“建议润色”，不会把正确表达也当成错误。

## 1. 总体评价

全文语言已经具备较好的可读性，没有发现大量明显的单词拼写错误，美式拼写也整体一致。主要问题集中在少数缺词、表达搭配不自然、比较对象不够明确，以及正文、图表和旧术语表之间的名称差异。冠词和主谓一致没有普遍性错误，但真实缓存文本中存在缺少冠词的句子，需要与作者正文分开处理。建议进行一次以术语统一和对象指代为中心的精修，不需要重新翻译全文。

## 2. 明显 typo、缺词与不完整表达

以下是本轮确认的问题；没有为了凑数量，把普通润色列成拼写错误。

| 位置 | 原文 | 修改建议 | 说明 |
|---|---|---|---|
| 3.3，AAKV 协议指引 | `\ref{app:aakv-protocol} specifies...` | `Appendix~\ref{app:aakv-protocol} specifies...` | 缺少 Appendix；当前显示为“A specifies…” |
| 4.1.2，复现协议指引 | `documented in \ref{app:reproduction}` | `documented in Appendix~\ref{app:reproduction}` | 缺少 Appendix |
| 4.3.2，行为分析指引 | `\ref{app:selector-behavior} reports...` | `Appendix~\ref{app:selector-behavior} reports...` | 缺少 Appendix |
| Figure 1 模块标题 | `(a)CLAP initial ranking` | `(a) CLAP initial ranking` | 面板编号后缺少空格 |
| Figure 1 离线模块 | `RotatE tail` | `RotatE tail retrieval` | 标签不完整，没有表达执行的操作 |
| Figure 1 融合模块 | `score fusion` | `Score fusion` | 与其余框内标签的首字母格式不一致 |
| Table 5 缓存原文 | `The sound of wind is instance of ocean.` | 语法修正形式为 `The sound of wind is an instance of ocean.` | 缺少冠词 an；但属于真实缓存记录，不能直接替换 |
| Table 5 缓存原文 | `The sound of engine is instance of motorcycle.` | 语法修正形式为 `The sound of engine is an instance of motorcycle.` | 同上；实体措辞应保持原样 |

**Table 5 的两句需要特殊处理。**它们是实验实际读取的文本，不应为了语法正确而静默修改。建议保留原文，并在表注中简短说明：

> Cached evidence texts are reproduced verbatim.

这样明确区分“模型输出的原始文本”和“作者撰写的英文正文”，不必逐句添加 `[sic]`。

## 3. 语法、用词和句子层面的修改

### 3.1 摘要与引言

**① 摘要：知识与类别的关系、分类对象不够明确**

Original:

> Knowledge graphs can add semantics absent from short class names, but knowledge related to a class may not help distinguish it in the current audio.

Revised:

> Knowledge graphs can supply semantic information absent from short class names. However, knowledge associated with a class may have limited value for distinguishing that class in a given audio sample.

说明：`add semantics` 较抽象；`distinguish it in the current audio` 指代和搭配不够自然。修改后仍保留“类别相关知识不一定具有样本判别价值”的原意。

**② 摘要：`omit the relations` 容易被理解为删除图谱关系**

Original:

> Moreover, prompts that concatenate class names with retrieved tail entities omit the relations connecting them, leaving part of the graph's meaning unexpressed.

Revised:

> Prompts formed by concatenating class names with retrieved tail entities leave the connecting relations implicit, expressing only part of the retrieved graph information.

说明：这里准确的问题是文本没有显式表达关系，而不是检索过程删除了关系。

**③ 摘要：关系预测的表述偏绕**

Original:

> SAKI then selects relations using class predictions obtained separately from each relation's evidence.

Revised:

> SAKI then selects relations based on the class predictions produced by relation-specific predictors.

说明：使用已经确定的术语，避免再次解释同一对象。预测器的具体定义放在方法部分。

**④ 摘要：最后一句偏长，重复列举方法**

Original:

> These results indicate that selecting relations for individual audio samples, preserving their meaning in text, and combining their evidence with the original CLAP prediction can improve the use of structured knowledge in zero-shot audio classification.

Revised:

> These results support adapting graph evidence to individual audio samples through relation selection, constrained verbalization, and score fusion for zero-shot audio classification.

说明：保留结论范围，压缩重复描述；没有增加新的贡献。

**⑤ 引言：PAT 的两个动词结构不协调**

Original:

> PAT uses downstream-task audio to weight and ensemble prompts, and aligns audio and text representations.

Revised:

> PAT uses audio from the downstream task to assign weights to prompts and combine them. It also aligns audio and text representations.

说明：`ensemble` 作动词并非错误，但这里 `assign weights ... and combine ...` 更明确，也避免 `downstream-task audio` 的密集复合修饰。

**⑥ 引言：`Further use` 没有清楚指向要解决的问题**

Original:

> Further use of this knowledge requires considering its discriminative value for the current audio.

Revised:

> Using this knowledge for a given audio sample also requires assessing its discriminative value for that sample.

说明：把对象从泛泛的“进一步利用”明确为“对当前样本利用知识”。

**⑦ 引言：`affect` 的确较泛**

Original:

> Weakly related knowledge may also affect class rankings.

Revised:

> Knowledge weakly related to the input audio may also alter candidate class rankings.

说明：此处不能直接改成 `distort`，因为原句没有明确声称一定产生负面变化。`alter` 准确表达“改变排序”，避免擅自加强结论。

**⑧ 引言：融合机制的总结不够自然**

Original:

> This separates evidence aggregation from control over its contribution to the final class ranking.

Revised:

> This separates evidence aggregation from the weighting of knowledge evidence in the final class scores.

说明：`control over its contribution` 偏抽象；修改后直接对应类别分数计算。

### 3.2 Related Work

**⑨ 相关工作开头：三类研究与三个概念的映射过于机械**

Original:

> These research directions address cross-modal matching, the information supplied by class descriptions, and the use of relations in classification, respectively.

Revised:

> These directions concern cross-modal matching, semantic information in class descriptions, and the incorporation of relational knowledge into classification.

说明：`the information supplied by...` 可压缩；不必用 `respectively` 强行建立严格的一一对应。

**⑩ 2.2：方法名称与动词单复数容易使读者停顿**

Original:

> Binary Attribute Embeddings represents classes through attributes such as pitch, duration, and source material.

Revised:

> The Binary Attribute Embeddings method represents classes through attributes such as pitch, duration, and source material.

说明：原句不一定是主谓一致错误，因为名称可以指一个方法。增加 `method` 后，单数主语更加明确。

**⑪ 2.2：`ensemble text representations` 可明确为聚合**

Original:

> It uses these sums to weight and ensemble text representations.

Revised:

> It uses these sums to assign weights to the text representations and compute their weighted combination.

说明：保持原来“赋权并集成”的含义，减少动词 `ensemble` 带来的理解负担。

**⑫ 2.2：`description of sound` 与全文习惯不同**

Original:

> AAKV therefore verbalizes the supplied entities and directed relation as a description of sound under explicit content constraints.

Revised:

> AAKV therefore converts the supplied entities and directed relation into a sound description under explicit content constraints.

说明：统一为 `sound description`，并用 `converts ... into ...` 清楚表达输入与输出。

**⑬ 2.3：结尾用词过泛**

Original:

> ...retrieving external graph evidence during audio–language inference involves a different process for using knowledge.

Revised:

> ...retrieving external graph evidence during inference differs from incorporating graph structure into model learning.

说明：准确表达这里比较的是“学习阶段融入结构”与“推理阶段检索证据”。

**⑭ 2.3：`initial candidates depend on the audio` 不够具体**

Original:

> Its graph scores assess entity–relation compatibility, while its initial candidates depend on the audio.

Revised:

> Its graph scores assess entity–relation compatibility, whereas CLAP predictions for the input audio determine the initial candidate classes.

说明：保留原意，明确谁根据音频确定候选类别。

### 3.3 Method

**⑮ 方法概述：Figure 并不是执行“分离”的主体**

Original:

> Figure 1 separates offline knowledge preparation from online inference.

Revised:

> Figure 1 shows the offline knowledge preparation and online inference stages.

说明：图展示两个阶段；框架才是划分和执行这些阶段的主体。

**⑯ 方法概述：`retrieves tails` 建议首次完整写明**

Original:

> ...retrieve tails with RotatE...

Revised:

> ...retrieve tail entities with RotatE...

说明：正文使用完整专业名称；图内受空间限制时可简称 `tails`。

**⑰ 3.1：`its final class score` 指代不清**

Original:

> ...where \(\hat y\) is the predicted class and \(s_{\mathrm{final}}(c_i\mid x^a)\) is its final class score.

Revised:

> ...where \(\hat y\) is the predicted class and \(s_{\mathrm{final}}(c_i\mid x^a)\) is the final score assigned to class \(c_i\).

说明：该函数是任意候选类别 \(c_i\) 的分数，不仅是预测类别 \(\hat y\) 的分数。

**⑱ 3.2：`the model's plausibility for triple` 搭配不自然**

Original:

> ...the score \(\phi_{\mathrm{KG}}(h_i,r,t)\) measures the model's plausibility for triple \((h_i,r,t)\).

Revised:

> ...the score \(\phi_{\mathrm{KG}}(h_i,r,t)\) measures the plausibility of triple \((h_i,r,t)\) under the embedding model.

说明：合理性属于三元组，不属于模型。

**⑲ 3.3：要求列表中的概念归属不平行**

Original:

> It also requires the original entity wording, relation meaning and direction, and tail entity to be retained without adding information beyond the triple.

Revised:

> It requires preserving the supplied head and tail wording, together with the relation's meaning and direction. No information beyond the triple may be added.

说明：`entity wording` 已包含尾实体措辞，后面再列 `tail entity` 不协调。修改后清楚区分“实体措辞”和“关系语义”。

**⑳ 3.3：检查内容有“检测存在”与“检查禁止”混杂**

Original:

> A rule-based check tests the required prefix, head and tail coverage, coverage of terms denoting the relation, sentence and length constraints, and prohibited additions.

Revised:

> Rule-based checks verify the required prefix, head and tail coverage, relation terms, and sentence and length constraints. They also check for prohibited additions.

说明：原列表没有明确是确认禁止内容存在，还是确认它们不存在。

**㉑ 3.4：方法叙述突然切换为操作指令**

Original:

> For class \(c_i\) and relation \(r\), collect the evidence scores...

Revised:

> For class \(c_i\) and relation \(r\), we collect the evidence scores...

说明：正文统一陈述式；祈使句留在 Algorithm 1 中。

**㉒ 3.4：`followed by the lower index` 省略了比较动作**

Original:

> Ties are resolved by the sum of supporting predictors' top-two score gaps, followed by the lower index in the fixed candidate class list.

Revised:

> Ties are first resolved by the larger sum of score gaps among supporting predictors. Remaining ties favor the lower index in the fixed candidate class list.

说明：明确两个逐级规则，保留原算法。

**㉓ 3.5：`At final scoring` 搭配生硬**

Original:

> At final scoring, Eq. (7) combines the merged evidence sequence with the original CLAP score, rather than with a relation-specific score.

Revised:

> At the final scoring stage, Eq. (7) combines the aggregated knowledge score with the original CLAP score.

说明：真正参与加权的是聚合后的知识分数，而不是直接把证据序列与标量相加。公式保持不变。

### 3.4 Experiments

**㉔ 4.1.2：iKnow† 方法条目没有直接说明身份**

Original:

> Our controlled reimplementation provides the knowledge-enhanced comparison method.

Revised:

> Our controlled reimplementation of iKnow-audio serves as the knowledge-enhanced baseline.

说明：明确复现对象及其比较角色，也为后文的 `baseline` 提供指代。

**㉕ 4.1.3：降低“提示工程差异”的描述过宽**

Original:

> Candidate class labels are lowercased, and underscores are replaced with spaces to limit differences due to prompt engineering.

Revised:

> We lowercase candidate class labels and replace underscores with spaces to standardize label formatting.

说明：这两项操作直接统一的是标签格式，不足以概括整个 prompt engineering。

**㉖ 4.1.3：计数参数含义需要准确**

Original:

> ...\(M\) is the number of tail entities retained for each class–relation pair.

Revised:

> ...\(M\) is the maximum number of tail entities retained for each class–relation pair.

说明：正文已说明过滤后可能不足 \(M\) 个，因此这里应写最大数量。

**㉗ 4.1.4：单标签和多标签定义可以直接统一**

Original:

> MRR averages the reciprocal rank of the ground-truth class in the complete class ranking.

Revised:

> MRR is the mean reciprocal rank of the highest-ranked ground-truth label in the complete class ranking.

说明：与后面的多标签规则协调，不改变评价方式。

**㉘ 4.2：主语是方法名称，但实际提供证据的是结果**

Original:

> Under our common evaluation protocol, iKnow† supports the value of class-related knowledge, while SAKI provides further gains.

Revised:

> Under the common evaluation protocol, the results for iKnow† support the value of class-related knowledge. SAKI achieves further gains over this baseline.

说明：方法本身不“支持结论”，比较结果才提供支持。

**㉙ 4.3.1：`The difference chiefly involved` 不自然**

Original:

> The difference chiefly involved a small numerical increase in MRR, with nearly unchanged top-1 accuracy.

Revised:

> Adding Hierarchical Fusion slightly increased MRR, while Hit@1 remained nearly unchanged.

说明：直接交代变化来自哪个操作、体现在哪个指标。

**㉚ 4.3.2：Random 对照的比较对象被省略**

Original:

> Random Top-5 also varied the relation set across audio samples, yet its mean Hit@1 and MRR were lower by 2.06 and 0.95 percentage points.

Revised:

> Random Top-5 also varied relation sets across samples. Its mean Hit@1 and MRR were 2.06 and 0.95 percentage points lower than those of SAKI.

说明：明确“比谁低”，数值不变。

**㉛ 4.3.2：最大频率集合的名称建议统一**

Original:

> ...with the dominant set accounting for only 1.06%–1.53% of samples.

Revised:

> ...with the most frequent set accounting for 1.06%–1.53% of samples.

说明：`most frequent set` 更直接；图表中的指标名仍可保留 `Dominant-set share`，首次说明含义即可。

**㉜ 4.3.3：`ranking gains` 和前面所列 Hit@1 证据混用**

Original:

> AAKV therefore improved Hit@1 consistently across datasets, with larger ranking gains on FSD50K and TUT2017 and comparable performance between the two representations on ESC-50.

Revised:

> AAKV improved Hit@1 over both controls on all five datasets, with larger gains over Direct concatenation on FSD50K and TUT2017. On ESC-50, its MRR was comparable to that of Raw triple.

说明：分别说明 Hit@1 的对照与 MRR 的对照，避免 `the two representations` 指代不明。

**㉝ 4.4.1：统计分析的开头过度抽象**

Original:

> We examine whether sampling uncertainty analysis supports the metric gains of SAKI over iKnow†.

Revised:

> We assess uncertainty in the Hit@1 and MRR gains of SAKI over iKnow† using paired bootstrap confidence intervals.

说明：明确分析对象和所用方法。

**㉞ 4.4.2：转移方向表达不完整**

Original:

> Corrections from iKnow† to SAKI outnumbered reverse transitions on all five datasets...

Revised:

> Transitions from incorrect iKnow† predictions to correct SAKI predictions outnumbered the reverse transitions on all five datasets...

说明：明确比较的是同一样本在两个方法下的正误变化。

**㉟ 4.4.2：`retain matching biases` 搭配不自然**

Original:

> ...agreement across relation evidence may retain matching biases of the shared model.

Revised:

> ...agreement among their predictions may reflect matching biases shared by the underlying model.

说明：一致的是预测结果，不是“证据之间的一致”。保留 `may`，不把解释写成已验证机制。

**㊱ 4.4.3：重复解释 MRR 打破同分**

Original:

> MRR distinguishes configurations with identical Hit@1...

后文又写：

> MRR further distinguished configurations with the same top-1 accuracy.

建议：保留第一处，删除第二处重复句。

说明：属于语言冗余，不涉及删除有效实验信息。

**㊲ 4.4.4：预热描述不够地道**

Original:

> ...warmed up with 20 samples...

Revised:

> ...processed 20 samples for warm-up...

说明：明确是处理样本完成预热。

**㊳ 4.4.4：把不同性质的比例直接比较，文字容易误解**

Original:

> Compared with the latency ratio, peak memory increased modestly, whereas cache size increased substantially.

Revised:

> Relative to CLAP, SAKI showed a smaller proportional increase in peak GPU memory usage than in latency, while its cache size increased substantially.

说明：补出共同参照 CLAP，避免“memory 和 ratio 比较”。

### 3.5 Conclusion 与附录

**㊴ Conclusion：`support jointly considering` 不够自然**

Original:

> These findings support jointly considering sample relevance, text representation, and score fusion when incorporating structured knowledge into pretrained audio–language models under the evaluated settings.

Revised:

> Under the evaluated settings, these findings support coordinating sample relevance, text representation, and score fusion when incorporating structured knowledge into pretrained audio–language models.

说明：保留证据边界，改善动词搭配。

**㊵ 附录 A：模型不是被“解码”的对象**

Original:

> Qwen2.5-7B-Instruct is decoded greedily...

Revised:

> Text is generated with Qwen2.5-7B-Instruct using greedy decoding...

说明：解码的是输出序列，不是模型本身。

**㊶ 附录 A：检查项并列不协调**

Original:

> ...a maximum of 30 words, a single line and sentence, and the absence of prohibited formatting and acoustic property terms.

Revised:

> ...a 30-word limit, the requirement for a single sentence on one line, and the absence of prohibited formatting and acoustic property terms.

说明：把数量、格式和禁止内容写成明确的检查条件。实际生成指令的逐字引文应保持原样，不随正文润色修改。

## 4. 标点、大小写、时态与格式

### ① 文献叙述与实验结果的时态

当前整体合理，不需要把全文强行改成一个时态。建议锁定：

- 文献方法、本文方法机制：一般现在时，如 `CLAP learns`、`SAKI selects`。
- 已完成的实验操作和结果：一般过去时，如 `we selected`、`SAKI achieved`。
- 图表展示：一般现在时，如 `Table 1 shows`、`Figure 4 illustrates`。

“Table 1 shows that SAKI achieved...”是合理搭配，不属于时态混乱。

### ② 图、表、公式引用

正文目前主要使用 `Figure`、`Table`、`Section` 和 `Eq.`，可以保留这一套：

- `Figure 1`
- `Table 2`
- `Section 3.4`
- `Appendix A`
- `Eq. (7)`；多个公式用 `Eqs. (9)–(10)`

不要为了追求“统一”把所有名称都缩写。LaTeX 的 `Figure~\ref{...}`、`Eq.~\eqref{...}` 写法正确，`~` 可以避免编号与名称断行。

### ③ 模块名称与普通操作

建议区分：

- 模块专名：`Sample-level Relation Selector`、`Hierarchical Fusion`
- 普通操作：`sample-level relation selection`、`score fusion`

因此，正文模块名大写，而小节标题采用句首大写，并不一定冲突。Figure 1 中 `score fusion` 应改为 `Score fusion`，属于图内标签格式统一。

### ④ 百分号与单位

当前写法基本正确：

- 百分数：`64.46%`，不加普通空格。
- 单位：`44.1 kHz`、`743.22 MiB`，数值与单位之间留空格。
- 差值：`3.18 percentage points`，不写成 `3.18%`。
- `MiB` 保留，不换成 `MB`，两者不是相同单位。

### ⑤ 连字符

不能把所有连字符都删除。以下表达功能明确，可以保留：

- `zero-shot`
- `sample-level`
- `relation-specific`
- `top-two`
- `rule-based`
- `single-label`
- `highest-ranked`

建议减少的是 `downstream-task audio` 这类不必要的紧凑修饰，改为 `audio from the downstream task`。

`audio–text` 和 `audio–language` 表示两个模态或领域之间的联系，可以保持全文使用连接号。不要把 PDF 自动断行产生的 `classifi- cation` 当成源码拼写错误。

### ⑥ 图内英文

Figure 1 建议调整为：

| 当前文字 | 建议 |
|---|---|
| `Class-entity mapping` | `Class-to-entity mapping` |
| `RotatE tail` | `RotatE tail retrieval` |
| `Top-1`，表头 | `Top-1 class` |
| `Gap Δr` | 可保留，正文定义为 `top-two score gap` |
| `Vote A · Δr ↓` | `Votes for A · Δr ↓` |
| `Others · Δr ↓` | `Other votes · Δr ↓` |
| `score fusion` | `Score fusion` |

Figure 3 的图例 `Wrong → correct` 与正文 `incorrect → correct` 可统一为：

> Incorrect → correct  
> Correct → incorrect

### ⑦ 附录表头

建议：

- `Mean Jaccard vs FrozenRq` → `Mean Jaccard similarity with FrozenRq`
- `Rescued` → `Incorrect → correct`
- `Harmed` → `Correct → incorrect`

`Rescued/Harmed` 并非拼写错误，但拟人化较强，与正文采用的客观表达不一致。

## 5. 术语和符号的一致性

### 5.1 术语统一表

| 概念 | 当前不同写法或问题 | 建议锁定 |
|---|---|---|
| SAKI 名称 | 标题含 `Relational`，摘要全称不含 | 框架全称锁定 `Sample-Adaptive Knowledge Integration (SAKI)`；标题可含描述词 Relational，但不能当作另一个全称 |
| 关系预测器 | 正文 `relation-specific predictor`；旧术语表 `relation expert` | `relation-specific predictor` |
| 前两名分数差 | 正文 `top-two score gap`；旧术语表 `classification margin` | `top-two score gap` |
| 投票 | `top-1 voting` | 保留；不能替换成 `majority voting` |
| 共识类别 | `consensus class`；图内 `Consensus: A` | 正文 `consensus class`，图内可简称 |
| 原始 CLAP 分数 | 正文 `original CLAP score`；旧表 `base CLAP score` | 正文统一 `original CLAP score`，符号仍为 \(s_{\mathrm{base}}\) |
| 分层融合 | 正文 `Hierarchical Fusion`；旧表 `hierarchical knowledge fusion` | 模块名称 `Hierarchical Fusion` |
| 知识文本 | `knowledge text`、`knowledge texts`、`sound descriptions`、`descriptions of sounds` | 对具体 AAKV 输出用 `sound descriptions`；对输入表示类别用 `knowledge text` |
| 知识增强提示 | `enriched prompts`、`knowledge-augmented prompts`、`knowledge-enhanced...` | 作者叙述统一 `knowledge-augmented prompts`；逐字引文保留原措辞 |
| 类别名称 | `class names`、`class labels`、`class texts` | 不应全部替换：名称用 `class names`，类别标识用 `class labels`，实际编码文本用 `class text` |
| 重排序 | `rerank`、`reranking`；旧表 `re-ranking` | `rerank`、`reranking` |
| 五数据集均值 | `mean across five datasets`、`unweighted mean` | 首次完整定义，后文 `unweighted mean` |
| 聚合算子 | `log-sum-exp`、附录 `LogSumExp` | 普通叙述统一 `log-sum-exp` |
| 受控复现 | 正文 `controlled reimplementation`；旧表 `controlled reproduction` | `controlled reimplementation` |
| 数据集 | 开头顺序与各表顺序不同 | 全文列举顺序统一 ESC-50、UrbanSound8K、FSD50K、AudioSet、TUT2017 |

**旧术语表明显落后于当前稿件。**其中的 `relation expert`、`classification margin`、`hierarchical knowledge fusion` 和 `controlled reproduction` 应更新，否则下一轮翻译会重新引入旧表达。

### 5.2 `candidate ranking` 的介词不能机械统一

你老师提醒的重点应理解为：**同一语义关系使用稳定搭配，而不是全文只能使用 in 或 for。**

建议固定：

- 用于排序的证据：`evidence for candidate class ranking`
- 排序过程中：`during candidate class ranking`
- 排序发生变化：`changes in candidate class rankings`
- 改善排序：`improve candidate class ranking`
- 对类别重排序：`rerank candidate classes`

`evidence in candidate ranking` 容易模糊“证据出现在哪里”与“证据用于什么”。但 `changes for candidate ranking` 也不能替代 `changes in candidate class rankings`。

### 5.3 符号与定义表

| 符号 | 当前问题 | 建议 |
|---|---|---|
| \(K,M,N_r\) | 符号表写成 `Initial candidate classes...and selected relations`，像是在定义对象 | 改为 `Number of shortlisted classes, maximum number of tails per class–relation pair, and number of selected relations` |
| \(\mathcal E_{i,r},\mathcal U_{i,r}\) | 表中只写 `Retained tails and evidence scores` | 改为 `Retained tail entity set and evidence score sequence` |
| \(\mathcal U_i^*\) | 正文是序列，表中未说明 | 明确为 `Merged evidence score sequence after tail deduplication` |
| \(\lambda\) | 当前定义为固定 scale | 保留 `aggregation scale`；不要与温度参数随意混称 |
| \(\alpha\) | 当前表示原始 CLAP 分数权重 | 保留；对应知识分数权重为 \(1-\alpha\) |
| \(\Delta_r\) | 图中简称 Gap，正文使用完整名称 | 可以；首次明确定义为 `top-two score gap` |
| \(R_q\)、\(\mathcal R\) | 分别用于原文关系子集和本文关系池 | 可以共存；注明来源区别，不必强行改成相同字体 |
| \(n\) | 公式中是证据条数；附录检验表中是样本数 | 属于局部定义复用，不构成公式错误，但各处必须解释清楚 |

公式中的 \(u_j\)、\(j=1,\ldots,n\) 与前面 \(u_{irt}\) 不冲突：前者是通用聚合序列的局部编号，后者是具体类别、关系和尾实体索引。当前方法已经解释了这一点，**不需要因为字母不同而改公式。**

## 6. 本轮建议的处理顺序

优先修正三类：

1. **明确缺词与指代问题**：三处 Appendix、\(s_{\mathrm{final}}\) 的解释、符号表的数量定义。
2. **全文术语与图表一致性**：关系预测器、分数差、原始 CLAP 分数、log-sum-exp，以及旧术语表。
3. **句子精修**：明确比较对象，减少抽象搭配与重复句，保留美式拼写和现有技术边界。

现有 `recognize`、`modeling`、`behavior`、`normalized`、`centered` 等美式写法可以保留。`forms of “be”` 中的 `forms`、AKG 关系名中的 `affects` 也不应机械替换：前者是准确的语法术语，后者是原始关系名称。

**这轮的重点不是把全文换成“更高级”的词，而是让每个词准确指向一个对象、每个比较明确指向一个对照。**以上修改均可以在不改变技术含义和数值的前提下实施；真实缓存文本及附录中的原始生成指令应保留逐字记录。
