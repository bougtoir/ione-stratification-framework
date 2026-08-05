"""
Markdown-to-docx converter for RSM manuscripts.

Supports:
- Headings (#, ##, ###, ####)
- Paragraphs with **bold**, *italic*, `code`
- Bullet and numbered lists
- Blockquotes
- Tables (pipe syntax)
- Citations [key] -> (Author Year)
- Figures ![caption](path)
- Page breaks via a {{PAGE}} marker line
"""

import re
import os
import copy
from docx import Document
from docx.shared import Inches, Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from collections import OrderedDict


class CiteManager:
    """Author-date citation manager."""
    def __init__(self):
        self._refs = OrderedDict()

    def register(self, key, author_short, year, full_ref):
        self._refs[key] = {'author': author_short, 'year': year, 'full': full_ref}
        return key

    def cite(self, key, narrative=False):
        if key not in self._refs:
            raise KeyError(f'Citation key {key} not registered')
        r = self._refs[key]
        if narrative:
            return f"{r['author']} ({r['year']})"
        return f"({r['author']} {r['year']})"

    def write_reference_list(self, doc):
        doc.add_heading('References', level=1)
        items = sorted(
            self._refs.items(),
            key=lambda kv: (kv[1]['author'].split(' and ')[0].split(',')[0].strip().lower(),
                           kv[1]['year'], kv[0])
        )
        for _, v in items:
            p = doc.add_paragraph()
            p.add_run(v['full'])


def _apply_inline(runs, text, cite_manager=None):
    """Apply inline formatting and citation replacement to a paragraph or cell."""
    # Replace citations first, keeping markers for formatting splits
    if cite_manager:
        text = re.sub(r'\[([a-zA-Z0-9_]+)\]', lambda m: cite_manager.cite(m.group(1)), text)
    parts = re.split(r'(\*\*[^*]+\*\*|\*[^*]+\*|\`[^`]+\`)', text)
    for part in parts:
        if part.startswith('**') and part.endswith('**'):
            run = runs.add_run(part[2:-2])
            run.bold = True
        elif part.startswith('*') and part.endswith('*') and len(part) > 2:
            run = runs.add_run(part[1:-1])
            run.italic = True
        elif part.startswith('`') and part.endswith('`'):
            run = runs.add_run(part[1:-1])
            run.font.name = 'Courier New'
        else:
            runs.add_run(part)


def convert(md_path, docx_path, cite_manager=None, figure_dir=None):
    with open(md_path, 'r', encoding='utf-8') as f:
        lines = [l.rstrip('\n') for l in f]

    doc = Document()
    style = doc.styles['Normal']
    style.font.name = 'Times New Roman'
    style.font.size = Pt(11)

    i = 0
    while i < len(lines):
        line = lines[i]
        if not line.strip():
            i += 1
            continue

        stripped = line.strip()

        # Page break marker
        if stripped == '{{PAGE}}':
            doc.add_page_break()
            i += 1
            continue

        # Reference list marker
        if stripped == '{{REFS}}':
            if cite_manager:
                cite_manager.write_reference_list(doc)
            i += 1
            continue

        # Figure: ![caption](path)
        m = re.match(r'!\[([^\]]*)\]\(([^)]+)\)', stripped)
        if m:
            caption, path = m.group(1), m.group(2)
            if figure_dir:
                path = os.path.join(figure_dir, path)
            if os.path.exists(path):
                p = doc.add_paragraph()
                p.alignment = WD_ALIGN_PARAGRAPH.CENTER
                p.add_run().add_picture(path, width=Inches(5.8))
            else:
                doc.add_paragraph(f'[Figure not found: {path}]')
            cap = doc.add_paragraph()
            cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
            cap_run = cap.add_run(caption)
            cap_run.bold = True
            i += 1
            continue

        # Headings
        if line.startswith('# '):
            p = doc.add_heading(line[2:], level=0)
            p.alignment = WD_ALIGN_PARAGRAPH.LEFT
            i += 1
            continue
        if line.startswith('## '):
            doc.add_heading(line[3:], level=1)
            i += 1
            continue
        if line.startswith('### '):
            doc.add_heading(line[4:], level=2)
            i += 1
            continue
        if line.startswith('#### '):
            doc.add_heading(line[5:], level=3)
            i += 1
            continue

        # Blockquote
        if line.startswith('> '):
            p = doc.add_paragraph()
            p.paragraph_format.left_indent = Inches(0.3)
            _apply_inline(p, line[2:], cite_manager)
            i += 1
            continue

        # Bullet list
        if line.startswith('- '):
            p = doc.add_paragraph(style='List Bullet')
            _apply_inline(p, line[2:], cite_manager)
            i += 1
            continue

        # Numbered list
        m = re.match(r'^(\d+)\.\s+', line)
        if m:
            p = doc.add_paragraph(style='List Number')
            _apply_inline(p, line[m.end():], cite_manager)
            i += 1
            continue

        # Table
        if line.startswith('|'):
            rows = []
            while i < len(lines) and lines[i].startswith('|'):
                cells = [c.strip() for c in lines[i].split('|')]
                if cells and cells[0] == '':
                    cells = cells[1:]
                if cells and cells[-1] == '':
                    cells = cells[:-1]
                # Skip separator rows
                if not all(re.match(r':?-+:?', c) for c in cells if c):
                    rows.append(cells)
                i += 1
            if rows:
                n_cols = max(len(r) for r in rows)
                table = doc.add_table(rows=len(rows), cols=n_cols)
                table.style = 'Table Grid'
                for r_idx, r in enumerate(rows):
                    for c_idx in range(n_cols):
                        cell = table.rows[r_idx].cells[c_idx]
                        if c_idx < len(r):
                            _apply_inline(cell.paragraphs[0], r[c_idx], cite_manager)
                        if r_idx == 0:
                            for run in cell.paragraphs[0].runs:
                                run.bold = True
            continue

        # Plain paragraph (possibly merged with next if continuation? keep simple)
        p = doc.add_paragraph()
        _apply_inline(p, line, cite_manager)
        i += 1

    apply_math_to_doc(doc)
    doc.save(docx_path)
    print(f'[md_to_rsm_docx] {md_path} -> {docx_path}')

# ---------------------------------------------------------------------------
# Word equation (OMML) insertion for mathematical expressions
# ---------------------------------------------------------------------------

_MATH_PATTERNS = [
    (r'P\(Y=1\|A=1\) - P\(Y=1\|A=0\)', 'riskdiff'),
    (r'C1 = 1 - I\^2', 'c1def'),
    (r'Y ~ X \+ A \+ X\*A', 'ymodel'),
    (r'1 - \|bias_([a-z_]+)\| / \|bias_([a-z_]+)\|', 'frac'),
    (r'\|bias_([a-z_]+)\| - \|bias_([a-z_]+)\|', 'diff'),
    (r'tau\^2', 'tausq'),
    (r'W_(true|est)', 'wsub'),
    (r'I\^2', 'isq'),
]


def _math_text(oMath, text):
    r = OxmlElement('m:r')
    t = OxmlElement('m:t')
    t.set(qn('xml:space'), 'preserve')
    t.text = text
    r.append(t)
    oMath.append(r)


def _math_superscript(oMath, base, sup):
    ss = OxmlElement('m:sSup')
    e = OxmlElement('m:e')
    _math_text(e, base)
    sup_el = OxmlElement('m:sup')
    _math_text(sup_el, sup)
    ss.append(e)
    ss.append(sup_el)
    oMath.append(ss)


def _math_subscript(oMath, base, sub):
    ss = OxmlElement('m:sSub')
    e = OxmlElement('m:e')
    _math_text(e, base)
    sub_el = OxmlElement('m:sub')
    _math_text(sub_el, sub)
    ss.append(e)
    ss.append(sub_el)
    oMath.append(ss)


def _math_fraction(oMath, num, den):
    f = OxmlElement('m:f')
    num_el = OxmlElement('m:num')
    _math_text(num_el, num)
    den_el = OxmlElement('m:den')
    _math_text(den_el, den)
    f.append(num_el)
    f.append(den_el)
    oMath.append(f)


def _make_math_omath(kind, match):
    oMath = OxmlElement('m:oMath')
    if kind == 'riskdiff':
        _math_text(oMath, 'P(Y=1|A=1) - P(Y=1|A=0)')
    elif kind == 'c1def':
        _math_text(oMath, 'C1 = 1 - ')
        _math_superscript(oMath, 'I', '2')
    elif kind == 'ymodel':
        _math_text(oMath, 'Y ~ X + A + X×A')
    elif kind == 'isq':
        _math_superscript(oMath, 'I', '2')
    elif kind == 'tausq':
        _math_superscript(oMath, 'τ', '2')
    elif kind == 'wsub':
        _math_subscript(oMath, 'W', match.group(1))
    elif kind == 'diff':
        _math_text(oMath, f'|bias_{match.group(1)}| - |bias_{match.group(2)}|')
    elif kind == 'frac':
        _math_text(oMath, '1 - ')
        _math_fraction(oMath, f'|bias_{match.group(1)}|', f'|bias_{match.group(2)}|')
    return oMath


def _text_run(text, rPr):
    r = OxmlElement('w:r')
    if rPr is not None:
        r.append(copy.deepcopy(rPr))
    t = OxmlElement('w:t')
    t.set(qn('xml:space'), 'preserve')
    t.text = text
    r.append(t)
    return r


def _split_text_to_elems(text, rPr, patterns):
    best = None
    for pat, kind in patterns:
        m = re.search(pat, text)
        if m:
            if best is None or m.start() < best[0].start():
                best = (m, kind)
    if best is None:
        return [_text_run(text, rPr)]
    m, kind = best
    pre = text[:m.start()]
    post = text[m.end():]
    elems = []
    if pre:
        elems.append(_text_run(pre, rPr))
    elems.append(_make_math_omath(kind, m))
    if post:
        elems.extend(_split_text_to_elems(post, rPr, patterns))
    return elems


def _split_run(run, patterns):
    text = run.text
    if not text:
        return None
    rPr = run._r.rPr
    for pat, kind in patterns:
        if re.search(pat, text):
            return _split_text_to_elems(text, rPr, patterns)
    return None


def apply_math_to_doc(doc):
    """Replace plain-text mathematical expressions with Word OMML equations."""
    paras = list(doc.paragraphs)
    for table in doc.tables:
        for row in table.rows:
            for cell in row.cells:
                paras.extend(cell.paragraphs)
    for p in paras:
        for run in list(p.runs):
            new_elems = _split_run(run, _MATH_PATTERNS)
            if new_elems:
                for el in new_elems:
                    run._r.addprevious(el)
                p._p.remove(run._r)
