#!/usr/bin/env python3
"""Dựng slide báo cáo kỹ thuật: slides_bao_cao_ky_thuat.pptx (python-pptx).

Số liệu lấy từ file JSON do các script đo tạo ra (xem README_do_dac trong slide 'Phương pháp đo'):
  --bench   bench.json        thời gian từng công đoạn (benchmark độc lập)
  --live    live_probe.json   đo trên hệ thống đang chạy (WebSocket)
  --gt      gt_result.json    đối chiếu số xe đếm với vị trí xe thật trong Gazebo
"""
import argparse
import json
import statistics as st

from pptx import Presentation
from pptx.chart.data import CategoryChartData
from pptx.dml.color import RGBColor
from pptx.enum.chart import XL_CHART_TYPE, XL_LEGEND_POSITION, XL_LABEL_POSITION
from pptx.enum.shapes import MSO_CONNECTOR, MSO_SHAPE
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
from pptx.util import Emu, Inches, Pt

NAVY, ORANGE, TEAL = RGBColor(0x0F, 0x24, 0x33), RGBColor(0xF2, 0x8C, 0x28), RGBColor(0x1B, 0x8A, 0x8F)
LIGHT, MUTED, WHITE = RGBColor(0xEE, 0xF3, 0xF6), RGBColor(0x5B, 0x6B, 0x78), RGBColor(0xFF, 0xFF, 0xFF)
RED = RGBColor(0xB0, 0x3A, 0x2E)
TITLE_FONT, BODY_FONT, MONO = 'Cambria', 'Calibri', 'Consolas'
SW, SH = 13.333, 7.5

prs = Presentation()
prs.slide_width, prs.slide_height = Inches(SW), Inches(SH)
BLANK = prs.slide_layouts[6]
_n = [0]


def tb(slide, x, y, w, h, text='', size=14, bold=False, color=NAVY, font=BODY_FONT, align=PP_ALIGN.LEFT,
       anchor=MSO_ANCHOR.TOP, name=None):
    s = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    if name:
        s.name = name
    tf = s.text_frame
    tf.word_wrap = True
    tf.margin_left = tf.margin_right = Inches(0.05)
    tf.margin_top = tf.margin_bottom = Inches(0.03)
    tf.vertical_anchor = anchor
    lines = text if isinstance(text, list) else [text]
    for i, ln in enumerate(lines):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.alignment = align
        runs = ln if isinstance(ln, list) else [(ln, {})]
        for t, o in runs:
            r = p.add_run()
            r.text = t
            r.font.size = Pt(o.get('size', size))
            r.font.bold = o.get('bold', bold)
            r.font.name = o.get('font', font)
            r.font.color.rgb = o.get('color', color)
    return s


def bullets(slide, x, y, w, h, items, size=14, gap=4, color=NAVY):
    s = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    tf = s.text_frame
    tf.word_wrap = True
    tf.margin_left = tf.margin_right = Inches(0.05)
    for i, it in enumerate(items):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.space_after = Pt(gap)
        runs = it if isinstance(it, list) else [(it, {})]
        first = True
        for t, o in runs:
            r = p.add_run()
            r.text = ('• ' if first else '') + t
            first = False
            r.font.size = Pt(o.get('size', size))
            r.font.bold = o.get('bold', False)
            r.font.name = o.get('font', BODY_FONT)
            r.font.color.rgb = o.get('color', color)
    return s


def box(slide, x, y, w, h, text='', fill=LIGHT, line=None, size=12, bold=False, color=NAVY, font=BODY_FONT,
        shape=MSO_SHAPE.RECTANGLE, align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE):
    s = slide.shapes.add_shape(shape, Inches(x), Inches(y), Inches(w), Inches(h))
    s.shadow.inherit = False
    if fill is None:
        s.fill.background()
    else:
        s.fill.solid()
        s.fill.fore_color.rgb = fill
    if line is None:
        s.line.fill.background()
    else:
        s.line.color.rgb = line
        s.line.width = Pt(1.25)
    tf = s.text_frame
    tf.word_wrap = True
    tf.margin_left = tf.margin_right = Inches(0.06)
    tf.margin_top = tf.margin_bottom = Inches(0.03)
    tf.vertical_anchor = anchor
    lines = text if isinstance(text, list) else [text]
    for i, ln in enumerate(lines):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.alignment = align
        runs = ln if isinstance(ln, list) else [(ln, {})]
        for t, o in runs:
            r = p.add_run()
            r.text = t
            r.font.size = Pt(o.get('size', size))
            r.font.bold = o.get('bold', bold)
            r.font.name = o.get('font', font)
            r.font.color.rgb = o.get('color', color)
    return s


def arrow(slide, x1, y1, x2, y2, color=MUTED, width=1.75, dash=False):
    c = slide.shapes.add_connector(MSO_CONNECTOR.STRAIGHT, Inches(x1), Inches(y1), Inches(x2), Inches(y2))
    c.line.color.rgb = color
    c.line.width = Pt(width)
    ln = c.line._get_or_add_ln()
    from lxml import etree
    ns = 'http://schemas.openxmlformats.org/drawingml/2006/main'
    tail = etree.SubElement(ln, f'{{{ns}}}tailEnd')
    tail.set('type', 'triangle')
    if dash:
        d = etree.SubElement(ln, f'{{{ns}}}prstDash')
        d.set('val', 'dash')
        ln.remove(d)
        ln.insert(1, d)
    return c


def new_slide(title, section=None, notes=None):
    s = prs.slides.add_slide(BLANK)
    _n[0] += 1
    if section:
        tb(s, 0.6, 0.28, 9, 0.3, section.upper(), size=11, bold=True, color=TEAL)
    tb(s, 0.6, 0.55, 12.1, 0.8, title, size=28, bold=True, font=TITLE_FONT, anchor=MSO_ANCHOR.MIDDLE, name='Title')
    tb(s, 12.2, 7.05, 0.6, 0.3, str(_n[0]), size=10, color=MUTED, align=PP_ALIGN.RIGHT)
    if notes:
        s.notes_slide.notes_text_frame.text = notes
    return s


def table(slide, x, y, w, rows, col_w, size=12, row_h=0.34, header_fill=NAVY, first_col_bold=False, mono_cols=()):
    nr, nc = len(rows), len(rows[0])
    gs = slide.shapes.add_table(nr, nc, Inches(x), Inches(y), Inches(w), Inches(row_h * nr))
    t = gs.table
    tblPr = gs._element.graphic.graphicData.tbl.tblPr
    tblPr.set('bandRow', '0')
    tblPr.set('firstRow', '0')
    sid = tblPr.find('{http://schemas.openxmlformats.org/drawingml/2006/main}tableStyleId')
    if sid is not None:
        sid.text = '{5940675A-B579-460E-94D1-54222C63F5DA}'  # No Style, Table Grid
    tot = sum(col_w)
    for j, cw in enumerate(col_w):
        t.columns[j].width = Inches(w * cw / tot)
    for i, row in enumerate(rows):
        t.rows[i].height = Inches(row_h)
        for j, val in enumerate(row):
            c = t.cell(i, j)
            c.margin_left = c.margin_right = Inches(0.07)
            c.margin_top = c.margin_bottom = Inches(0.025)
            c.vertical_anchor = MSO_ANCHOR.MIDDLE
            tf = c.text_frame
            tf.word_wrap = True
            p = tf.paragraphs[0]
            r = p.add_run()
            r.text = str(val)
            r.font.size = Pt(size)
            r.font.name = MONO if (j in mono_cols and i > 0) else BODY_FONT
            if i == 0:
                r.font.bold = True
                r.font.color.rgb = WHITE
                c.fill.solid()
                c.fill.fore_color.rgb = header_fill
            else:
                r.font.bold = first_col_bold and j == 0
                r.font.color.rgb = NAVY
                c.fill.solid()
                c.fill.fore_color.rgb = WHITE if i % 2 else LIGHT
    return gs


def style_chart(ch, legend=False, size=11):
    ch.font.size = Pt(size)
    ch.font.name = BODY_FONT
    ch.font.color.rgb = NAVY
    ch.has_legend = legend
    if legend:
        ch.legend.position = XL_LEGEND_POSITION.BOTTOM
        ch.legend.include_in_layout = False
        ch.legend.font.size = Pt(size)
