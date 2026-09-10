# 任务09：Qwen约束式、可核验的一跳关系语言化

## 唯一研究问题

在任务06完全相同的一跳证据和推理配置下，将三元组自动语言化，能否达到或超过人工关系模板？

## 冻结项（直接继承任务06）

- 六个数据集、音频、标签、多标签排名口径；
- 严格实体映射及其哈希；
- 每个数据集的关系集合；
- KG、RotatE、尾实体过滤和已经保存的一跳三元组；
- K=5、M=3、Top-P=5；
- CLAP版本、类别文本、logit scale=100；
- 归一化LSE、动态alpha范围[0.4,0.8]；
- 仅一跳，不加入二跳、gamma、delta或门控。

## 唯一改变变量

同一条 `(head, relation, tail)` 的文本表达。

| 列 | 含义 |
|---|---|
| CLAP | 不使用KG证据 |
| Manual-Template | 任务06原有人工关系模板 |
| Qwen-Constrained | Qwen2.5-7B-Instruct固定提示词的首次确定性输出 |
| Qwen-Verified | 自动检查；首次失败则重写一次，仍失败回退Manual-Template |

Qwen使用 `do_sample=False`。生成在正式音频推理前离线完成并缓存，不计入在线推理时间。

## 输出

- `prompts/qwen_generation_audit.json`：每条三元组、首次输出、失败原因、修复输出、最终文本和回退状态；
- `cache/qwen_text_embeddings.pt`：生成文本的CLAP嵌入缓存；
- `results/qwen_verified_table.csv`：四列Hit@1/3/5和MRR；
- `results/qwen_verified_results.json`：协议、指标和逐样本排名。

## 解释边界

- `Qwen-Constrained`用于显示未经回退的实际生成效果；
- `Qwen-Verified`才是完整方法；
- 若Qwen-Verified不优于Manual-Template，不把LLM语言化作为主创新；
- 本任务不使用真实标签选择文本，也不进行样本级Oracle选择。
