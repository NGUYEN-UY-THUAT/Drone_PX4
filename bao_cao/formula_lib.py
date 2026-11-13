"""Vẽ công thức thành ảnh PNG (matplotlib mathtext, font STIX) để slide hiển thị đúng, không phụ thuộc font của máy."""
import hashlib
import os

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

matplotlib.rcParams['mathtext.fontset'] = 'stix'
matplotlib.rcParams['font.family'] = 'DejaVu Sans'
CACHE = os.path.join(os.path.dirname(os.path.abspath(__file__)), '_formula_cache')
DPI = 220


def render(lines, size=16, color='#0F2433'):  # nền trùng màu thẻ (EEF3F6)
    """lines: danh sách chuỗi mathtext (đặt công thức trong $...$). Trả (đường dẫn PNG, rộng inch, cao inch)."""
    os.makedirs(CACHE, exist_ok=True)
    key = hashlib.md5(('|'.join(lines) + f'{size}{color}').encode()).hexdigest()[:12]
    path = f'{CACHE}/{key}.png'
    fig = plt.figure(figsize=(8, 0.5 * len(lines) + 0.3), facecolor='#EEF3F6')
    n = len(lines)
    for i, ln in enumerate(lines):
        fig.text(0.0, 1 - (i + 0.5) / n, ln, fontsize=size, color=color, va='center', ha='left')
    fig.savefig(path, dpi=DPI, facecolor='#EEF3F6', bbox_inches='tight', pad_inches=0.03)
    plt.close(fig)
    from PIL import Image
    w, h = Image.open(path).size
    return path, w / DPI, h / DPI
