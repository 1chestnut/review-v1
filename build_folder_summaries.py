#!/usr/bin/env python3
import json
from pathlib import Path

BASE=Path('/data/zkx/zkx/review1')
DIRS={
 '01':(BASE/'01clap-iknow','clap_iknow_results.json'),
 '02':(BASE/'02clap-iknow-strict-map-v2','clap_iknow_results.json'),
 '03':(BASE/'03_full-second-hop-pilot','exploratory_results.json'),
 '04':(BASE/'04_iknow-km-reproduction-audit','km_audit_results.json'),
 '05':(BASE/'05_frozen-k5m3-strict-comparison','exploratory_results.json'),
}
NAMES={'01_ESC50':'ESC-50','02_UrbanSound8K':'UrbanSound8K','03_FSD50K':'FSD50K',
       '04_DCASE17_T4':'DCASE17-T4','05_AudioSet':'AudioSet','06_TUT2017':'TUT2017'}

def load(path):
 try:return json.loads(path.read_text())
 except:return None

def f(x):return f'{x:+.2f}'
def v(x):return f'{x:.2f}'

def onehop(tag,root,result_name):
 title='任务01：原版映射的一跳iKnow复现' if tag=='01' else '任务02：严格实体映射v2的一跳iKnow复现'
 lines=[f'# {title}','','## 本目录回答什么',
        '',('在历史冻结配置下重新得到CLAP与一跳iKnow结果，作为后续审计起点。' if tag=='01' else
            '只替换为严格、可审计的类别—KG实体映射，检查映射质量对一跳复现的影响。'),
        '','## 固定配置','',
        '- 深度：一跳；知识文本：`class_name, tail`直接拼接。',
        '- 聚合：原始类别分数与一跳证据的联合、证据数归一化LSE100。',
        '- Top-M=3；Top-K与逐数据集关系集合见各子目录`config.json`。',
        '- 本目录每次运行内部的`iKnow−CLAP`才是主要比较量。','',
        '## 结果汇总','',
        '| 数据集 | N | CLAP H@1 | iKnow H@1 | ΔH@1 | CLAP MRR | iKnow MRR | ΔMRR |',
        '|---|---:|---:|---:|---:|---:|---:|---:|']
 rows=[]
 for d in sorted(root.glob('[0-9][0-9]_*')):
  j=load(d/'results'/result_name)
  if not j or not j.get('completed'):continue
  a,b=j['metrics']['CLAP'],j['metrics']['iKnow'];n=j.get('evaluated_samples',len(j.get('samples',[])))
  rows.append((d.name,b['Hit@1']-a['Hit@1'],b['MRR']-a['MRR']))
  lines.append(f"| {NAMES[d.name]} | {n} | {v(a['Hit@1'])} | {v(b['Hit@1'])} | {f(b['Hit@1']-a['Hit@1'])} | {v(a['MRR'])} | {v(b['MRR'])} | {f(b['MRR']-a['MRR'])} |")
 lines+=['','## 当前结论','']
 if tag=='01':
  lines+=['- ESC、US8K、FSD50K、DCASE和TUT为正增益；AudioSet为负增益。',
          '- 该目录复现方向基本成立，但映射覆盖不足，不能作为最终冻结版。']
 else:
  lines+=['- 严格映射使ESC、US8K和DCASE的一跳增益更清楚，AudioSet下降缩小但仍略低于CLAP。',
          '- 严格映射提高语义可审计性，总体优于01原映射，但仍不能完全重现论文增益幅度。',
          '- 本目录只检查映射，不证明关系集合或K/M最优。']
 lines+=['','## 结果文件','',f'- 每集完整JSON：`<dataset>/results/{result_name}`',
         '- 每集简表：`<dataset>/results/clap_iknow_table.csv`']
 return '\n'.join(lines)+'\n'

def mechanisms(tag,root,result_name):
 frozen=tag=='05'
 title='任务05：严格映射、统一K5M3的一跳—全量二跳冻结比较' if frozen else '任务03：原版映射配置下的全量二跳潜力探索'
 lines=[f'# {title}','','## 本目录回答什么','',
        ('在严格映射、统一K=5/M=3以及任务01关系集合下，重新冻结一跳iKnow并检查新融合和全量二跳。' if frozen else
         '先判断新一跳融合组合及完整全量二跳是否有潜力，不作为最终参数选择或正式效率结论。'),
        '','## 四列及相邻比较','',
        '| 列 | 相对前一列的变化 | 比较含义 |','|---|---|---|',
        '| CLAP | 无知识 | 原始零样本基线 |',
        '| iKnow-1st | 加入一跳KG与联合NormLSE100 | `iKnow-1st−CLAP`：一跳知识是否有效 |',
        '| Ours-1st | 改为先聚合、再动态α融合，并使用Top-P=5 | `Ours-1st−iKnow-1st`：新融合组合是否有潜力 |',
        '| 2nd-Full | 加入全部可用二跳证据并乘γ=0.85 | `2nd-Full−Ours-1st`：完整全量二跳组合是否有潜力 |','',
        '## 结果汇总','',
        '| 数据集 | N | iKnow−CLAP ΔH@1/ΔMRR | Ours1−iKnow ΔH@1/ΔMRR | Full2−Ours1 ΔH@1/ΔMRR |',
        '|---|---:|---:|---:|---:|']
 completed=0;d_full=[];d_formula=[]
 for d in sorted(root.glob('[0-9][0-9]_*')):
  j=load(d/'results'/result_name)
  if not j or not j.get('completed'):
   st=load(d/'run_status.json') or {};lines.append(f"| {NAMES[d.name]} | — | {st.get('state','等待')} | — | — |")
   continue
  completed+=1;m=j['metrics'];n=j.get('evaluated_samples') or j.get('run_audit',{}).get('evaluated')
  g1=(m['iKnow-1st']['Hit@1']-m['CLAP']['Hit@1'],m['iKnow-1st']['MRR']-m['CLAP']['MRR'])
  g2=(m['Ours-1st']['Hit@1']-m['iKnow-1st']['Hit@1'],m['Ours-1st']['MRR']-m['iKnow-1st']['MRR'])
  g3=(m['2nd-Full']['Hit@1']-m['Ours-1st']['Hit@1'],m['2nd-Full']['MRR']-m['Ours-1st']['MRR'])
  d_formula.append(g2);d_full.append(g3)
  lines.append(f"| {NAMES[d.name]} | {n} | {f(g1[0])}/{f(g1[1])} | {f(g2[0])}/{f(g2[1])} | {f(g3[0])}/{f(g3[1])} |")
 lines+=['','## 当前结论','']
 if completed<6:lines.append(f'- 当前完成{completed}/6个数据集；以下结论等待自动更新，不能作为最终结论。')
 else:
  pos_formula=sum(x[0]>0 for x in d_formula);pos_full=sum(x[0]>0.05 for x in d_full)
  lines.append(f'- 新融合组合在{pos_formula}/6个数据集取得正Hit@1变化。')
  lines.append(f'- 全量二跳在{pos_full}/6个数据集取得超过0.05个百分点的Hit@1增益；其余为近零或下降。')
  lines.append(f"- 全量二跳六集宏平均变化：ΔHit@1={f(sum(x[0] for x in d_full)/6)}，ΔMRR={f(sum(x[1] for x in d_full)/6)}。")
  lines.append('- 本比较支持的是完整二跳组合，不把差值单独归因于二跳深度或γ=0.85。')
 lines+=['','## 配置与结果文件','',
         '- 详细列定义：`COLUMN_COMPARISON.md`（任务03）或`PROTOCOL.md`（任务05）。',
         f'- 每集完整JSON：`<dataset>/results/{result_name}`',
         '- 共享缓存runner的wall time不作为正式效率结论。']
 return '\n'.join(lines)+'\n'

def km(root,result_name):
 lines=['# 任务04：iKnow一跳K/M复现配置审计','','## 本目录回答什么','',
        '固定任务01原版映射、关系集合、直接拼接与一跳NormLSE，只枚举`K={5,10,15}`、`M={1,3,5}`，补查原文未公开的实现配置。','',
        '## 统一K5M3与每集最佳配置','',
        '| 数据集 | K5M3 ΔH@1/ΔMRR | 本集最高Hit@1配置 | 最高ΔH@1 | 判断 |','|---|---:|---|---:|---|']
 for d in sorted(root.glob('[0-9][0-9]_*')):
  j=load(d/'results'/result_name)
  if not j or not j.get('completed'):continue
  gains=j['gains_over_clap'];base=j['metrics']['CLAP'];key='iKnow-K5-M3';g=gains[key]
  best=max(gains,key=lambda k:gains[k]['Hit@1'])
  judgment='K5M3为最高' if best==key else f'最高为{best.replace("iKnow-","")}'
  lines.append(f"| {NAMES[d.name]} | {f(g['Hit@1'])}/{f(g['MRR'])} | {best.replace('iKnow-','')} | {f(gains[best]['Hit@1'])} | {judgment} |")
 lines+=['','## 结论','',
         '- 统一K=5、M=3在六集均为正增益，并在ESC、FSD、DCASE和TUT达到最高或最稳结果。',
         '- US8K以K5M1略高，但K5M3仍稳定为正；AudioSet的K5M3轻微为正，而历史K15M3为负。',
         '- 因此K5M3是当前最稳、成本更低的复现冻结候选。该结论属于已暴露数据上的复现校准，不是独立验证集选参。',
         '- 本任务没有枚举关系集合，不能证明现有关系集合最优。','',
         '## 完整结果','',
         '- 每集九组表：`<dataset>/results/km_audit_table.csv`',
         '- 每集逐样本JSON：`<dataset>/results/km_audit_results.json`']
 return '\n'.join(lines)+'\n'

def main():
 for tag,(root,result) in DIRS.items():
  if not root.exists():continue
  if tag in ('01','02'):text=onehop(tag,root,result)
  elif tag in ('03','05'):text=mechanisms(tag,root,result)
  else:text=km(root,result)
  (root/'README_SUMMARY.md').write_text(text,encoding='utf-8')
  print(tag,root/'README_SUMMARY.md')
if __name__=='__main__':main()
