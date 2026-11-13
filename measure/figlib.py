"""Vẽ sơ đồ quy trình (phong cách khối bo góc, dải màu theo giai đoạn) bằng matplotlib."""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Rectangle, Polygon
from matplotlib import font_manager as fm

plt.rcParams['font.family'] = 'DejaVu Sans'
NAVY, ORANGE, TEAL, MUTED = '#0F2433', '#F28C28', '#1B8A8F', '#5B6B78'
INK = '#16323f'
PAL = {  # (viền, nền dải, nền đầu dải)
    'green': ('#3E9B2F', '#EAF7E6', '#2E8B3A'),
    'purple': ('#7A5FC9', '#EFEBFB', '#6A4FB8'),
    'orange': ('#E07B1A', '#FFF3E4', '#D9701A'),
    'blue': ('#1479B8', '#E6F3FB', '#0F5F93'),
}


def canvas(w=16, h=9, title=None, sub=None):
    fig = plt.figure(figsize=(w, h), dpi=150)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, w); ax.set_ylim(h, 0); ax.axis('off')
    fig.patch.set_facecolor('#F6FAFD')
    if title:
        pill(ax, w / 2, 0.55, title, sub)
    return fig, ax


def pill(ax, cx, cy, text, sub=None, w=9.2, h=0.8):
    ax.add_patch(FancyBboxPatch((cx - w / 2, cy - h / 2), w, h, boxstyle='round,pad=0,rounding_size=0.4',
                                fc=NAVY, ec='none', zorder=3))
    ax.text(cx, cy - (0.0 if not sub else 0.1), text, color='white', fontsize=21, fontweight='bold', ha='center',
            va='center', zorder=4)
    if sub:
        ax.text(cx, cy + 0.27, sub, color='#CFDDE6', fontsize=12.5, ha='center', va='center', zorder=4)
    for x0, x1 in ((0.5, cx - w / 2 - 0.2), (cx + w / 2 + 0.2, 15.5)):
        ax.plot([x0, x1], [cy, cy], color=NAVY, lw=1.2, zorder=1)


def band(ax, x, y, w, h, kind, title, icon=''):
    ec, bg, hd = PAL[kind]
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle='round,pad=0,rounding_size=0.35', fc=bg, ec=ec, lw=1.4,
                                alpha=1, zorder=0))
    tw = 0.5 + 0.215 * len(title) + (0.55 if icon else 0)
    ax.add_patch(Polygon([(x + 0.2, y + 0.16), (x + 0.2 + tw, y + 0.16), (x + 0.2 + tw - 0.25, y + 0.78),
                          (x + 0.2, y + 0.78)], closed=True, fc=hd, ec='none', zorder=2))
    ax.text(x + 0.2 + (0.62 if icon else 0.28), y + 0.47, title, color='white', fontsize=16.5, fontweight='bold',
            va='center', ha='left', zorder=3)
    if icon:
        ax.text(x + 0.5, y + 0.47, icon, color='white', fontsize=17, va='center', ha='center', zorder=3)


def node(ax, cx, cy, w, h, text, style='plain', fs=13.5, kind='green', sub=None, icon=None):
    """style: plain (nền nhạt viền xanh đen), hero (xanh dương đậm, chữ trắng), data (xếp chồng, màu theo kind),
    chip (nhãn nhỏ)."""
    if style == 'data':
        cy += 0.1
    x, y = cx - w / 2, cy - h / 2
    ec, bg, hd = PAL[kind]
    sh = FancyBboxPatch((x + 0.05, y + 0.07), w, h, boxstyle='round,pad=0,rounding_size=0.22', fc='#0F2433',
                        ec='none', alpha=0.13, zorder=4)
    ax.add_patch(sh)
    if style == 'data':
        for k in (2, 1):
            ax.add_patch(FancyBboxPatch((x + 0.07 * k, y - 0.07 * k), w, h, boxstyle='round,pad=0,rounding_size=0.2',
                                        fc=bg if kind != 'green' else '#C8EDA8', ec=ec, lw=1.3, zorder=4))
        fc = {'green': '#A9E07F', 'purple': '#D8CFF6', 'orange': '#FFD27A'}[kind]
        ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle='round,pad=0,rounding_size=0.2', fc=fc, ec=ec, lw=1.6, zorder=5))
        tc = INK
    elif style == 'hero':
        ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle='round,pad=0,rounding_size=0.22', fc='#1479B8', ec='#0B4F7A',
                                    lw=1.6, zorder=5))
        ax.add_patch(FancyBboxPatch((x + 0.06, y + 0.06), w - 0.12, h * 0.42, boxstyle='round,pad=0,rounding_size=0.18',
                                    fc='white', ec='none', alpha=0.12, zorder=6))
        tc = 'white'
    elif style == 'result':
        ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle='round,pad=0,rounding_size=0.22', fc='#D6F2BF', ec=ec, lw=1.8, zorder=5))
        tc = INK
    elif style == 'warn':
        ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle='round,pad=0,rounding_size=0.22', fc='#FDE8E4', ec='#B03A2E', lw=1.8, zorder=5))
        tc = INK
    elif style == 'gray':
        ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle='round,pad=0,rounding_size=0.22', fc='#EEF2F5', ec='#8a99a5', lw=1.6, zorder=5))
        tc = INK
    elif style == 'light':
        ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle='round,pad=0,rounding_size=0.22', fc='#D4EEFB', ec='#1479B8', lw=1.8, zorder=5))
        tc = '#0B3C5E'
    else:
        ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle='round,pad=0,rounding_size=0.22', fc='#F4F8FB', ec='#2B4657', lw=1.6, zorder=5))
        tc = INK
    ty = cy - (0.14 if sub else 0) + (0.22 if icon else 0)
    if icon:
        ax.text(cx, y + h * 0.27, icon, fontsize=22, ha='center', va='center', color=tc if style != 'plain' else TEAL, zorder=7)
    ax.text(cx, ty, text, fontsize=fs, fontweight='bold', color=tc, ha='center', va='center', zorder=7, linespacing=1.15)
    if sub:
        ax.text(cx, cy + h * 0.30, sub, fontsize=fs - 2.8, color=tc, ha='center', va='center', zorder=7, alpha=.9)


def chip(ax, cx, cy, w, h, text, kind='green', fs=11):
    ec, bg, hd = PAL[kind]
    ax.add_patch(FancyBboxPatch((cx - w / 2, cy - h / 2), w, h, boxstyle='round,pad=0,rounding_size=0.14', fc='white',
                                ec=ec, lw=1.4, zorder=5))
    ax.text(cx, cy, text, fontsize=fs, fontweight='bold', color=INK, ha='center', va='center', zorder=6)


def arrow(ax, pts, color=INK, lw=2.4, dash=False, label=None, lpos=None, fs=10.5, lcolor=None):
    xs, ys = zip(*pts)
    ax.plot(xs[:-1] + (xs[-1],), ys, color=color, lw=lw, solid_capstyle='round', zorder=3,
            linestyle='--' if dash else '-') if False else None
    ax.plot(xs, ys, color=color, lw=lw, zorder=3, linestyle='--' if dash else '-', solid_joinstyle='round')
    (x0, y0), (x1, y1) = pts[-2], pts[-1]
    dx, dy = x1 - x0, y1 - y0
    n = (dx * dx + dy * dy) ** .5
    ux, uy = dx / n, dy / n
    s = 0.12
    ax.add_patch(Polygon([(x1, y1), (x1 - ux * s * 1.5 + uy * s, y1 - uy * s * 1.5 - ux * s),
                          (x1 - ux * s * 1.5 - uy * s, y1 - uy * s * 1.5 + ux * s)], closed=True, fc=color, ec=color,
                         zorder=3))
    if label:
        lx, ly = lpos if lpos else ((pts[0][0] + pts[-1][0]) / 2, (pts[0][1] + pts[-1][1]) / 2 - 0.22)
        ax.text(lx, ly, label, fontsize=fs, color=lcolor or MUTED, ha='center', va='center', zorder=6, fontweight='bold')


def matrix(ax, cx, cy, cols=5, rows=2, color='#7BC94F', s=0.2, gap=0.07):
    w = cols * s + (cols - 1) * gap
    for r in range(rows):
        for c in range(cols):
            x = cx - w / 2 + c * (s + gap)
            y = cy - (rows * s + (rows - 1) * gap) / 2 + r * (s + gap)
            ax.add_patch(FancyBboxPatch((x, y), s, s, boxstyle='round,pad=0,rounding_size=0.04', fc=color, ec='none', zorder=4))


def dashed(ax, y, x0=0.4, x1=15.6):
    ax.plot([x0, x1], [y, y], color=INK, lw=1.2, ls=(0, (5, 4)), zorder=1)


def save(fig, path):
    fig.savefig(path, dpi=150, facecolor=fig.get_facecolor())
    plt.close(fig)


def lab(ax, x, y, text, fs=10.5, w=None, kind='blue'):
    """Nhãn nhỏ nền trắng đặt trên mũi tên."""
    w = w or (0.13 * len(text) * fs / 11 + 0.3)
    ec = PAL[kind][0]
    ax.add_patch(FancyBboxPatch((x - w / 2, y - 0.17), w, 0.34, boxstyle='round,pad=0,rounding_size=0.12', fc='white', ec=ec, lw=1.1, zorder=6))
    ax.text(x, y, text, fontsize=fs, color=INK, ha='center', va='center', zorder=7, fontweight='bold')
