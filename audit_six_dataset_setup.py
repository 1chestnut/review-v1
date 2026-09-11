#!/usr/bin/env python3
import importlib.util, json, statistics
from pathlib import Path
import soundfile as sf

ROOT=Path('/data/zkx/zkx/review1/12_shared-abcd-statistics')
DATASETS=['01_ESC50','02_UrbanSound8K','03_FSD50K','04_DCASE17_T4','05_AudioSet','06_TUT2017']
out={}
for ds in DATASETS:
 p=ROOT/ds/'frozen_inputs'/'runtime.py';spec=importlib.util.spec_from_file_location('rt_'+ds,p);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
 data=m.load_dataset();samples=list(m.iter_samples(data));dur=[];sr=[];missing=[]
 for x in samples:
  try:
   info=sf.info(x['audio_path']);dur.append(info.frames/info.samplerate);sr.append(info.samplerate)
  except Exception as e:missing.append({'path':x['audio_path'],'error':str(e)})
 labels=[len(x['true_indices']) for x in samples]
 rec={'samples':len(samples),'classes':len(data['label_classes']),'single_label_samples':sum(n==1 for n in labels),'multi_label_samples':sum(n>1 for n in labels),'zero_mapped_label_samples':sum(n==0 for n in labels),'audio_readable':len(dur),'audio_unreadable':len(missing),'sample_rates':sorted(set(sr))}
 if dur:rec['duration_seconds']={'min':min(dur),'median':statistics.median(dur),'mean':statistics.fmean(dur),'max':max(dur),'total_hours':sum(dur)/3600}
 if 'df' in data:rec['metadata_columns']=list(data['df'].columns)
 out[ds]=rec
payload=json.dumps(out,ensure_ascii=False,indent=2)
Path('/data/zkx/zkx/review1/six_dataset_audit.json').write_text(payload,encoding='utf-8')
print(payload)
