#!/usr/bin/env python3
import os
import re
import csv
import argparse
from io import BytesIO
from PyPDF2 import PdfReader, PdfWriter

MODEL_LIMITS = {
    "chatgpt": 20 * 1024 * 1024,      # 20MB
    "notebooklm": 200 * 1024 * 1024   # 200MB
}

def save_pdf(writer, base_name, part, start_page, end_page):
    output_file = f"{base_name}_part{part}.pdf"
    with open(output_file, "wb") as f:
        writer.write(f)
    print(f"✅ {output_file} ({start_page+1}–{end_page} pages)")
    return output_file

def split_with_csv(pdf_path, csv_path, max_size):
    reader = PdfReader(pdf_path)
    total_pages = len(reader.pages)

    # Load split points
    split_points = []
    with open(csv_path, newline="", encoding="utf-8-sig") as f:
        reader_csv = csv.DictReader(f)
        for row in reader_csv:
          print("DEBUG keys:", row.keys())
          print("DEBUG row:", row)
          split_points.append((row["title"], int(row["page"])))
    split_points.sort(key=lambda x: x[1])

    for i, (title, start_page) in enumerate(split_points):
        end_page = split_points[i+1][1] if i+1 < len(split_points) else total_pages
        writer = PdfWriter()
        part = 1
        chunk_start = start_page

        for page_num in range(start_page, end_page):
            writer.add_page(reader.pages[page_num])
            buffer = BytesIO()
            writer.write(buffer)
           
            if buffer.tell() > max_size:
                # remove last page safely
                writer = drop_last_page(writer)
                save_writer(writer, base_title, part, chunk_start, page_num)
                part += 1

                writer = PdfWriter()
                writer.add_page(reader.pages[page_num])
                chunk_start = page_num

        if len(writer.pages) > 0:
          safe_title = safe_filename(title)
          save_pdf(writer, safe_title, part, chunk_start, end_page-1)

def split_by_size(pdf_path, max_size):
    reader = PdfReader(pdf_path)
    total_pages = len(reader.pages)

    base_name = os.path.splitext(os.path.basename(pdf_path))[0]
    writer = PdfWriter()
    part = 1
    chunk_start = 0

    for page_num in range(total_pages):
        writer.add_page(reader.pages[page_num])
        buffer = BytesIO()
        writer.write(buffer)
        if buffer.tell() > max_size:
            # save and reset
            writer = drop_last_page(writer)
            save_pdf(writer, base_name, part, chunk_start, page_num-1)
            part += 1
            writer = PdfWriter()
            writer.add_page(reader.pages[page_num])
            chunk_start = page_num

    if len(writer.pages) > 0:
        save_pdf(writer, base_name, part, chunk_start, total_pages-1)


def drop_last_page(writer: PdfWriter) -> PdfWriter:
    """Return a new PdfWriter without the last page."""
    temp_writer = PdfWriter()
    for p in writer.pages[:-1]:
        temp_writer.add_page(p)
    return temp_writer


def main(pdf_file, csv_file, target):
    max_size = MODEL_LIMITS[target]
    # If CSV not provided, look for index.csv in the same folder as the PDF
    if not csv_file:
        default_csv = os.path.join(os.path.dirname(pdf_file), "index.csv")
        if os.path.exists(default_csv):
            csv_file = default_csv

    if csv_file and os.path.exists(csv_file):
        split_with_csv(pdf_file, csv_file, max_size)
    else:
        split_by_size(pdf_file, max_size)

def safe_filename(title: str) -> str:
    # Replace only characters that are illegal in filenames
    return re.sub(r'[\\/:*?"<>|]', "_", title)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Split PDF by CSV index or size")
    parser.add_argument("-pdf", "--pdf_file", required=True, help="Input PDF file")
    parser.add_argument("-csv", "--csv_file", default=None, help="CSV file (optional)")
    parser.add_argument("--target", choices=MODEL_LIMITS.keys(), default="chatgpt",
                        help="Target platform (default: chatgpt)")
    args = parser.parse_args()
    main(args.pdf_file, args.csv_file, args.target)

