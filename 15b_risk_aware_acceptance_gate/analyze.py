import csv,json
from pathlib import Path
import numpy as np
from scipy.stats import binomtest

ROOT=Path('/data/zkx/zkx/review1');OUT=ROOT/'15b_risk_aware_acceptance_gate';OUT.mkdir(parents=True,exist_ok=True)
DATASETS=['01_ESC50','02_UrbanSound8K','03_FSD50K','04_DCASE17_T4','05_AudioSet','06_TUT2017']
METHODS=['D-1st','2nd-Full','Accept-Entropy','Accept-Margin','Accept-EntropyMargin','Accept-Consensus','Accept-RiskAware','Accept-Oracle']
def save(p,x):Path(p).write_text(json.dumps(x,ensure_ascii=False,indent=2),encoding='utf-8')
def prob(x):
 z=100*x;z-=z.max(1,keepdims=True);e=np.exp(z);return e/e.sum(1,keepdims=True)
def entropy(p):return -np.sum(p*np.log(np.clip(p,1e-12,1)),1)/np.log(p.shape[1])
def margin(x):s=np.sort(x,axis=1);return s[:,-1]-s[:,-2]
def ranks(scores,truth):
 order=np.argsort(-scores,axis=1,kind='stable');out=[]
 for i,t in enumerate(truth):out.append(min(int(np.where(order[i]==y)[0][0])+1 for y in t))
 return np.asarray(out)
all_summary=[]
for ds in DATASETS:
 z=np.load(ROOT/'14_aakv_mp_potential'/ds/'predictions.npz',allow_pickle=True);names=[str(x) for x in z['methods']];s=z['scores']
 rows=json.load(open(ROOT/'14_aakv_mp_potential'/ds/'samples.json'));truth=[r['true_indices'] for r in rows]
 first=s[:,names.index('1st-P5'),:];m1=s[:,names.index('AAKV-M1-P5'),:]
 m3=s[:,names.index('AAKV-M3-P5'),:];m5=s[:,names.index('AAKV-M5-P5'),:]
 p1=prob(first);p2=prob(m1);h1=entropy(p1);h2=entropy(p2);g1=margin(first);g2=margin(m1)
 top1=np.argmax(first,1);topm1=np.argmax(m1,1);topm3=np.argmax(m3,1);topm5=np.argmax(m5,1)
 rules={
  'D-1st':np.zeros(len(first),bool),'2nd-Full':np.ones(len(first),bool),
  'Accept-Entropy':h2<h1,'Accept-Margin':g2>g1,
  'Accept-EntropyMargin':(h2<h1)&(g2>g1),
  'Accept-Consensus':(topm1==topm3)&(topm1==topm5),
 }
 rules['Accept-RiskAware']=rules['Accept-EntropyMargin']&rules['Accept-Consensus']
 rfirst=ranks(first,truth);rfull=ranks(m1,truth);rules['Accept-Oracle']=rfull<rfirst
 method_scores=[];method_ranks=[]
 for name in METHODS:
  gate=rules[name];v=np.where(gate[:,None],m1,first);method_scores.append(v);method_ranks.append(ranks(v,truth))
 R=np.stack(method_ranks,1);metrics={};diagnostics={};hitfirst=rfirst==1;hitfull=rfull==1
 full_rescue=(~hitfirst)&hitfull;full_harm=hitfirst&(~hitfull)
 for j,name in enumerate(METHODS):
  r=R[:,j];hit=r==1;gate=rules[name]
  metrics[name]={'Hit@1':float(100*np.mean(r<=1)),'Hit@3':float(100*np.mean(r<=3)),'Hit@5':float(100*np.mean(r<=5)),'MRR':float(100*np.mean(1/r))}
  diagnostics[name]={'accept_n':int(gate.sum()),'accept_rate':float(gate.mean()),
   'wrong_to_right':int(np.sum((~hitfirst)&hit)),'right_to_wrong':int(np.sum(hitfirst&(~hit))),
   'full_rescue_retained':int(np.sum(full_rescue&hit)),'full_rescue_total':int(full_rescue.sum()),
   'rescue_retention':float(np.sum(full_rescue&hit)/max(1,full_rescue.sum())),
   'full_harm_avoided':int(np.sum(full_harm&hit)),'full_harm_total':int(full_harm.sum()),
   'harm_avoidance':float(np.sum(full_harm&hit)/max(1,full_harm.sum())),
   'rank_improved':int(np.sum(r<rfirst)),'rank_worsened':int(np.sum(r>rfirst))}
 comparisons=[];rawp=[];rng=np.random.default_rng(42)
 for j,name in enumerate(METHODS[1:],1):
  dh=100*((R[:,j]==1).astype(float)-(rfirst==1).astype(float));dr=100*(1/R[:,j]-1/rfirst)
  boot=np.empty((10000,2))
  for k in range(10000):
   ix=rng.integers(0,len(R),len(R));boot[k]=[dh[ix].mean(),dr[ix].mean()]
  gain=int(np.sum((rfirst>1)&(R[:,j]==1)));loss=int(np.sum((rfirst==1)&(R[:,j]>1)));p=float(binomtest(gain,gain+loss,.5).pvalue) if gain+loss else 1.
  comparisons.append({'method':name,'delta_Hit@1_pp':float(dh.mean()),'Hit@1_CI95':np.quantile(boot[:,0],[.025,.975]).tolist(),
   'delta_MRR_pp':float(dr.mean()),'MRR_CI95':np.quantile(boot[:,1],[.025,.975]).tolist(),'mcnemar_p':p});rawp.append(p)
 order=np.argsort(rawp);adj=np.zeros(len(rawp));last=0
 for k,j in enumerate(order):last=max(last,min(1,(len(rawp)-k)*rawp[j]));adj[j]=last
 for x,p in zip(comparisons,adj):x['holm_p']=float(p)
 folder=OUT/ds;folder.mkdir(exist_ok=True);save(folder/'metrics.json',metrics);save(folder/'gate_diagnostics.json',diagnostics);save(folder/'statistics.json',comparisons)
 np.savez_compressed(folder/'predictions.npz',ranks=R,methods=np.asarray(METHODS),
  accept=np.stack([rules[x] for x in METHODS],1),entropy_first=h1,entropy_second=h2,margin_first=g1,margin_second=g2,
  top_first=top1,top_m1=topm1,top_m3=topm3,top_m5=topm5)
 with (folder/'metrics.csv').open('w',newline='',encoding='utf-8') as f:
  w=csv.writer(f);w.writerow(['method','Hit@1','Hit@3','Hit@5','MRR','accept_rate','wrong_to_right','right_to_wrong','rescue_retention','harm_avoidance'])
  for name in METHODS:w.writerow([name]+[metrics[name][q] for q in ['Hit@1','Hit@3','Hit@5','MRR']]+[diagnostics[name][q] for q in ['accept_rate','wrong_to_right','right_to_wrong','rescue_retention','harm_avoidance']])
 best=max(METHODS[1:-1],key=lambda x:metrics[x]['MRR'])
 all_summary.append({'dataset':ds,'best_real_gate':best,'best_Hit@1':metrics[best]['Hit@1'],'best_MRR':metrics[best]['MRR'],
  'delta_Hit@1':metrics[best]['Hit@1']-metrics['D-1st']['Hit@1'],'delta_MRR':metrics[best]['MRR']-metrics['D-1st']['MRR'],
  'accept_rate':diagnostics[best]['accept_rate'],'oracle_delta_MRR':metrics['Accept-Oracle']['MRR']-metrics['D-1st']['MRR']})
save(OUT/'summary.json',all_summary)
save(OUT/'protocol.json',{'analysis_only':True,'fixed_second_hop':'AAKV M2=1 P=5 gamma=0.85','no_new_inference':True,
 'risk_rule':'accept iff second-hop entropy decreases, margin increases, and M2={1,3,5} Top-1 predictions agree',
 'oracle':'accept iff fixed second hop improves true-label rank; post-hoc upper bound only',
 'efficiency_warning':'post-retrieval acceptance rules do not save second-hop computation'})
print(json.dumps(all_summary,indent=2))
