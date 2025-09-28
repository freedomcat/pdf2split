## README_ja.md

## pdf2split

`pdf2split` は、**CSV インデックスに基づいて大きな PDF を章ごとに分割する**ための軽量な Python スクリプトです。  
もともとは、ChatGPT やその他の LLM にアップロードして使うために OCR 済みの教科書を準備する目的で作られました。  
多くの LLM では 1 ファイルあたり ~20MB 前後のアップロード制限があるため、それを超えないようにする用途に最適です。

---

## 特徴
- CSV インデックスを使って PDF を章ごとに分割  
- 各出力 PDF にブックマークを追加  
- ファイルサイズを自動チェックし、制限を超えた場合はさらに分割  
- Python のみで動作し、必要な外部ライブラリは [PyPDF2](https://pypi.org/project/PyPDF2/) のみ  

---

## 必要環境
- Python 3.10 以上
- [PyPDF2](https://pypi.org/project/PyPDF2/) （または [pypdf](https://pypi.org/project/pypdf/)）

インストール方法:
```bash
pip install PyPDF2
````

---

## 使い方

1. 章タイトルと開始ページ番号（0始まり）を記載した CSV ファイルを用意します。

```csv
title,page
第1章 アルゴリズムを始めよう,0
第2章 擬似言語の基本,45
第3章 データ構造とサンプル,110
```

2. スクリプトを実行します。

```bash
python pdf2split.py -pdf input.pdf -csv split_points.csv
```

3. 実行結果の例:

```
✅ 第1章_アルゴリズムを始めよう_part1.pdf (pages 1–45)
✅ 第2章_擬似言語の基本.pdf (pages 46–110)
✅ 第3章_データ構造とサンプル.pdf (pages 111–...)
```

---

## 出力

* 各章ごとに分割された PDF が生成されます。
* ファイル名は章タイトルから自動生成されます。
* 章が 20MB を超える場合、自動的に複数ファイルに分割され、ファイル名の末尾に番号が付きます。  
* 出力された PDF の先頭ページにはしおりが付きます。

---

## ライセンス

MIT License

Copyright (c) 2025 freedomcat

