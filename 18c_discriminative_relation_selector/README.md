# Task 18C — Discriminative sample-level one-hop relation selection

最后一次有边界的自动关系选择验证。严格冻结Task05b/18A的一跳配置，仅改变无标签关系评分：Margin、Entropy、Consensus-Margin；Abs-Top3作为18B失败对照，Oracle只作上限。不加入AAKV、新融合、二跳或门控。

停止规则：如果同一个预先指定的选择器不能在多数数据集稳定超过Frozen-iKnow，则停止自动关系选择方向，不再根据各测试集分别挑选规则。
