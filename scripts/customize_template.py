#!/usr/bin/env python3
"""ライフプランテンプレートをユーザー情報でカスタマイズするスクリプト

使い方:
    python3 customize_template.py \
        --config user_inputs.json \
        --output ~/lifeplan_work/my_lifeplan.xlsx

user_inputs.json の例:
{
  "family": {
    "本人": {"name": "あなたの名前", "age": 40},
    "配偶者": {"name": "配偶者の名前", "age": 38},
    "子1": {"name": "子1の名前", "age": 8},
    "子2": {"name": "子2の名前", "age": 5}
  },
  "income": {
    "給与": 5000000,
    "副業": 0,
    "賞与": 1500000,
    "不動産収入": 0,
    "配当": 0,
    "老齢年金": 2160000,
    "配偶者年金": 0
  },
  "fire_target": {
    "想定寿命": 95,
    "退職年齢": 60,
    "目標資産": 50000000,
    "運用利回り": 0.05,
    "FIRE後生活費": 3500000
  },
  "life_events": {
    "教育費_子1": [4000000, 2035, 4],
    "教育費_子2": [4000000, 2038, 4],
    "車買い替え": [{"年": 2030, "金額": 1500000}, {"年": 2037, "金額": 1500000}],
    "親介護": [{"年": 2040, "金額": 5000000}, {"年": 2045, "金額": 5000000}],
    "予備費": 500000
  },
  "current_assets": {
    "金融資産合計": 21000000,
    "FIRE資産から除外": 2000000
  }
}
"""
import argparse
import json
import shutil
import sys
from pathlib import Path

try:
    import openpyxl
except ImportError:
    print("⚠️  openpyxl が必要です: pip3 install openpyxl")
    sys.exit(1)


SCRIPT_DIR = Path(__file__).parent
SKILL_DIR = SCRIPT_DIR.parent
DEFAULT_TEMPLATE = SKILL_DIR / "templates" / "lifeplan_template.xlsx"


def customize(template: Path, config: dict, output: Path) -> None:
    shutil.copy(template, output)
    wb = openpyxl.load_workbook(output)

    # === ライフプランシート：家族構成 ===
    ws_lp = wb["ライフプランシート"]
    family = config.get("family", {})
    family_rows = {"本人": 4, "配偶者": 5, "子1": 6, "子2": 7}
    for key, row in family_rows.items():
        member = family.get(key, {})
        if member:
            ws_lp.cell(row=row, column=3).value = member.get("name", "")
            ws_lp.cell(row=row, column=4).value = member.get("age", 0)

    # === 想定寿命 / 退職年齢 ドロップダウンの初期値 ===
    ft = config.get("fire_target", {})
    if "想定寿命" in ft:
        ws_lp.cell(row=1, column=6).value = ft["想定寿命"]  # F1
    if "退職年齢" in ft:
        ws_lp.cell(row=1, column=14).value = ft["退職年齢"]  # N1

    # === 予算計画シート：収入欄 ===
    ws_bp = wb["予算計画シート"]
    income = config.get("income", {})
    income_mapping = {
        "給与":         (7, "給与"),
        "副業":         (8, "副業（駐車場など）"),
        "賞与":         (11, None),
        "老齢年金":     (14, "老齢年金"),
        "配当":         (31, "高配当株配当"),
        "配偶者年金":   (32, "配偶者年金"),
    }
    for key, (row, label) in income_mapping.items():
        if key in income:
            ws_bp.cell(row=row, column=4).value = income[key]
            if label:
                ws_bp.cell(row=row, column=3).value = label

    # === 不動産収入 ===
    if "不動産収入" in income and income["不動産収入"] > 0:
        ws_bp.cell(row=15, column=4).value = income["不動産収入"]
        ws_bp.cell(row=15, column=3).value = "賃貸物件1棟目"

    # === 退職金 (1,800万円固定) ===
    ws_bp.cell(row=28, column=4).value = 18000000
    ws_bp.cell(row=28, column=3).value = f"退職金(FIRE{ft.get('退職年齢', 60)}歳)"

    # === 初期資産 ===
    assets = config.get("current_assets", {})
    if "金融資産合計" in assets:
        excluded = assets.get("FIRE資産から除外", 0)
        net_assets = assets["金融資産合計"] - excluded
        # ライフプランシート D95 = 初期資産（=D92+net_assets ではなく直接代入）
        ws_lp.cell(row=95, column=4).value = f"=D92+{net_assets}"

    wb.save(output)
    print(f"✓ カスタマイズ完了: {output}")
    print(f"  家族: {len(family)} 人")
    print(f"  想定寿命: {ft.get('想定寿命', '未指定')} 歳")
    print(f"  退職年齢: {ft.get('退職年齢', '未指定')} 歳")


def main():
    parser = argparse.ArgumentParser(description="テンプレートのカスタマイズ")
    parser.add_argument("--template", type=Path, default=DEFAULT_TEMPLATE,
                        help=f"テンプレートxlsx (デフォルト: {DEFAULT_TEMPLATE.name})")
    parser.add_argument("--config", type=Path, required=True,
                        help="ユーザー入力JSON")
    parser.add_argument("--output", type=Path, required=True,
                        help="出力xlsxパス")
    args = parser.parse_args()

    if not args.template.exists():
        print(f"❌ テンプレートが見つかりません: {args.template}")
        sys.exit(1)
    if not args.config.exists():
        print(f"❌ 設定ファイルが見つかりません: {args.config}")
        sys.exit(1)

    config = json.loads(args.config.read_text(encoding="utf-8"))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    customize(args.template, config, args.output)


if __name__ == "__main__":
    main()
