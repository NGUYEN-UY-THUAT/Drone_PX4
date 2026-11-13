"""Slide 19-31: kết quả, thời gian xử lý, độ phức tạp, realtime, phụ lục. Số liệu đọc từ measure/*.json."""
import math
import os

from report_lib import *

M = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'measure')
bench = json.load(open(f'{M}/bench.json'))
live = json.load(open(f'{M}/live_probe.json'))
gt = json.load(open(f'{M}/gt_result.json'))
trk = json.load(open(f'{M}/bench_tracker.json'))


def f1(x, d=1):
    return f'{x:.{d}f}'.replace('.', ',')


def wilson(k, n, z=1.96):
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return c - h, c + h


def pctl(v, q):
    v = sorted(v)
    return v[min(len(v) - 1, int(q * len(v)))]


def bar_chart(s, x, y, w, h, cats, series, colors, fmt='0.000', stacked=False, horizontal=False, labels=True,
              size=11, legend=True, vmax=None, title=None):
    cd = CategoryChartData()
    cd.categories = cats
    for name, vals in series:
        cd.add_series(name, [round(v, 3) for v in vals])
    if horizontal:
        t = XL_CHART_TYPE.BAR_STACKED if stacked else XL_CHART_TYPE.BAR_CLUSTERED
    else:
        t = XL_CHART_TYPE.COLUMN_STACKED if stacked else XL_CHART_TYPE.COLUMN_CLUSTERED
    gf = s.shapes.add_chart(t, Inches(x), Inches(y), Inches(w), Inches(h), cd)
    ch = gf.chart
    style_chart(ch, legend=legend and len(series) > 1, size=size)
    if title:
        ch.has_title = True
        ch.chart_title.text_frame.text = title
        ch.chart_title.text_frame.paragraphs[0].runs[0].font.size = Pt(size + 1)
        ch.chart_title.text_frame.paragraphs[0].runs[0].font.bold = True
    else:
        ch.has_title = False
    va = ch.value_axis
    va.has_major_gridlines = True
    va.major_gridlines.format.line.color.rgb = RGBColor(0xDD, 0xE4, 0xE9)
    va.format.line.fill.background()
    va.tick_labels.font.size = Pt(size)
    if vmax is not None:
        va.maximum_scale = vmax
    va.minimum_scale = 0
    ch.category_axis.tick_labels.font.size = Pt(size)
    ch.category_axis.format.line.color.rgb = MUTED
    pl = ch.plots[0]
    pl.gap_width = 60
    if stacked:
        pl.overlap = 100
    for i, ser in enumerate(pl.series):
        ser.format.fill.solid()
        ser.format.fill.fore_color.rgb = colors[i % len(colors)]
    if labels:
        pl.has_data_labels = True
        dl = pl.data_labels
        dl.number_format = fmt
        dl.number_format_is_linked = False
        dl.font.size = Pt(size - 1)
        if stacked:
            dl.position = XL_LABEL_POSITION.CENTER
            dl.font.color.rgb = WHITE
        else:
            dl.position = XL_LABEL_POSITION.OUTSIDE_END
    return ch


# ---------------------------------------------------------------- 19. Độ chính xác phát hiện (tổng)
s = new_slide('Độ chính xác phát hiện: tập test 300 ảnh mô phỏng', '7 · Kết quả đánh giá')
table(s, 0.6, 1.5, 6.4, [
    ['Mô hình', 'Ảnh train', 'P', 'R', 'mAP50', 'mAP50–95'],
    ['YOLOv8m COCO (gốc)', '—', '0,482', '0,535', '0,402', '0,323'],
    ['Tinh chỉnh 30 epoch', '2123', '0,984', '0,929', '0,971', '0,826'],
    ['Tinh chỉnh 50 epoch', '6371', '0,981', '0,947', '0,982', '0,876'],
], [2.4, 0.9, 0.7, 0.7, 0.8, 1.0], size=12, row_h=0.5)
bullets(s, 0.6, 3.75, 6.4, 3.2, [
    'Tập test: 300 ảnh, 1017 đối tượng, tách riêng (seed khác), không dùng khi huấn luyện; val 1163 ảnh.',
    'Đánh giá bằng finetune/evaluate.py, imgsz 640, 5 lớp; số của mô hình 50 epoch do tôi chạy lại trên máy này.',
    'Mô hình 30 epoch huấn luyện trên GTX 1650 (batch 4); 50 epoch trên Colab T4 (batch 16) với tập lớn gấp 3.',
    'Tốc độ khi đánh giá (batch 8): 28,0 ms suy luận + 0,3 ms tiền xử lý + 0,6 ms hậu xử lý mỗi ảnh.',
    'Kết quả đo trên miền mô phỏng: chưa phản ánh hiệu năng trên ảnh UAV thật.',
], size=13, gap=6)
bar_chart(s, 7.3, 1.45, 5.5, 5.4, ['COCO gốc', '30 epoch', '50 epoch'],
          [('mAP50', [0.402, 0.971, 0.982]), ('mAP50–95', [0.323, 0.826, 0.876])], [NAVY, ORANGE], fmt='0.000', vmax=1.1)

# ---------------------------------------------------------------- 20. Theo lớp
s = new_slide('Độ chính xác phát hiện theo lớp (mô hình 50 epoch)', '7 · Kết quả đánh giá')
table(s, 0.6, 1.5, 6.4, [
    ['Lớp', 'P', 'R', 'mAP50', 'mAP50–95'],
    ['Người', '0,944', '0,884', '0,960', '0,648'],
    ['Ô tô', '0,987', '0,985', '0,994', '0,960'],
    ['Xe máy', '0,996', '0,972', '0,995', '0,882'],
    ['Xe buýt', '0,986', '0,946', '0,978', '0,942'],
    ['Xe tải', '0,990', '0,946', '0,984', '0,948'],
], [1.6, 1.0, 1.0, 1.1, 1.3], size=12, row_h=0.46)
bullets(s, 0.6, 4.45, 6.4, 2.5, [
    'Lớp yếu nhất là người (mAP50–95 = 0,648): vật thể nhỏ, hình dạng thay đổi theo góc nhìn.',
    'Xe máy: recall 0,243 → 0,972 sau tinh chỉnh (mô hình gốc nhận nhầm thành “người”).',
    'Ngưỡng 0,25 (đánh giá Colab 27/10): 8 nhầm lớp, 13 bỏ sót, 27 phát hiện thừa nền (12 là “người”).',
], size=13, gap=6)
bar_chart(s, 7.3, 1.45, 5.5, 5.4, ['Người', 'Ô tô', 'Xe máy', 'Xe buýt', 'Xe tải'],
          [('COCO gốc', [0.046, 0.580, 0.326, 0.428, 0.237]), ('30 epoch', [0.542, 0.926, 0.839, 0.908, 0.917]),
           ('50 epoch', [0.648, 0.960, 0.882, 0.942, 0.948])], [MUTED, TEAL, ORANGE], fmt='0.00', vmax=1.15, size=10,
          title='mAP50–95 theo lớp')

# ---------------------------------------------------------------- 21. Phương pháp ground truth đếm
s = new_slide('Đánh giá độ chính xác đếm: đối chiếu với vị trí xe thật trong Gazebo', '7 · Kết quả đánh giá')
bullets(s, 0.6, 1.45, 6.2, 5.5, [
    [('Bố trí. ', {'bold': True}), ('UAV bay offboard tới (288,3; −161,9), cao 16,8 m, pitch 45°, hướng camera vuông góc với đường; đứng yên suốt phép đo.', {})],
    [('Ghi dữ liệu. ', {'bold': True}), ('Pose của 16 xe và của camera lấy từ pose/info của Gazebo, 20 Hz, 2152 mẫu trong 120,1 s mô phỏng (cửa sổ tính từ lúc bộ đếm bắt đầu).', {})],
    [('Chiếu. ', {'bold': True}), ('Tâm xe (+0,8 m) chiếu lên ảnh bằng mô hình pinhole (f = 1398 px). Hình bên: chấm đỏ = tâm xe chiếu, khung xanh = vùng đếm; kiểm tra bằng mắt trên một khung.', {})],
    [('Sự kiện GT. ', {'bold': True}), ('Một xe tạo sự kiện khi tâm đi từ ngoài vào trong vùng đếm, cùng luật với bộ đếm. 16 xe chạy tuần hoàn nên một xe có thể tạo nhiều sự kiện.', {})],
    [('Ghép cặp. ', {'bold': True}), ('Hungarian theo thời gian, cùng chiều, |Δt| ≤ 1 s, không dùng lớp. TP = cặp khớp; FN = GT không có sự kiện đếm; FP = sự kiện đếm không có GT.', {})],
], size=14, gap=8)
s.shapes.add_picture(f'{M}/projection_check.jpg', Inches(7.1), Inches(1.6), width=Inches(5.6))
tb(s, 7.1, 4.75, 5.6, 1.2,
   'Kiểm tra phép chiếu: các chấm đỏ rơi trên thân xe (lệch ≈ 1 m dọc xe do gốc mô hình không nằm ở tâm). '
   'Sai lệch này tương ứng ≈ 0,1 s ở 10 m/s, nhỏ hơn dung sai ghép 1 s.', size=11, color=MUTED)

# ---------------------------------------------------------------- 22. Kết quả đếm
s = new_slide('Kết quả đếm: độ chính xác cao, đếm thiếu xe máy', '7 · Kết quả đánh giá')
lo_p, hi_p = wilson(gt['tp'], gt['counted'])
lo_r, hi_r = wilson(gt['tp'], gt['gt'])
table(s, 0.6, 1.5, 6.3, [
    ['Chỉ số (cửa sổ 120,1 s mô phỏng)', 'Giá trị'],
    ['Sự kiện ground truth (GT)', str(gt['gt'])],
    ['Số xe bộ đếm đưa ra (N)', str(gt['counted'])],
    ['Khớp (TP) / bỏ sót (FN) / thừa (FP)', f"{gt['tp']} / {gt['fn']} / {gt['fp']}"],
    ['Precision', f"{f1(gt['precision'], 3)}  (KTC 95 %: {f1(lo_p, 3)}–{f1(hi_p, 3)})"],
    ['Recall', f"{f1(gt['recall'], 3)}  (KTC 95 %: {f1(lo_r, 3)}–{f1(hi_r, 3)})"],
    ['F1', f1(gt['f1'], 3)],
    ['Sai số tổng (N − GT)/GT', f"−{f1(abs(gt['counted'] - gt['gt']) / gt['gt'] * 100)} %"],
    ['Lưu lượng q: GT / bộ đếm', f"{f1(gt['q_gt'])} / {f1(gt['q_cnt'])} xe/phút"],
    ['Phân loại đúng trong số khớp', f"{gt['cls_ok']}/{gt['tp']}  (100 %)"],
    ['Lệch thời gian đếm so với GT', f"{f1(gt['dt_mean'], 2)} ± {f1(gt['dt_std'], 2)} s"],
], [3.6, 2.7], size=12, row_h=0.43)
pc = gt['per_class']
cls = ['Ô tô', 'Xe máy', 'Xe buýt', 'Xe tải']
bar_chart(s, 7.2, 1.45, 5.6, 4.5, cls, [('Ground truth', [pc[c][0] for c in cls]), ('Bộ đếm', [pc[c][1] for c in cls])],
          [NAVY, ORANGE], fmt='0', vmax=95, title='Số xe theo lớp trong 120,1 s')
tb(s, 7.2, 6.0, 5.6, 0.95, 'Một kịch bản, 120 s, 16 xe tuần hoàn: các sự kiện không độc lập hoàn toàn, nên khoảng tin cậy chỉ mang tính tham khảo.',
   size=11, color=MUTED)

# ---------------------------------------------------------------- 23. Phân tích sai số, hiệu quả
s = new_slide('Phân tích sai số đếm và hiệu quả hệ thống', '7 · Kết quả đánh giá')
rec = [pc[c][2] / pc[c][0] for c in cls]
bar_chart(s, 0.6, 1.45, 5.6, 4.2, cls, [('Recall đếm', rec)], [TEAL], fmt='0.00', vmax=1.15, legend=False,
          title='Recall của bộ đếm theo lớp (TP/GT)')
tb(s, 0.6, 5.7, 5.6, 1.2, f"FN theo lớp: xe máy {pc['Xe máy'][0] - pc['Xe máy'][2]}, ô tô {pc['Ô tô'][0] - pc['Ô tô'][2]}, "
   f"xe tải {pc['Xe tải'][0] - pc['Xe tải'][2]}, xe buýt {pc['Xe buýt'][0] - pc['Xe buýt'][2]}. FP: 1 (xe máy).", size=12, color=MUTED)
tb(s, 6.5, 1.45, 6.2, 0.4, 'Nhận xét', size=16, bold=True, color=TEAL)
bullets(s, 6.5, 1.9, 6.2, 5.0, [
    f"Precision {f1(gt['precision'], 3)}: gần như không đếm thừa, nhờ luật “vào vùng” + MIN_HITS = 3 + loại ID mới sinh trong vùng.",
    f"Sai số là hệ thống, không ngẫu nhiên: N thấp hơn GT {f1(abs(gt['counted'] - gt['gt']) / gt['gt'] * 100)} %, gần như toàn bộ do xe máy (recall {f1(pc['Xe máy'][2] / pc['Xe máy'][0], 2)}).",
    'Phân loại không phải nguồn sai số: 135/135 xe khớp có đúng lớp.',
    'Chưa tách được nguyên nhân bỏ sót xe máy (phát hiện không ra, hay track bị đứt trước khi vào vùng). Giả thuyết: xe máy nhỏ (≈ 130 px) và nhanh; cần đo thêm recall phát hiện tại ngưỡng 0,3.',
    'Vì thiên lệch ổn định, q đo được có thể hiệu chỉnh theo lớp, nhưng cần kiểm tra lại trên kịch bản khác trước khi dùng.',
], size=13, gap=8)

# ---------------------------------------------------------------- 24. Thời gian từng công đoạn
s = new_slide('Thời gian xử lý từng công đoạn', '8 · Thời gian xử lý')
pl = bench['pipeline']
lm = lambda k: st.mean(x[k] for x in live)
lmed = lambda k: pctl([x[k] for x in live], 0.5)
lp95 = lambda k: pctl([x[k] for x in live], 0.95)
srv = [x['pre_ms'] + x['infer_ms'] + x['encode_ms'] for x in live]
table(s, 0.6, 1.5, 7.2, [
    ['Công đoạn (ms)', 'Độc lập: TV', 'p95', 'Hệ thống chạy: TV', 'p95'],
    ['Chuyển định dạng ảnh', f1(pl['convert']['med'], 2), f1(pl['convert']['p95'], 2), f1(lmed('pre_ms'), 2), f1(lp95('pre_ms'), 2)],
    ['YOLO (tiền xử lý + suy luận + hậu xử lý)', f1(pl['detect']['med'], 2), f1(pl['detect']['p95'], 2), f1(lmed('infer_ms'), 2), f1(lp95('infer_ms'), 2)],
    ['Theo vết (ByteTrack)', f1(pl['track']['med'], 2), f1(pl['track']['p95'], 2), 'không đo', ''],
    ['Đếm (FlowCounter)', f1(pl['count']['med'], 2), f1(pl['count']['p95'], 2), 'không đo', ''],
    ['JPEG (+ danh sách hộp)', f1(pl['jpeg']['med'], 2), f1(pl['jpeg']['p95'], 2), f1(lmed('encode_ms'), 2), f1(lp95('encode_ms'), 2)],
    ['base64', f1(pl['b64']['med'], 2), f1(pl['b64']['p95'], 2), 'không đo', ''],
    ['Tổng nhánh bộ đếm (chuyển + YOLO + vết + đếm)', f1(pl['convert']['med'] + pl['detect']['med'] + pl['track']['med'] + pl['count']['med'], 1), '', '', ''],
    ['Tổng nhánh backend (chuyển + YOLO + JPEG)', f1(pl['convert']['med'] + pl['detect']['med'] + pl['jpeg']['med'], 1), '', f1(pctl(srv, 0.5), 1), f1(pctl(srv, 0.95), 1)],
], [3.6, 1.0, 0.7, 1.3, 0.7], size=11, row_h=0.5)
tb(s, 0.6, 6.1, 7.2, 0.9, 'TV = trung vị. “Độc lập”: bench.py, một tiến trình, GPU rảnh, 150 khung. “Hệ thống chạy”: 195 khung đo qua WebSocket khi Gazebo, bộ đếm và backend chạy cùng lúc.',
   size=11, color=MUTED)
bar_chart(s, 8.0, 1.45, 4.8, 4.9, ['Độc lập', 'Hệ thống chạy'],
          [('Chuyển ảnh', [pl['convert']['mean'], lm('pre_ms')]), ('YOLO', [pl['detect']['mean'], lm('infer_ms')]),
           ('JPEG', [pl['jpeg']['mean'], lm('encode_ms')])], [MUTED, NAVY, ORANGE], fmt='0.0', stacked=True,
          title='Nhánh backend, trung bình (ms)', size=10)
tb(s, 8.0, 6.35, 4.8, 0.65, f"Khi chạy cùng Gazebo và bộ đếm, mỗi khung tốn ≈ {f1(sum([lm('pre_ms'), lm('infer_ms'), lm('encode_ms')]) / (pl['convert']['mean'] + pl['detect']['mean'] + pl['jpeg']['mean']), 1)}× so với chạy riêng.",
   size=11, color=MUTED)

# ---------------------------------------------------------------- 25. Độ trễ đầu cuối
s = new_slide('Độ trễ đầu cuối: từ ảnh vào ROS đến gói tới web', '8 · Thời gian xử lý')
e2e = [(x['tr'] - x['t_rx']) * 1e3 for x in live]
rest = [(x['tr'] - x['t_rx']) * 1e3 - (x['pre_ms'] + x['infer_ms'] + x['encode_ms']) for x in live]
table(s, 0.6, 1.5, 6.0, [
    ['Đại lượng (ms)', 'TB', 'TV', 'p95', 'Max'],
    ['Xử lý trong backend (chuyển + YOLO + JPEG)', f1(st.mean(srv)), f1(pctl(srv, .5)), f1(pctl(srv, .95)), f1(max(srv))],
    ['base64 + JSON + hàng đợi 50 ms + gửi', f1(st.mean(rest)), f1(pctl(rest, .5)), f1(pctl(rest, .95)), f1(max(rest))],
    ['Tổng: ROS nhận ảnh → client nhận gói', f1(st.mean(e2e)), f1(pctl(e2e, .5)), f1(pctl(e2e, .95)), f1(max(e2e))],
], [3.4, 0.7, 0.7, 0.7, 0.7], size=11, row_h=0.62)
bullets(s, 0.6, 4.2, 6.0, 2.8, [
    f'Số khung: {len(live)} trong {f1(live[-1]["tr"] - live[0]["tr"])} s → {f1((len(live) - 1) / (live[-1]["tr"] - live[0]["tr"]))} gói/s.',
    'Chưa đo: độ trễ Gazebo → /camera, thời gian giải mã JPEG và vẽ trong trình duyệt. Độ trễ thấy trên màn hình lớn hơn con số này.',
    'Hàng đợi 50 ms trong vòng phát (asyncio.sleep(0,05)) đóng góp trung bình ≈ 25 ms.',
], size=12, gap=6)
cd = CategoryChartData()
cd.categories = list(range(1, len(e2e) + 1))
cd.add_series('Độ trễ (ms)', [round(v, 1) for v in e2e])
gf = s.shapes.add_chart(XL_CHART_TYPE.LINE, Inches(6.9), Inches(1.45), Inches(5.9), Inches(5.4), cd)
ch = gf.chart
style_chart(ch, legend=False, size=10)
ch.has_title = True
ch.chart_title.text_frame.text = 'Độ trễ từng gói (ms) theo thứ tự gói'
ch.chart_title.text_frame.paragraphs[0].runs[0].font.size = Pt(11)
ch.chart_title.text_frame.paragraphs[0].runs[0].font.bold = True
ser = ch.plots[0].series[0]
ser.format.line.color.rgb = ORANGE
ser.format.line.width = Pt(1.5)
ser.smooth = False
from pptx.enum.chart import XL_TICK_LABEL_POSITION, XL_TICK_MARK
ch.category_axis.tick_labels.font.size = Pt(9)
ch.category_axis.tick_label_position = XL_TICK_LABEL_POSITION.LOW
ch.category_axis.major_tick_mark = XL_TICK_MARK.NONE
ch.value_axis.minimum_scale = 0
ch.value_axis.maximum_scale = 200
ch.value_axis.major_gridlines.format.line.color.rgb = RGBColor(0xDD, 0xE4, 0xE9)
from pptx.oxml.ns import qn
cax = ch.category_axis._element
for tag, val in (('c:tickLblSkip', '25'), ('c:tickMarkSkip', '25')):
    el = cax.makeelement(qn(tag), {'val': val})
    cax.append(el)

# ---------------------------------------------------------------- 26. Độ phức tạp lý thuyết
s = new_slide('Độ phức tạp tính toán của từng thành phần', '9 · Độ phức tạp')
table(s, 0.6, 1.5, 12.1, [
    ['Thành phần', 'Thời gian', 'Bộ nhớ', 'Ký hiệu / giá trị của hệ thống'],
    ['Chuyển ảnh, letterbox, JPEG', 'O(H·W)', 'O(H·W)', 'H·W = 1920×1080 = 2,07 M điểm ảnh; ảnh thô 6,22 MB'],
    ['Mạng YOLOv8m (tích chập)', 'O(Σ k²·C_in·C_out·h·w) ∝ số điểm ảnh vào S', 'O(P + Σ activation) = 25,9 M tham số ≈ 104 MB FP32', '78,9 GFLOPs @640×640; ≈ 47 GFLOPs @640×384 (tỉ lệ diện tích, ước lượng)'],
    ['Giải mã đầu ra', 'O(A·(4 + C))', 'O(A·(4 + C))', 'A = 80·48 + 40·24 + 20·12 = 5040 điểm, C = 80'],
    ['NMS', 'O(m²) xấu nhất', 'O(m)', 'm = số hộp qua ngưỡng 0,1; tối đa 300 hộp'],
    ['Kalman (dự đoán + cập nhật)', 'O(n·d³) = O(n)', 'O(n·d²)', 'n = số track; d = 8 (hằng số)'],
    ['Ma trận chi phí IoU', 'O(n·m)', 'O(n·m)', 'n track × m hộp'],
    ['Gán Hungarian (lapjv)', 'O(k³), k = max(n, m); 2 giai đoạn', 'O(k²)', 'k ≈ 5–20 trong cảnh thực'],
    ['FlowCounter', 'O(m) mỗi khung', 'O(15·n) lịch sử tâm', 'Mỗi sự kiện ghi 1 dòng CSV (mở/đóng file): O(1)'],
    ['Web (vẽ hộp, giải mã JPEG)', 'O(m + H·W)', 'O(H·W)', 'Canvas 1920×1080'],
], [2.6, 3.2, 2.9, 3.4], size=11, row_h=0.5)
tb(s, 0.6, 6.55, 12.1, 0.5, 'Tổng: T(khung) = O(H·W·P) + O(k³) + O(m²); số hạng mạng nơ-ron chiếm ưu thế (92 % thời gian đo).', size=13, bold=True, color=NAVY)

# ---------------------------------------------------------------- 27. Độ phức tạp thực nghiệm
s = new_slide('Kiểm chứng thực nghiệm: thời gian theo kích thước đầu vào và số hộp', '9 · Độ phức tạp')
keys = ['1920x1080 imgsz640 fp32 GPU', '1280x720 imgsz640 fp32 GPU', '1920x1080 imgsz480 fp32 GPU']
vals = [bench[k]['total']['med'] for k in keys]
bar_chart(s, 0.6, 1.45, 6.0, 3.9, ['1920×1080\nimgsz 640', '1280×720\nimgsz 640', '1920×1080\nimgsz 480'],
          [('ms/khung (trung vị)', vals)], [TEAL], fmt='0.0', legend=False, vmax=40, title='YOLOv8m trên GPU: thời gian một khung (ms)')
S640, S480 = 640 * 384, 480 * 288
b = (vals[0] - vals[2]) / (S640 - S480)
a = vals[0] - b * S640
bullets(s, 0.6, 5.4, 6.0, 1.6, [
    'Độ phân giải nguồn không ảnh hưởng (letterbox về imgsz): 1920×1080 và 1280×720 cùng ≈ 32 ms.',
    f'imgsz 640 → 480 (diện tích × {f1(S480 / S640, 2)}): thời gian × {f1(vals[2] / vals[0], 2)}; khớp hai điểm: t ≈ {f1(a)} + {b * 1e4:.2f}·10⁻⁴·S ms.',
], size=12, gap=4)
ns = sorted(int(k) for k in trk)
bar_chart(s, 6.9, 1.45, 5.9, 3.9, [str(n) for n in ns], [('ms/khung', [trk[str(n)] for n in ns])], [ORANGE], fmt='0.0',
          legend=False, vmax=38, title='ByteTrack: thời gian update theo số hộp n (ms)')
bullets(s, 6.9, 5.4, 5.9, 1.6, [
    f'Từ n = 5 đến 400 thời gian tăng gần tuyến tính ({f1(trk["400"] / 400, 3)} ms/hộp ở n = 400); số hạng O(k³) của lapjv chưa lộ ra trong dải này.',
    'Dữ liệu tổng hợp (xe chuyển động thẳng + nhiễu), không phải cảnh thực.',
], size=12, gap=4)

# ---------------------------------------------------------------- 28. Realtime
s = new_slide('Realtime: FPS và độ trễ', '10 · Realtime')
cap_counter = pl['convert']['med'] + pl['detect']['med'] + pl['track']['med'] + pl['count']['med']
cap_bridge = pl['convert']['med'] + pl['detect']['med'] + pl['jpeg']['med'] + pl['b64']['med']
span = live[-1]['tr'] - live[0]['tr']
table(s, 0.6, 1.5, 12.1, [
    ['Chỉ tiêu', 'Giá trị đo', 'Điều kiện đo', 'Nhận định'],
    ['Nguồn ảnh', '30,3 khung/s (sim) = 11,7 khung/s (thực); RTF 0,38', 'Cả hệ thống chạy, 15 s', 'Mô phỏng chạy chậm hơn thời gian thực'],
    ['Năng lực nhánh bộ đếm', f'{f1(cap_counter)} ms → ≈ {f1(1000 / cap_counter, 0)} khung/s', 'Độc lập, GPU rảnh', 'Đủ cho 30 khung/s, biên rất mỏng'],
    ['Năng lực nhánh backend', f'{f1(cap_bridge)} ms → ≈ {f1(1000 / cap_bridge, 0)} khung/s', 'Độc lập, GPU rảnh', 'Trần thiết kế MAX_FPS = 8'],
    ['Backend khi chạy cả hệ thống', f'{f1(st.mean(srv))} ms/khung (trần ≈ {f1(1000 / st.mean(srv), 1)} khung/s)', 'Gazebo + bộ đếm cùng chạy', 'Chậm gấp ≈ 2,2 lần chạy riêng'],
    ['Tốc độ khung tới web', f'{f1((len(live) - 1) / span)} gói/s', '45 s, 195 gói', 'Thấp hơn trần 8; nguyên nhân chưa tách'],
    ['Độ trễ ROS → web', f'TB {f1(st.mean(e2e), 0)} ms; p95 {f1(pctl(e2e, .95), 0)} ms; max {f1(max(e2e), 0)} ms', 'Như trên', 'Chưa gồm render Gazebo và vẽ trên trình duyệt'],
    ['Tần số tối thiểu để đếm đúng', 'f_min ≈ 3 khung/s (sim) theo ví dụ slide 17', 'MIN_HITS = 3, v = 10 m/s', 'Đạt: ≥ 11,7 khung/s thực = 30 khung/s sim'],
], [2.6, 3.9, 2.6, 3.0], size=13, row_h=0.62)
tb(s, 0.6, 6.55, 12.1, 0.5, 'Đếm dùng thời gian mô phỏng nên kết quả không phụ thuộc RTF; với UAV thật chạy 30 khung/s, năng lực 27–32 khung/s trên GTX 1650 chỉ vừa sát.',
   size=12, color=MUTED)

# ---------------------------------------------------------------- 29. Nút thắt và tối ưu
s = new_slide('Nút thắt và các phương án tối ưu', '10 · Realtime')
table(s, 0.6, 1.5, 12.1, [
    ['Phương án', 'Thời gian/khung', 'Khung/s tối đa', 'Trạng thái và nhận xét'],
    ['Hiện tại: imgsz 640, FP32, GPU', f"{f1(bench[keys[0]]['total']['med'])} ms", f1(1000 / bench[keys[0]]['total']['med'], 0), 'Đã đo. Suy luận chiếm 29,35/31,9 ms = 92 %'],
    ['imgsz 480', f"{f1(bench[keys[2]]['total']['med'])} ms", f1(1000 / bench[keys[2]]['total']['med'], 0), 'Đã đo tốc độ; chưa đánh giá lại mAP, nên cần kiểm tra lại độ chính xác trước khi dùng'],
    ['FP16 (half = True)', f"{f1(bench['1920x1080 imgsz640 fp16 GPU']['total']['med'])} ms", f1(1000 / bench['1920x1080 imgsz640 fp16 GPU']['total']['med'], 0), 'Đã đo: chậm gấp ≈ 4,2 lần trên GTX 1650 Max-Q với bản Ultralytics này; chưa rõ nguyên nhân, không dùng'],
    ['CPU (12 luồng)', f"{f1(bench['1920x1080 imgsz640 fp32 CPU']['total']['med'])} ms", f1(1000 / bench['1920x1080 imgsz640 fp32 CPU']['total']['med'], 0), 'Đã đo: không đáp ứng realtime'],
    ['Dùng chung một lần suy luận cho bộ đếm và backend', 'chưa đo', '—', 'Đề xuất: hiện cùng một khung được chạy YOLO hai lần ở hai tiến trình; gộp sẽ giảm ≈ một nửa tải GPU'],
    ['TensorRT / ONNX', 'chưa đo', '—', 'Đề xuất, chưa thử'],
], [3.5, 1.6, 1.4, 5.6], size=12, row_h=0.62)
tb(s, 0.6, 6.0, 12.1, 0.9, ['Kết luận: nút thắt là suy luận YOLO trên GPU nhỏ (4 GB) dùng chung với Gazebo; phần theo vết và đếm không đáng kể (< 1 ms).'],
   size=13, bold=True)

# ---------------------------------------------------------------- 30. Hạn chế
s = new_slide('Hạn chế và việc cần làm', 'Kết luận')
table(s, 0.6, 1.5, 12.1, [
    ['Hạn chế (đã đo hoặc đã biết)', 'Hệ quả', 'Việc cần làm'],
    ['Đếm thiếu xe máy: recall 0,59 (33/80 bỏ sót)', 'q thấp hơn thực tế 21 %', 'Tách lỗi phát hiện / theo vết; thử conf thấp hơn, MIN_HITS = 2, imgsz lớn hơn'],
    ['UAV phải đứng yên, vùng đếm cố định trong ảnh', 'Không đếm được khi đang bay', 'Chiếu về mặt phẳng đường (homography) và định nghĩa vùng đếm trên mặt đất'],
    ['Ground truth chỉ một kịch bản 120 s, 16 xe tuần hoàn', 'Khoảng tin cậy chỉ tham khảo', 'Chạy nhiều lần, đổi vị trí/độ cao, đổi mật độ xe'],
    ['Huấn luyện và đánh giá đều trên mô phỏng', 'Chưa biết hiệu năng trên ảnh thật', 'Thu thập ảnh UAV thật, đánh giá lại và tinh chỉnh'],
    ['YOLO chạy hai lần trên cùng khung; backend chỉ đạt 4,3 gói/s', 'Lãng phí GPU, FPS thấp', 'Gộp bộ đếm vào backend; đo lại FPS'],
    ['Chưa đo độ trễ Gazebo → /camera và phía trình duyệt', 'Độ trễ đầu cuối thực lớn hơn 116 ms', 'Gắn nhãn thời gian ở nguồn ảnh và ở bước vẽ'],
], [4.4, 3.2, 4.5], size=12, row_h=0.72)

# ---------------------------------------------------------------- 31. Phụ lục phương pháp đo
s = new_slide('Phụ lục: phương pháp đo và cách chạy lại', 'Phụ lục')
table(s, 0.6, 1.5, 12.1, [
    ['Phép đo', 'Script (thư mục measure/)', 'Điều kiện', 'Mẫu'],
    ['Thời gian công đoạn (độc lập)', 'bench.py → bench.json', 'GTX 1650 Max-Q; khung từ video_bay_nhan_dien.mp4 phóng 1920×1080; 10 khung khởi động', '150 khung/cấu hình'],
    ['Thời gian theo số hộp', 'bench_tracker.py → bench_tracker.json', 'Hộp tổng hợp, 60 khung mỗi n, bỏ 10 khung đầu', 'n = 5…400'],
    ['Độ trễ khi chạy hệ thống', 'ws_probe.py → live_probe.json; backend thêm t_rx, timing', 'Client WebSocket cùng máy; đồng hồ chung', '195 gói / 45 s'],
    ['Tốc độ ảnh nguồn', 'camrate.py', 'gz-transport, đếm stamp sim và thời gian thực', '175 khung / 15 s'],
    ['Ground truth đếm', 'hover.py, gt_record.py, proj.py, gt_analyze.py → gt_result.json', 'UAV offboard đứng yên; bộ đếm khởi động lại sau khi UAV vào vị trí; log counter_events.csv', '2152 mẫu pose; 120,1 s sim'],
    ['Độ chính xác phát hiện', 'finetune/evaluate.py', 'Tập test 300 ảnh, imgsz 640, 5 lớp', '1017 đối tượng'],
], [2.6, 3.7, 4.4, 1.4], size=12, row_h=0.7)
tb(s, 0.6, 6.55, 12.1, 0.5, 'Chạy lại: gõ start → bay tới vị trí bằng hover.py → gt_record.py và traffic_counter.py song song → gt_analyze.py <thư mục> gt.pkl counter_events.csv <t0> 1.0 kq.json.',
   size=11, color=MUTED)
