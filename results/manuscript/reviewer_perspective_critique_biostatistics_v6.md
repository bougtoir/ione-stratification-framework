# Biostatistics（Oxford）査読者目線 プレ・サブミッション・クリティカル・レビュー v6

対象原稿：`results/manuscript/biostatistics_submission/IONE_biostatistics_v3.md` / `.docx` / `v3_ione_biostatistics_submission_package.zip`  
想定投稿先：*Biostatistics*（Oxford University Press）  
レビュー日：2026-08-10  
レビュー実施環境：`bougtoir/ione-stratification-framework`, branch `devin/ione-biostatistics-v4`, commit `9b1e031`（package commit `28599d8`）

---

## 1. 総合評価

**判断：Morris 2021 ブログソースを Haas et al. 2021（*Lancet*, peer-reviewed）の公表集計カウントに差し替えたことで、半合成例のデータ出所が学術的に適切になり、再現性も向上した。しかし、入院イベントの希少性とそれに伴うノイズ・0 件セルのリスク、および Israel 例の解釈の弱め方が、査読者から指摘されうる新しいポイントになった。**

### 強み（維持・強化すべき点）
- **データソースが peer-reviewed になった**：Israeli national surveillance の年齢別・2 回接種別 COVID-19 関連入院集計（Haas et al. 2021, *Lancet* 397(10287):1819–1829, Table 2, PMCID PMC8099315）に差し替え。
- **出所が CSV 化・追跡可能**：`data/haas_2021_israel_hospitalization_counts.csv` に論文名・表番号・ surveillance 期間を明記。
- **再現性パイプラインが一貫している**：`real_data_analysis.py` → `generate_summary.py` → `generate_rsm_tables.py` → `generate_ione_rsm_v3.py` で、Israel 例も含めて全数値が再生成される。
- **体裁は v5 対応後の状態を維持**：ダブルスペース PDF 22 ページ（25 ページ制限内）、Vancouver 上標引用、見出し Times New Roman/黒、Supplementary の重複・空 References 削除。
- **参考文献が整理された**：Morris 2021（ブログ）と Morris 2025（コメンタリ）を削除し、Haas 2021 を [14] として組み込み。最終的な文献数は 24 件、orphan reference なし。
- **コミットハッシュが記録された**：`results/commit_hash.txt` に package 生成コミット `28599d8` が記録されている。

### 残存リスク（修正必須～高優先）
1. **Haas データのイベント希少性**：N=100,000 の pseudo-IPD で入院イベントは約 90 件（率 0.0009）。一部（年齢群×ワクチン）セルでは 0 イベントが発生しうる。
2. **Israel 例の ARI / bias reduction が低い**：最高の非オラクル方法（2B_clustering）でも ARI ≈ 0.64（K=2）/ 0.49（K=3）と他の 4 例より低く、bias reduction も絶対値で ~0.0008 と小さい。「年齢・接種状況の交絡は存在するが、多変量共変量から完全に回収するのは困難」という解釈を明確にする必要がある。
3. **pseudo-IPD の down-sampling ハードコード**：`target_n = 100000` は `prepare_israel_vaccine_data()` 内にリテラル。再現性には影響しないが、Methods の記述と一致させるべき。
4. **用語の微調整**：本文では「vaccination-effectiveness evaluations [haas2021]」と書かれているが、Haas et al. は surveillance データを用いた *observational study* である。vaccine effectiveness/effectiveness の記載は論文内でも行われているため致命的ではないが、「national vaccine-surveillance data」と表現を近づけるとより正確。

---

## 2. Morris → Haas 差し替えの詳細レビュー

### 2.1 データソースの妥当性

| 項目 | 差し替え前（Morris 2021） | 差し替え後（Haas 2021） | 評価 |
|---|---|---|---|
| 出所種別 | 個人ブログ（covid-datascience.com） | *Lancet* 原著論文 | ◎ 大幅改善 |
| データ内容 | 推定された dashboard 集計 | 年齢別・2 回接種別の人口・入院カウント | ◎ 透明 |
| 追跡可能性 | URL のみ | PMCID + DOI + Table 2 + CSV | ◎ 大幅改善 |
| 倫理/利用規約 | 不明確 | 論文付属データ・公表集計 | ◎ 問題なし |

- Haas et al. 2021 は *Lancet* 原著論文（PMCID PMC8099315）であり、査読者が「一次データ出所として不適切」とはならない。
- ただし、**Israel 例はあくまで公表集計からの pseudo-IPD 再構成**であることは、本文中「These are illustrations, not real-IPD validation」で既に制限付き。

### 2.2 再構成手法の妥当性

- `real_data_analysis.py` は `data/haas_2021_israel_hospitalization_counts.csv` を読み込み、各セルの `population` に比例して多項分布で N=100,000 を層化抽出。
- 各セルでは `hospitalizations / population` を真のイベント率として二項分布で Y を発生させ、年齢・共変量を該当年齢群の分布から生成。
- 生成された pseudo-IPD は下記の通り、Simpson-type paradox を保持：
  - True ATE ≈ -0.00446（ワクチンが入院リスクを下げる方向）
  - Crude bias ≈ +0.00159（周辺集計では接種群の入院率が高く見える）
  - Stratified bias ≈ +0.00081（層別化で改善）

これは年齢が接種と入院双方に強く作用するため、交絡調整の必要性を示す妥当な例になっている。

### 2.3 新たに生じた統計的課題

- **イベント希少性**：入院数 90 件前後に対し、X には 7 変数、Random Forest は 100 本、層別ロジスティック回帰は L2 正則化がかかっているが、0 イベントセルがあると `_safe_predict_proba` は平均で埋めてしまう。
- **推定の不安定性**：`real_data_summary.csv` では、ARI が 2B_clustering で最高でも 0.64（K=2）に留まり、1A/1B/1C/1D/GMM は ARI < 0.10。これはイベント希少性により、Y 情報を用いた方法が機能しにくいため。
- **bias reduction の絶対値が小さい**：~0.0008 と他の例に比べて 1–2 桁小さい。これは偽装ではなく、希少イベントに伴う ATE の小ささを反映しているが、読者が「効果がない」と誤解しないよう注意書きが必要。

---

## 3. Biostatistics 投稿規定・スコープとの適合度

| 適合要件 | 現状 | 適合度 | 備考 |
|---|---|---|---|
| 統計的方法論の新規性（C1, W 診断） | C1 = 1 − I²、W = CATE 分散説明率 | ◎ | 維持 |
| 実問題への動機付け（IPD meta-analysis） | 隠れ効果修修飾の診断 | ◎ | 維持 |
| 25 ページドラフト制限 | 22 ページ / 約 3,300 語 | ◎ | 余裕あり |
| 図表インライン配置 + 別ファイル | docx 内インライン + pptx/png/eps + 別表 docx | ◎ | 維持 |
| 参考文献 Vancouver 上標 | 1–24、順次、上標化済み | ◎ | Morris 削除後も整合 |
| データ/Code Availability | GitHub + lock ファイル + commit_hash.txt | ◎ | Zenodo DOI は acceptance 後想定 |
| 半合成例のデータ出所 | Haas 2021 *Lancet* | ◎ | ブログ問題解決 |
| Israel 例の解釈制限 | 「illustrations, not real-IPD validation」 | △ | さらに「希少イベント・抽出困難」を付記するとよい |

**総じて、Morris 差し替えにより「一次データ出所」のリスクは解消され、Biostatistics への適合度は向上した。**

---

## 4. 査読者が突きそうな科学的・方法論的指摘

### 4.1 Haas データ・Israel 例に関する指摘

- **「なぜ入院データを選んだのか」**：Haas et al. では感染・発症・入院・重症・死亡の複数アウトカムがある。なぜ入院を選んだかを本文か Supplementary で 1 文説明すべき。
  - 提案：年齢による交給が最も顕著に現れ、かつイベント数が層別化に十分な統計力を持つため（Table 2 より感染より age-confounding が強い）。

- **「N=100,000 の down-sampling は妥当か」**：公表集計の総人口 ~650 万をそのまま pseudo-IPD 展開すると計算コストが高い。層化無作為抽出は妥当だが、Methods に `target_n = 100000` とその理由（計算可行性と 0 イベント問題のバランス）を記載すべき。

- **「0 イベントセルがあるのでは」**：16–44 歳接種群などで入院数が極めて少なく、ロジスティック回帰が退化する。Methods に `np.random.default_rng(42)` による二項生成と、退化時の平均埋め（`_safe_predict_proba`）を言及。

- **「ARI が低すぎるのでは」**：Israel 例の ARI が低いことを「抽出困難な例」として提示。'The Israel example shows the most challenging case among the five: strong confounding by age and very rare hospitalisation events made outcome-informed recovery difficult, although the crude marginal association was reversed by stratification.'

### 4.2 他の残存リスク

- **v5 で既に対応済みの事項**（C1/W 帰無分布、W_est 誤指定感度、DL caveats、相対バイアス低減の delta-method SE、30 反復拡張感度）は、現状の docx/PDF でも維持されている。
- **タイトル / Abstract は v5 対応後の C1/W 診断中心構成**を維持。
- **参考文献の継続的整理**：Haas 2021 の追加に伴い、初出順が再計算され [14] となった。`generate_ione_rsm_v3.py` の `CiteManager` は動的に番号付けしているため手動再番号は不要。

---

## 5. 再現性（Data / Code Availability）

| 項目 | 現状 | 評価 |
|---|---|---|
| 公開リポジトリ | https://github.com/bougtoir/ione-stratification-framework | ◎ |
| `requirements-lock.txt` | 存在 | ◎ |
| `results/commit_hash.txt` | `28599d8` を記録 | ◎ |
| Haas データ CSV | `data/haas_2021_israel_hospitalization_counts.csv` | ◎ |
| 1 コマンド再生成 | `generate_summary.py` → `generate_rsm_tables.py` → `generate_ione_rsm_v3.py` | ◎ |
| クリーン clone 検証 | 未実施（v5 時に実施済みのため今回は省略） | △：投稿前に推奨 |

**注**：Morris 差し替えにより `real_data_analysis.py` を含む全パイプラインが変更されたため、投稿直前には再度 `/tmp/ione-repro` 等でクリーン clone からの再生成を推奨。

---

## 6. 原稿表現・体裁の確認

### 6.1 引用番号・参考文献
- `[14]` Haas et al. 2021 は `vaccination-effectiveness evaluations` の直後に出現。`CiteManager` により上標化され、References に Vancouver 形式で記載。
- Morris 2021/2025 は文献リストから完全に削除。

### 6.2 用語の正確性
- `IONE_biostatistics_v3.md` では：
  - `The Israeli vaccination example used pseudo-IPD reconstructed from age- and vaccination-stratified COVID-19-related hospitalisation counts published by Haas et al. [haas2021].`
- これは実装と一致。提案：`vaccination-effectiveness evaluations` を `national vaccine-surveillance data` に近づけるとより正確。

### 6.3 図表
- Figure 3（`fig3_rsm_real_data_ari.png`）が再生成され、Israel Vaccine 行が Haas データに基づく値を反映。
- Table 2 は best non-Oracle method per dataset を報告。Israel における best は `2B_clustering`（K=2, ARI ≈ 0.64）。

---

## 7. 最優先で対応すべき修正案（v6 時点）

### 7.1 必須（投稿前に対応）
1. **Methods の Israel 例セクションに下記を追加**
   - 公表集計总人口 ~6.5M から `target_n = 100000` への層化ダウンサンプリングを明示。
   - 希少イベント（入院）と 0 イベントセルの可能性に言及。
   - なぜ「入院」をアウトカムに選んだか（年齢交絡が最も強く、かつイベント数が層別化に十分）を 1 文説明。
2. **Results / Discussion の Israel 例解釈を強化**
   - `The Israel hospitalisation example is the most challenging of the five illustrations: the crude marginal association reversed with age stratification, but recovery of the true age groups from multi-covariate patterns remained modest because of the very low event rate.`
3. **用語微修正**
   - `vaccination-effectiveness evaluations` → `national vaccine-surveillance data`（または `vaccine-surveillance data`）に変更。

### 7.2 高優先（査読をスムーズに）
4. **クリーン clone 再現性の最終確認**
   - `/tmp/ione-repro` に `git clone` し、パイプラインを実行して `real_data_summary.csv`、`IONE_biostatistics_v3.md`、`IONE_biostatistics_v3_double_spaced.pdf` が一致するか確認。
5. **Figure 3 / Table 2 のキャプション**
   - Israel 行が Haas 2021 由来であることを Table 2 脚注または Figure 3 キャプションで再確認。

### 7.3 中優先・任意
6. `target_n` を CSV に含めるか、`real_data_analysis.py` の定数を `config` 化する。
7. 0 イベントセルへの対処を `_safe_predict_proba` だけでなく、Methods の 1 文で説明。

---

## 8. 図表の再確認結果

| 図表 | 本文言及 | 備考 |
|---|---|---|
| Figure 1 | あり | Primary IPD scenario |
| Figure 2 | あり | Sensitivity to K |
| Figure 3 | あり | Semi-synthetic ARI；Israel row は Haas データに更新済み |
| Figure 4 | あり | Sample size sensitivity |
| Figure 5 | あり | Non-linearity robustness |
| Table 1 | あり | Primary scenario |
| Table 2 | あり | Israel best method は `2B_clustering`（K=2） |
| Table 3 | あり | Non-linearity |

orphan figure/table なし。

---

## 9. 総合判断

- **Morris 2021 → Haas 2021 差し替えは成功**しており、半合成例のデータ出所が peer-reviewed になった。これは v5 時点での重大リスク（ブログソース）を解消する。
- **新たなリスクは主に Israel 例の統計的難しさ**（希少イベント、低 ARI、小さい bias reduction）にあり、これを「希少イベント下では層別抽出が困難である例」として正しく位置づけることが必要。
- 体裁・引用・参考文献・ページ数は v5 対応後の良好な状態を維持。
- **推奨次ステップ**：上記 7.1 の 3 点（Methods 明示、Israel 例解釈、用語微修正）を `generate_ione_rsm_v3.py` に反映し、再生成・再 push。投稿前にクリーン clone 再現性を最終確認。

---

## 10. 推奨されるタイトル/Abstract への影響

- Morris 差し替え自体はタイトル/Abstract に直接影響しない。ただし、Abstract/Discussion で「five semi-synthetic illustrations」に触れる場合は、Israel 例が *Lancet* 集計データに基づくことを付記してもよい。
- タイトルは C1/W 診断を前面に置いたままでよい。
