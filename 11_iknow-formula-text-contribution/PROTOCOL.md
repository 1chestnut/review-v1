# 任务11：固定iKnow聚合公式的文本贡献实验

## 唯一问题

固定任务06所采用的复现iKnow一跳联合归一化LSE，只改变同一组三元组的文本表达，判断AAKV文本语言化是否有效。

## 输出列

| 列 | 文本 |
|---|---|
| CLAP | 无KG |
| iKnow-05-Direct | 05冻结基线的 `head, tail` |
| RawTriple | `head relation tail` |
| Qwen-General | 任务09严格提示词的首次原始输出 `qwen_constrained`；不使用检查修复或人工模板回退 |
| AAKV | 任务10-hard生成的固定声音锚点、事实约束文本 |

CLAP为参考列；四个KG方法才是文本贡献的四列比较。

## 所有KG列共同使用的公式

`s = [logsumexp(kappa * [s_base, s_1, ..., s_n]) - log(n+1)] / kappa`

- kappa/logit scale=100；
- 不使用动态alpha；
- 不使用“先聚合再加权”的Ours公式；
- 不使用Top-P、二跳、gamma、delta或门控。

因此四个KG方法之间的差异只能来自文本表达。

## 冻结项

任务11直接读取任务06的样本、严格实体映射、关系集合、K=5、M=3、尾实体过滤、一跳三元组、CLAP、RotatE和评测口径。AAKV直接读取任务10-hard离线生成的JSON，不重新生成或根据准确率选择文本。

## 解释

- RawTriple vs iKnow-05-Direct：关系词是否有贡献；
- Qwen-General vs RawTriple：普通LLM自然语言化是否有贡献；
- AAKV vs Qwen-General：音频锚点和更严格约束是否带来增益；
- AAKV vs RawTriple：完整自动音频锚定语言化是否有效。
