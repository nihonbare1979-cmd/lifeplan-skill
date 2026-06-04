#!/usr/bin/env python3
"""マネーフォワードCSVを年別・費目別に集計するスクリプト

使い方:
    python3 analyze_mf_csv.py /path/to/mf_export.csv
    python3 analyze_mf_csv.py /path/to/mf_export.csv --output summary.json
"""
import argparse
import json
import sys
from pathlib import Path

try:
    import pandas as pd
except ImportError:
    print("⚠️  pandas が必要です: pip3 install pandas")
    sys.exit(1)


def load_csv(path: Path) -> pd.DataFrame:
    """文字コードを自動判定してCSV読込"""
    encodings = ["utf-8-sig", "utf-8", "shift_jis", "cp932"]
    for enc in encodings:
        try:
            df = pd.read_csv(path, encoding=enc)
            print(f"✓ 読込成功（エンコード: {enc}）")
            return df
        except (UnicodeDecodeError, UnicodeError):
            continue
    raise RuntimeError(f"CSVを読み込めませんでした: {path}")


def analyze(df: pd.DataFrame) -> dict:
    """マネーフォワードCSVを集計"""
    # マネーフォワードの典型的な列名: '日付', '内容', '金額（円）', '保有金融機関', '大項目', '中項目', '振替'...
    date_col = next((c for c in df.columns if "日付" in c), None)
    amount_col = next((c for c in df.columns if "金額" in c), None)
    big_cat_col = next((c for c in df.columns if "大項目" in c), None)

    if not all([date_col, amount_col, big_cat_col]):
        raise ValueError(f"必要な列が見つかりません: 日付/金額/大項目")

    df[date_col] = pd.to_datetime(df[date_col], errors="coerce")
    df = df.dropna(subset=[date_col])
    df["年"] = df[date_col].dt.year
    df[amount_col] = pd.to_numeric(df[amount_col], errors="coerce").fillna(0)

    summary = {"年別サマリー": {}, "費目別年別": {}, "統計": {}}

    for year, group in df.groupby("年"):
        income = group[group[amount_col] > 0][amount_col].sum()
        expense = -group[group[amount_col] < 0][amount_col].sum()
        savings = income - expense
        rate = (savings / income * 100) if income else 0
        summary["年別サマリー"][int(year)] = {
            "収入": int(income),
            "支出": int(expense),
            "貯蓄額": int(savings),
            "貯蓄率": round(rate, 1),
        }

    # 費目別×年別
    pivot = df.pivot_table(
        index=big_cat_col, columns="年", values=amount_col, aggfunc="sum", fill_value=0
    )
    for cat, row in pivot.iterrows():
        summary["費目別年別"][str(cat)] = {int(y): int(v) for y, v in row.items()}

    # 統計
    summary["統計"] = {
        "総レコード数": len(df),
        "対象年範囲": f"{int(df['年'].min())}-{int(df['年'].max())}",
        "費目数": len(pivot),
    }

    return summary


def print_report(summary: dict) -> None:
    """人が読みやすい形で表示"""
    print("\n" + "=" * 60)
    print("📊 マネーフォワード家計サマリー")
    print("=" * 60)
    print(f"\n対象期間: {summary['統計']['対象年範囲']}")
    print(f"総レコード数: {summary['統計']['総レコード数']:,}件")
    print(f"費目数: {summary['統計']['費目数']}項目\n")

    print("=== 年別サマリー ===")
    print(f"{'年':>6} {'収入':>14} {'支出':>14} {'貯蓄額':>14} {'貯蓄率':>8}")
    print("-" * 60)
    for year, s in sorted(summary["年別サマリー"].items()):
        print(
            f"{year:>6} {s['収入']:>13,}円 {s['支出']:>13,}円 "
            f"{s['貯蓄額']:>13,}円 {s['貯蓄率']:>7}%"
        )

    print("\n=== 費目別の年平均（上位10項目） ===")
    cat_avgs = []
    for cat, years in summary["費目別年別"].items():
        if years:
            avg = sum(years.values()) / len(years)
            cat_avgs.append((cat, abs(avg)))
    cat_avgs.sort(key=lambda x: x[1], reverse=True)
    for cat, avg in cat_avgs[:10]:
        print(f"  {cat:20} 年平均 {int(avg):>12,}円")


def main():
    parser = argparse.ArgumentParser(description="MFのCSVを年別・費目別に集計")
    parser.add_argument("csv_path", type=Path, help="MFのCSVファイル")
    parser.add_argument("--output", "-o", type=Path, help="JSON出力先（任意）")
    args = parser.parse_args()

    if not args.csv_path.exists():
        print(f"❌ ファイルが見つかりません: {args.csv_path}")
        sys.exit(1)

    df = load_csv(args.csv_path)
    summary = analyze(df)
    print_report(summary)

    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(
            json.dumps(summary, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        print(f"\n✓ JSONを保存: {args.output}")


if __name__ == "__main__":
    main()
