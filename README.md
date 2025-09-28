## README.md (English, MIT License included)

````markdown
# pdf2split

`pdf2split` is a lightweight Python script to **split a large PDF into chapters based on a CSV index, or automatically by file size**.  
It was designed to prepare OCR-processed textbooks for use with ChatGPT and other LLMs, which often have file upload limits (~20MB per file).

---

## Features
- Split PDF into chapters using a CSV index
- Or split PDF purely by size if no CSV is provided
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

### 1. Split by CSV

Prepare a CSV file with chapter titles and start pages (0-based):

```csv
title,page
Chapter 1: Getting Started with Algorithms,0
Chapter 2: Basics of Pseudocode,45
Chapter 3: Data Structures and Examples,110
```

Run the script:

```bash
python pdf2split.py -pdf input.pdf -csv split_points.csv
```

Example output:

```
✅ Chapter_1_Getting_Started_with_Algorithms_part1.pdf (pages 1–45)
✅ Chapter_2_Basics_of_Pseudocode.pdf (pages 46–110)
✅ Chapter_3_Data_Structures_and_Examples.pdf (pages 111–...)
```

---

### 2. Split by Size (no CSV)

If no CSV is provided, the script will automatically split the PDF into parts under the size limit.
The target platform determines the size threshold:
- ChatGPT (default) → ~20MB
- NotebookLM → ~200MB
Examples:
```bash
# Default: ChatGPT (~20MB)
python pdf2split.py -pdf input.pdf

# NotebookLM (~200MB)
python pdf2split.py -pdf input.pdf --target notebooklm
```

---

## Output

* A separate PDF is generated for each chapter (if CSV provided) or by size chunks (if no CSV).
* Filenames are automatically derived from chapter titles or the original PDF name.
* If a file exceeds the size limit, it will be automatically split into multiple files, with sequential numbering appended to the filename.

---

## License

MIT License

Copyright (c) 2025 freedomcat

```

