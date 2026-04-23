import json
import io
import base64
from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from fastapi.responses import StreamingResponse
from bson import Binary
from app.database import db
from app.models.visa_user_details import VisaUserDetails

router = APIRouter(
    prefix="/visa",
    tags=["visa"],
)

@router.post("/user_details")
async def save_visa_user_details(
    payload: str = Form(...),
    pdf: UploadFile = File(...)
):
    # Parse JSON payload
    visa_data = VisaUserDetails(**json.loads(payload))

    # Read PDF
    pdf_bytes = await pdf.read()

    # Create document
    document = visa_data.model_dump()
    document["filename"] = pdf.filename
    document["file_data"] = Binary(pdf_bytes)

    # Save / update
    await db.visa_user_details.update_one(
        {"email": visa_data.email},   # Match existing record
        {"$set": document},
        upsert=True
    )

    return {"message": f"Visa details and PDF saved for {visa_data.email}"}


# Get visa user details + PDF by email or visaGrantNumber
@router.get("/visa_user_details/{reference}")
async def get_visa_user_details(reference: str, download_pdf: bool = False):
    record = await db.visa_user_details.find_one({
        "$or": [
            {"email": reference},
            {"visaGrantNumber": reference}
        ]
    })

    if not record:
        raise HTTPException(status_code=404, detail="No visa details found")

    record["_id"] = str(record["_id"])

    if download_pdf and "file_data" in record:
        # return as file download
        return StreamingResponse(
            io.BytesIO(record["file_data"]),
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename={record['filename']}"}
        )

    # Convert binary PDF to base64 so frontend can handle it
    if "file_data" in record:
        record["file_data"] = base64.b64encode(record["file_data"]).decode("utf-8")

    return record
