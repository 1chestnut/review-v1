import importlib.util
import json
from pathlib import Path
from pykeen.triples import TriplesFactory

ROOT=Path('/data/zkx/zkx/review1/clap-iknow-strict-map-v2')
mapping=json.loads((ROOT/'entity_mapping_v2.json').read_text())
report={}
factory=None
for folder in sorted(ROOT.glob('0*')):
    cfg=json.loads((folder/'config.json').read_text())
    spec=importlib.util.spec_from_file_location('strict_'+folder.name,folder/'iknow_runtime.py')
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    data=module.load_dataset()
    if factory is None:factory=TriplesFactory.from_path(module.TRAIN_TRIPLES_PATH)
    table=mapping[cfg['dataset']]
    labels=[str(x) for x in data['label_classes']]
    missing_keys=[x for x in labels if x not in table]
    invalid_entities=[(x,table[x]['entity']) for x in labels if x in table and table[x]['entity'] and table[x]['entity'] not in factory.entity_to_id]
    mapped=sum(bool(table[x]['entity']) for x in labels if x in table)
    report[folder.name]={'classes':len(labels),'mapped':mapped,'unmapped':len(labels)-mapped,'missing_mapping_rows':missing_keys,'mapped_entities_absent_from_AKG':invalid_entities}
    print(folder.name, json.dumps(report[folder.name], ensure_ascii=False), flush=True)
    assert not missing_keys and not invalid_entities
(ROOT/'strict_mapping_preflight.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
print(json.dumps(report,ensure_ascii=False,indent=2))
