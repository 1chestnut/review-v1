# 任务06：严格映射下的一跳文本表达审计

## 前置条件

仅在任务05b六集全部成功完成后自动启动。任务06读取与05b相同的 `entity_mapping_v2.json`；未映射类别不扩展，不使用首词/尾词回退。

## 固定项

- 一跳；K=5，M=3。
- 关系集合、三元组、尾实体过滤、CLAP、RotatE和数据完全相同。
- Ours三列均采用相同的先聚合再动态alpha融合，内部Top-P=5。
- 不使用二跳、gamma、delta、门控或LLM。

## 列定义

| 列 | 唯一差异 |
|---|---|
| CLAP | 无KG |
| iKnow-1st | 严格映射的一跳Direct文本与联合NormLSE100 |
| Ours1-Direct | `class_name, tail` |
| Ours1-RawTriple | `class_name relation tail` |
| Ours1-Template | 按旧模板措辞重建的确定性关系句 |
| Ours1-Oracle | 逐样本取前三种Ours文本中真实标签最佳排名，仅作上限分析 |

Oracle不参与推理选择，不可作为真实方法报告。它只判断三种表达是否具有值得开发无标签路由器的互补空间。
