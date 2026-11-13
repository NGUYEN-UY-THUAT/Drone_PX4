#!/usr/bin/env python3
"""Dựng slides_bao_cao_ky_thuat.pptx từ report_part_a/b/c/d/e.py (số liệu đọc từ measure/, ảnh từ measure/figs/).

Chạy trước (sinh PNG): python3 measure/fig_diagrams.py; python3 measure/fig_charts.py; python3 measure/fig_review.py;\n~/px4-venv/bin/python measure/fig_sim_results.py
"""
import os
import re

import report_part_a, report_part_b, report_part_c, report_part_d, report_part_e  # noqa: F401  (import = dựng slide)
from report_lib import prs, Inches, Pt, tb, MUTED

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'slides_bao_cao_ky_thuat.pptx')
N_OLD, N_D, N_E = 31, 13, 11
assert len(prs.slides) == N_OLD + N_D + N_E
o = lambda k: k - 1                  # slide gốc số k (1-based, đánh số trong report_part_a/b/c)
n = lambda i: N_OLD + i              # slide thứ i trong report_part_d
e = lambda i: N_OLD + N_D + i        # slide thứ i trong report_part_e
S1, S2, S3, S4, S5 = '1 · Hệ thống', '2 · Sự tương tác', '3 · Luồng dữ liệu', '4 · Công thức toán học', '5 · Độ phức tạp'
S6, S7, S8 = '6 · Web, backend và API', '7 · Kết quả đánh giá', '8 · Thời gian xử lý và realtime'
# (slide, nhãn mục) theo đúng thứ tự trình bày đã duyệt
plan = [(o(1), None), (o(2), None),
        (o(3), S1), (o(4), S1), (e(0), S1), (o(6), S1),
        (e(1), S2),
        (e(2), S3), (o(14), S3), (n(11), S3),
        (o(15), S4), (o(16), S4), (o(17), S4), (o(18), S4), (e(3), S4), (e(10), S4),
        (o(26), S5), (n(10), S5),
        (e(4), S6), (e(5), S6),
        (n(1), S7), (n(2), S7), (n(3), S7), (e(6), S7), (e(7), S7), (n(4), S7), (e(8), S7), (n(5), S7), (n(6), S7),
        (n(8), S8), (n(9), S8), (o(28), S8), (o(29), S8),
        (n(12), None), (e(9), None), (o(31), None)]
final = [p for p, _ in plan]
lst = prs.slides._sldIdLst
els = list(lst)
for i, el in enumerate(els):
    lst.remove(el)
    if i not in final:
        prs.part.drop_rel(el.rId)
for i in final:
    lst.append(els[i])
for pos, (_, label) in enumerate(plan):
    if label:
        for sh in prs.slides[pos].shapes:
            if sh.has_text_frame and abs(sh.top - Inches(0.28)) < 20000 and sh.left == Inches(0.6):
                sh.text_frame.paragraphs[0].runs[0].text = label.upper()

# đánh lại số trang và cập nhật mục lục (slide 2)
sec_pages = {}
for pos, s in enumerate(prs.slides, 1):
    for sh in s.shapes:
        if sh.has_text_frame and abs(sh.left - Inches(12.2)) < 20000 and abs(sh.top - Inches(7.05)) < 20000:
            sh.text_frame.paragraphs[0].runs[0].text = str(pos)
        elif sh.has_text_frame and abs(sh.top - Inches(0.28)) < 20000 and sh.left == Inches(0.6):
            m = re.match(r'(\d+) ·', sh.text_frame.text)
            key = int(m.group(1)) if m else 'end'
            sec_pages.setdefault(key, []).append(pos)
toc = [sh for sh in prs.slides[1].shapes if sh.has_table][0].table
rows = [('1', 'Hệ thống', 'Mục tiêu, công nghệ, sơ đồ khối, các khối chức năng'),
        ('2', 'Sự tương tác', 'Sơ đồ tương tác giữa các khối, kênh và giao thức'),
        ('3', 'Luồng dữ liệu', 'Sơ đồ luồng dữ liệu, giải thích từng bước, lưu đồ thuật toán đếm'),
        ('4', 'Công thức toán học', 'IoU/mAP, Kalman + ByteTrack, luật đếm, hình học camera, điều khiển UAV'),
        ('5', 'Độ phức tạp', 'Phân tích lý thuyết và đo thực nghiệm'),
        ('6', 'Web, backend và API', 'Giao thức WebSocket v1, backend, xác thực, giới hạn'),
        ('7', 'Kết quả đánh giá', 'Huấn luyện, ma trận nhầm lẫn, kết quả thực tế trong mô phỏng, độ chính xác đếm'),
        ('8', 'Thời gian xử lý và realtime', 'Thời gian từng công đoạn, độ trễ đầu cuối, FPS, nút thắt'),
        ('', 'Kết luận', 'Tổng hợp chỉ số, hạn chế và hướng cải thiện, phụ lục phương pháp đo')]
tbl = toc._tbl
trs = tbl.findall('{http://schemas.openxmlformats.org/drawingml/2006/main}tr')
for extra in trs[len(rows) + 1:]:
    tbl.remove(extra)
for r, (k, name, desc) in enumerate(rows, 1):
    for c, val in enumerate((k, name, desc)):
        cell = toc.cell(r, c)
        runs = cell.text_frame.paragraphs[0].runs
        if runs:
            runs[0].text = val
        elif val:
            cell.text_frame.paragraphs[0].add_run().text = val
    key = int(k) if k else 'end'
    pg = sec_pages[key]
    toc.cell(r, 3).text_frame.paragraphs[0].runs[0].text = f'{min(pg)}–{max(pg)}' if min(pg) != max(pg) else str(min(pg))
# sửa tham chiếu số slide trong bảng Realtime ("theo ví dụ slide 17") theo vị trí mới của slide Kalman
kal = next(p for p, sl in enumerate(prs.slides, 1) if any(sh.has_text_frame and 'Công thức: luật đếm' in sh.text_frame.text for sh in sl.shapes))
for sl in prs.slides:
    for sh in sl.shapes:
        if sh.has_table:
            for r in sh.table.rows:
                for c in r.cells:
                    for p in c.text_frame.paragraphs:
                        for run in p.runs:
                            if 'slide 17' in run.text:
                                run.text = run.text.replace('slide 17', f'slide {kal}')
prs.save(OUT)
print(OUT, len(prs.slides), 'slides', {k: (min(v), max(v)) for k, v in sec_pages.items()})
