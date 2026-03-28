#!/usr/bin/env python3
"""Create IONE manuscript Japanese figure/table PowerPoint with 1 item per slide."""

from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE
import os

prs = Presentation()
prs.slide_width = Inches(13.333)
prs.slide_height = Inches(7.5)

FIG_SIM = '/home/ubuntu/repos/stratification_project/results/figures'
FIG_RD = '/home/ubuntu/repos/stratification_project/results/real_data'

# Colours
BLUE = RGBColor(0x1F, 0x77, 0xB4)
ORANGE = RGBColor(0xFF, 0x7F, 0x0E)
GREEN = RGBColor(0x2C, 0xA0, 0x2C)
RED = RGBColor(0xD6, 0x27, 0x28)
PURPLE = RGBColor(0x94, 0x67, 0xBD)
DARK = RGBColor(0x33, 0x33, 0x33)
WHITE = RGBColor(0xFF, 0xFF, 0xFF)
HEADER_BG = RGBColor(0x1F, 0x77, 0xB4)


def add_title_footer(slide, title_text, subtitle_text=""):
    left = Inches(0)
    top = Inches(0)
    width = prs.slide_width
    height = Inches(0.9)
    shape = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, left, top, width, height)
    shape.fill.solid()
    shape.fill.fore_color.rgb = HEADER_BG
    shape.line.fill.background()
    tf = shape.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = title_text
    p.font.size = Pt(26)
    p.font.color.rgb = WHITE
    p.font.bold = True
    p.alignment = PP_ALIGN.LEFT
    tf.margin_left = Inches(0.5)
    tf.vertical_anchor = MSO_ANCHOR.MIDDLE

    if subtitle_text:
        txBox = slide.shapes.add_textbox(Inches(0.5), Inches(0.95), Inches(8.0), Inches(0.35))
        tf2 = txBox.text_frame
        tf2.word_wrap = True
        p2 = tf2.paragraphs[0]
        p2.text = subtitle_text
        p2.font.size = Pt(13)
        p2.font.color.rgb = DARK
        p2.font.italic = True


def add_image_slide(prs, title, subtitle, img_path):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    add_title_footer(slide, title, subtitle)

    if os.path.exists(img_path):
        from PIL import Image
        img = Image.open(img_path)
        img_w, img_h = img.size
        aspect = img_w / img_h

        max_w = Inches(11.5)
        max_h = Inches(5.8)
        if aspect > (max_w / max_h):
            w = max_w
            h = int(w / aspect)
        else:
            h = max_h
            w = int(h * aspect)

        left = int((prs.slide_width - w) / 2)
        top = Inches(1.4)
        slide.shapes.add_picture(img_path, left, top, w, h)
    else:
        txBox = slide.shapes.add_textbox(Inches(2), Inches(3), Inches(9), Inches(1))
        tf = txBox.text_frame
        tf.paragraphs[0].text = f"[図版未検出: {img_path}]"
        tf.paragraphs[0].font.size = Pt(18)
        tf.paragraphs[0].font.color.rgb = RED


def add_table_slide(prs, title, subtitle, headers, rows, col_widths=None):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    add_title_footer(slide, title, subtitle)

    n_rows = 1 + len(rows)
    n_cols = len(headers)

    if col_widths is None:
        total_w = Inches(12)
        cw = total_w // n_cols
        col_widths = [cw] * n_cols

    total_w = sum(col_widths)
    left = int((prs.slide_width - total_w) / 2)
    top = Inches(1.5)
    table_shape = slide.shapes.add_table(n_rows, n_cols, left, top, total_w, Inches(0.4 * n_rows))
    table = table_shape.table

    for i, w in enumerate(col_widths):
        table.columns[i].width = w

    for i, h in enumerate(headers):
        cell = table.cell(0, i)
        cell.text = h
        cell.fill.solid()
        cell.fill.fore_color.rgb = HEADER_BG
        for p in cell.text_frame.paragraphs:
            p.font.size = Pt(11)
            p.font.color.rgb = WHITE
            p.font.bold = True
            p.alignment = PP_ALIGN.CENTER
        cell.vertical_anchor = MSO_ANCHOR.MIDDLE

    for r_idx, row in enumerate(rows):
        for c_idx, val in enumerate(row):
            cell = table.cell(r_idx + 1, c_idx)
            cell.text = str(val)
            if r_idx % 2 == 0:
                cell.fill.solid()
                cell.fill.fore_color.rgb = RGBColor(0xE8, 0xF0, 0xFE)
            else:
                cell.fill.solid()
                cell.fill.fore_color.rgb = WHITE
            for p in cell.text_frame.paragraphs:
                p.font.size = Pt(10)
                p.font.color.rgb = DARK
                p.alignment = PP_ALIGN.CENTER
            cell.vertical_anchor = MSO_ANCHOR.MIDDLE


def add_editable_dag(prs):
    """因果DAG（編集可能）

    Z-order（背面→前面）:
      1. タイトルバー＋サブタイトル
      2. コネクタ（線）
      3. 矢印ラベル
      4. 列ヘッダラベル
      5. 図形シェイプ（Z, X, Y ボックス）-- 最前面
    """
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    add_title_footer(slide, "因果有向非巡回グラフ（DAG）",
                     "データ生成メカニズム：Z（重大変数）\u2192 X（一般変数）\u2192 Y（アウトカム）")

    # --- Layer 2: コネクタ（低z） ---
    cxn = slide.shapes.add_connector(1, Inches(3.3), Inches(3.5), Inches(4.9), Inches(3.5))
    cxn.line.color.rgb = PURPLE
    cxn.line.width = Pt(3)
    cxn2 = slide.shapes.add_connector(1, Inches(7.9), Inches(3.5), Inches(9.4), Inches(3.5))
    cxn2.line.color.rgb = PURPLE
    cxn2.line.width = Pt(3)
    cxn3 = slide.shapes.add_connector(1, Inches(3.3), Inches(5.5), Inches(9.4), Inches(4.2))
    cxn3.line.color.rgb = ORANGE
    cxn3.line.width = Pt(2)
    cxn3.line.dash_style = 4

    # --- Layer 3: 矢印ラベル ---
    arrow_label = slide.shapes.add_textbox(Inches(3.4), Inches(2.7), Inches(1.5), Inches(0.5))
    tf = arrow_label.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "Z \u2192 X"
    p.font.size = Pt(12)
    p.font.bold = True
    p.font.color.rgb = PURPLE
    p.alignment = PP_ALIGN.CENTER
    p2 = tf.add_paragraph()
    p2.text = "(\u03b1_jl)"
    p2.font.size = Pt(10)
    p2.font.color.rgb = PURPLE
    p2.alignment = PP_ALIGN.CENTER

    arrow_label2 = slide.shapes.add_textbox(Inches(8.1), Inches(2.7), Inches(1.3), Inches(0.5))
    tf = arrow_label2.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "X \u2192 Y"
    p.font.size = Pt(12)
    p.font.bold = True
    p.font.color.rgb = PURPLE
    p.alignment = PP_ALIGN.CENTER
    p2 = tf.add_paragraph()
    p2.text = "(\u03b2_Xj)"
    p2.font.size = Pt(10)
    p2.font.color.rgb = PURPLE
    p2.alignment = PP_ALIGN.CENTER

    # Z->Yラベルを X列の下に配置（重なり回避）
    arrow_label3 = slide.shapes.add_textbox(Inches(3.5), Inches(6.6), Inches(5.5), Inches(0.4))
    p = arrow_label3.text_frame.paragraphs[0]
    p.text = "Z \u2192 Y（直接効果：\u03b2_Zl, OR 1.5\u20133.0）"
    p.font.size = Pt(12)
    p.font.bold = True
    p.font.color.rgb = ORANGE
    p.alignment = PP_ALIGN.CENTER

    # --- Layer 4: 列ヘッダラベル ---
    lbl = slide.shapes.add_textbox(Inches(1.0), Inches(1.6), Inches(2.2), Inches(0.35))
    lbl.text_frame.paragraphs[0].text = "重大変数 Z（意図的に除外）"
    lbl.text_frame.paragraphs[0].font.size = Pt(12)
    lbl.text_frame.paragraphs[0].font.bold = True
    lbl.text_frame.paragraphs[0].font.color.rgb = BLUE
    lbl.text_frame.paragraphs[0].alignment = PP_ALIGN.CENTER

    lbl2 = slide.shapes.add_textbox(Inches(5.0), Inches(1.45), Inches(2.8), Inches(0.35))
    lbl2.text_frame.paragraphs[0].text = "一般変数 X（測定済み）"
    lbl2.text_frame.paragraphs[0].font.size = Pt(12)
    lbl2.text_frame.paragraphs[0].font.bold = True
    lbl2.text_frame.paragraphs[0].font.color.rgb = GREEN
    lbl2.text_frame.paragraphs[0].alignment = PP_ALIGN.CENTER

    lbl3 = slide.shapes.add_textbox(Inches(9.5), Inches(2.5), Inches(2.5), Inches(0.35))
    lbl3.text_frame.paragraphs[0].text = "アウトカム"
    lbl3.text_frame.paragraphs[0].font.size = Pt(12)
    lbl3.text_frame.paragraphs[0].font.bold = True
    lbl3.text_frame.paragraphs[0].font.color.rgb = RED
    lbl3.text_frame.paragraphs[0].alignment = PP_ALIGN.CENTER

    # --- Layer 5: 図形シェイプ（最前面） ---

    # Z変数（左列）
    z_vars = [
        ("Z\u2081（年齢）", "N(60, 12\u00b2)"),
        ("Z\u2082（性別）", "Bernoulli(0.5)"),
        ("Z\u2083（BMI区分）", "3水準"),
    ]
    z_x = Inches(1.0)
    z_start_y = Inches(2.1)
    z_spacing = Inches(1.5)
    z_w = Inches(2.2)
    z_h = Inches(0.9)

    for i, (name, dist) in enumerate(z_vars):
        y = z_start_y + i * z_spacing
        shape = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, z_x, y, z_w, z_h)
        shape.fill.solid()
        shape.fill.fore_color.rgb = RGBColor(0xE3, 0xF2, 0xFD)
        shape.line.color.rgb = BLUE
        shape.line.width = Pt(2)
        tf = shape.text_frame
        tf.word_wrap = True
        p = tf.paragraphs[0]
        p.text = name
        p.font.size = Pt(14)
        p.font.bold = True
        p.font.color.rgb = BLUE
        p.alignment = PP_ALIGN.CENTER
        p2 = tf.add_paragraph()
        p2.text = dist
        p2.font.size = Pt(10)
        p2.font.color.rgb = DARK
        p2.alignment = PP_ALIGN.CENTER

    # X変数（中央列）
    x_x = Inches(5.0)
    x_start_y = Inches(1.9)
    x_spacing = Inches(0.5)
    x_w = Inches(2.8)
    x_h = Inches(0.42)
    x_labels = ["X\u2081（HbA1c）", "X\u2082（コレステロール）", "X\u2083（収縮期血圧）", "X\u2084（ALT）",
                "X\u2085（クレアチニン）", "X\u2086（ヘモグロビン）", "X\u2087（白血球数）", "X\u2088（アルブミン）",
                "X\u2089（CRP）", "X\u2081\u2080（尿酸）"]

    for i, label in enumerate(x_labels):
        y = x_start_y + i * x_spacing
        shape = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, x_x, y, x_w, x_h)
        shape.fill.solid()
        shape.fill.fore_color.rgb = RGBColor(0xE8, 0xF5, 0xE9)
        shape.line.color.rgb = GREEN
        shape.line.width = Pt(1)
        tf = shape.text_frame
        tf.word_wrap = True
        p = tf.paragraphs[0]
        p.text = label
        p.font.size = Pt(10)
        p.font.color.rgb = DARK
        p.alignment = PP_ALIGN.CENTER
        tf.vertical_anchor = MSO_ANCHOR.MIDDLE

    # Yアウトカム（右列）
    y_x = Inches(9.5)
    y_y = Inches(3.0)
    y_w = Inches(2.5)
    y_h = Inches(1.2)
    shape = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, y_x, y_y, y_w, y_h)
    shape.fill.solid()
    shape.fill.fore_color.rgb = RGBColor(0xFC, 0xE4, 0xEC)
    shape.line.color.rgb = RED
    shape.line.width = Pt(2)
    tf = shape.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "Y（二値アウトカム）"
    p.font.size = Pt(14)
    p.font.bold = True
    p.font.color.rgb = RED
    p.alignment = PP_ALIGN.CENTER
    p2 = tf.add_paragraph()
    p2.text = "イベント率 10\u201320%"
    p2.font.size = Pt(10)
    p2.font.color.rgb = DARK
    p2.alignment = PP_ALIGN.CENTER


def add_editable_workflow(prs):
    """IONEワークフロー（編集可能）

    Z-order: タイトル -> コネクタ -> 判定ダイヤモンド -> ステージボックス（最前面）
    """
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    add_title_footer(slide, "IONEフレームワーク：二段階ワークフロー",
                     "第1段階：検出（C1コヒーレンス指標）\u2192 第2段階：抽出（層別化）")

    # --- コネクタ（低z、先に追加） ---
    arrow_positions = [
        (Inches(2.7), Inches(3.8), Inches(3.0), Inches(3.8)),
        (Inches(6.2), Inches(3.8), Inches(6.5), Inches(3.8)),
        (Inches(9.7), Inches(3.8), Inches(10.0), Inches(3.8)),
    ]
    for x1, y1, x2, y2 in arrow_positions:
        cxn = slide.shapes.add_connector(1, x1, y1, x2, y2)
        cxn.line.color.rgb = DARK
        cxn.line.width = Pt(3)

    # --- 判定ダイヤモンドとはい/いいえラベル（中間z） ---
    diamond = slide.shapes.add_shape(MSO_SHAPE.DIAMOND,
                                     Inches(3.6), Inches(6.0),
                                     Inches(1.8), Inches(1.0))
    diamond.fill.solid()
    diamond.fill.fore_color.rgb = RGBColor(0xFF, 0xF3, 0xE0)
    diamond.line.color.rgb = ORANGE
    diamond.line.width = Pt(2)
    tf = diamond.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "C1 < 0.05?"
    p.font.size = Pt(11)
    p.font.bold = True
    p.font.color.rgb = ORANGE
    p.alignment = PP_ALIGN.CENTER
    tf.vertical_anchor = MSO_ANCHOR.MIDDLE

    yes_lbl = slide.shapes.add_textbox(Inches(5.5), Inches(6.2),
                                       Inches(1.5), Inches(0.4))
    yes_lbl.text_frame.paragraphs[0].text = "はい \u2192"
    yes_lbl.text_frame.paragraphs[0].font.size = Pt(11)
    yes_lbl.text_frame.paragraphs[0].font.bold = True
    yes_lbl.text_frame.paragraphs[0].font.color.rgb = GREEN

    no_lbl = slide.shapes.add_textbox(Inches(1.5), Inches(6.2),
                                      Inches(2.0), Inches(0.4))
    no_lbl.text_frame.paragraphs[0].text = "\u2190 いいえ（コヒーレント）"
    no_lbl.text_frame.paragraphs[0].font.size = Pt(11)
    no_lbl.text_frame.paragraphs[0].font.bold = True
    no_lbl.text_frame.paragraphs[0].font.color.rgb = RED

    # --- ステージボックス（最前面、最高z） ---
    stages = [
        {
            "title": "入力データ",
            "desc": "観察研究\nN個の観測\nX1...X10（測定済み）\nY（アウトカム）\n（Zは未測定）",
            "x": Inches(0.3), "y": Inches(2.0),
            "w": Inches(2.3), "h": Inches(3.5),
            "color": RGBColor(0xE0, 0xE0, 0xE0),
            "border": DARK,
        },
        {
            "title": "第1段階：検出",
            "desc": "C1コヒーレンス指標を\nI^2異質性統計量から算出\n\nC1 < 0.05 -> インコヒーレント\nC1 >= 0.05 -> コヒーレント\n\n「警告」機能\n仮定不要",
            "x": Inches(3.1), "y": Inches(1.6),
            "w": Inches(3.0), "h": Inches(4.2),
            "color": RGBColor(0xE3, 0xF2, 0xFD),
            "border": BLUE,
        },
        {
            "title": "第2段階：抽出",
            "desc": "インコヒーレントな場合：\n\nファミリー1（決定力ベース）\n  1A 予測確率\n  1B 残差\n  1C 交差検証型\n  1D ML不確実性\n\nファミリー2（特徴量得点ベース）\n  2A PCA\n  2B クラスタリング",
            "x": Inches(6.6), "y": Inches(1.6),
            "w": Inches(3.0), "h": Inches(4.2),
            "color": RGBColor(0xE8, 0xF5, 0xE9),
            "border": GREEN,
        },
        {
            "title": "出力",
            "desc": "コヒーレントな部分集団\nによる正しい推論\n\nバイアスの軽減\nパラドックスの解消\n効果修飾の検出",
            "x": Inches(10.1), "y": Inches(2.0),
            "w": Inches(2.8), "h": Inches(3.5),
            "color": RGBColor(0xFC, 0xE4, 0xEC),
            "border": RED,
        },
    ]

    for s in stages:
        shape = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE,
                                       s["x"], s["y"], s["w"], s["h"])
        shape.fill.solid()
        shape.fill.fore_color.rgb = s["color"]
        shape.line.color.rgb = s["border"]
        shape.line.width = Pt(2)
        tf = shape.text_frame
        tf.word_wrap = True
        tf.margin_left = Inches(0.1)
        tf.margin_right = Inches(0.1)
        p = tf.paragraphs[0]
        p.text = s["title"]
        p.font.size = Pt(14)
        p.font.bold = True
        p.font.color.rgb = s["border"]
        p.alignment = PP_ALIGN.CENTER
        p2 = tf.add_paragraph()
        p2.text = ""
        p3 = tf.add_paragraph()
        p3.text = s["desc"]
        p3.font.size = Pt(10)
        p3.font.color.rgb = DARK
        p3.alignment = PP_ALIGN.LEFT


def add_editable_method_overview(prs):
    """手法概観（編集可能）

    Z-order: タイトル -> ファミリーヘッダ（低z） -> 手法ボックス（最前面）
    """
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    add_title_footer(slide, "IONE手法の概観",
                     "2ファミリーの層別化手法 + ベースライン")

    families = [
        {
            "title": "ファミリー1：決定力ベース\n（アウトカム使用）",
            "methods": [
                "1A：予測確率\nロジスティック回帰 P(Y|X) \u2192 分位層別化",
                "1B：残差\n|Y \u2212 \u0070\u0302| \u2192 分位層別化（最も頑健）",
                "1C：交差検証型\nK-fold CVで過学習を回避",
                "1D：ML不確実性\nランダムフォレスト予測分散 \u2192 層別化",
            ],
            "x": Inches(0.5), "color": BLUE,
        },
        {
            "title": "ファミリー2：特徴量得点ベース\n（アウトカム不使用）",
            "methods": [
                "2A：PCA\n第1主成分得点 \u2192 分位層別化",
                "2B：クラスタリング\nk-means on X \u2192 クラスタ＝層",
            ],
            "x": Inches(5.0), "color": GREEN,
        },
        {
            "title": "ベースライン",
            "methods": [
                "ランダム：無作為割当（下限）",
                "Oracle：k-means on Z（上限）",
            ],
            "x": Inches(9.5), "color": DARK,
        },
    ]

    # 全ファミリーヘッダを先に追加（低z）
    for fam in families:
        hdr = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE,
                                     fam["x"], Inches(1.6), Inches(3.5), Inches(0.9))
        hdr.fill.solid()
        hdr.fill.fore_color.rgb = fam["color"]
        hdr.line.fill.background()
        tf = hdr.text_frame
        tf.word_wrap = True
        p = tf.paragraphs[0]
        p.text = fam["title"]
        p.font.size = Pt(13)
        p.font.bold = True
        p.font.color.rgb = WHITE
        p.alignment = PP_ALIGN.CENTER
        tf.vertical_anchor = MSO_ANCHOR.MIDDLE

    # 次に全手法ボックス（高z、最前面）
    for fam in families:
        for i, m in enumerate(fam["methods"]):
            y = Inches(2.7) + i * Inches(1.15)
            box = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE,
                                         fam["x"], y, Inches(3.5), Inches(1.0))
            box.fill.solid()
            box.fill.fore_color.rgb = WHITE
            box.line.color.rgb = fam["color"]
            box.line.width = Pt(1.5)
            tf = box.text_frame
            tf.word_wrap = True
            tf.margin_left = Inches(0.1)
            lines = m.split("\n")
            p = tf.paragraphs[0]
            p.text = lines[0]
            p.font.size = Pt(11)
            p.font.bold = True
            p.font.color.rgb = fam["color"]
            if len(lines) > 1:
                p2 = tf.add_paragraph()
                p2.text = lines[1]
                p2.font.size = Pt(9)
                p2.font.color.rgb = DARK


def add_editable_application_guidance(prs):
    """適用ガイダンス（編集可能）

    Z-order: タイトル -> コネクタ（低z） -> ボックス（最前面）
    """
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    add_title_footer(slide, "IONE適用ガイダンス",
                     "\u03b7\u00b2とサブグループ構造に基づく判断フレームワーク")

    scenarios = [
        {
            "condition": "\u03b7\u00b2 > 0.4\n2\u301c3の離散的サブグループ",
            "method": "特徴量得点ベース\nクラスタリング（2B）",
            "expected": "ARI > 0.7",
            "example": "腎結石、イスラエルワクチン",
            "color": GREEN,
        },
        {
            "condition": "0.15 < \u03b7\u00b2 \u2264 0.4\n多群・連続的",
            "method": "決定力ベース（1A, 1B）\n両ファミリー推奨",
            "expected": "ARI 0.1\u20130.5",
            "example": "喫煙\u30fb死亡率",
            "color": ORANGE,
        },
        {
            "condition": "\u03b7\u00b2 < 0.15\n弱い痕跡",
            "method": "C1検出のみ\n抽出は限定的",
            "expected": "ARI < 0.1",
            "example": "COVID-19、バークレー",
            "color": RED,
        },
    ]

    # 全コネクタを先に追加（低z）
    for i in range(3):
        y = Inches(1.8) + i * Inches(1.8)
        cxn = slide.shapes.add_connector(1, Inches(3.6), y + Inches(0.7),
                                         Inches(4.0), y + Inches(0.7))
        cxn.line.color.rgb = DARK
        cxn.line.width = Pt(2)
        cxn2 = slide.shapes.add_connector(1, Inches(7.4), y + Inches(0.7),
                                          Inches(7.8), y + Inches(0.7))
        cxn2.line.color.rgb = DARK
        cxn2.line.width = Pt(2)

    # 次に全ボックス（高z、最前面）
    for i, s in enumerate(scenarios):
        y = Inches(1.8) + i * Inches(1.8)

        box1 = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE,
                                      Inches(0.5), y, Inches(3.0), Inches(1.4))
        box1.fill.solid()
        box1.fill.fore_color.rgb = WHITE
        box1.line.color.rgb = s["color"]
        box1.line.width = Pt(2)
        tf = box1.text_frame
        tf.word_wrap = True
        p = tf.paragraphs[0]
        p.text = s["condition"]
        p.font.size = Pt(12)
        p.font.bold = True
        p.font.color.rgb = s["color"]
        p.alignment = PP_ALIGN.CENTER
        tf.vertical_anchor = MSO_ANCHOR.MIDDLE

        box2 = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE,
                                      Inches(4.1), y, Inches(3.2), Inches(1.4))
        box2.fill.solid()
        box2.fill.fore_color.rgb = RGBColor(0xF5, 0xF5, 0xF5)
        box2.line.color.rgb = s["color"]
        box2.line.width = Pt(1.5)
        tf = box2.text_frame
        tf.word_wrap = True
        p = tf.paragraphs[0]
        p.text = s["method"]
        p.font.size = Pt(11)
        p.font.bold = True
        p.font.color.rgb = DARK
        p.alignment = PP_ALIGN.CENTER
        tf.vertical_anchor = MSO_ANCHOR.MIDDLE

        box3 = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE,
                                      Inches(7.9), y, Inches(2.5), Inches(1.4))
        box3.fill.solid()
        box3.fill.fore_color.rgb = WHITE
        box3.line.color.rgb = s["color"]
        box3.line.width = Pt(1.5)
        tf = box3.text_frame
        tf.word_wrap = True
        p = tf.paragraphs[0]
        p.text = f"期待値: {s['expected']}"
        p.font.size = Pt(12)
        p.font.bold = True
        p.font.color.rgb = s["color"]
        p.alignment = PP_ALIGN.CENTER
        p2 = tf.add_paragraph()
        p2.text = s["example"]
        p2.font.size = Pt(10)
        p2.font.color.rgb = DARK
        p2.alignment = PP_ALIGN.CENTER
        tf.vertical_anchor = MSO_ANCHOR.MIDDLE


# ============================================================
# BUILD SLIDES
# ============================================================

# --- Title slide ---
slide = prs.slides.add_slide(prs.slide_layouts[6])
bg = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, prs.slide_width, prs.slide_height)
bg.fill.solid()
bg.fill.fore_color.rgb = HEADER_BG
bg.line.fill.background()
tf = bg.text_frame
tf.word_wrap = True
tf.vertical_anchor = MSO_ANCHOR.MIDDLE
p = tf.paragraphs[0]
p.text = "IONE"
p.font.size = Pt(54)
p.font.color.rgb = WHITE
p.font.bold = True
p.alignment = PP_ALIGN.CENTER
p2 = tf.add_paragraph()
p2.text = "インコヒーレンス指向の中和と抽出\n観察研究における隠れた集団構造の検出"
p2.font.size = Pt(20)
p2.font.color.rgb = WHITE
p2.alignment = PP_ALIGN.CENTER
p3 = tf.add_paragraph()
p3.text = ""
p4 = tf.add_paragraph()
p4.text = "図表集"
p4.font.size = Pt(16)
p4.font.color.rgb = RGBColor(0xBB, 0xDE, 0xFB)
p4.alignment = PP_ALIGN.CENTER
p5 = tf.add_paragraph()
p5.text = "BMC Medical Research Methodology"
p5.font.size = Pt(14)
p5.font.color.rgb = RGBColor(0xBB, 0xDE, 0xFB)
p5.alignment = PP_ALIGN.CENTER

# --- Editable diagrams ---
add_editable_dag(prs)
add_editable_workflow(prs)
add_editable_method_overview(prs)
add_editable_application_guidance(prs)

# --- Table 1 ---
add_table_slide(prs, "表1. 既報シンプソンのパラドックス事例",
    "実データ検証に使用した5つの事例",
    ["事例", "出典", "N", "隠れた交絡因子", "群数", "パラドックスの内容"],
    [
        ["COVID-19致死率", "von Kugelgen 2021", "50,459", "年齢群", "9", "全体ではイタリア＞中国だが、各年齢群ではイタリア＜中国"],
        ["腎結石治療", "Charig 1986", "700", "結石サイズ", "2", "全体ではB＞Aだが、大小とも A＞B"],
        ["UCバークレー入学", "Bickel 1975", "4,425", "学部", "6", "全体では男性＞女性だが、多くの学部では逆転"],
        ["イスラエルワクチン", "Morris 2021", "6,100", "年齢群", "2", "全体ではワクチン無効だが、両群で有効"],
        ["喫煙・死亡率", "Appleton 1996", "1,314", "年齢群", "7", "全体では喫煙者が低死亡率だが、各群で高死亡率"],
    ],
    [Inches(1.5), Inches(1.5), Inches(0.8), Inches(1.3), Inches(0.6), Inches(5.5)]
)

# --- Table 2 ---
add_table_slide(prs, "表2. Phase 1シミュレーション 手法別性能ランキング",
    "全シナリオ平均（N=2,000；シナリオあたり200反復）",
    ["順位", "手法", "ファミリー", "ARI", "NMI", "η²（平均）", "C1"],
    [
        ["1", "Oracle（k-means on Z）", "ベースライン（上限）", "0.353", "0.616", "0.562", "0.019"],
        ["2", "Oracle（quantile on Z）", "ベースライン（上限）", "0.073", "0.260", "0.283", "0.010"],
        ["3", "1B：残差", "決定力ベース", "0.020", "0.069", "0.091", "0.001"],
        ["4", "1D：ML不確実性", "決定力ベース", "0.017", "0.056", "0.074", "0.001"],
        ["5", "1A：予測確率", "決定力ベース", "0.014", "0.053", "0.069", "0.022"],
        ["6", "1C：交差検証型", "決定力ベース", "0.014", "0.051", "0.067", "0.028"],
        ["7", "2A：PCA（k=2）", "特徴量得点", "0.012", "0.042", "0.052", "0.098"],
        ["8", "2A：PCA（k=1）", "特徴量得点", "0.011", "0.047", "0.063", "0.095"],
        ["9", "2B：クラスタリング", "特徴量得点", "0.011", "0.041", "0.053", "0.079"],
        ["10", "ランダム", "ベースライン（下限）", "-0.000", "0.007", "0.002", "0.863"],
    ],
    [Inches(0.6), Inches(2.5), Inches(2.0), Inches(0.8), Inches(0.8), Inches(1.0), Inches(0.8)]
)

# --- Table 3 ---
add_table_slide(prs, "表3. Z→X影響度別ARI（K=5層）",
    "Z→X影響度が性能の最大の決定因子",
    ["手法", "zx=0.3（弱）", "zx=0.5（中）", "zx=1.0（強）", "強/弱比"],
    [
        ["1A：予測確率", "0.004", "0.010", "0.030", "8.7"],
        ["1B：残差", "0.014", "0.018", "0.029", "1.9"],
        ["1C：交差検証型", "0.003", "0.009", "0.029", "9.6"],
        ["2A：PCA（k=2）", "0.002", "0.006", "0.029", "18.3"],
        ["2B：クラスタリング", "0.002", "0.006", "0.025", "14.0"],
        ["Oracle（k-means on Z）", "0.378", "0.378", "0.380", "1.0"],
    ],
    [Inches(2.5), Inches(1.8), Inches(1.8), Inches(1.8), Inches(1.5)]
)

# --- Table 4 ---
add_table_slide(prs, "表4. 重大変数別イータ二乗η²（K=5, zx=1.0）",
    "年齢（連続）の捕捉が最良、性別（二値）は困難",
    ["手法", "Z1（年齢）", "Z2（性別）", "Z3（BMI）", "平均"],
    [
        ["Oracle（k-means on Z）", "0.312", "0.982", "0.663", "0.652"],
        ["1A：予測確率", "0.327", "0.008", "0.092", "0.142"],
        ["1C：交差検証型", "0.322", "0.007", "0.090", "0.140"],
        ["1B：残差", "0.295", "0.012", "0.093", "0.133"],
        ["2B：クラスタリング", "0.238", "0.026", "0.090", "0.118"],
        ["ランダム", "0.002", "0.002", "0.002", "0.002"],
    ],
    [Inches(2.8), Inches(1.5), Inches(1.5), Inches(1.5), Inches(1.2)]
)

# --- Table 5 ---
add_table_slide(prs, "表5. 感度分析におけるZ→X影響度別ARI",
    "Z→X影響度が最重要パラメータであることを確認",
    ["手法", "zx=0.2（弱）", "zx=0.5（中）", "zx=1.0（強）", "強/弱比"],
    [
        ["1A：予測確率", "0.002", "0.009", "0.028", "17.5"],
        ["1C：交差検証型", "0.001", "0.008", "0.027", "22.3"],
        ["2B：クラスタリング", "0.001", "0.006", "0.024", "34.3"],
        ["2A：PCA（60%）", "0.001", "0.004", "0.015", "30.8"],
    ],
    [Inches(2.5), Inches(1.8), Inches(1.8), Inches(1.8), Inches(1.5)]
)

# --- Simulation Figures ---
add_image_slide(prs,
    "図1. ARI・NMIヒートマップ（Phase 1シミュレーション）",
    "全Phase 1条件における手法×シナリオの性能",
    f"{FIG_SIM}/heatmap_ari_nmi.png")

add_image_slide(prs,
    "図2. Z→X影響度の効果（感度分析）",
    "弱条件から強条件でARIが最大18倍に増加",
    f"{FIG_SIM}/sensitivity_zx_influence.png")

add_image_slide(prs,
    "図3. 手法別・重大変数別イータ二乗（η²）",
    "年齢（連続）>> BMI（順序）>> 性別（二値）の差分捕捉",
    f"{FIG_SIM}/eta_squared.png")

add_image_slide(prs,
    "図4. 手法別コヒーレンス指標C1",
    "低C1 = インコヒーレンス検出成功；提案手法C1~0.001 vs ランダムC1~0.863",
    f"{FIG_SIM}/coherence_diagnosis.png")

add_image_slide(prs,
    "図5. サンプルサイズの効果（感度分析）",
    "N=500からN=10,000まで性能はほぼ一定",
    f"{FIG_SIM}/sensitivity_sample_size.png")

add_image_slide(prs,
    "図6. Phase 1シミュレーション サマリーダッシュボード",
    "全手法・全条件のシミュレーション結果の総括",
    f"{FIG_SIM}/summary_dashboard.png")

# --- Table 6 ---
add_table_slide(prs, "表6. 実データ検証結果サマリー",
    "5つの既報シンプソンのパラドックス事例へのIONE適用結果",
    ["事例", "最良手法", "最良ARI", "Oracle ARI", "達成率", "C1（最良）", "C1（ランダム）", "η²"],
    [
        ["腎結石", "2B クラスタリング", "0.851", "1.000", "85.1%", "0.034", "0.695", "0.428"],
        ["イスラエルワクチン", "2B クラスタリング", "0.746", "1.000", "74.6%", "0.005", "0.770", "0.432"],
        ["喫煙・死亡率", "1A 予測確率", "0.498", "1.000", "49.8%", "0.005", "1.000", "0.686"],
        ["UCバークレー", "1A 予測確率", "0.082", "1.000", "8.2%", "0.011", "0.954", "0.152"],
        ["COVID-19 CFR", "1B 残差", "0.064", "1.000", "6.4%", "0.001", "0.778", "0.171"],
    ],
    [Inches(1.5), Inches(1.5), Inches(0.9), Inches(0.9), Inches(0.8), Inches(1.0), Inches(1.0), Inches(0.8)]
)

# --- Real Data Figures ---
add_image_slide(prs,
    "図7. シンプソンのパラドックスの視覚的実証",
    "5つの既報事例におけるパラドックスの可視化",
    f"{FIG_RD}/fig1_paradox_demonstration.png")

add_image_slide(prs,
    "図8. コヒーレンス分析（C1）：全5事例",
    "全事例でC1がインコヒーレンスを正確に検出（C1=0.001-0.034 vs ランダムC1=0.695-1.000）",
    f"{FIG_RD}/fig3_coherence_analysis.png")

add_image_slide(prs,
    "図9. 手法間比較（ARI）：全5事例",
    "2群構造では2Bクラスタリングが最良、多群構造では1A/1Bが最良",
    f"{FIG_RD}/fig2_method_comparison.png")

add_image_slide(prs,
    "図10. イータ二乗（η²）ヒートマップ（実データ）",
    "高η²は高ARIと相関（シミュレーション結果と整合）",
    f"{FIG_RD}/fig4_eta_squared_heatmap.png")

add_image_slide(prs,
    "図11. 効果方向の一貫性分析",
    "層間での曝露-アウトカム関連の方向の一貫性",
    f"{FIG_RD}/fig5_direction_consistency.png")

add_image_slide(prs,
    "図12. 実データ検証 サマリーダッシュボード",
    "5つのシンプソンのパラドックス適用結果の総括",
    f"{FIG_RD}/fig6_summary_dashboard.png")

# --- Table 7 ---
add_table_slide(prs, "表7. シミュレーションと実データの一致性",
    "シミュレーションの主要知見が実データ検証で再現",
    ["知見", "シミュレーション", "実データ検証"],
    [
        ["1B残差が最も頑健", "最高ARI（0.020）", "COVID-19で最良（ARI=0.064）"],
        ["C1がインコヒーレンス検出", "ランダム0.863 vs 提案0.001", "ランダム0.70-1.00 vs 提案0.00-0.03"],
        ["Z→X影響度が決定的", "ARIがzxとともに増加", "高η² -> 高ARI"],
        ["全手法がランダムを上回る", "全シナリオ", "全5事例"],
    ],
    [Inches(2.5), Inches(3.5), Inches(3.5)]
)

# --- Save ---
outpath = '/home/ubuntu/repos/stratification_project/results/manuscript/IONE_figures_tables_JA.pptx'
prs.save(outpath)
print(f'Saved to {outpath}')
