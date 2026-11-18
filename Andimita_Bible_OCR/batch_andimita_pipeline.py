import os
import sys
import time
import shutil
import subprocess
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
import pymupdf
import docx
from docx.shared import Pt, Inches, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

BASE_URL = "http://www.ethiopianorthodox.org/amharic/yeqolotbet/addiskidantitle/addiskidan/"
OUTPUT_ROOT = r"C:\Users\Abraham.sisay\Documents\Andimita Bible OCR"
LOCAL_SOURCE_DIR = r"C:\Users\Abraham.sisay\Documents\Bible Assets\New testament"

TESSERACT_EXE = r"C:\Users\Abraham.sisay\AppData\Local\Tesseract5\tesseract.exe"
TESSDATA_DIR = r"C:\Users\Abraham.sisay\AppData\Local\Tesseract5\tessdata"
MAX_WORKERS = 8

PDF_BOOKS = [
    "matthewos.pdf",
    "markos.pdf",
    "lukas.pdf",
    "yohanneswengel.pdf",
    "gebrehawariat.pdf",
    "rome.pdf",
    "korontos1.pdf",
    "korontos2.pdf",
    "gelatiya.pdf",
    "epheson.pdf",
    "filipisius.pdf",
    "kolasis.pdf",
    "Teselonke.pdf",
    "teselonke2.pdf",
    "timotiwos1.pdf",
    "timotiwos2.pdf",
    "tito.pdf",
    "filmona.pdf",
    "hebrew.pdf",
    "yacoub.pdf",
    "peter1.pdf",
    "peter2.pdf",
    "melkteyohanes1.pdf",
    "melkteyohanes2.pdf",
    "melkteyohanes3.pdf",
    "yihuda.pdf",
    "raeyeyohannes.pdf",
]


def obtain_pdf(pdf_filename, dest_path):
    """Obtain PDF from local source first, verifying completeness."""
    local_source = os.path.join(LOCAL_SOURCE_DIR, pdf_filename)
    
    # 1. Check local source
    if os.path.exists(local_source) and os.path.getsize(local_source) > 10000:
        expected_size = os.path.getsize(local_source)
        # If dest exists and matches size, all good
        if os.path.exists(dest_path) and os.path.getsize(dest_path) == expected_size:
            print(f"  [Verified] PDF ready in folder ({expected_size:,} bytes)")
            return True
        # Otherwise copy from local source
        print(f"  [Local Source] Copying from Bible Assets: {local_source}")
        shutil.copy2(local_source, dest_path)
        print(f"  Copied instantly ({expected_size:,} bytes)")
        return True

    # 2. If already in destination and large enough
    if os.path.exists(dest_path) and os.path.getsize(dest_path) > 100000:
        print(f"  [Present] PDF ready ({os.path.getsize(dest_path):,} bytes)")
        return True

    # 3. Fallback: Download from web
    url = BASE_URL + pdf_filename
    print(f"  [Web Download] Downloading from {url}")
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=180) as resp, open(dest_path, "wb") as out_f:
            while True:
                chunk = resp.read(65536)
                if not chunk:
                    break
                out_f.write(chunk)
        print(f"  Download successful ({os.path.getsize(dest_path):,} bytes)")
        return True
    except Exception as e:
        print(f"  Download failed: {e}")
        return False


def ocr_single_page(page_idx, pdf_path, scratch_dir, pages_dir):
    """Worker function: extracts image and runs Tesseract OCR."""
    page_num = page_idx + 1
    t0 = time.time()
    try:
        doc = pymupdf.open(str(pdf_path))
        page = doc[page_idx]
        images = page.get_images()
        
        img_path = os.path.join(scratch_dir, f"page_{page_num:03d}.png")
        if not images:
            pix = page.get_pixmap(dpi=200)
            pix.save(img_path)
        else:
            xref = images[0][0]
            base_img = doc.extract_image(xref)
            with open(img_path, "wb") as f:
                f.write(base_img["image"])
        doc.close()
        
        out_base = os.path.join(scratch_dir, f"ocr_{page_num:03d}")
        cmd = [
            TESSERACT_EXE,
            img_path,
            out_base,
            "-l", "amh_best",
            "--tessdata-dir", TESSDATA_DIR
        ]
        
        subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        txt_path = out_base + ".txt"
        
        text = ""
        if os.path.exists(txt_path):
            with open(txt_path, "r", encoding="utf-8") as f:
                text = f.read()
        
        page_txt_file = os.path.join(pages_dir, f"page_{page_num:03d}.txt")
        with open(page_txt_file, "w", encoding="utf-8") as pf:
            pf.write(text)
            
        try:
            if os.path.exists(img_path):
                os.remove(img_path)
        except Exception:
            pass
            
        return page_idx, text, time.time() - t0, None
    except Exception as e:
        return page_idx, "", 0, str(e)


def process_book(pdf_filename, book_index, total_books):
    book_name = os.path.splitext(pdf_filename)[0]
    book_dir = os.path.join(OUTPUT_ROOT, book_name)
    os.makedirs(book_dir, exist_ok=True)
    
    docx_path = os.path.join(book_dir, f"{book_name}_complete.docx")
    txt_path = os.path.join(book_dir, f"{book_name}_complete.txt")
    md_path = os.path.join(book_dir, f"{book_name}_complete.md")
    pages_dir = os.path.join(book_dir, f"{book_name}_pages_text")
    os.makedirs(pages_dir, exist_ok=True)
    
    if os.path.exists(docx_path) and os.path.getsize(docx_path) > 10000:
        print(f"\n[{book_index:02d}/{total_books:02d}] {book_name} is ALREADY COMPLETE. Skipping.")
        return True
        
    print(f"\n{'='*70}")
    print(f"[{book_index:02d}/{total_books:02d}] Processing: {book_name.upper()} ({pdf_filename})")
    print(f"{'='*70}")
    
    # 1. Obtain PDF
    pdf_dest = os.path.join(book_dir, pdf_filename)
    if not obtain_pdf(pdf_filename, pdf_dest):
        print(f"Could not obtain {pdf_filename}. Skipping.")
        return False
        
    # 2. Inspect PDF
    doc = pymupdf.open(pdf_dest)
    total_pages = len(doc)
    doc.close()
    if total_pages == 0:
        print(f"Warning: {pdf_filename} has 0 pages. Re-copying from local source...")
        local_src = os.path.join(LOCAL_SOURCE_DIR, pdf_filename)
        shutil.copy2(local_src, pdf_dest)
        doc = pymupdf.open(pdf_dest)
        total_pages = len(doc)
        doc.close()
        
    print(f"  Total pages to OCR: {total_pages}")
    if total_pages == 0:
        return False
        
    scratch_dir = os.path.join(book_dir, f"_temp_scratch_{book_name}")
    os.makedirs(scratch_dir, exist_ok=True)
    
    # 3. Multi-threaded OCR
    t_start = time.time()
    results = [None] * total_pages
    completed_pages = 0
    
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = {
            executor.submit(ocr_single_page, idx, pdf_dest, scratch_dir, pages_dir): idx 
            for idx in range(total_pages)
        }
        
        for future in as_completed(futures):
            p_idx, text, elapsed, err = future.result()
            completed_pages += 1
            p_num = p_idx + 1
            if err:
                print(f"    Page {p_num:03d} FAILED: {err}")
            else:
                if completed_pages % 10 == 0 or completed_pages == total_pages:
                    print(f"    Progress: {completed_pages:03d}/{total_pages:03d} pages completed ({elapsed:.1f}s/page)")
            results[p_idx] = text or ""
            
    total_ocr_sec = time.time() - t_start
    print(f"  OCR completed in {total_ocr_sec:.1f}s ({total_ocr_sec/total_pages:.2f}s/page)")
    
    # 4. Save Master Text File
    with open(txt_path, "w", encoding="utf-8") as f:
        for idx, text in enumerate(results):
            f.write(f"\n{'='*50}\n")
            f.write(f"ገጽ {idx+1}  |  Page {idx+1}\n")
            f.write(f"{'='*50}\n\n")
            f.write(text.strip() + "\n")
            
    # 5. Save Master Markdown
    with open(md_path, "w", encoding="utf-8") as f:
        f.write(f"# {book_name.upper()} (አዲስ ኪዳን አንድምታ)\n\n")
        f.write(f"*OCR Transcription generated from `{pdf_filename}` ({total_pages} pages)*\n\n---\n\n")
        for idx, text in enumerate(results):
            f.write(f"## ገጽ {idx+1} (Page {idx+1})\n\n")
            f.write(text.strip() + "\n\n---\n\n")
            
    # 6. Save Formatted Word Document (.docx)
    w_doc = docx.Document()
    for s in w_doc.sections:
        s.top_margin = Inches(0.8)
        s.bottom_margin = Inches(0.8)
        s.left_margin = Inches(0.8)
        s.right_margin = Inches(0.8)
        
    p_title = w_doc.add_paragraph()
    p_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_title.paragraph_format.space_before = Pt(16)
    p_title.paragraph_format.space_after = Pt(8)
    r_t = p_title.add_run(f"{book_name.upper()}")
    r_t.font.name = "Nyala"
    r_t.font.size = Pt(20)
    r_t.font.bold = True
    r_t.font.color.rgb = RGBColor(140, 20, 20)
    
    p_sub = w_doc.add_paragraph()
    p_sub.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_sub.paragraph_format.space_after = Pt(20)
    r_sub = p_sub.add_run(f"Complete Transcription ({total_pages} Pages)")
    r_sub.font.name = "Nyala"
    r_sub.font.size = Pt(11)
    r_sub.font.color.rgb = RGBColor(100, 100, 100)
    
    for idx, text in enumerate(results):
        if idx > 0:
            w_doc.add_page_break()
            
        p_hdr = w_doc.add_paragraph()
        p_hdr.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        r_hdr = p_hdr.add_run(f"ገጽ {idx+1}  |  Page {idx+1}")
        r_hdr.font.name = "Nyala"
        r_hdr.font.size = Pt(9)
        r_hdr.font.color.rgb = RGBColor(128, 128, 128)
        
        for line in text.splitlines():
            line_str = line.strip()
            if not line_str:
                continue
            p = w_doc.add_paragraph()
            p.paragraph_format.space_after = Pt(2)
            p.paragraph_format.line_spacing = 1.15
            run = p.add_run(line_str)
            run.font.name = "Nyala"
            if any(k in line_str for k in ["ምዕራፍ", "ክፍል", "አርእስት"]):
                p.alignment = WD_ALIGN_PARAGRAPH.CENTER
                run.font.bold = True
                run.font.size = Pt(13)
                run.font.color.rgb = RGBColor(140, 20, 20)
            else:
                run.font.size = Pt(11)
                
    w_doc.save(docx_path)
    
    try:
        import shutil
        shutil.rmtree(scratch_dir, ignore_errors=True)
    except Exception:
        pass
        
    print(f"  ✓ Saved: {docx_path}")
    print(f"  ✓ Saved: {txt_path}")
    print(f"  ✓ Saved: {md_path}")
    print(f"  ✓ Individual page files in: {pages_dir}")
    return True


def main():
    print("==================================================")
    print("   ANDEMTA NEW TESTAMENT COMPLETE OCR PIPELINE    ")
    print("==================================================")
    print(f"Output Directory: {OUTPUT_ROOT}")
    print(f"Source Directory: {LOCAL_SOURCE_DIR}")
    print(f"Total Books:      {len(PDF_BOOKS)}")
    print(f"Parallel Workers: {MAX_WORKERS}")
    print("==================================================\n")
    
    start_all = time.time()
    completed_books = 0
    
    for idx, pdf in enumerate(PDF_BOOKS):
        success = process_book(pdf, idx + 1, len(PDF_BOOKS))
        if success:
            completed_books += 1
            
    total_elapsed = time.time() - start_all
    print("\n" + "="*70)
    print(f"ALL DONE! {completed_books}/{len(PDF_BOOKS)} books processed successfully.")
    print(f"Total pipeline time: {total_elapsed/60:.1f} minutes")
    print("="*70)

if __name__ == "__main__":
    main()
