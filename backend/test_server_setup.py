
import sys
import os
from pathlib import Path
import logging

# Setup logging to stdout
logging.basicConfig(stream=sys.stdout, level=logging.INFO)
logger = logging.getLogger(__name__)

print("--- STARTING DIAGNOSTICS ---")

# 1. Check Paths
print(f"CWD: {os.getcwd()}")
print(f"Python: {sys.version}")

# 2. Check Config and Directories
try:
    from config import settings
    print(f"Config Loaded. UPLOAD_FOLDER: {settings.UPLOAD_FOLDER}")
    
    if not settings.UPLOAD_FOLDER.exists():
        print("Creating upload folder...")
        settings.UPLOAD_FOLDER.mkdir(parents=True, exist_ok=True)
    
    test_file = settings.UPLOAD_FOLDER / "test_write.txt"
    with open(test_file, "w") as f:
        f.write("test")
    print("✅ File write permission verified.")
    os.remove(test_file)
    
except Exception as e:
    print(f"❌ Config/File Error: {e}")

# 3. Check OCR Mock
try:
    from ocr.paddle_ocr import ocr_processor
    print("OCR Processor Imported.")
    
    print(f"USE_MOCK_OCR: {settings.USE_MOCK_OCR}")
    
    # Test OCR call
    result = ocr_processor.process_document("dummy.pdf")
    print(f"OCR Test Result Length: {len(str(result))}")
    print("✅ OCR Processor Check Passed")
    
except Exception as e:
    print(f"❌ OCR Error: {e}")
    import traceback
    traceback.print_exc()

# 4. Check Database
try:
    from database import engine, Base
    print("Database Engine Created.")
    Base.metadata.create_all(bind=engine)
    print("✅ Database Tables Created/Verified")
except Exception as e:
    print(f"❌ Database Error: {e}")

print("--- DIAGNOSTICS COMPLETE ---")
