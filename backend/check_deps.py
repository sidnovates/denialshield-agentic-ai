import sys
import os
import shutil

print(f"Python: {sys.version}")
try:
    from pdf2image import convert_from_path, pdfinfo_from_path
    print("pdf2image imported successfully.")
except ImportError:
    print("ERROR: pdf2image not installed.")
    sys.exit(1)

# Check for poppler
if shutil.which("pdftoppm") or shutil.which("pdfinfo"):
    print("Poppler found in PATH.")
else:
    print("ERROR: Poppler NOT found in PATH. pdf2image requires poppler-utils.")

try:
    from paddleocr import PaddleOCR
    print("PaddleOCR imported successfully.")
except ImportError:
    print("ERROR: paddleocr not installed.")
