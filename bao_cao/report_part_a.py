"""Slide 1-9: tiêu đề, mục lục, hệ thống, khối chức năng, tương tác."""
from report_lib import *
from report_lib import _n

# ---------------------------------------------------------------- 1. Tiêu đề
s = prs.slides.add_slide(BLANK)
_n[0] += 1
bg = s.background.fill
bg.solid()
bg.fore_color.rgb = NAVY
tb(s, 0.9, 1.7, 11.5, 1.6, 'Hệ thống giám sát và đếm lưu lượng giao thông bằng UAV', size=40, bold=True,
   color=WHITE, font=TITLE_FONT, name='Title')
tb(s, 0.9, 3.5, 11.5, 0.9, 'YOLOv8 + ByteTrack trên mô phỏng PX4 / Gazebo / ROS 2, giao diện web thời gian thực',
   size=20, color=RGBColor(0xCF, 0xDD, 0xE6))
tb(s, 0.9, 4.6, 11.5, 0.5, 'Báo cáo kỹ thuật: kiến trúc, thuật toán, đánh giá và hiệu năng', size=16, color=ORANGE, bold=True)
tb(s, 0.9, 6.0, 11.5, 0.9, ['Nguyễn Công Uy Thuật · Nguyễn Thái Hoàng',
                            'GVHD: TS. Nguyễn Văn Hiếu · PBL5, Trường Đại học Bách khoa – ĐH Đà Nẵng · 11/2026'],
   size=14, color=RGBColor(0xCF, 0xDD, 0xE6))

# ---------------------------------------------------------------- 2. Mục lục
s = new_slide('Nội dung báo cáo')
rows = [['#', 'Mục', 'Nội dung chính', 'Slide'],
        ['1', 'Hệ thống', 'Mục tiêu, công nghệ, kiến trúc tổng thể', '3–5'],
        ['2', 'Các khối chức năng', 'Danh sách khối, vào/ra, tham số', '6–7'],
        ['3', 'Sự tương tác', 'Kênh giao tiếp, giao thức WebSocket v1', '8–9'],
        ['4', 'Các sơ đồ', 'Sơ đồ khối, luồng dữ liệu, tuần tự, lưu đồ thuật toán đếm', '10–13'],
        ['5', 'Luồng dữ liệu', 'Đầu vào → xử lý → đầu ra, kích thước dữ liệu', '14'],
        ['6', 'Công thức toán học', 'IoU/mAP, Kalman + ByteTrack, luật đếm và lưu lượng, hình học camera', '15–18'],
        ['7', 'Kết quả đánh giá', 'Độ chính xác phát hiện, độ chính xác đếm (đối chiếu ground truth), hiệu quả', '19–23'],
        ['8', 'Thời gian xử lý', 'Thời gian từng công đoạn, độ trễ đầu cuối', '24–25'],
        ['9', 'Độ phức tạp', 'Phân tích lý thuyết và đo thực nghiệm', '26–27'],
        ['10', 'Realtime', 'FPS, độ trễ, nút thắt và tối ưu', '28–29'],
        ['', 'Kết luận', 'Hạn chế, việc cần làm; phụ lục phương pháp đo', '30–31']]
table(s, 0.6, 1.55, 12.1, rows, [0.5, 2.6, 8.0, 1.0], size=14, row_h=0.43)
tb(s, 0.6, 6.85, 11.3, 0.35,
   'Mọi con số trong báo cáo là số đo trên máy phát triển (xem phụ lục, thư mục measure/); không có số liệu ước lượng trừ khi ghi rõ.',
   size=11, color=MUTED)

# ---------------------------------------------------------------- 3. Mục tiêu
s = new_slide('Mục tiêu, phạm vi và ràng buộc kỹ thuật', '1 · Hệ thống')
tb(s, 0.6, 1.5, 6.0, 0.4, 'Mục tiêu', size=18, bold=True, color=TEAL)
bullets(s, 0.6, 1.95, 6.0, 3.6, [
    'Nhận diện 5 lớp (người, ô tô, xe máy, xe buýt, xe tải) trên ảnh camera gắn UAV.',
    'Đếm xe đi qua một vùng cố định trong ảnh; tính lưu lượng q = N/T (xe/phút) theo loại xe và chiều đi.',
    'Hiển thị ảnh, hộp nhận diện và lưu lượng trên web gần thời gian thực; điều khiển bay (độ cao, di chuyển) từ web.',
    'Chạy trên mô phỏng PX4 SITL + Gazebo; các khối ghép nối qua ROS 2 để thay nguồn ảnh bằng UAV thật.',
], size=15, gap=8)
tb(s, 7.0, 1.5, 5.7, 0.4, 'Ràng buộc và phạm vi kết luận', size=18, bold=True, color=TEAL)
table(s, 7.0, 1.95, 5.7, [
    ['Hạng mục', 'Giá trị'],
    ['GPU / CPU', 'GTX 1650 Max-Q 4 GB / 12 luồng'],
    ['Ảnh', '1920×1080 rgb8, 30 Hz thời gian mô phỏng'],
    ['Tốc độ mô phỏng', 'RTF ≈ 0,38 khi chạy toàn bộ hệ thống'],
    ['Điều kiện đếm', 'UAV đứng yên; vùng đếm cố định trong ảnh'],
    ['Dữ liệu huấn luyện', '6371 / 1163 / 300 ảnh mô phỏng (train/val/test)'],
    ['Phạm vi', 'Kết quả chỉ có giá trị trên miền mô phỏng'],
], [1.7, 3.6], size=12, row_h=0.5)

# ---------------------------------------------------------------- 4. Công nghệ
s = new_slide('Công nghệ sử dụng', '1 · Hệ thống')
table(s, 0.6, 1.5, 12.1, [
    ['Lớp', 'Công nghệ (phiên bản đo)', 'Vai trò trong hệ thống'],
    ['Mô phỏng', 'Gazebo Sim 8.15; world Sonoma raceway; camera IMX214 (HFOV 1,204 rad)', '16 xe + 2 người; ảnh 1920×1080; nhãn tự động cho tập huấn luyện'],
    ['Bay', 'PX4 SITL (x500_depth + gimbal 2 trục); MAVSDK-Python 3.17.2', 'Arm, offboard velocity/position, telemetry độ cao'],
    ['Middleware', 'ROS 2 Humble; ros_gz_bridge; Micro XRCE-DDS Agent (UDP 8888)', 'Chuyển gz.msgs.Image → sensor_msgs/Image (/camera); topic /fmu/*'],
    ['Nhận diện', 'Ultralytics 8.4.152; YOLOv8m (25,9 M tham số; 78,9 GFLOPs @640); PyTorch 2.6.0+cu124', 'Phát hiện 5 lớp COCO [0,2,3,5,7]; tinh chỉnh trên ảnh mô phỏng'],
    ['Theo vết', 'ByteTrack (BYTETracker của Ultralytics); bộ lọc Kalman XYAH; lap 0.5.13 (lapjv)', 'Gán ID ổn định cho từng xe giữa các khung hình'],
    ['Truyền', 'websockets 16.1.1; JSON + ảnh JPEG base64; token so sánh bằng hmac', 'Backend → web: ảnh, hộp, số đếm, telemetry; web → backend: lệnh bay'],
    ['Giao diện', 'HTML/JS thuần (canvas); http.server', 'Hiển thị, lọc lớp, ô lưu lượng, điều khiển'],
    ['Xử lý ảnh', 'OpenCV 5.0.0.93; NumPy 2.2.6', 'Chuyển định dạng, mã hóa JPEG, vẽ'],
], [1.4, 5.6, 5.1], size=12, row_h=0.56)

# ---------------------------------------------------------------- 5. Kiến trúc tổng thể
s = new_slide('Kiến trúc tổng thể', '1 · Hệ thống')
cols = [(0.6, 'Mô phỏng', ['Gazebo Sim\nworld + camera IMX214', 'PX4 SITL\nx500_depth + gimbal', 'traffic.py\n16 xe, 20 Hz']),
        (3.85, 'ROS 2', ['ros_gz_bridge\ngz.msgs.Image → /camera', 'Micro XRCE-DDS Agent\nUDP 8888, /fmu/*', 'Topic /traffic/counts\nstd_msgs/String, 1 Hz']),
        (7.1, 'Xử lý (GPU)', ['traffic_counter.py\nYOLOv8m + ByteTrack + đếm', 'uav_bridge.py\nYOLOv8m + MAVSDK\nWebSocket server', '']),
        (10.35, 'Giao diện', ['Trình duyệt\ncanvas, lọc lớp,\nô lưu lượng', 'Lệnh bay\nlên/xuống, tiến/lùi, xoay', ''])]
for x, head, items in cols:
    box(s, x, 1.5, 2.75, 0.45, head, fill=NAVY, color=WHITE, size=14, bold=True)
    box(s, x, 1.95, 2.75, 4.6, '', fill=LIGHT)
    yy = 2.1
    for it in items:
        if it:
            box(s, x + 0.12, yy, 2.51, 1.2, it.split('\n'), fill=WHITE, line=TEAL, size=12)
        yy += 1.4
for x1, y1, x2, y2, lab in [(3.35, 2.7, 3.85, 2.7, ''), (6.6, 2.7, 7.1, 2.7, ''), (9.85, 3.5, 10.35, 3.5, '')]:
    arrow(s, x1, y1, x2, y2, color=ORANGE, width=2.5)
tb(s, 0.6, 6.62, 11.3, 0.55,
   'Cổng: UDP 8888 (XRCE) · UDP 14540 (MAVSDK, backend) · WebSocket 127.0.0.1:8765 · HTTP 127.0.0.1:8000. '
   'Ảnh từ /camera đi vào hai tiến trình độc lập (bộ đếm và backend), mỗi tiến trình chạy YOLO riêng.',
   size=12, color=MUTED)

# ---------------------------------------------------------------- 6. Các khối chức năng
s = new_slide('Các khối chức năng', '2 · Các khối chức năng')
table(s, 0.6, 1.5, 12.1, [
    ['#', 'Khối', 'Triển khai', 'Đầu vào', 'Đầu ra', 'Chức năng'],
    ['1', 'Mô phỏng cảnh', 'Gazebo + traffic.py', 'Pose xe (set_pose_vector, 20 Hz)', 'Ảnh camera', '16 xe trên 4 làn, giữ khoảng cách an toàn (MIN_GAP 3 m, headway 1,2 s)'],
    ['2', 'UAV + gimbal', 'PX4 SITL, setup_gimbal.py', 'Lệnh offboard/MAVLink', 'Vị trí, độ cao, ảnh', 'Bay, giữ vị trí; gimbal 2 trục (pitch −0,5…1,57 rad)'],
    ['3', 'Cầu nối ảnh', 'ros_gz_bridge', 'gz.msgs.Image', '/camera (sensor_msgs/Image)', 'Chuyển ảnh từ Gazebo sang ROS 2'],
    ['4', 'Nhận diện', 'YOLOv8m best.pt', 'Ảnh BGR 1920×1080', 'Hộp, lớp, độ tin cậy', 'Phát hiện người/ô tô/xe máy/xe buýt/xe tải'],
    ['5', 'Theo vết + đếm', 'traffic_counter.py', 'Hộp từng khung', '/traffic/counts (JSON 1 Hz), CSV', 'ByteTrack gán ID; đếm khi tâm hộp đi từ ngoài vào vùng; tính q'],
    ['6', 'Backend', 'uav_bridge.py', '/camera, /traffic/counts, telemetry', 'Gói WebSocket', 'YOLO + JPEG + gộp số đếm + telemetry; nhận lệnh bay, đẩy xuống PX4'],
    ['7', 'Giao diện web', 'index.html, live.js, app.js, controls.js', 'Gói WebSocket', 'Hiển thị; lệnh bay', 'Vẽ ảnh + hộp, lọc lớp, ô Xe đã đếm / Lưu lượng q, điều khiển'],
], [0.4, 1.6, 2.3, 2.4, 2.4, 4.4], size=11, row_h=0.62)

# ---------------------------------------------------------------- 7. Tham số khối nhận diện & đếm
s = new_slide('Tham số của khối nhận diện, theo vết và đếm', '2 · Các khối chức năng')
table(s, 0.6, 1.5, 5.9, [
    ['Nhận diện (YOLOv8m)', 'Giá trị'],
    ['Trọng số', 'yolov8m_sim_50ep_colab/best.pt'],
    ['Lớp giữ lại', 'COCO 0, 2, 3, 5, 7'],
    ['Kích thước vào', '640 (letterbox 1920×1080 → 640×384)'],
    ['Ngưỡng tin cậy', '0,1 (bộ đếm); 0,25 mặc định (backend)'],
    ['Huấn luyện', '50 epoch, batch 16, Colab T4'],
    ['Tăng cường', 'fliplr/flipud 0,5; xoay 10°; scale 0,5; mosaic'],
], [2.2, 3.7], size=12, row_h=0.5)
table(s, 6.8, 1.5, 5.9, [
    ['Theo vết (ByteTrack)', 'Giá trị'],
    ['track_high_thresh', '0,25 (giai đoạn 1)'],
    ['track_low_thresh', '0,1 (giai đoạn 2)'],
    ['new_track_thresh', '0,25'],
    ['match_thresh', '0,8 (ngưỡng chi phí 1 − IoU)'],
    ['track_buffer', '30 khung'],
    ['Trạng thái Kalman', '(cx, cy, a, h, vx, vy, va, vh)'],
], [2.2, 3.7], size=12, row_h=0.5)
table(s, 0.6, 5.2, 12.1, [
    ['Đếm (FlowCounter)', 'Giá trị', 'Backend (uav_bridge)', 'Giá trị'],
    ['Vùng đếm', '[0,42; 0; 0,58; 1] (chuẩn hóa)', 'MAX_FPS', '8 (bỏ khung nếu < 125 ms từ khung trước)'],
    ['MIN_HITS / hộp tối thiểu', '3 khung / độ tin cậy ≥ 0,3', 'Ảnh gửi đi', 'JPEG chất lượng 80; STALE_S = 3 s'],
    ['Cửa sổ lưu lượng / ổn định', '60 s / T ≥ 20 s', 'Lệnh bay', 'SPEED 2 m/s; lên 2, xuống 1,5 m/s'],
], [2.6, 3.4, 2.0, 4.1], size=12, row_h=0.42)

# ---------------------------------------------------------------- 8. Kênh giao tiếp
s = new_slide('Kênh giao tiếp giữa các khối', '3 · Sự tương tác')
table(s, 0.6, 1.45, 12.1, [
    ['Từ → Đến', 'Kênh', 'Dữ liệu', 'Tần suất', 'Ghi chú'],
    ['traffic.py → Gazebo', 'gz service set_pose_vector', 'Pose_V (16 xe)', '20 Hz', 'Tốc độ thực phụ thuộc RTF'],
    ['Gazebo → ros_gz_bridge', 'gz topic …/IMX214/image', 'Image rgb8 1920×1080 (6,22 MB)', '30,3 Hz sim = 11,7 Hz thực', 'Đo 15 s: RTF 0,38'],
    ['ros_gz_bridge → ROS 2', '/camera', 'sensor_msgs/Image', 'như trên', 'Hai bên đăng ký: bộ đếm và backend'],
    ['/camera → traffic_counter', 'Subscribe, QoS sensor_data, depth 1', 'Khung mới nhất', 'Theo khả năng xử lý', 'Khung cũ bị bỏ, không xếp hàng'],
    ['traffic_counter → ROS 2', '/traffic/counts', 'std_msgs/String (JSON ≈ 0,4 kB)', '1 Hz (thời gian mô phỏng)', 'Kèm CSV từng xe trong logs/'],
    ['/camera, /traffic/counts → uav_bridge', 'Subscribe depth 1 / 10', 'Ảnh + JSON số đếm', '≤ 8 khung/s', 'Số đếm quá 5 s bị loại'],
    ['uav_bridge ↔ PX4', 'MAVSDK udpin://:14540', 'Telemetry; setpoint vận tốc thân máy bay', '20 Hz (offboard)', 'Offboard cần setpoint liên tục'],
    ['uav_bridge ↔ Web', 'WebSocket 127.0.0.1:8765', 'JSON: ảnh base64, hộp, số đếm, telemetry', 'Đo 4,3 gói/s', 'Xác thực token; xem slide 9'],
    ['PX4 ↔ ROS 2', 'XRCE-DDS UDP 8888', 'Topic /fmu/in, /fmu/out', 'theo PX4', 'Dùng cho offboard ROS 2'],
], [2.7, 2.7, 3.0, 2.1, 2.6], size=11, row_h=0.52)

# ---------------------------------------------------------------- 9. Giao thức WebSocket v1
s = new_slide('Giao thức WebSocket v1 giữa backend và web', '3 · Sự tương tác')
table(s, 0.6, 1.5, 7.4, [
    ['Bản tin (type)', 'Hướng', 'Trường chính'],
    ['auth', 'web → backend', 'protocol = 1, token'],
    ['hello', 'backend → web', 'protocol, source = ros, topic, model, telemetry'],
    ['frame', 'backend → web', 'seq, timestamp, width, height, image (JPEG base64), detections[{cls, confidence, xyxy}], telemetry, traffic, t_rx, timing'],
    ['status', 'backend → web', 'camera_fresh, message, telemetry, traffic'],
    ['flight_command', 'web → backend', 'request_id, action ∈ {forward, backward, left, right, up, down, yaw_left, yaw_right, hold}'],
    ['set_altitude', 'web → backend', 'request_id, altitude_m (4–35 m)'],
    ['command_result', 'backend → web', 'request_id, message'],
], [1.7, 1.6, 4.1], size=11, row_h=0.62, mono_cols=(0,))
tb(s, 8.4, 1.5, 4.3, 0.4, 'Cơ chế bảo vệ và ổn định', size=16, bold=True, color=TEAL)
bullets(s, 8.4, 1.95, 4.3, 4.6, [
    'Token ≥ 16 ký tự, so sánh bằng hmac.compare_digest; sai thì đóng kết nối mã 1008.',
    'Chỉ lắng nghe 127.0.0.1; kích thước tối đa mỗi gói 1 MiB.',
    'Backend phát khung theo vòng 50 ms; khi không có ảnh mới quá 3 s gửi status camera_fresh = false.',
    'Web kiểm tra từng gói (kiểu, miền giá trị, kích thước ảnh khớp dữ liệu hộp) trước khi vẽ.',
    'Trường traffic = JSON từ /traffic/counts; null nếu bộ đếm không chạy hoặc dữ liệu quá 5 s.',
    'Trường timing và t_rx (mới thêm) cho phép đo độ trễ từng công đoạn ở phía client.',
], size=13, gap=6)
