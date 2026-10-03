# main-4 蓝色修改：原文依据

仅修改作者确认的四组语言/组织问题；不改实验数据、公式、原始提示指令或引用键。下列页码为 PDF 文件页码。

## 1. 摘要与引言

统一为 `reducing dependence on labeled audio`，删除 `annotated audio` 这一同义变体。不是声称预训练完全不需要标注，而是表述目标任务中的标注依赖。摘要保留 `for the target task`。

## 2. Related Work 2.1 衔接

- `complementary route` 改为说明配对数据与共享表示的具体句子，不改变后续 CLIP、AudioCLIP、Wav2CLIP 的文献陈述。
- 删除无明确并列对象的 `also`。从跨模态表示能力转向类别描述决定的文本语义输入，再引出 2.2。这是本文的结构性归纳，不冒充某篇论文的直接结论。

## 3. TSPE

原文：`C:/Users/zkx/Desktop/论文修改/写作/翻译文献库/anand2025tspe.pdf`。

- PDF p.2，III.B：作者向 GPT-4 提供任务与标签信息、声音属性及来源实例；随后人工将属性和来源映射到任务类别。
- PDF p.3，III.B/C：生成后人工筛选提示，并对提示的文本嵌入取平均。
- 短摘录：`we manually filter 20`；`then average these embeddings`。
- 修改明确保留人工筛选、属性/来源和嵌入平均；没有写成逐样本自适应提示或完全自动生成。

## 4. PAT

原文：`C:/Users/zkx/Desktop/论文修改/写作/翻译文献库/seth2025pat.pdf`，NAACL 2025 正式版本。

- PDF p.4–5，4.2、Algorithm 1、Eqs. (1)–(2)：对下游任务音频的最大类别预测 logit 求和，softmax 归一化后组合文本表示。因此正文压缩为利用该任务音频的预测对提示表示赋权并组合。
- PDF p.5，4.3、Eqs. (3)–(5)：帧级音频表示与组合后的文本表示计算注意力并进行变换。
- 短摘录：`a cumulative sum of maximum prediction logits`；`parameter free attention weights`。
- 保留任务级赋权范围，没有改写成每条音频分别确定提示权重，也没有称其训练新的注意力模块。

## 5. AudioCards

原文：`C:/Users/zkx/Desktop/论文修改/写作/翻译文献库/sridhar2026audiocards.pdf`。

- PDF p.1，Abstract；p.2，2.1；p.3，3.1–3.2：以声学属性和声音描述组织结构化元数据，并用于模型训练。
- PDF p.3–4，4.1–4.4：对应元数据生成、声音描述生成、文本–音频检索任务。
- 短摘录：`structured metadata grounded in acoustic attributes and sonic descriptors`；`training on audiocards improves downstream text-audio retrieval`。
- 单独作为声音设计这一相邻领域的段落，不将其归为零样本类别重排序方法，不将其写成无需训练的提示集成。

## 6. 段落功能

TSPE/PAT 段讨论提示构造、集成和表示适配；AudioCards 段补充相邻任务中的描述组织。下一段继续引出图谱三元组的实体及关系表达要求。原来只比较 PAT 和 AudioCards 的总结句已删除。
