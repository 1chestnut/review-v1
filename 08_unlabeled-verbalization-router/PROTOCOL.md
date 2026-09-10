# 任务08：无标签样本级文本路由

## 只回答一个问题

在不知道真实标签的情况下，当前音频能否根据三种知识表达产生的分类分布，自动选择 `Direct / RawTriple / Template`，并超过任务06中的最佳固定表达。

## 固定项

- 严格复用任务06的样本、CLAP、映射、关系集合、K=5、M=3、Top-P=5、动态 alpha、归一化LSE及三种证据文本缓存。
- 不加入二跳、门控、LLM或新的知识关系。
- 类别概率统一使用 `softmax(100 × score)`；100沿用冻结聚合尺度，不在六个测试集调参。

## 新增列

- `Entropy-Router`：逐样本选择类别分布熵最低的表达。
- `Margin-Router`：逐样本选择Top-1与Top-2概率差最大的表达。
- `Oracle`：使用真实标签形成的分析上限，不是真实方法。

Router决策不读取真实标签。真实标签只在决策完成后用于计算Hit@K、MRR、Oracle一致率及正负翻转。

## 输出

- `unlabeled_router_table.csv`：六种方法的Hit@1/3/5和MRR。
- `unlabeled_router_results.json`：选择比例、Oracle一致率、正负翻转和逐样本选择。
- `class_scores_float16.npz`：三种固定表达的完整类别分数，方便后续离线审计，避免再次运行音频编码。
