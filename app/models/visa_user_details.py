from pydantic import BaseModel, Field
from typing import List

class VisaCondition(BaseModel):
    code: str
    description: str
    details: str
    reference: str

class VisaUserDetails(BaseModel):
    email: str
    visaGrantNumber: str
    currentDateTime: str
    familyName: str
    visaDescription: str
    documentNumber: str
    countryOfPassport: str
    visaClass: str
    visaStream: str
    visaApplicant: str
    visaGrantDate: str
    visaExpiryDate: str
    location: str
    visaStatus: str
    entriesAllowed: str
    mustNotArriveAfter: str
    periodOfStay: str
    workEntitlements: str
    workplaceRights: str
    workplaceRightsLink: str
    studyEntitlements: str
    visaConditions: List[VisaCondition] = Field(default_factory=list)
