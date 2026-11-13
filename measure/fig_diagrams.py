#!/usr/bin/env python3
"""Sinh 3 sơ đồ quy trình: figs/wf_runtime.png, wf_training.png, wf_counteval.png"""
import os
from figlib import *

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'figs')
H = 7.6


def runtime():
    fig, ax = canvas(16, H)
    bx, bw = 1.0, 14.7
    ys = [0.25, 2.65, 5.05]
    hh = 2.15
    band(ax, bx, ys[0], bw, hh, 'green', 'Mô phỏng & thu ảnh', '⚙')
    band(ax, bx, ys[1], bw, hh, 'purple', 'Nhận diện & đếm', '◎')
    band(ax, bx, ys[2], bw, hh, 'orange', 'Hiển thị & điều khiển', '▣')
    cy = [y + 1.4 for y in ys]
    h = 1.05
    # --- dải 1
    X = [3.0, 6.55, 10.1, 13.65]
    node(ax, X[0], cy[0], 2.5, h, 'Thế giới Gazebo\nxe · người · đường', 'data', kind='green', fs=12.5)
    node(ax, X[1], cy[0], 2.7, h, 'PX4 SITL\nUAV x500 + gimbal', fs=12.5)
    node(ax, X[2], cy[0], 2.7, h, 'Camera 1920×1080\n30 Hz mô phỏng', fs=12.5)
    node(ax, X[3], cy[0], 2.7, h, 'ros_gz_bridge\n/camera (ROS 2)', 'hero', fs=12.5, sub='11,7 Hz thực (RTF 0,38)')
    for a, b, w1, w2 in ((0, 1, 2.5, 2.7), (1, 2, 2.7, 2.7), (2, 3, 2.7, 2.7)):
        arrow(ax, [(X[a] + w1 / 2 + 0.05, cy[0]), (X[b] - w2 / 2 - 0.02, cy[0])])
    # --- dải 2
    X2 = [2.6, 5.75, 8.9, 12.05, 14.75]
    w2 = 2.3
    node(ax, X2[0], cy[1], w2, h, 'Chuyển ảnh\nROS → BGR', fs=12.5, sub='0,8 ms')
    node(ax, X2[1], cy[1], w2, h, 'YOLOv8m\n(tinh chỉnh)', 'hero', fs=12.5, sub='30,1 ms')
    node(ax, X2[2], cy[1], w2, h, 'ByteTrack\nKalman + IoU', fs=12.5, sub='0,75 ms')
    node(ax, X2[3], cy[1], w2, h, 'FlowCounter\nvùng 0,42–0,58', fs=12.5, sub='0,02 ms')
    X2[4] = 14.75
    node(ax, X2[4], cy[1], 1.7, h, 'Số xe\nlưu lượng', 'result', fs=12, kind='green')
    for i in range(3):
        arrow(ax, [(X2[i] + w2 / 2 + 0.05, cy[1]), (X2[i + 1] - w2 / 2 - 0.02, cy[1])])
    arrow(ax, [(X2[3] + w2 / 2 + 0.05, cy[1]), (X2[4] - 0.85 - 0.02, cy[1])])
    # nối dải 1 → dải 2 qua lề trái
    g1 = (ys[0] + hh + ys[1]) / 2
    arrow(ax, [(X[3], cy[0] + h / 2 + 0.05), (X[3], g1), (0.62, g1), (0.62, cy[1]), (X2[0] - w2 / 2 - 0.02, cy[1])], color=INK)
    # --- dải 3
    X3 = [3.0, 6.55, 10.1, 13.65]
    node(ax, X3[0], cy[2], 2.5, h, 'Backend FastAPI\nJPEG + danh sách hộp', fs=12, sub='4,7 ms JPEG')
    node(ax, X3[1], cy[2], 2.7, h, 'WebSocket v1\ntrung bình 4,3 gói/s', fs=12, sub='116 ms đầu cuối')
    node(ax, X3[2], cy[2], 2.7, h, 'Giao diện web\nvideo + ô lưu lượng', 'light', fs=12)
    node(ax, X3[3], cy[2], 2.7, h, 'Lệnh điều khiển\nbay · gimbal → PX4', 'data', kind='orange', fs=12)
    for a, b, w1, w2_ in ((0, 1, 2.5, 2.7), (1, 2, 2.7, 2.7), (2, 3, 2.7, 2.7)):
        arrow(ax, [(X3[a] + w1 / 2 + 0.05, cy[2]), (X3[b] - w2_ / 2 - 0.02, cy[2])])
    g2 = (ys[1] + hh + ys[2]) / 2
    arrow(ax, [(X2[4], cy[1] + h / 2 + 0.05), (X2[4], g2), (0.62, g2), (0.62, cy[2]), (X3[0] - 1.25 - 0.02, cy[2])], color=INK)
    save(fig, f'{OUT}/wf_runtime.png')


def training():
    fig, ax = canvas(16, 8.05)
    bx, bw = 0.4, 15.2
    b1, b2, b3 = (0.25, 2.4), (2.9, 2.6), (5.75, 2.15)
    band(ax, bx, b1[0], bw, b1[1], 'green', 'Huấn luyện', '⚙')
    band(ax, bx, b2[0], bw, b2[1], 'purple', 'Kiểm định', '✔')
    band(ax, bx, b3[0], bw, b3[1], 'orange', 'Kiểm thử / Dự đoán', '◎')
    h = 1.1
    c1, c2, c3 = b1[0] + 1.4, b2[0] + 1.4, b3[0] + 1.3
    # huấn luyện
    node(ax, 2.2, c1 + 0.1, 2.5, 1.2, 'Gazebo datagen\nxe + người ngẫu nhiên', 'data', kind='green', fs=11, sub='nhãn tự động từ bbox camera')
    node(ax, 5.3, c1, 2.5, h, 'Chụp ngẫu nhiên\nđộ cao · pitch · hướng', fs=11.5)
    ax.text(8.0, c1 - 0.78, 'Ma trận ảnh (6371)', fontsize=11, fontweight='bold', color=INK, ha='center')
    matrix(ax, 8.0, c1 - 0.3, 5, 2)
    ax.text(8.0, c1 + 0.2, '6371 ảnh train', fontsize=11, color=MUTED, fontweight='bold', ha='center')
    node(ax, 10.9, c1, 2.5, h, 'Fine-tune YOLOv8m\n50 epoch · lr0 0,002', fs=11.5)
    node(ax, 14.0, c1, 2.5, h, 'Mô hình ứng viên\n(last.pt)', 'hero', fs=12)
    arrow(ax, [(3.4, c1), (4.03, c1)]); arrow(ax, [(6.58, c1), (7.0, c1)] if False else [(6.58, c1), (7.12, c1)])
    arrow(ax, [(8.9, c1), (9.62, c1)]); arrow(ax, [(12.2, c1), (12.72, c1)])
    # kiểm định
    node(ax, 2.2, c2, 2.3, 1.2, 'Tập val\n1163 ảnh', 'data', kind='purple', fs=12, sub='kèm nhãn')
    node(ax, 5.3, c2, 2.5, h, 'Suy luận\nimgsz 640', fs=12)
    matrix(ax, 7.95, c2, 5, 1)
    node(ax, 10.4, c2, 2.5, h, 'Đánh giá\nP · R · mAP', 'plain', fs=12)
    node(ax, 14.0, c2, 2.5, h, 'best.pt\n(mô hình cuối)', 'hero', fs=12)
    arrow(ax, [(3.4, c2), (4.03, c2)]); arrow(ax, [(6.58, c2), (7.12, c2)]); arrow(ax, [(8.78, c2), (9.12, c2)])
    arrow(ax, [(11.7, c2), (12.72, c2)])
    chip(ax, 8.4, c2 + 0.9, 3.45, 0.42, 'Chỉ số: P, R, mAP50, mAP50–95', 'purple', fs=9.5)
    chip(ax, 12.1, c2 + 0.9, 3.4, 0.42, 'Chọn best.pt · dừng sớm (patience 10)', 'purple', fs=9.5)
    arrow(ax, [(9.6, c2 + 0.69), (9.6, c2 + 0.58)], lw=1.8); arrow(ax, [(11.5, c2 + 0.69), (11.5, c2 + 0.58)], lw=1.8)
    g1 = (b1[0] + b1[1] + b2[0]) / 2
    arrow(ax, [(14.0, c1 + h / 2 + 0.05), (14.0, g1), (10.4, g1), (10.4, c2 - h / 2 - 0.02)])
    # kiểm thử
    node(ax, 2.2, c3, 2.3, h, 'Ảnh kiểm thử\n300 ảnh (seed khác)', 'data', kind='orange', fs=11)
    node(ax, 5.3, c3, 2.5, h, 'Letterbox 640\nchuẩn hoá ảnh', fs=12)
    matrix(ax, 7.95, c3, 5, 1)
    node(ax, 10.4, c3, 2.7, h + 0.1, 'best.pt  →  Dự đoán', 'light', fs=12)
    node(ax, 14.0, c3, 2.5, h, 'Hộp + lớp + độ tin cậy\nmAP50 0,982', 'result', fs=11, kind='green')
    arrow(ax, [(3.4, c3), (4.03, c3)]); arrow(ax, [(6.58, c3), (7.12, c3)]); arrow(ax, [(8.78, c3), (9.0, c3)])
    arrow(ax, [(11.78, c3), (12.72, c3)])
    g2 = (b2[0] + b2[1] + b3[0]) / 2
    arrow(ax, [(14.0, c2 + h / 2 + 0.05), (14.0, g2), (10.4, g2), (10.4, c3 - h / 2 - 0.1)])
    dashed(ax, (b1[0] + b1[1] + b2[0]) / 2 + 0.0, 0.4, 0.4) if False else None
    save(fig, f'{OUT}/wf_training.png')


def counteval():
    fig, ax = canvas(16, H)
    bx, bw = 0.4, 14.9
    b1, b2, b3 = (0.25, 2.1), (2.6, 2.1), (5.15, 2.2)
    band(ax, bx, b1[0], bw, b1[1], 'green', 'Ground truth', '◎')
    band(ax, bx, b2[0], bw, b2[1], 'purple', 'Hệ thống đếm', '⚙')
    band(ax, bx, b3[0], bw, b3[1], 'orange', 'Đối chiếu', '✔')
    h = 1.1
    c1, c2, c3 = b1[0] + 1.3, b2[0] + 1.3, b3[0] + 1.45
    X = [2.4, 5.3, 8.2, 11.1, 13.9]
    node(ax, X[0], c1, 2.3, h, 'Pose xe thật\n2152 mẫu / 120 s', 'data', kind='green', fs=11.5)
    node(ax, X[1], c1, 2.5, h, 'Chiếu pinhole\nHFOV 1,204 rad', fs=11.5)
    node(ax, X[2], c1, 2.5, h, 'Xe vào vùng đếm\nx ∈ [0,42; 0,58]·W', fs=11.5)
    node(ax, X[3], c1, 2.3, h, 'Chiều qua vùng\n← hoặc →', fs=11.5)
    node(ax, X[4], c1, 2.1, h, 'GT = 173 xe', 'hero', fs=13)
    node(ax, X[0], c2, 2.3, h, 'Ảnh camera\nUAV cao 14 m', 'data', kind='purple', fs=11.5)
    node(ax, X[1], c2, 2.5, h, 'YOLOv8m\n+ ByteTrack', fs=11.5)
    node(ax, X[2], c2, 2.5, h, 'FlowCounter\n(trạng thái vùng)', fs=11.5)
    node(ax, X[3], c2, 2.3, h, 'Nhật ký sự kiện\ncounter_events.csv', fs=11)
    node(ax, X[4], c2, 2.1, h, 'Đếm = 136 xe', 'hero', fs=13)
    for c in (c1, c2):
        arrow(ax, [(X[0] + 1.2, c), (X[1] - 1.27, c)])
        arrow(ax, [(X[1] + 1.27, c), (X[2] - 1.27, c)])
        arrow(ax, [(X[2] + 1.27, c), (X[3] - 1.17, c)])
        arrow(ax, [(X[3] + 1.17, c), (X[4] - 1.12, c)])
    # đối chiếu
    node(ax, 5.4, c3, 3.4, h + 0.2, 'Ghép Hungarian\n|Δt| ≤ 1 s · cùng chiều', 'light', fs=12)
    node(ax, 9.3, c3, 2.5, h, 'TP 135\nFN 38 · FP 1', fs=12.5)
    node(ax, 12.0, c3, 2.2, h, 'P 0,993\nR 0,780', fs=12.5)
    node(ax, 14.35, c3, 1.9, h, 'q: 68,0\nvs 86,4', 'result', fs=11.5, kind='green')
    ax.text(14.35, c3 + 0.72, 'xe/phút', fontsize=10, color=MUTED, ha='center', fontweight='bold', zorder=6)
    arrow(ax, [(7.12, c3), (8.02, c3)]); arrow(ax, [(10.57, c3), (10.88, c3)]); arrow(ax, [(13.12, c3), (13.38, c3)])
    ga = (b2[0] + b2[1] + b3[0]) / 2
    arrow(ax, [(X[4], c2 + h / 2 + 0.05), (X[4], ga - 0.1), (4.5, ga - 0.1), (4.5, c3 - h / 2 - 0.12)])
    ax.plot([15.52, 15.52], [c1, ga + 0.1], color=INK, lw=2.4, zorder=3)
    ax.plot([X[4] + 1.07, 15.52], [c1, c1], color=INK, lw=2.4, zorder=3)
    arrow(ax, [(15.52, ga + 0.1), (6.6, ga + 0.1), (6.6, c3 - h / 2 - 0.12)])
    save(fig, f'{OUT}/wf_counteval.png')


def counter():
    fig, ax = canvas(16, 5.75)
    bx, bw = 1.0, 14.7
    b1, b2 = (0.25, 2.1), (2.65, 2.45)
    band(ax, bx, b1[0], bw, b1[1], 'purple', 'Phát hiện & theo vết', '◎')
    band(ax, bx, b2[0], bw, b2[1], 'orange', 'Luật đếm theo vùng', '✔')
    h = 1.05
    c1, c2 = b1[0] + 1.4, b2[0] + 1.6
    X = [3.0, 6.55, 10.1, 13.65]
    node(ax, X[0], c1, 2.5, h, 'Ảnh /camera\nt = stamp ảnh', 'data', kind='purple', fs=12)
    node(ax, X[1], c1, 2.7, h, 'YOLOv8m predict\nconf 0,1 · lớp 0,2,3,5,7', fs=11.5)
    node(ax, X[2], c1, 2.7, h, 'ByteTrack\nupdate', fs=12.5)
    node(ax, X[3], c1, 2.7, h, 'Track\nid · lớp · hộp', 'hero', fs=12.5)
    for a, b, w1, w2 in ((0, 1, 2.5, 2.7), (1, 2, 2.7, 2.7), (2, 3, 2.7, 2.7)):
        arrow(ax, [(X[a] + w1 / 2 + 0.05, c1), (X[b] - w2 / 2 - 0.02, c1)])
    node(ax, 4.0, c2, 5.2, 1.3, 'Đếm khi cả 4 điều kiện đúng', 'light', fs=12.5, sub='id chưa đếm · điểm trước ngoài vùng · thấy ≥ 3 khung · tâm trong vùng')
    node(ax, 8.4, c2, 2.3, h, 'Lớp = đa số\nphiếu của track', fs=11.5)
    node(ax, 11.4, c2, 2.7, h, 'N += 1\ntheo lớp · chiều · CSV', fs=11.5)
    node(ax, 14.4, c2, 2.2, h, 'Mỗi 1 s: JSON\nN · q · q₆₀', 'result', fs=11.5, kind='green')
    arrow(ax, [(6.65, c2), (7.22, c2)]); arrow(ax, [(9.57, c2), (10.0, c2)]); arrow(ax, [(12.77, c2), (13.27, c2)])
    g = (b1[0] + b1[1] + b2[0]) / 2
    arrow(ax, [(X[3], c1 + h / 2 + 0.05), (X[3], g), (0.62, g), (0.62, c2), (1.38, c2)])
    save(fig, f'{OUT}/wf_counter.png')


if __name__ == '__main__':
    runtime(); training(); counteval(); counter()
    print('ok')
