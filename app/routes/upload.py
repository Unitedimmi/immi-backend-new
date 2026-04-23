from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Depends
from fastapi.responses import StreamingResponse
from io import BytesIO
from app.database import db
from app.models.document import Document
from app.utils.auth import get_current_user  

router = APIRouter(
    prefix="/upload",
    tags=["upload"],
    dependencies=[Depends(get_current_user)]
)

@router.post("/doc")
async def upload_doc(
    email: str = Form(...),
    status: str = Form(...),
    visa_type: str = Form(...),
    submitted_date: str = Form(...),   
    last_date: str = Form(...),        
    file: UploadFile = File(...)
):
    user = await db.users.find_one({"email": email})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Validate file type
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed")
    
    # Read the PDF content
    pdf_content = await file.read()
    
    # Check if document exists for this email
    existing_doc = await db.documents.find_one({"email": email})
    
    if existing_doc:
        # 🔁 UPDATE
        await db.documents.update_one(
            {"email": email},
            {"$set": {
                "filename": file.filename,
                "status": status,
                "visa_type": visa_type,
                "submitted_date": submitted_date,
                "last_date": last_date,
                "file_data": pdf_content
            }}
        )

        return {
            "message": "Document updated successfully",
            "action": "updated"
        }

    else:
        # ➕ INSERT
        doc = Document(
            email=email,
            filename=file.filename,
            status=status,
            visa_type=visa_type,
            submitted_date=submitted_date,
            last_date=last_date,
            file_data=pdf_content
        )

        await db.documents.insert_one(doc.model_dump())

        return {
            "message": "New document uploaded successfully",
            "action": "created"
        }


# ⬇️ Retrieve PDF
@router.get("/doc/{email}")
async def get_user_pdf(email: str):
    doc = await db.documents.find_one({"email": email})
    if not doc:
        raise HTTPException(status_code=404, detail="No PDF found for this user")

    pdf_stream = BytesIO(doc["file_data"])
    headers = {
        "Content-Disposition": f'inline; filename="{doc["filename"]}"',
        "Content-Type": "application/pdf",
        "Content-Length": str(len(doc["file_data"])),
        "Cache-Control": "no-cache"
    }

    return StreamingResponse(pdf_stream, media_type="application/pdf", headers=headers)


# 📋 Get PDF Details (Fixed with .get() for safety)
@router.get("/doc/details/{email}")
async def get_user_pdf_details(email: str):
    doc = await db.documents.find_one({"email": email})
    if not doc:
        raise HTTPException(status_code=404, detail="No PDF data found")

    return {
        "email": doc.get("email", ""),
        "filename": doc.get("filename", ""),
        "visa_type": doc.get("visa_type", ""),
        "status": doc.get("status", "Pending"),
        "submitted_date": doc.get("submitted_date", ""),  # ✅ Safe access
        "last_date": doc.get("last_date", "")              # ✅ Safe access
    }