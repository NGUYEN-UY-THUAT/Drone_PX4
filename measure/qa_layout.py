"""Kiểm tra bố cục slide khi không có LibreOffice: ước lượng chiều cao chữ sau khi xuống dòng (font Liberation ≈ Arial,
rộng hơn Calibri ~8 % nên ước lượng thiên về an toàn) và so với khung / hàng bảng / mép slide.
    python measure/qa_layout.py slides_bao_cao_ky_thuat.pptx [--png out_dir]
"""
import sys
from pptx import Presentation
from pptx.util import Emu
from PIL import Image, ImageDraw, ImageFont

FONTS = {
    'sans': '/usr/share/fonts/truetype/liberation2/LiberationSans-Regular.ttf',
    'sansb': '/usr/share/fonts/truetype/liberation2/LiberationSans-Bold.ttf',
    'mono': '/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf',
    'serifb': '/usr/share/fonts/truetype/liberation2/LiberationSerif-Bold.ttf',
}
CAL = 0.93   # Calibri hẹp hơn Arial ~7 %
_cache = {}


def font(kind, px):
    k = (kind, round(px))
    if k not in _cache:
        _cache[k] = ImageFont.truetype(FONTS[kind], max(6, round(px)))
    return _cache[k]


def kind_of(run):
    n = (run.font.name or 'Calibri')
    b = bool(run.font.bold)
    if n == 'Consolas':
        return 'mono'
    if n == 'Cambria':
        return 'serifb' if b else 'serifb'
    return 'sansb' if b else 'sans'


def para_lines(p, width_in, scale=1.0):
    """Số dòng và chiều cao (inch) của một đoạn."""
    runs = [r for r in p.runs]
    if not runs:
        return 1, 12 * 1.2 / 72
    size = max((r.font.size.pt if r.font.size else 14) for r in runs)
    words = []
    for r in runs:
        k = kind_of(r)
        sz = r.font.size.pt if r.font.size else 14
        for w in r.text.replace('\n', ' \n ').split(' '):
            words.append((w, k, sz))
    maxw = width_in * 72.0   # pt
    lines, cur = 1, 0.0
    for w, k, sz in words:
        if w == '\n':
            lines += 1
            cur = 0
            continue
        f = font(k, sz * 4)
        ww = f.getlength(w + ' ') / 4 * (CAL if k.startswith('sans') else 1.0)
        if cur + ww > maxw and cur > 0:
            lines += 1
            cur = ww
        else:
            cur += ww
    return lines, lines * size * 1.2 / 72


def tf_height(tf, width_in):
    h = 0
    for p in tf.paragraphs:
        n, hh = para_lines(p, width_in)
        sa = (p.space_after.pt if p.space_after is not None else 0) / 72
        h += hh + sa
    return h


def check(path, png=None):
    prs = Presentation(path)
    SW, SH = prs.slide_width / 914400, prs.slide_height / 914400
    problems = 0
    for si, slide in enumerate(prs.slides, 1):
        items = []
        texts = []
        for sh in slide.shapes:
            x, y, w, h = sh.left / 914400, sh.top / 914400, sh.width / 914400, sh.height / 914400
            if x < -0.01 or y < -0.01 or x + w > SW + 0.01 or y + h > SH + 0.01:
                print(f'  [{si}] NGOÀI SLIDE: {sh.name} ({x:.2f},{y:.2f},{w:.2f},{h:.2f})')
                problems += 1
            if sh.has_text_frame and sh.text_frame.text.strip():
                tf = sh.text_frame
                ml = (tf.margin_left or 0) / 914400
                mr = (tf.margin_right or 0) / 914400
                mt = (tf.margin_top or 0) / 914400
                mb = (tf.margin_bottom or 0) / 914400
                need = tf_height(tf, w - ml - mr) + mt + mb
                if need > h + 0.04:
                    print(f'  [{si}] TRÀN CHỮ: "{tf.text[:50]}" cần {need:.2f}" có {h:.2f}"  (y={y:.2f})')
                    problems += 1
                from pptx.enum.text import MSO_ANCHOR
                anc = tf.vertical_anchor
                if anc == MSO_ANCHOR.BOTTOM:
                    used = (y + h - need, y + h)
                elif anc == MSO_ANCHOR.MIDDLE:
                    used = (y + (h - need) / 2, y + (h + need) / 2)
                else:
                    used = (y, y + need)
                items.append((used[0], used[1], x, x + w, 'text'))
                texts.append((used[0], used[1], x, x + w, tf.text[:30], sh.shape_type))
            elif sh.has_table:
                t = sh.table
                tot = 0
                for ri, row in enumerate(t.rows):
                    rh = row.height / 914400
                    need_r = 0
                    for ci, cell in enumerate(row.cells):
                        cw = t.columns[ci].width / 914400 - (cell.margin_left + cell.margin_right) / 914400
                        need_c = tf_height(cell.text_frame, cw) + (cell.margin_top + cell.margin_bottom) / 914400
                        need_r = max(need_r, need_c)
                    tot += max(rh, need_r)
                declared = sum(r.height for r in t.rows) / 914400
                bottom = y + tot
                flag = ''
                if bottom > 7.2:
                    flag = '  <-- VƯỢT MÉP DƯỚI'
                    problems += 1
                if tot > declared + 0.05:
                    print(f'  [{si}] bảng cao hơn khai báo: {tot:.2f}" vs {declared:.2f}" (đáy {bottom:.2f}"){flag}')
                elif flag:
                    print(f'  [{si}] bảng đáy {bottom:.2f}"{flag}')
                items.append((y, bottom, x, x + w, 'table'))
        for i, a in enumerate(texts):
            for b in texts[i + 1:]:
                ox = min(a[3], b[3]) - max(a[2], b[2]); oy = min(a[1], b[1]) - max(a[0], b[0])
                if ox > 0.05 and oy > 0.03:
                    print(f'  [{si}] CHỮ CHỒNG: "{a[4]}" và "{b[4]}" (chồng {oy:.2f}" dọc)')
                    problems += 1
        # chồng lấn giữa bảng và các khối bên dưới trong cùng cột
        for a in items:
            if a[4] != 'table':
                continue
            for b in items:
                if b is a:
                    continue
                if b[0] >= a[0] and b[0] < a[1] - 0.02 and not (b[3] <= a[2] or b[2] >= a[3]) and b[0] > a[0] + 0.05:
                    print(f'  [{si}] bảng (đáy ước lượng {a[1]:.2f}") chồng lên khối bắt đầu y={b[0]:.2f}"')
                    problems += 1
    print('Tổng số vấn đề:', problems)


if __name__ == '__main__':
    check(sys.argv[1])
