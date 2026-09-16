# 第5节写作前证据图与待确认项

写作论点：在冻结CLAP、KGE、候选类别和统一评估器的条件下，检验AAKV、分层融合和样本级关系选择能否相对当前iKnow复现基线改善五个数据集的排序；结论须限定在当前数据与复现配置内。

## 段落顺序

1. 5.1 实验设置：数据角色、处理、候选类别、基线、公平配置、评价指标与参数确定方式。
2. 5.2 整体结果：先报完整方法相对CLAP/iKnow的Hit@1和MRR，再说明Hit@3/5并非处处提高。
3. 5.3 组件分析：三因素消融、关系选择对照、知识语言化对照。把单模块不稳定与组合互补写清楚。
4. 5.4 补充分析：成对统计、DCASE参数网格、可核对的案例。只报告有原始逐样本证据的分析。

## 已核实的来源

- 主表及消融：`任务清单/最终实验表格/FINAL_TABLES.md` 与 `final_experiment_package/01_main_table`、`02_ablation_table`。
- 参数网格：`final_experiment_package/05_parameter_table/results/selected_config.json`。
- Selector成对统计：`final_experiment_package/04_Selector_table/results/REPORT.md`。
- TUT运行数据源：`final_experiment_package/01_main_table/code/runtime/06_TUT2017/runtime.py` 第44–45、111–128行。

## 必须在定稿前解决的两处不一致

1. TUT2017被主表标为“final test”，但代码读取`development/meta.txt`，进度记录为4,680条。此前这批数据也用于探索。不能直接写作“独立官方测试集”。可选择重新跑官方evaluation集，或将其明确写为探索性/补充评估并从独立五测试主张中移除。
2. 表5写α由DCASE“按MRR选择”；`selected_config.json`写主指标先最大化Hit@1，同分再比较MRR，仍同分优先较小N_r。中文协议必须与实际选择规则一致，不能同时保留两种说法。

待作者确认上述范围后，再扩展完整中文结果段落；所有具体数字应从冻结CSV转写并再次核验。

