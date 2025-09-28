# pdf2split

`pdf2split` は、大きな PDF を **CSV インデックスに基づいて章ごとに分割、またはサイズ単位で自動分割** できる軽量な Python スクリプトです。  
ChatGPT や NotebookLM など、ファイルアップロードに制限（1ファイルあたり ~20MB など）がある LLM 用に、、大きな PDF データを分割して扱いやすくする目的で作られました。

---

## 特長
- CSV インデックスを利用して章ごとに PDF を分割  
- CSV がない場合はサイズ単位で自動分割  
- ファイルサイズを自動でチェックし、制限を超えた場合はさらに分割  
- 依存は [PyPDF2](https://pypi.org/project/PyPDF2/) のみ（純粋な Python 実装）

---

## 必要環境
- Python 3.10 以上  
- [PyPDF2](https://pypi.org/project/PyPDF2/) （または [pypdf](https://pypi.org/project/pypdf/)）

インストール例:
```bash
pip install PyPDF2
```

---

## 使い方

### 1. CSVで分割する場合

章タイトルと開始ページ（**1始まり**）を記載した CSV ファイルを準備します：

```csv
title,page
第1章 アルゴリズム・はじめの一歩,1
第2章 擬似言語の基礎,46
第3章 データ構造と例題,111
```

#### CSVに関する注意
* `page` 列は **1始まり** です（例：`1` は PDF の最初のページを指します）。  
* `-csv` が省略された場合、PDF と同じフォルダの `index.csv` が自動的に使われます。  

実行例:

```bash
python pdf2split.py -pdf input.pdf -csv split_points.csv
```

出力例:

```
✅ 第1章_アルゴリズム・はじめの一歩_part1.pdf (pages 1–45)
✅ 第2章_擬似言語の基礎.pdf (pages 46–110)
✅ 第3章_データ構造と例題.pdf (pages 111–...)
```

---

### 2. CSVがない場合（サイズで自動分割）

CSV を指定しなければ、ファイルサイズの制限に従って自動的に分割されます。  
対象プラットフォームによって制限サイズが変わります：

- ChatGPT （デフォルト） → 約 20MB  
- NotebookLM → 約 200MB  

実行例:
```bash
# デフォルト: ChatGPT (~20MB)
python pdf2split.py -pdf input.pdf

# NotebookLM (~200MB)
python pdf2split.py -pdf input.pdf --target notebooklm
```

---

## 出力

* CSV がある場合は章ごと、ない場合はサイズ単位で PDF が生成されます。  
* ファイル名は章タイトルまたは元の PDF ファイル名から自動生成されます。  
* サイズ上限を超える場合はさらに分割され、末尾に番号が付きます。  

---

### その他のオプション

* `--verbose` : 処理中の詳細ログを表示します。  
* `--log-file LOG.txt` : コンソール出力に加えてログをファイルに保存します。  

---

## ライセンス

MIT License  

Copyright (c) 2025 freedomcat

