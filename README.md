## README.md (English, MIT License included)


# pdf2split

`pdf2split` is a lightweight Python script to **split a large PDF into chapters and add bookmarks automatically**, based on split points defined in a CSV file.  
It was originally created to prepare study materials (e.g., IT exam textbooks) for easier use with ChatGPT by uploading chapter-level PDFs.

---

## Features
- Add bookmarks at specified pages
- Split PDF into multiple chapter files
- Manage split points with a simple CSV file
- No external tools required, pure Python solution

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
Chapter 1: Introduction to Algorithms,0
Chapter 2: Rules of Pseudocode,49
Chapter 3: Key Points of Pseudocode Programs,119
```

2. Run the script:

```bash
python pdf2split.py -pdf input.pdf -csv split_points.csv
```

3. Example output:

```
✅ Chapter_1_Introduction_to_Algorithms.pdf (pages 1–49)
✅ Chapter_2_Rules_of_Pseudocode.pdf (pages 50–119)
✅ Chapter_3_Key_Points_of_Pseudocode_Programs.pdf (pages 120–...)
```

---

## Output

* Each chapter is exported as a separate PDF file.
* Filenames are automatically derived from chapter titles.
* Each output PDF contains a bookmark pointing to the first page.

---

## License

MIT License

Copyright (c) 2025 freedomcat


