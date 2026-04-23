from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from app.models.user_info import UserPersonalInfo, UserIdRequest
from app.database import db
from app.utils.auth import get_current_user
from datetime import date, datetime

router = APIRouter(
    prefix="/userInfo",
    tags=["userInfo"],
    dependencies=[Depends(get_current_user)]
)

class FieldRequest(BaseModel):
    user_id: str
    fieldName: str

# ✅ Save user personal info
@router.post("/submit")
async def submit_user_info(info: UserPersonalInfo):
    data = info.model_dump()

    # ✅ Convert all `date` objects to ISO strings
    for key, value in data.items():
        if isinstance(value, date):
            data[key] = value.isoformat()

    # ✅ Add submitted_date in "19-July-2025" format
    submitted_date = datetime.now().strftime("%d-%B-%Y")
    data["submitted_date"] = submitted_date

    # ✅ Check if user_id exists, then update or insert
    existing_user = await db.user_info.find_one({"user_id": info.user_id})
    if existing_user:
        await db.user_info.update_one(
            {"user_id": info.user_id},
            {"$set": data}
        )
    else:
        await db.user_info.insert_one(data)

    return {
        "message": "User personal info saved successfully",
        "user_id": info.user_id
    }


# ✅ Get user info with data found flag and greeting
@router.post("/userdetails")
async def get_user_info(payload: UserIdRequest):
    user_id = payload.user_id

    user_info = await db.user_info.find_one({"user_id": user_id})
    if user_info:
        user_info["_id"] = str(user_info["_id"])
        return {
            "user_data_found": True,
            "user_info": user_info
        }
    else:
        return {
            "user_data_found": False,
            "greeting": "No data available."
        }


@router.post("/SvisaType")
async def save_field_name_to_visa_type(payload: FieldRequest):
    await db.visa_type.insert_one({
        "user_id": payload.user_id,
        "field_name": payload.fieldName
    })

    return {
        "message": f"Field name '{payload.fieldName}' saved to visa_type collection for user {payload.user_id}"
    }

    
@router.get("/SvisaType/{user_id}")
async def get_field_name_from_visa_type(user_id: str):
    record = await db.visa_type.find_one({"user_id": user_id})

    if not record:
        raise HTTPException(status_code=404, detail="No visa_type data found for this user")

    return {
        "visa_type": record["field_name"]
    }
