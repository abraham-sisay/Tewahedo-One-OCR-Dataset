# Claude Code Project Guide: Synaxarium Verification (መጽሐፈ ስንክሳር ዘወርኃ ጥቅምት)

## Objective
Perform a rigorous, line-by-line, word-by-word audit and correction of the OCR-converted Ethiopian Orthodox Synaxarium (Tikimt / ጥቅምት) against the original scanned source document.

## File Hierarchy
- Source Scanned PDF: zewerha tikemet.pdf (113 pages, A4 scans)
- Original OCR Docx: Sinkisar_Tikimt.docx (Raw OCR conversion)
- Page Images: page_images/page_001.png through page_113.png (High-res 150 DPI)
- Raw OCR Pages JSON: pages_data/page_001.json through page_113.json
- Verified Output JSON: erified_data/page_001.json through page_113.json
- Final Output Document: Sinkisar_Tikimt_Verified.docx

## Structure of the Synaxarium Text
Each physical page contains two distinct linguistic sections:
1. **Ge'ez (ግዕዝ)**: The ancient liturgical text (geez array in JSON).
2. **Amharic (አማርኛ)**: The authoritative translation (mharic array in JSON).

## Common OCR Errors to Detect and Correct
1. **Cut-off & Truncated Sentences**:
   - Words broken at column or page edges (e.g. የካ at the bottom of Page 1 and ዳችሁ at the top of Page 2 forming የካዳችሁ).
   - Suffixes or prefixes dropped due to margin binding shadows.
2. **Column Jumps & Mixed Text**:
   - Ge'ez sentences accidentally inserted into the Amharic section or vice versa.
3. **Punctuation & Ethiopic Numbers**:
   - Restore missing Ethiopic numerals (፩, ፪, ፫, ፬, ፭, ፮, ፯, ፰, ፱, ፲, ፳, ፴...).
   - Restore traditional punctuation:
     - ፡ (Word separator / ሁለት ነጥብ)
     - ። (Sentence end / አራት ነጥብ)
     - ፤ (Semicolon / ሠረዝ)
     - ፥ (Comma / ድርብ ሠረዝ)
4. **Faded Glyphs & Misread Characters**:
   - Common OCR confusions: ሀ/ሐ/ኀ, ሰ/ሠ, አ/ዐ, ጸ/ፀ, ደ/ጀ, ጠ/ጨ, etc.

## Verification Workflow
For each page (or batch of pages):
1. **Inspect Scan Image**: View page_images/page_NNN.png.
2. **Inspect Raw OCR**: Read pages_data/page_NNN.json.
3. **Compare**: Read word-by-word, checking against the scan image.
4. **Save Verified**: Write the cleaned, complete Ge'ez and Amharic text to erified_data/page_NNN.json with "status": "verified".
5. **Reassemble**: Run python page_tool.py assemble to generate Sinkisar_Tikimt_Verified.docx.

## CLI Utilities (page_tool.py)
- python page_tool.py get --page <N> : Display text for page N.
- python page_tool.py status : Check verification progress across all 113 pages.
- python page_tool.py assemble : Build Sinkisar_Tikimt_Verified.docx.
