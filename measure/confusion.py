#!/usr/bin/env python3
"""Ma trận nhầm lẫn 5 lớp + nền trên tập test (300 ảnh) cho 3 mô hình -> measure/confusion.json.
Chạy bằng môi trường có ultralytics:  ~/px4-venv/bin/python measure/confusion.py
Ultralytics: matrix[dự đoán, thật]; ngưỡng conf 0,25, IoU 0,45 (mặc định của ConfusionMatrix)."""
import json, os
from ultralytics import YOLO
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IDS = [0, 2, 3, 5, 7]
MODELS = {'COCO gốc': f'{ROOT}/yolov8m.pt',
          '30 epoch': f'{ROOT}/finetune/runs/yolov8m_sim/weights/best.pt',
          '50 epoch': f'{ROOT}/finetune/runs/yolov8m_sim_50ep_colab/weights/best.pt'}
out = {}
for name, w in MODELS.items():
    m = YOLO(w).val(data=f'{ROOT}/finetune/sim_traffic.yaml', split='test', imgsz=640, batch=8, plots=True, verbose=False, project=os.environ.get('CM_TMP', '/tmp/cm'), name=name.replace(' ', '_'), exist_ok=True)
    M = m.confusion_matrix.matrix            # (81, 81): hàng = dự đoán, cột = thật, chỉ số 80 = nền
    idx = IDS + [80]
    out[name] = [[float(M[i][j]) for j in idx] for i in idx]
    print(name, 'tổng', M.sum())
json.dump(out, open(f'{ROOT}/measure/confusion.json', 'w'), indent=1)
