## README.md (English, MIT License included)


# pdf2split

`pdf2split` is a lightweight Python script to **split a large PDF into chapters based on a CSV index**.  
It was designed to prepare OCR-processed textbooks for use with ChatGPT and other LLMs, which often have file upload limits (~20MB per file).

---

## Features
- Split PDF into chapters using a CSV index
- Add bookmarks to each output PDF
- Automatically check file size and split further if over the limit
- Pure Python, no external dependencies except [PyPDF2](https://pypi.org/project/PyPDF2/)

---

## Requirements
- Python 3.10+
- [PyPDF2](https://pypi.org/project/PyPDF2/) (or [pypdf](https://pypi.org/project/pypdf/))

Install:
```bash
pip install PyPDF2
````

---

## Usage

1. Prepare a CSV file with chapter titles and start pages (0-based):

```csv
title,page
Chapter 1: Getting Started with Algorithms,0
Chapter 2: Basics of Pseudocode,45
Chapter 3: Data Structures and Examples,110
```

2. Run the script:

```bash
python pdf2split.py -pdf input.pdf -csv split_points.csv
```

3. Example output:

```
✅ Chapter_1_Getting_Started_with_Algorithms_part1.pdf (pages 1–45)
✅ Chapter_2_Basics_of_Pseudocode.pdf (pages 46–110)
✅ Chapter_3_Data_Structures_and_Examples.pdf (pages 111–...)
```

---

## Output

* A separate PDF is generated for each chapter.  
* Filenames are automatically derived from chapter titles.  
* If a chapter exceeds 20MB, it will be automatically split into multiple files, with sequential numbering appended to the filename.  
* Each output PDF includes a bookmark pointing to the first page.

---

## License

MIT License

Copyright (c) 2025 freedomcat


