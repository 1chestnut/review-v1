# 12：同次音频编码的A/B/C/D与配对统计

固定任务06缓存中的一跳三元组及05b配置：K=5、M=3、逐数据集关系、严格映射、scale=100。文本来源为10-hard既有JSON，逐条核对head/relation/tail并保存输入快照和哈希。

| 方法 | 文本 | 聚合 |
|---|---|---|
| CLAP | 类别标签 | 原始匹配 |
| A | Direct | 联合NormLSE100，全证据 |
| B | Direct | Top-P=5，知识NormLSE100，再动态alpha |
| C | 10-hard AAKV | 联合NormLSE100，全证据 |
| D | 10-hard AAKV | Top-P=5，知识NormLSE100，再动态alpha |

alpha=clip(0.4+0.4*max(base),0.4,0.8)。B/D同时包含融合和Top-P，不能单独归因为某一项。

随机控制：master seed=42，每音频路径以SHA256导出固定seed；保留原CLAP随机裁剪实现，固定其结果，不改成中心裁剪。eval模式，torch确定性算法，禁用TF32与cuDNN benchmark。每音频嵌入只生成一次保存，各列共享；运行出错显式停止，不静默剔除样本。

统计：单种子冻结模型推理，不是多种子训练。以音频clip为配对单位，10000次有放回配对Bootstrap百分位95% CI，报告Hit@1、MRR差值以及D-B-C+A交互效应。D-A、B-A、C-A、D-B、D-C做双侧exact McNemar；每数据集5项Holm校正。区间基于clip独立假设，未核对源录音聚类，不能作为已排除相关性的证明；CI不衡量预训练模型或LLM生成随机性。

输出：各数据集metrics.csv/json，statistics.json，samples.json，predictions.npz完整类别分数和排序，audio_cache/，text_embeddings.pt，manifest.json，protocol.json，frozen_inputs/，progress.json。

任务05/06/10/11的旧点估计不混入本次配对统计。已有开发和测试探索历史须保留，统一重跑不消除历史选参影响。

三卡队列：GPU0 ESC→AudioSet；GPU1 US8K→TUT；GPU2 DCASE→FSD。环境使用/home/star/anaconda3/envs/zkx/bin/python。
