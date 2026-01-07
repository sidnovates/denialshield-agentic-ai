from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, Form
from sqlalchemy.orm import Session
from typing import List
from pathlib import Path
import uuid
import shutil
import logging
import json

from database import get_db, UploadedDocument
from config import settings
from ocr.paddle_ocr import ocr_processor

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/upload")
async def upload_files(
    files: List[UploadFile] = File(...),
    category: str = Form("PreClaim"), # Expects form data
    db: Session = Depends(get_db)
):
    """
    Upload multiple files (PDFs or images) and perform OCR.
    Files are saved in subfolders based on 'category'.
    """
    if not files:
        raise HTTPException(status_code=400, detail="No files provided")
    
    uploaded_files_info = []
    
    for file in files:
        try:
            # Validate file type
            file_extension = Path(file.filename).suffix.lower()
            allowed_extensions = ['.pdf', '.jpg', '.jpeg', '.png', '.bmp', '.tiff']
            
            if file_extension not in allowed_extensions:
                logger.warning(f"Unsupported file type: {file.filename}")
                continue
            
            # Use category subdirectory
            # Sanitize category to prevent traversal
            safe_category = "".join([c for c in category if c.isalnum()])
            if not safe_category:
                safe_category = "general"
                
            upload_dir = settings.UPLOAD_FOLDER / safe_category
            upload_dir.mkdir(parents=True, exist_ok=True)

            # Generate unique filename
            unique_filename = f"{uuid.uuid4()}_{file.filename}"
            file_path = upload_dir / unique_filename
            
            # Save file
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
            
            logger.info(f"File saved: {file_path}")
            
            print(f"Start processing file: {file.filename}...")
            # Perform OCR with error handling
            try:
                ocr_text = ocr_processor.process_document(str(file_path))
                print(f"Finished processing file: {file.filename}")
                print(f"--- OCR Extracted Text ({file.filename}) ---\n{ocr_text}\n---------------------------------------------")
            except Exception as ocr_error:
                logger.error(f"OCR Failed for {file.filename}: {ocr_error}")
                ocr_text = "" # Fallback to empty text so basic upload succeeds
            
            # Store in database
            db_document = UploadedDocument(
                filename=file.filename,
                file_path=str(file_path),
                file_type=file_extension.replace('.', ''),
                ocr_text=json.dumps(ocr_text) if isinstance(ocr_text, dict) else ocr_text,
                ocr_completed=1 if ocr_text else 0
            )
            db.add(db_document)
            db.commit()
            db.refresh(db_document)
            
            uploaded_files_info.append({
                "id": db_document.id,
                "filename": file.filename,
                "file_type": db_document.file_type,
                "ocr_completed": bool(db_document.ocr_completed),
                "ocr_text_length": len(ocr_text) if ocr_text else 0
            })
            
            logger.info(f"OCR completed for {file.filename}, text length: {len(ocr_text)}")
            
        except Exception as e:
            logger.error(f"Error processing file {file.filename}: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error processing file: {str(e)}")
    
    return {
        "success": True,
        "files_uploaded": len(uploaded_files_info),
        "files": uploaded_files_info
    }


@router.post("/upload/clear")
async def clear_uploads(category: str = None):
    """
    Clear files in the upload directory.
    If category is provided, clears only that subdirectory.
    """
    try:
        folder = settings.UPLOAD_FOLDER
        if not folder.exists():
            return {"success": True, "message": "Nothing to clear"}

        if category:
            safe_category = "".join([c for c in category if c.isalnum()])
            target_dir = folder / safe_category
            if target_dir.exists():
                shutil.rmtree(target_dir)
                target_dir.mkdir(parents=True, exist_ok=True)
                logger.info(f"Cleared upload/category directory: {target_dir}")
        else:
            # Remove the directory and all its contents (legacy behavior or full reset)
            shutil.rmtree(folder)
            # Recreate the empty directory
            folder.mkdir(parents=True, exist_ok=True)
            logger.info(f"Cleared full upload directory: {folder}")
            
        return {"success": True, "message": "Upload directory cleared"}
    except Exception as e:
        logger.error(f"Error clearing upload directory: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error clearing uploads: {str(e)}")


@router.get("/upload/documents")
async def get_documents(category: str = None, db: Session = Depends(get_db)):
    """
    Get list of files currently in the upload directory.
    Recursively scans subfolders or specific category.
    """
    try:
        folder = settings.UPLOAD_FOLDER
        if not folder.exists():
            return {"success": True, "files": []}
            
        # Helper to get files recursively
        physical_files = []
        # Using rglob to find all files in subfolders
        # We need relative paths for checking against filename if logic preserved, 
        # or simplified approach: just list everything.
        
        target_dirs = [folder]
        if category:
             safe_category = "".join([c for c in category if c.isalnum()])
             target_dirs = [folder / safe_category]
        
        found_files = []
        for d in target_dirs:
            if d.exists():
                # If checking root (recursive)
                if d == folder:
                     for f in d.rglob("*"):
                         if f.is_file() and not f.name.endswith('.json'): # Skip session json
                             found_files.append(f)
                else:
                     for f in d.glob("*"):
                         if f.is_file() and not f.name.endswith('.json'):
                            found_files.append(f)

        if not found_files:
            return {"success": True, "files": []}
            
        physical_filenames = [f.name for f in found_files]
            
        # Get metadata from DB for these files
        documents = db.query(UploadedDocument).all()
        
        existing_docs = []
        for doc in documents:
            doc_path = Path(doc.file_path)
            if doc_path.name in physical_filenames:
                existing_docs.append({
                    "id": doc.id,
                    "filename": doc.filename,
                    "file_type": doc.file_type,
                    "ocr_completed": bool(doc.ocr_completed)
                })
                
        return {"success": True, "files": existing_docs}
        
    except Exception as e:
        logger.error(f"Error listing documents: {str(e)}")
        return {"success": False, "files": [], "error": str(e)}
