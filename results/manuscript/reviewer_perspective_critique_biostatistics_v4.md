# Biostatistics（Oxford）査読者目線 プレ・サブミッション・クリティカル・レビュー v4

対象原稿：`results/manuscript/biostatistics_submission/IONE_biostatistics_v3.md` / `.docx` / `v3_ione_biostatistics_submission_package.zip`  
想定投稿先：*Biostatistics*（Oxford University Press）  
レビュー日：2026-08-13  
レビュー実施環境：`bougtoir/ione-stratification-framework`, branch `devin/ione-rsm-reframe`

---

## 1. 総合評価

**判断：Biostatistics へのスコープ適合度は高いまま。前回（v3）指摘の多く（Supplementary Materials 分離、K 選択根拠、neutralisation 定義、Monte Carlo SE 追加、Figure 1 パネル分割、ダブルスペース PDF）が対応された。しかし、投稿前に避けられない体裁・再現性・主張の問題が残っている。最も深刻なのは (1) ダブルスペース PDF が 33 ページで 25 ページ制限を超過、(2) 引用番号が Word 上標になっていない、(3) タイトルページの数値がハードコードで実態と矛盾、(4) 編集可能 pptx が zip に含まれていない、(5) 拡張感度分析の Monte Carlo 誤差が大きすぎること。**

### 強み（対応済み・維持すべき点）
- Supplementary Materials への分離：Additional files、Abbreviations、感度表 S1–S4 が `biostatistics_supplementary_v3.docx` に移動し、本文は Table 1・3・7 + Figure 1–5 に整理された。
- Figure 1 は 3 パネル（ARI / C1・W / ATE bias reduction）に分割され、異なるスケールの指標を混在させなくなった。
- K 選択の a priori ルールと「neutralisation」の定義が Methods / Abstract に追加された。
- 拡張感度表に Monte Carlo SE 列が追加され、10 反復の不確実性が可視化された。
- Vancouver 番号付き参考文献は初出順に 1–32 と整理され、orphan reference なし。すべての図表は本文で言及されている。
- 数式は LaTeX 表記ではなく Word OMML（下付き `W_true` / `W_est`、上付き `I^2`、`τ^2`）に変換され、PDF で視認できる。

### 残存リスク（修正必須～高優先）
- **本文長超過**：double-spaced PDF が 33 ページ（Letter サイズ）。Biostatistics のドラフト 25 ページ制限を明確に超過。
- **引用・参考文献の体裁**：本文 `[1]` や参考リスト `[1] ...` が通常サイズの括弧付きで、Word-native の上標になっていない。
- **タイトルページのハードコード**：「Number of tables: 7」「Word count: ... ~5,900」が生成スクリプト内にリテラルで書かれており、実際の主文書（表 3 個、語数 ~6,400）と矛盾。
- **編集可能 pptx の欠落**：zip に `biostatistics_figures.pptx` が含まれていない。`generate_ione_rsm_v3.py` が `results/figures/rsm_figures.pptx` を探しているが、実際は `results/figures/pptx/rsm_figures.pptx` に存在するため、パス不一致で追加されていない。
- **拡張感度分析の反復数**：K・サンプルサイズ・Z→Y・Z→X 各感度表は 10 反復。`Rel reduction RE SE` が 0.2–1.2 程度に広がり、相対バイアス低減の解釈が困難。
- **Supplementary docx の重複**：「Additional file 1: Supplementary Methods」が冒頭と「Additional files」セクションの 2 カ所に同じ内容で出現。空の「References」セクションも残っている。

---

## 2. 前回 v3 レビュー指摘の対応状況

| v3 指摘 | 対応状況 | 備考 |
|---|---|---|
| Supplementary Materials 分離 | ◎ | 主文書は簡潔化されたが、ページ数は依然超過 |
| K 選択の a priori ルール記載 | ◎ | Methods に `{2, 3, min(K_true,4), K_true}` を明記 |
| neutralisation 定義 | ◎ | Methods / Abstract に定義を追加 |
| Monte Carlo SE 追加 | ◎ | 拡張感度表（S1–S4）に SE 列追加 |
| Figure 1 分割・正規化 | ◎ | 3 パネル化されスケール問題は解消 |
| ダブルスペース PDF | ◎ | 生成されたが 33 ページで制限超過 |
| Data/Code Availability 拡充 | △ | Zenodo DOI 未取得、commit hash ファイルなし |
| AI 宣言拡充 | ◎ | 使用 LLM・目的・人間レビュー体質を記載 |
| 25 ページ制限 | × | 主文書 6,417 語、PDF 33 ページ |
| タイトル・Abstract 短縮 | △ | Abstract は 219 語に改善、タイトルは依然として long |
| カバーレター | ◎ | Biostatistics 向けに書き換え済み |

---

## 3. Biostatistics 投稿規定との適合度

| 要件 | 現状 | 適合度 | 対応の急務 |
|---|---|---|---|
| スコープ（health/disease 統計的方法） | IPD メタアナリシス診断法 | ◎ | — |
| ダブルスペース PDF | 生成済みだが 33 ページ | △ | **高**：25 ページ以内に圧縮 |
| ページ制限（表・図除く 25 原稿ページ） | 超過 | △ | **高**：本文 6,400 語 → ~5,000–5,500 語へ |
| 引用番号体裁 | `[1]` 通常テキスト、上標なし | △ | **高**：`run.font.superscript = True` を適用 |
| タイトルページ | 存在するが数値がハードコードで誤り | △ | **高**：表数・語数を動的に修正 |
| 図表個別ファイル | PNG/EPS は zip 内にあるが pptx 欠落 | △ | **高**：`biostatistics_figures.pptx` を同梱 |
| Data/Code Availability | GitHub 公開、environment.yml あり、DOI未取得 | △ | 中：Zenodo/Figshare DOI 取得またはリリース化 |
| 再現性バッジ（D/C/R） | commit hash ファイルなし、pip バージョン未固定 | △ | 中：lock ファイル・hash ファイル追加 |
| 参考文献 Vancouver | 1–32 番号、順序一致 | ◎ | — |
| 図表本文言及 | Figure 1–5、Table 1・3・7、Supp. Table S1–S4 | ◎ | — |

### 3.1 ページ数・語数の詳細

- `IONE_biostatistics_v3_double_spaced.pdf`: 33 ページ（Letter サイズ、11 pt、2 倍行間）。
- 主文書 `.docx` の本文単語数（References 以前、表・図除く）：約 6,417 語。
- セクション別語数：
  - Abstract: 230
  - Introduction: 1,164
  - Methods: 2,008
  - Results: 1,514
  - Discussion: 1,084
  - Conclusions: 93
  - Declarations: 301
- 目標：Biostatistics ドラフト 25 ページ制限に合わせ、本文を **5,000–5,500 語**（約 20–22 ページ分）に圧縮。

### 3.2 タイトルページの不一致

`title_page_biostatistics_v3.docx` には以下のリテラルが記載：

```
Number of figures: 5
Number of tables: 7
Word count: Abstract ~240; Main text ~5,900 (excluding references, tables and figures)
```

実態は：

- 主文書 `.docx` 内の表数：**3**（Table 1, 3, 7）
- 主文書本文語数：**~6,417**（References 以前、表・図除き）
- Abstract 語数：**219**（~240 は近似的に許容）

**「Number of tables: 7」は `biostatistics_tables_separate.docx` の総表数か、旧版の名残。主文書用タイトルページでは「Number of tables: 3」とすべき。**

---

## 4. 査読者が突きそうな科学的・方法論的指摘

### 4.1 新規性とメソッドの正当化
- **C1 / W の統計的性質が未明示**。C1 は `1 - I²` であるが、`I²` の計算対象が「発見された層の層固有 log OR」であり、層数やサンプルサイズ、各層イベント数によって決定論的に変化する。低い C1 が「隠れ効果修飾の証拠」と解釈するための閾値やサンプリング分布がない。査読者は「これは単なる層間異質性の記述ではないか」と指摘する可能性がある。
- **W_est のモデル依存性**。`Y ~ X + A + X×A` のロジスティック回帰が正しく指定されていないと `W_est` は誤る。Outcome model の誤指定に対する感度分析がない。
- **DerSimonian-Laird (DL) の使用**。層は同じデータから発見されるため、層固有推定値は独立ではない。本文はこの点を Methods と Discussion で述べているが、DL である必然性（例：Bayesian 階層モデルとの比較）が議論されていない。

### 4.2 結果の解釈と主張の強さ
- **ARI が極めて低い**。最良非オラクル ARI は 0.032（Table 1）。オラクル k-means でも 0.372。本文は「診断的検出は可能だが、真の構造の抽出は困難」と慎重に論じているが、Abstract / Conclusions の「partially reduce ATE bias」が読者には「有用な調整手法」と誤読される可能性がある。特に `Crude bias 0.01865 → RE bias 0.00816` は絶対差 0.01 未満で、臨床的意義は不明。
- **C1 の圧縮**。Table 1 の C1 は 0.858–0.927 の狭い範囲。random baseline が 0.883 なので、多くの方法が random と区別しにくい。「C1 is low」の基準が読者には伝わらない。
- **相対バイアス低減の SE が不適切**。Supplementary Tables S1–S4 で `Rel reduction RE SE` が 0.386、1.230 などを超える。相対低減は [0,1] に拘束されるが、通常の Monte Carlo SE は比の分布に対して対称近似を仮定しているため、CI が [-1.5, 2.5] のようになり解釈不可能。**相対低減には SE を報告せず、絶対バイアスと絶対低減量（SE 付き）のみ報告し、相対低減は記述統計として括弧内に示すのが望ましい。**
- **拡張感度分析は 10 反復**。Table S2–S4 の多くのセルで SE が大きく、方法間の比較がノイズに埋もれている。`n=500` の `PS_propensity_score`（rel reduction 0.005; SE 0.386）などは信頼できない。20–50 反復への増加、または方法間差の検定力計算が必要。

### 4.3 半合成例（Table 3）
- **「real-data illustration」という表現**。Table 3 のキャプションが "Best real-data illustration result" となっているが、これらは公開集計値から再構成した擬似個人データであり、実際の IPD ではない。"Semi-synthetic illustration" に統一すべき。
- **バイアス低減の絶対値が小さい**。Table 3 の Bias reduction は 0.011–0.114。これが何を表すのか（絶対差？相対差？）がキャプションに明記されていない。Methods に「Table 3 の bias reduction は `|bias_crude| - |bias_stratified|` の平均」と明記する必要がある。
- **Morris [19]（Israeli vaccine）がブログ投稿**。査読者は一次データ出典として不適切とみなす可能性がある。Israeli Ministry of Health または論文化されているデータソースへの差し替えを推奨。

---

## 5. 原稿表現・体裁の問題

### 5.1 引用番号・参考文献
- **本文の `[1]`, `[2][3]` が通常サイズ**。Word-native の上標（`run.font.superscript = True`）にしていない。Vancouver 番号付きスタイルでは多くの雑誌が上標を求める。`md_to_rsm_docx.py` の `_apply_inline` または `CiteManager.cite` 出力段階で上標化する。
- **参考リストも `[1]`, `[2]` が通常サイズ**。こちらも上標または少なくとも括弧内で統一。
- **参考リストに blog 投稿 [19] が含まれる**。可能であれば peer-reviewed または公式行政データに置き換える。

### 5.2 フォント・見出し
- **PDF 見出しが Calibri（青色）**。本文は Times New Roman だが、`Abstract`, `1. Introduction` などの Heading スタイルがデフォルトの青色 Calibri のまま。`md_to_rsm_docx.py` で Heading 1–3 のフォントも Times New Roman、色黒に設定する。
- **Figure 1 の x 軸ラベルが重なり読みにくい**。メソッド名（`1A_predicted_prob` など）を 45 度回転、または短いエイリアス（`1A`, `1B`, `2A`, `2B`, `PS`, `Progn`, `GMM`, `Oracle-K`, `Oracle-Q`, `Random`）に置き換える。

### 5.3 Supplementary docx
- **「Additional file 1: Supplementary Methods」が 2 回出現**。`biostatistics_supplementary_v3.md` の冒頭と `_additional_files()` の両方で追加されている。片方を削除。
- **空の「References」セクション**。`{{REFS}}` マーカーがあるが引用がないため、空の見出しが生成される。削除。

### 5.4 zip パッケージ
- **`biostatistics_figures.pptx` が zip に含まれていない**。`generate_ione_rsm_v3.py` 内のパス `os.path.join(FIG_DIR, 'rsm_figures.pptx')` を `os.path.join(FIG_DIR, 'pptx', 'rsm_figures.pptx')` に修正し、zip 内ファイル名を `biostatistics_figures.pptx` にリネームする。
- **PNG/EPS ファイル名に `rsm_` が残る**。`fig1_rsm_ipd_primary.png` などは Biostatistics 向け名称 `fig1_ione_ipd_primary.png` 等に変更するか、少なくとも提出用 zip 内では `biostatistics_` 接頭辞に統一すると印象が良い。

---

## 6. 再現性（Data/Code Availability）

| 項目 | 現状 | 指摘 |
|---|---|---|
| 公開リポジトリ | https://github.com/bougtoir/ione-stratification-framework | ◎ |
| `requirements.txt` / `environment.yml` | 存在するが `>=` ばかり | △：lock ファイル（`pip freeze` / `conda env export`）を追加 |
| README 再現手順 | 記載あり | ◎：ただしタイトルページに省略されすぎ |
| commit hash 記録 | **ファイルなし** | ×：「commit hash is recorded in the repository」と記載があるが実ファイルがない |
| Zenodo/Figshare DOI | 未取得 | △：Biostatistics D/C/R バッジ取得前に必要 |
| 固定 random seed | README / Methods で言及 | ◎：seed 値は `data_generation.py` 等にあるはず |
| ワンコマンド再生成 | `generate_summary.py` → `generate_ione_rsm_v3.py` → `generate_rsm_tables.py` | ◎：実行確認済み |

**特に「commit hash used to generate the results is recorded in the repository」という記述は虚偽になりうる。** 実際には `results/commit_hash.txt` のようなファイルが見当たらない。以下のいずれかを行う：
- `generate_ione_rsm_v3.py` 実行時に `git rev-parse HEAD` を `results/commit_hash.txt` 等に書き出す。
- あるいは上記記述を削除。

---

## 7. 優先度付きアクションリスト

### 7.1 投稿前に必須（desk reject / major revision 回避）
1. **本文を 25 ページ以内に圧縮**。目標語数 5,000–5,500 語。具体的には：
   - Introduction の Simpson's paradox 例を 2–3 例に絞る（現在 5 例、~300 語）。
   - Methods の「Stratification methods」で各方法の根拠を短縮。
   - Discussion の「Future directions」は 1 段落にまとめる。
   - `Implications for practice` と `Conclusions` を統合。
2. **引用番号を Word 上標に変換**。`md_to_rsm_docx.py` の `_apply_inline` で `[n]` パターンを検出し `run.font.superscript = True` を設定。
3. **タイトルページのハードコード値を動的に修正**：
   - `Number of tables` を主文書内の実際の表数（3）に。
   - `Word count` を `python-docx` で自動計算した値に更新（現在 ~6,400）。
4. **Supplementary docx の重複・空セクションを削除**。
   - 「Additional file 1」の重複を解消。
   - 空の「References」見出しを削除。
5. **編集可能 pptx を zip に同梱**。`generate_ione_rsm_v3.py` の pptx パスを `results/figures/pptx/rsm_figures.pptx` に修正し、zip 内では `biostatistics_figures.pptx` として保存。

### 7.2 高優先（査読をスムーズにする）
6. **拡張感度分析の反復数増加または表示方法の見直し**：
   - 最低でも 20 反復、できれば 50 反復で再実行。
   - 相対バイアス低減に SE を報告するのをやめ、絶対バイアス低減（`abs_bias_crude - abs_bias_re`）の SE を報告。相対値は括弧内にのみ記す。
7. **DL 層別化の限界を一段深める**： strata 間の相関を考慮した標準誤差（例：cluster-robust SE、Bayesian 階層モデル）を議論。現状の注意書きを強化。
8. **C1 / W_est の解釈基準を追加**：「C1 がどれくらい低ければアラートとするか」について、シミュレーション分布に基づく経験的閾値または絶対値の指針を示す。現状では random baseline C1=0.883、最良方法 C1=0.927 なので差が小さい。
9. **Table 3 のキャプションと定義を修正**：
   - "real-data" → "semi-synthetic"
   - "Bias reduction" が絶対差であることを明記。
   - Morris [19] ブログ引用を正式な一次データソースに差し替え。
10. **commit hash 記録**：`generate_ione_rsm_v3.py` 実行時に自動で `results/commit_hash.txt` を生成。または虚偽記述を削除。

### 7.3 中優先（ジャーナル適合度向上）
11. **見出しフォントを Times New Roman / 黒に統一**。
12. **Figure 1 の x 軸ラベルを回転または短縮**。
13. **図ファイル名の `rsm_` を `ione_` または `biostatistics_` に変更**。
14. **environment.yml / requirements.txt にピン留めバージョンまたは lock ファイルを追加**。
15. **AI 宣言の日付を統一**（title page は "August 2025-August 2026"、main docx は "between August 2025 and August 2026"）。

### 7.4 任意（さらに強い論文にする）
16. **W_est の outcome model 誤指定に対する感度分析**（高次項・交互作用追加）。
17. **Bayesian 階層モデルとの DL 比較**。
18. **実際の IPD データ 1 例を追加**（可能であれば）。
19. **C1 / W のサンプリング分布・検定力評価**（null シナリオ下での分布）。

---

## 8. 図表の再確認結果

| 図表 | 本文言及 | 場所 | 備考 |
|---|---|---|---|
| Figure 1 | あり | Primary IPD scenario 後 | 3 パネル、英語、x 軸ラベル重複 |
| Figure 2 | あり | Sensitivity to the number of strata | — |
| Figure 3 | あり | Semi-synthetic illustrations | — |
| Figure 4 | あり | Sample size sensitivity | — |
| Figure 5 | あり | Non-linearity robustness | — |
| Table 1 | あり | Primary scenario | — |
| Table 3 | あり | Semi-synthetic illustrations | キャプション「real-data」は不適切 |
| Table 7 | あり | Non-linearity robustness | — |
| Supp. Table S1–S4 | あり | 各感度セクション | SE 列追加済み、相対低減 SE が過大 |

全図表は本文で順に言及されており orphan なし。

---

## 9. 総合判断

- **Biostatistics には依然として妥当な投稿先**だが、現状の v3 パッケージは「構成は整ったが、投稿直前の体裁チェックが不十分」という印象を与える。
- **最低限の必須対応**：25 ページ圧縮、引用番号上標化、タイトルページのハードコード修正、Supplementary 重複削除、pptx 同梱、commit hash 記録。
- これらを修正すれば、Major revision なしで initial review に入れる可能性が大きく向上する。
- 科学的に最も重いのは「ARI が低い」「10 反復感度分析の信頼性」「相対低減 SE の不適切な報告」であり、これらは Methods / Results / Discussion で追加の説明または追加シミュレーションで対応すべき。
