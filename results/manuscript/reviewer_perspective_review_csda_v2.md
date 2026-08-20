# CSDA査読者目線レビュー v2：ジャーナル適合度向上提案

**Target journal:** *Computational Statistics & Data Analysis* (Elsevier)  
**対象パッケージ:** `results/manuscript/csda_submission/v1_ione_csda_submission_package.zip`  
**Git branch:** `devin/ione-csda-v2` (PR #8)  
**レビュー日:** 2026-08-20

---

## エグゼクティブサマリー

v1パッケージは機械的整備（引用番号、図表インライン配置、OMML数式、ハードコードなし、再現性）が整っている。しかし、CSDAの「**計算/データ解析**」読者に対しては、（1）計算手法・実装の提示が弱い、（2）貢献が「否定的な診断結果」に偏重しすぎている、（3）シミュレーションが「どの手法をいつ使うべきか」を定量化した推奨表にまとまっていない、という3点が査読者からの指摘リスクとして残っている。

本レビューでは、**本文の再構成と小さな追加でジャーナル適合度を上げる**ための優先度付き提案を示す。機械的修正はv1レビュー済みなので、ここでは**戦略的な構成・フレーミング**に焦点を当てる。

---

## 1. CSDAガイドラインとの照合

CSDAの *Guide for Authors*（2026年8月時点）から本稿に直接関係する要点：

> "The focus of the papers submitted to CSDA must include either a computational or a data analysis component. Papers, which are purely theoretical are not appropriate for CSDA, and will be returned to the authors."

> "Manuscripts describing simulation studies must a) be thorough with regard to the choice of parameter settings, b) not over-generalize the conclusions, c) carefully describe the limitations of the simulations studies, and d) **should guide the user regarding when the recommended methods are appropriate**. In addition, it is recommended that the author(s) indicate **why comparisons cannot be made theoretically and why therefore simulations are necessary**."

> "Papers reporting results based on computations should provide enough information so that readers can evaluate the quality of the results, as well as descriptions of **pseudo-random-number generators, numerical algorithms, computer(s), programming language(s), and major software components** that were used."

v1の対応状況：

| ガイドライン項目 | v1対応 | 残リスク |
|---|---|---|
| 計算/データ解析要素 | ◎ シミュレーション＋疑似実データ例 | 計算実装の詳細記載が不足 |
| パラメータ設定の徹底 | ◎ K, n, Z-to-X, Z-to-Y, 非線形mappingを変動 | 推奨方法の使い分け表がない |
| 結論の過度な一般化 | ◎ 否定的・限定された主張 | 「貢献」が弱く見える可能性 |
| 限界の説明 | ◎ Discussionに複数記載 | ARIの「真の分割」基準が曖昧 |
| いつ使うべきかの指針 | △ 断片的に言及 | 具体的推奨表を追加すべき |
| 数値結果の評価情報 | △ 生成式・言語のみ | RNG、アルゴリズム、ソフトウェア詳細なし |
| シミュレーションが必要な理由 | △ 理論比較の困難性が暗黙的 | 明示的な1文がない |

---

## 2. 査読者が投げそうな本質的質問

### Q1. 計算/統計的な新規性は何か？
- 現状：C1はI²の再解釈、WはCATE分散比、手法は既存（residual stratification, PS, prognostic score, GMM, k-means, PCA）の組み合わせ。
- リスク：「新規診断統計量×ベンチマーク」としての位置づけはあるが、**個々の部品は既知**に見える。

### Q2. 主張が否定的すぎるのでは？
- 現状：C1/WはAUC ~0.5で区別できない、ARIはOracle 0.372に対しbest 0.032と極めて低い。
- リスク：「では読者は何を使えばよいのか？」が曖昧。CSDAは否定的結果も受け入れるが、**「どう使うべきかの指針」**が必要。

### Q3. いつこの手法を信頼できるか？
- 現状：「Z-to-Y効果が強いとき」「サンプルサイズが大きいとき」など条件別の性能は報告されているが、1枚の推奨表にまとまっていない。
- リスク：CSDAガイドライン(d)の "guide the user regarding when the recommended methods are appropriate" に直接的に応えていない。

### Q4. ARIの「真のZ分割」って何？
- 現状：「constructed true-Z reference partition is a k-means clustering of standardised Z-space with K strata」。
- リスク：これは真のラベルではなくk-means近似なので、ARIが低く出るのは当たり前では？と指摘される。基準の非唯一性を説明する必要がある。

### Q5. 理論的に比較できない理由は？
- 現状：Simulation onlyの正当化が本文にない。
- リスク：CSDAは "why comparisons cannot be made theoretically and why therefore simulations are necessary" を推奨している。

---

## 3. 優先度別 改善提案

### HIGH — 投稿前にすべき変更

#### 3.1 Abstractに「計算貢献」と「否定的所見の意義」を入れる（v2案）

**提案本文（191 words → 約210 words、CSDAのconcise範囲内）：**

> **Background:** In individual participant data (IPD) meta-analysis, marginal effect estimates can be biased by hidden effect modifiers. We introduce two coherence diagnostics, C1 and W, and present a reproducible simulation benchmark of stratification approaches.
>
> **Methods:** We simulated an IPD meta-analysis with 10 studies (n=2000), binary treatment and outcome, measured covariates carrying traces of an unmeasured modifier, and study-level variation in baseline risk and treatment prevalence. Seven stratification methods were compared: two proposed outcome-informed approaches, two outcome-free approaches, propensity-score stratification, prognostic-score stratification, and a Gaussian mixture model. Stratum-specific risk differences were synthesised with fixed-effect and DerSimonian-Laird random-effects meta-analysis. C1 and W were calibrated against an empirical null distribution (200 replications).
>
> **Results:** At n=2000 and K=5, C1 and W_est did not reliably distinguish the alternative DGM from the empirical null (C1 AUC 0.460–0.545; W AUC 0.427–0.561). The residual-based method achieved the largest random-effects ATE bias reduction (0.01865 → 0.00816; relative reduction 0.563), with a structural bias floor of ~0.008 across n=500, 2000 and 10 000.
>
> **Conclusions:** IONE is a descriptive sensitivity framework, not an inferential test. The benchmark shows that data-driven stratification can reduce marginal bias only when covariate traces of hidden effect modification are strong, and that diagnostic thresholds must be method- and DGM-specific.

**変更のポイント：**
- "reproducible simulation benchmark" を明記。
- "seven stratification methods" で手法数を明示。
- "structural bias floor" を導入し、否定的なn=10,000結果を「構造的限界」として再解釈。
- Conclusionsに "only when covariate traces... are strong" でいつ使うかの指針を入れる。

---

#### 3.2 Methodsに「Computational implementation」小節を追加

**CSDAガイドラインに直接応える。** 追加位置：Methodsの最後（"Reporting and reproducibility"の前）。

```markdown
### Computational implementation

All simulations were implemented in Python 3.11 using NumPy 2.x, SciPy, scikit-learn 1.5, pandas, statsmodels andpython-docx. Pseudo-random numbers were generated with `numpy.random.default_rng` seeded per scenario (seeds are recorded in each simulation script and in `results/summary/` metadata). Stratification used k-means (`scikit-learn`, default initialization with 10 random starts), Gaussian mixture models (`scikit-learn` with full covariance and 10 EM initializations), and quantile-based equal-frequency binning. Logistic regressions were fit with `scikit-learn.linear_model.LogisticRegression` (L2 penalty, C=1.0, solver=lbfgs, max_iter=1000), and the DerSimonian-Laird estimator used `statsmodels.stats.meta_analysis`. The semi-synthetic pseudo-IPD reconstructions are deterministic functions of the published aggregate counts. Wall-clock runtime for the full primary scenario (50 replications, 10 studies, n=2000, K=5, 7 methods) was approximately X seconds on an Intel Xeon / AMD EPYC instance; runtime for the empirical null (200 replications) was Y seconds. All code, dependency pins, random seeds and the commit hash are available in the public repository.
```

**必要な情報：** X, Y は `generate_summary.py` やシミュレーションスクリプト実行時の `time` 出力を確認して埋める。なければ「approximately 2–3 hours for the full benchmark on a single core」程度の概算でも有用。

---

#### 3.3 シミュレーション必要理由をIntroductionに1文追加

CSDAは理論比較不可能性の説明を推奨。Introductionの最後あたりに：

> "Because the finite-sample distributions of discovered-stratum risk differences depend on the unknown joint distribution of unmeasured modifiers and measured covariates, closed-form comparisons of the stratification methods are not available; the ADEMP-based simulation benchmark is therefore required to quantify their relative performance and the operating characteristics of C1 and W."

これを入れるだけで査読者の「なぜシミュレーションだけか？」という疑問を大きく減らせる。

---

#### 3.4 Resultsに「推奨表（When to use which method）」を追加

CSDAの(d)項に最も直接的に対応。Table 5として新設するか、Discussion冒頭に配置。

**提案表（本文はMarkdown、docxは`generate_rsm_tables.py`または手動）：**

```markdown
| Scenario characteristic | Recommended method(s) | Rationale | Caveat |
|---|---|---|---|
| Strong Z-to-X trace (zx ≥ 1.0) and moderate-to-large n | Prognostic score / clustering / residual | ARI and relative bias reduction improve with trace strength | Still below Oracle; ARI modest |
| Small sample (n ≈ 500) | Residual method (1B) | Achieves largest relative bias reduction (0.815) and lowest absolute bias floor | Relative reduction inflated by large crude bias; absolute bias ~0.008 |
| Large sample (n = 10 000) with strong confounding | Propensity score / prognostic score / clustering | Largest relative reductions (0.533–0.669) once finite-sample error is removed | Residual method hits structural floor ~0.008 |
| Rare outcome / sparse cells | Outcome-free methods (PCA/k-means) or prognostic score | Avoids degenerate logistic fits in near-zero event cells | ATE bias reduction may be small |
| Need a descriptive flag for incoherence | Report C1_excess and W_est_excess alongside method-specific null thresholds | Empirically calibrated under no effect modification | Do not use as a standalone test; AUC ≈ 0.5 in primary scenario |
```

**効果：**「では実務家はどう使うのか？」に答える。Discussionの「Recommendation」に発展させやすい。

---

#### 3.5 ARI「真の分割」基準をより慎重に定義

Methodsの"Evaluation metrics"段落を以下のように補強：

> "The true-Z partition is a k-means clustering of standardised Z-space with K strata. It is therefore an operational upper bound on the agreement achievable by any K-stratum covariate-based method, not a clinically meaningful or unique true partition. Oracle methods use this same k-means partition directly; their ARI is necessarily high, but even their random-effects ATE bias is not zero because k-means on Z only approximates the true CATE surface."

これにより「ARI 0.032 vs Oracle 0.372」の大きな差が過大評価されにくくなる。

---

### MEDIUM — 採用すると査読印象が良くなる

#### 3.6 C1とWの数式をMethodsまたはIntroductionに明示

CSDA読者は数式を読む。現在、定義は文面に埋もれている。以下を本文or Methodsの最初に入れる：

> For a given stratification with K strata, let \(\hat{\theta}_k\) be the stratum-specific log odds ratio and \(\hat{\tau}^2\) the DerSimonian-Laird between-stratum variance. We define
> \[
> C_1 = 1 - I^2 = 1 - \frac{\hat{\tau}^2}{\hat{\tau}^2 + \bar{v}},
> \]
> where \(\bar{v}\) is the typical within-stratum sampling variance. Let \(\hat{\tau}(X_i)\) denote the estimated conditional average treatment effect for individual i. We define
> \[
> W = \frac{\sum_k n_k \left(\bar{\hat{\tau}}_k - \bar{\hat{\tau}}\right)^2}{\sum_i \left(\hat{\tau}(X_i) - \bar{\hat{\tau}}\right)^2},
> \]
> where \(\bar{\hat{\tau}}_k\) is the stratum mean of \(\hat{\tau}(X_i)\). Both indices are descriptive: low C1 (high between-stratum heterogeneity of log odds ratios) or high W (large explained CATE variance) flag potential incoherence.

（`md_to_rsm_docx`対応するLaTeX表記に合わせて調整。）

---

#### 3.7 図表のキャプションに「推奨文脈」を追加

- **Figure 4 (sample size)** キャプションに： "The residual method reaches a structural bias floor near 0.008; propensity/prognostic/clustering approaches overtake it at n=10 000."
- **Figure 6 (diagnostic calibration)** キャプションに： "C1 and W_est do not provide reliable classification on their own in the primary scenario; use them only as descriptive flags calibrated to the empirical null."

これだけで図の「読み方」が査読者に伝わる。

---

#### 3.8 ReferencesにDOIを追加

v1レビューでも言及。以下の主要文献はDOIが容易に見つかるはず（CrossRef等）：
- Borenstein et al. (2009)
- Riley et al. (2010)
- Simmonds et al. (2005)
- DerSimonian & Laird (1986)
- Higgins & Thompson (2002)
- Pearl (2009)
- Greenland et al. (1999)
- Simpson (1951)
- Morris et al. (2019)
- Hubert & Arabie (1985)
- Rosenbaum & Rubin (1983)
- McLachlan & Peel (2000)
- Hansen (2008)

**対応：** `generate_ione_rsm_v3.py` 内の `cm.register` 辞書に `doi=` フィールドを追加し、`md_to_rsm_docx`または`CiteManager`で reference list の末尾にDOIを付与する。難しければ手動で `references.docx` を上書きする方向でも可。

---

#### 3.9 Cover letterにCSDAの推奨フレーズを追加

現在のカバーレターは良いが、以下の一文を追加するとCSDA編集者に訴求：

> "Because the sampling distributions of the discovered-stratum estimators depend on the unknown joint distribution of unmeasured modifiers and observed covariates, closed-form theoretical comparisons of the stratification methods are not available; the simulation benchmark is therefore necessary to quantify relative performance. We believe this aligns with the journal's scope of computationally grounded methodological development."

---

### OPTIONAL — 改善点として挙げておく

#### 3.10 Semi-synthetic illustrationsの扱い

Israel vaccinationの擬似IPDは面白いが、CSDAの査読者は疑似データの生成過程をもっと厳密に確認したい。Supplementary Methodsに以下を追加：

- 各データセットの元公開表（年齢×ワクチン接種×入院数など）から擬似レコードを生成した決定的関数。
- 下位層セルが0イベントの場合の対処。

ただしv1でも「pseudo-IPD」と断っているため、必須ではない。

#### 3.11 図の配色/

ElsevierのGuideでは "color should be used for any figures in print"を宣言する必要がある。Figure 1-7は既にカラーPNG。カバーレターまたはsubmission notesに "Figures are intended for color online and in print" と明記する。

---

## 4. 改訂後の想定構成（推奨）

```
Abstract
Keywords
1. Introduction
2. Methods
   2.1 Aims
   2.2 IPD data-generating mechanism
   2.3 Stratification methods
   2.4 Synthesis of stratum-specific effects
   2.5 Study-level meta-analysis benchmark
   2.6 Evaluation metrics  ← C1/Wの数式を明示
   2.7 Empirical null distribution
   2.8 W_est misspecification sensitivity
   2.9 Diagnostic calibration
   2.10 True-CATE-quantile oracle
   2.11 Semi-synthetic illustrations
   2.12 Computational implementation  ← 新規
   2.13 Reporting and reproducibility
3. Results
   3.1 Primary IPD scenario
   3.2 Sensitivity to K
   3.3 Semi-synthetic illustrations
   3.4 Sensitivity to sample size
   3.5 Z-to-X / Z-to-Y sensitivity
   3.6 Non-linear mapping
   3.7 Diagnostic discrimination
   3.8 CATE variance explained
   3.9 Recommendations for method choice  ← 新規（Table 5）
4. Discussion
   4.1 Principal findings
   4.2 Detection vs. subgroup recovery
   4.3 Comparison with study-level and covariate-adjustment approaches
   4.4 W denominator and misspecification
   4.5 Large-sample behaviour
   4.6 Relevance to CSDA readers
   4.7 Strengths and limitations
5. Conclusions
Declarations
References
```

---

## 5. リスク評価（査読者目線）

| 項目 | リスクレベル | 理由 |
|---|---|---|
| スコープ外（計算要素不足） | 中 | Computational implementation 小節があれば回避 |
| ニューオネス不足 | 中 | C1/Wの明示的定義とベンチマーク資源の位置づけで緩和 |
| 否定的結果の受け入れ | 低〜中 | CSDAは否定的シミュレーションを容認するが、「いつ使うか」の指針が必要 |
| ARI基準の妥当性 | 中 | 真の分割がk-means近似であることを明示すれば回避 |
| シミュレーションの正当化 | 中 | 理論比較不可能性の1文追加で回避 |
| DOI/参考文献形式 | 低 | 追加推奨、必須ではない |

---

## 6. 優先度まとめ

| 優先度 | 提案 | 影響 |
|---|---|---|
| **HIGH** | Abstractの改訂（計算貢献・構造的限界を強調） | 編集者/査読者の第一印象を変える |
| **HIGH** | Methodsに Computational implementation 小節を追加 | CSDAガイドライン直接対応 |
| **HIGH** | Introductionに理論比較不可能性の1文を追加 | 「なぜシミュレーションか」の正当化 |
| **HIGH** | Resultsに method-choice 推奨表（Table 5）を追加 | CSDAの(d)項に直接応える |
| **HIGH** | ARI true-Z分割をk-means近似として再定義 | 真の分割妥当性への批判を防ぐ |
| **MEDIUM** | C1/Wの数式をMethodsに明示 | 計算統計読者への可読性向上 |
| **MEDIUM** | 図キャプションに推奨文脈を追加 | 読者の誤解を減らす |
| **MEDIUM** | ReferencesにDOIを追加 | 編集・査読の印象向上 |
| **MEDIUM** | Cover letterにCSDAフレーズを追加 | デスク判断を助ける |
| **OPTIONAL** | Semi-synthetic生成過程の詳細補強 | 再現性への信頼向上 |

---

## 7. 最終所見

v1パッケージは提出可能な水準にあるが、CSDAの**計算/データ解析**読者に対しては「何が計算貢献か」「いつ何を使うか」をもう一段階明確にする必要がある。上記HIGH項目を実施すれば、査読者に対して「本稿は模擬実験の批判的有用性を定量化したベンチマーク研究である」と納得させる構成になる。実施内容を反映したv2原稿を生成後、改めて本文を再チェックすれば提出価値は大きく向上する。
