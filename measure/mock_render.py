"""Vẽ gần đúng slide (hình khối, chữ, bảng, ảnh, mũi tên) bằng PIL để duyệt bố cục khi không có LibreOffice."""
import sys, io
from pptx import Presentation
from pptx.enum.shapes import MSO_SHAPE_TYPE
from PIL import Image, ImageDraw, ImageFont
sys.path.insert(0, __file__.rsplit('/', 1)[0])
from qa_layout import font, kind_of, CAL

DPI = 100
def rgb(c, d):
    try:
        return tuple(c.rgb) if c is not None and c.type is not None else d
    except Exception:
        return d

def draw_text(dr, tf, x, y, w, h, scale=DPI):
    from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
    lines = []
    for p in tf.paragraphs:
        runs = p.runs
        if not runs:
            lines.append(([], 12, p.alignment)); continue
        size = max((r.font.size.pt if r.font.size else 14) for r in runs)
        words = []
        for r in runs:
            for wd in r.text.split(' '):
                words.append((wd, kind_of(r), r.font.size.pt if r.font.size else 14, rgb(r.font.color, (15, 36, 51))))
        cur, curw, out = [], 0, []
        maxw = (w - 0.1) * 72
        for wd, k, sz, col in words:
            f = font(k, sz * scale / 72)
            ww = f.getlength(wd + ' ') * 72 / scale * (CAL if k.startswith('sans') else 1)
            if curw + ww > maxw and cur:
                out.append(cur); cur, curw = [], 0
            cur.append((wd, k, sz, col, ww)); curw += ww
        out.append(cur)
        for ln in out:
            lines.append((ln, size, p.alignment))
    total = sum(sz * 1.2 / 72 for _, sz, _ in lines)
    anc = tf.vertical_anchor
    yy = y + 0.03 if anc in (None, MSO_ANCHOR.TOP) else (y + (h - total) / 2 if anc == MSO_ANCHOR.MIDDLE else y + h - total - 0.03)
    for ln, sz, al in lines:
        lw = sum(t[4] for t in ln) / 72
        xx = x + 0.05
        if al == PP_ALIGN.CENTER: xx = x + (w - lw) / 2
        elif al == PP_ALIGN.RIGHT: xx = x + w - lw - 0.05
        for wd, k, s2, col, ww in ln:
            dr.text((xx * scale, yy * scale), wd, font=font(k, s2 * scale / 72), fill=col)
            xx += ww / 72
        yy += sz * 1.2 / 72

def render(path, idxs, out):
    prs = Presentation(path)
    W, H = int(prs.slide_width / 914400 * DPI), int(prs.slide_height / 914400 * DPI)
    for i in idxs:
        sl = prs.slides[i - 1]
        im = Image.new('RGB', (W, H), (255, 255, 255)); dr = ImageDraw.Draw(im)
        try:
            if sl.background.fill.type == 1: dr.rectangle([0, 0, W, H], fill=tuple(sl.background.fill.fore_color.rgb))
        except Exception: pass
        for sh in sl.shapes:
            x, y, w, h = [v / 914400 for v in (sh.left, sh.top, sh.width, sh.height)]
            box = [x * DPI, y * DPI, (x + w) * DPI, (y + h) * DPI]
            if sh.shape_type == MSO_SHAPE_TYPE.PICTURE:
                pic = Image.open(io.BytesIO(sh.image.blob)).convert('RGB').resize((int(w * DPI), int(h * DPI))); im.paste(pic, (int(x * DPI), int(y * DPI)))
            elif sh.has_chart if hasattr(sh, 'has_chart') else False:
                dr.rectangle(box, outline=(150, 150, 150)); dr.text((box[0] + 6, box[1] + 6), '[biểu đồ]', fill=(120, 120, 120), font=font('sans', 14))
            elif sh.has_table if hasattr(sh, 'has_table') else False:
                t = sh.table; yy = y
                for ri, row in enumerate(t.rows):
                    cx = x
                    rh = row.height / 914400
                    for ci, cell in enumerate(row.cells):
                        cw = t.columns[ci].width / 914400
                        col = (15, 36, 51) if ri == 0 else ((255, 255, 255) if ri % 2 else (238, 243, 246))
                        dr.rectangle([cx * DPI, yy * DPI, (cx + cw) * DPI, (yy + rh) * DPI], fill=col, outline=(200, 205, 210))
                        draw_text(dr, cell.text_frame, cx, yy, cw, rh); cx += cw
                    yy += rh
            elif sh.shape_type == MSO_SHAPE_TYPE.LINE or sh.shape_type is None and sh.__class__.__name__ == 'Connector':
                bx, by, ex, ey = [v / 914400 * DPI for v in (sh.begin_x, sh.begin_y, sh.end_x, sh.end_y)]
                dr.line([bx, by, ex, ey], fill=(242, 140, 40), width=3)
                import math
                a = math.atan2(ey - by, ex - bx); L = 9
                dr.polygon([(ex, ey), (ex - L * math.cos(a - .4), ey - L * math.sin(a - .4)), (ex - L * math.cos(a + .4), ey - L * math.sin(a + .4))], fill=(242, 140, 40))
            else:
                try:
                    if sh.fill.type == 1: dr.rectangle(box, fill=tuple(sh.fill.fore_color.rgb))
                    if sh.line.fill.type == 1: dr.rectangle(box, outline=tuple(sh.line.color.rgb), width=2)
                except Exception: pass
                if sh.has_text_frame: draw_text(dr, sh.text_frame, x, y, w, h)
        im.save(f'{out}/mock_{i:02d}.png')
if __name__ == '__main__':
    render(sys.argv[1], [int(a) for a in sys.argv[3:]], sys.argv[2])
