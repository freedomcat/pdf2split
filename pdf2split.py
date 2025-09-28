#!/usr/bin/env python3
import csv
import argparse
from PyPDF2 import PdfReader, PdfWriter

def main(pdf_path, csv_path):
    # CSVから分割ポイントを読み込む
    split_points = []
    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            split_points.append((row["title"], int(row["page"])))

    # ページ順にソート
    split_points.sort(key=lambda x: x[1])

    reader = PdfReader(pdf_path)
    total_pages = len(reader.pages)

    for i, (title, start_page) in enumerate(split_points):
        writer = PdfWriter()

        # 次のしおりの直前まで
        end_page = split_points[i+1][1] if i+1 < len(split_points) else total_pages

        for page_num in range(start_page, end_page):
            writer.add_page(reader.pages[page_num])

        # 出力PDFにしおり追加（先頭ページに設定）
        writer.add_outline_item(title, 0)

        # ファイル名用に安全な文字列に変換
        safe_title = title.replace(" ", "_").replace("/", "_")
        output_file = f"{safe_title}.pdf"
        with open(output_file, "wb") as f:
            writer.write(f)

        print(f"✅ {output_file} を出力しました ({start_page+1}～{end_page} ページ)")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="PDFを章ごとに分割するツール")
    parser.add_argument("-pdf", "--pdf_file", required=True, help="入力PDFファイル")
    parser.add_argument("-csv", "--csv_file", required=True, help="分割ポイントCSVファイル")
    args = parser.parse_args()

    main(args.pdf_file, args.csv_file)

