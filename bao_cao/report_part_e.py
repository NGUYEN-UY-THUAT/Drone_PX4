"""Slide theo danh sách đã duyệt: sơ đồ (measure/figs/review), công thức điều khiển, web/API, ma trận nhầm lẫn,
kết quả thực tế trong mô phỏng, hạn chế."""
import json

from report_lib import *
from report_part_d import fig_slide, M, _c

CM = json.load(open(f'{M}/confusion.json'))


def rec(model, j):
    mat = CM[model]
    true = sum(mat[i][j] for i in range(6))
    return int(mat[j][j]), int(true)


# e0. Sơ đồ khối hệ thống
fig_slide('Sơ đồ khối hệ thống', '1 · Hệ thống', 'review/01_so_do_khoi_he_thong', [
    'Bốn nhóm khối: mô phỏng (Gazebo, traffic.py, PX4 SITL, gimbal), trung gian (ros_gz_bridge, ROS 2, MAVSDK), xử lý AI (YOLOv8m, ByteTrack, FlowCounter, backend) và giao diện (web, bàn phím).',
    'Dữ liệu ảnh đi một chiều từ mô phỏng lên giao diện; lệnh bay và gimbal đi ngược lại (nét đứt).',
], max_h=4.5)

# e1. Tương tác
fig_slide('Sơ đồ tương tác giữa các khối', '2 · Sự tương tác', 'review/02_tuong_tac_giua_cac_khoi', [
    'Hai tiến trình cùng nhận /camera: traffic_counter.py (đếm) và uav_bridge.py (hiển thị); backend lấy số đếm qua /traffic/counts (1 Hz).',
    'Hai đường điều khiển UAV: bàn phím gửi manual_control, backend gửi offboard velocity 20 Hz qua MAVSDK; gimbal chỉnh bằng gz topic.',
], max_h=4.75)

# e2. Luồng dữ liệu
fig_slide('Sơ đồ luồng dữ liệu và kích thước dữ liệu', '3 · Luồng dữ liệu', 'review/03_so_do_luong_du_lieu', [
    'Ảnh thô 6,22 MB được giảm còn ≈ 61 kB (JPEG) trước khi gửi; mỗi gói frame ≈ 82 kB (đo thật, 195 gói). Số đếm chỉ ≈ 0,4 kB mỗi giây.',
    'Hai nhánh xử lý YOLO độc lập (đếm và hiển thị) cùng đọc /camera nên cùng một khung bị suy luận hai lần.',
], max_h=4.75)

# e3. Sơ đồ điều khiển UAV
fig_slide('Sơ đồ điều khiển UAV: ba đường điều khiển', '4 · Công thức toán học', 'review/07_dieu_khien_uav', [
    'Bàn phím điều khiển trực tiếp qua manual control (PX4 chế độ Position/Altitude/Hold); web điều khiển bằng vận tốc theo hệ toạ độ thân ở chế độ Offboard; gimbal nhận góc đặt qua gz topic.',
    'Công thức và giá trị cụ thể của từng đường điều khiển ở slide kế tiếp.',
], max_h=4.45)

# e4. Web / backend / API
fig_slide('Web, backend và API: giao thức WebSocket v1', '6 · Web, backend và API', 'review/05_web_backend_api', [
    'Trình duyệt chỉ nói chuyện với backend qua một kết nối WebSocket (JSON): nhận gói frame (ảnh JPEG base64, hộp, telemetry, số đếm), gửi lệnh bay và độ cao.',
    'Mọi gói của trình duyệt đều bị backend kiểm tra: gói đầu tiên bắt buộc là auth đúng token; lệnh bay chỉ được nhận khi UAV đã armed và đang bay.',
], max_h=4.5)

s = new_slide('Backend uav_bridge.py: cách chạy, xác thực và giới hạn', '6 · Web, backend và API')
table(s, 0.6, 1.45, 12.1, [
    ['Hạng mục', 'Chi tiết (theo code)'],
    ['Chạy backend', 'UAV_BRIDGE_TOKEN=<≥ 16 ký tự> python3 web/backend/uav_bridge.py [--model] [--topic /camera] [--host 127.0.0.1] [--port 8765] [--mavsdk udp://:14540]'],
    ['Giao diện web', 'HTML/JS thuần (index.html, app.js, live.js, controls.js); trình duyệt nhập địa chỉ ws:// và token để kết nối'],
    ['Nguồn dữ liệu', 'ROS 2: /camera (ảnh), /traffic/counts (JSON; quá 5 s coi như không có); MAVSDK: độ cao, chế độ bay, armed, in_air'],
    ['Xác thực', 'Gói đầu tiên: {type: auth, protocol: 1, token}; so token bằng hmac.compare_digest; sai hoặc quá 10 s thì đóng kết nối (mã 1008)'],
    ['Điều kiện lệnh', 'can_control = connected, armed và in_air; set_altitude còn cần có toạ độ; độ cao ngoài 4–35 m bị từ chối'],
    ['Tần số và giới hạn', 'Suy luận tối đa 8 khung/s (MAX_FPS); ảnh cũ hơn 3 s thì gửi gói status; gói nhận tối đa 1 MiB; mặc định chỉ lắng nghe 127.0.0.1'],
    ['Lệnh bay', 'forward, backward, left, right, up, down, yaw_left, yaw_right, hold; lệnh mới thay lệnh đang chạy, không xếp hàng'],
], [2.0, 10.1], size=12, row_h=0.62, first_col_bold=True)
tb(s, 0.6, 6.55, 12.1, 0.5, 'Backend chỉ bind 127.0.0.1 theo mặc định: muốn truy cập từ máy khác phải đổi --host và đặt token đủ mạnh.', size=12, color=MUTED)

# e6. Ma trận nhầm lẫn
r50 = {n: rec('50 epoch', j) for j, n in enumerate(['Người', 'Ô tô', 'Xe máy', 'Xe buýt', 'Xe tải'])}
fig_slide('Ma trận nhầm lẫn trên tập test (300 ảnh, 1017 đối tượng)', '7 · Kết quả đánh giá', 'review/04a_ma_tran_nham_lan_3_mo_hinh', [
    f'COCO gốc: 268 xe máy bị gán “Người”, 172 xe máy bị bỏ sót, 64 xe tải bị gán “Ô tô”. Mô hình 50 epoch: xe máy {r50["Xe máy"][0]}/{r50["Xe máy"][1]}, ô tô {r50["Ô tô"][0]}/{r50["Ô tô"][1]}, xe tải {r50["Xe tải"][0]}/{r50["Xe tải"][1]}, xe buýt {r50["Xe buýt"][0]}/{r50["Xe buýt"][1]}, người {r50["Người"][0]}/{r50["Người"][1]}.',
    'Lớp yếu nhất vẫn là “Người”: 12 phát hiện thừa trên nền (precision 0,846). Từ 30 lên 50 epoch: recall người 0,884 → 0,957, phát hiện thừa xe máy 13 → 7.',
    'Ngưỡng conf = 0,25, IoU = 0,45; hàng = lớp thật, cột = dự đoán, hàng/cột “Nền” = phát hiện thừa/bỏ sót. Ma trận COCO chỉ hiện 5 lớp (nhầm sang lớp COCO khác không hiện).',
], max_h=3.7, size=12)

# e7. Kết quả thực tế: nhận diện
fig_slide('Kết quả thực tế trong mô phỏng: nhận diện trên ảnh camera UAV', '7 · Kết quả đánh giá', 'sim_compare', [
    'Hai ảnh test chụp từ camera UAV trong Gazebo (độ cao và góc nhìn khác nhau). Mô hình COCO gốc gán nhãn “Người” cho xe máy (người lái) và gán xe tải thành “Ô tô”.',
    'Mô hình 50 epoch cho số hộp bằng số đối tượng thật ở cả hai ảnh (10/10 và 9/9) và lớp trùng với nhãn thật trên hình; hộp “Người” ở ảnh dưới chỉ đạt độ tin cậy 0,35.',
], max_h=4.5, size=12)

# e8. Kết quả thực tế: đếm trên video bay
fig_slide('Kết quả thực tế trong mô phỏng: đếm xe trên video UAV bay', '7 · Kết quả đánh giá', 'sim_counting_demo', [
    'traffic_counter.py (mô hình 50 epoch + ByteTrack + FlowCounter) chạy trên video quay từ UAV trong Gazebo (30 s, 10 khung/s, 1280×720; vùng đếm là dải vàng ở giữa ảnh).',
    'Kết quả: 14 xe đi qua vùng đếm (9 ô tô, 3 xe tải, 1 xe buýt, 1 xe máy; 8 xe sang trái, 6 xe sang phải), lưu lượng q = 28 xe/phút. Đoạn video này không có ground truth; độ chính xác đếm được đo ở thử nghiệm 120 s có ground truth (các slide sau).',
], max_h=4.3, size=12)

# e9. Hạn chế
fig_slide('Hạn chế và hướng cải thiện', 'Kết luận', 'review/06_han_che_huong_cai_thien', [
    'Mọi hạn chế ghi ở đây đều là điều đã đo được hoặc đã biết rõ từ thiết kế; các hướng cải thiện chưa được thử, nên chưa có số đo kèm theo.',
], max_h=5.1, size=12)

# e10. Công thức điều khiển (thẻ công thức)
from report_part_b import card
s = new_slide('Công thức điều khiển UAV và các tham số', '4 · Công thức toán học')
cards = [
    ('Bàn phím (manual control)', [r'$u=(\mathrm{roll},\ \mathrm{pitch},\ \mathrm{throttle},\ \mathrm{yaw})$'],
     'roll, pitch, yaw ∈ {−0,5; 0; 0,5}; throttle ∈ {0; 0,5; 1}; gửi mỗi 0,1 s'),
    ('Web: di chuyển ngang', [r'$v=(v_{fwd},\,v_{right},\,v_{down},\,\omega_{yaw}),\qquad d=v\,T$'],
     'v = 2 m/s, T = 0,6 s  →  d = 1,2 m mỗi lệnh'),
    ('Web: xoay (yaw)', [r'$\Delta\psi=\omega_{yaw}\,T=30\,^{\circ}/\mathrm{s}\times1\,\mathrm{s}=30^{\circ}$'],
     'ω_yaw = 30 °/s, giữ 1 s'),
    ('Web: lên / xuống', [r'$\mathrm{stop\ if}\ \left|h-h_{0}\right|\geq\Delta H-b=1-0{,}25=0{,}75\ \mathrm{m}$'],
     'v_lên = 2 m/s, v_xuống = 1,5 m/s, tối đa 4 s; b bù quán tính'),
    ('Web: độ cao đích', [r'$h_{abs}=h_{abs,now}-h_{rel}+h_{goal}$'],
     '4 ≤ h_đích ≤ 35 m; gửi bằng goto_location(lat, lon, h_abs)'),
    ('Gimbal', [r'$\theta_{k+1}=\mathrm{clip}\left(\theta_{k}\pm\delta,\ \theta_{min},\ \theta_{max}\right)$'],
     'δ = 0,05 rad (≈ 2,9°); pitch ∈ [−0,5; 1,57], yaw ∈ [−1,57; 1,57] rad'),
]
for k, (t, f, n) in enumerate(cards):
    card(s, 0.6 + (k % 2) * 6.15, 1.45 + (k // 2) * 1.75, 5.95, 1.65, t, f, n, size=15, nh=0.5)
tb(s, 0.6, 6.7, 12.1, 0.35, 'Setpoint offboard gửi liên tục 20 Hz (PX4 thoát Offboard nếu ngừng nhận); dừng lệnh = gửi vận tốc 0 nhưng vẫn ở Offboard.', size=11, color=MUTED)
