#!/usr/bin/env python3
"""Run the Task23 grid on one held-out test dataset for diagnostics only."""
import argparse
import importlib.util
from pathlib import Path

ROOT = Path('/data/zkx/zkx/review1')
VALID = {
    '01_ESC50', '02_UrbanSound8K', '03_FSD50K',
    '05_AudioSet', '06_TUT2017',
}

parser = argparse.ArgumentParser()
parser.add_argument('dataset', choices=sorted(VALID))
args = parser.parse_args()

spec = importlib.util.spec_from_file_location('task23_core', str(ROOT/'task23_dcase_validation.py'))
core = importlib.util.module_from_spec(spec)
spec.loader.exec_module(core)
core.DATASET = args.dataset
core.SOURCE = ROOT/'12_shared-abcd-statistics'/args.dataset
core.OUT = ROOT/'23B_five_test_parameter_diagnostic'/args.dataset
core.main()
