# models/passport.py
from pydantic import BaseModel, ConfigDict
from typing import Optional, List
from datetime import date

class UserPersonalInfo(BaseModel):
    user_id: str 
    familyName: str
    givenNames: str
    sex: str
    dateOfBirth: date
    passportNumber: str
    countryOfPassport: str
    nationality: str
    passportDateOfIssue: date
    passportDateOfExpiry: date
    passportPlaceOfIssue: str
    hasNationalIDCard: bool
    nationalIDCardNumber: Optional[str] = None
    nationalIDIssuingCountry: Optional[str] = None
    placeOfBirthTownCity: str
    placeOfBirthStateProvince: str
    placeOfBirthCountry: str
    relationshipStatus: str
    hasOtherNames: bool
    otherNames: List[str] = []
    isCitizenOfPassportCountry: bool
    hasOtherCitizenship: bool
    otherCitizenships: List[str] = []
    hasOtherPassports: bool
    otherPassports: List[str] = []
    hasOtherIdentityDocs: bool
    otherIdentityDocuments: List[str] = []
    hasUndertakenHealthExam: bool

    # ✅ Automatically convert datetime.date to ISO string for MongoDB
    model_config = ConfigDict(
        json_encoders={
            date: lambda v: v.isoformat()
        }
    )



class UserIdRequest(BaseModel):
    user_id: str
