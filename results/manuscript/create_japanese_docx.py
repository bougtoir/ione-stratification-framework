#!/usr/bin/env python3
"""Create IONE manuscript Japanese summary as .docx with embedded color figures."""

from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml.ns import qn
import os

doc = Document()

# --- Style setup ---
style = doc.styles['Normal']
font = style.font
font.name = 'Times New Roman'
font.size = Pt(11)
style.paragraph_format.line_spacing = 1.5
style.paragraph_format.space_after = Pt(4)

# Set East Asian font for Normal style
rPr = style.element.get_or_add_rPr()
rFonts = rPr.find(qn('w:rFonts'))
if rFonts is None:
    from lxml import etree
    rFonts = etree.SubElement(rPr, qn('w:rFonts'))
rFonts.set(qn('w:eastAsia'), 'Yu Mincho')

for level in range(1, 4):
    hs = doc.styles[f'Heading {level}']
    hs.font.name = 'Times New Roman'
    hs.font.color.rgb = RGBColor(0, 0, 0)
    hrPr = hs.element.get_or_add_rPr()
    hrFonts = hrPr.find(qn('w:rFonts'))
    if hrFonts is None:
        from lxml import etree
        hrFonts = etree.SubElement(hrPr, qn('w:rFonts'))
    hrFonts.set(qn('w:eastAsia'), 'Yu Gothic')
    if level == 1:
        hs.font.size = Pt(16)
    elif level == 2:
        hs.font.size = Pt(13)
    else:
        hs.font.size = Pt(11)

# Paths
FIG_SIM = '/home/ubuntu/repos/stratification_project/results/figures'
FIG_RD = '/home/ubuntu/repos/stratification_project/results/real_data'


def add_figure(doc, path, caption, width=Inches(5.5)):
    if os.path.exists(path):
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run = p.add_run()
        run.add_picture(path, width=width)
        cap = doc.add_paragraph(caption)
        cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
        cap.style = doc.styles['Normal']
        for run in cap.runs:
            run.font.size = Pt(9)
            run.italic = True
        doc.add_paragraph()
    else:
        p = doc.add_paragraph(f'[図版未検出: {path}]')
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER


def add_table(doc, headers, rows):
    table = doc.add_table(rows=1 + len(rows), cols=len(headers))
    table.style = 'Table Grid'
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    for i, h in enumerate(headers):
        cell = table.rows[0].cells[i]
        cell.text = h
        for p in cell.paragraphs:
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            for run in p.runs:
                run.bold = True
                run.font.size = Pt(9)
                run.font.name = 'Times New Roman'
    for r_idx, row in enumerate(rows):
        for c_idx, val in enumerate(row):
            cell = table.rows[r_idx + 1].cells[c_idx]
            cell.text = str(val)
            for p in cell.paragraphs:
                p.alignment = WD_ALIGN_PARAGRAPH.CENTER
                for run in p.runs:
                    run.font.size = Pt(9)
                    run.font.name = 'Times New Roman'
    doc.add_paragraph()
    return table


# ============================================================
# TITLE PAGE
# ============================================================
title = doc.add_heading('', level=1)
title.alignment = WD_ALIGN_PARAGRAPH.CENTER
run = title.add_run('IONE論文 日本語抄訳')
run.font.size = Pt(18)
run.bold = True

doc.add_paragraph()
p = doc.add_paragraph()
p.alignment = WD_ALIGN_PARAGRAPH.CENTER
run = p.add_run(
    'IONE：観察研究における隠れた集団構造の検出のための\n'
    'インコヒーレンス指向の中和と抽出'
)
run.font.size = Pt(14)
run.bold = True

p = doc.add_paragraph()
p.alignment = WD_ALIGN_PARAGRAPH.CENTER
run = p.add_run(
    'IONE: Incoherence-Oriented Neutralisation and Extraction\n'
    'for Detecting Hidden Population Structure in Observational Studies'
)
run.italic = True
run.font.size = Pt(11)

doc.add_paragraph()
p = doc.add_paragraph('[著者名を挿入]')
p.alignment = WD_ALIGN_PARAGRAPH.CENTER
p = doc.add_paragraph('[所属を挿入]')
p.alignment = WD_ALIGN_PARAGRAPH.CENTER

doc.add_page_break()

# ============================================================
# ABSTRACT
# ============================================================
doc.add_heading('抄録（構造化抄録）', level=1)

p = doc.add_paragraph()
p.add_run('背景：').bold = True
p.add_run(
    '観察研究は、隠れた集団構造に起因する複数のバイアス（交絡、シンプソンのパラドックス、未検出の効果修飾、'
    '生態学的誤謬、非崩壊性）の影響を受けやすい。傾向スコアや予後スコアなどの既存の調整手法は測定された'
    '交絡因子のみに対処し、未測定変数による部分集団構造を検出する仕組みを持たない。本研究では、日常的に'
    '測定される変数のみを用いて集団のインコヒーレンスを定量化し、コヒーレントな部分集団を抽出する枠組みで'
    'あるIONE（Incoherence-Oriented Neutralisation and Extraction）を提案する。'
)

p = doc.add_paragraph()
p.add_run('方法：').bold = True
p.add_run(
    'ADEMPフレームワークに準拠したモンテカルロシミュレーション研究を実施した。意図的に除外した3つの重大変数'
    '（年齢、性別、BMI）が10の測定変数と二値アウトカムに影響する因果有向非巡回グラフ（DAG）からデータを'
    '生成した。決定力ベース手法4種と特徴量得点ベース手法2種の計6手法を評価した。性能はAdjusted Rand Index'
    '（ARI）、イータ二乗（η²）、I²異質性統計量に基づくコヒーレンス指標（C1）で評価した。Phase 1は'
    '1,200シナリオにわたる18,000評価、感度分析は8,100シナリオにわたる48,600評価で構成された。さらに、'
    'IONEを5つの既報シンプソンのパラドックス事例に適用した。'
)

p = doc.add_paragraph()
p.add_run('結果：').bold = True
p.add_run(
    'シミュレーションでは、全提案手法がランダム層別化を有意に上回った（最良ARI = 0.020 vs. 0.000）。'
    '隠れた変数の測定変数への影響力（Z→X影響度）が性能の最大の決定因子であり、弱条件から強条件でARIが'
    '最大18倍に増加した。コヒーレンス指標C1は集団のインコヒーレンスを明確に識別した（提案手法C1 = 0.001 '
    'vs. ランダムC1 = 0.863）。実データ検証では、C1は全5事例でインコヒーレンスを正確に検出した。'
    '2群構造に対しては高い精度を達成した（腎結石ARI = 0.851、イスラエルワクチンARI = 0.746）。'
)

p = doc.add_paragraph()
p.add_run('結論：').bold = True
p.add_run(
    'IONEは二段階の貢献を提供する。C1コヒーレンス指標はサブグループの複雑さに関わらず集団の'
    'インコヒーレンスを確実に検出する。層別化によるコヒーレント部分集団の抽出は、隠れた変数が'
    '測定変数に十分強い痕跡を残す場合（η² > 0.4）かつ部分集団構造が離散的である場合に有効である。'
    'コヒーレンス評価を観察研究報告の標準的なステップとして組み込むことを推奨する。'
)

p = doc.add_paragraph()
p.add_run('キーワード：').bold = True
p.add_run('シンプソンのパラドックス、交絡、集団異質性、コヒーレンス、層別化、未測定交絡因子、観察研究、因果推論')

doc.add_page_break()

# ============================================================
# 1. BACKGROUND
# ============================================================
doc.add_heading('1. 背景（Background）', level=1)

doc.add_paragraph(
    '観察研究（特に後ろ向きコホート研究）は、治療割り付けが研究者の制御下にないため、隠れた集団構造に'
    '起因する複数のバイアスに脆弱である。これらのバイアスはすべて単一の根本原因——研究対象集団が異質な'
    '部分集団を内包していること——から生じる。'
)

doc.add_paragraph('本研究が対象とするバイアス：')

biases = [
    ('交絡バイアス', '曝露と結果の両方に影響する未測定変数が見かけ上の関連を生む'),
    ('シンプソンのパラドックス', '全体の関連がサブグループで逆転する現象'),
    ('効果修飾の見落とし', '効果が部分集団間で真に異なるのに単一の「平均的」効果として報告される'),
    ('生態学的誤謬', '集団レベルの関連を個人に不適切に一般化する'),
    ('非崩壊性', 'オッズ比が交絡なしでも周辺と条件付きで一致しない数学的性質'),
]
for name, desc in biases:
    p = doc.add_paragraph()
    p.add_run(f'• {name}：').bold = True
    p.add_run(desc)

doc.add_paragraph(
    '既存手法（傾向スコア、予後スコア、hdPS等）は測定された共変量のみを調整し、未測定変数による'
    '集団構造を検出する仕組みがない。'
)
doc.add_paragraph('IONEは2段階アプローチを提案する：')
doc.add_paragraph('(1) コヒーレンス度指標（C1）で集団の均質性を定量評価')
doc.add_paragraph('(2) インコヒーレンスが検出された場合、測定変数の多変量パターンで層別化し、各部分集団内で分析')

doc.add_page_break()

# ============================================================
# 2. METHODS
# ============================================================
doc.add_heading('2. 方法（Methods）— ADEMP構造', level=1)

doc.add_heading('目的（Aims）', level=2)
doc.add_paragraph('1. 測定変数のみによる層別化で未測定変数による群構造を再現できるか')
doc.add_paragraph('2. 決定力ベース手法 vs 特徴量得点ベース手法の比較')
doc.add_paragraph('3. C1指標のインコヒーレンス検出能力の評価')
doc.add_paragraph('4. 手法が有効/無効なデータ生成条件の特定')

doc.add_heading('データ生成メカニズム（Data-generating mechanisms）', level=2)
doc.add_paragraph(
    '因果DAG：重大変数Z（年齢・性別・BMI）→ 一般変数X（10変数）→ アウトカムY（二値）\n'
    '• Z1（年齢）：N(60, 12^2)、Z2（性別）：Bernoulli(0.5)、Z3（BMI区分）：3水準\n'
    '• X：臨床検査値を模擬（HbA1c、コレステロール、血圧、ALT、クレアチニン等）\n'
    '• Y：ロジスティックモデル、イベント率10-20%'
)

doc.add_heading('推定量（Estimands）', level=2)
doc.add_paragraph('1. サブグループ再現度（ARI）')
doc.add_paragraph('2. 痕跡捕捉度（η²）')
doc.add_paragraph('3. コヒーレンス（C1 = 1 − I²）')

doc.add_heading('評価手法（Methods）', level=2)
add_table(doc,
    ['ファミリー', '手法', '概要'],
    [
        ['決定力ベース（Y使用）', '1A 予測確率', 'ロジスティック回帰の予測確率で層別化'],
        ['', '1B 残差', '絶対残差の大きさで層別化'],
        ['', '1C 交差検証型', 'K-fold CVで過学習を回避'],
        ['', '1D ML不確実性', 'ランダムフォレストの予測分散で層別化'],
        ['特徴量得点ベース（Y不使用）', '2A PCA', '第1主成分得点で層別化'],
        ['', '2B クラスタリング', 'k-meansのクラスタ割当を層とする'],
        ['ベースライン', 'ランダム', '無作為に層を割当（下限）'],
        ['', 'Oracle', '真のZでk-means（上限）'],
    ]
)

doc.add_heading('性能指標（Performance measures）', level=2)
doc.add_paragraph(
    '• ARI（Adjusted Rand Index）：偶然一致補正済みクラスタ一致度\n'
    '• η²（イータ二乗）：層別化がZの分散を説明する割合\n'
    '• C1（コヒーレンス指標）：C1 ≈ 0 で異質（インコヒーレント）、C1 ≈ 1 で均質（コヒーレント）'
)

doc.add_heading('シミュレーション規模', level=2)
doc.add_paragraph(
    '• Phase 1：1,200シナリオ × 15手法 = 18,000評価（6.0分）\n'
    '• 感度分析：8,100シナリオ × 6手法 = 48,600評価（9.4分）\n'
    '• 合計66,600評価'
)

doc.add_heading('実データ検証', level=2)
doc.add_paragraph('5つの既報シンプソンのパラドックス事例に適用：')
add_table(doc,
    ['事例', '出典', 'N', '隠れた交絡因子', '群数'],
    [
        ['COVID-19致死率', 'von Kugelgen et al. 2021', '50,459', '年齢群（9群）', '9'],
        ['腎結石治療', 'Charig et al. 1986', '700', '結石サイズ（2群）', '2'],
        ['UCバークレー入学', 'Bickel et al. 1975', '4,425', '学部（6群）', '6'],
        ['イスラエルワクチン', 'Morris 2021', '6,100', '年齢群（2群）', '2'],
        ['喫煙・死亡率', 'Appleton et al. 1996', '1,314', '年齢群（7群）', '7'],
    ]
)

doc.add_page_break()

# ============================================================
# 3. RESULTS
# ============================================================
doc.add_heading('3. 結果（Results）', level=1)

doc.add_heading('3.1 シミュレーション結果', level=2)

doc.add_heading('手法ランキング（Phase 1）', level=3)
add_table(doc,
    ['順位', '手法', 'ARI', 'C1'],
    [
        ['1', 'Oracle（k-means on Z）', '0.353', '0.019'],
        ['2', '1B 残差', '0.020', '0.001'],
        ['3', '1D ML不確実性', '0.017', '0.001'],
        ['4', '1A 予測確率', '0.014', '0.022'],
        ['5', '1C 交差検証型', '0.014', '0.028'],
        ['6', '2A PCA', '0.012', '0.098'],
        ['7', '2B クラスタリング', '0.011', '0.079'],
        ['8', 'ランダム', '-0.000', '0.863'],
    ]
)

doc.add_paragraph('重要な知見：')
doc.add_paragraph('• Z→X影響度が最大の決定因子：弱(0.3)→強(1.0)でARI最大18倍増加')
doc.add_paragraph('• 年齢（連続変数）の捕捉が最も良好：η² = 0.327。性別（二値）は困難：η² < 0.03')
doc.add_paragraph('• C1指標は確実にインコヒーレンスを検出：提案手法C1 = 0.001 vs ランダムC1 = 0.863')
doc.add_paragraph('• サンプルサイズの影響は小さい（N=500でもN=10,000でもほぼ同じARI）')

add_figure(doc,
    f'{FIG_SIM}/heatmap_ari_nmi.png',
    '図1. Phase 1シミュレーションにおける手法別・シナリオ別のARIおよびNMIヒートマップ'
)

add_figure(doc,
    f'{FIG_SIM}/sensitivity_zx_influence.png',
    '図2. Z→X影響度が手法性能に与える効果（感度分析）'
)

add_figure(doc,
    f'{FIG_SIM}/eta_squared.png',
    '図3. 各手法による個別重大変数の捕捉度（イータ二乗η²）'
)

add_figure(doc,
    f'{FIG_SIM}/coherence_diagnosis.png',
    '図4. 手法別コヒーレンス指標C1。低C1値は集団インコヒーレンスの検出に成功していることを示す'
)

add_figure(doc,
    f'{FIG_SIM}/sensitivity_sample_size.png',
    '図5. サンプルサイズが手法性能に与える効果（感度分析）'
)

add_figure(doc,
    f'{FIG_SIM}/summary_dashboard.png',
    '図6. Phase 1シミュレーション結果のサマリーダッシュボード',
    width=Inches(6.0)
)

doc.add_page_break()

# ============================================================
# 3.2 EMPIRICAL VALIDATION
# ============================================================
doc.add_heading('3.2 実データ検証結果', level=2)

add_table(doc,
    ['事例', '最良手法', 'ARI', 'C1（提案）', 'C1（ランダム）'],
    [
        ['腎結石（2群）', '2B クラスタリング', '0.851', '0.034', '0.695'],
        ['イスラエルワクチン（2群）', '2B クラスタリング', '0.746', '0.005', '0.770'],
        ['喫煙・死亡率（7群）', '1A 予測確率', '0.498', '0.005', '1.000'],
        ['UCバークレー（6群）', '1A 予測確率', '0.082', '0.011', '0.954'],
        ['COVID-19 CFR（9群）', '1B 残差', '0.064', '0.001', '0.778'],
    ]
)

doc.add_paragraph('5つの知見：')
doc.add_paragraph('1. C1指標は全5事例でインコヒーレンスを正確に検出（普遍的に有効）')
doc.add_paragraph('2. 2群構造はARI > 0.7で高精度に同定、多群構造はARI < 0.1で限定的')
doc.add_paragraph('3. 決定力ベース手法と特徴量得点ベース手法は相補的')
doc.add_paragraph('4. η²が高いほどARIが高い（シミュレーション結果と整合）')
doc.add_paragraph('5. シミュレーション結果と実データ結果は一貫')

add_figure(doc,
    f'{FIG_RD}/fig1_paradox_demonstration.png',
    '図7. 5つの既報シンプソンのパラドックス事例におけるパラドックスの視覚的実証'
)

add_figure(doc,
    f'{FIG_RD}/fig3_coherence_analysis.png',
    '図8. 全5事例におけるコヒーレンス指標C1の比較：提案手法 vs ランダムベースライン'
)

add_figure(doc,
    f'{FIG_RD}/fig2_method_comparison.png',
    '図9. 5つの実データ事例における手法間比較（ARI）'
)

add_figure(doc,
    f'{FIG_RD}/fig4_eta_squared_heatmap.png',
    '図10. 実データ事例×手法のイータ二乗（η²）ヒートマップ'
)

add_figure(doc,
    f'{FIG_RD}/fig5_direction_consistency.png',
    '図11. 5つの実データ事例における効果方向の一貫性分析'
)

add_figure(doc,
    f'{FIG_RD}/fig6_summary_dashboard.png',
    '図12. 実データ検証結果のサマリーダッシュボード',
    width=Inches(6.0)
)

doc.add_page_break()

# ============================================================
# 4. DISCUSSION
# ============================================================
doc.add_heading('4. 考察（Discussion）', level=1)

doc.add_heading('二段階の有用性', level=2)
p = doc.add_paragraph()
p.add_run('第一段階（確実）：').bold = True
p.add_run('C1指標による「警告」機能——集団が均質でないことを検出。全条件で堅牢。')

p = doc.add_paragraph()
p.add_run('第二段階（条件付き）：').bold = True
p.add_run('層別化による部分集団の抽出——2群構造でARI > 0.7、多群でARI < 0.1。η²が0.4超なら有効。')

doc.add_paragraph('適用ガイダンス：')
doc.add_paragraph(
    '• 2〜3の離散的サブグループ、強い痕跡（η² > 0.4）：'
    '特徴量得点ベースのクラスタリング（手法2B）が有効。ARI > 0.7が期待できる'
)
doc.add_paragraph(
    '• 多群・連続的サブグループ、中程度の痕跡（0.15 < η² ≤ 0.4）：'
    '決定力ベース手法（1A, 1B）が部分的に有効。両ファミリーの適用を推奨'
)
doc.add_paragraph(
    '• 弱い痕跡（η² < 0.15）：抽出精度は限定的。C1はインコヒーレンスを検出しうるが、層の解釈には慎重を要する'
)

doc.add_heading('既存手法との関係', level=2)
doc.add_paragraph(
    'IONEは既存手法の代替ではなく補完である。想定されるワークフロー：\n'
    '(1) C1で集団の均質性を検証\n'
    '(2) インコヒーレンスが検出されれば層別化→層内で傾向スコア分析\n'
    '(3) この二段階調整は単独手法より信頼性の高い効果推定を可能にする'
)

doc.add_heading('主な限界', level=2)
doc.add_paragraph('1. 実データ検証は疑似一般変数を使用（真の臨床データでの検証が次のステップ）')
doc.add_paragraph('2. シミュレーションのデータ生成メカニズムは比較的単純')
doc.add_paragraph('3. Oracleとのギャップが大きい（ARI 0.020 vs 0.353）')
doc.add_paragraph('4. 二値変数（性別）の捕捉が困難（η² < 0.03）')
doc.add_paragraph('5. C1閾値0.05は暫定値（さらなる校正が必要）')

doc.add_heading('今後の展望', level=2)
doc.add_paragraph(
    '• 生存アウトカム、連続アウトカム、時間変動交絡への拡張\n'
    '• 傾向スコアとの二段階調整の正式な枠組み\n'
    '• C1の多段階診断への発展（最適サブグループ数の推奨）\n'
    '• 個人レベル臨床データベース（MIMIC-IV、UK Biobank等）での検証\n'
    '• R/Pythonパッケージの開発'
)

doc.add_page_break()

# ============================================================
# 5. CONCLUSIONS
# ============================================================
doc.add_heading('5. 結論（Conclusions）', level=1)

doc.add_paragraph(
    'IONEは観察研究における隠れた集団構造の検出と抽出のための枠組みを提供する。66,600件の'
    'シミュレーション評価と5つの既報シンプソンのパラドックス事例への実証により、二段階の貢献を実証した：'
)

p = doc.add_paragraph()
p.add_run('1. C1コヒーレンス指標').bold = True
p.add_run('は集団のインコヒーレンスを確実に検出する')

p = doc.add_paragraph()
p.add_run('2. 層別化による部分集団抽出').bold = True
p.add_run('は、痕跡が十分に強く構造が離散的な場合に有効')

doc.add_paragraph()
p = doc.add_paragraph()
p.add_run('コヒーレンス評価を観察研究報告の標準的なステップとして組み込むことを推奨する。').bold = True

doc.add_page_break()

# ============================================================
# REFERENCES
# ============================================================
doc.add_heading('参考文献（全28件）', level=1)

doc.add_paragraph('主要な引用文献：')
refs = [
    '[4] Simpson EH (1951) — シンプソンのパラドックスの原論文',
    '[9] Charig et al. (1986, BMJ) — 腎結石治療',
    '[10] Bickel et al. (1975, Science) — UCバークレー入学',
    '[11] von Kugelgen et al. (2021, IEEE TAI) — COVID-19致死率',
    '[12] Morris (2021) — イスラエルワクチン有効性',
    '[13] Appleton et al. (1996) — 喫煙・死亡率パラドックス',
    '[14] Rosenbaum & Rubin (1983) — 傾向スコア',
    '[15] Hansen (2008) — 予後スコア',
    '[19] Schneeweiss et al. (2009) — 高次元傾向スコア',
    '[25] Higgins & Thompson (2002) — I²統計量',
    '[26] Morris et al. (2019) — ADEMPフレームワーク',
    '[27] Hubert & Arabie (1985) — Adjusted Rand Index',
    '[28] Strehl & Ghosh (2002) — Normalised Mutual Information',
]
for ref in refs:
    doc.add_paragraph(ref)

doc.add_paragraph()
doc.add_paragraph('（完全な参考文献リスト（28件）は英語版原稿を参照）')

doc.add_page_break()

# ============================================================
# SUBMISSION INFO
# ============================================================
doc.add_heading('投稿先情報', level=1)

add_table(doc,
    ['項目', '内容'],
    [
        ['投稿先', 'BMC Medical Research Methodology'],
        ['特集号', 'Causal inference and observational data vol. 2'],
        ['締切', '2026年7月30日'],
        ['IF', '3.4（オープンアクセス）'],
        ['言語', 'British English（原稿）/ 日本語（本抄訳）'],
    ]
)

doc.add_heading('空欄箇所', level=2)
doc.add_paragraph('以下の項目は現時点で空欄としています：')
doc.add_paragraph('• 著者名・所属・連絡先')
doc.add_paragraph('• 利益相反・資金源・著者貢献・謝辞')
doc.add_paragraph('• リポジトリURL')
doc.add_paragraph('• Monte Carlo標準誤差（補足表向け）')
doc.add_paragraph('• Additional file 1（補足方法の詳細）')
doc.add_paragraph('• Additional file 4（補足結果の詳細）')
doc.add_paragraph('• STROBE-Sim Item 18（MC SE in main tables）, Item 23/25（funding/funder role）')

doc.add_paragraph()
p = doc.add_paragraph()
p.alignment = WD_ALIGN_PARAGRAPH.CENTER
p.add_run('本抄訳は原稿（約7,300語、図12点、表7点）の全セクションを網羅しています。').italic = True

# --- Save ---
outpath = '/home/ubuntu/repos/stratification_project/results/manuscript/IONE_manuscript_japanese_summary.docx'
doc.save(outpath)
print(f'Saved to {outpath}')
