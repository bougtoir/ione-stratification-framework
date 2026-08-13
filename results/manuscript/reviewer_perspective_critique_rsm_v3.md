# RSM 査読者目線 プレ・サブミッション・クリティカル・レビュー

対象原稿： `results/manuscript/rsm_submission/IONE_rsm_v3.md` / `IONE_rsm_v3.docx`  
想定投稿先： *Research Synthesis Methods*（Cambridge University Press）  
レビュー日： 2026-08-10

---

## 1. 総合評価

**判断： 投稿は可能だが、投稿規定上の不備が複数あり、軽いデスク・リジェクトリスクあり。RSM スコープとしては「IPD メタ解析の診断法」という位置づけで合うが、原稿の導入部分が観察研究全般の議論に傾きすぎており、RSM 読者にとっての「研究合成の方法論」という結びつきがもう一段階強化できる。**

**強み**
- ADEMP・STROBE-Sim の記載があり、シミュレーション設計は透明。
- 感度分析（サンプルサイズ、Z→Y 強度、Z→X 強度、非線形性、層数 K）が比較的広範。
- C1 / W を「探索的診断」として位置づけ、主張を過大にしない姿勢が一貫している。
- 数値が `generate_summary.py` → CSV → `generate_ione_rsm_v3.py` とハードコードされていない。
- Risk-difference ATE への切り替えは collapsibility 問題を回避する正しい判断。

**弱み・リスク**
- **参考文献が本文（author-date）と Reference list（Vancouver 風・番号なし）で形式が不一致**。RSM は「形式は何でもよいが一貫性が必要」と明記しており、これは投稿規定違反。
- **タイトルページが RSM 要求事項を大きく欠落**（ORCID、CRediT、倫理・同意・許諾・臨床試験登録の宣言、AI 利用の詳細記載）。
- **本文内に「Table 1」への幻の言及**（Introduction）があり、図表番号の一貫性を損なう。
- **「neutralisation」という用語がタイトル・アブストラクトに出るが、本文で定義されていない**。
- 1 著者で CRediT 記載がない。
- AI 利用宣言が Cambridge の要求より簡素（ツール名・バージョン・利用日・目的が不足）。
- アブストラクト 261 語。RSM 公称の制限は見当たらないが、多くの Cambridge 誌で 250–300 語が目安のため、念のため確認・短縮を推奨。

---

## 2. RSM 投稿規定との適合度

Cambridge RSM の *Submitting your materials* および *Preparing your materials* から、以下が必須または強く推奨されている。

| 要件 | 現状 | 適合度 | 対応の急務 |
|---|---|---|---|
| ORCID（責任著者） | タイトルページになし | × | **必須**：対応著者の ORCID iD を記載 |
| タイトルページに著者・所属・Email | あり | ○ | 既存 |
| タイトルページに各種宣言 | データ可用性・資金・競合利益のみ本文内。倫理・同意・許諾・臨床試験登録・CRediT・AI 宣言がタイトルページまたは直後にない | △ | **高優先**：RSM 指定の項目を「該当せず / 該当する」で明記 |
| CRediT taxonomy | 本文 Declarations に「T. Onishi …」と簡素な記述のみ | △ | **高優先**：14 項目に沿って対応著者分を記載 |
| AI ツール利用の透明性 | 「Large language models were used …」のみ | △ | **高優先**：ツール名・バージョン・利用日・目的・レビュー体制を記載 |
| 参考文献の一貫性 | 本文 author-date / Reference list Vancouver 風・番号なし | × | **必須**：Vancouver 番号付きに統一、または Harvard author-date に統一 |
| 図表の legend / 本文引用 | 全 Figure/Table に legend あり、本文でも引用あり | ○ | 「Table 1」の幻の言及だけ修正 |
| 図の解像度 | PNG 2400–3900 px、EPS あり | ○ | 良好 |
| 図の alt-text（WCAG） | 不明 | △ | Word 図に alt-text を追加、または別途 description ファイル |
| 補足資料の別ファイル化 | ADEMP/STROBE-Sim チェックリストが本文内「Additional files」としてあるが、zip には同梱されていない | △ | **高優先**：補足資料を docx/pdf 化し zip に追加 |
| 英語の質 | 全体的に読めるが、やや冗長 | △ | 校正・短縮 |

**致命的に近いのは「参考文献の不整合」と「タイトルページの不備」**。これらは事務チェックで差し戻される可能性が高い。

---

## 3. 査読者が突きそうな科学的・方法論的指摘

### 3.1 新規性とスコープ
- RSM は「研究合成の方法論」が核。原稿は IPD メタ解析をターゲットにしているが、Introduction の観察研究全般（Simpson's paradox、confounding、ecological fallacy 等）の議論が多く、RSM 読者にとって「この問題が IPD メタ解析でなぜ重要か」が少し遠い。
- 「neutralisation」という造語がタイトルに入っているが、本文で「層別化によるバイアス低減」にしか定義されていない。査読者は「この言葉は必要か？」と質問する。
- IONE が既存手法（PS 層別、GMM、予後スコア、 clustering）と何が違うのか、1 文で明確にする必要がある。現状は「2 つの診断（C1 と W）＋ 層別化」という組み合わせが貢献だと書かれているが、目立ちにくい。

### 3.2 統計設計と estimand
- **Risk-difference ATE は正しい選択**。この点は肯定される。
- **C1 = 1 − I² は stratum-specific log OR に対して定義されているが、ATE バイアスは risk-difference スケール**。スケールが異なることを自覚的に説明しているが、査読者は「C1 が RD バイアスをどれだけ反映するか」をさらに問う。C1 はあくまで間接診断であることをもっと強調。
- **層間を DerSimonian-Laird (DL) ランダム効果モデルで合成しているが、発見された層は同じデータから作られており独立ではない**。DL を使うことの正当化と限界をもっと明記。特に「層を独立した研究のように扱う」仮定はかなり強い。
- **W_est は Y ~ X + A + X*A の logistic モデルに依存**。モデル特定誤りがあれば W_est が誤導的になる。Limitations で言及はあるが、Methods と Discussion でもっと前置き。
- **n=500 の感度分析で層あたり約 100 人（さらに 50/50 分割で 50 人）となり、Y=1 の細胞が少なく、RD の標準誤差が大きい**。n=500 の結果は信頼できないことを明記するか、除外・補足に移す。

### 3.3 シミュレーション結果の解釈
- **最良非オラクル ARI = 0.032**。これは「真の亜集団構造をほとんど復元できていない」ことを意味する。著者は慎重に解釈しているが、査読者は「では実用価値は？」と反論する。`Detection` と `Extraction` の 2 段階フレーム（Discussion にある）は良いが、Abstract と Introduction の最初に置くべき。
- **サンプルサイズ感度の拡張シナリオは 10 反復のみ**。Monte Carlo 誤差が大きく、数値的差異の解釈が難しい。Table 4–7 に Monte Carlo SE が含まれていない。拡張シナリオも MCSE を報告するか、反復数が少ないことを明記。
- **Table 3（実データ例）の K 選択基準が不明**。Methods ではシミュレーションで K=3,5,10 を使ったとあるが、実データで K=2,3,7 などが選ばれている理由が書かれていない。探索的に複数 K を試したのか、AIC/BIC 等で選んだのかを明記。

### 3.4 実データ例の扱い
- 5 つの Simpson's paradox 例は「半合成例」として公開集計データから疑似 IPD を再構成したもの。査読者は「なぜ実際の IPD データを使わないのか」と問う。
- これは現稿で「illustration, not validation」と弁護しているが、RSM においては「研究合成の文脈で実際の IPD 例がない」ことをもう一段強調し、今後の仕事として位置づける。

---

## 4. 原稿表現・体裁の問題

### 4.1 参考文献
現状：
- 本文： `(Borenstein et al. 2009)`
- Reference list：`Borenstein M, Hedges LV, Higgins JPT, Rothstein HR. Introduction to Meta-Analysis. Chichester: John Wiley & Sons; 2009.`（番号なし、アルファベット順）

RSM の明確な要件は **「一貫性」**。現状は author-date と Vancouver 風の混在。対応案：
1. **Vancouver 番号付きに統一**（本文 `[1]`、Reference list を出現順に番号付け）。ユーザーの知見ノートもこの方針。
2. もし author-date を維持するなら、Reference list も author-date 形式・出版物年順にする。

最善は **Vancouver 番号付き**。

### 4.2 タイトルページ
RSM 要求に基づき、以下を含める：
- 論文タイトル
- 全著者名・所属・Email
- 責任著者の ORCID iD
- 各種宣言：
  - Data availability statement
  - Funding statement
  - Competing interests
  - Ethics approval statement
  - Consent for publication
  - Permissions to reproduce material
  - Clinical trial registration（該当せず）
- CRediT 著者貢献
- AI 利用宣言（詳細版）
- 謝辞（該当すれば）

### 4.3 図表
- Introduction の `baseline characteristics tables (Table 1)`（`IONE_rsm_v3.md` 25 行目付近）を修正。これは「通常論文に表記される baseline characteristics table」の例としての言及だが、実際の Table 1 と区別がつかない。**「a conventional baseline characteristics table」** などに言い換えるか、丸括弧を外す。
- Figure 1 は一つのパネルに複数指標（C1 ~0.9、バイアス低減 ~0.01 等）を並べており、スケールが異なる。2 パネルに分けることを検討。
- 全 Figure に alt text / 長い description を追加（Cambridge WCAG 要求）。

### 4.4 アブストラクト
- 261 語。RSM の制限が確認できていないが、**250 語程度に圧縮** しておくのが無難。
- Background / Methods / Results / Conclusions を構造化見出しで分けた方が読みやすい。現在は 1 段落に Bold ラベルが埋め込まれている。

### 4.5 AI 宣言
Cambridge の要求を満たすため、以下を記述：
- 使用ツール名（例：ChatGPT / Claude / GitHub Copilot 等）
- バージョン（可能な範囲で）
- 利用日
- 利用目的（原稿起草、コード生成、文章校正、表作成等）
- 人間による査読・承認の確認

---

## 5. 優先度付きアクションリスト

### 5.1 投稿前に必須（デスクリジェクト・大修正を回避）
1. **参考文献を Vancouver 番号付きに統一**（`md_to_rsm_docx.py` の `CiteManager` を修正し、`generate_ione_rsm_v3.py` を再実行）。
2. **タイトルページを RSM 要求事項で完成させる**：ORCID、CRediT、倫理・同意・許諾・臨床試験登録、AI 宣言（詳細）を追加。
3. **Introduction の幻の「Table 1」言及を修正**。
4. **AI 利用宣言を Cambridge 基準に拡充**（ツール名・バージョン・利用日・目的・人間レビュー）。

### 5.2 高優先（査読をスムーズにする）
5. **Abstract を構造化・短縮**（250 語前後、Background/Methods/Results/Conclusions）。
6. **C1 のスケールと DL 層別化の限界を Methods / Discussion で一段明確化**。
7. **拡張シナリオ（n, Z-to-Y, Z-to-X, 非線形）に Monte Carlo SE を追加**、または反復数が少ないことを強調。
8. **Table 3（実データ例）の K 選択方法を Methods に明記**。
9. **ADEMP / STROBE-Sim チェックリストを本文から切り離し、別ファイルとして zip に同梱**。
10. **Figure 1 の複数スケール問題を解消**（2 パネル化または正規化）。

### 5.3 中優先（ジャーナル適合度向上）
11. **Introduction を再構成**：IPD メタ解析の文脈から入り、観察研究・Simpson's paradox は動機付けとして短くまとめる。
12. **「neutralisation」という用語を定義するか、タイトル・アブストラクトで弱化**。
13. **タイトルを短縮**（例：`A coherence diagnostic for hidden effect modification in IPD meta-analysis: a simulation study of stratification-based extraction`）。
14. **Methods にシミュレーション・パラメータ表を追加**（Z 分布、X 生成係数、A/Y モデル係数等を一箇所に集約）。
15. **Figure alt text を追加**（WCAG 2.1 Level AA）。

### 5.4 任意（より強い論文にする）
16. **n=500 の結果を補足資料へ移動**、または別シミュレーションで信頼性を高める。
17. **DL ではなく one-stage hierarchical model との比較を追加**。
18. **実 IPD データ例を 1 例追加**（可能であれば）。

---

## 6. ジャーナル適合度を上げる具体的提案

RSM の読者・編集委員は「エビデンス合成の方法論」を求めている。現稿は内容として合っているが、**物語の入り口**が一般の観察研究寄りになっている。以下で適合度を上げられる。

### 6.1 タイトルとアブストラクト
- 「neutralisation」を外し、**診断的な側面**を前面に出す。
- 例：`A coherence diagnostic for hidden effect modification in individual participant data meta-analysis: a simulation study of stratification-based extraction`
- アブストラクトの 1 文目から「IPD meta-analyses often report an average treatment effect, but hidden effect modifiers can make that average fragile」と RSM の関心事を引き込む。

### 6.2 Introduction の再構成
- 第 1 段落：IPD メタ解析における heterogeneity と average effect の問題。
- 第 2 段落：between-study heterogeneity（I²、τ²）だけでは within-study の hidden effect modification が見逃される。
- 第 3 段落：これが観察研究・Simpson's paradox と共通する構造問題であることを短く述べ、例を挙げる。
- 第 4 段落：IONE を「IPD 合成前後に適用する探索的診断」として提案。

### 6.3 ワークフロー図の追加
- 図またはテキストで、**IPD 取得 → 調整 → 従来の two-stage / one-stage 合成 → IONE 診断 → 必要なら層別化** という流れを示す。これが RSM 読者に「どこで使うのか」を直感的に伝える。

### 6.4 カバーレター
- 現状のカバーレターはよく書けている。追加すべきは：
  - RSM の「synthesis of individual participant data」という言葉を 1 文目で使う。
  - 本稿が「conventional random-effects meta-analysis of IPD」に**追加する** sensitivity diagnostic であることを強調。
  - 以前 BMC MRM へ投稿したことや、Research Square プレプリントの有無は正直に開示（該当すれば）。

---

## 7. 総合判断

- **現状のまま投稿することは推奨しない**。最低でも「参考文献の統一」「タイトルページの完成」「AI 宣言の拡充」「Introduction の Table 1 幻言及の修正」は必要。
- これらを完了すれば、**RSM は妥当なターゲット**であり、査読に進める。
- ただし、**RSM よりも `Biostatistics` や `Observational Studies` の方がスコープフィットは自然**（過去の `rsm_biostatistics_obs_comparison.md` と同じ結論）。RSM を選ぶのであれば、上記の「RSM 向け再構成」を徹底すること。

---

## 付録：簡易メトリクス

| 項目 | 値 |
|---|---|
| 本文総語数（docx） | 約 7,281 語 |
| Abstract 語数 | 261 語 |
| 図 | 5 |
| 表 | 7 |
| 参考文献 | 38 |
| リポジトリ | https://github.com/bougtoir/ione-stratification-framework |
