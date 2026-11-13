#!/usr/bin/env python3
"""Sơ đồ để duyệt (chưa đưa vào slide) -> measure/figs/review/*.png"""
import json, os, statistics as st
import numpy as np
from figlib import *
import matplotlib.pyplot as plt

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = f'{HERE}/figs/review'
os.makedirs(OUT, exist_ok=True)
live = json.load(open(f'{HERE}/live_probe.json'))


def sv(fig, name):
    fig.savefig(f'{OUT}/{name}.png', dpi=150, facecolor=fig.get_facecolor())
    plt.close(fig)


def b4(ax, x0, y0, items, style_list=None, kind='green'):
    """Lưới 2x2 khối trong dải: items = [(chữ, kiểu)] theo thứ tự trái→phải, trên→dưới."""
    for k, (t, sty) in enumerate(items):
        cx = x0 + 0.25 + 1.7 + (k % 2) * 3.6
        cy = y0 + 1.6 + (k // 2) * 1.1
        node(ax, cx, cy, 3.4, 0.9, t, sty, fs=11.5, kind=kind)


# ------------------------------------------------------------------ 01 sơ đồ khối hệ thống
def block_diagram():
    fig, ax = canvas(16, 7.55)
    W, Hb = 7.4, 3.3
    X0, X1 = 0.3, 8.3
    Y0, Y1 = 0.25, 3.95
    band(ax, X0, Y0, W, Hb, 'orange', 'Giao diện & điều khiển', '▣')
    band(ax, X1, Y0, W, Hb, 'purple', 'Xử lý AI', '◎')
    band(ax, X0, Y1, W, Hb, 'green', 'Mô phỏng', '⚙')
    band(ax, X1, Y1, W, Hb, 'blue', 'Trung gian', '⇄')
    b4(ax, X0, Y0, [('Web UI\nvideo · hộp · lưu lượng', 'plain'), ('WebSocket v1\nJSON + ảnh JPEG', 'plain'),
                    ('Bàn phím\nbay + gimbal', 'plain'), ('Lệnh bay từ web\n(offboard)', 'plain')], kind='orange')
    b4(ax, X1, Y0, [('YOLOv8m\ntinh chỉnh, 5 lớp', 'hero'), ('ByteTrack\nKalman + IoU', 'plain'),
                    ('FlowCounter\nđếm theo vùng', 'plain'), ('uav_bridge.py\nbackend', 'plain')], kind='purple')
    b4(ax, X0, Y1, [('Gazebo Sim\nđường Sonoma + camera', 'plain'), ('traffic.py\n16 xe, 20 Hz', 'plain'),
                    ('PX4 SITL\nUAV x500_depth', 'plain'), ('Gimbal 2 trục\npitch · yaw', 'plain')], kind='green')
    b4(ax, X1, Y1, [('ros_gz_bridge\nảnh gz → /camera', 'plain'), ('ROS 2 Humble\n/camera · /traffic/counts', 'plain'),
                    ('MAVSDK-Python\nUDP 14540', 'plain'), ('gz topic\n/gimbal/cmd_*', 'plain')], kind='blue')
    ym = Y1 + Hb / 2 + 0.3
    arrow(ax, [(X0 + W + 0.03, ym), (X1 - 0.03, ym)]); lab(ax, 8.0, ym - 0.35, 'ảnh', fs=9.5, w=0.7)
    arrow(ax, [(X1 + W / 2, Y1 - 0.03), (X1 + W / 2, Y0 + Hb + 0.03)]); lab(ax, X1 + W / 2 + 0.9, Y0 + Hb + 0.35, 'ảnh · số đếm', fs=9.5, w=1.6)
    arrow(ax, [(X1 - 0.03, Y0 + Hb / 2 + 0.3), (X0 + W + 0.03, Y0 + Hb / 2 + 0.3)]); lab(ax, 8.0, Y0 + Hb / 2 - 0.05, 'WS', fs=9.5, w=0.6)
    arrow(ax, [(X0 + W / 2, Y0 + Hb + 0.03), (X0 + W / 2, Y1 - 0.03)], dash=True, color=MUTED); lab(ax, X0 + W / 2 + 1.0, Y0 + Hb + 0.35, 'lệnh bay, gimbal', fs=9.5, w=1.8)
    sv(fig, '01_so_do_khoi_he_thong')


# ------------------------------------------------------------------ 02 tương tác giữa các khối
def interaction():
    fig, ax = canvas(16, 8.7)
    N = lambda x, y, t, sty='plain', w=2.7, h=1.0: node(ax, x, y, w, h, t, sty, fs=12)
    N(2.3, 1.2, 'traffic.py\n16 xe, 20 Hz'); N(2.3, 3.9, 'Gazebo Sim\n(world + camera)', 'data'); N(2.3, 6.6, 'PX4 SITL\nUAV + gimbal')
    N(6.7, 3.9, 'ros_gz_bridge'); N(10.7, 2.3, 'traffic_counter.py\nYOLOv8m + ByteTrack', 'hero', w=3.0); N(10.7, 5.5, 'uav_bridge.py\n(backend)', 'hero', w=3.0)
    N(14.4, 5.5, 'Web UI\ntrình duyệt', 'light', w=2.3); N(6.7, 6.6, 'keyboard-\nmavsdk-test.py')
    arrow(ax, [(2.3, 1.75), (2.3, 3.33)]); lab(ax, 3.65, 2.55, 'set_pose_vector · 20 Hz', fs=9.5, w=2.4)
    arrow(ax, [(3.7, 3.9), (5.33, 3.9)]); lab(ax, 4.5, 3.55, 'gz Image', fs=9.5, w=1.1)
    ax.plot([8.05, 8.75], [3.9, 3.9], color=INK, lw=2.4, zorder=3); ax.plot([8.75, 8.75], [2.3, 5.5], color=INK, lw=2.4, zorder=3)
    arrow(ax, [(8.75, 2.3), (9.18, 2.3)]); arrow(ax, [(8.75, 5.5), (9.18, 5.5)])
    lab(ax, 8.75, 4.72, '/camera', fs=9.5, w=1.05)
    arrow(ax, [(10.7, 2.85), (10.7, 4.95)]); lab(ax, 12.2, 3.9, '/traffic/counts · 1 Hz', fs=9.5, w=2.2)
    arrow(ax, [(12.25, 5.3), (13.22, 5.3)]); arrow(ax, [(13.22, 5.7), (12.25, 5.7)])
    lab(ax, 12.73, 6.6, 'WebSocket 8765', fs=9.5, w=1.9)
    arrow(ax, [(5.32, 6.6), (3.67, 6.6)]); lab(ax, 4.5, 6.95, 'manual_control', fs=9.5, w=1.6)
    arrow(ax, [(10.7, 6.05), (10.7, 8.0), (2.3, 8.0), (2.3, 7.17)], dash=True, color=MUTED)
    lab(ax, 6.5, 8.0, 'MAVSDK: offboard 20 Hz ↓ · telemetry ↑', fs=9.5, w=4.4)
    arrow(ax, [(5.7, 6.1), (5.7, 5.25), (3.0, 5.25), (3.0, 4.5)], dash=True, color=MUTED); lab(ax, 4.35, 5.25, 'gz topic: gimbal', fs=9.5, w=1.9)
    sv(fig, '02_tuong_tac_giua_cac_khoi')


# ------------------------------------------------------------------ 03 luồng dữ liệu
def dataflow():
    fig, ax = canvas(16, 8.0)
    bx, bw = 1.0, 14.7
    ys = [0.25, 2.8, 5.35]; hh = 2.2
    band(ax, bx, ys[0], bw, hh, 'green', 'Nguồn ảnh', '⚙')
    band(ax, bx, ys[1], bw, hh, 'purple', 'Nhánh đếm (traffic_counter)', '◎')
    band(ax, bx, ys[2], bw, hh, 'orange', 'Nhánh hiển thị (uav_bridge)', '▣')
    c = [y + 1.45 for y in ys]
    h = 1.0
    jb = st.mean(x['jpeg_bytes'] for x in live) / 1e3
    nb = st.mean(x['n'] for x in live) / 1e3
    def row(cy, items, xs, ws):
        for (t, sty, kind), x, w in zip(items, xs, ws):
            node(ax, x, cy, w, h, t, sty, fs=10.8, kind=kind)
        for i in range(len(items) - 1):
            arrow(ax, [(xs[i] + ws[i] / 2 + 0.04, cy), (xs[i + 1] - ws[i + 1] / 2 - 0.03, cy)])
    row(c[0], [('Gazebo render\ncamera IMX214', 'plain', 'green'), ('Ảnh rgb8 1920×1080\n6,22 MB · 30 Hz sim', 'data', 'green'),
               ('ros_gz_bridge', 'plain', 'green'), ('/camera\nsensor_msgs/Image', 'data', 'green')],
        [2.9, 6.3, 9.8, 13.1], [2.5, 3.0, 2.4, 2.9])
    row(c[1], [('Chuyển ảnh\nrgb→BGR', 'plain', 'purple'), ('YOLOv8m\nletterbox 640×384', 'plain', 'purple'), ('Hộp: N×(xyxy,\nconf, lớp)', 'data', 'purple'),
               ('ByteTrack\n+ FlowCounter', 'plain', 'purple'), ('JSON: N, q, q₆₀\n≈ 0,4 kB · 1 Hz', 'data', 'purple')],
        [2.7, 5.5, 8.4, 11.2, 14.0], [2.2, 2.6, 2.4, 2.4, 2.5])
    row(c[2], [('Chuyển ảnh\n+ YOLOv8m', 'plain', 'orange'), ('JPEG q80\n≈ %s kB' % f'{jb:.0f}', 'data', 'orange'), ('base64 + gộp JSON\n(hộp, telemetry, số đếm)', 'plain', 'orange'),
               ('Gói frame\n≈ %s kB · ≤ 8/s' % f'{nb:.0f}', 'data', 'orange'), ('WebSocket\n→ Web: giải mã, vẽ', 'light', 'orange')],
        [2.6, 5.35, 8.5, 11.45, 14.3], [2.1, 2.0, 3.0, 2.2, 2.5])
    g1 = (ys[0] + hh + ys[1]) / 2
    arrow(ax, [(13.1, c[0] + h / 2 + 0.04), (13.1, g1), (0.62, g1), (0.62, c[1]), (1.58, c[1])])
    arrow(ax, [(0.62, c[1]), (0.62, c[2] + 0.0), (1.58, c[2])])
    g2 = (ys[1] + hh + ys[2]) / 2
    arrow(ax, [(14.0, c[1] + h / 2 + 0.04), (14.0, g2), (8.7, g2), (8.7, c[2] - h / 2 - 0.03)])
    lab(ax, 11.3, g2 - 0.0, 'số đếm', fs=9.5, w=1.0)
    sv(fig, '03_so_do_luong_du_lieu')


# ------------------------------------------------------------------ 04 ma trận nhầm lẫn
def confusion():
    cm = json.load(open(f'{HERE}/confusion.json'))
    names = ['Người', 'Ô tô', 'Xe máy', 'Xe buýt', 'Xe tải', 'Nền']
    def draw(ax, M, title, big=False):
        M = np.array(M).T            # hàng = thật, cột = dự đoán  (nguồn: hàng = dự đoán, cột = thật)
        tot = M.sum(axis=1, keepdims=True); N = np.divide(M, tot, out=np.zeros_like(M), where=tot > 0)
        ax.imshow(N, cmap='Blues', vmin=0, vmax=1)
        for i in range(6):
            for j in range(6):
                if M[i, j] == 0 or (i == 5 and j == 5):
                    continue
                ax.text(j, i, f'{int(M[i, j])}', ha='center', va='center', fontsize=15 if big else 11.5,
                        color='white' if N[i, j] > 0.55 else NAVY, fontweight='bold')
        ax.set_xticks(range(6)); ax.set_yticks(range(6))
        ax.set_xticklabels(names, rotation=35, ha='right', fontsize=13 if big else 11); ax.set_yticklabels(names, fontsize=13 if big else 11)
        ax.set_xlabel('Dự đoán'); ax.set_ylabel('Thật'); ax.set_title(title, fontsize=15 if big else 13)
        ax.grid(False)
        for s in ax.spines.values(): s.set_visible(False)
    fig, axs = plt.subplots(1, 3, figsize=(17, 5.8))
    for ax, k in zip(axs, ('COCO gốc', '30 epoch', '50 epoch')):
        draw(ax, cm[k], k)
    fig.suptitle('Ma trận nhầm lẫn trên tập test (300 ảnh): số đối tượng, màu = tỉ lệ theo hàng · hàng “Nền” = phát hiện thừa, cột “Nền” = bỏ sót', fontsize=12.5, color=NAVY, y=1.0)
    fig.tight_layout(); fig.savefig(f'{OUT}/04a_ma_tran_nham_lan_3_mo_hinh.png', dpi=150, bbox_inches='tight'); plt.close(fig)
    fig, ax = plt.subplots(figsize=(7.2, 6.4))
    draw(ax, cm['50 epoch'], 'Mô hình 50 epoch (tập test)', big=True)
    fig.tight_layout(); fig.savefig(f'{OUT}/04b_ma_tran_nham_lan_50_epoch.png', dpi=150, bbox_inches='tight'); plt.close(fig)


# ------------------------------------------------------------------ 05 web · backend · API
def webapi():
    fig, ax = canvas(16, 8.3)
    band(ax, 0.3, 0.25, 4.6, 7.8, 'orange', 'Trình duyệt', '▣')
    band(ax, 11.1, 0.25, 4.6, 7.8, 'purple', 'Backend', '⚙')
    L = [('index.html + style.css\ngiao diện, ô lưu lượng', 'plain'), ('live.js\nWebSocket client, kiểm tra gói,\nvẽ hộp lên ảnh', 'plain'),
         ('controls.js\nnút bay, ô độ cao', 'plain'), ('app.js\nchế độ xem tệp / demo', 'plain')]
    for k, (t, s) in enumerate(L):
        node(ax, 2.6, 1.9 + k * 1.5, 4.0, 1.15, t, s, fs=11.2, kind='orange')
    R = [('CameraNode (luồng ROS)\n/camera → YOLOv8m → JPEG q80', 'plain'), ('telemetry_tasks (MAVSDK)\nđộ cao, chế độ bay, armed', 'plain'),
         ('handler WebSocket\nxác thực token, gửi frame, nhận lệnh', 'plain'), ('stream_setpoint\noffboard velocity 20 Hz', 'plain')]
    for k, (t, s) in enumerate(R):
        node(ax, 13.4, 1.9 + k * 1.5, 4.0, 1.15, t, s, fs=11.2, kind='purple')
    ax.text(8.0, 0.75, 'WebSocket v1 · ws://127.0.0.1:8765 · JSON', ha='center', fontsize=15, fontweight='bold', color=NAVY)
    msgs = [('→', 'auth', '{ type, protocol: 1, token }'), ('←', 'hello', '{ protocol, source, topic, model, telemetry }'),
            ('←', 'frame', '{ seq, timestamp, image (JPEG base64), detections[], telemetry, traffic }'), ('←', 'status', '{ camera_fresh: false, message }'),
            ('→', 'flight_command', '{ action: forward · backward · left · right · up · down · yaw_* · hold }'),
            ('→', 'set_altitude', '{ altitude_m: 4 – 35 }'), ('←', 'command_result', '{ request_id, message }')]
    for k, (d, n, body) in enumerate(msgs):
        y = 1.75 + k * 0.98
        x0, x1 = 5.0, 11.0
        arrow(ax, [(x0, y), (x1, y)] if d == '→' else [(x1, y), (x0, y)], color=ORANGE if d == '→' else PAL['purple'][0], lw=2.2)
        ax.text(8.0, y - 0.4, n, ha='center', fontsize=12.5, fontweight='bold', color=INK)
        ax.text(8.0, y + 0.28, body, ha='center', fontsize=8.6, color=MUTED)
    ax.text(15.7, 8.25, '', fontsize=1)
    chip(ax, 13.4, 7.62, 4.2, 0.4, 'ROS 2 /camera, /traffic/counts  ·  MAVSDK ↔ PX4', 'purple', fs=9.3)
    sv(fig, '05_web_backend_api')


# ------------------------------------------------------------------ 06 hạn chế → hướng cải thiện
def limits():
    fig, ax = canvas(16, 8.3)
    rows = [('Đếm thiếu xe máy\nrecall 0,59 (33/80 bỏ sót)', 'lưu lượng q thấp hơn thật 21 %', 'Tách lỗi phát hiện / theo vết;\nthử conf thấp hơn, MIN_HITS = 2, imgsz lớn hơn'),
            ('UAV phải đứng yên,\nvùng đếm cố định trong ảnh', 'không đếm được khi đang bay', 'Chiếu về mặt phẳng đường (homography),\nđịnh nghĩa vùng đếm trên mặt đất'),
            ('Ground truth chỉ 1 kịch bản\n120 s, 16 xe tuần hoàn', 'khoảng tin cậy chỉ tham khảo', 'Chạy nhiều lần; đổi vị trí, độ cao,\nmật độ xe'),
            ('Huấn luyện và đánh giá\nchỉ trên mô phỏng', 'chưa biết hiệu năng trên ảnh thật', 'Thu thập ảnh UAV thật, đánh giá lại,\ntinh chỉnh tiếp'),
            ('YOLO chạy 2 lần trên cùng khung;\nbackend 4,3 gói/s', 'lãng phí GPU, FPS thấp', 'Gộp bộ đếm vào backend;\nthử TensorRT / ONNX, đo lại FPS'),
            ('Chưa đo độ trễ Gazebo → /camera\nvà phía trình duyệt', 'độ trễ thật lớn hơn 116 ms', 'Gắn nhãn thời gian tại nguồn ảnh\nvà ở bước vẽ')]
    for x, t in ((2.75, 'Hạn chế (đã đo hoặc đã biết)'), (7.9, 'Hệ quả'), (13.1, 'Hướng cải thiện')):
        ax.text(x, 0.4, t, ha='center', fontsize=15, fontweight='bold', color=NAVY)
    for k, (a, b, c) in enumerate(rows):
        y = 1.55 + k * 1.1
        node(ax, 2.75, y, 4.7, 0.9, a, 'warn', fs=11.5)
        node(ax, 7.9, y, 4.2, 0.9, b, 'gray', fs=11.2)
        node(ax, 13.1, y, 5.1, 0.9, c, 'result', fs=10.8, kind='green')
        arrow(ax, [(5.12, y), (5.77, y)]); arrow(ax, [(10.02, y), (10.5, y)])
    sv(fig, '06_han_che_huong_cai_thien')


# ------------------------------------------------------------------ 07 điều khiển UAV
def control():
    fig, ax = canvas(16, 8.0)
    bx, bw = 0.3, 15.4
    ys = [0.25, 2.8, 5.35]; hh = 2.2
    band(ax, bx, ys[0], bw, hh, 'green', 'Bàn phím → MAVSDK (chế độ Position / Altitude)', '⌨')
    band(ax, bx, ys[1], bw, hh, 'purple', 'Web → Offboard (vận tốc theo thân)', '▣')
    band(ax, bx, ys[2], bw, hh, 'orange', 'Gimbal (camera 2 trục)', '◎')
    c = [y + 1.45 for y in ys]; h = 1.05
    def row(cy, items, kind):
        xs = [2.3, 6.2, 10.3, 14.0]; ws = [3.1, 3.6, 3.7, 2.9]
        for (t, sty), x, w in zip(items, xs, ws):
            node(ax, x, cy, w, h, t, sty, fs=10.2, kind=kind)
        for i in range(3):
            arrow(ax, [(xs[i] + ws[i] / 2 + 0.04, cy), (xs[i + 1] - ws[i + 1] / 2 - 0.03, cy)])
    row(c[0], [('Phím ↑ ↓ ← →, w s, a d\nr arm · l hạ cánh · h/p/o', 'data'), ('roll, pitch, yaw ∈ {−0,5; 0; 0,5}\nthrottle ∈ {0; 0,5; 1}', 'plain'),
               ('set_manual_control_input\nchu kỳ 0,1 s · UDP 14540', 'plain'), ('PX4\nPosition / Altitude / Hold', 'hero')], 'green')
    row(c[1], [('Nút bay trên web\nflight_command', 'data'), ('v = (2 | 0 | −2 | 1,5) m/s\nyaw ±30 °/s · giữ 0,6 s', 'plain'),
               ('VelocityBodyYawspeed\nsetpoint 20 Hz', 'plain'), ('PX4 OFFBOARD\n(dừng = vận tốc 0)', 'hero')], 'purple')
    row(c[2], [('Phím j k (pitch)\nn m (yaw)', 'data'), ('pitch ∈ [−0,5; 1,57] rad\nyaw ∈ [−1,57; 1,57] · bước 0,05', 'plain'),
               ('gz topic gz.msgs.Double\n/gimbal/cmd_pitch · cmd_yaw', 'plain'), ('JointPositionController\ntrong Gazebo', 'hero')], 'orange')
    ax.text(8.0, c[1] + 0.95, 'Độ cao: set_altitude → goto_location(lat, lon, h), 4 ≤ h ≤ 35 m · lên/xuống dừng khi |Δh| ≥ 1 − 0,25 m', ha='center', fontsize=10.2, color=MUTED, fontweight='bold', zorder=6)
    sv(fig, '07_dieu_khien_uav')


if __name__ == '__main__':
    block_diagram(); interaction(); dataflow(); confusion(); webapi(); limits(); control()
    print(sorted(os.listdir(OUT)))
