# 査読者目線レビュー：IONE JCMDS v1

## 総合評価

- **致命的（fatal）**: なし
- **高（high）**: 3 点
- **中（medium）**: 4 点
- **低 / 任意（optional）**: 3 点

全体としては内容・再現性・形式は JCMDS 投稿に耐えうる水準にある。ただし、数値の整合性、一部の AI っぽい表現、細かい形式ミスについては査読者または編集によって指摘される可能性がある。

---

## High（提出前に修正推奨）

### 1. Results の n=2000 における residual RE bias の値が表と本文で食い違う

- **該当箇所**: Table 1（0.00816） vs サンプルサイズ感度の結果文（0.00852）
- **問題点**: 両方とも n=2000、K=5、z=1.0、zx=1.0 の条件だが値が異なる。これは Table 1 が primary 50 replications、Figure 4 / Supplementary Table S2 が別バッチ 30 replications から来ているため。ただし、読者は「同じ設定なのになぜ値が違う？」と疑問に思う。
- **具体策**: サンプルサイズ感度の文に以下を追加する。
  > "These estimates come from a separate 30-replication sensitivity batch and therefore differ from Table 1 by Monte Carlo error."
- **対象ファイル**: `results/manuscript/IONE_manuscript.md` または `generate_ione_rsm_v3.py` の該当テンプレート

### 2. "Relevance to JCMDS readers" セクションが自演マーケティング的

- **該当箇所**: Discussion 末尾の `### Relevance to JCMDS readers`
- **問題点**: 査読者を説得するためのセクションだが、「この論文は JCMDS のスコープにぴったりです」という主張を独立セクションにすると、AI 生成臭が強く、学術的な抑揚を損なう。
- **具体策**: サブセクションごと削除し、内容は Introduction の研究動機や Discussion の "Relevance to ..." 冒頭 1–2 文に溶け込ませる。または "Relevance to JCMDS readers" 見出しを消して、直前の "Large-sample behaviour" や "Strengths and limitations" に内容を移す。

### 3. Table 5 の n=10,000 推奨が若干誇張

- **該当箇所**: Table 5「Large sample (n ~ 10 000) ... Prognostic-score or predicted-probability stratification (1A)」
- **問題点**: n=10,000 で最小の絶対 RE bias を持つのは Prognostic_score（0.004375）で、1A_predicted_prob（0.004543）は 2 位。「or predicted-probability stratification (1A)」と並列させると、1A も同格に最良のように見えてしまう。
- **具体策**:
  - Recommended method: `Prognostic-score stratification`
  - Rationale: `Smallest absolute RE bias (0.0044) and largest relative reduction (0.669) at n=10,000; predicted-probability stratification (1A) was second (0.0045, 0.657)`
  - Caveat: 既存の記述を維持

---

## Medium（対応すれば完成度が上がる）

### 4. 図キャプションの `Z->X` 表記が不格好

- **該当箇所**: Figure 5 キャプション「Non-linear Z->X robustness」
- **問題点**: `->` は生 LaTeX / テキスト矢印。論文全体で `Z-to-X` や `Z-by-A` と表記しているので統一する。
- **具体策**: `Non-linear Z-to-X robustness` に変更（または Unicode `→`）。

### 5. カバーレターの C1 説明が plain text 抽出で壊れる

- **該当箇所**: `cover_letter_jcmds_v1.md` 11 行目「C1, an I^2-based within-stratum ...」
- **問題点**: docx では I² として表示される可能性が高いが、plain text 抽出すると「an -based」になり、サブミッションシステムの自動スクリーニングで不自然に映る。
- **具体策**: `an I-squared-based within-stratum heterogeneity/coherence index` に変更。表現は自然であり、フォーマット崩れのリスクもない。

### 6. Figure 7 の画像代替テキストに未変換 LaTeX が残っている

- **該当箇所**: `IONE_jcmds_v1.docx` の `word/document.xml` 中の Figure 7 `descr`
- **問題点**: `eta^2 = W_true` という LaTeX 表記が docx の alt 属性にそのまま入っている。Word 画面上は非表示だが、アクセシビリティや生産工程で問題になりうる。
- **具体策**: `md_to_rsm_docx.py` または `generate_ione_rsm_v3.py` の alt text 生成部分で、`^2` を `-squared` (`eta-squared`) に置換する。

### 7. AI 協力者声明の期間が不自然に広い

- **該当箇所**: Declarations「used OpenAI GPT-4 and GPT-4o (accessed August 2025 through August 2026)」
- **問題点**: 現在 2026-08 なので未来を含む期間になっている。実態と合わないと不信感を与える。
- **具体策**: 実際に使用した期間に修正。例：「August 2025 through August 2026」→「August 2025 through August 2026」のままでも今年度内だが、より具体的に「August 2025 through August 2026」は維持可能。ただし「through August 2026」が未来を含むなら「through the present」とするか、明確に現在までの期間にする。

---

## Low / Optional（対応しても大きく変わらない / 個人の好み）

### 8. Abstract に AUC 結果を入れると、Table/図参照がない

- **該当箇所**: Abstract Results 文の AUC (0.460–0.545; 0.427–0.561)
- **問題点**: Abstract 内で AUC を提示しているが、Abstract 単体ではどの表に対応するかが不明。これ自体は致命ではないが、「see Table 4」を入れると親切。

### 9. Discussion の "ARI ceiling" 比喩が前定義されていない

- **該当箇所**: Discussion "This floor is consistent with the ARI ceiling"
- **問題点**: `ARI ceiling` という用語が前文で定義されていない。読者を混乱させる可能性がある。
- **具体策**: `This floor is consistent with the bounded sorting accuracy reflected in the modest ARI values` 等に言い換える。

### 10. PDF 抽出時に `I 2` / `W est` にスペースが入る

- **該当箇所**: LibreOffice 変換後 PDF および pdftotext 出力
- **問題点**: Word OMML の上付き・下付きが LibreOffice 経由で分離して表示される。Word 画面上では影響がないが、一部抽出環境で不自然に見える。
- **具体策**: 深刻な問題ではない。修正する場合は `run.font.superscript`/`subscript` の利用方法を見直すか、LibreOffice 用に別の変換方法を検討する。ただし、この問題に労力を割く優先度は低い。

---

## 強み（査読者に伝えておくべき点）

- ADEMP / STROBE-Sim チェックリストが整備されている。
- 全数値がリポジトリ CSV から読み出され、`make submission` で再現可能。
- 因果的な主張を過度に拡大せず、C1 / W の限界を率直に報告している。
- Vancouver 引用、図表順序、OMML 数式の形式チェックは概ねクリア。
- JCMDS 編集へのカバーレター宛名は正しい。

---

## 修正優先順位の提案

1. **High をすべて対応**（数値整合性の注釈、Relevance セクション削除/統合、Table 5 の n=10,000 表現）
2. **Medium を可能な範囲で対応**（`Z->X`、`I-squared`、alt text LaTeX、AI 使用期間）
3. **Optional は時間があれば対応**

どの項目から実装を始めますか？
