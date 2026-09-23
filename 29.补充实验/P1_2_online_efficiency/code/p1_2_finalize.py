#!/usr/bin/env python3
"""Create a reviewable LaTeX section and protocol note after the serial run."""
import csv
import json
import os
from pathlib import Path

root=Path(os.environ['P1_2_TASK_ROOT'])
with (root/'efficiency_manuscript_summary.csv').open(encoding='utf-8-sig',newline='') as f:
    rows=list(csv.DictReader(f))
if len(rows)!=6:raise RuntimeError('Expected six method/batch summary rows')
lookup={(int(r['batch_size']),r['method']):r for r in rows}
for batch in (1,32):
    for method in ('CLAP','iKnow_dagger','SAKI'):
        if (batch,method) not in lookup:raise RuntimeError('Missing summary cell')

def f(batch,method,key):return float(lookup[(batch,method)][key])
lines=[]
lines.append(r'\subsubsection{Efficiency analysis}\label{sec:efficiency}')
lines.append(r'\begin{CJK*}{UTF8}{gbsn}')
lines.append('为评估样本级关系选择带来的计算开销，本文比较CLAP、iKnow\\textsuperscript{\\dag}和SAKI的在线推理效率。所有方法在相同型号的GPU上使用相同的测试样本，分别以batch size为1和32进行测量；每个数据集固定抽取200条样本，预热20条后重复计时5次。AAKV文本生成、知识图谱尾实体检索以及知识文本特征缓存均属于离线预处理，不计入在线推理时间。表~\\ref{tab:efficiency}报告五个测试集的等权平均结果。')
lines.extend([r'\end{CJK*}',r'\begin{table*}[!t]',r'\centering',
    r'\caption{五个测试集上的在线推理效率。每个数据集固定抽取200条样本，预热20条并重复测量5次；相对开销以相同batch size下的CLAP延迟为基准。峰值显存包含模型和在线计算，离线缓存仅计预计算的文本特征及证据索引。}',
    r'\label{tab:efficiency}',r'\footnotesize',r'\setlength{\tabcolsep}{5pt}',
    r'\begin{tabular}{c l r r r r r}',r'\toprule',
    r'Batch size & Method & Latency (ms/sample) & Relative overhead & Throughput (samples/s) & Peak GPU memory (MiB) & Offline cache (MiB) \\',r'\midrule'])
for batch in (1,32):
    if batch==32:lines.append(r'\midrule')
    for method,label in (('CLAP','CLAP'),('iKnow_dagger',r'iKnow\textsuperscript{\dag}'),('SAKI','SAKI')):
        values=[f(batch,method,k) for k in ('online_latency_ms_per_sample','relative_overhead_x','throughput_samples_per_s','peak_gpu_memory_mib','offline_cache_mib')]
        lines.append(f'{batch} & {label} & {values[0]:.2f} & {values[1]:.2f}$\\times$ & {values[2]:.2f} & {values[3]:.2f} & {values[4]:.2f} '+r'\\')
lines.extend([r'\bottomrule',r'\end{tabular}',r'\end{table*}',r'\begin{CJK*}{UTF8}{gbsn}'])
lines.append(f'在batch size为1时，SAKI的平均单样本延迟为{f(1,"SAKI","online_latency_ms_per_sample"):.2f} ms，是CLAP的{f(1,"SAKI","relative_overhead_x"):.2f}倍；batch size为32时，两者分别为{f(32,"SAKI","online_latency_ms_per_sample"):.2f} ms和{f(32,"CLAP","online_latency_ms_per_sample"):.2f} ms，相对开销增至{f(32,"SAKI","relative_overhead_x"):.2f}倍。SAKI的离线缓存规模高于两种对照方法，但其平均峰值GPU显存增量相对有限。该结果表明，在当前实现中，样本级关系评估与知识融合增加了在线计算，且尚未充分利用批处理提高吞吐量。')
lines.append(r'\end{CJK*}')
(root/'efficiency_section.tex').write_text('\n\n'.join(lines)+'\n',encoding='utf-8')

protocols=[]
for dataset in ('ESC-50','UrbanSound8K','FSD50K','AudioSet','TUT2017'):
    p=json.loads((root/dataset/'protocol.json').read_text(encoding='utf-8'))
    if len(p['sample_manifest_positions'])!=200:raise RuntimeError(dataset+' sample count')
    protocols.append((dataset,p['final_manifest'],p['final_manifest_sha256']))
text=['# P1-2 serial online efficiency profile','',
      'Five datasets were run serially on physical GPU 0 (NVIDIA GeForce RTX 4090 D).',
      'Each dataset uses 200 evenly spaced samples from its final manifest, 20 model-warm-up samples, 5 timed repeats, and batch sizes 1 and 32.',
      'The TUT2017 sample frame is the final 6300-record rerun, not the earlier 4680-record set.',
      'All selected audio files were read once before timing to reduce order-dependent cold file-cache effects.',
      'Timed latency includes live audio preprocessing/CLAP audio encoding and method-specific scoring/ranking.',
      'Offline AAKV generation, RotatE retrieval, and CLAP text-feature/cache construction are excluded.',
      'Offline cache size comprises precomputed label/evidence text embeddings and evidence-index mapping only; it excludes model weights and raw audio.',
      'The manuscript summary gives dataset-equal macro means. Relative overhead is the latency ratio against CLAP at the same batch size. Throughput is 1000 divided by macro-mean latency (ms/sample).',
      '', '## Final manifests','']
for ds,path,sha in protocols:text.append(f'- {ds}: `{path}`; SHA-256 `{sha}`')
text.extend(['','## Artifacts','',
             '- `efficiency_by_dataset.csv`: all five datasets × two batch sizes × three methods.',
             '- `efficiency_manuscript_summary.csv`: six macro-summary rows.',
             '- `efficiency_section.tex`: proposed LaTeX text/table, requiring manuscript-layout review before insertion.',
             '- Dataset folders: five-repeat timings, per-dataset summary, exact protocol, and completion marker.'])
(root/'README.md').write_text('\n'.join(text)+'\n',encoding='utf-8')
print('Serial efficiency artifacts complete:',root)
