# Task 18B — Label-free sample-level one-hop relation selection

本任务只验证：在冻结Task05b的一跳iKnow基础上，能否依据当前音频与一跳证据文本的CLAP相似度，为每条样本自动选择关系。

固定：数据、CLAP、RotatE、严格映射、K=5、M=3、`class_name, tail`、scale=100归一化联合LSE、任务12确定性音频协议。禁止真实标签参与选择；不使用AAKV、新融合、二跳和门控。

方法：Frozen-iKnow、All-47、Abs-Top1/3、Gain-Top1/3和分析用Oracle。Absolute按Top-K候选类别上的证据相似度选择；Gain按证据相对原类别分数的增量选择。Oracle只标明18A上限。

本轮是方向筛选，不是最终主表；Top1/Top3同时报告，不能看测试结果后为每个数据集采用不同R。
