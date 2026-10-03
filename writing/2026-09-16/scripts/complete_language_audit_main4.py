"""Apply the authorized remaining language edits; protect scientific records."""
from pathlib import Path
import shutil, re, json, hashlib

root = Path(__file__).resolve().parents[1]
backup = root / 'tmp' / 'language_audit_completion_20261003'
backup.mkdir(parents=True, exist_ok=True)
names = ['main-4.tex', 'sections/01_introduction_main4.tex', 'sections/02_related_work_main4.tex', 'sections/03_method_main4.tex', 'sections/04_experiments_main4.tex', 'sections/06_conclusion_main4.tex', 'sections/07_appendix_main4.tex', 'main-4.pdf', 'translation_prep/terminology_lock_main4.md']
for name in names:
    destination = backup / name
    destination.parent.mkdir(parents=True, exist_ok=True)
    if destination.exists(): raise RuntimeError('Backup already exists; do not reapply edits')
    shutil.copy2(root / name, destination)
changes=[]
def edit(name, pairs):
    path=root/name
    text=path.read_text(encoding='utf-8-sig')
    for number,old,new in pairs:
        if text.count(old)!=1: raise ValueError((number,name,text.count(old),old))
        if '&' in old and '&' in new:
            before, after = old.split(' & '), new.split(' & ')
            replacement = ' & '.join(a if a == b else r'\redrevision{'+b+'}' for a,b in zip(before,after))
        else:
            replacement = r'\redrevision{'+new+'}'
        text=text.replace(old, replacement)
        changes.append(dict(item=number,file=name,original=old,revised=new))
    path.write_text(text,encoding='utf-8')

edit('main-4.tex',[
 (1,"Knowledge graphs can add semantics absent from short class names, but knowledge related to a class may not help distinguish it in the current audio.","Knowledge graphs can supply semantic information absent from short class names. However, knowledge associated with a class may have limited value for distinguishing that class in a given audio sample."),
 (2,"Moreover, prompts that concatenate class names with retrieved tail entities omit the relations connecting them, leaving part of the graph's meaning unexpressed.","Prompts formed by concatenating class names with retrieved tail entities leave the connecting relations implicit, expressing only part of the retrieved graph information."),
 (3,"SAKI then selects relations using class predictions obtained separately from each relation's evidence.","SAKI then selects relations using class predictions computed separately for each relation from its evidence and the original CLAP scores."),
 (4,"These results indicate that selecting relations for individual audio samples, preserving their meaning in text, and combining their evidence with the original CLAP prediction can improve the use of structured knowledge in zero-shot audio classification.","These results support adapting graph evidence to individual audio samples through relation selection, constrained verbalization, and score fusion for zero-shot audio classification."),
])
edit('sections/01_introduction_main4.tex',[
 (5,"PAT uses downstream-task audio to weight and ensemble prompts, and aligns audio and text representations~\\cite{seth2025pat}.","PAT uses audio from the downstream task to assign weights to prompts and combine them. It also aligns audio and text representations~\\cite{seth2025pat}."),
 (6,"Further use of this knowledge requires considering its discriminative value for the current audio.","Using this knowledge for a given audio sample also requires assessing its discriminative value for that sample."),
 (7,"Weakly related knowledge may also affect class rankings.","Knowledge weakly related to the input audio may also alter candidate class rankings."),
 (8,"This separates evidence aggregation from control over its contribution to the final class ranking.","This separates evidence aggregation from the weighting of knowledge evidence in the final class scores."),
])
edit('sections/03_method_main4.tex',[
 (19,"It also requires the original entity wording, relation meaning and direction, and tail entity to be retained without adding information beyond the triple.","It requires preserving the supplied head and tail wording, together with the relation's meaning and direction. No information beyond the triple may be added."),
 (23,r'\greenrevision{At final scoring, Eq.~\eqref{eq:unified-fusion} combines the merged evidence sequence with the original CLAP score, rather than with a relation-specific score:}',r'At the final scoring stage, Eq.~\eqref{eq:unified-fusion} combines the aggregated knowledge score with the original CLAP score:'),
 ('notation',"Retained tails and evidence scores for a class--relation pair","Retained tail entity set and evidence score sequence for a class--relation pair"),
 ('notation',"Evidence scores after merging selected relations and removing duplicate tails","Merged evidence score sequence after tail deduplication"),
])
edit('sections/04_experiments_main4.tex',[
 (28,r'Under our common evaluation protocol, iKnow\textsuperscript{\dag} supports the value of class-related knowledge, while SAKI provides further gains.',r'Under the common evaluation protocol, the results for iKnow\textsuperscript{\dag} support the value of class-related knowledge. SAKI achieves further gains over iKnow\textsuperscript{\dag}.'),
 (29,"The difference chiefly involved a small numerical increase in MRR, with nearly unchanged top-1 accuracy.","Adding Hierarchical Fusion slightly increased MRR, while Hit@1 remained nearly unchanged."),
 (30,"Random Top-5 also varied the relation set across audio samples, yet its mean Hit@1 and MRR were lower by 2.06 and 0.95 percentage points.","Random Top-5 also varied relation sets across samples. Its mean Hit@1 and MRR were 2.06 and 0.95 percentage points lower than those of SAKI."),
 (31,r'with the dominant set accounting for only 1.06\%--1.53\% of samples.',r'with the most frequent set accounting for 1.06\%--1.53\% of samples.'),
 (32,"AAKV therefore improved Hit@1 consistently across datasets, with larger ranking gains on FSD50K and TUT2017 and comparable performance between the two representations on ESC-50.","AAKV improved Hit@1 over both controls on all five datasets, with larger gains over Direct concatenation on FSD50K and TUT2017. On ESC-50, its MRR was comparable to that of Raw triple."),
 (33,r'We examine whether sampling uncertainty analysis supports the metric gains of SAKI over iKnow\textsuperscript{\dag}.',r'We assess uncertainty in the Hit@1 and MRR gains of SAKI over iKnow\textsuperscript{\dag} using paired bootstrap confidence intervals.'),
 (34,r'Corrections from iKnow\textsuperscript{\dag} to SAKI outnumbered reverse transitions on all five datasets, yielding a net improvement in top-1 accuracy.',r'Transitions from incorrect iKnow\textsuperscript{\dag} predictions to correct SAKI predictions outnumbered the reverse transitions on all five datasets. The difference yielded a net improvement in top-1 accuracy.'),
 (36,"The benefit of adding relations was therefore nonmonotonic within the tested range. MRR further distinguished configurations with the same top-1 accuracy.","The benefit of adding relations was therefore nonmonotonic within the tested range."),
 (37,"For each dataset, we selected 200 fixed samples, warmed up with 20 samples, and repeated timing five times at batch size one.","For each dataset, we selected 200 fixed samples and processed 20 samples for warm-up. We then repeated timing five times at batch size one."),
 (38,"Compared with the latency ratio, peak memory increased modestly, whereas cache size increased substantially.","Relative to CLAP, SAKI showed a smaller proportional increase in peak GPU memory usage than in latency, while its cache size increased substantially."),
 ('verbatim',"The sentences are examples of \\greenrevision{cached evidence for candidate classes} read during inference.","The cached evidence texts are reproduced verbatim and provide examples of evidence read for candidate classes during inference."),
])
edit('sections/06_conclusion_main4.tex',[
 (39,"These findings support jointly considering sample relevance, text representation, and score fusion when incorporating structured knowledge into pretrained audio--language models under the evaluated settings.","Under the evaluated settings, these findings support coordinating sample relevance, text representation, and score fusion when incorporating structured knowledge into pretrained audio--language models."),
])
edit('sections/07_appendix_main4.tex',[
 ('aggregation',"LogSumExp over base and knowledge-enhanced scores","Log-sum-exp over original CLAP and knowledge-augmented prompt scores"),
 ('jaccard',"Mean Jaccard vs FrozenRq",r'\shortstack{Mean Jaccard similarity\\with FrozenRq}'),
 ('transition',r'Rescued denotes iKnow\textsuperscript{\dag} incorrect and SAKI correct; harmed denotes the reverse.',r'Incorrect $\to$ correct denotes an incorrect iKnow\textsuperscript{\dag} prediction and a correct SAKI prediction; correct $\to$ incorrect denotes the reverse.'),
 ('transition',r'Dataset & $n$ & Rescued & Harmed & $p_{\mathrm{exact}}$ & $p_{\mathrm{Holm}}$',r'Dataset & $n$ & \shortstack{Incorrect\\$\to$ correct} & \shortstack{Correct\\$\to$ incorrect} & $p_{\mathrm{exact}}$ & $p_{\mathrm{Holm}}$'),
])

# Update the working terminology policy, not historical evidence records.
p=root/'translation_prep/terminology_lock_main4.md'
t=p.read_text(encoding='utf-8-sig')
note='''\n## 2026-10-03 作者确认后的术语修订（优先于下方历史条目）\n\n- 不再将本文逐关系评分分支命名为 `relation-specific predictor`。正文采用动作句：`For each relation, we compute class scores ...`；其结果称 `class predictions computed separately for each relation`。图中短标签为 `Predictions for 47 relations`。共享冻结的 CLAP，不增加或训练独立模型。\n- 保留 `relation-specific class score`、`top-1 prediction`、`top-two score gap`，三者分别指分数、预测类别和前两名分数差。\n- `CLAP` 是 `knowledge-free baseline`；`iKnow†` 是 `knowledge-enhanced baseline`。结果段优先直接写比较方法名，不使用无明确指代的 baseline。\n- 介绍 iKnow-audio 原文时允许并保留其 `enriched prompts` 和 `curated subset of informative relations`；不为词汇统一改写已经核实的原文用语。\n- 附录 A、缓存文本逐字记录、文献原题不适用一般语言改写；以下旧进度说明是历史记录，不代表当前完成状态。\n'''
t=t.replace('\n## 全文执行规则',note+'\n## 全文执行规则',1)
p.write_text(t,encoding='utf-8')

def read(name,old=False): return ((backup if old else root)/name).read_text(encoding='utf-8-sig')
def unwrap(text):
    # Scoped color commands are formatting, not scientific content.
    for command in ['redrevision','greenrevision','methodrevision','purplerevision','nextrevision']:
        prefix='\\'+command+'{'
        while prefix in text:
            start=text.index(prefix); a=start+len(prefix); depth=1; b=a
            while depth:
                if text[b]=='{': depth+=1
                elif text[b]=='}': depth-=1
                b+=1
            text=text[:start]+text[a:b-1]+text[b:]
    return text
rw='sections/02_related_work_main4.tex'
assert read(rw)==read(rw,True),'Related Work must remain unchanged'
ap='sections/07_appendix_main4.tex'
assert read(ap).split(r'\section{Controlled reimplementation')[0]==read(ap,True).split(r'\section{Controlled reimplementation')[0],'Appendix A must remain verbatim'
for name in names:
    if not name.endswith('.tex'): continue
    old,new=unwrap(read(name,True)),unwrap(read(name))
    for pattern in [r'\\begin\{equation\}.*?\\end\{equation\}',r'^\\\[\s*$.*?^\\\]\s*$',r'\\cite\{[^}]*\}',r'\\label\{[^}]*\}']:
        assert re.findall(pattern,old,re.S|re.M)==re.findall(pattern,new,re.S|re.M),(name,pattern)
    # Dataset names (ESC-50) and repeated indicator names (Hit@1) can recur
    # differently after sentence edits; check reported values, not those labels.
    for pattern in [r'\d+\.\d+|\d{1,3}(?:,\d{3})+']:
        assert re.findall(pattern,old)==re.findall(pattern,new),(name,'numbers changed')
    old_tables=re.findall(r'\\begin\{tabular\}.*?\\end\{tabular\}',old,re.S)
    new_tables=re.findall(r'\\begin\{tabular\}.*?\\end\{tabular\}',new,re.S)
    assert [re.findall(r'\d+',t) for t in old_tables]==[re.findall(r'\d+',t) for t in new_tables],(name,'table numbers changed')
    if 'experiments' in name:
        assert re.findall(r'\\begin\{tabular\}.*?\\end\{tabular\}',old,re.S)==re.findall(r'\\begin\{tabular\}.*?\\end\{tabular\}',new,re.S),'Experimental table bodies changed'
(backup/'edits.json').write_text(json.dumps(changes,ensure_ascii=False,indent=2),encoding='utf-8')
print('Applied',len(changes),'language edits; scientific records and protected sections passed checks.')
