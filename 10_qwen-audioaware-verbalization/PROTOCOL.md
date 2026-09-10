# 任务10：统一Qwen-AudioAware语言化

## 研究问题

在任务06完全相同的配置下，统一、自动的音频感知LLM语言化能否达到人工关系模板的性能？

## 三列结果

| 列 | 含义 |
|---|---|
| CLAP | 无KG证据 |
| Manual-Template | 任务06冻结的人工关系模板 |
| Qwen-AudioAware | Qwen统一生成、自动检查和修复；最终失败使用关系无关的统一格式 |

任务09的Qwen-General不进入本任务结果表。

## 相对任务09的唯一生成变化

- 每句必须包含明确音频语境；Qwen依据关系语义在 `the sound of {head}`、`the audio event {head}`、`the acoustic category {head}` 中选择合适句法，不强制统一硬前缀；
- head和tail尽量保持原字符串，不改为复数或同义词；
- 明确保持关系语义及方向；
- 同样禁止增加音高、音色、频率、场景、原因和外部事实；
- 首次失败后根据失败原因重写一次；
- 再失败不回退人工关系模板，而统一序列化为：
  `The audio event {head} has the relation {relation} with {tail}.`

## 冻结项

- 直接读取任务06已经保存的一跳三元组，不重新查询KG；
- 六集数据、标签、多标签评测口径、严格实体映射与关系集合；
- K=5、M=3、Top-P=5；
- CLAP、RotatE、尾实体过滤；
- logit scale=100、归一化LSE、动态alpha范围[0.4,0.8]；
- 仅一跳，不加入二跳、gamma、delta或门控。

## 公平性记录

每条三元组保存首次输出、检查失败原因、修复输出、最终文本和状态。每集汇总首次通过、修复通过、统一格式回退数量及比例。Qwen使用确定性解码 `do_sample=False`，文本离线生成并缓存。
