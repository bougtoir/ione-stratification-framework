#!/usr/bin/env python3
"""Create IONE manuscript English figure/table PowerPoint with 1 item per slide."""

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
LIGHT_BG = RGBColor(0xF5, 0xF5, 0xF5)
HEADER_BG = RGBColor(0x1F, 0x77, 0xB4)

def add_title_footer(slide, title_text, subtitle_text=""):
    """Add a title bar at top and optional subtitle."""
    # Title background bar
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
    p.font.size = Pt(28)
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
        p2.font.size = Pt(14)
        p2.font.color.rgb = DARK
        p2.font.italic = True

def add_image_slide(prs, title, subtitle, img_path):
    """Add a slide with a code-generated figure image."""
    slide = prs.slides.add_slide(prs.slide_layouts[6])  # blank
    add_title_footer(slide, title, subtitle)

    if os.path.exists(img_path):
        # Centre image on slide
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
        tf.paragraphs[0].text = f"[Image not found: {img_path}]"
        tf.paragraphs[0].font.size = Pt(18)
        tf.paragraphs[0].font.color.rgb = RED

def add_table_slide(prs, title, subtitle, headers, rows, col_widths=None):
    """Add a slide with an editable table."""
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

    # Header row
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

    # Data rows
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
    """Create editable Causal DAG slide (Z -> X -> Y).

    Z-order (back to front):
      1. Title bar + subtitle (from add_title_footer)
      2. Connectors (lines)
      3. Arrow labels
      4. Column header labels
      5. Diagram shapes (Z, X, Y boxes) -- FRONT
    """
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    add_title_footer(slide, "Causal Directed Acyclic Graph (DAG)",
                     "Data-generating mechanism: Z (critical) -> X (general) -> Y (outcome)")

    # --- Layer 2: Connectors (lowest z after title) ---
    cxn = slide.shapes.add_connector(1, Inches(3.3), Inches(3.5), Inches(4.9), Inches(3.5))
    cxn.line.color.rgb = PURPLE
    cxn.line.width = Pt(3)
    cxn2 = slide.shapes.add_connector(1, Inches(7.9), Inches(3.5), Inches(9.4), Inches(3.5))
    cxn2.line.color.rgb = PURPLE
    cxn2.line.width = Pt(3)
    cxn3 = slide.shapes.add_connector(1, Inches(3.3), Inches(5.5), Inches(9.4), Inches(4.2))
    cxn3.line.color.rgb = ORANGE
    cxn3.line.width = Pt(2)
    cxn3.line.dash_style = 4  # dash

    # --- Layer 3: Arrow labels ---
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

    # Z->Y label placed BELOW X column to avoid overlap
    arrow_label3 = slide.shapes.add_textbox(Inches(3.5), Inches(6.6), Inches(5.5), Inches(0.4))
    p = arrow_label3.text_frame.paragraphs[0]
    p.text = "Z \u2192 Y (direct: \u03b2_Zl, OR 1.5\u20133.0)"
    p.font.size = Pt(12)
    p.font.bold = True
    p.font.color.rgb = ORANGE
    p.alignment = PP_ALIGN.CENTER

    # --- Layer 4: Column header labels ---
    lbl = slide.shapes.add_textbox(Inches(1.0), Inches(1.6), Inches(2.2), Inches(0.35))
    lbl.text_frame.paragraphs[0].text = "Critical Variables Z (Withheld)"
    lbl.text_frame.paragraphs[0].font.size = Pt(12)
    lbl.text_frame.paragraphs[0].font.bold = True
    lbl.text_frame.paragraphs[0].font.color.rgb = BLUE
    lbl.text_frame.paragraphs[0].alignment = PP_ALIGN.CENTER

    lbl2 = slide.shapes.add_textbox(Inches(5.0), Inches(1.45), Inches(2.8), Inches(0.35))
    lbl2.text_frame.paragraphs[0].text = "General Variables X (Measured)"
    lbl2.text_frame.paragraphs[0].font.size = Pt(12)
    lbl2.text_frame.paragraphs[0].font.bold = True
    lbl2.text_frame.paragraphs[0].font.color.rgb = GREEN
    lbl2.text_frame.paragraphs[0].alignment = PP_ALIGN.CENTER

    lbl3 = slide.shapes.add_textbox(Inches(9.5), Inches(2.5), Inches(2.5), Inches(0.35))
    lbl3.text_frame.paragraphs[0].text = "Outcome"
    lbl3.text_frame.paragraphs[0].font.size = Pt(12)
    lbl3.text_frame.paragraphs[0].font.bold = True
    lbl3.text_frame.paragraphs[0].font.color.rgb = RED
    lbl3.text_frame.paragraphs[0].alignment = PP_ALIGN.CENTER

    # --- Layer 5: Interactive diagram shapes (FRONT) ---

    # Z variables (left column)
    z_vars = [
        ("Z1 (Age)", "N(60, 12\u00b2)"),
        ("Z2 (Sex)", "Bernoulli(0.5)"),
        ("Z3 (BMI)", "3 categories"),
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

    # X variables (middle column)
    x_x = Inches(5.0)
    x_start_y = Inches(1.9)
    x_spacing = Inches(0.5)
    x_w = Inches(2.8)
    x_h = Inches(0.42)
    x_labels = ["X1 (HbA1c)", "X2 (Cholesterol)", "X3 (SBP)", "X4 (ALT)",
                "X5 (Creatinine)", "X6 (Haemoglobin)", "X7 (WBC)", "X8 (Albumin)",
                "X9 (CRP)", "X10 (Uric acid)"]

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

    # Y outcome (right)
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
    p.text = "Y (Binary Outcome)"
    p.font.size = Pt(14)
    p.font.bold = True
    p.font.color.rgb = RED
    p.alignment = PP_ALIGN.CENTER
    p2 = tf.add_paragraph()
    p2.text = "Event rate 10\u201320%"
    p2.font.size = Pt(10)
    p2.font.color.rgb = DARK
    p2.alignment = PP_ALIGN.CENTER


def add_editable_workflow(prs):
    """Create editable IONE two-stage workflow slide.

    Z-order: title -> connectors -> decision diamond/labels -> stage boxes (front).
    """
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    add_title_footer(slide, "IONE Framework: Two-Stage Workflow",
                     "Stage 1: Detection (C1 coherence indicator) \u2192 Stage 2: Extraction (stratification)")

    # --- Connectors (low z, added first) ---
    arrow_positions = [
        (Inches(2.7), Inches(3.8), Inches(3.0), Inches(3.8)),
        (Inches(6.2), Inches(3.8), Inches(6.5), Inches(3.8)),
        (Inches(9.7), Inches(3.8), Inches(10.0), Inches(3.8)),
    ]
    for x1, y1, x2, y2 in arrow_positions:
        cxn = slide.shapes.add_connector(1, x1, y1, x2, y2)
        cxn.line.color.rgb = DARK
        cxn.line.width = Pt(3)

    # --- Decision diamond and Yes/No labels (middle z) ---
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
                                       Inches(1), Inches(0.4))
    yes_lbl.text_frame.paragraphs[0].text = "Yes \u2192"
    yes_lbl.text_frame.paragraphs[0].font.size = Pt(11)
    yes_lbl.text_frame.paragraphs[0].font.bold = True
    yes_lbl.text_frame.paragraphs[0].font.color.rgb = GREEN

    no_lbl = slide.shapes.add_textbox(Inches(2.0), Inches(6.2),
                                      Inches(1.5), Inches(0.4))
    no_lbl.text_frame.paragraphs[0].text = "\u2190 No (Coherent)"
    no_lbl.text_frame.paragraphs[0].font.size = Pt(11)
    no_lbl.text_frame.paragraphs[0].font.bold = True
    no_lbl.text_frame.paragraphs[0].font.color.rgb = RED

    # --- Stage boxes (FRONT, highest z) ---
    stages = [
        {
            "title": "Input Data",
            "desc": "Observational study\nN observations\nX1...X10 (measured)\nY (outcome)\n(Z unmeasured)",
            "x": Inches(0.3), "y": Inches(2.0),
            "w": Inches(2.3), "h": Inches(3.5),
            "color": RGBColor(0xE0, 0xE0, 0xE0),
            "border": DARK,
        },
        {
            "title": "Stage 1: DETECTION",
            "desc": "Compute C1 coherence indicator\nfrom I^2 heterogeneity\n\nC1 < 0.05 -> Incoherent\nC1 >= 0.05 -> Coherent\n\n'Warning function'\nNo assumptions needed",
            "x": Inches(3.1), "y": Inches(1.6),
            "w": Inches(3.0), "h": Inches(4.2),
            "color": RGBColor(0xE3, 0xF2, 0xFD),
            "border": BLUE,
        },
        {
            "title": "Stage 2: EXTRACTION",
            "desc": "If incoherent:\n\nFamily 1 (Decision power)\n  1A Predicted probability\n  1B Residual\n  1C Cross-validated\n  1D ML uncertainty\n\nFamily 2 (Feature score)\n  2A PCA\n  2B Clustering",
            "x": Inches(6.6), "y": Inches(1.6),
            "w": Inches(3.0), "h": Inches(4.2),
            "color": RGBColor(0xE8, 0xF5, 0xE9),
            "border": GREEN,
        },
        {
            "title": "Output",
            "desc": "Coherent subpopulations\nfor valid within-subgroup\ninference\n\nBias reduction\nParadox resolution\nEffect modification detected",
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
    """Create editable method comparison overview.

    Z-order: title -> family headers (low z) -> method boxes (front).
    """
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    add_title_footer(slide, "IONE Methods Overview",
                     "Two families of stratification methods plus baselines")

    families = [
        {
            "title": "Family 1: Decision Power-Based\n(Outcome-Informed)",
            "methods": [
                "1A: Predicted Probability\nLogistic regression P(Y|X) \u2192 quantile strata",
                "1B: Residual\n|Y \u2212 \u0070\u0302| \u2192 quantile strata (most robust)",
                "1C: Cross-Validated\nK-fold CV to prevent overfitting",
                "1D: ML Uncertainty\nRandom forest prediction variance \u2192 strata",
            ],
            "x": Inches(0.5), "color": BLUE,
        },
        {
            "title": "Family 2: Feature Score-Based\n(Outcome-Free)",
            "methods": [
                "2A: PCA\nPC1 score \u2192 quantile strata",
                "2B: Clustering\nk-means on X \u2192 cluster = stratum",
            ],
            "x": Inches(5.0), "color": GREEN,
        },
        {
            "title": "Baselines",
            "methods": [
                "Random: Random assignment (lower bound)",
                "Oracle: k-means on Z (upper bound)",
            ],
            "x": Inches(9.5), "color": DARK,
        },
    ]

    # Add ALL family headers first (low z)
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

    # Then ALL method boxes (high z, in front)
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
    """Create editable application guidance / decision tree.

    Z-order: title -> connectors (low z) -> boxes (front).
    """
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    add_title_footer(slide, "IONE Application Guidance",
                     "Decision framework based on \u03b7\u00b2 and subgroup structure")

    scenarios = [
        {
            "condition": "\u03b7\u00b2 > 0.4\n2\u20133 discrete subgroups",
            "method": "Feature score clustering (2B)",
            "expected": "ARI > 0.7",
            "example": "Kidney stone, Israeli vaccine",
            "color": GREEN,
        },
        {
            "condition": "0.15 < \u03b7\u00b2 \u2264 0.4\nMulti-group / continuous",
            "method": "Decision power (1A, 1B)\nBoth families recommended",
            "expected": "ARI 0.1\u20130.5",
            "example": "Smoking\u2013mortality",
            "color": ORANGE,
        },
        {
            "condition": "\u03b7\u00b2 < 0.15\nWeak traces",
            "method": "C1 detection only\nExtraction limited",
            "expected": "ARI < 0.1",
            "example": "COVID-19, Berkeley",
            "color": RED,
        },
    ]

    # Add ALL connectors first (low z)
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

    # Then ALL boxes (high z, in front)
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
        p.text = f"Expected: {s['expected']}"
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
p2.text = "Incoherence-Oriented Neutralisation and Extraction\nfor Detecting Hidden Population Structure in Observational Studies"
p2.font.size = Pt(20)
p2.font.color.rgb = WHITE
p2.alignment = PP_ALIGN.CENTER
p3 = tf.add_paragraph()
p3.text = ""
p4 = tf.add_paragraph()
p4.text = "Figures and Tables"
p4.font.size = Pt(16)
p4.font.color.rgb = RGBColor(0xBB, 0xDE, 0xFB)
p4.alignment = PP_ALIGN.CENTER
p5 = tf.add_paragraph()
p5.text = "BMC Medical Research Methodology"
p5.font.size = Pt(14)
p5.font.color.rgb = RGBColor(0xBB, 0xDE, 0xFB)
p5.alignment = PP_ALIGN.CENTER

# --- Editable: Causal DAG ---
add_editable_dag(prs)

# --- Editable: IONE Workflow ---
add_editable_workflow(prs)

# --- Editable: Methods Overview ---
add_editable_method_overview(prs)

# --- Editable: Application Guidance ---
add_editable_application_guidance(prs)

# --- Table 1: Simpson's paradox examples ---
add_table_slide(prs, "Table 1. Published Simpson's Paradox Examples",
    "Five examples used for empirical validation",
    ["Example", "Source", "N", "Hidden Confounder", "Groups", "Paradox"],
    [
        ["COVID-19 CFR", "von Kugelgen 2021", "50,459", "Age group", "9", "Italy > China overall, reversed within age groups"],
        ["Kidney stone", "Charig 1986", "700", "Stone size", "2", "Treatment B > A overall, A > B within each size"],
        ["UC Berkeley", "Bickel 1975", "4,425", "Department", "6", "Males > females overall, reversed in most departments"],
        ["Israeli vaccine", "Morris 2021", "6,100", "Age group", "2", "Vaccine ineffective overall, effective in both groups"],
        ["Smoking-mortality", "Appleton 1996", "1,314", "Age group", "7", "Smokers lower mortality overall, higher within groups"],
    ],
    [Inches(1.5), Inches(1.5), Inches(0.8), Inches(1.3), Inches(0.8), Inches(5.5)]
)

# --- Table 2: Method ranking ---
add_table_slide(prs, "Table 2. Method Performance Ranking (Phase 1 Simulation)",
    "Averaged across all scenarios (N=2,000; 200 repetitions per scenario)",
    ["Rank", "Method", "Family", "ARI", "NMI", "eta^2 (mean)", "C1"],
    [
        ["1", "Oracle (k-means on Z)", "Baseline (upper)", "0.353", "0.616", "0.562", "0.019"],
        ["2", "Oracle (quantile on Z)", "Baseline (upper)", "0.073", "0.260", "0.283", "0.010"],
        ["3", "1B: Residual", "Decision power", "0.020", "0.069", "0.091", "0.001"],
        ["4", "1D: ML uncertainty", "Decision power", "0.017", "0.056", "0.074", "0.001"],
        ["5", "1A: Predicted probability", "Decision power", "0.014", "0.053", "0.069", "0.022"],
        ["6", "1C: Cross-validated", "Decision power", "0.014", "0.051", "0.067", "0.028"],
        ["7", "2A: PCA (k=2)", "Feature score", "0.012", "0.042", "0.052", "0.098"],
        ["8", "2A: PCA (k=1)", "Feature score", "0.011", "0.047", "0.063", "0.095"],
        ["9", "2B: Clustering", "Feature score", "0.011", "0.041", "0.053", "0.079"],
        ["10", "Random", "Baseline (lower)", "-0.000", "0.007", "0.002", "0.863"],
    ],
    [Inches(0.6), Inches(2.5), Inches(1.8), Inches(0.8), Inches(0.8), Inches(1.2), Inches(0.8)]
)

# --- Table 3: Z->X influence ---
add_table_slide(prs, "Table 3. ARI by Z->X Influence Strength (K=5 strata)",
    "The Z->X influence is the single most important determinant of performance",
    ["Method", "zx=0.3 (weak)", "zx=0.5 (moderate)", "zx=1.0 (strong)", "Strong/weak ratio"],
    [
        ["1A: Predicted probability", "0.004", "0.010", "0.030", "8.7"],
        ["1B: Residual", "0.014", "0.018", "0.029", "1.9"],
        ["1C: Cross-validated", "0.003", "0.009", "0.029", "9.6"],
        ["2A: PCA (k=2)", "0.002", "0.006", "0.029", "18.3"],
        ["2B: Clustering", "0.002", "0.006", "0.025", "14.0"],
        ["Oracle (k-means on Z)", "0.378", "0.378", "0.380", "1.0"],
    ],
    [Inches(2.5), Inches(1.8), Inches(1.8), Inches(1.8), Inches(1.8)]
)

# --- Table 4: Eta-squared ---
add_table_slide(prs, "Table 4. Eta-Squared for Each Critical Variable (K=5, zx=1.0)",
    "Age (continuous) captured best; sex (binary) captured poorly",
    ["Method", "Z1 (age)", "Z2 (sex)", "Z3 (BMI)", "Mean"],
    [
        ["Oracle (k-means on Z)", "0.312", "0.982", "0.663", "0.652"],
        ["1A: Predicted probability", "0.327", "0.008", "0.092", "0.142"],
        ["1C: Cross-validated", "0.322", "0.007", "0.090", "0.140"],
        ["1B: Residual", "0.295", "0.012", "0.093", "0.133"],
        ["2B: Clustering", "0.238", "0.026", "0.090", "0.118"],
        ["Random", "0.002", "0.002", "0.002", "0.002"],
    ],
    [Inches(2.8), Inches(1.5), Inches(1.5), Inches(1.5), Inches(1.5)]
)

# --- Table 5: Sensitivity analysis ---
add_table_slide(prs, "Table 5. ARI by Z->X Influence in Sensitivity Analysis",
    "Confirming Z->X influence as the most important parameter",
    ["Method", "zx=0.2 (weak)", "zx=0.5 (moderate)", "zx=1.0 (strong)", "Strong/weak ratio"],
    [
        ["1A: Predicted probability", "0.002", "0.009", "0.028", "17.5"],
        ["1C: Cross-validated", "0.001", "0.008", "0.027", "22.3"],
        ["2B: Clustering", "0.001", "0.006", "0.024", "34.3"],
        ["2A: PCA (60%)", "0.001", "0.004", "0.015", "30.8"],
    ],
    [Inches(2.5), Inches(1.8), Inches(1.8), Inches(1.8), Inches(1.8)]
)

# --- Simulation Figures ---
add_image_slide(prs,
    "Figure 1. ARI and NMI Heatmap (Phase 1 Simulation)",
    "Method x scenario performance across all Phase 1 conditions",
    f"{FIG_SIM}/heatmap_ari_nmi.png")

add_image_slide(prs,
    "Figure 2. Effect of Z->X Influence Strength",
    "Sensitivity analysis: ARI increases up to 18-fold from weak to strong Z->X influence",
    f"{FIG_SIM}/sensitivity_zx_influence.png")

add_image_slide(prs,
    "Figure 3. Eta-Squared by Method and Critical Variable",
    "Differential capture: age (continuous) >> BMI (ordinal) >> sex (binary)",
    f"{FIG_SIM}/eta_squared.png")

add_image_slide(prs,
    "Figure 4. Coherence Indicator C1 Across Methods",
    "Low C1 = successful detection of population incoherence; proposed methods C1~0.001 vs random C1~0.863",
    f"{FIG_SIM}/coherence_diagnosis.png")

add_image_slide(prs,
    "Figure 5. Effect of Sample Size",
    "Performance is largely insensitive to sample size (N=500 to N=10,000)",
    f"{FIG_SIM}/sensitivity_sample_size.png")

add_image_slide(prs,
    "Figure 6. Phase 1 Simulation Summary Dashboard",
    "Comprehensive overview of simulation results across all methods and conditions",
    f"{FIG_SIM}/summary_dashboard.png")

# --- Table 6: Empirical validation ---
add_table_slide(prs, "Table 6. Summary of Empirical Validation Results",
    "IONE applied to five published Simpson's paradox examples",
    ["Example", "Best Method", "Best ARI", "Oracle ARI", "Achievement", "C1 (best)", "C1 (random)", "eta^2"],
    [
        ["Kidney stone", "2B Clustering", "0.851", "1.000", "85.1%", "0.034", "0.695", "0.428"],
        ["Israeli vaccine", "2B Clustering", "0.746", "1.000", "74.6%", "0.005", "0.770", "0.432"],
        ["Smoking-mortality", "1A Pred. prob.", "0.498", "1.000", "49.8%", "0.005", "1.000", "0.686"],
        ["UC Berkeley", "1A Pred. prob.", "0.082", "1.000", "8.2%", "0.011", "0.954", "0.152"],
        ["COVID-19 CFR", "1B Residual", "0.064", "1.000", "6.4%", "0.001", "0.778", "0.171"],
    ],
    [Inches(1.5), Inches(1.3), Inches(1.0), Inches(1.0), Inches(1.0), Inches(1.0), Inches(1.0), Inches(0.8)]
)

# --- Real Data Figures ---
add_image_slide(prs,
    "Figure 7. Simpson's Paradox Demonstration",
    "Visualisation of the paradox in all five published examples",
    f"{FIG_RD}/fig1_paradox_demonstration.png")

add_image_slide(prs,
    "Figure 8. Coherence Analysis (C1) Across Examples",
    "C1 correctly detected incoherence in all five examples (C1=0.001-0.034 vs random C1=0.695-1.000)",
    f"{FIG_RD}/fig3_coherence_analysis.png")

add_image_slide(prs,
    "Figure 9. Method Comparison Across Examples (ARI)",
    "2B Clustering best for 2-group; 1A/1B best for multi-group structures",
    f"{FIG_RD}/fig2_method_comparison.png")

add_image_slide(prs,
    "Figure 10. Eta-Squared Heatmap (Empirical Validation)",
    "Higher eta-squared correlates with higher ARI, consistent with simulation findings",
    f"{FIG_RD}/fig4_eta_squared_heatmap.png")

add_image_slide(prs,
    "Figure 11. Direction Consistency Analysis",
    "Consistency of exposure-outcome association direction across strata",
    f"{FIG_RD}/fig5_direction_consistency.png")

add_image_slide(prs,
    "Figure 12. Empirical Validation Summary Dashboard",
    "Comprehensive overview of all five Simpson's paradox applications",
    f"{FIG_RD}/fig6_summary_dashboard.png")

# --- Table 7: Concordance ---
add_table_slide(prs, "Table 7. Concordance Between Simulation and Empirical Findings",
    "Key findings from simulation replicated in empirical validation",
    ["Finding", "Simulation", "Empirical Validation"],
    [
        ["1B Residual is most robust", "Highest ARI (0.020)", "Best for COVID-19 (ARI=0.064)"],
        ["C1 detects incoherence", "Random 0.863 vs proposed 0.001", "Random 0.70-1.00 vs proposed 0.00-0.03"],
        ["Z->X influence is decisive", "ARI increases with zx", "Higher eta^2 -> higher ARI"],
        ["All methods outperform random", "All scenarios", "All five examples"],
    ],
    [Inches(2.5), Inches(3.5), Inches(3.5)]
)

# --- Save ---
outpath = '/home/ubuntu/repos/stratification_project/results/manuscript/IONE_figures_tables_EN.pptx'
prs.save(outpath)
print(f'Saved to {outpath}')
