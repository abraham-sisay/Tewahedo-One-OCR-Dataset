"""usage: zoom.py <pdf> <page 1-based> <am|geez> <y0 frac> <y1 frac> <out.png>  (300 dpi)"""
import sys
import pymupdf
pdf, page, col, y0, y1, out = sys.argv[1], int(sys.argv[2]), sys.argv[3], float(sys.argv[4]), float(sys.argv[5]), sys.argv[6]
doc = pymupdf.open(pdf)
r = doc[page - 1].rect
x0, x1 = (r.width * 0.5 - 6, r.width * 0.97) if col == "am" else (r.width * 0.03, r.width * 0.5 + 6)
doc[page - 1].get_pixmap(dpi=300, clip=pymupdf.Rect(x0, r.height * y0, x1, r.height * y1)).save(out)
