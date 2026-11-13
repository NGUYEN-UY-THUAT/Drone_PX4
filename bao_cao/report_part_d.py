"""Các slide biểu đồ và sơ đồ quy trình (ảnh sinh bởi measure/fig_diagrams.py và measure/fig_charts.py)."""
import os
import struct

from report_lib import *
from report_lib import _n

F = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'measure', 'figs')
M = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'measure')
_live = json.load(open(f'{M}/live_probe.json'))
_gt = json.load(open(f'{M}/gt_result.json'))
_e2e = sorted((x['tr'] - x['t_rx']) * 1e3 for x in _live)


def _c(x, d=1):
    return f'{x:.{d}f}'.replace('.', ',')


def png_size(path):
    with open(path, 'rb') as f:
        h = f.read(24)
    return struct.unpack('>II', h[16:24])


def fig_slide(title, section, img, points, max_h=4.9, notes=None, size=13):
    """Ảnh căn giữa (tối đa 12,1 x max_h in), bên dưới là các ý rút ra."""
    s = new_slide(title, section, notes)
    pw, ph = png_size(f'{F}/{img}.png')
    w = 12.1
    h = w * ph / pw
    if h > max_h:
        h, w = max_h, max_h * pw / ph
    x = (SW - w) / 2
    s.shapes.add_picture(f'{F}/{img}.png', Inches(x), Inches(1.4), Inches(w), Inches(h))
    bullets(s, 0.6, 1.4 + h + 0.12, 12.1, 7.0 - (1.4 + h + 0.12), points, size=size, gap=3)
    return s


# 1. Quy trình runtime
fig_slide('Sơ đồ hệ thống: quy trình từ mô phỏng đến giao diện web', '4 · Các sơ đồ', 'wf_runtime', [
    'Ba giai đoạn: thu ảnh từ mô phỏng, nhận diện + theo vết + đếm, hiển thị và điều khiển. Thời gian ghi trên mỗi khối là trung bình đo độc lập (bench.json).',
    'YOLOv8m là khối nặng nhất (30,1 ms); theo vết và đếm cộng lại dưới 1 ms. Độ trễ đầu cuối 116 ms (trung bình) đo khi cả hệ thống chạy.',
], max_h=4.3)

# 2. Quy trình huấn luyện
fig_slide('Quy trình huấn luyện, kiểm định và kiểm thử mô hình', '7 · Kết quả đánh giá', 'wf_training', [
    'Dữ liệu sinh tự động từ Gazebo (nhãn lấy từ bbox camera), tách train 6371 / val 1163 / test 300 ảnh; tập test dùng seed khác, không tham gia huấn luyện.',
    'Chọn best.pt theo chỉ số trên tập val; số cuối cùng báo cáo trên tập test: mAP50 = 0,982, mAP50–95 = 0,876 (mô hình 50 epoch).',
], max_h=4.3)

# 3. Đường cong huấn luyện (50 epoch, Colab T4)
fig_slide('Quá trình huấn luyện 50 epoch (Colab T4, batch 16)', '7 · Kết quả đánh giá', 'c_training', [
    'mAP50 trên tập val đã đạt 0,928 ở epoch 1 và hội tụ ở 0,976; mAP50–95 tăng từ 0,627 lên 0,869 (best.pt = epoch 49). Tổng thời gian huấn luyện ≈ 1 giờ 56 phút.',
    'Loss val trùng với loss train ở cuối quá trình (box 0,457 so với 0,460): không có dấu hiệu quá khớp. Đường chấm là mAP50 của YOLOv8m COCO gốc (0,402).',
], max_h=3.9)

# 4. So sánh mô hình
fig_slide('So sánh mô hình: COCO gốc, 30 epoch, 50 epoch', '7 · Kết quả đánh giá', 'c_models', [
    'Xe máy cải thiện mạnh nhất (mAP50–95 0,326 → 0,882); lớp “người” vẫn yếu nhất (0,648) do vật thể nhỏ.',
    'Radar: mọi chỉ số đều tăng; precision tăng từ 0,482 lên 0,981.',
], max_h=4.3)

# 5. Quy trình đánh giá đếm
fig_slide('Quy trình đánh giá độ chính xác đếm', '7 · Kết quả đánh giá', 'wf_counteval', [
    'Hai nhánh độc lập cùng chạy 120 s mô phỏng: ground truth từ vị trí xe trong Gazebo và số đếm của hệ thống; sau đó ghép Hungarian theo thời gian, cùng chiều (|Δt| ≤ 1 s).',
    'Phân loại lớp không dùng để ghép, nên độ chính xác phân loại (135/135) được đánh giá độc lập với việc ghép cặp.',
], max_h=4.3)

# 6. Tích luỹ
fig_slide('Số xe tích luỹ theo thời gian: hệ thống so với ground truth', '7 · Kết quả đánh giá', 'c_cumulative', [
    f'Hai đường tăng song song: hệ thống đếm {_gt["counted"]} / {_gt["gt"]} xe, chênh lệch tăng đều theo tỉ lệ (≈ 21%), không tăng vọt ở thời điểm nào, nên là sai số hệ thống chứ không phải do trôi dần.',
    'Vạch đỏ (xe bỏ sót) tập trung ở hàng “Xe máy”; xe buýt không bỏ sót xe nào. Nguyên nhân (phát hiện hay theo vết) chưa được tách riêng.',
], max_h=4.6)

# 7. Theo lớp
fig_slide('Kết quả đếm theo lớp xe', '7 · Kết quả đánh giá', 'c_counting', [
    'Recall: ô tô 57/60, xe buýt 10/10, xe tải 21/23, xe máy chỉ 47/80 (0,588). 33 trong 38 xe bỏ sót là xe máy.',
    'Khoảng tin cậy Wilson 95% của xe máy (≈ 0,48–0,69) không chứa mức recall của ô tô: khác biệt giữa các lớp không phải do ngẫu nhiên với cỡ mẫu này.',
], max_h=4.5)

# 8. Lưu lượng
fig_slide('Lưu lượng theo từng khoảng 15 s và theo chiều', '7 · Kết quả đánh giá', 'c_flow', [
    'Ở cả 8 khoảng 15 s hệ thống đều đếm ít hơn ground truth (xấp xỉ 15–19 so với 19–26 xe); chiều ← và → đều thiếu (76/92 và 59/81).',
    f'Lưu lượng trung bình: đếm {_c(_gt["q_cnt"])} xe/phút so với thật {_c(_gt["q_gt"])} (−21%). Cột “↓” là 1 lần đếm thừa (xe máy, t = 183,15 s).',
], max_h=3.9)

# 9. Thời gian từng công đoạn
fig_slide('Thời gian xử lý: từng công đoạn và theo cấu hình', '8 · Thời gian xử lý', 'c_latency', [
    'YOLO chiếm ≈ 82% tổng thời gian nhánh độc lập (30,06 / 36,55 ms); theo vết + đếm < 1 ms. Giảm imgsz 640 → 480 còn 21,2 ms (≈ 47 FPS), đổi lại độ chính xác chưa đo.',
    'FP16 chậm hơn FP32 (134,4 so với 31,9 ms), chưa xác định nguyên nhân; chạy CPU 207 ms (≈ 5 FPS).',
], max_h=4.3)

# 10. Độ trễ đầu cuối
fig_slide('Độ trễ đầu cuối: phân bố và thành phần', '8 · Thời gian xử lý', 'c_e2e', [
    f'{len(_e2e)} gói đo: trung vị {_c(_e2e[len(_e2e) // 2], 0)} ms, p95 {_c(_e2e[int(.95 * len(_e2e))], 0)} ms, lớn nhất {_c(_e2e[-1], 0)} ms; đuôi ngắn (không có gói trễ quá 180 ms).',
    'Phần xử lý trong backend chiếm khoảng 2/3 độ trễ; phần còn lại là base64, JSON, hàng đợi 50 ms và truyền WebSocket. Chưa đo phần Gazebo → /camera và giải mã trong trình duyệt.',
], max_h=3.9)

# 11. Thực nghiệm độ phức tạp
fig_slide('Kiểm chứng thực nghiệm: thời gian theo số hộp và kích thước ảnh', '9 · Độ phức tạp', 'c_scaling', [
    'ByteTrack: thời gian tăng gần tuyến tính theo số hộp N trong khoảng 5–400 (hồi quy R² = 0,997): ≈ 0,08 ms mỗi hộp. Ở mật độ giao thông thực tế (vài chục hộp) chỉ khoảng 1–4 ms.',
    'YOLOv8m: chỉ có hai điểm đo (imgsz 480 và 640), nên chỉ kết luận thời gian tăng theo số điểm ảnh đầu vào; thời gian không phụ thuộc kích thước ảnh gốc (1280×720 cho 29,8 ms, 1920×1080 cho 29,3 ms).',
], max_h=4.2)

# 13. Lưu đồ đếm (thay lưu đồ cũ)
fig_slide('Lưu đồ thuật toán đếm theo vùng (FlowCounter)', '4 · Các sơ đồ', 'wf_counter', [
    'Chỉ đếm khi track từng nằm ngoài vùng: track xuất hiện sẵn trong vùng (hoặc ID mới sau khi mất vết) không bao giờ được đếm, nên đổi ID không gây đếm đôi.',
    'Lớp lấy theo đa số phiếu trên cả track; hộp dùng là hộp phát hiện khớp (không phải hộp Kalman); chiều = dịch chuyển tâm trên 15 điểm gần nhất; thời gian lấy theo stamp ảnh nên không phụ thuộc RTF.',
], max_h=4.3)

# 12. KPI
fig_slide('Tổng hợp các chỉ số chính', 'Kết luận', 'c_kpi', [
    'Phát hiện tốt trên miền mô phỏng (mAP50 0,982); đếm chính xác khi đã đếm (precision 0,993) nhưng thiếu 22% xe, chủ yếu xe máy, nên lưu lượng thấp hơn thật 21%.',
    'Hệ thống thời gian thực mềm: YOLO ≈ 31 FPS khi chạy riêng, nhưng camera mô phỏng chỉ đạt 11,7 Hz do RTF 0,38; độ trễ đầu cuối 116 ms.',
], max_h=4.5)

# ghi chú nguồn biểu đồ trên slide phụ lục (slide gốc số 31)
tb(prs.slides[30], 0.6, 6.92, 11.4, 0.3,
   'Sơ đồ và biểu đồ: python3 measure/fig_diagrams.py && python3 measure/fig_charts.py → measure/figs/*.png, rồi python3 bao_cao/make_report.py.',
   size=10, color=MUTED)
