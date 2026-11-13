"""Slide 10-18: sơ đồ, luồng dữ liệu, công thức."""
from report_lib import *


def chain(s, y, items, x0=0.6, w=1.7, h=0.85, gap=0.45, fill=LIGHT, line=TEAL, size=12):
    xs = []
    for i, it in enumerate(items):
        x = x0 + i * (w + gap)
        box(s, x, y, w, h, it.split('\n'), fill=fill, line=line, size=size)
        xs.append(x)
        if i:
            arrow(s, x - gap + 0.02, y + h / 2, x - 0.02, y + h / 2, color=ORANGE, width=2.25)
    return xs


# ---------------------------------------------------------------- 10. Sơ đồ khối
s = new_slide('Sơ đồ khối hệ thống', '4 · Các sơ đồ')
tb(s, 0.6, 1.4, 6, 0.3, 'Luồng nhận diện và đếm', size=13, bold=True, color=TEAL)
box(s, 6.15, 1.75, 5.3, 1.3, '', fill=None, line=MUTED)
tb(s, 6.2, 1.76, 3.5, 0.28, 'traffic_counter.py', size=11, color=MUTED)
box(s, 0.6, 2.0, 1.4, 0.85, ['Camera', 'IMX214', '(Gazebo)'], size=11)
box(s, 2.3, 2.0, 1.4, 0.85, ['ros_gz_', 'bridge'], size=11)
box(s, 4.0, 2.0, 1.4, 0.85, ['/camera', 'Image'], size=11, fill=WHITE, line=TEAL)
box(s, 6.3, 2.1, 1.5, 0.7, ['YOLOv8m'], size=11)
box(s, 8.05, 2.1, 1.5, 0.7, ['ByteTrack'], size=11)
box(s, 9.8, 2.1, 1.55, 0.7, ['Đếm theo', 'vùng'], size=11)
box(s, 11.7, 2.0, 1.1, 0.85, ['/traffic', '/counts'], size=11, fill=WHITE, line=TEAL)
for x1, x2 in [(2.0, 2.3), (3.7, 4.0), (5.4, 6.3), (7.8, 8.05), (9.55, 9.8), (11.35, 11.7)]:
    arrow(s, x1, 2.425, x2, 2.425, color=ORANGE, width=2.25)
tb(s, 0.6, 3.45, 6, 0.3, 'Luồng hiển thị và điều khiển', size=13, bold=True, color=TEAL)
box(s, 4.0, 3.9, 3.0, 0.9, ['uav_bridge.py', 'YOLOv8m + JPEG + gộp số đếm'], size=11)
box(s, 8.0, 3.9, 2.0, 0.9, ['Web', '(canvas, ô lưu lượng)'], size=11)
arrow(s, 4.7, 2.85, 4.7, 3.9, color=ORANGE, width=2.25)
arrow(s, 12.25, 2.85, 12.25, 3.35, color=ORANGE, width=2.25)
arrow(s, 12.25, 3.35, 6.2, 3.35, color=ORANGE, width=2.25)
arrow(s, 6.2, 3.35, 6.2, 3.9, color=ORANGE, width=2.25)
arrow(s, 7.0, 4.1, 8.0, 4.1, color=ORANGE, width=2.25)
arrow(s, 8.0, 4.6, 7.0, 4.6, color=MUTED, width=2.25)
tb(s, 7.0, 3.78, 1.0, 0.3, 'frame', size=10, color=MUTED, align=PP_ALIGN.CENTER)
tb(s, 7.0, 4.62, 1.0, 0.3, 'lệnh', size=10, color=MUTED, align=PP_ALIGN.CENTER)
tb(s, 0.6, 5.1, 6, 0.3, 'Vòng điều khiển bay', size=13, bold=True, color=TEAL)
box(s, 8.0, 5.55, 2.0, 0.85, ['Web', 'lệnh bay'], size=11)
box(s, 5.3, 5.55, 2.2, 0.85, ['uav_bridge', 'MAVSDK offboard'], size=11)
box(s, 2.7, 5.55, 2.0, 0.85, ['PX4 SITL'], size=11)
box(s, 0.6, 5.55, 1.6, 0.85, ['UAV +', 'gimbal'], size=11)
arrow(s, 8.0, 5.97, 7.5, 5.97, color=MUTED, width=2.25)
arrow(s, 5.3, 5.97, 4.7, 5.97, color=MUTED, width=2.25)
arrow(s, 2.7, 5.97, 2.2, 5.97, color=MUTED, width=2.25)
arrow(s, 1.4, 5.55, 1.4, 2.85, color=MUTED, width=2.25, dash=True)
tb(s, 1.45, 4.1, 2.4, 0.5, 'thay đổi góc nhìn camera', size=10, color=MUTED)

# ---------------------------------------------------------------- 11. Sơ đồ luồng dữ liệu
s = new_slide('Sơ đồ luồng dữ liệu và kích thước dữ liệu từng bước', '4 · Các sơ đồ')
chain(s, 1.55, ['Ảnh rgb8\n1920×1080\n6,22 MB', 'ndarray BGR\n1080×1920×3\n(cvtColor)', 'Letterbox\n640×384, FP32\n÷255', 'Đầu ra YOLO\n(4+80) × 5040\nđiểm dự đoán'],
      w=2.6, h=1.15, gap=0.5, size=12)
tb(s, 0.6, 2.75, 12, 0.3, 'Giải mã + NMS → ByteTrack → đếm', size=12, bold=True, color=TEAL)
chain(s, 3.1, ['NMS (conf 0,1)\nhộp (x1,y1,x2,y2,\nconf, lớp) ≤ 300', 'ByteTrack\nthêm track id;\nhộp khớp theo id', 'FlowCounter\nsự kiện (t, id,\nlớp, chiều)', 'Tổng hợp\nJSON ≈ 0,4 kB\n1 Hz + CSV'],
      w=2.6, h=1.15, gap=0.5, size=12)
tb(s, 0.6, 4.3, 12, 0.3, 'Nhánh hiển thị (backend)', size=12, bold=True, color=TEAL)
chain(s, 4.65, ['JPEG chất lượng 80\n59 kB (cảnh thực đo)\n121 kB (video thử)', 'base64\n+33 % kích thước', 'Gói JSON frame\n≈ 80 kB/gói\n(đo, 4,3 gói/s)', 'Web: giải mã JPEG,\nvẽ hộp + ô lưu lượng'],
      w=2.6, h=1.15, gap=0.5, size=12)
tb(s, 0.6, 6.0, 12.1, 0.9,
   ['Tốc độ dữ liệu: ảnh thô 6,22 MB × 11,7 khung/s thực = 72,5 MB/s (187 MB/s theo thời gian mô phỏng 30 khung/s). '
    'Tới web: JPEG 59 kB × 4,3 gói/s ≈ 0,25 MB/s; sau base64 và JSON, 80 kB × 4,3 gói/s ≈ 0,34 MB/s.'], size=12, color=MUTED)

# ---------------------------------------------------------------- 12. Sơ đồ tuần tự
s = new_slide('Sơ đồ tuần tự: từ khung ảnh đến ô lưu lượng và lệnh bay', '4 · Các sơ đồ')
lanes = ['Gazebo', 'ros_gz_bridge', 'traffic_counter', 'uav_bridge', 'Web', 'PX4']
LX = [1.45, 3.4, 5.35, 7.3, 9.25, 11.2]
for x, nme in zip(LX, lanes):
    box(s, x - 0.85, 1.4, 1.7, 0.42, nme, fill=NAVY, color=WHITE, size=11, bold=True)
    c = s.shapes.add_connector(MSO_CONNECTOR.STRAIGHT, Inches(x), Inches(1.82), Inches(x), Inches(6.85))
    c.line.color.rgb = MUTED
    c.line.width = Pt(1)
    ln = c.line._get_or_add_ln()
    from lxml import etree
    d = etree.SubElement(ln, '{http://schemas.openxmlformats.org/drawingml/2006/main}prstDash')
    d.set('val', 'dash')
msgs = [(0, 1, 2.4, '1) Image 1920×1080, 30 Hz (sim)'),
        (1, 2, 2.85, '2) /camera (khung mới nhất)'),
        (1, 3, 3.25, '3) /camera'),
        (2, 3, 4.3, '5) /traffic/counts, 1 Hz'),
        (3, 4, 4.75, '6) frame JSON ≤ 8/s (ảnh+hộp+số đếm)'),
        (4, 3, 5.2, '7) flight_command'),
        (3, 5, 5.65, '8) setpoint offboard 20 Hz'),
        (5, 3, 6.1, '9) telemetry (độ cao, chế độ)'),
        (3, 4, 6.55, '1) command_result; frame kế tiếp mang độ cao mới')]
for a, b, y, lab in msgs:
    x1, x2 = LX[a], LX[b]
    arrow(s, x1, y, x2 + (0.03 if x2 < x1 else -0.03), y, color=ORANGE if a < b else TEAL, width=2)
    lo, hi = min(x1, x2), max(x1, x2)
    tb(s, lo + 0.05, y - 0.42, hi - lo - 0.1, 0.4, lab, size=10, color=NAVY, align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.BOTTOM)
box(s, 4.5, 3.45, 1.7, 0.42, ['4) YOLO → vết → đếm'], fill=LIGHT, line=TEAL, size=10)
box(s, 6.45, 3.45, 1.7, 0.42, ['YOLO → JPEG'], fill=LIGHT, line=TEAL, size=10)

# ---------------------------------------------------------------- 13. Lưu đồ thuật toán đếm
s = new_slide('Lưu đồ thuật toán đếm theo vùng (FlowCounter)', '4 · Các sơ đồ')
steps = [(1.45, 0.5, 'Nhận ảnh /camera; t = stamp ảnh (thời gian mô phỏng)', False),
         (2.07, 0.5, 'predict(conf = 0,1; lớp 0, 2, 3, 5, 7)', False),
         (2.69, 0.5, 'BYTETracker.update → (id, lớp, hộp phát hiện khớp)', False),
         (3.31, 0.62, 'Với mỗi track có conf ≥ 0,3: tâm c; lưu 15 tâm gần nhất; thêm phiếu lớp', False),
         (4.12, 0.62, 'id chưa đếm VÀ điểm trước nằm NGOÀI vùng VÀ số lần thấy ≥ 3 VÀ c TRONG vùng?', True),
         (4.93, 0.55, 'ĉ = lớp nhiều phiếu nhất; ĉ là xe (ô tô/xe máy/xe buýt/xe tải)?', True),
         (5.67, 0.55, 'N += 1; theo lớp, theo chiều; ghi CSV; id → đã đếm', False),
         (6.4, 0.5, 'Mỗi 1 s: publish JSON (N, q, q₆₀, ổn định?)', False)]
for y, h, t, dec in steps:
    box(s, 0.6, y, 5.6, h, t, fill=WHITE if dec else LIGHT, line=ORANGE if dec else TEAL, size=11)
for i in range(len(steps) - 1):
    y1 = steps[i][0] + steps[i][1]
    arrow(s, 3.4, y1, 3.4, steps[i + 1][0], color=MUTED, width=1.75)
box(s, 6.45, 4.18, 1.6, 0.5, 'Không → track kế', fill=None, size=10, color=MUTED)
arrow(s, 6.2, 4.43, 6.45, 4.43, color=MUTED, width=1.5)
box(s, 6.45, 4.97, 1.6, 0.5, 'Không → bỏ qua', fill=None, size=10, color=MUTED)
arrow(s, 6.2, 5.2, 6.45, 5.2, color=MUTED, width=1.5)
tb(s, 8.4, 1.45, 4.3, 0.35, 'Quyết định thiết kế', size=16, bold=True, color=TEAL)
bullets(s, 8.4, 1.9, 4.3, 5.0, [
    'Chỉ đếm khi track đã từng nằm ngoài vùng: track xuất hiện sẵn trong vùng (đầu phiên, hoặc ID mới sau khi mất vết) không bao giờ được đếm, nên đổi ID không gây đếm đôi.',
    'Lớp lấy theo đa số phiếu trên cả track, một khung nhận sai nhãn không làm đổi kết quả.',
    'Dùng hộp phát hiện khớp với track thay cho hộp Kalman, vì hộp Kalman trễ và co lại khi xe vào từ mép ảnh.',
    'Chiều: dịch chuyển tâm trên 15 điểm gần nhất; |Δ| < 4 px thì ghi “?”.',
    'T lấy theo stamp ảnh nên không phụ thuộc tốc độ chạy thực của mô phỏng.',
], size=13, gap=6)

# ---------------------------------------------------------------- 14. Bảng luồng dữ liệu
s = new_slide('Luồng dữ liệu: đầu vào → xử lý → đầu ra (kèm thời gian đo)', '5 · Luồng dữ liệu')
table(s, 0.6, 1.5, 12.1, [
    ['Công đoạn', 'Đầu vào', 'Xử lý', 'Đầu ra', 'Đo (trung vị)'],
    ['1. Thu ảnh', 'Cảnh Gazebo', 'Render camera IMX214', 'Image rgb8 1920×1080 (6,22 MB)', '30,3 Hz sim / 11,7 Hz thực'],
    ['2. Chuyển định dạng', 'msg.data (bytes)', 'frombuffer → reshape → RGB→BGR', 'ndarray 1080×1920×3 uint8', '0,76 ms'],
    ['3. Tiền xử lý', 'ndarray BGR', 'Letterbox 640×384, BGR→RGB, ÷255, tensor', 'Tensor FP32 1×3×384×640', '1,16 ms'],
    ['4. Suy luận', 'Tensor', 'YOLOv8m (backbone, neck, head)', '(4+80)×5040 điểm', '29,35 ms'],
    ['5. Hậu xử lý', 'Đầu ra thô', 'Lọc conf ≥ 0,1 + NMS', 'Hộp (x1,y1,x2,y2,conf,lớp)', '1,06 ms'],
    ['6. Theo vết', 'Hộp', 'Kalman + IoU + Hungarian', 'Track (id, hộp khớp)', '0,83 ms'],
    ['7. Đếm', 'Track', 'Luật vào vùng + bầu chọn lớp', 'Sự kiện (t, id, lớp, chiều); N, q', '0,02 ms'],
    ['8. Mã hóa hiển thị', 'ndarray BGR', 'JPEG q80 + base64', 'Chuỗi ≈ 80–160 kB', '4,69 + 0,17 ms'],
    ['9. Truyền & vẽ', 'Gói JSON', 'WebSocket → giải mã → canvas', 'Hiển thị', 'Chưa đo giải mã phía trình duyệt'],
], [1.9, 1.9, 3.4, 3.0, 2.0], size=11, row_h=0.5)
tb(s, 0.6, 6.55, 12.1, 0.6,
   'Số đo từ bench.py: 150 khung từ video_bay_nhan_dien.mp4 phóng lên 1920×1080, GTX 1650 Max-Q, GPU chỉ chạy tiến trình đo. '
   'Công đoạn 1 đo bằng gz-transport trong 15 s (175 khung).', size=11, color=MUTED)


from formula_lib import render


def card(s, x, y, w, h, title, lines, note=None, size=17, nh=0.85):
    """Thẻ công thức: tiêu đề, công thức (ảnh mathtext), ghi chú."""
    box(s, x, y, w, h, '', fill=LIGHT)
    tb(s, x + 0.12, y + 0.06, w - 0.24, 0.35, title, size=14, bold=True, color=TEAL)
    path, iw, ih = render(lines, size=size)
    note_h = nh if note else 0.1
    avail_w, avail_h = w - 0.3, h - 0.5 - note_h
    k = min(1.3, avail_w / iw, avail_h / ih)
    s.shapes.add_picture(path, Inches(x + 0.15), Inches(y + 0.5 + (avail_h - ih * k) / 2), Inches(iw * k), Inches(ih * k))
    if note:
        tb(s, x + 0.12, y + h - nh + 0.03, w - 0.24, nh - 0.05, note, size=11, color=MUTED, anchor=MSO_ANCHOR.BOTTOM)


SEC = '4 · Công thức toán học'
# ---------------------------------------------------------------- 15. Công thức: phát hiện
s = new_slide('Công thức: phát hiện và đánh giá', SEC)
card(s, 0.6, 1.5, 5.95, 2.55, 'IoU và hàm mất mát box',
     [r'$\mathrm{IoU}(A,B)=\frac{|A\cap B|}{|A\cup B|}$',
      r'$L_{CIoU}=1-\mathrm{IoU}+\frac{\rho^{2}(b,b_{gt})}{c^{2}}+\alpha v$'],
     'ρ: khoảng cách tâm, c: đường chéo hộp bao nhỏ nhất, v: sai khác tỉ lệ cạnh. IoU cũng là độ đo khớp hộp trong ByteTrack.')
card(s, 6.75, 1.5, 5.95, 2.55, 'Tổng hàm mất mát khi huấn luyện',
     [r'$L=7{,}5\,L_{CIoU}+0{,}5\,L_{BCE}+1{,}5\,L_{DFL}$'],
     'Hệ số mặc định của Ultralytics (box 7,5; cls 0,5; dfl 1,5). Đầu ra không neo: 5040 điểm dự đoán ở 640×384.')
card(s, 0.6, 4.25, 5.95, 2.65, 'Precision, Recall, F1',
     [r'$P=\frac{TP}{TP+FP}\qquad R=\frac{TP}{TP+FN}$', r'$F_1=\frac{2PR}{P+R}$'],
     'Dùng cho phát hiện (khớp hộp IoU ≥ 0,5) và cho độ chính xác đếm (TP là sự kiện đếm khớp ground truth).')
card(s, 6.75, 4.25, 5.95, 2.65, 'AP và mAP',
     [r'$AP=\int_{0}^{1}p(r)\,dr$', r'$mAP_{50}=\frac{1}{C}\sum_{c=1}^{C}AP_{c}@0{,}5$',
      r'$mAP_{50\text{-}95}=\frac{1}{10}\sum_{\tau}mAP@\tau,\ \ \tau=0{,}50;\,0{,}55;\,\ldots;\,0{,}95$'.replace(r'\text{-}', '-')],
     'C = 5 lớp. AP lấy theo nội suy 101 điểm của Ultralytics.', size=15)

# ---------------------------------------------------------------- 16. Công thức: theo vết
s = new_slide('Công thức: Kalman và ByteTrack', SEC)
card(s, 0.6, 1.5, 5.95, 2.75, 'Bộ lọc Kalman (vận tốc không đổi)',
     [r'$x^{-}=Fx,\qquad P^{-}=FPF^{T}+Q$', r'$K=P^{-}H^{T}\left(HP^{-}H^{T}+R\right)^{-1}$', r'$x=x^{-}+K\left(z-Hx^{-}\right)$'],
     'Trạng thái x = (cx, cy, a, h, vx, vy, va, vh), a = w/h. Độ lệch chuẩn nhiễu tỉ lệ theo chiều cao hộp: vị trí h/20, vận tốc h/160.', size=15)
card(s, 6.75, 1.5, 5.95, 2.75, 'Chi phí ghép và gán tối ưu',
     [r'$C_{ij}=1-\mathrm{IoU}\left(T_{i}^{-},D_{j}\right)$', r'$\min\ \sum_{i,j}C_{ij}X_{ij}\ \ \ \mathrm{s.t.}\ \ C_{ij}\leq0{,}8$'],
     'Hộp dự đoán T của track i so với hộp phát hiện D_j; X là phép gán, giải bằng lap.lapjv (Jonker–Volgenant).', size=15)
box(s, 0.6, 4.45, 5.95, 2.45, '', fill=LIGHT)
tb(s, 0.72, 4.51, 5.7, 0.35, 'ByteTrack hai giai đoạn', size=14, bold=True, color=TEAL)
bullets(s, 0.72, 4.95, 5.7, 1.2, ['Giai đoạn 1: D_high (conf ≥ 0,25) ghép với mọi track',
                                  'Giai đoạn 2: D_low (0,1 ≤ conf < 0,25) ghép với track còn lại',
                                  'Track mất quá 30 khung bị xóa'], size=14, gap=4)
tb(s, 0.72, 6.1, 5.7, 0.78, 'Giai đoạn 2 giữ lại xe bị che một phần (conf thấp), nên bộ đếm chạy predict với conf = 0,1.', size=11, color=MUTED, anchor=MSO_ANCHOR.BOTTOM)
rows = [['Số hộp n', '5', '20', '50', '100', '200', '400'], ['Thời gian (ms)', '0,60', '1,70', '3,68', '7,06', '14,66', '31,94']]
tb(s, 6.75, 4.45, 5.95, 0.35, 'Đo thời gian BYTETracker.update theo số hộp (trung vị, dữ liệu tổng hợp)', size=12, bold=True, color=TEAL)
table(s, 6.75, 4.95, 5.95, rows, [1.6, 0.8, 0.8, 0.8, 0.8, 0.8, 0.8], size=12, row_h=0.45)
tb(s, 6.75, 5.95, 5.95, 0.95, 'Quan hệ gần tuyến tính, ≈ 0,08 ms/hộp, trong khoảng 5–400 hộp. Cảnh thực tế có ≤ 20 hộp: ≈ 1,7 ms.', size=12, color=MUTED)

# ---------------------------------------------------------------- 17. Công thức: đếm
s = new_slide('Công thức: luật đếm và lưu lượng', SEC)
card(s, 0.6, 1.5, 5.95, 2.75, 'Vùng và điều kiện đếm',
     [r'$\mathrm{in}(c)\Leftrightarrow x_{1}W\leq c_{x}\leq x_{2}W\ \wedge\ y_{1}H\leq c_{y}\leq y_{2}H$',
      r'$\mathrm{count}(id)\Leftrightarrow\neg\mathrm{in}(c_{k-1})\wedge\mathrm{in}(c_{k})$',
      r'$\wedge\ \mathrm{hits}\geq3\ \wedge\ id\notin\mathrm{đã\ đếm}$'.replace(r'\mathrm{đã\ đếm}', r'\mathcal{C}')],
     'c = tâm hộp phát hiện khớp; C = tập id đã đếm; vùng mặc định (x1,y1,x2,y2) = (0,42; 0; 0,58; 1) tọa độ chuẩn hóa.', size=14)
card(s, 6.75, 1.5, 5.95, 2.75, 'Lớp và chiều',
     [r'$\hat{c}=\arg\max_{c}\sum_{k}\mathbf{1}\left[c_{k}=c\right]$', r'$\Delta=c_{k}-c_{k-14}$',
      r'$\mathrm{dir}=\mathrm{sign}(\Delta x)\ \mathrm{if}\ |\Delta x|\geq|\Delta y|\ \mathrm{else}\ \mathrm{sign}(\Delta y)$'],
     'Lớp = đa số phiếu trên cả track; chiều lấy trên tối đa 15 tâm gần nhất; max|Δ| < 4 px thì ghi “?”.', size=14)
card(s, 0.6, 4.45, 5.95, 2.45, 'Lưu lượng',
     [r'$q=\frac{60\,N}{T}\ \ (\mathrm{xe/phút}),\qquad T=t-t_{0}$', r'$q_{60}=\frac{60\,N_{60}}{\min(60,\,T)}$'],
     'T theo stamp ảnh (thời gian mô phỏng). T < 20 s: gắn nhãn “chưa ổn định” vì mỗi xe làm q dao động mạnh.', size=16)
card(s, 6.75, 4.45, 5.95, 2.45, 'Tần số khung hình tối thiểu (ví dụ minh họa)',
     [r'$f_{min}=\frac{\mathrm{MIN\_HITS}\cdot v}{L}=\frac{3\cdot10\ \mathrm{m/s}}{10\ \mathrm{m}}=3\ \mathrm{khung/s}$'],
     'v: tốc độ xe; L: đoạn đường nhìn thấy trước vùng đếm (giả định 10 m). Camera cho 30 khung/s theo thời gian mô phỏng.', size=16)

# ---------------------------------------------------------------- 18. Công thức: hình học camera
s = new_slide('Công thức: hình học camera và ground truth đếm', SEC)
card(s, 0.6, 1.5, 5.95, 2.55, 'Chiếu điểm 3D lên ảnh (pinhole)',
     [r'$f=\frac{W/2}{\tan(\mathrm{HFOV}/2)}=\frac{960}{\tan0{,}602}\approx1398\ \mathrm{px}$',
      r'$u=\frac{W}{2}-f\,\frac{y_{c}}{x_{c}},\qquad v=\frac{H}{2}-f\,\frac{z_{c}}{x_{c}}$'],
     'Hệ camera Gazebo: x phía trước, y trái, z lên; (x_c, y_c, z_c) = Rᵀ(P − t); chỉ chiếu khi x_c > 0,1 m.', size=15)
card(s, 6.75, 1.5, 5.95, 2.55, 'Tư thế camera trong thế giới',
     [r'$R=R_{model}\,R_{link}$', r'$t=p_{model}+R_{model}\,p_{link}+R\,p_{sensor}$'],
     'Lấy từ topic pose/info của Gazebo. p_sensor = (0,01233; −0,03; 0,01878) m trong camera_link.', size=16)
card(s, 0.6, 4.25, 5.95, 2.65, 'Độ phân giải mặt đất (GSD)',
     [r'$\mathrm{GSD}\approx\frac{d}{f}$', r'$d\approx20\ \mathrm{m}\ \Rightarrow\ \mathrm{GSD}\approx1{,}4\ \mathrm{cm/px}$'],
     'd là khoảng cách xiên từ camera đến điểm giữa ảnh (độ cao ≈ 14,5 m trên mặt đường, pitch 45°); ô tô 4 m ≈ 280 px, xe máy 1,9 m ≈ 130 px.', size=16)
card(s, 6.75, 4.25, 5.95, 2.65, 'Ground truth đếm và ghép cặp',
     [r'GT: $\neg\mathrm{in}(u_{k-1})\wedge\mathrm{in}(u_{k})$,  $(u,v)=\pi(p_{xe}+0{,}8\ \mathrm{m})$', r'$\mathrm{match:}\ \min\sum\left|t_{gt}-t_{cnt}\right|$'],
     'Ghép cùng chiều, |Δt| ≤ 1 s, thuật toán Hungarian; không dùng lớp nên độ chính xác phân loại được đánh giá độc lập với việc ghép.', size=14)
