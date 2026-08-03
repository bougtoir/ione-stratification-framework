# IONE 改稿セッション引き継ぎ資料

> 本資料は、BMC Medical Research Methodology 最終拒否後の新規セッション（Statistics in Medicine への改稿）への引き継ぎ用です。

## 決定事項

- **第一投稿先**: *Statistics in Medicine*（購読型で APC $0）
- **次点（フォールバック）**: *Journal of Causal Inference*（De Gruyter）
- **論文の再位置づけ**: 「成熟した2段階ワークフロー」ではなく「**探索的診断感度研究**（exploratory diagnostic sensitivity study）」として改稿

## ベース原稿

- `results/manuscript/r2_source/IONE_manuscript_r2_cleaned.docx`: BMC MRM への R2 原稿（最終的に拒否された版）
- `results/manuscript/r2_source/IONE_response_to_reviewers_v2.docx`: R1 → R2 の返答状
- `results/manuscript/r2_source/IONE_figure_legends.docx`: R2 の図凡例

R2 原稿にはすでに W、表 8–11、モンテカルロ標準誤差、能動的比較対象、ADEMP フレーミングが含まれています。**改稿はこの R2 版から始めてください**（リポジトリ内の `IONE_manuscript.md` や `create_docx.py` は第1ラウンド版のため古い）。

## 拒否の背景

- **Submission ID**: `7f49c954-3442-436d-8bdd-ea6aa9468caf`
- **経緯**: 3/30 投稿 → 6/3 修正依頼 → 8/3 最終拒否
- **編集者**: Lan Lan, *BMC Medical Research Methodology*
- **編集者コメント**: 指摘された懸念はこれ以上の修正では対応できない（not viewed as addressable through revision）と判断されたため、BMC MRM への再投稿不可
- **レビュアー**: Reviewer 1, 2, 3, 4 の4名。Reviewer 2, 3 は添付ファイルあり

## 最優先の修正項目

詳細は `results/manuscript/revision_plan.md` を参照。特に以下は致命的だった指摘です。

1. **バイアス削減の数値と式の整合性**（Reviewer 1/2）
   - 相対削減 `1 - |bias_stratified| / |bias_crude|` と報告された 7.4% が一致しない
   - 式・表・図・抄録を統一する
2. **W 指標のオラクル性**（Reviewer 1）
   - 真の CATE から計算されるため実践的診断として不適切
   - 選択肢: (a) 観測データのみの推定 CATE 版を実装・評価する、(b) シミュレーション限定性能指標として再位置づけする
3. **C1 の未校正・判別力不足**（Reviewer 1/2）
   - 主要シミュレーションで C1 = 0.77–0.88 と提案手法・ランダム層化・オラクル基準の間で重なりが大きい
   - 固定しきい値ではなく、複数領域での校正曲線を提示
4. **真の構造・オラクル基準の定義**（Reviewer 2/3）
   - 真の部分集団は `Z` の離散カテゴリとして定義し、同じ K でオラクル ARI ≈ 1 にする
5. **方法分類の不整合**（Reviewer 2）
   - 能動的比較対象 3/4 つ、18 手法カウントなどを統一
6. **結果に関与する方法の循環性**（Reviewer 2/3）
   - 残差・予測確率ベースの層化は診断に限定し、効果推定には発見/評価分割を要求
7. **追加ファイル1の不整合**（Reviewer 1）
8. **実装詳細と恒久的コードアーカイブ**（Reviewer 2）

## ONISHI フレームワークとの連携

- **ONISHI**: AJE（7/10 投稿）→ 7/30 デスクリジェクト → 7/31 **Research Synthesis Methods** 投稿済
- IONE、KOTHA、LINKO はいずれも ONISHI 内で **Research Square** の URL/DOI で参照されている
- 改稿後は **Research Square v2** を速やかに公開し、ONISHI の引用先を更新可能にする
- **KOTHA** は RSM 向けに準備中（別セッション）、**LINKO** は BMC MRM 通常号または RSM（別セッション）

## このブランチで作成された資料

- `results/manuscript/next_journal_proposal.md`: 日本語の投稿先提案書
- `results/manuscript/revision_plan.md`: 日本語の修正計画
- `results/manuscript/BMC_decision_response.md`: 編集者宛返答状（英語）
- `results/manuscript/r2_source/`: R2 原稿・返答状・図凡例のコピー
- `results/manuscript/handoff_to_revision_session.md`: 本ファイル

## 新規セッションでの最初のタスク案

1. `r2_source/IONE_manuscript_r2_cleaned.docx` の内容を確認（特に W、表 8–11、バイアス削減数値）
2. バイアス削減の式と数値を整合させる
3. W 指標の扱いを決定（推定 CATE 版かシミュレーション限定か）
4. C1 の校正曲線を追加・提示する方向を具体化
5. Statistics in Medicine の Author Guidelines を確認
6. 改稿版 docx / 返答状 / 図表 pptx / 表 docx を作成

## 注意

- 数値はすべて最新のコード/結果から再生成すること（ハードコード禁止）
- 図表は本文内で出現順に引用し、キャプションは別ファイルでも提供
- 投稿前に `results/manuscript/next_journal_proposal.md` の目標誌を再確認
