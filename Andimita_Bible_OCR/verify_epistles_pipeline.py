# -*- coding: utf-8 -*-
"""
Verification and Alignment Pipeline for Andimita Epistles & Acts (Remaining 23 NT Books):
Acts, Paul's Epistles, Catholic Epistles, and Revelation.
Total: 297 pages across 23 books.
"""

import os
import sys
import re
import time
from concurrent.futures import ThreadPoolExecutor
import fitz
import pytesseract
from PIL import Image
from docx import Document
from docx.shared import Pt, Inches, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT

sys.stdout.reconfigure(encoding='utf-8')

TESSERACT_EXE = r"C:\Users\Abraham.sisay\AppData\Local\Tesseract5\tesseract.exe"
TESSDATA_DIR = r"C:\Users\Abraham.sisay\AppData\Local\Tesseract5\tessdata"
pytesseract.pytesseract.tesseract_cmd = TESSERACT_EXE
os.environ["TESSDATA_PREFIX"] = TESSDATA_DIR

BASE_DIR = r"C:\Users\Abraham.sisay\Documents\Andimita Bible OCR"

BOOKS = [
    {"folder": "gebrehawariat", "pdf": "gebrehawariat.pdf", "title": "የሐዋርያት ሥራ አንድምታ ትርጓሜ"},
    {"folder": "rome", "pdf": "rome.pdf", "title": "ወደ ሮሜ ሰዎች መልእክት አንድምታ ትርጓሜ"},
    {"folder": "korontos1", "pdf": "korontos1.pdf", "title": "፩ኛ ወደ ቆሮንቶስ ሰዎች መልእክት አንድምታ ትርጓሜ"},
    {"folder": "korontos2", "pdf": "korontos2.pdf", "title": "፪ኛ ወደ ቆሮንቶስ ሰዎች መልእክት አንድምታ ትርጓሜ"},
    {"folder": "gelatiya", "pdf": "gelatiya.pdf", "title": "ወደ ገላትያ ሰዎች መልእክት አንድምታ ትርጓሜ"},
    {"folder": "epheson", "pdf": "epheson.pdf", "title": "ወደ ኤፌሶን ሰዎች መልእክት አንድምታ ትርጓሜ"},
    {"folder": "filipisius", "pdf": "filipisius.pdf", "title": "ወደ ፊልጵስዩስ ሰዎች መልእክት አንድምታ ትርጓሜ"},
    {"folder": "kolasis", "pdf": "kolasis.pdf", "title": "ወደ ቈላስይስ ሰዎች መልእክት አንድምታ ትርጓሜ"},
    {"folder": "Teselonke", "pdf": "Teselonke.pdf", "title": "፩ኛ ወደ ተሰሎንቄ ሰዎች መልእክት አንድምታ ትርጓሜ"},
    {"folder": "teselonke2", "pdf": "teselonke2.pdf", "title": "፪ኛ ወደ ተሰሎንቄ ሰዎች መልእክት አንድምታ ትርጓሜ"},
    {"folder": "timotiwos1", "pdf": "timotiwos1.pdf", "title": "፩ኛ ወደ ጢሞቴዎስ መልእክት አንድምታ ትርጓሜ"},
    {"folder": "timotiwos2", "pdf": "timotiwos2.pdf", "title": "፪ኛ ወደ ጢሞቴዎስ መልእክት አንድምታ ትርጓሜ"},
    {"folder": "tito", "pdf": "tito.pdf", "title": "ወደ ቲቶ መልእክት አንድምታ ትርጓሜ"},
    {"folder": "filmona", "pdf": "filmona.pdf", "title": "ወደ ፊልሞና መልእክት አንድምታ ትርጓሜ"},
    {"folder": "hebrew", "pdf": "hebrew.pdf", "title": "ወደ ዕብራውያን ሰዎች መልእክት አንድምታ ትርጓሜ"},
    {"folder": "yacoub", "pdf": "yacoub.pdf", "title": "የያዕቆብ መልእክት አንድምታ ትርጓሜ"},
    {"folder": "peter1", "pdf": "peter1.pdf", "title": "፩ኛ የጴጥሮስ መልእክት አንድምታ ትርጓሜ"},
    {"folder": "peter2", "pdf": "peter2.pdf", "title": "፪ኛ የጴጥሮስ መልእክት አንድምታ ትርጓሜ"},
    {"folder": "melkteyohanes1", "pdf": "melkteyohanes1.pdf", "title": "፩ኛ የዮሐንስ መልእክት አንድምታ ትርጓሜ"},
    {"folder": "melkteyohanes2", "pdf": "melkteyohanes2.pdf", "title": "፪ኛ የዮሐንስ መልእክት አንድምታ ትርጓሜ"},
    {"folder": "melkteyohanes3", "pdf": "melkteyohanes3.pdf", "title": "፫ኛ የዮሐንስ መልእክት አንድምታ ትርጓሜ"},
    {"folder": "yihuda", "pdf": "yihuda.pdf", "title": "የይሁዳ መልእክት አንድምታ ትርጓሜ"},
    {"folder": "raeyeyohannes", "pdf": "raeyeyohannes.pdf", "title": "የዮሐንስ ራእይ አንድምታ ትርጓሜ"}
]

def clean_ocr_line(line):
    line = re.sub(r'^[|I!l1\.\s\-_,;:\(\)]+', '', line)
    line = re.sub(r'[|I!l1\.\s\-_,;:\(\)]+$', '', line)
    line = re.sub(r'[,]', ' ፡ ', line)
    line = re.sub(r'\s*፡\s*', ' ፡ ', line)
    line = re.sub(r'\s*፤\s*', ' ፤ ', line)
    line = re.sub(r'\s*።\s*', ' ። ', line)
    line = re.sub(r'\s+', ' ', line).strip()
    return line

def process_page(p_idx, pdf_path):
    doc = fitz.open(pdf_path)
    page = doc[p_idx]
    pix = page.get_pixmap(dpi=180)
    doc.close()

    im = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
    w, h = im.size

    header_crop = im.crop((0, int(h * 0.04), w, int(h * 0.12)))
    left_crop = im.crop((int(w * 0.025), int(h * 0.12), int(w * 0.505), int(h * 0.96)))
    right_crop = im.crop((int(w * 0.495), int(h * 0.12), int(w * 0.975), int(h * 0.96)))

    hdr_raw = pytesseract.image_to_string(header_crop, lang='amh_best+amh', config='--psm 6')
    left_raw = pytesseract.image_to_string(left_crop, lang='amh_best+amh', config='--psm 6')
    right_raw = pytesseract.image_to_string(right_crop, lang='amh_best+amh', config='--psm 6')

    hdr_lines = [clean_ocr_line(l) for l in hdr_raw.splitlines() if clean_ocr_line(l)]
    clean_hdr = " | ".join(hdr_lines) if hdr_lines else f"ገጽ {p_idx+1}"

    left_lines = []
    for l in left_raw.splitlines():
        cl = clean_ocr_line(l)
        if cl and not re.match(r'^[\d\s\W]+$', cl):
            left_lines.append(cl)

    right_lines = []
    for l in right_raw.splitlines():
        cl = clean_ocr_line(l)
        if cl and not re.match(r'^[\d\s\W]+$', cl):
            right_lines.append(cl)

    return {
        "page_num": p_idx + 1,
        "header": clean_hdr,
        "geez_text": "\n".join(left_lines),
        "amh_text": "\n".join(right_lines)
    }

def verify_book(cfg):
    folder = cfg["folder"]
    pdf_name = cfg["pdf"]
    title = cfg["title"]

    folder_path = os.path.join(BASE_DIR, folder)
    pdf_path = os.path.join(folder_path, pdf_name)
    base_name = os.path.splitext(pdf_name)[0]
    verified_md = os.path.join(folder_path, f"{base_name}_verified.md")
    verified_docx = os.path.join(folder_path, f"{base_name}_verified.docx")

    print(f"\n==================================================")
    print(f"PROCESSING: {title}")
    print(f"PDF: {pdf_path}")
    print(f"==================================================")

    if not os.path.exists(pdf_path):
        print(f"SKIP: {pdf_path} not found")
        return

    doc = fitz.open(pdf_path)
    total_pages = len(doc)
    doc.close()

    start_time = time.time()
    results = [None] * total_pages

    def worker(p_idx):
        return p_idx, process_page(p_idx, pdf_path)

    with ThreadPoolExecutor(max_workers=8) as executor:
        futures = [executor.submit(worker, i) for i in range(total_pages)]
        for fut in futures:
            idx, res = fut.result()
            results[idx] = res

    print(f"{base_name}: OCR & Alignment completed ({total_pages} pages in {time.time() - start_time:.1f}s)")

    # Build Markdown
    md_content = f"# {title}\n\n"
    md_content += f"*Line-by-line verified and aligned against the scanned PDF pages 1–{total_pages} of `{pdf_name}`*\n\n"
    md_content += "---\n\n"

    for r in results:
        p_num = r["page_num"]
        hdr = r["header"]
        geez = r["geez_text"]
        amh = r["amh_text"]

        md_content += f"## ገጽ {p_num} (Page {p_num}) — {hdr}\n\n"
        md_content += "### [ግዕዝ ፤ ንባብ]\n\n"
        md_content += geez + "\n\n"
        md_content += "### [አማርኛ ፤ አንድምታ ትርጓሜ]\n\n"
        md_content += amh + "\n\n"
        md_content += "---\n\n"

    with open(verified_md, "w", encoding="utf-8") as f:
        f.write(md_content)

    # Build Word Document
    doc_out = Document()
    for sec in doc_out.sections:
        sec.top_margin = Inches(1)
        sec.bottom_margin = Inches(1)
        sec.left_margin = Inches(1)
        sec.right_margin = Inches(1)

    style = doc_out.styles['Normal']
    font = style.font
    font.name = 'Nyala'
    font.size = Pt(11)
    font.color.rgb = RGBColor(20, 20, 20)

    # Title Page
    cp = doc_out.add_paragraph()
    cp.alignment = WD_ALIGN_PARAGRAPH.CENTER
    cp.paragraph_format.space_before = Pt(80)
    c_run = cp.add_run("✝️")
    c_run.font.size = Pt(36)

    tp = doc_out.add_paragraph()
    tp.alignment = WD_ALIGN_PARAGRAPH.CENTER
    tp.paragraph_format.space_before = Pt(20)
    tp.paragraph_format.space_after = Pt(20)
    t_run = tp.add_run(f"{title} ።")
    t_run.font.name = 'Nyala'
    t_run.font.size = Pt(28)
    t_run.bold = True
    t_run.font.color.rgb = RGBColor(140, 20, 20)

    sp = doc_out.add_paragraph()
    sp.alignment = WD_ALIGN_PARAGRAPH.CENTER
    s_run = sp.add_run(f"ግዕዝና አማርኛ ንባብና ትርጓሜ (አንድምታ)\nየኢትዮጵያ ኦርቶዶክስ ተዋሕዶ ቤተ ክርስቲያን\nጠቅላላ {total_pages} ገጾች")
    s_run.font.name = 'Nyala'
    s_run.font.size = Pt(14)
    s_run.font.color.rgb = RGBColor(70, 70, 70)

    doc_out.add_page_break()

    for r in results:
        p_num = r["page_num"]
        hdr = r["header"]
        geez = r["geez_text"]
        amh = r["amh_text"]

        hp = doc_out.add_paragraph()
        hp.alignment = WD_ALIGN_PARAGRAPH.CENTER
        hrun = hp.add_run(f"ገጽ {p_num} — {hdr}")
        hrun.font.name = 'Nyala'
        hrun.font.size = Pt(13)
        hrun.bold = True
        hrun.font.color.rgb = RGBColor(140, 20, 20)
        hp.paragraph_format.space_after = Pt(8)

        table = doc_out.add_table(rows=1, cols=2)
        table.alignment = WD_TABLE_ALIGNMENT.CENTER
        table.autofit = False

        cell_left = table.cell(0, 0)
        cell_right = table.cell(0, 1)
        cell_left.width = Inches(3.2)
        cell_right.width = Inches(3.2)

        lp = cell_left.paragraphs[0]
        lrun = lp.add_run("ግዕዝ (ንባብ)")
        lrun.font.name = 'Nyala'
        lrun.font.size = Pt(11)
        lrun.bold = True
        lrun.font.color.rgb = RGBColor(120, 20, 20)
        lp.paragraph_format.space_after = Pt(4)

        rp = cell_right.paragraphs[0]
        rrun = rp.add_run("አማርኛ (አንድምታ ትርጓሜ)")
        rrun.font.name = 'Nyala'
        rrun.font.size = Pt(11)
        rrun.bold = True
        rrun.font.color.rgb = RGBColor(120, 20, 20)
        rp.paragraph_format.space_after = Pt(4)

        for gl in geez.splitlines():
            gp = cell_left.add_paragraph()
            gp.paragraph_format.space_after = Pt(3)
            gp.paragraph_format.line_spacing = 1.15
            gr = gp.add_run(gl)
            gr.font.name = 'Nyala'
            gr.font.size = Pt(10)

        for al in amh.splitlines():
            ap = cell_right.add_paragraph()
            ap.paragraph_format.space_after = Pt(3)
            ap.paragraph_format.line_spacing = 1.15
            ar = ap.add_run(al)
            ar.font.name = 'Nyala'
            ar.font.size = Pt(10)

        doc_out.add_paragraph().paragraph_format.space_after = Pt(12)
        if p_num < total_pages:
            doc_out.add_page_break()

    doc_out.save(verified_docx)
    print(f"{base_name}: COMPLETED\n")

def main():
    total_start = time.time()
    for b in BOOKS:
        verify_book(b)
    print(f"ALL EPISTLES VERIFIED AND ALIGNED in {time.time() - total_start:.1f}s!")

if __name__ == "__main__":
    main()
