#!/usr/bin/env python3
"""Kết quả thực tế trong mô phỏng -> measure/figs/sim_compare.png, sim_counting_demo.png
Chạy:  ~/px4-venv/bin/python measure/fig_sim_results.py
  - sim_compare: ảnh chụp từ camera UAV trong Gazebo (tập test): nhãn thật | YOLOv8m gốc | mô hình 50 epoch
  - sim_counting_demo: traffic_counter.py (50 epoch + ByteTrack + FlowCounter) chạy trên video bay trong mô phỏng"""
import csv, glob, os, shutil, subprocess, sys, tempfile
import cv2, numpy as np
from ultralytics import YOLO

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = f'{ROOT}/measure/figs'
IDS = {0: 'Người', 2: 'Ô tô', 3: 'Xe máy', 5: 'Xe buýt', 7: 'Xe tải'}
COL = {0: (60, 60, 230), 2: (230, 140, 30), 3: (60, 180, 60), 5: (200, 60, 200), 7: (0, 190, 220)}   # BGR


def draw(img, boxes, with_conf=False):
    img = img.copy()
    for c, x1, y1, x2, y2, p in boxes:
        col = COL[c]
        cv2.rectangle(img, (int(x1), int(y1)), (int(x2), int(y2)), col, 3)
        t = IDS[c] + (f' {p:.2f}' if with_conf else '')
        (tw, th), _ = cv2.getTextSize(t, cv2.FONT_HERSHEY_SIMPLEX, 0.9, 2)
        cv2.rectangle(img, (int(x1), int(y1) - th - 10), (int(x1) + tw + 6, int(y1)), col, -1)
        cv2.putText(img, t, (int(x1) + 3, int(y1) - 6), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255, 255, 255), 2, cv2.LINE_AA)
    return img


def title(img, text):
    h, w = img.shape[:2]
    bar = np.full((70, w, 3), 255, np.uint8)
    cv2.putText(bar, text, (20, 48), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (36, 51, 15), 3, cv2.LINE_AA)
    return np.vstack([bar, img])


def compare():
    coco = YOLO(f'{ROOT}/yolov8m.pt'); ft = YOLO(f'{ROOT}/finetune/runs/yolov8m_sim_50ep_colab/weights/best.pt')
    imgs = sorted(glob.glob(f'{ROOT}/finetune/data/images/test/*.jpg'))
    cand = []
    for p in imgs:
        lb = p.replace('/images/', '/labels/').rsplit('.', 1)[0] + '.txt'
        L = [l.split() for l in open(lb)] if os.path.exists(lb) else []
        cls = {int(l[0]) for l in L}
        if len(L) >= 8 and 0 in cls and 3 in cls and (2 in cls or 7 in cls):
            cand.append((len(L), p))
    cand = [c for c in cand if c[0] <= 20]
    pick = [cand[len(cand) // 4][1], cand[3 * len(cand) // 4][1]]
    rows = []
    for p in pick:
        im = cv2.imread(p); h, w = im.shape[:2]
        lb = p.replace('/images/', '/labels/').rsplit('.', 1)[0] + '.txt'
        gt = [(int(l[0]), (float(l[1]) - float(l[3]) / 2) * w, (float(l[2]) - float(l[4]) / 2) * h,
               (float(l[1]) + float(l[3]) / 2) * w, (float(l[2]) + float(l[4]) / 2) * h, 1) for l in (x.split() for x in open(lb))]
        res = []
        for m in (coco, ft):
            b = m.predict(im, classes=list(IDS), conf=0.25, verbose=False)[0].boxes
            res.append([(int(c), *xy, float(s)) for c, xy, s in zip(b.cls, b.xyxy.tolist(), b.conf)])
        panels = [draw(im, gt), draw(im, res[0], True), draw(im, res[1], True)]
        print(os.path.basename(p), 'GT', len(gt), 'COCO', len(res[0]), '50ep', len(res[1]))
        rows.append(np.hstack([cv2.resize(x, (800, int(800 * h / w))) for x in panels]))
    head = np.hstack([title(np.zeros((1, 800, 3), np.uint8), t)[:70] for t in ('Nhãn thật', 'YOLOv8m gốc (COCO)', 'Mô hình 50 epoch')])
    cv2.imwrite(f'{OUT}/sim_compare.png', np.vstack([head] + rows))


def counting_demo():
    tmp = tempfile.mkdtemp(); vid = f'{tmp}/ann.mp4'
    before = set(os.listdir(f'{ROOT}/logs')) if os.path.isdir(f'{ROOT}/logs') else set()
    subprocess.run([sys.executable, f'{ROOT}/detection/traffic_counter.py', '--video', f'{ROOT}/demo/video_bay_nhan_dien.mp4',
                    '--no-show', '--save', vid], check=True, capture_output=True)
    new = [f for f in os.listdir(f'{ROOT}/logs') if f not in before]
    rows = list(csv.DictReader(open(f'{ROOT}/logs/{new[0]}', encoding='utf-8')))
    for f in new:
        os.remove(f'{ROOT}/logs/{f}')                     # log của lần chạy dựng hình này không cần giữ
    cap = cv2.VideoCapture(vid)
    ts = [2.5, 6.0, 9.0, 12.5, 16.0, 24.5]
    ims = []
    for t in ts:
        cap.set(cv2.CAP_PROP_POS_FRAMES, int(t * 10)); ok, f = cap.read()
        f = cv2.resize(f, (800, 450)); cv2.rectangle(f, (0, 0), (799, 449), (255, 255, 255), 3); ims.append(f)
    cv2.imwrite(f'{OUT}/sim_counting_demo.png', np.vstack([np.hstack(ims[:3]), np.hstack(ims[3:])]))
    shutil.rmtree(tmp)
    from collections import Counter
    print(len(rows), Counter(r['class'] for r in rows), Counter(r['direction'] for r in rows))


if __name__ == '__main__':
    compare(); counting_demo()
