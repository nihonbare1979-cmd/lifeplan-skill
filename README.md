# /lifeplan — Claude Code スキル

マネーフォワードの家計データから、**FIREシミュレーション付きライフプランシート**（Google Sheets / Excel）を自動生成する Claude Code スキルです。リベシティ公式の「支出管理表＋ライフプランシート」を“自分専用”に育てる発想をベースにしています。

---

## できること

- マネーフォワードのCSVデータを読み込んで家計実績を自動集計
- FIRE条件（目標資産額・運用利回り・生活費）を対話形式で設定
- 8シート構成のライフプランを自動生成
- FIRE達成予想年齢・想定寿命時の残余資産をシミュレーション
- インフレ率・年代別生活費・大型ライフイベント（教育費／介護費／予備費など）を反映
- 「Die with Zero」思想（資産取り崩し）を設計に組み込み
- 想定寿命・退職年齢をドロップダウンで切り替えて感度分析

---

## 必要なもの

- **Claude Code**
- **マネーフォワード ME**（無料プランで可）
- **Googleアカウント**（Google Sheets で開く場合）
- **Python 3**（`openpyxl` を使用）
- （任意）リベシティ公式の「支出管理表＋ライフプランシート」※ベースに使う場合は各自で入手してください

---

## インストール

```bash
# 1. このリポジトリを ~/.claude/skills/lifeplan に配置
git clone https://github.com/<your-account>/lifeplan-skill.git ~/.claude/skills/lifeplan
#   （zipでダウンロードした場合は、展開した lifeplan フォルダを ~/.claude/skills/ に置く）

# 2. 依存ライブラリをインストール
pip3 install openpyxl

# 3. Claude Code を再起動
```

インストール後、Claude Code で `/lifeplan` が使えるようになります。

---

## 使い方

Claude Code のチャットで:

```
/lifeplan
```

と入力するだけで開始できます。あとはヒアリングに答えていくだけ。データを全部揃えてからでなくても大丈夫です。答えたくない項目は「●●●」と入力すると、その部分をレンジ（範囲）で計算する形にしてくれます。難しいプログラミングの知識は不要です。

---

## ファイル構成

```
lifeplan/
├── SKILL.md                          ← /lifeplan の挙動定義（メイン）
├── README.md                         ← このファイル
├── templates/
│   ├── lifeplan_template.xlsx        ← 8シート構成の空テンプレート
│   └── sample_user_inputs.json       ← ユーザー入力JSONのサンプル
├── scripts/
│   ├── analyze_mf_csv.py             ← MFのCSVを年別・費目別に集計
│   ├── customize_template.py         ← テンプレートをユーザー情報で書き換え
│   └── generate_charts.py            ← 資産推移をHTMLグラフ化
└── docs/
    └── customization_guide.md        ← 数式・カスタマイズの技術詳細
```

---

## サンプルデータについて（重要）

`templates/lifeplan_template.xlsx` と `templates/sample_user_inputs.json` に入っている**名前・年齢・金額はすべてダミーのサンプル値**です。スキル実行時に、あなた自身のデータで上書きされます。テンプレートに実在の個人情報は含まれていません。

---

## 既知の制約

1. **Google Sheets へのアップロードは手動**: 生成された xlsx を各自で Google Sheets にインポートしてください（`ByCol`・`Lambda` などGoogle Sheets固有関数を使うため、開く際は Google Sheets を推奨）。
2. **マネーフォワードのCSV形式変更**: `analyze_mf_csv.py` は列名（日付／金額／大項目）を自動探索していますが、CSV仕様が変わった場合は調整が必要です。

---

## 免責事項

本スキルが生成するのは、入力した前提条件に基づく**概算シミュレーション**です。将来を保証するものではありません。投資・資産運用・退職などの判断は、ご自身の責任で、必要に応じて専門家に相談のうえ行ってください。

---

## 開発・保守

数式やカスタマイズの技術的な詳細は [`docs/customization_guide.md`](docs/customization_guide.md) を参照してください。
