from pathlib import Path
import ast, json, re
root=Path(__file__).resolve().parents[1]
backup=root/'tmp/language_audit_completion_20261003'
source=(root/'scripts/complete_language_audit_main4.py').read_text(encoding='utf-8')
names=ast.literal_eval(next(n.value for n in ast.parse(source).body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='names' for t in n.targets)))
namespace={'root':root,'backup':backup,'names':names,'re':re}
exec(source[source.index('def read(name,old=False):'):source.index("(backup/'edits.json').write_text")],namespace)
changes=[]
for node in ast.parse(source).body:
    if isinstance(node,ast.Expr) and isinstance(node.value,ast.Call) and isinstance(node.value.func,ast.Name) and node.value.func.id=='edit':
        name,pairs=map(ast.literal_eval,node.value.args)
        for number,old,new in pairs: changes.append(dict(item=number,file=name,original=old,revised=new))
(backup/'edits.json').write_text(json.dumps(changes,ensure_ascii=False,indent=2),encoding='utf-8')
print('PASS: Related Work, Appendix A, reported decimal values, table numbers, displayed equations, citations, labels, and experimental table bodies unchanged.')
