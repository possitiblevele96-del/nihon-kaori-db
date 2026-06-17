"""
convert_excel.py
================
1食材1Excelファイル → JSON変換スクリプト

使い方:
    python convert_excel.py data/raw/broccoli.xlsx --ingredient-id broccoli --ingredient-name-ja ブロッコリー

出力:
    data/ingredients/broccoli.json     （その食材の全成分）
    data/compounds.json                （全食材横断の成分マスター・追記型）
"""

import argparse
import json
import os
import re
import sys
from pathlib import Path

try:
    import pandas as pd
except ImportError:
    print("ERROR: pandas が必要です。 pip install pandas openpyxl")
    sys.exit(1)


# ────────────────────────────────────────────
# 設定
# ────────────────────────────────────────────

# Excelの列名マッピング（列名が変わったらここだけ修正）
COL_COMPOUND     = "揮発性成分名"
COL_ODOR_TYPE    = "呈する香りのタイプ"
COL_FOUND_IN     = "Odor description in literature"

# 出力先ディレクトリ
DIR_INGREDIENTS  = Path("data/ingredients")
FILE_COMPOUNDS   = Path("data/compounds.json")


# ────────────────────────────────────────────
# ユーティリティ
# ────────────────────────────────────────────

def make_id(name_ja: str) -> str:
    """日本語名からシンプルなIDを生成（スペース・記号を除去）"""
    # ひらがな・カタカナ・漢字はそのまま残し、記号・空白を除去
    return re.sub(r"[\s\u3000\(\)（）\[\]「」・,，。、/\\]", "_", name_ja).strip("_")


def split_csv_field(value) -> list[str]:
    """「A、B、C」や「A,B,C」などを分割してリストに"""
    if pd.isna(value) or str(value).strip() == "":
        return []
    # 全角・半角カンマ、読点、スペースで分割
    parts = re.split(r"[、，,\s　]+", str(value))
    return [p.strip() for p in parts if p.strip()]


# ────────────────────────────────────────────
# 変換処理
# ────────────────────────────────────────────

def load_excel(filepath: str) -> pd.DataFrame:
    df = pd.read_excel(filepath, header=0)
    # 必須列チェック
    for col in [COL_COMPOUND, COL_ODOR_TYPE, COL_FOUND_IN]:
        if col not in df.columns:
            print(f"WARNING: 列 '{col}' が見つかりません。列名を確認してください。")
            print(f"  実際の列名: {list(df.columns)}")
    # 成分名が空の行を除去
    df = df[df[COL_COMPOUND].notna() & (df[COL_COMPOUND].str.strip() != "")]
    return df


def row_to_compound(row, ingredient_id: str) -> dict:
    """1行 → 成分オブジェクト"""
    name_ja = str(row[COL_COMPOUND]).strip()
    return {
        "id": make_id(name_ja),
        "name_ja": name_ja,
        "odor_descriptors": split_csv_field(row.get(COL_ODOR_TYPE)),
        "found_in_ingredients": split_csv_field(row.get(COL_FOUND_IN)),
        "source_ingredients": [ingredient_id],   # どの食材シートから来たか
    }


def convert(excel_path: str, ingredient_id: str, ingredient_name_ja: str):
    print(f"\n📂 読み込み: {excel_path}")
    df = load_excel(excel_path)
    print(f"   {len(df)} 行のデータを検出")

    compounds = [row_to_compound(row, ingredient_id) for _, row in df.iterrows()]

    # ── 食材ファイルの出力 ──
    DIR_INGREDIENTS.mkdir(parents=True, exist_ok=True)
    ingredient_data = {
        "id": ingredient_id,
        "name_ja": ingredient_name_ja,
        "compound_count": len(compounds),
        "compounds": compounds,
    }
    out_path = DIR_INGREDIENTS / f"{ingredient_id}.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(ingredient_data, f, ensure_ascii=False, indent=2)
    print(f"✅ 食材ファイル出力: {out_path}")

    # ── 横断マスター（compounds.json）への追記 ──
    if FILE_COMPOUNDS.exists():
        with open(FILE_COMPOUNDS, encoding="utf-8") as f:
            master = json.load(f)
    else:
        master = {}

    added = 0
    updated = 0
    for c in compounds:
        cid = c["id"]
        if cid not in master:
            master[cid] = c
            added += 1
        else:
            # 既存エントリに今回の食材を追記
            existing_sources = master[cid].get("source_ingredients", [])
            if ingredient_id not in existing_sources:
                existing_sources.append(ingredient_id)
                master[cid]["source_ingredients"] = existing_sources
            updated += 1

    with open(FILE_COMPOUNDS, "w", encoding="utf-8") as f:
        json.dump(master, f, ensure_ascii=False, indent=2)
    print(f"✅ 横断マスター更新: {FILE_COMPOUNDS}  (新規追加: {added}, 既存更新: {updated})")
    print(f"\n🎉 完了！ 総成分数（マスター）: {len(master)}")


# ────────────────────────────────────────────
# エントリーポイント
# ────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Excel VOCデータ → JSON変換")
    parser.add_argument("excel_file", help="変換するExcelファイルのパス")
    parser.add_argument("--ingredient-id",      required=True, help="食材ID（英数字）例: broccoli")
    parser.add_argument("--ingredient-name-ja", required=True, help="食材名（日本語）例: ブロッコリー")
    args = parser.parse_args()

    if not os.path.exists(args.excel_file):
        print(f"ERROR: ファイルが見つかりません: {args.excel_file}")
        sys.exit(1)

    convert(args.excel_file, args.ingredient_id, args.ingredient_name_ja)


if __name__ == "__main__":
    main()
