#!/usr/bin/env python3
"""Aggregate completed P1-2 profiles into dataset and manuscript tables."""
import csv
import json
import os
from pathlib import Path
from statistics import mean

ROOT=Path(os.environ.get('P1_2_TASK_ROOT',str(Path(__file__).resolve().parent/'P1_2_online_efficiency')))
DATASETS=('ESC-50','UrbanSound8K','FSD50K','AudioSet','TUT2017')
METHODS=('CLAP','iKnow_dagger','SAKI')
records=[]
for dataset in DATASETS:
    with (ROOT/dataset/'timing_summary.csv').open(encoding='utf-8-sig',newline='') as f:
        rows=list(csv.DictReader(f))
    with (ROOT/dataset/'protocol.json').open(encoding='utf-8') as f:
        protocol=json.load(f)
    if len(rows)!=6 or len(protocol['sample_manifest_positions'])!=200:
        raise RuntimeError(f'{dataset}: incomplete profile')
    for row in rows:
        if int(row['n_profiled'])!=200 or int(row['repeats'])!=5:
            raise RuntimeError(f'{dataset}: unexpected sample/repeat count')
        records.append(row)

detail=[]
for dataset in DATASETS:
    for bs in (1,32):
        baseline=next(r for r in records if r['dataset']==dataset and r['method']=='CLAP' and int(r['batch_size'])==bs)
        base_latency=float(baseline['end_to_end_ms_per_sample_mean'])
        for method in METHODS:
            r=next(x for x in records if x['dataset']==dataset and x['method']==method and int(x['batch_size'])==bs)
            latency=float(r['end_to_end_ms_per_sample_mean'])
            detail.append({'dataset':dataset,'batch_size':bs,'method':method,'n_samples':200,'repeats':5,
                'online_latency_ms_per_sample':latency,'relative_overhead_x':latency/base_latency,
                'throughput_samples_per_s':float(r['throughput_samples_per_s_mean']),
                'peak_gpu_memory_mib':float(r['peak_gpu_mib_mean']),
                'offline_cache_mib':float(r['offline_cache_mib_mean'])})

def write(path,rows):
    with path.open('w',encoding='utf-8-sig',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=list(rows[0]));writer.writeheader();writer.writerows(rows)
write(ROOT/'efficiency_by_dataset.csv',detail)

main=[]
for bs in (1,32):
    base_latency=mean(r['online_latency_ms_per_sample'] for r in detail if r['batch_size']==bs and r['method']=='CLAP')
    for method in METHODS:
        rs=[r for r in detail if r['batch_size']==bs and r['method']==method]
        latency=mean(r['online_latency_ms_per_sample'] for r in rs)
        main.append({'batch_size':bs,'method':method,'datasets':5,'samples_per_dataset':200,'repeats':5,
            'online_latency_ms_per_sample':latency,'relative_overhead_x':latency/base_latency,
            'throughput_samples_per_s':1000/latency,
            'peak_gpu_memory_mib':mean(r['peak_gpu_memory_mib'] for r in rs),
            'offline_cache_mib':mean(r['offline_cache_mib'] for r in rs)})
write(ROOT/'efficiency_manuscript_summary.csv',main)
print((ROOT/'efficiency_manuscript_summary.csv').read_text(encoding='utf-8-sig'))
