"""Thời gian BYTETracker.update theo số hộp phát hiện (dữ liệu tổng hợp: n xe chuyển động thẳng + nhiễu)."""
import sys, time, json, statistics as st
import numpy as np
from ultralytics.trackers.byte_tracker import BYTETracker
from ultralytics.utils import YAML, IterableSimpleNamespace
from ultralytics.utils.checks import check_yaml
from ultralytics.engine.results import Boxes
rng = np.random.default_rng(0)
out = {}
for n in (5, 10, 20, 50, 100, 200, 400):
    tr = BYTETracker(IterableSimpleNamespace(**YAML.load(check_yaml('bytetrack.yaml'))))
    pos = rng.uniform([0, 0], [1800, 1000], (n, 2)); vel = rng.normal(0, 8, (n, 2)); wh = rng.uniform(30, 90, (n, 2))
    ts = []
    for f in range(60):
        c = pos + vel * f + rng.normal(0, 1.5, (n, 2))
        xyxy = np.c_[c - wh / 2, c + wh / 2]
        data = np.c_[xyxy, rng.uniform(0.3, 0.95, n), rng.integers(0, 5, n)].astype(np.float32)
        b = Boxes(data, (1080, 1920))
        t = time.perf_counter(); tr.update(b.cpu().numpy() if hasattr(b, 'cpu') else b, None); ts.append((time.perf_counter() - t) * 1e3)
    out[n] = round(st.median(ts[10:]), 3)
    print(n, out[n], flush=True)
json.dump(out, open(sys.argv[1], 'w'))
