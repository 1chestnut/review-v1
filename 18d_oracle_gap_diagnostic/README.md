# 任务18D：18A–18C Oracle差距诊断

## 目的

在不重新运行CLAP/KGE的情况下，使用任务18A和18C保存的逐样本结果判断样本级关系选择是否仍有可实现空间。

## 口径

- `Oracle opportunity`：18A中Oracle关系的真实标签排名优于冻结iKnow的样本。
- `Top-R coverage`：18C选出的Consensus-Margin Top-R关系是否包含至少一个Oracle关系。
- `Recovery`：存在Oracle opportunity时，18C是否也把真实标签排名改善到优于冻结iKnow。
- `Harm`：18C是否把真实标签排名变得比冻结iKnow更差。
- Oracle使用真实标签，只是分析上限，不是可报告为实际方法的结果。

## 结果（%）

| Dataset | Oracle opportunity | Oracle relation in Top-1 | Oracle relation in Top-3 | Consensus correct on opportunity | CM Top-1 recovery | CM Top-3 recovery | CM Top-1 harm |
|---|---:|---:|---:|---:|---:|---:|---:|
| ESC-50 | 5.85 | 55.56 | 55.56 | 52.99 | 60.68 | 58.97 | 1.60 |
| UrbanSound8K | 13.09 | 26.07 | 27.65 | 24.58 | 37.53 | 36.22 | 4.78 |
| FSD50K | 24.80 | 31.89 | 35.83 | 24.99 | 46.79 | 44.07 | 10.31 |
| DCASE17-T4 | 28.40 | 34.45 | 38.66 | 25.21 | 53.78 | 43.70 | 8.83 |
| AudioSet | 26.13 | 25.69 | 32.02 | 15.81 | 43.57 | 42.06 | 10.07 |
| TUT2017 | 44.06 | 34.58 | 38.94 | 26.58 | 51.60 | 51.41 | 18.72 |

## 结论

1. 18A证明关系互补空间存在，尤其是FSD50K、DCASE、AudioSet和TUT2017。
2. 18C只找到其中一部分；复杂数据集上多数关系的共识类别在Oracle opportunity样本中仅约16%–27%正确。
3. Top-3相对Top-1覆盖提升很小，且恢复率没有提高，因此继续简单增大R没有依据。
4. 主要瓶颈是硬Top-1多数投票丢失关系给出的完整类别排序，并压制有价值的少数关系。
5. 最多再进行一次Ranked Consensus：让每种关系对Top-L类别按排名软投票；若不能稳定超过18C，则停止该方向。

## 文件

- `summary.csv`：六个数据集汇总。
- `summary.json`：机器可读汇总。
- `01_.../sample_diagnostic.csv`：逐样本诊断。
- 上述结果完全由任务18A/18C现有输出离线产生，未重新编码音频，也未使用额外GPU。
