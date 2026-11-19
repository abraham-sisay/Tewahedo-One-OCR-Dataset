"""usage: band.py <pdf> <page> <y0 frac> <y1 frac> <out.png> [dpi=450] [col=am]  - tight high-res band for blurry spots."""
import sys, pymupdf
a = sys.argv
pdf, page, y0, y1, out = a[1], int(a[2]), float(a[3]), float(a[4]), a[5]
dpi = int(a[6]) if len(a) > 6 else 450
col = a[7] if len(a) > 7 else "am"
p = pymupdf.open(pdf)[page - 1]; r = p.rect
x0, x1 = (r.width * 0.5, r.width * 0.97) if col == "am" else (r.width * 0.03, r.width * 0.5 + 6)
p.get_pixmap(dpi=dpi, clip=pymupdf.Rect(x0, r.height * y0, x1, r.height * y1)).save(out)
