# Biostatistics（Oxford）査読者目線 プレ・サブミッション・クリティカル・レビュー v5

対象原稿：`results/manuscript/biostatistics_submission/IONE_biostatistics_v3.md` / `.docx` / `v3_ione_biostatistics_submission_package.zip`  
想定投稿先：*Biostatistics*（Oxford University Press）  
レビュー日：2026-08-13  
レビュー実施環境：`bougtoir/ione-stratification-framework`, branch `devin/ione-rsm-reframe`  

---

## 1. 総合評価

**判断：25ページ対応後、体裁は前回（v4）より大幅に改善された。しかし、Biostatistics 編集部・査読者が重視する「原著論文としての統計的方法論的新規性」「D/C/R 再現性」「Vancouver 上標引用」「Supplementary Materials の体裁」について、いくつかの残存リスクがある。特に (1) 引用番号が Word 上標になっていない、(2) 見出しが青色 Calibri のまま、(3) Supplementary docx に重複・空セクションがある、(4) C1/W の統計的性質（閾値・サンプリング分布）が未明示、(5) D/C/R 再現性バッジのためのコードアーカイブが未整備、が編集前に対応すべき課題。**

### 強み（維持すべき点）
- 25 ページ制限をクリア：double-spaced PDF が 25 ページ、本文 3,338 語。
- タイトルページの図/表/語数が動的に生成され、実文書と一致。
- 全図表が本文で順次言及されている（Figure 1–5、Table 1, 3, 7）。
- 本文 DOCX 内に図表がインライン配置され、別途 `biostatistics_figures.pptx` と `biostatistics_tables_separate.docx` が zip に同梱されている。
- `|` を含む問題の数式パターンは排除され、PDF で変な記号（∨, ¿ 等）が出ない。
- 全数値が `results/summary` 配下の CSV から読み込まれ、ハードコードされていない。
- Vancouver 番号付き参考文献は初出順に 1–30 となっており、orphan reference なし。

### 残存リスク（修正必須～高優先）
1. **引用番号の体裁**：本文 `[1]`, `[2][3]` が通常サイズのテキスト。Biostatistics の Vancouver スタイルでは上標（superscript）が標準的。
2. **見出しのフォント**：`Abstract`, `1. Introduction` 等 Heading 1–2 がデフォルトの青色 Calibri。本文は Times New Roman だが見出しが浮く。
3. **Supplementary docx の体裁**：冒頭と `Additional files` セクションで「Additional file 1: Supplementary Methods」が重複。末尾の `{{REFS}}` により空の「References」見出しが生成される。
4. **C1/W の統計的正当化**：C1 は `1 − I²` だが、閾値やサンプリング分布、帰無分布が示されていない。低い C1 が「隠れ効果修飾の証拠」と解釈できる根拠が弱い。
5. **相対バイアス低減の Monte Carlo SE**：Supplementary Tables S1–S4 で `Rel reduction RE SE` が 0.2–1.2 程度に広がり、[0,1] に拘束される量に対して対称近似の SE は不適切。
6. **拡張感度分析は 10 反復**：SE が大きく、方法間比較がノイズに埋もれている。
7. **D/C/R 再現性バッジの未整備**：GitHub リンクはあるが、Figshare/Zenodo 等の永続アーカイブ・commit hash ファイル・lock ファイルがない。
8. **Morris 2021 ソースがブログ投稿**：半合成例のデータソースとして、査読者から「一次データ出典として不適切」と指摘される可能性。

---

## 2. Biostatistics 投稿規定・スコープとの適合度

Biostatistics の *Information for Authors* によれば、投稿論文は以下のいずれかを満たすべき：

1. 健康・生物医学の実問題に動機付けられた新しい確率モデルまたは統計的方法論の開発
2. 健康・生物医学の実問題に対する統計的方法論の革新的応用
3. 健康・生物医学への応用に関わる統計的方法論の領域の批評的レビュー
4. 重要な健康・生物医学データに基づくケーススタディ

### 現状の適合度

| 適合要件 | 現状 | 適合度 | 備考 |
|---|---|---|---|
| 統計的方法論の新規性（C1, W 診断） | C1 = 1 − I²、W = CATE 分散説明率を定義 | ◎ | 新しい統計診断の提示は満たす |
| 実問題への動機付け（IPD meta-analysis） | IPD プール時の隠れ効果修飾 | ◎ | 健康データの証拠統合という実問題 |
| 方法論的貢献の明確化 | IONE フレームワークとして提示 | ◎ | ただし「診断」と「調整」の区別を強化すべき |
| 25 ページドラフト制限 | 25 ページ / 3,338 語でクリア | ◎ | 表・図を除く本文は制限内 |
| 引用番号体裁 | 通常テキスト | △ | **高：上標化** |
| フォント・見出し統一 | Heading が青 Calibri | △ | **高：黒の Times New Roman** |
| Supplementary 体裁 | 重複・空 References あり | △ | **中：整理** |
| コード・データ可用性 D/C/R | GitHub ある、DOI/lock/hash なし | △ | **中：永続アーカイブ** |
| 図表ファイル別提出 | png/eps/pptx 同梱 | ◎ | 個別ファイルは整備済み |

### ジャーナル適合度をさらに高めるための方向性

Biostatistics は「original methodology should be grounded in substantive problems」と明記している。現状の Intro は IPD meta-analysis 一般と Simpson's paradox の例で動機付けしているが、**Biostatistics 読者が最も関心を持つのは「メタアナリシスにおける異質性診断」という統計的問題** である。したがって、以下の再構成を提案する：

- **Abstract の先頭に「what is the statistical problem?」を置く**：
  - 現在：「In IPD meta-analysis, marginal treatment-effect estimates can be biased when hidden effect modifiers are ignored.」
  - 改善例：「Marginal summaries in individual participant data (IPD) meta-analysis can be biased when hidden effect modifiers are ignored. We propose two coherence diagnostics, C1 and W, that flag when a pooled IPD population is incoherent with respect to the conditional treatment effect.」
  - このように「方法（C1/W）」を先に置くことで、Biostatistics 読者にすぐに方法論的貢献が伝わる。

- **Title のシャープ化**：
  - 現在：「IONE: Incoherence-Oriented Neutralisation and Extraction for hidden effect modification in individual participant data meta-analysis: a simulation study of stratification-based extraction」
  - 提案例：
    - 「Coherence diagnostics for hidden effect modification in individual participant data meta-analysis: a simulation study」
    - 「C1 and W: diagnostics for incoherent treatment effects in pooled individual participant data」
  - IONE という造語は本文内で定義すればよく、タイトルは統計的貢献を前面に出す。

- **Introduction の後半で「なぜ既存メタアナリシス手法では不十分か」を強調**：
  - subgroup analysis、meta-regression、one-stage mixed model は *measured* な treatment-covariate interaction や *study-level* heterogeneity を扱う。
  - 一方、IONE は *pooled participants* 自体が内的に一様かどうかを問う新しい診断層を追加する。
  - この対比を 1 段落で明確にすると、新規性が際立つ。

- **Discussion に「Biostatistics 的文脈での位置づけ」段落を追加**：
  - 既存の IPD meta-analysis 診断ツール（heterogeneity statistics、interaction tests、posterior predictive checks 等）との関係を簡潔に述べ、IONE が「model-checking / sensitivity」ステップとして組み込まれることを示す。
  - ただし、実在しない文献や過度な主張は避ける。

- **Cover letter を Biostatistics 的観点で再強調**：
  - 現在でもスコープ説明はよく書けているが、冒頭で「two new diagnostics (C1, W)」と「simulation-based evaluation」を 1 文で強調する。
  - 再現性に関して、GitHub + Zenodo/Figshare DOI の取得予定を明記する。

---

## 3. 査読者が突きそうな科学的・方法論的指摘

### 3.1 C1 と W の統計的性質

- **C1 の解釈基準が不明**：Table 1 で random baseline C1 = 0.883、最良方法 C1 = 0.927 とほぼ重なる。「C1 is low」は相対的に何と比較すればよいか示されていない。
  - 提案：null シナリオ（隠れ効果修飾なし）下で C1/W の経験分布をシミュレーションで求め、経験的閾値（例：C1 の 95 パーセンタイル）を提示する。または、C1 を「診断的傾向指標」と位置づけ、閾値は将来の研究に委ねることを明記。

- **W_est の outcome model 依存性**：W_est はロジスティック回帰 `Y ~ X + A + X·A` の当てはまりに依存。誤指定（高次項・非線形項省略）に対する感度分析がない。
  - 提案：Appendix/Supplementary に、outcome model を `Y ~ X + A + X·A + X²` 等に変えた場合の W_est 変動を報告。または、W_est は「補助的指標」であり、誤指定リスクがあることを Discussion で一段強調。

- **DerSimonian-Laird (DL) の使用理由**：発見された層は同じデータから導かれるため推定値が独立ではない。本文は caveats で言及しているが、なぜ DL を選んだのか、cluster-robust SE や Bayesian hierarchical model との比較がない。
  - 提案：Methods で「層内推定値は独立ではないが、Biostatistics 読者に親しみやすい標準的 random-effects 統合を用い、感度として固定効果も示す」と理由を追加。または Supplementary で cluster-robust SE による感度分析を追加。

### 3.2 結果の解釈と主張の強さ

- **ARI が極めて低い**：最良非オラクル ARI = 0.032。オラクル k-means でも 0.372。本文は「診断的検出は可能だが、真の構造の抽出は困難」と慎重だが、Abstract/Conclusions の「partially reduce ATE bias」は「調整手法」として読まれるリスクがある。
  - 提案：Abstract/Conclusions で「primarily a diagnostic flag」と明記。ATE バイアス低減は「層別化が成功した場合のベストケースの例示」であることを Methods/Discussion で強調。

- **相対バイアス低減の SE**：Supplementary Tables S1–S4 で `Rel reduction RE SE` が 1.230 等を超える。比率に対する対称的 SE は不適切で、信頼区間が [-1.5, 2.5] のようになり解釈不可能。
  - 提案：絶対バイアス低減 `abs_bias_crude - abs_bias_re` に SE を付けて報告。相対低減は括弧内の記述統計のみに留める。または `log(relative risk)` 変換等を用いる。

- **10 反復の拡張感度分析**：K、サンプルサイズ、Z→X、Z→Y の感度表が 10 反復。SE が大きく、方法間の比較が困難。
  - 提案：最低でも 30–50 反復で再実行。計算コストが高い場合は、10 反復の結果を「探索的」として明記し、主要結論を primary scenario（50 反復）のみに基づくことを明言。

### 3.3 半合成例（Table 3）

- **Bias reduction の定義が不明**：Table 3 の `Bias reduction` 列が絶対差か相対差かキャプションに記載されていない。
  - 提案：キャプションに「`Bias reduction` is the absolute difference between crude and random-effects ATE bias」と明記。

- **Morris 2021 ソースの扱い**：Israel vaccine データがブログ投稿。Stat Med レビュー（`results/manuscript/statmed_submission/reviewer2_comments.txt`）でも指摘されている。
  - 提案：Israeli Ministry of Health 等の公式データソースに差し替えるか、本文中で「publicly available data-analysis example, not a peer-reviewed study」と明確に限定。

---

## 4. 再現性（Data / Code Availability）

Biostatistics は D/C/R バッジ制度を採用しており、**R（Data + Code reproducible）** を目指すべき。

| 項目 | 現状 | 指摘 |
|---|---|---|
| 公開リポジトリ | https://github.com/bougtoir/ione-stratification-framework | ◎ |
| `requirements.txt` / `environment.yml` | 存在するが `>=` ばかり | △：lock ファイルまたは `pip freeze` 出力を追加 |
| README 再現手順 | 記載あり | ◎ |
| commit hash 記録 | ファイルなし | △：`results/commit_hash.txt` 等を生成 |
| Zenodo/Figshare DOI | 未取得 | △：Biostatistics はコードアーカイブを推奨 |
| 固定 random seed | Methods で言及 | ◎ |
| ワンコマンド再生成 | `generate_summary.py` → `generate_ione_rsm_v3.py` → `generate_rsm_tables.py` | ◎ |

**提案**：
- `generate_ione_rsm_v3.py` 実行時に `git rev-parse HEAD` を `results/commit_hash.txt` に書き出し、Declarations/Data Availability にパスを記載。
- `requirements-lock.txt`（または `conda env export`）を追加し、pip バージョンをピン留め。
- 投稿前に GitHub release を作成し、Zenodo DOI を取得。カバーレターと Data Availability で DOI を言及。

---

## 5. 原稿表現・体裁の問題

### 5.1 引用番号・参考文献
- **本文 `[1]`, `[2][3]` が通常サイズ**。`md_to_rsm_docx.py` の `_apply_inline` で `[n]` パターンを検出し、`run.font.superscript = True` を設定する。
- **参考リストの `[1]` は通常サイズでよい**（Vancouver reference list は多くの雑誌で通常サイズ）。

### 5.2 フォント・見出し
- **PDF 見出しが青 Calibri**。`md_to_rsm_docx.py` で `Heading 1`–`Heading 3` のフォントを Times New Roman、色を黒に設定。
- **図キャプションの太字**: 現在はボールド。これは問題ないが、Figure/Table の上下スペースを統一すると印象が良い。

### 5.3 Supplementary docx
- **「Additional file 1: Supplementary Methods」が 2 回出現**。`biostatistics_supplementary_v3.md` の冒頭の重複を削除するか、`generate_ione_rsm_v3.py` の supp_md から初期重複を除く。
- **空の「References」見出し**。Supplementary には本文からの引用がないため、`{{REFS}}` マーカーを削除する。

### 5.4 AI 宣言の日付
- title page: 「August 2025-August 2026」
- main docx: 「between August 2025 and August 2026」
- 統一する。

---

## 6. ジャーナル適合度を上げるための具体的提案（優先度順）

### 6.1 必須（投稿前に対応）

1. **本文引用番号を上標化**（`md_to_rsm_docx.py` 修正）
   - `_apply_inline` で `[n]` を分割し、`run.font.superscript = True`。
2. **見出しのフォント・色を修正**（`md_to_rsm_docx.py` 修正）
   - `Heading 1`–`Heading 3` を Times New Roman、黒色に。
3. **Supplementary docx の重複・空 References を削除**
   - `generate_ione_rsm_v3.py` の supp_md から初期 `Additional file 1` 重複と `{{REFS}}` を除去。
4. **Abstract / Conclusions で「primarily a diagnostic flag」と明記**
   - ATE バイアス低減は成功例の例示であり、必ずしも保証された調整効果ではないことを強調。
5. **Table 3 の `Bias reduction` 定義をキャプションに追加**
   - 絶対差 `|bias_crude| − |bias_re|` であることを明記。
6. **Morris 2021 ブログソースの扱い**
   - 公式一次データソースに差し替えるか、本文・参考リストで「data-analysis example」と限定。

### 6.2 高優先（査読をスムーズにする）

7. **C1/W の解釈基準を追加**
   - null シナリオ下の経験分布または経験的閾値を Supplementary に追加。不可能なら Discussion で「経験的傾向指標」と位置づける。
8. **DL 層別化の相関を考慮した標準誤差**
   - cluster-robust SE または固定効果との比較を Methods/Discussion で追加。
9. **W_est の outcome model 誤指定感度**
   - Supplementary で高次項・非線形項を含む model への感度を報告。
10. **拡張感度分析の反復数増加または SE 表現の変更**
    - 相対低減に SE を出さず、絶対バイアス低減に SE を付ける。反復数を 30–50 に増やすか、10 反復結果は探索的と明記。
11. **D/C/R バッジ整備**
    - `results/commit_hash.txt` 生成、`requirements-lock.txt` 追加、GitHub release + Zenodo DOI 取得。

### 6.3 中優先（ジャーナル適合度向上）

12. **Title シャープ化**
    - IONE の造語をサブタイトルに下げ、統計貢献（coherence diagnostics / IPD meta-analysis）を前面に。
13. **Abstract リード文の変更**
    - 方法論的新規性（C1, W）を最初に提示し、応用背景を後に。
14. **Discussion に「Biostatistics 的文脈での位置づけ」追加**
    - IPD meta-analysis 診断ツール群との関係、および sensitivity step としての使い方。
15. **AI 宣言日付統一**
    - title page と main docx を一致。
16. **environment.yml / requirements.txt にピン留めまたは lock ファイル追加**

### 6.4 任意（さらに強い論文にする）

17. **実際の IPD データ 1 例を追加**（可能であれば）。
18. **Bayesian hierarchical 層別化との比較**。
19. **C1 / W の漸近分布や検定力評価**（null 分布下の理論的性質）。
20. **簡易 Python パッケージ化**（GitHub + `pip install` 可能な構成）で Software news 投稿の可能性を残す。

---

## 7. 総合判断

- **Biostatistics には依然として妥当な投稿先**。25 ページ制限クリア、動的タイトルページ、図表の適切な分離、再現性のための公開リポジトリは整っている。
- **現段階で最もジャーナル適合度を下げるリスクは体裁面**：引用上標、見出しフォント、Supplementary 重複、AI 宣言の不一致。これらは技術的に容易に修正でき、編集部スクリーニングを通過する上で重要。
- **科学的には「C1/W の解釈基準」「相対バイアス低減の SE」「10 反復感度分析」「W_est の誤指定感度」「DL の独立性仮定」が査読者から最も突かれるポイント**。これらに対する追加説明または追加シミュレーションを Methods / Results / Discussion に組み込むと、Major revision の可能性を大きく減らせる。
- **タイトルと Abstract を「方法論的診断（C1, W）」中心に再構成**すれば、Biostatistics 読者に新規性が伝わりやすくなる。

---

## 8. 図表の再確認結果（v5 時点）

| 図表 | 本文言及 | 備考 |
|---|---|---|
| Figure 1 | あり | Primary IPD scenario 後。3 パネル |
| Figure 2 | あり | Sensitivity to K 後 |
| Figure 3 | あり | Semi-synthetic illustrations 後 |
| Figure 4 | あり | Sample size sensitivity 後 |
| Figure 5 | あり | Non-linearity robustness 後 |
| Table 1 | あり | Primary scenario |
| Table 3 | あり | Semi-synthetic illustrations |
| Table 7 | あり | Non-linearity robustness |
| Supp. Table S1–S4 | あり | 各感度セクション |

全図表は本文で順に言及されており orphan なし。ただし Table 3 の `Bias reduction` 定義追加が望ましい。

---

## 9. 推奨次ステップ

1. まず必須の体裁修正（上標・見出し・Supplementary 重複・AI 宣言統一）を `md_to_rsm_docx.py` / `generate_ione_rsm_v3.py` で実施し、docx/PDF/zip を再生成。
2. 次に高優先の科学的修正（C1/W 閾値・相対 SE・10 反復の扱い・W_est 誤指定・DL 相関）を検討。追加シミュレーションが必要な場合は別ブランチで実施。
3. 最後にタイトル/Abstract/Cover letter の再構成と D/C/R バッジ整備を実施。
