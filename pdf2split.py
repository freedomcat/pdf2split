#!/usr/bin/env python3
import csv
import argparse
import os
from io import BytesIO
from PyPDF2 import PdfReader, PdfWriter

# Max file size in bytes (e.g., 18MB)
MAX_FILE_SIZE = 18 * 1024 * 1024

def save_writer(writer, base_title, part, start_page, end_page):
    """Write the current PdfWriter content to a file"""
    safe_title = base_title.replace(" ", "_").replace("/", "_")
    output_file = f"{safe_title}_part{part}.pdf"
    with open(output_file, "wb") as f:
        writer.write(f)
    print(f"✅ {output_file} generated ({start_page+1}–{end_page} pages)")
    return output_file

def main(pdf_path, csv_path):
    # Load split points from CSV
    split_points = []
    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            split_points.append((row["title"], int(row["page"])))

    split_points.sort(key=lambda x: x[1])

    reader = PdfReader(pdf_path)
    total_pages = len(reader.pages)

    for i, (title, start_page) in enumerate(split_points):
        end_page = split_points[i+1][1] if i+1 < len(split_points) else total_pages

        writer = PdfWriter()
        part = 1
        chunk_start = start_page

        for page_num in range(start_page, end_page):
            writer.add_page(reader.pages[page_num])

            # Check size in memory
            buffer = BytesIO()
            writer.write(buffer)
            size = buffer.tell()

            if size > MAX_FILE_SIZE:
                # Rebuild writer without the last page (PyPDF2 3.x has no remove_page)
                temp_writer = PdfWriter()
                for j in range(len(writer.pages) - 1):
                    temp_writer.add_page(writer.pages[j])

                save_writer(temp_writer, title, part, chunk_start, page_num)
                part += 1

                # Start new writer with current page
                writer = PdfWriter()
                writer.add_page(reader.pages[page_num])
                chunk_start = page_num

        # Save remaining pages
        if writer.pages:
            save_writer(writer, title, part, chunk_start, end_page)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Split a PDF into chapters based on CSV, auto-split by size if needed")
    parser.add_argument("-pdf", "--pdf_file", required=True, help="Input PDF file")
    parser.add_argument("-csv", "--csv_file", required=True, help="CSV file with split points")
    args = parser.parse_args()

    main(args.pdf_file, args.csv_file)
