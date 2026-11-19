"""Render one PDF page and crop the Amharic (right) or Ge'ez (left) column into N horizontal strips.
usage: crop_page.py <pdf> <page 1-based> <am|geez> <strips> <outdir>"""
import sys
import pymupdf

pdf, page, col, strips, out = sys.argv[1], int(sys.argv[2]), sys.argv[3], int(sys.argv[4]), sys.argv[5]
doc = pymupdf.open(pdf)
r = doc[page - 1].rect
# body sits roughly between 12% and 97% of the page height; columns split at the middle
x0, x1 = (r.width * 0.5 - 6, r.width * 0.97) if col == "am" else (r.width * 0.03, r.width * 0.5 + 6)
y0, y1 = r.height * 0.10, r.height * 0.98
h = (y1 - y0) / strips
for i in range(strips):
    clip = pymupdf.Rect(x0, y0 + i * h - 8, x1, y0 + (i + 1) * h + 8)
    doc[page - 1].get_pixmap(dpi=220, clip=clip).save(f"{out}/p{page:03d}_{col}_{i + 1}.png")
print("ok")
