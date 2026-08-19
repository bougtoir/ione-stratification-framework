# IONE v3 査読者目線レビュー & ジャーナル適合度向上案（v7）

対象原稿：`results/manuscript/biostatistics_submission/IONE_biostatistics_v3.md` / `.docx`  
対象パッケージ：`v3_ione_biostatistics_submission_package.zip`  
ブランチ：`devin/ione-biostatistics-v4`（commit `1b3243c`）  
レビュー日：2026-08-18  

---

## 1. エグゼクティブサマリー

現状の `IONE_biostatistics_v3` は体裁・引用・図表対応・再現性パイプラインの面で高い完成度を持つが、**核心にある診断指標 C1 と W の識別性能が非常に弱い**ことが、査読者目線で最大のリスクである。シミュレーション raw データから計算した受信者操作特性（ROC/AUC）では、C1 も W_est もほぼ偶然レベル（AUC ≈ 0.5、5% FPR 閾値での真陽性率 0–17%）であり、「incohérence を flag する診断ツール」という主張は現状の数値では裏付けられていない。

これは投稿先を問わず fatal ないし major revision に直結する問題である。現稿を *Biostatistics*（Oxford）にそのまま送るのはリスクが高い。ジャーナル適合度を上げる最短ルートは、

1. 診断性能を AUC/ROC/TPR で正直に定量化し、
2. W の分母問題を修正・正規化し、
3. 「真の潜在集団の回収」という表現を削ぎ、探索的感度診断として再位置づける

ことである。これらを実施したうえで、**第一目標を *Statistical Methods in Medical Research*（SMMR）、第二を *Statistics in Medicine*、Biostatistics は理論的裏付け追加後に再検討**するのが現実的である。

---

## 2. 前提と対象原稿

確認対象：

- `results/manuscript/biostatistics_submission/IONE_biostatistics_v3.md`（本文）
- `results/manuscript/biostatistics_submission/biostatistics_supplementary_v3.md`（補足）
- `results/manuscript/biostatistics_submission/cover_letter_biostatistics_v3.md`（カバーレター）
- `results/manuscript/reviewer_perspective_critique_biostatistics_v6.md`（前回レビュー）
- `results/manuscript/journal_comparison.md`
- `results/manuscript/next_journal_proposal.md`
- `results/manuscript/journal_shortlist_apc_if.md`
- `results/rsm_ipd_results.csv`, `results/rsm_ipd_null_results.csv`, `results/rsm_ipd_sensitivity_results.csv`（診断性能の検証用 raw データ）

前回 v6 レビューで指摘された Morris 2021 ブログソースの Haas 2021 *Lancet* への差し替え、Israel 例の希少性/0 イベントの言及、ページ数引用順の整備は実装済みで、これは維持すべき強みである。

---

## 3. ジャーナル適合度スコア

| 審査軸 | *Biostatistics* | *Statistical Methods in Medical Research* | *Statistics in Medicine* | *Research Synthesis Methods* | *Journal of Causal Inference* |
|---|---|---|---|---|---|
| スコープ適合 | 中。biostatistical methodology は合うが、理論的保証を期待。 | 強。医療統計・観察研究の方法論・シミュレーション比較が中核。 | 強。医学統計の方法論・シミュレーションが対象だが競争率高い。 | 中。IPD-MA の異質性診断として再位置づければ合う。 | 中。因果推論的フレーミングにすれば合うが、理論的厳密性が必要。 |
| 方法論的新規性 | 中。C1/W は I²/R² の再構成に過ぎず、形式的理論が薄い。 | 強。既存手法（PS/prognostic score/GMM）との比較が価値。 | 中。診断アイデアは興味深いが、臨床応用や実データが弱い。 | 中。シミュレーションのみなら価値は限定。 | 弱。未観測交絡の識別は主張されていない。 |
| 査読者が求める深さ | 高。一致性・漸近理論・校正の形式化。 | 中。ADEMP、Monte Carlo SE、感度分析、比較対象の正当化。 | 高。実問題への動機、校正、robustness。 | 中。SR/MA 文脈での利用可能性。 | 高。因果仮定・識別条件。 |
| 現稿の形式適合 | タイトル/カバーレターは Biostatistics 向け。25 ページ制限内（22 p）。 | Abstract 250 語制限に引っかかる（現 281 語）。Vancouver OK。 | Abstract/形式要確認。購読型は APC $0。 | フル OA、2,740 USD 程度。 | フル OA。 |
| 致命的リスク | 診断指標の性能が理論的根拠なし。 | 「抽出」主張が残れば major revision。 | 競争により「incremental」判定。 | IONE を研究統合診断として再位置づけが必要。 | 因果的解釈の整合性。 |
| 総合適合度 | △（理論追加後なら○） | ◎（再構成後最も自然） | ○（校正追加後） | △ | △ |

**推奨**：

1. **第一候補：*Statistical Methods in Medical Research*** — 現稿の「シミュレーションに基づく医療統計的手法比較」という姿勢に最も自然に合う。購読型での APC $0 も利点。
2. **第二候補：*Statistics in Medicine*** — 可視性が高いが、診断の AUC/ROC 等の裏付けを入れたうえで挑む。
3. **Biostatistics（Oxford）**：原稿を「新しい診断統計量の形式的性質＋漸近理論」に昇華できた場合のみ。

---

## 4. 査読者目線クリティカルレビュー（5 領域）

### 4.1 原稿・新規性・焦点

**強み**

- ADEMP フレームワーク、STROBE-Sim チェックリスト、Monte Carlo SE の報告は方法論ジャーナルで高く評価される。
- IPD-MA における隠れ効果修飾という動機は現実的で、Simpson パラドックスの例がわかりやすい。
- 推奨/比較する層別化手法（PS、prognostic score、GMM、PCA、clustering、residual）が比較的広く、再現性の高いベンチマークとして貢献する可能性がある。

**弱み・リスク**

- **「Extraction」の主張が結果を超えている。** 主要シナリオで最良非 Oracle ARI = 0.032、Oracle ARI = 0.372 と低い。にもかかわらず "recovery of hidden subgroup structure" を含む aim が残っている（ Methods: Aims ）。前回 BMC MRM の拒否理由の核心でもある。
- **C1 と W の新規性が薄い。** C1 = 1 − I²、W = 1 − 層内分散/全体分散は既存統計量の直接的な再構成であり、特に Biostatistics では「新しい方法論とは言い難い」と指摘される。
- **「Neutralisation」の概念が曖昧。** 操作としては「層別＋ランダム効果モデル」であり、他の SR/MA 手法と何が異なるかが抽象的すぎる。

### 4.2 統計設計

**致命的不良がある点**

- **C1/W の診断性能がほぼ偶然レベル。** 下記 §5 で定量化するが、主要シナリオ（z=1.0、n=2000、K=5、zx=1.0）では C1 の AUC が 0.46–0.55、W_est の AUC が 0.49–0.59 の範囲。「診断」として使用するのは困難。
- **W_true/W_est の分母問題。** 無効果修飾（null）の DGM では true CATE 分散が小さいため、比例 `1 − Var(CATE|層)/Var(CATE)` は不安定になり、**null 時の W_true の方が alternative 時より高くなる**ケースがある（1B residual null 0.492 vs alt 0.367 など）。「CATE 分散の説明率」としての解釈が成立していない。
- **C1 の解釈が逆になる。** "lower C1 indicates stronger between-stratum heterogeneity" と定義しているが、最良方法（1B residual）の C1 は null（0.893）より alternative（0.927）で高い。これは K=5・各層の log OR 精度が低いために I² が 0 に張り付きやすく、サンプリング誤差で C1 が 1 に近づくため。Definition と observed pattern の整合性が欠けている。
- **True-Z partition が本来の「真の構造」ではない。** DGM は連続的な Z-by-A interaction から個体レベル CATE を生成しており、K 個の真の離散集団は存在しない。そのうえ Oracle baselines の 1 つ（`oracle_quantile`）は Z1（年齢）の分位数のみを使う。ARI が低いのはむしろ当然であり、これを「回収率」と呼ぶのは誤解を招く。
- **研究単位の無視。** IPD-MA では通常、研究内効果と研究間効果を分離する。原稿はプールした IPD を一括で層別している。`results/summary/rsm_ipd_study_summary.csv` に研究単位層別の結果があるが、本文では触れられていない。SMMR/SiM/RSM の読者はこの点を指摘する。
- **DerSimonian-Laird の層間 tau²・SE。** Caveats は書かれているが、層別特定効果が同一サンプルから生じること、および層内 log OR が未調整（Z を層別するだけ）であることは、結果の不確実性を過小評価しうる。

**その他の指摘**

- 経験的 null 分布は「方法ごと・主要 DGM 条件付き」であり、実際の適用時には DGM が不明なためそのままの閾値は使えない。
- W_est misspecification（main-effects のみで W_est が膨らむ）は補足 Table S6 にあるが、本文での議論が不足。主張の強さを過小評価させる重要な点。

### 4.3 図表

- 図 1–5、表 1–3 はすべて本文で言及され、出現順にナンバリングされている（確認済み）。
- ただし **C1/W の分布や ROC 曲線が全くない。** 「診断ツール」と位置づけるなら、null と alternative の分布の重なり・閾値 performance を可視化するのが必須。
- 既存の `results/figures/eta_squared.png`（Z 変数の層間分離度）や `fig4_rsm_real_data_ari.png` 相当の情報を本文に取り入れると、ARI だけに依存しない評価ができる。
- Table 2 の Israel 例の K=2 ARI = 0.644 は、他例と比べ高いが、これは 2 値年齢層の分位数に近いことによるものであり、「完全な回収」とは言えない。本文で制限を強調する必要がある。

### 4.4 再現性

- GitHub 公開、requirements-lock、commit_hash.txt、ADEMP/STROBE-Sim チェックリスト、シミュレーション raw CSV の公開は強み。
- 前回 v6 レビューで推奨されたクリーン clone からの再生成は、現環境では `1b3243c` 時点で確認されている。投稿前にもう一度実行すべき。
- Zenodo DOI は acceptance 後に作成予定と書かれている。投稿時には GitHub URL でもよいが、acceptance 前に DOI 確保が望ましい。

### 4.5 主張の強さ

- "C1 and W diagnostics can flag incoherence"（Abstract/Discussion/Conclusions）は、現状の ROC 性能を考えると**強すぎる**。Flag するためのカットオフも達成できていない。
- "We recommend that coherence assessment using C1 and W be considered as a standard sensitivity step"（Conclusions）は、十分な裏付けがない。探索的 step とし、かつ検出力が限定的であることを明記すべき。
- "Extraction of the true hidden partition remained difficult" は弱め方として正しいが、Title/Abstract/Aims では extraction 的な記述が残っている。前後の整合性を取る必要がある。

---

## 5. 定量的裏付け：C1/W の診断性能

`results/rsm_ipd_results.csv`（alternative、50 replications）と `rsm_ipd_null_results.csv`（null、200 replications）を用い、主要条件（n=2000、K=5、z_effect_scale=1.0、zx_influence_scale=1.0、linear）で診断性能を計算した。

### 5.1 主要シナリオ（n=2000, K=5, z=1.0, zx=1.0）

| method | n_null | n_alt | C1 null mean | C1 alt mean | TPR(C1 < null 5%) | AUC(C1) | W_est null mean | W_est alt mean | TPR(W_est > null 95%) | AUC(W_est) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1A_predicted_prob | 200 | 50 | 0.903 | 0.891 | 0.060 | 0.506 | 0.094 | 0.111 | 0.080 | 0.541 |
| 1B_residual | 200 | 50 | 0.893 | 0.927 | 0.060 | 0.460 | 0.067 | 0.078 | 0.060 | 0.542 |
| 1C_cv_decision | 200 | 50 | 0.903 | 0.891 | 0.060 | 0.506 | 0.094 | 0.111 | 0.080 | 0.541 |
| 2A_PCA_cum60 | 200 | 50 | 0.876 | 0.881 | 0.060 | 0.464 | 0.084 | 0.080 | 0.060 | 0.490 |
| 2B_clustering | 200 | 50 | 0.887 | 0.865 | 0.020 | 0.545 | 0.133 | 0.143 | 0.060 | 0.537 |
| GMM | 200 | 50 | 0.879 | 0.895 | 0.060 | 0.489 | 0.081 | 0.096 | 0.080 | 0.561 |
| PS_propensity_score | 200 | 50 | 0.879 | 0.881 | 0.060 | 0.481 | 0.065 | 0.059 | 0.020 | 0.494 |
| Prognostic_score | 200 | 50 | 0.878 | 0.858 | 0.020 | 0.520 | 0.093 | 0.107 | 0.040 | 0.528 |
| baseline_oracle_kmeans | 200 | 50 | 0.893 | 0.913 | 0.000 | 0.507 | 0.031 | 0.030 | 0.040 | 0.506 |
| baseline_oracle_quantile | 200 | 50 | 0.883 | 0.897 | 0.000 | 0.507 | 0.037 | 0.042 | 0.060 | 0.537 |
| baseline_random | 200 | 50 | 0.899 | 0.883 | 0.040 | 0.544 | 0.004 | 0.004 | 0.040 | 0.427 |

**解釈**：

- 全方法で C1 の AUC は 0.46–0.55、W_est の AUC は 0.43–0.56 と**ほぼ偶然レベル**。
- 推奨される null 5% 閾値を使った場合の真陽性率（TPR）は 0–8%（期待値 5%）。つまり alternative 時でも flag がほとんど上がらない。
- これは **C1/W が現状の定義では「診断」として機能していない**ことを示す。

### 5.2 W_true の分母問題

| method | W_true null mean | W_true alt mean | 傾向 |
|---|---|---|---|
| 1B_residual | 0.492 | 0.363 | null > alt |
| 1A_predicted_prob | 0.479 | 0.352 | null > alt |
| baseline_oracle_quantile | 0.535 | 0.447 | null > alt |

無効果修飾時の true CATE 分散が小さいため、比率 `1 − Var(層内)/Var(全体)` がノイズで大きくなり、むしろ null 側の W_true の方が高くなる。したがって「W が高い → 効果修飾を捉えている」と解釈できない。

### 5.3 方法レベルでは ATE バイアスと相関がある

| metric | 方法平均レベルで bias_re との相関 |
|---|---|
| C1 | −0.53（C1 が高い方法ほどバイアス小） |
| W_true | −0.76（最も強い） |
| eta2_mean | −0.16（やや弱い） |
| W_est | −0.25（弱い） |

**解釈**：個別 replication レベルでは弱いが、方法を横断して比較すると W_true/C1 と ATE バイアス低下が一定程度相関する。これは「手法選択の参考情報」としては価値があるが、個別データセットでの「診断」とは言い難い。

---

### 5.4 数値の出所

§5 の ROC/AUC・TPR は `results/rsm_ipd_results.csv`（alternative）および `results/rsm_ipd_null_results.csv`（null）を pandas で読み込み、`sklearn.metrics.roc_auc_score` を用いて計算した。条件は n=2000、n_strata=5、z_effect_scale=1.0、zx_influence_scale=1.0、linear マッピング。同じ raw データから第三者が再計算可能である（commit `1b3243c`）。

---

## 6. ジャーナル適合度向上のための具体的提案

| 優先度 | 提案 | 対応ジャーナル | 実行可能度 | データ・コード変更 |
|---|---|---|---|---|
| **必須** | ① 診断性能を AUC/ROC/TPR・FPR として定量化し、本文に Table/Figure として追加 | 全て | 小（既存 raw データ） | 分析スクリプト＋原稿追加 |
| **必須** | ② W_true/W_est を分母の小ささに頑健な指標に修正、または null 平均に対する偏差/パーセンタイルとして報告 | 全て | 小（計算変更・変換のみ） | `evaluation.py`、原稿 |
| **必須** | ③ 「真の潜在集団の回収」という表現を削除。true-Z partition は constructed reference、DGM は連続的 CATE であることを明示 | 全て | 小 | `generate_ione_rsm_v3.py`、原稿 |
| **高** | ④ C1 の公式・解釈を整理。または、K=5 程度では I² が 0 付近に張り付く問題を解消する代替指標（例：層内 CATE モデルベースの Q）を追加 | 全て | 小～中 | `evaluation.py`、原稿 |
| **高** | ⑤ ターゲットジャーナルに応じたタイトル/Abstract/カバーレターの再調整。SMMR/SiM では抽出より「ベンチマーク」「感度分析」を強調 | SMMR/SiM | 小 | `generate_ione_rsm_v3.py`、cover letter |
| **高** | ⑥ 研究単位（study-level）の層別化や研究指標の共変量としての組み込みを追加検討し、本文で言及 | SMMR/SiM/RSM | 中 | `run_rsm_ipd_simulation.py` または Discussion |
| **高** | ⑦ W_est misspecification（main-effects のみで膨らむ）を本文に数量化して議論 | SMMR/SiM | 小 | 原稿追加 |
| **中** | ⑧ true-CATE quantile oracle を導入し、ARI に加えて「並べ替え性能」を評価 | 全て | 中 | `methods.py`、再実行 |
| **中** | ⑨ eta²（Z 変数の層間分離度）や CATE 分離度の図表を本文に追加 | 全て | 小 | 既存 figure を再利用 |
| **中** | ⑩ 大標本（n=10,000）での漸近的挙動や floor effect の議論を強化（Biostatistics 向け） | *Biostatistics* | 中 | 原稿追加 |
| **中** | ⑪ 英表現の自然化・「AI らしい」フレーズの削減 | 全て | 小 | 原稿修正 |
| **任意** | ⑫ 経験的 null の代わりに permutation/bootstrap ベースの形式的 null を提案（Biostatistics 向け） | *Biostatistics* | 大 | 新規スクリプト |

### 6.1 タイトル・Abstract 変更案

**SMMR/SiM 向け案**：

- タイトル案：*Sensitivity diagnostics for hidden effect modification in individual participant data meta-analysis: a simulation benchmark of stratification approaches*
- Abstract：
  - ` extraction of the true hidden structure` → `diagnostic ranking of stratification approaches`
  - `can flag incoherence` → `can be used as descriptive sensitivity flags for incoherence, although their discriminative performance is limited in moderate effect-modification settings`
  - 語数 SMMR の 250 語目安に短縮。

**Biostatistics 向け案**（理論追加後）：

- タイトル案：*Coherence indicators for hidden effect modification: an I²-based diagnostic with empirical calibration for IPD meta-analysis*
- Abstract/Introduction で形式化・consistency・permutation null を強調。

---

## 7. 推奨する投稿戦略

1. **現稿をそのまま投稿することは推奨しない。** 特に *Biostatistics* では診断の理論的裏付けが不足しており、desk reject ないし major revision の可能性が高い。
2. **最短でジャーナル適合度を上げるには、SMMR または SiM を狙い、上記「必須＋高」提案を実施する。** 必須の 3 点は既存データのみで対応可能で、致命的な主張の強さを修正できる。
3. もし **Biostatistics を目指すなら、さらに⑩⑫の理論的・形式的な裏付けが必要**である。これは追加実行時間がかかる。
4. 投稿先を変更する場合は、新規スレッドを開始するか、少なくともカバーレター・タイトル・Abstract を対象ジャーナル仕様に再生成する。

---

## 8. 総合判断

IONE v3 は、体裁・引用・再現性の面で出版可能レベルに近い。しかし査読者目線では、**C1 と W の診断能力が主張を裏付けていない**ことが最大の欠陥である。これを修正し、研究を「探索的感度診断・手法ベンチマーク」として再位置づけることで、*Statistical Methods in Medical Research* あたりへの適合度が大きく向上する。

次のステップとしては、必須提案 3 点を実装した新しい manuscript/package を生成し、再び査読者目線で点検することを推奨する。
