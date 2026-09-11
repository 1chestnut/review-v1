# Task25(e) Selector behavior analysis

This is a post-hoc explanation of the frozen Task25 selector. No result is used to modify the method or parameters.

| Dataset | unique used / pool | unique selected sets | dominant set share | normalized top-1 entropy | outside frozen set | mean Jaccard |
|---|---:|---:|---:|---:|---:|---:|
| ESC-50 | 47/47 | 1708 | 1.40% | 0.938 | 92.92% | 0.040 |
| UrbanSound8K | 47/47 | 5461 | 1.53% | 0.880 | 86.14% | 0.074 |
| FSD50K | 47/47 | 9066 | 1.51% | 0.977 | 92.32% | 0.057 |
| AudioSet | 47/47 | 15671 | 1.50% | 0.970 | 91.16% | 0.058 |
| TUT2017 | 47/47 | 3334 | 1.03% | 0.939 | 89.10% | 0.063 |

Interpretation rules: low dominant-set share and non-zero entropy indicate sample-dependent behavior; they do not by themselves prove better accuracy. Performance-by-vote tables show association, not causation.
