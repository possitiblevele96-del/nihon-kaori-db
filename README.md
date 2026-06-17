# 🌿 nihon-kaori-db

日本食材の揮発性香り成分（VOC）データベース

## 概要

日本の食材に含まれる揮発性成分（Volatile Organic Compounds）と、それぞれの香りの特徴を収録したオープンデータベースです。料理人、フードクリエイター、食品研究者、香りに興味を持つすべての人に向けて公開しています。

## データ構造

```
data/
├── ingredients/         # 食材ごとの成分データ
│   └── broccoli.json    # ブロッコリー（54成分）
├── compounds.json       # 全食材横断の成分マスター
└── raw/                 # 元データ（Excel）
```

### 成分データの例

```json
{
  "id": "アセトン",
  "name_ja": "アセトン",
  "odor_descriptors": ["化学品", "エーテル", "バター", "乳脂"],
  "found_in_ingredients": ["ネギ族", "アボカド", "ニンジン", "セロリ"],
  "source_ingredients": ["broccoli"]
}
```

## 収録食材

| 食材 | 成分数 |
|------|--------|
| ブロッコリー | 54 |

※ 随時追加予定

## スクリプト

### Excel → JSON 変換

```bash
pip install pandas openpyxl

python scripts/convert_excel.py data/raw/食材名.xlsx \
  --ingredient-id 食材ID（英語） \
  --ingredient-name-ja 食材名（日本語）
```

## ライセンス

データは [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/deed.ja) で公開しています。

## 貢献・問い合わせ

Issue・Pull Request歓迎します。
