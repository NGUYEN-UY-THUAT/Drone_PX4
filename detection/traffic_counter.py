#!/usr/bin/env python3
"""Count traffic flow from the UAV camera with YOLOv8 + ByteTrack.

A counting zone (rectangle) is drawn on the image. Every tracked vehicle is
counted once, the first time its box centre enters the zone, by class and by
direction of travel. Flow is q = N / T (vehicles/minute): N vehicles counted
over the counting time T since the start or the last reset, in simulation time.
The flow over only the last --window seconds is shown as well.

Keep the drone hovering at a fixed altitude and gimbal angle while counting:
the zone is fixed in the image, so it only stays on the same piece of road
while the camera does not move.

    # live, from the ROS 2 /camera topic (same setup as uav_camera_det.py)
    python detection/traffic_counter.py
    # offline test on a recorded video
    python detection/traffic_counter.py --video demo/video_bay_nhan_dien.mp4

In the window: drag with the mouse to draw a new zone (counts are reset),
'r' resets the counts, 'q' quits. Counted vehicles are appended to a CSV in
logs/, and a JSON summary is published on /traffic/counts (std_msgs/String).
"""

import argparse
import csv
import json
import os
import time
from collections import Counter, defaultdict, deque

import cv2
import numpy as np
from ultralytics import YOLO
from ultralytics.trackers.byte_tracker import BYTETracker
from ultralytics.utils import YAML, IterableSimpleNamespace
from ultralytics.utils.checks import check_yaml

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)   # gốc repo
WEIGHTS_50EP = os.path.join(ROOT, 'finetune/runs/yolov8m_sim_50ep_colab/weights/best.pt')
WEIGHTS_30EP = os.path.join(ROOT, 'finetune/runs/yolov8m_sim/weights/best.pt')

# COCO ids kept by the fine-tuned model
CLASSES = {0: 'Người', 2: 'Ô tô', 3: 'Xe máy', 5: 'Xe buýt', 7: 'Xe tải'}
VEHICLES = (2, 3, 5, 7)
COLORS = {0: (60, 180, 75), 2: (255, 160, 40), 3: (40, 200, 230), 5: (200, 80, 200), 7: (40, 120, 255)}
WINDOW = 'Dem luu luong'
MIN_HITS = 3  # frames a track must exist before it can be counted
STABLE_S = 20  # below this counting time, q = N/T swings with every single vehicle


class FlowCounter:
    """Zone-entry counter on top of tracker output; independent of ROS."""

    def __init__(self, zone, window_s, csv_path, count_people=False):
        self.zone = zone  # (x1, y1, x2, y2), normalised 0..1
        self.window_s = window_s
        self.csv_path = csv_path
        self.classes = tuple(CLASSES) if count_people else VEHICLES
        self.reset()

    def reset(self):
        self.counted = set()
        self.by_class = Counter()
        self.by_dir = Counter()
        self.events = deque()  # (time, class) of counted vehicles, for flow
        self.history = defaultdict(lambda: deque(maxlen=15))  # id -> centres
        self.cls_votes = defaultdict(Counter)  # id -> class votes
        self.t0 = None

    def _in_zone(self, cx, cy, w, h):
        x1, y1, x2, y2 = self.zone
        return x1 * w <= cx <= x2 * w and y1 * h <= cy <= y2 * h

    def _direction(self, tid):
        pts = self.history[tid]
        if len(pts) < 3:
            return '?'
        dx, dy = pts[-1][0] - pts[0][0], pts[-1][1] - pts[0][1]
        if max(abs(dx), abs(dy)) < 4:
            return '?'
        if abs(dx) >= abs(dy):
            return '→' if dx > 0 else '←'
        return '↓' if dy > 0 else '↑'

    def update(self, boxes, w, h, t):
        """boxes: list of (track_id, cls, x1, y1, x2, y2). Returns ids counted now."""
        if self.t0 is None:
            self.t0 = t
        new = []
        for tid, cls, x1, y1, x2, y2 in boxes:
            cx, cy = (x1 + x2) / 2, (y1 + y2) / 2
            pts = self.history[tid]
            was_outside = bool(pts) and not self._in_zone(*pts[-1], w, h)
            pts.append((cx, cy))
            self.cls_votes[tid][cls] += 1
            # Count on entry only: the track must have been seen outside the zone first.
            # A track that appears inside the zone (start of the run, or a new id after
            # the tracker lost a vehicle) is never counted, so id switches do not double count.
            if tid in self.counted or not was_outside or len(pts) < MIN_HITS or not self._in_zone(cx, cy, w, h):
                continue
            # majority class over the track so far, so a one-frame mislabel does not count
            c = self.cls_votes[tid].most_common(1)[0][0]
            if c not in self.classes:
                continue
            d = self._direction(tid)
            self.counted.add(tid)
            self.by_class[c] += 1
            self.by_dir[d] += 1
            self.events.append((t, c))
            new.append(tid)
            with open(self.csv_path, 'a', newline='') as f:
                csv.writer(f).writerow([f'{t:.2f}', tid, CLASSES[c], d])
        while self.events and t - self.events[0][0] > self.window_s:
            self.events.popleft()
        return new

    def elapsed(self, t):
        return t - self.t0 if self.t0 is not None else 0.0

    def flow_per_min(self, t):
        """q = N / T: vehicles counted since the start (or last reset) over the counting time."""
        T = self.elapsed(t)
        return sum(self.by_class.values()) * 60.0 / T if T > 0 else 0.0

    def recent_flow_per_min(self, t):
        """N / T over only the last window_s seconds: follows changes such as congestion."""
        T = min(self.window_s, self.elapsed(t))
        return len(self.events) * 60.0 / T if T > 0 else 0.0

    def summary(self, t):
        return {
            't': round(t, 2),
            'elapsed_s': round(self.elapsed(t), 1),
            'total': sum(self.by_class.values()),
            'by_class': {CLASSES[c]: n for c, n in self.by_class.items()},
            'by_direction': dict(self.by_dir),
            'flow_per_min': round(self.flow_per_min(t), 1),
            'recent_flow_per_min': round(self.recent_flow_per_min(t), 1),
            'window_s': self.window_s,
            'stable': self.elapsed(t) >= STABLE_S,
            'zone': [round(v, 3) for v in self.zone],
        }


def draw(frame, counter, tracks, t, flash):
    h, w = frame.shape[:2]
    x1, y1, x2, y2 = counter.zone
    p1, p2 = (int(x1 * w), int(y1 * h)), (int(x2 * w), int(y2 * h))
    overlay = frame.copy()
    cv2.rectangle(overlay, p1, p2, (0, 200, 255), -1)
    cv2.addWeighted(overlay, 0.15, frame, 0.85, 0, frame)
    cv2.rectangle(frame, p1, p2, (0, 200, 255), 2)
    for tid, cls, bx1, by1, bx2, by2 in tracks:
        col = COLORS.get(cls, (200, 200, 200))
        thick = 4 if tid in flash else 2
        cv2.rectangle(frame, (int(bx1), int(by1)), (int(bx2), int(by2)), col, thick)
        mark = ' *' if tid in counter.counted else ''
        cv2.putText(frame, f'#{tid}{mark}', (int(bx1), int(by1) - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, col, 2)
    s = counter.summary(t)
    note = '' if s['stable'] else '  (chua on dinh)'
    lines = [f"q = N/T = {s['total']} xe / {s['elapsed_s']:.0f} s = {s['flow_per_min']:.1f} xe/phut{note}",
             f"{s['window_s']:.0f} s gan nhat: {s['recent_flow_per_min']:.1f} xe/phut"]
    lines += [f"{ascii_name(CLASSES[c])}: {counter.by_class[c]}" for c in counter.classes]
    lines += ['Chieu: ' + '  '.join(f'{ascii_dir(d)} {n}' for d, n in counter.by_dir.items())]
    pad = 8
    bh = 22 * len(lines) + pad
    cv2.rectangle(frame, (0, 0), (460, bh), (20, 20, 20), -1)
    for i, ln in enumerate(lines):
        cv2.putText(frame, ln, (pad, 20 + 22 * i), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (255, 255, 255), 1, cv2.LINE_AA)
    return frame


def ascii_name(name):
    # cv2.putText has no Vietnamese glyphs
    return {'Người': 'Nguoi', 'Ô tô': 'O to', 'Xe máy': 'Xe may', 'Xe buýt': 'Xe buyt', 'Xe tải': 'Xe tai'}[name]


def ascii_dir(d):
    return {'→': 'trai->phai', '←': 'phai->trai', '↓': 'tren->duoi', '↑': 'duoi->tren'}.get(d, 'chua ro')


class ZoneEditor:
    """Mouse drag in the window sets a new zone."""

    def __init__(self, counter):
        self.counter = counter
        self.start = None
        self.size = (1, 1)

    def __call__(self, event, x, y, flags, param):
        w, h = self.size
        if event == cv2.EVENT_LBUTTONDOWN:
            self.start = (x, y)
        elif event == cv2.EVENT_LBUTTONUP and self.start:
            (ax, ay), self.start = self.start, None
            if abs(x - ax) > 10 and abs(y - ay) > 10:
                self.counter.zone = (min(ax, x) / w, min(ay, y) / h, max(ax, x) / w, max(ay, y) / h)
                self.counter.reset()
                print('Vung dem moi:', [round(v, 3) for v in self.counter.zone])


class Pipeline:
    def __init__(self, args):
        weights = args.weights or (WEIGHTS_50EP if os.path.exists(WEIGHTS_50EP) else WEIGHTS_30EP)
        print('Model:', weights)
        self.model = YOLO(weights)
        self.tracker = BYTETracker(IterableSimpleNamespace(**YAML.load(check_yaml('bytetrack.yaml'))))
        self.args = args
        os.makedirs(os.path.join(ROOT, 'logs'), exist_ok=True)
        csv_path = os.path.join(ROOT, 'logs', time.strftime('traffic_%Y%m%d_%H%M%S.csv'))
        with open(csv_path, 'w', newline='') as f:
            csv.writer(f).writerow(['time_s', 'track_id', 'class', 'direction'])
        print('Ghi log:', csv_path)
        self.counter = FlowCounter(tuple(args.zone), args.window, csv_path, args.count_people)
        self.editor = ZoneEditor(self.counter)
        self.flash = {}
        self.writer = None
        if args.show:
            cv2.namedWindow(WINDOW, cv2.WINDOW_NORMAL)
            cv2.setMouseCallback(WINDOW, self.editor)

    def process(self, frame, t, wait_ms=1):
        h, w = frame.shape[:2]
        self.editor.size = (w, h)
        # ByteTrack needs the low-score detections too (second association stage), hence conf=0.1 here
        det = self.model.predict(frame, classes=list(CLASSES), conf=0.1, verbose=False)[0].boxes.cpu().numpy()
        tracks = []
        # Use each track's matched detection box (column 7 = its index in det), not the Kalman-smoothed
        # box: the filter lags when a vehicle enters from the image edge and its box grows fast.
        for x1, y1, x2, y2, tid, score, cls, idx in self.tracker.update(det, frame):
            if score >= self.args.conf:
                tracks.append((int(tid), int(cls), *det.xyxy[int(idx)]))
        for tid in self.counter.update(tracks, w, h, t):
            self.flash[tid] = 6
        self.flash = {k: v - 1 for k, v in self.flash.items() if v > 1}
        if self.args.show or self.args.save:
            frame = draw(frame, self.counter, tracks, t, self.flash)
        if self.args.save:
            if self.writer is None:
                self.writer = cv2.VideoWriter(self.args.save, cv2.VideoWriter_fourcc(*'mp4v'), self.args.save_fps, (w, h))
            self.writer.write(frame)
        if self.args.show:
            cv2.imshow(WINDOW, frame)
            key = cv2.waitKey(wait_ms) & 0xFF
            if key == ord('r'):
                self.counter.reset()
                print('Da reset bo dem')
            elif key == ord('q'):
                return False
        return True


def run_video(args, pipe):
    cap = cv2.VideoCapture(args.video)
    fps = cap.get(cv2.CAP_PROP_FPS) or 10
    args.save_fps = fps
    i = 0
    while True:
        ok, frame = cap.read()
        if not ok:
            break
        start = time.time()
        # play at the video's own speed when showing it, as fast as possible otherwise
        if not pipe.process(frame, i / fps, wait_ms=1):
            break
        if args.show:
            time.sleep(max(0.0, 1 / fps - (time.time() - start)))
        i += 1
    if args.show:
        print('Het video, nhan phim bat ky tren cua so de dong')
        cv2.waitKey(0)
    print(json.dumps(pipe.counter.summary(i / fps), ensure_ascii=False, indent=1))


def run_ros(args, pipe):
    import rclpy
    from rclpy.node import Node
    from rclpy.qos import qos_profile_sensor_data
    from sensor_msgs.msg import Image
    from std_msgs.msg import String

    class CounterNode(Node):
        def __init__(self):
            super().__init__('traffic_counter')
            # sensor-data QoS keeps only the newest frame, so detection never lags behind the camera
            self.create_subscription(Image, args.topic, self.on_image, qos_profile_sensor_data)
            self.pub = self.create_publisher(String, '/traffic/counts', 10)
            self.last_pub = 0.0

        def on_image(self, msg):
            frame = np.frombuffer(msg.data, dtype=np.uint8).reshape(msg.height, msg.step)
            frame = frame[:, :msg.width * 3].reshape(msg.height, msg.width, 3)
            if msg.encoding == 'rgb8':
                frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
            t = msg.header.stamp.sec + msg.header.stamp.nanosec * 1e-9  # simulation time
            if not pipe.process(frame.copy(), t):
                rclpy.shutdown()
                return
            if t - self.last_pub >= 1.0:
                self.last_pub = t
                self.pub.publish(String(data=json.dumps(pipe.counter.summary(t), ensure_ascii=False)))

    rclpy.init()
    node = CounterNode()
    try:
        rclpy.spin(node)
    except (KeyboardInterrupt, rclpy.executors.ExternalShutdownException):
        pass
    print(json.dumps(pipe.counter.summary(node.last_pub), ensure_ascii=False, indent=1))


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--weights', help='default: 50-epoch Colab model if present, else 30-epoch model')
    ap.add_argument('--video', help='run on a video file instead of the ROS 2 topic')
    ap.add_argument('--topic', default='camera')
    ap.add_argument('--zone', type=float, nargs=4, default=[0.42, 0.0, 0.58, 1.0], metavar=('X1', 'Y1', 'X2', 'Y2'),
                    help='counting zone, normalised 0..1 (default: vertical band in the middle, '
                         'for a road running left-right in the image)')
    ap.add_argument('--window', type=float, default=60, help='flow window in seconds (default 60)')
    ap.add_argument('--conf', type=float, default=0.3, help='min confidence of a tracked box to be shown/counted')
    ap.add_argument('--count-people', action='store_true', help='also count people')
    ap.add_argument('--no-show', dest='show', action='store_false', help='no OpenCV window')
    ap.add_argument('--save', help='also write the annotated frames to this .mp4')
    ap.add_argument('--save-fps', type=float, default=15, help='fps of --save in ROS mode (video mode uses the source fps)')
    args = ap.parse_args()
    pipe = Pipeline(args)
    try:
        (run_video if args.video else run_ros)(args, pipe)
    finally:
        if pipe.writer is not None:
            pipe.writer.release()
            print('Da luu video:', args.save)


if __name__ == '__main__':
    main()
