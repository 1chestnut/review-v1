#!/usr/bin/env python3
"""Task23D: missing Nr={5,10,47} test-set sensitivity cells; diagnostic only."""
import argparse
import importlib.util
from pathlib import Path

ROOT=Path('/data/zkx/zkx/review1')
VALID={'01_ESC50','02_UrbanSound8K','03_FSD50K','05_AudioSet','06_TUT2017'}
p=argparse.ArgumentParser();p.add_argument('dataset',choices=sorted(VALID));a=p.parse_args()
spec=importlib.util.spec_from_file_location('task23_core',str(ROOT/'task23_dcase_validation.py'))
core=importlib.util.module_from_spec(spec);spec.loader.exec_module(core)
core.DATASET=a.dataset
core.SOURCE=ROOT/'12_shared-abcd-statistics'/a.dataset
core.OUT=ROOT/'23D_five_test_extended_Nr_sensitivity'/a.dataset
core.N_RELATIONS=(5,10,47)
core.METHODS=[f'TFS_alpha{x:.1f}_Nr{nr}' for nr in core.N_RELATIONS for x in core.ALPHAS]
core.main()
