# CSDA投稿パッケージ 査読者目線レビュー v3

**Target journal:** *Computational Statistics & Data Analysis* (Elsevier)  
**対象パッケージ:** `results/manuscript/csda_submission/v1_ione_csda_submission_package.zip`  
**Git branch:** `devin/ione-csda-v2`（PR #8）  
**レビュー日:** 2026-08-21  

---

## エグゼクティブサマリー

v2レビューで指摘されたHIGH/MEDIUM項目は、おおむね現行パッケージに反映されている。

- 計算実装セクション（Methods: Computational implementation）
- Abstract/Conclusionsの構造的限界フレーミング
- Introduction最後の「理論比較不可能 ⇒ シミュレーション必要」1文
- Table 5（method-choice推奨表）
- C1/Wの形式的定義
- カバーレターでのCSDAスコープ対応

しかし、v2以降にも残る、または新たに浮かび上がった査読リスクがいくつかある。最も大きなのは、**「経験的null分布がシミュレーションDGMに依存しており、実データIPDにどう適用するかの具体的レシピが不足している」**点である。これは「いつ/どう使うのか」というCSDAガイドラインの(d)項への回答を不完全にし、major revisionに発展する可能性がある。

本レビューでは、致命的になりうる点を中心に、残りの指摘を優先度別にまとめる。

---

## 1. 優先度別 残存リスク一覧

| 優先度 | 項目 | 査読リスク | 修正効果 |
|---|---|---|---|
| **最優先（投稿前必須）** | Method 1C (`cv_decision`) の実装がメソッド名/docstringと一致しない | 手法記載の信頼性崩壊 / major revision | 実装を修正するか削除し、全結果を再生成 |
| **最優先（投稿前必須）** | 経験的null/C1_excess, W_est_excessの実データ適用手順が欠如 | Major revision / 実用性への根本的批判 | 手順を明確化すればCSDA読者の信頼獲得 |
| **高優先** | Table 5のサンプルサイズ層の整合性（n≈2000とn≈10,000で異なる） | 推奨の整合性を査読者に指摘される | サンプルサイズで行を細分化 |
| **高優先** | Abstract「7 methods」の数え方 | 手法数の齟齬による信頼低下 | 1Cの扱い確定後に修正 |
| **中優先** | 参考文献の未付DOI・Charigのissue番号誤り | 体裁 / 信頼性の印象低下 | 簡単に修正可能 |
| **中優先** | Highlightsの略号・専門用語（C1/W/ATE/ARI） | ElsevierのHighlightsガイドライン違反 | 平易な日本語/英語に置換 |
| **中優先** | タイトルの長さと略号（IONE/IPD） | 読みにくさ / 一部ジャーナルで略号制限 | 短縮案提示 |
| **任意** | その他小さな改善 | 微細な指摘 | 好印象アップ |

---

## 2. 最優先： 経験的nullの実データ適用が示されていない

### 問題

Methodsの "Empirical null distribution and null-centred reporting" では、Z-by-A交互作用を0にしたDGM で200 replicationsを回し、C1/W_estの5th/95thパーセンタイルを求めている。Table 5では「C1_excess, W_est_excessを主解析と併せて報告せよ」と推奨している。しかし、**実際のIPDデータでは「真のDGMを交互作用0にする」ことはできない**。したがって、

> 「経験的nullを計算せよ」とは言われているが、
> 実際にどうやってnull分布を得るかの手順がない。

査読者は次のように指摘する可能性が高い。

- C1_excess/W_est_excessはシミュレーション固有のnullにのみキャリブレートされており、他のDGMや実データには移設できないのでは？
- 実データで「no effect modification」を仮定するにはどうすればよいか？
- これでは推奨が再現可能な手順として不完全ではないか？

### 提案

Methodsの "Empirical null distribution" 小節、またはDiscussionのLimitationsに、**少なくとも以下の実データ近似手法のうち1つを明示的に記述する。**

> **Option A: permutation-based null.** Preserve the study-specific covariate distribution and the marginal treatment prevalence, then repeatedly permute the treatment indicator within each study. Recompute C1 and W_est for each permuted dataset to obtain the null distribution under "no effect modification conditional on covariates". For observational studies, this also removes confounding-treatment associations, so it should be interpreted as an upper-bound null rather than an exact null.
>
> **Option B: parametric residual null.** Fit a main-effects-only outcome model (Y ~ X + A + study) and sample synthetic outcomes from it while keeping covariates fixed. Recompute C1/W_est across replications. This corresponds to the no-interaction DGM used in the simulation and is therefore comparable to Supplementary Table S5, provided the main-effects model is a reasonable null for the data at hand.
>
> **Option C: bootstrap percentile.** Bootstrap the IPD with replacement, recomputing C1/W_est for each resample under an assumed weak-modification reference (e.g., the fitted values from a main-effects model). This gives an operational null for the observed sample.

さらにTable 5の "Need a descriptive flag for internal incoherence" のCaveatを強化し、例えば次のように書き換える。

> Do not use as a standalone inferential test; thresholds are method-specific, DGM-conditional, and should be re-derived for each real dataset by permutation/bootstrap under a defensible no-modification model.

### 影響

- CSDAガイドライン(d) "guide the user regarding when the recommended methods are appropriate" に直接的に応える。
- 「シミュレーションだけでなく、実データでどう使うか」という実用性を査読者に示せる。

---

## 3. 最優先： Method 1C (`cv_decision`) の実装とメソッド名が一致しない

### 問題

`methods.py` の `method_1c_cv_decision` は、関数名・docstring（"cross-validation-based decision power score"）とは異なり、実際には **Method 1Aと同じロジスティック回帰予測をそのまま使っている**（`methods.py` lines 97–103）。

```python
def method_1c_cv_decision(X, A, Y, n_strata, discovery_idx=None):
    """Method 1C: cross-validation-based decision power score."""
    ...
    p_hat_full = _safe_predict_proba(model, X[train], Y[train], X)
    return _quantile_stratify(p_hat_full, n_strata, discovery_idx)
```

この関数は `method_1a_predicted_probability` と同一の計算を行っているため、Table 1 / Supplementary Table S1–S7 で `1A_predicted_prob` と `1C_cv_decision` がすべて同一になっている。

これは、査読者が見れば容易に発見する重大な問題である。

- **「1Cは実際にCVを使っていない」** → 方法の記載と実装が食い違う（methodological inconsistency）。
- **「1Aと1Cが同一ならなぜ両方含めたのか」** → 手法数の水増しや結果の信頼性を疑われる。
- Abstractの "seven methods" も不整合になりやすい。

### 提案

**選択肢1：1Cを削除する（最も安全）**

- `methods.py` から `method_1c_cv_decision` を削除、またはコメントアウトする。
- `run_simulation.py`, `run_rsm_ipd_extended.py`, `run_rsm_ipd_null.py`, `run_w_est_misspec.py` の `method_specs` から `1C_cv_decision` を削除する。
- 全結果を再生成し、Table 1 / Supplementary Tables / Figure / PPT から `1C_cv_decision` を完全に削除する。
- Abstractを "seven methods" のまま保てる（1A, 1B, 2A, 2B, PS, Prognostic, GMM）。

**選択肢2：1Cを実装し直す（時間と検証が必要）**

- `method_1c_cv_decision` を、K-fold CVで1A（predicted probability）と1B（absolute residual）を評価し、cross-validated criterion（例：内部の stratum 間 W や validation ATE bias）でより良い方を選択する戦略に変更する。
- これは新規の手法拡張であり、再計算と再検証が必要。**投稿直前では時間がない場合は採用しない。**

**最低限、Methodsの記述を修正する（選択肢3）**

どうしても1Cを残すなら、少なくともMethodsで以下のように正直に書く。

> Method 1C is currently implemented as a cross-validated variant of Method 1A, but in the present implementation it reduces to the same predicted-probability score and therefore yields identical stratifications. We report it for completeness, but it does not contribute independent information in the benchmark.

ただし、この選択肢は「なぜ査読者に無駄な手法を提示したのか」という批判を完全には防げない。

### 影響

- Methodsと実装の整合性を回復し、論文の信頼性を守る。
- Table/Abstract/Supplementaryの整合性も同時に解決する。
- 削除を選ぶ場合、投稿パッケージを完全に再生成する必要がある。

---

## 4. 高優先： Table 5のサンプルサイズ層の整合性

### 問題

Table 5の最初の行は

> "Strong covariate trace of a hidden modifier and moderate-to-large sample | Residual-based IONE (1B) | ..."

だが、Supplementary Table S2（n=10,000）では、1B_residualのRE bias 0.00864はpropensity/prognostic/clustering（0.00618, 0.00438, 0.00580）より悪く、relative reductionも低い。つまり「moderate-to-large sample」にまでresidualを推奨すると、n=10,000の結果と矛盾する可能性がある。

### 提案

Table 5の行をサンプルサイズで分割し、n=10,000の結果を反映する。

| Scenario characteristic | Recommended method | Rationale | Caveat |
|---|---|---|---|
| Strong Z-to-X trace and **moderate sample (n ≈ 2 000)** | Residual-based IONE (1B) | Highest random-effects ATE bias reduction in the primary scenario (0.01865 → 0.00816) | Hits a structural bias floor that does not vanish with n; requires a correctly specified outcome model |
| Strong Z-to-X trace and **large sample (n ≈ 10 000)** | Propensity-score, prognostic-score or clustering stratification | Largest relative reductions (0.533–0.669) once finite-sample error is dominated by structural mismatch | Overtakes residual only when crude bias is small; performance is still DGM-dependent |
| Small sample (n ≈ 500) with moderate modification | Residual-based IONE (1B) | Largest relative bias reduction and smallest absolute bias floor | Relative reduction partly reflects large crude bias; residual model can overfit rare events |

これにより、Table 5とTable S2のn=10,000結果が整合する。

---

## 5. 中優先： 参考文献DOI・issue番号

### 問題

Reference listで以下のDOIが欠落している、またはissue番号が誤っている。

| # | Reference | 現状 | 修正案 |
|---|---|---|---|
| 6 | Riley RD, Higgins JPT, Deeks JJ. Interpretation of random effects meta-analyses. BMJ. 2011;342:d549. | DOI欠落 | `doi: 10.1136/bmj.d549` |
| 11 | Charig CR, et al. Comparison of treatment of renal calculi. BMJ. 1986;**292(6521)**:879–882. | 誤: issue `6521`；DOI欠落 | 正: `292(6524):879–882`；`doi: 10.1136/bmj.292.6524.879` |
| 12 | Bickel PJ, et al. Sex bias in graduate admissions. Science. 1975;187(4175):398–404. | DOI欠落 | `doi: 10.1126/science.187.4175.398` |
| 13 | von Kügelgen J, et al. Simpson's paradox in Covid-19 CFRs. IEEE Trans Artif Intell. 2021;2(1):18–27. | DOI欠落 | `doi: 10.1109/tai.2021.3073088` |
| 14 | Haas EJ, et al. Impact and effectiveness of mRNA BNT162b2 vaccine. Lancet. 2021;397(10287):1819–1829. | DOI欠落 | `doi: 10.1016/S0140-6736(21)00947-8` |
| 15 | Appleton DR, et al. Ignoring a covariate. Am Stat. 1996;50(4):340–341. | DOI欠落 | `doi: 10.1080/00031305.1996.10473563` |

### 修正案

`generate_ione_rsm_v3.py`またはCiteManagerの`cm.register`辞書に`doi`フィールドを追加して再生成する。Charigのissue番号も同時に修正する。

---

## 6. 中優先： Highlightsの略号・専門用語

### 問題

ElsevierのHighlightsガイドラインは

> "No jargon, acronyms, or abbreviations: aim for a general audience"
> "Each Highlight can be no more than 85 characters, including spaces"

現行のHighlightsは文字数ではギリギリ85文字以内だが、`C1`, `W`, `IPD`, `ATE`, `ARI` といった略号を含んでいる。Editorial Managerでrejectされる可能性は低いが、査読/編集段階で指摘されるリスクがある。

### 提案

以下のように平易化した案を用意しておく（文字数を確認済み）。

```
- A reproducible simulation benchmark compares seven stratification approaches.
- Outcome-residual stratification gives the best bias reduction in moderate samples.
- Strata diagnostics signal hidden effect modification but are not standalone tests.
- All code, data and results are reproducible from a public repository.
- A practical heuristic table guides method choice for sensitivity analyses.
```

これは5本（85文字以内）。`C1`/`W`はハイライトでは避け、本文で定義する。

---

## 7. 中優先： タイトルの長さと略号

### 問題

現行タイトル（28 words）:

> "Coherence diagnostics for hidden effect modification in individual participant data meta-analysis: IONE (Incoherence-Oriented Neutralisation and Extraction) and a simulation benchmark of stratification approaches"

CSDAガイドラインでは「簡潔で情報量のあるタイトル」を求めており、一般的なElsevier指針では略号を避けることが推奨されている。タイトル内に `IPD` （定義はある）と `IONE` （独自略号）が含まれる。これはdesk rejectには至らないが、タイトルの鮮明さを損ねる。

### 提案（選択肢）

**Option A（推奨）:**

> "Coherence diagnostics and a reproducible benchmark for hidden effect modification in individual participant data meta-analysis"

- `IONE` をタイトルから外し、Abstract・Keywordsに残す。
- `IPD` は展開形で十分伝わる。

**Option B:**

> "C1 and W: coherence diagnostics for hidden effect modification in IPD meta-analysis"

- 短いが、C1/Wを略号としてタイトルに入れるため、Elsevierの略号制限に抵触する可能性がある。

---

## 8. 任意： その他の小さな改善

| 項目 | 提案 |
|---|---|
| **Computational implementationのハードウェア情報** | "single modern CPU core" の具体的なCPU/メモリ/OSを補足（例：Intel Xeon / AMD EPYC, 8 GB RAM, Ubuntu 22.04）。再現性審査で役立つ。 |
| **Figure 2のキャプション** | "Data-driven methods did not reliably improve with K; choose K conservatively" という解釈をキャプションに入れる。 |
| **Abstract word count** | Title pageで226 wordsと報告されているが、Markdown換算では263 words前後。Editorial ManagerやWordのカウント方法を確認し、表記を統一する。 |
| **Semi-synthetic illustrationsのK選択** | "K was selected from {2, 3, min(K_true, 4), K_true}, keeping the value that maximised ARI" という手続きをMethodsに1文追加（現行 Supplementary Additional file 4にのみ記載されている）。 |
| **AI statement** | 現在のAI statementはDeclarations内にある。Elsevierは「References listの直前、core manuscript file内」に新しいセクションとして追加することを推奨している。原稿docx内の位置を確認する。 |
| **タイトルページの Zenodo DOI 予定** | "An archived Zenodo DOI will be obtained before acceptance"は可だが、可能であればZenodoに先行登録してDOIを付与すると強い。 |

---

## 9. リスク評価まとめ（査読者目線）

| 項目 | リスクレベル | 理由 |
|---|---|---|
| 1C (`cv_decision`) の実装とメソッド名・docstringの不整合 | **高**（major revision / 再現性信頼低下） | Methodsの説明と実装が食い違う；公開リポの検証を受ける |
| 経験的nullの実データ適用不明 | **高**（major revisionリスク） | CSDAは実用性を重視し、推奨に手順が必要 |
| 1A/1C重複と手法数の不整合 | 中〜高 | 数値の信頼性や冗長性を疑われる |
| Table 5のサンプルサイズ整合性（n≈2000 vs n≈10,000） | 中 | 推奨表の整合性に指摘されやすい |
| 参考文献DOI/issue番号 | 低〜中 | 体裁問題；修正は容易 |
| Highlights略号 | 低〜中 | Elsevier政策に抵触する可能性 |
| タイトル長/略号 | 低 | 編集段階で短縮を求められる可能性 |
| その他任意項目 | 低 | 好印象アップ |

---

## 10. 結論

現行のCSDA投稿パッケージは、v2レビュー指摘をふまえた上で大幅に改善されており、機械的・構成面ではほぼ完成度が高い。しかし、**最優先で対応すべき問題が2つある**。1. **`method_1c_cv_decision` の実装とメソッド名/docstringが一致しない**（`methods.py` lines 97–103）。これは公開リポを検証する査読者にすぐ発見され、Methods記載の信頼性を大きく損なう。削除または正しい実装に修正してから、全結果を再生成する必要がある。
2. **経験的null/C1_excess, W_est_excessを実際のIPDにどう適用するかの手順が不足している**。CSDAの実用性を重視する読者に対して、「シミュレーション固有のnull」ではなく「実データで使える手順」をMethods/Discussionに明記し、Table 5のCaveatを強化する必要がある。

これらを解決した上で、高優先・中優先項目（Table 5階層化、参考文献DOI/Charig issue、Highlightsからの略号除去、タイトル短縮など）を反映し、改めて公開リポから全結果を再生成・再確認すれば、デスクリジェクトリスクは低く、major revisionのポイントも大幅に減る。

---

## 添付・参照ファイル

- 本レビュー対象原稿: `results/manuscript/csda_submission/IONE_csda_v1.md`
- 補足資料: `results/manuscript/csda_submission/csda_supplementary_v1.md`
- 表・図セパレート版: `results/manuscript/csda_submission/csda_tables_separate.docx`
- Reference list（docx内）: `results/manuscript/csda_submission/IONE_csda_v1.docx`
- 前回レビュー: `results/manuscript/reviewer_perspective_review_csda_v2.md`
