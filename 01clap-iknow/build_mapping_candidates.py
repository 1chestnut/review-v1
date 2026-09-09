import difflib
import importlib.util
import json
import re
from pathlib import Path

from pykeen.triples import TriplesFactory

ROOT = Path('/data/zkx/zkx/review1/clap-iknow')


def tokens(text):
    return set(re.findall(r'[a-z0-9]+', text.lower()))


def candidate_score(label, entity):
    left, right = tokens(label), tokens(entity)
    overlap = len(left & right) / max(1, len(left | right))
    sequence = difflib.SequenceMatcher(None, label.lower(), entity.lower()).ratio()
    containment = 1.0 if label.lower() in entity.lower() or entity.lower() in label.lower() else 0.0
    return 0.50 * overlap + 0.35 * sequence + 0.15 * containment


factory = None
records = {}
for folder in sorted(ROOT.glob('0*')):
    spec = importlib.util.spec_from_file_location('mapping_' + folder.name, folder / 'iknow_runtime.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    data = module.load_dataset()
    if factory is None:
        factory = TriplesFactory.from_path(module.TRAIN_TRIPLES_PATH)
    entities = list(factory.entity_to_id)
    rows = []
    for label in data['kg_classes']:
        transformed = module.get_kg_entity(label)
        resolved = module.resolve_head_query(transformed, factory)
        exact = transformed in factory.entity_to_id
        valid = resolved in factory.entity_to_id
        if valid:
            method = 'exact_after_get_kg_entity' if exact else 'legacy_first_or_last_word_fallback'
            candidates = []
        else:
            method = 'unmapped'
            ranked = sorted(
                ((candidate_score(transformed, entity), entity) for entity in entities),
                reverse=True,
            )[:20]
            candidates = [{'entity': entity, 'lexical_score': round(score, 6)} for score, entity in ranked]
        rows.append({
            'dataset_label': label,
            'legacy_transformed': transformed,
            'legacy_resolved': resolved if valid else None,
            'legacy_method': method,
            'candidates': candidates,
        })
    records[folder.name] = rows

(ROOT / 'entity_mapping_v2_candidates.json').write_text(
    json.dumps(records, ensure_ascii=False, indent=2), encoding='utf-8'
)
print(json.dumps({name: {'classes': len(rows), 'unmapped': sum(r['legacy_method'] == 'unmapped' for r in rows)} for name, rows in records.items()}, indent=2))
