#!/usr/bin/env python3
"""Biểu đồ số liệu cho báo cáo kỹ thuật (matplotlib) -> measure/figs/*.png. Đọc số từ measure/*.json, finetune/runs."""
import csv, json, os, runpy, sys, math, statistics as st, collections
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
OUT = f'{HERE}/figs'
NAVY, ORANGE, TEAL, MUTED, GREEN, RED, PURPLE = '#0F2433', '#F28C28', '#1B8A8F', '#5B6B78', '#3E9B2F', '#B03A2E', '#6A4FB8'
plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 12, 'axes.edgecolor': '#8a99a5', 'axes.labelcolor': NAVY,
                     'xtick.color': NAVY, 'ytick.color': NAVY, 'axes.spines.top': False, 'axes.spines.right': False,
                     'axes.grid': True, 'grid.color': '#DDE4E9', 'grid.linewidth': 0.8, 'axes.axisbelow': True,
                     'figure.facecolor': 'white', 'axes.titleweight': 'bold', 'axes.titlesize': 13.5, 'axes.titlecolor': NAVY})
vn = FuncFormatter(lambda v, _: f'{v:g}'.replace('.', ','))
bench = json.load(open(f'{HERE}/bench.json'))
live = json.load(open(f'{HERE}/live_probe.json'))
gt = json.load(open(f'{HERE}/gt_result.json'))
trk = json.load(open(f'{HERE}/bench_tracker.json'))


def fx(x, d=1):
    return f'{x:.{d}f}'.replace('.', ',')


def save(fig, name):
    fig.savefig(f'{OUT}/{name}.png', dpi=150, bbox_inches='tight', facecolor='white')
    plt.close(fig)


def vfmt(ax, axis='y'):
    (ax.yaxis if axis == 'y' else ax.xaxis).set_major_formatter(vn)


# 1. đường cong huấn luyện (30 epoch, GTX 1650)
def training_curves():
    rows = list(csv.DictReader(open(f'{ROOT}/finetune/runs/yolov8m_sim_50ep_colab/results.csv')))
    g = lambda k: [float(r[k]) for r in rows]
    ep = [int(r['epoch']) for r in rows]
    fig, axs = plt.subplots(1, 3, figsize=(17, 4.9))
    a = axs[0]
    a.plot(ep, g('train/box_loss'), color=NAVY, lw=2.2, label='box (train)')
    a.plot(ep, g('val/box_loss'), color=NAVY, lw=2.2, ls='--', label='box (val)')
    a.plot(ep, g('train/cls_loss'), color=ORANGE, lw=2.2, label='cls (train)')
    a.plot(ep, g('val/cls_loss'), color=ORANGE, lw=2.2, ls='--', label='cls (val)')
    a.set_title('Hàm mất mát'); a.set_xlabel('epoch'); a.legend(frameon=False, ncol=2, fontsize=10.5); vfmt(a)
    a = axs[1]
    a.plot(ep, g('metrics/mAP50(B)'), color=TEAL, lw=2.4, label='mAP50')
    a.plot(ep, g('metrics/mAP50-95(B)'), color=ORANGE, lw=2.4, label='mAP50–95')
    a.axhline(0.402, color=MUTED, lw=1.4, ls=':'); a.text(ep[-1], 0.402 + 0.02, 'COCO gốc: mAP50 0,402', ha='right', color=MUTED, fontsize=10.5)
    a.set_ylim(0, 1.05); a.axvline(49, color=GREEN, lw=1.2, ls=':'); a.text(48.5, 0.2, 'best.pt\n(epoch 49)', ha='right', color=GREEN, fontsize=10.5); a.set_title('mAP trên tập val'); a.set_xlabel('epoch'); a.legend(frameon=False, loc='center right'); vfmt(a)
    a = axs[2]
    a.plot(ep, g('metrics/precision(B)'), color=GREEN, lw=2.4, label='Precision')
    a.plot(ep, g('metrics/recall(B)'), color=PURPLE, lw=2.4, label='Recall')
    a.set_ylim(0.8, 1.0); a.set_title('Precision / Recall (val)'); a.set_xlabel('epoch'); a.legend(frameon=False, loc='lower right'); vfmt(a)
    fig.tight_layout(); save(fig, 'c_training')


# 2. so sánh mô hình: theo lớp + radar tổng
def model_compare():
    cls = ['Người', 'Ô tô', 'Xe máy', 'Xe buýt', 'Xe tải']
    m = {'COCO gốc': [0.046, 0.580, 0.326, 0.428, 0.237], '30 epoch': [0.542, 0.926, 0.839, 0.908, 0.917],
         '50 epoch': [0.648, 0.960, 0.882, 0.942, 0.948]}
    fig = plt.figure(figsize=(17, 5.4))
    ax = fig.add_axes([0.04, 0.12, 0.55, 0.78])
    x = np.arange(5); w = 0.26
    for i, ((k, v), c) in enumerate(zip(m.items(), (MUTED, TEAL, ORANGE))):
        b = ax.bar(x + (i - 1) * w, v, w, color=c, label=k)
        for r, val in zip(b, v):
            ax.text(r.get_x() + r.get_width() / 2, val + 0.012, fx(val, 2), ha='center', fontsize=9.2, color=NAVY)
    ax.set_xticks(x); ax.set_xticklabels(cls); ax.set_ylim(0, 1.1); ax.set_title('mAP50–95 theo lớp (tập test 300 ảnh)')
    ax.legend(frameon=False, ncol=3, loc='upper left'); vfmt(ax)
    ax2 = fig.add_axes([0.70, 0.14, 0.24, 0.66], projection='polar')
    lab = ['Precision', 'Recall', 'mAP50', 'mAP50–95']
    vals = {'COCO gốc': [0.482, 0.535, 0.402, 0.323], '50 epoch': [0.981, 0.947, 0.982, 0.876]}
    ang = np.linspace(0, 2 * np.pi, 4, endpoint=False).tolist(); ang += ang[:1]
    for (k, v), c in zip(vals.items(), (MUTED, ORANGE)):
        v = v + v[:1]
        ax2.plot(ang, v, color=c, lw=2.4, label=k); ax2.fill(ang, v, color=c, alpha=0.18)
    ax2.set_xticks(ang[:-1]); ax2.set_xticklabels(lab, fontsize=11.5); ax2.tick_params(axis='x', pad=14); ax2.set_ylim(0, 1)
    ax2.set_yticks([0.25, 0.5, 0.75, 1.0]); ax2.set_yticklabels(['0,25', '0,5', '0,75', '1'], fontsize=8.5, color=MUTED)
    ax2.set_title('Chỉ số tổng thể', pad=18); ax2.legend(frameon=False, loc='lower center', bbox_to_anchor=(0.5, -0.17), ncol=2)
    save(fig, 'c_models')


# 3. thời gian từng công đoạn + cấu hình
def latency():
    pl = bench['pipeline']
    fig, axs = plt.subplots(1, 2, figsize=(17, 5.2), gridspec_kw={'width_ratios': [1.15, 1]})
    a = axs[0]
    names = ['Chuyển ảnh', 'YOLO', 'ByteTrack', 'FlowCounter', 'JPEG', 'base64']
    keys = ['convert', 'detect', 'track', 'count', 'jpeg', 'b64']
    vals = [pl[k]['mean'] for k in keys]
    cols = [MUTED, NAVY, TEAL, GREEN, ORANGE, PURPLE]
    y = np.arange(len(names))[::-1]
    a.barh(y, vals, color=cols, height=0.62)
    for yy, v in zip(y, vals):
        a.text(v + 0.6, yy, fx(v, 2) + ' ms', va='center', fontsize=11)
    a.set_yticks(y); a.set_yticklabels(names); a.set_xlim(0, 36)
    a.set_title('Thời gian từng công đoạn (benchmark độc lập, trung bình, GTX 1650)'); a.set_xlabel('ms / khung'); vfmt(a, 'x')
    a = axs[1]
    cfg = [('1920×1080\nimgsz 640', '1920x1080 imgsz640 fp32 GPU'), ('1920×1080\nimgsz 480', '1920x1080 imgsz480 fp32 GPU'),
           ('1280×720\nimgsz 640', '1280x720 imgsz640 fp32 GPU'), ('FP16\nimgsz 640', '1920x1080 imgsz640 fp16 GPU'),
           ('CPU\nimgsz 640', '1920x1080 imgsz640 fp32 CPU')]
    tot = [bench[k]['total']['mean'] for _, k in cfg]
    cc = [NAVY, TEAL, MUTED, RED, ORANGE]
    b = a.bar(range(len(cfg)), tot, color=cc, width=0.62)
    for r, v in zip(b, tot):
        a.text(r.get_x() + r.get_width() / 2, v + 4, f'{fx(v)} ms\n≈{v and 1000 / v:.0f} FPS', ha='center', fontsize=10.5, bbox=dict(fc='white', ec='none', pad=1.5, alpha=.9), zorder=5)
    a.axhline(33.3, color=GREEN, lw=1.6, ls='--', label='ngưỡng 30 FPS (33,3 ms)'); a.legend(frameon=False, loc='upper left')
    a.set_xticks(range(len(cfg))); a.set_xticklabels([c for c, _ in cfg], fontsize=10.5); a.set_ylim(0, 255)
    a.set_title('Tổng thời gian / khung theo cấu hình'); a.set_ylabel('ms'); vfmt(a)
    fig.tight_layout(); save(fig, 'c_latency')


# 4. độ trễ đầu cuối: histogram + CDF + chuỗi
def e2e():
    e = np.array([(x['tr'] - x['t_rx']) * 1e3 for x in live])
    fig, axs = plt.subplots(1, 3, figsize=(17, 4.9), gridspec_kw={'width_ratios': [1.1, 1, 1.2]})
    a = axs[0]
    a.hist(e, bins=22, color=TEAL, edgecolor='white')
    for q, c, ls in ((50, NAVY, '-'), (95, RED, '--')):
        v = np.percentile(e, q); a.axvline(v, color=c, lw=2, ls=ls); a.text(v + 2, a.get_ylim()[1] * (0.92 if q == 50 else 0.78), f'p{q} = {fx(v, 0)} ms', color=c, fontsize=11)
    a.set_title('Phân bố độ trễ đầu cuối'); a.set_xlabel('ms'); a.set_ylabel('số gói')
    a = axs[1]
    s = np.sort(e); p = np.arange(1, len(s) + 1) / len(s)
    a.plot(s, p, color=ORANGE, lw=2.6)
    for q in (0.5, 0.95):
        v = np.quantile(e, q); a.plot([v, v], [0, q], color=MUTED, lw=1, ls=':'); a.plot([s[0], v], [q, q], color=MUTED, lw=1, ls=':')
    a.set_title('Hàm phân phối tích luỹ (CDF)'); a.set_xlabel('ms'); a.set_ylabel('tỉ lệ gói ≤ x'); vfmt(a)
    a = axs[2]
    srv = np.array([x['pre_ms'] + x['infer_ms'] + x['encode_ms'] for x in live])
    rest = e - srv
    i = np.arange(len(e))
    a.stackplot(i, srv, rest, colors=[NAVY, ORANGE], labels=['xử lý trong backend', 'base64 + JSON + hàng đợi + gửi'], alpha=.9)
    a.set_title('Thành phần độ trễ theo thứ tự gói'); a.set_xlabel('gói'); a.set_ylabel('ms'); a.legend(frameon=False, loc='upper right', fontsize=10)
    a.set_ylim(0, max(e) * 1.35)
    fig.tight_layout(); save(fig, 'c_e2e')


# 5. độ phức tạp thực nghiệm
def scaling():
    n = np.array([int(k) for k in trk]); t = np.array(list(trk.values()))
    A = np.vstack([n, np.ones_like(n)]).T
    (m, c), res, *_ = np.linalg.lstsq(A, t, rcond=None)
    r2 = 1 - ((t - A @ [m, c]) ** 2).sum() / ((t - t.mean()) ** 2).sum()
    fig, axs = plt.subplots(1, 2, figsize=(17, 5.0))
    a = axs[0]
    a.plot(n, t, 'o', color=NAVY, ms=9, label='đo thực tế')
    xx = np.linspace(0, 420, 50); a.plot(xx, m * xx + c, color=ORANGE, lw=2.4, label=f'hồi quy tuyến tính: {fx(m, 3)}·N + {fx(c, 2)} ms (R² = {r2:.4f})'.replace('.', ',', 1) if False else f'tuyến tính: {fx(m, 3)}·N {"+" if c >= 0 else "−"} {fx(abs(c), 2)} ms, R² = {fx(r2, 4)}')
    a.set_title('ByteTrack: thời gian theo số hộp N'); a.set_xlabel('số hộp phát hiện N'); a.set_ylabel('ms / khung'); a.legend(frameon=False, loc='upper left', fontsize=11); vfmt(a)
    a = axs[1]
    px = [480 ** 2, 640 ** 2]; inf = [bench['1920x1080 imgsz480 fp32 GPU']['inf']['mean'], bench['1920x1080 imgsz640 fp32 GPU']['inf']['mean']]
    a.plot(px, inf, 'o-', color=TEAL, lw=2.4, ms=10)
    for p_, v, lab in zip(px, inf, ('imgsz 480', 'imgsz 640')):
        a.text(p_, v + 1.2, f'{lab}\n{fx(v)} ms', ha='center', fontsize=11)
    a.set_xlim(150000, 500000); a.set_ylim(10, 40)
    a.set_title('YOLOv8m: suy luận theo số điểm ảnh đầu vào (imgsz²)'); a.set_xlabel('imgsz²  (điểm ảnh)'); a.set_ylabel('ms')
    a.xaxis.set_major_formatter(FuncFormatter(lambda v, _: f'{int(v/1000)}k'))
    fig.tight_layout(); save(fig, 'c_scaling')


# 6. đếm: dữ liệu ghép
def count_data():
    r = runpy.run_path(f'{HERE}/gt_analyze.py', run_name='x') if False else None


def counting():
    sys.argv = ['gt_analyze.py', HERE, f'{HERE}/gt.pkl', f'{HERE}/counter_events.csv', '132.2', '1.0', f'/tmp/_gt_tmp.json']
    import io, contextlib
    with contextlib.redirect_stdout(io.StringIO()):
        g = runpy.run_path(f'{HERE}/gt_analyze.py', run_name='__main__')
    GT, EV, TP, FN, FP, T0, T1 = g['gt'], g['ev'], g['tp'], g['fn'], g['fp'], 132.2, g['t_end']
    # --- A: tích luỹ theo thời gian
    fig, axs = plt.subplots(2, 1, figsize=(15, 7.4), gridspec_kw={'height_ratios': [3, 1.1]}, sharex=True)
    a = axs[0]
    tg = sorted(x['t'] for x in GT) ; te = sorted(x['t'] for x in EV)
    a.step([T0] + tg + [T1], [0] + list(range(1, len(tg) + 1)) + [len(tg)], where='post', color=NAVY, lw=2.6, label=f'Ground truth ({len(tg)} xe)')
    a.step([T0] + te + [T1], [0] + list(range(1, len(te) + 1)) + [len(te)], where='post', color=ORANGE, lw=2.6, label=f'Hệ thống đếm ({len(te)} xe)')
    a.fill_between(np.linspace(T0, T1, 2), 0, 0, color='none')
    a.set_ylabel('số xe tích luỹ'); a.set_title('Số xe tích luỹ theo thời gian: ground truth và hệ thống đếm'); a.legend(frameon=False, loc='upper left')
    a = axs[1]
    cmap = {'Ô tô': TEAL, 'Xe máy': ORANGE, 'Xe buýt': PURPLE, 'Xe tải': GREEN}
    cls_order = list(cmap)
    for yi, c in enumerate(cls_order):
        ft = [g_['t'] for g_ in FN if g_['cls'] == c]
        a.scatter(ft, [yi] * len(ft), marker='|', s=260, color=RED, lw=2.4)
        okt = [x['t'] for x, e in TP if x['cls'] == c]
        a.scatter(okt, [yi] * len(okt), marker='|', s=130, color=cmap[c], lw=1.6, alpha=.8)
    a.set_yticks(range(4)); a.set_yticklabels(cls_order); a.set_ylim(-0.6, 3.6); a.grid(axis='y', alpha=0)
    a.set_xlabel('thời gian mô phỏng (s)'); a.set_title('Xe đếm đúng (màu theo lớp) và xe bỏ sót (đỏ)', fontsize=11.5)
    fig.tight_layout(); save(fig, 'c_cumulative')
    # --- B: theo lớp
    fig, axs = plt.subplots(1, 3, figsize=(17, 5.3), gridspec_kw={'width_ratios': [1.5, 1, 1]})
    a = axs[0]
    pc = gt['per_class']; names = list(pc)
    x = np.arange(len(names)); w = 0.26
    for i, (lab, idx, c) in enumerate((('Ground truth', 0, NAVY), ('Đếm được', 1, ORANGE), ('Đúng lớp + khớp', 2, TEAL))):
        v = [pc[n][idx] for n in names]
        b = a.bar(x + (i - 1) * w, v, w, color=c, label=lab)
        for r_, val in zip(b, v):
            a.text(r_.get_x() + r_.get_width() / 2, val + 1, str(val), ha='center', fontsize=10)
    a.set_xticks(x); a.set_xticklabels(names); a.set_title('Số xe theo lớp (120 s mô phỏng)'); a.legend(frameon=False, fontsize=10.5)
    a = axs[1]
    rec = [pc[n][2] / pc[n][0] for n in names]
    lo = []; hi = []
    for n in names:
        k, N = pc[n][2], pc[n][0]; p = k / N; z = 1.96; d = 1 + z * z / N; ctr = (p + z * z / (2 * N)) / d; hw = z * math.sqrt(p * (1 - p) / N + z * z / (4 * N * N)) / d
        lo.append(p - (ctr - hw)); hi.append((ctr + hw) - p)
    cols = [cmap[n] for n in names]
    a.bar(x, rec, 0.6, color=cols, yerr=[lo, hi], capsize=5, ecolor=NAVY)
    for xi, v, n in zip(x, rec, names):
        a.text(xi, 0.04, f'{pc[n][2]}/{pc[n][0]}', ha='center', color='white', fontsize=10.5, fontweight='bold')
    a.axhline(gt['recall'], color=RED, ls='--', lw=1.5, label=f'chung {fx(gt["recall"], 3)}'); a.legend(frameon=False, loc='lower right', fontsize=10, bbox_to_anchor=(1, 0.08))
    a.set_xticks(x); a.set_xticklabels(names, fontsize=10.5); a.set_ylim(0, 1.12); a.set_title('Recall đếm theo lớp (khoảng tin cậy Wilson 95%)', fontsize=12); vfmt(a)
    a = axs[2]
    fnc = collections.Counter(g_['cls'] for g_ in FN)
    labs = [f'{n}: {fnc[n]}' for n in names if fnc[n]]; vals = [fnc[n] for n in names if fnc[n]]
    a.pie(vals, labels=labs, colors=[cmap[n] for n in names if fnc[n]], startangle=90, counterclock=False, wedgeprops=dict(width=0.42, edgecolor='white'), textprops=dict(fontsize=11))
    a.text(0, 0, f'{len(FN)}\nxe bỏ sót', ha='center', va='center', fontsize=13, fontweight='bold', color=NAVY)
    a.set_title('Xe bỏ sót theo lớp'); a.grid(False)
    fig.tight_layout(); save(fig, 'c_counting')
    # --- C: lưu lượng theo từng 15 s
    fig, axs = plt.subplots(1, 2, figsize=(17, 4.9), gridspec_kw={'width_ratios': [1.8, 1]})
    a = axs[0]
    bins = T0 + 15 * np.arange(9); bins[-1] = T1
    bot = np.zeros(len(bins) - 1)
    for c in cls_order:
        h, _ = np.histogram([e['t'] for e in EV if e['cls'] == c], bins=bins)
        a.bar(bins[:-1], h, np.diff(bins), align='edge', bottom=bot, color=cmap[c], label=c, edgecolor='white'); bot += h
    hg, _ = np.histogram([x['t'] for x in GT], bins=bins)
    a.step(np.append(bins[:-1], bins[-1]), np.append(hg, hg[-1]), where='post', color=NAVY, lw=2.2, ls='--', label='Ground truth')
    a.set_xlabel('thời gian mô phỏng (s), khoảng 15 s'); a.set_ylabel('số xe / 15 s'); a.set_title('Lưu lượng đếm theo từng khoảng 15 s'); a.legend(frameon=False, ncol=5, fontsize=10.5, loc='upper left')
    a.set_ylim(0, max(bot.max(), hg.max()) + 4)
    a = axs[1]
    dirs = collections.Counter(e['dir'] for e in EV)
    dg = collections.Counter(x['dir'] for x in GT)
    ks = sorted(set(dirs) | set(dg)); xx = np.arange(len(ks))
    a.bar(xx - 0.2, [dg[k] for k in ks], 0.4, color=NAVY, label='Ground truth'); a.bar(xx + 0.2, [dirs[k] for k in ks], 0.4, color=ORANGE, label='Đếm được')
    for xi, k in zip(xx, ks):
        a.text(xi - 0.2, dg[k] + 1, str(dg[k]), ha='center', fontsize=10.5); a.text(xi + 0.2, dirs[k] + 1, str(dirs[k]), ha='center', fontsize=10.5)
    a.set_xticks(xx); a.set_xticklabels(ks, fontsize=16); a.set_title('Số xe theo chiều'); a.legend(frameon=False)
    fig.tight_layout(); save(fig, 'c_flow')
    return len(GT), len(EV), len(TP), len(FN), len(FP), dict(dg), dict(dirs)


# 7. KPI tổng hợp
def kpi():
    e = [(x['tr'] - x['t_rx']) * 1e3 for x in live]
    tiles = [('mAP50 (test)', '0,982', 'COCO gốc 0,402', TEAL), ('mAP50–95', '0,876', 'COCO gốc 0,323', TEAL),
             ('Precision đếm', fx(gt['precision'], 3), f'{gt["tp"]}/{gt["counted"]} xe đếm đúng', GREEN),
             ('Recall đếm', fx(gt['recall'], 3), f'{gt["tp"]}/{gt["gt"]} xe thật', ORANGE),
             ('Sai số lưu lượng', f'{(gt["q_cnt"] - gt["q_gt"]) / gt["q_gt"] * 100:.0f}%'.replace('-', '−'), f'{fx(gt["q_cnt"])} vs {fx(gt["q_gt"])} xe/phút', RED),
             ('Nhánh YOLO', f'{fx(bench["1920x1080 imgsz640 fp32 GPU"]["total"]["mean"])} ms', '≈ 31 FPS khi chạy riêng', NAVY),
             ('Độ trễ đầu cuối', f'{fx(st.mean(e), 0)} ms', f'trung bình · p95 = {fx(np.percentile(e, 95), 0)} ms', PURPLE),
             ('FPS camera thực', '11,7', 'RTF 0,38 (30,3 Hz mô phỏng)', MUTED)]
    fig, axs = plt.subplots(2, 4, figsize=(17, 5.8))
    for ax, (t, v, s_, c) in zip(axs.ravel(), tiles):
        ax.axis('off'); ax.set_xlim(0, 1); ax.set_ylim(0, 1)
        ax.add_patch(plt.Rectangle((0.0, 0.02), 1, 0.96, fc='#F4F8FB', ec='#D7E1E8', lw=1.2, transform=ax.transAxes))
        ax.add_patch(plt.Rectangle((0.0, 0.02), 0.035, 0.96, fc=c, ec='none', transform=ax.transAxes))
        ax.text(0.12, 0.8, t, fontsize=14, color=MUTED, fontweight='bold', va='center')
        ax.text(0.12, 0.47, v, fontsize=34, color=c, fontweight='bold', va='center')
        ax.text(0.12, 0.16, s_, fontsize=12, color=NAVY, va='center')
    fig.tight_layout(h_pad=1.2); save(fig, 'c_kpi')


if __name__ == '__main__':
    os.makedirs(OUT, exist_ok=True)
    training_curves(); model_compare(); latency(); e2e(); scaling(); print(counting()); kpi()
    print('ok')
