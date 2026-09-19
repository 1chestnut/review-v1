#!/usr/bin/env python3
"""Audit TUT2017 dev+eval and extend the deterministic CLAP cache to 6,300 clips."""
import hashlib
import importlib.util
import json
import os
import random
import shutil
from collections import Counter
from pathlib import Path

import numpy as np
import torch
import torch.nn.functional as F
from tqdm import tqdm

ROOT = Path('/data/zkx/zkx/review1')
TASK = ROOT / '28_TUT2017_full6300_rerun'
OLD = ROOT / '12_shared-abcd-statistics' / '06_TUT2017'


def load_module(path):
    spec = importlib.util.spec_from_file_location('tut6300_runtime', str(path))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def seed_all(value):
    random.seed(value)
    np.random.seed(value % (2**32 - 1))
    torch.manual_seed(value)
    torch.cuda.manual_seed_all(value)


def main():
    runtime = load_module(Path(__file__).parent / 'runtime' / '06_TUT2017' / 'runtime.py')
    dataset = runtime.load_dataset()
    samples = list(runtime.iter_samples(dataset))
    split_counts = Counter(s['source_split'] for s in samples)
    label_counts = Counter(dataset['records'][i][3] for i in range(len(dataset['records'])))
    paths = [str(Path(s['audio_path']).resolve()) for s in samples]
    missing = [p for p in paths if not Path(p).is_file()]
    duplicates = len(paths) - len(set(paths))
    audit = {
        'total': len(samples),
        'split_counts': dict(split_counts),
        'n_classes': len(dataset['kg_classes']),
        'classes': dataset['kg_classes'],
        'label_counts': dict(label_counts),
        'missing_audio': len(missing),
        'duplicate_paths': duplicates,
        'order': 'development followed by evaluation',
    }
    if audit['total'] != 6300 or split_counts != Counter({'development': 4680, 'evaluation': 1620}):
        raise RuntimeError(f'unexpected split counts: {audit}')
    if missing or duplicates or len(dataset['kg_classes']) != 15:
        raise RuntimeError(f'dataset audit failed: {audit}')

    cache_root = TASK / 'cache' / '06_TUT2017'
    audio_cache = cache_root / 'audio_cache'
    audio_cache.mkdir(parents=True, exist_ok=True)
    shutil.copy2(OLD / 'text_embeddings.pt', cache_root / 'text_embeddings.pt')

    for i in range(4680):
        src = OLD / 'audio_cache' / f'{i:06d}.pt'
        dst = audio_cache / f'{i:06d}.pt'
        if not src.is_file():
            raise FileNotFoundError(src)
        if not dst.exists():
            os.link(src, dst)

    seed_all(42)
    torch.use_deterministic_algorithms(True)
    torch.backends.cudnn.benchmark = False
    torch.backends.cudnn.deterministic = True
    torch.backends.cuda.matmul.allow_tf32 = False
    torch.backends.cudnn.allow_tf32 = False
    clap = runtime.CLAP(version='2023', use_cuda=True)
    clap.clap.eval()
    for i in tqdm(range(4680, len(samples)), desc='TUT2017 evaluation cache', mininterval=10):
        dst = audio_cache / f'{i:06d}.pt'
        if dst.is_file():
            continue
        sample = samples[i]
        sample_seed = int(hashlib.sha256(('42|' + sample['audio_path']).encode()).hexdigest()[:8], 16)
        seed_all(sample_seed)
        embedding = F.normalize(
            runtime.to_tensor(clap.get_audio_embeddings([sample['audio_path']])).to('cpu').float(), dim=-1
        )
        torch.save(embedding, dst)

    cached = len(list(audio_cache.glob('*.pt')))
    audit['cache_files'] = cached
    audit['reused_development_cache'] = 4680
    audit['new_evaluation_cache'] = 1620
    if cached != 6300:
        raise RuntimeError(f'expected 6300 cache files, got {cached}')
    TASK.mkdir(parents=True, exist_ok=True)
    (TASK / 'dataset_audit.json').write_text(json.dumps(audit, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps(audit, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
