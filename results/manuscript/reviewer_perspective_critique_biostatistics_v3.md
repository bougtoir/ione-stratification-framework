# Biostatistics（Oxford）査読者目線 プレ・サブミッション・クリティカル・レビュー

対象原稿： `results/manuscript/rsm_submission/IONE_rsm_v3.md` / `IONE_rsm_v3.docx`  
想定投稿先： *Biostatistics*（Oxford University Press）  
レビュー日： 2026-08-10

---

## 1. 総合評価

**判断： Biostatistics への適合度は高い。観察研究における隠れた効果修飾・交絡を診断するための層別化手法というテーマは、同誌の「health/disease における革新的な統計的方法」というスコープに強く合致する。ただし、現在の原稿は RSM 向けに調整された形跡があり、Biostatistics が重視する再現性バッジ（D/C/R）、簡潔な本文、および著者年式参照の整形に対応する必要がある。**

**強み**
- 主題が biostatistical method for health/disease に直結（Simpson's paradox の実例は腎結石治療、COVID-19 CFR、ワクチン有効性、喫煙死亡率、大学入学など）。
- ADEMP・STROBE-Sim による透明なシミュレーション設計。
- C1/W という 2 つの診断指標を組み合わせたアプローチは、単なる層別化手法とは区別される。
- Risk-difference ATE への estimand 選択は collapsibility 問題を回避しており、方法論的に適切。
- 感度分析（層数 K、サンプルサイズ、Z→Y 強度、Z→X 強度、非線形性）が広範。
- 数値がコードから自動生成され、ハードコードされていない。

**弱み・リスク**
- **本文が RSM 構成のまま**（Declarations / Additional files / List of abbreviations が本文末尾に入っている）。Biostatistics は Supplementary Materials への移動を推奨。
- **ページ数・語数の超過リスク**：docx 本文約 7,281 語。ダブルスペース換算で 25 ページ超（Biostatistics Overleaf テンプレートは本文＋謝辞＋参照で 25 ページ制限、表・図除く）。
- **再現性バッジ**: GitHub リンクはあるが、Zenodo/Figshare 等の DOI 付きアーカイブ・実行環境の固定化が不足。
- **Figure 1 は複数スケールの指標を 1 パネルに入れており読みにくい**。
- **実データ例 Table 3 の K 選択基準が Methods に記載されていない**（2, 3, 7 が出現する根拠が不明）。
- **タイトルが長く、「neutralisation」が未定義**。Biostatistics 読者にとっても方法名が分かりにくい。
- **拡張感度分析（n, Z-to-Y, Z→X, 非線形）は 10 反復**。Monte Carlo 誤差が大きく、細かい数値比較に注意が必要。

---

## 2. Biostatistics 投稿規定との適合度

公式 Author Guidelines（Oxford Academic）および pandoc-journal-templates からの主なポイント：

| 要件 | 現状 | 適合度 | 対応の急務 |
|---|---|---|---|
| スコープ：health/disease における革新的な統計的方法 | 観察研究・IPD 合成の診断法 | ◎ | — |
| 再現性（D/C/R バッジ） | GitHub は公開。ただし Zenodo/Figshare アーカイブ・環境固定がない | △ | **高**：コードアーカイブ DOI、requirements/環境ファイル、README で再現手順を明記 |
| 初回投稿は PDF、ダブルスペース | docx は単倍行間 | △ | **高**：ダブルスペース PDF を作成 |
| 25 原稿ページ制限（oupdraft テンプレート、表・図除く） | 約 7,281 語 → 25 ページ超 | △ | **高**：Additional files、詳細 DGM、感度表の多くを Supplementary Materials へ |
| 著者年式参照（natbib + biorefs.bst） | 本文は author-date、Reference list は Vancouver 風（番号なし）でやや不一致 | △ | 中：biorefs 形式または一貫した author-year に整える |
| タイトルページ：title, authors, address, email, ORCID, abstract, keywords, history | `title_page_rsm_v3.docx` は極めて簡素 | △ | 中：Biostatistics 用タイトルページを作成 |
| 図表は原稿末尾 | 本文内にインライン挿入 | △ | 中：PDF では図表を末尾に配置 |
| Supplementary Materials の記述 | 本文に Additional files セクションで詳述 | △ | 高：本文には短い「Supplementary Materials」段落のみ残す |
| Data/Code availability statement | 本文 Declarations に簡単な記述 | △ | 高：Biostatistics の要求に沿った明確な記述を追加 |

### 重要ポイント
- **Biostatistics は format-free 投稿を謳っている**（「Don’t format your first draft for Biostatistics」）。ただし **ダブルスペース PDF**、および **25 ページ制限** は初期審査にも影響しうる。
- **D/C/R バッジ**は同誌の特色。Associate Editor for Reproducibility が実際にコードを回せて、結果が再現できてはじめて “R” バッジ。単なる GitHub リンクでは不十分。

---

## 3. 査読者が突きそうな科学的・方法論的指摘

### 3.1 新規性とスコープ
- **Biostatistics 読者は「新しい統計的方法」を期待する**。現在の IONE は、既存の層別化・クラスタリング・予後スコア手法を組み合わせた探索的診断フレームワーク。新規性は「C1（層間 heterogeneity）＋ W（層内 CATE 均質性）を組み合わせ、IPD 観察データで marginal ATE の脆弱性を診断する」ことに帰結される。これを冒頭で 1 文で説明する。
- **「neutralisation」という造語**を使わず、*`coherence diagnostic` または `stratification-based diagnostic for hidden effect modification`* という方が Biostatistics 読者に伝わる。
- **タイトルから “Incoherence-Oriented Neutralisation and Extraction” を外すか、サブタイトルで定義**する。

### 3.2 統計設計の正当性
- **C1 = 1 − I² は stratum-specific log odds ratio で定義**されているが、ATE バイアスは risk-difference スケール。このスケール混在をもっと自覚的に議論。C1 は診断指標であり、直接の RD バイアス推定量ではないことを明記。
- **DerSimonian-Laird (DL) ランダム効果モデルを「発見された層」に適用**しているが、層は同じデータから生成されたため独立ではない。DL 使用の正当化と限界を Methods と Discussion で議論。
- **Outcome-informed 手法の 50/50 分割**：n=2000 であれば評価半分は 1000 人、K=5 層で各層 200 人。2 値アウトカムではセル数が少なく、RD の標誤差が大きい。n=500 ではさらに不安定。サンプルサイズ感度で信頼性の限界を強調。
- **W_est は Y ~ X + A + X*A のロジスティックモデルに依存**。モデル特定誤りがあれば診断が誤る。頑健性を確認する追加感度分析（高次項や交互作用の追加）があると強い。

### 3.3 シミュレーション結果の解釈
- **最良非オラクル ARI = 0.032**。真の構造はほとんど回復できていない。バイアス低減は「真の hidden subgroup を復元」ではなく「関連する測定変数で層別化したことによる相関」の可能性が高い。著者は慎重だが、*detection* と *extraction* の 2 段階フレームを Abstract でも宣言。
- **拡張感度分析は 10 反復**。数値的差異（method A vs B）が Monte Carlo 誤差の範囲内かもしれない。Table 4–7 に Monte Carlo SE を追加するか、信頼区間を示す。
- **実データ例の K 選択（Table 3: 2, 3, 7）**が Methods で説明されていない。シミュレーションでは K=3,5,10 だったが、実データでは何に基づいて K を選んだのか？ これは「K を探索的に試し、ARI 最大を選んだ」など明記。

### 3.4 実データ例
- 5 つの Simpson's paradox 例は「半合成例」であり real IPD ではない。これは原稿で正直に述べているが、**Table 3 の bias reduction は 0.011–0.114 と小さく、臨床的意義が不明**。これを「方法の可能性を示すイラストレーション」とし、過大解釈を避ける。
- 実例に「真の効果」がないため、バイアス低減の計算基準がシミュレーションと異なる？ Table 3 の `Bias reduction` がどう計算されたかを Methods に追加。

---

## 4. 原稿表現・体裁の問題

### 4.1 ページ数・構成
現状の `IONE_rsm_v3.md` セクション別語数（概算）：

| セクション | 語数 |
|---|---|
| Abstract | 275 |
| 1. Introduction | 1,098 |
| 2. Methods | 1,734 |
| 3. Results | 3,045 |
| 4. Discussion | 960 |
| 5. Conclusions | 94 |
| List of abbreviations | 76 |
| Declarations | 131 |
| Additional files | 493 |
| **合計** | **約 7,900 語** |

Biostatistics の Overleaf テンプレートは「Title, authors, affiliations, summary, keywords, the body, acknowledgements, a short section describing the Supplementary Materials, and the references (excluding tables and figures) should not exceed 25 manuscript pages in draft mode」。約 7,900 語はおおむね **30 原稿ページ**に相当し、表・図を除いても制限超過の可能性が高い。

**削減案**
- `Additional files`（493 語）→ Supplementary Materials へ全文移動。
- `List of abbreviations`（76 語）→ Supplementary または短縮表に。
- 感度分析 Table 2, 4, 5, 6 は本文から削除し、概要文＋ Supplementary へ。本文には Table 1（primary）と Table 7（non-linearity）、Table 3（real data）のみ残す。
- Introduction から観察研究一般論（1,098 語）を 700–800 語に短縮。

目標：**本文（+ 参照 + 短い Supplementary Materials 説明）を 5,500–6,000 語に圧縮**。

### 4.2 タイトル
現タイトル：
> IONE: Incoherence-Oriented Neutralisation and Extraction for hidden effect modification in individual participant data meta-analysis: a simulation study of stratification-based extraction

短縮案：
> A coherence diagnostic for hidden effect modification in pooled observational data: a simulation study of stratification-based extraction

または
> Detecting hidden effect modification in individual participant data meta-analyses: a stratification-based diagnostic

IONE は本文内で定義すれば十分。

### 4.3 参照文献
- Biostatistics の LaTeX テンプレートは `natbib` + `biorefs.bst`（著者年式）。
- 現在の docx は本文 `(Author Year)`、Reference list は著者順の Vancouver 風。これは draft submission では許容されるかもしれないが、**最終的には `biorefs` 形式**（`Author (Year). Title. Journal.`）に合わせる。
- 初期投稿では、**本文と Reference list が一貫している author-year 形式**で十分。番号付き Vancouver に変える必要はない。

### 4.4 タイトルページ
Biostatistics 用に以下を含むタイトルページを作成：
- Title
- Authors with `*` for corresponding author
- Address / affiliation
- E-mail
- ORCID（任意だが推奨）
- Abstract / Summary
- Keywords
- Acknowledgements（該当すれば）
- Short section describing Supplementary Materials
- 必要に応じて `\history{Received ...}`

### 4.5 図表
- **Figure 1** は C1（0.8–1.0 台）とバイアス低減（0.0–0.6 台）を同じパネルに描いており、スケールが異なる。**2 パネル化**または正規化を検討。
- 図表は PDF では**原稿末尾**に配置（LaTeX デフォルト）。
- Figure alt-text / 高解像度 PNG/EPS は既に用意済み（良好）。

### 4.6 AI / 倫理宣言
- Biostatistics は一般的な出版倫理（捏造・抄袭・AI 利用の透明性）を重視。現在の AI 宣言は簡素。**使用した LLM・バージョン・目的・人間レビュー体制**を明記。
- 倫理審査・同意はシミュレーションなので「Not applicable」。

---

## 5. 優先度付きアクションリスト

### 5.1 投稿前に必須（デスクリジェクト・大修正を回避）
1. **ダブルスペース PDF を作成**（本文 + 参照 + 短い Supplementary 説明）。
2. **25 ページ制限を満たす本文圧縮**：
   - `Additional files` と `List of abbreviations` を Supplementary Materials へ。
   - 感度分析 Table 2, 4, 5, 6 を本文から削除し、Supplementary へ移動（概要文のみ残す）。
3. **Supplementary Materials の短い説明セクション**を追加し、本文の `Additional files` セクションを削除。
4. **再現性を強化**：
   - `requirements.txt` または `environment.yml` で Python バージョン・パッケージを固定。
   - 実行手順（`git clone` → `generate_summary.py` → `generate_ione_rsm_v3.py`）を README に明記。
   - Zenodo または Figshare にコードをアーカイブし DOI を取得（Biostatistics の D/C/R バッジ）。
5. **AI 利用宣言を拡充**（ツール名・バージョン・利用日・目的・人間レビュー）。

### 5.2 高優先（査読をスムーズにする）
6. **タイトルとアブストラクトを Biostatistics 向けに再構成**：
   - タイトルから “neutralisation” を外すか定義。
   - アブストラクトを 200–250 語に短縮し、health/disease 動機を 1 文目に。
7. **C1/W と DL 層別化の限界を Methods / Discussion で一段明確化**。
8. **拡張感度分析に Monte Carlo SE または信頼区間を追加**（10 反復の解釈制約を明記）。
9. **Table 3（実データ例）の K 選択方法を Methods に明記**。
10. **Figure 1 を 2 パネル化または正規化**。
11. **Biostatistics 用タイトルページを作成**。

### 5.3 中優先（ジャーナル適合度向上）
12. **Introduction を再構成**：health/disease における観察研究の問題から入り、IPD 合成の文脈を短く挟む。
13. **タイトル/アブストラクトで detection vs extraction の 2 段階アプローチを明確化**。
14. **カバーレターを Biostatistics 向けに書き換え**：革新性、生物医学的動機、再現性を強調。
15. **Reference list を `biorefs` 著者年式に整える**（最終投稿時）。

### 5.4 任意（さらに強い論文にする）
16. **n=500 の結果を補足資料へ移動**、または追加シミュレーションで信頼性を高める。
17. **DL ではなくベイズ階層モデルとの比較を追加**。
18. **実際の IPD データを 1 例追加**（可能であれば）。
19. **W_est のモデル特定頑健性を追加感度分析**。

---

## 6. ジャーナル適合度を上げる具体的提案

Biostatistics は **health/disease における革新的な方法** を求める。以下で適合度を最大化できる。

### 6.1 タイトル・アブストラクトの再構成
- タイトル例：
  > *A coherence diagnostic for hidden effect modification in pooled observational data: a simulation study of stratification-based extraction*
- アブストラクトの 1 文目：
  > "In observational studies and individual participant data meta-analyses, marginal treatment-effect estimates can be biased when hidden effect modifiers are not accounted for."
- 最終文：
  > "The proposed diagnostics help flag populations that require subgroup-specific or sensitivity analysis before trusting a marginal summary."

### 6.2 Introduction の再構成
- **第 1 段落**：health/disease 観察研究での効果修飾・交給の問題。具体例（年齢、疾患重症度、併存症）を挙げる。
- **第 2 段落**：IPD 合成でも marginal summary が脆弱になりうることを短く述べる。
- **第 3 段落**：既存手法（PS、予後スコア、GMM、LCA）の限界—測定共変量のみ調整し、隠れた集団構造を診断しない。
- **第 4 段落**：IONE の提案：C1/W で異質性を診断し、必要に応じて層別化。detection と extraction を分ける。

### 6.3 Supplementary Materials への移動
Biostatistics は詳細なシミュレーション記述を Supplementary に入れることを条件にすることが多い。移動すべき：
- 詳細な DGM（Additional file 1）
- ADEMP / STROBE-Sim チェックリスト
- Table 2, 4, 5, 6（K 感度、サンプルサイズ、Z→Y、Z→X）
- 追加の図（必要なら）

本文には残す：
- Table 1（primary）
- Table 3（real data）
- Table 7（non-linearity）
- Figure 1–5

### 6.4 再現性バッジ
- `README.md` に再現手順を書き、requirements.txt / environment.yml を置く。
- GitHub リリースを作成し、Zenodo 連携で DOI を取得。
- 原稿内 Data/Code Availability statement で DOI を引用。

### 6.5 カバーレター
- Biostatistics 編集長への手紙で以下を強調：
  - 新規性：C1/W 診断と層別化 extraction の組み合わせ。
  - 生物医学的動機：Simpson's paradox の健康データ例。
  - 再現性：GitHub + Zenodo DOI。
  - 投稿前に既に実行した ADEMP/STROBE-Sim 遵守。

---

## 7. 総合判断

- **Biostatistics は現在の原稿にとって自然な投稿先**。RSM よりスコープフィットは高い。
- しかし、RSM 向けに残った構成（Declarations、Additional files、長めの本文）と再現性アーカイブの不足は、初期審査や reproducibility review で不利。
- **最低限の対応**：本文を 25 ページ以内に圧縮、Supplementary Materials を整理、ダブルスペース PDF を作成、コードを Zenodo/Figshare にアーカイブ、AI 宣言を拡充。
- これらを完了すれば、Biostatistics への採択可能性は高い。

---

## 付録：簡易メトリクス

| 項目 | 値 |
|---|---|
| 本文総語数（docx） | 約 7,281 語 |
| Abstract 語数 | 275 語 |
| 図 | 5 |
| 表 | 7 |
| 参考文献 | 38 |
| リポジトリ | https://github.com/bougtoir/ione-stratification-framework |
| Zenodo/Figshare DOI | 未取得 |
