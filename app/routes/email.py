# from fastapi import APIRouter
# from app.utils.email import send_email

# router = APIRouter(prefix="/email", tags=["email"])

# @router.post("/send")
# def send_email_route(payload: dict):
#     response = send_email(
#         to=payload["to"],
#         subject=payload["subject"],
#         html_content=payload["message"]
#     )
#     return {"status": "success", "response": response}


# from fastapi import APIRouter, HTTPException, BackgroundTasks
# from fastapi.responses import JSONResponse
# from app.utils.email import send_email_with_pdf
# from app.database import db

# router = APIRouter(prefix="/email", tags=["email"])


# @router.post("/send")
# async def send_email_route(background_tasks: BackgroundTasks, payload: dict):
#     try:
#         email = payload.get("email")
#         visa_grant_number = payload.get("visaGrantNumber")

#         if not email or not visa_grant_number:
#             raise HTTPException(status_code=400, detail="email and visaGrantNumber are required")

#         # --- Fetch record from MongoDB ---
#         record = await db.visa_user_details.find_one({
#             "email": email,
#             "visaGrantNumber": visa_grant_number
#         })

#         if not record:
#             raise HTTPException(status_code=404, detail="Record not found")

#         # --- Fix for visaConditions ---
#         conditions = record.get("visaConditions", [])
#         if conditions and isinstance(conditions[0], dict):
#             conditions = [c.get("condition", "") for c in conditions]

#         # --- HTML Email ---
#         html_content = f"""
#         <h2>Visa Grant Details</h2>
#         <p><strong>Email:</strong> {record.get('email')}</p>
#         <p><strong>Visa Grant Number:</strong> {record.get('visaGrantNumber')}</p>
#         <p><strong>Visa Status:</strong> {record.get('visaStatus')}</p>
#         <p><strong>Visa Class:</strong> {record.get('visaClass')}</p>
#         <p><strong>Visa Stream:</strong> {record.get('visaStream')}</p>
#         <p><strong>Expiry Date:</strong> {record.get('visaExpiryDate')}</p>
#         <p><strong>Conditions:</strong> {', '.join(conditions)}</p>
#         """

#         # --- Use Existing PDF from MongoDB ---
#         if "file_data" not in record:
#             raise HTTPException(status_code=400, detail="No PDF file found in record")

#         pdf_bytes = bytes(record["file_data"])  # Binary -> bytes
#         pdf_filename = record.get("filename", "VisaGrantNotice.pdf")

#         # --- Send Email with PDF ---
#         background_tasks.add_task(
#             send_email_with_pdf,
#             subject=payload.get("subject", "Visa Grant Notification"),
#             recipient=email,
#             html_content=html_content,
#             pdf_bytes=pdf_bytes,
#             pdf_filename=pdf_filename
#         )

#         return JSONResponse(content={"message": "Email sent successfully"}, status_code=200)

#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))




from fastapi import APIRouter, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse
from app.utils.email import send_email_with_pdf
from app.database import db
from datetime import datetime
from zoneinfo import ZoneInfo

router = APIRouter(prefix="/email", tags=["email"])

@router.post("/send")
async def send_email_route(background_tasks: BackgroundTasks, payload: dict):
    try:
        email = payload.get("email")
        visa_grant_number = payload.get("visaGrantNumber")

        if not email or not visa_grant_number:
            raise HTTPException(status_code=400, detail="email and visaGrantNumber are required")

        # --- Fetch record from MongoDB using ONLY visaGrantNumber ---
        record = await db.visa_user_details.find_one({
            "visaGrantNumber": visa_grant_number  # Only search by visa grant number
        })

        if not record:
            raise HTTPException(status_code=404, detail="Record not found for the provided visaGrantNumber")

        # --- Use Existing PDF from MongoDB ---
        if "file_data" not in record:
            raise HTTPException(status_code=400, detail="No PDF file found in record")

        pdf_bytes = bytes(record["file_data"])  # Binary -> bytes
        pdf_filename = record.get("filename", "VisaGrantNotice.pdf")

        # --- Exact VEVO Styled HTML Email Template ---
        html_content = """
        <div style="font-family: Arial, sans-serif; font-size: 14px; color: #000; line-height:1.6;">
            
            <p style="color:red; font-weight:bold; margin:0;">OFFICIAL: Sensitive</p>
            <p style="color:red; font-weight:bold; margin:0;">Personal Privacy</p>
            <br/>

            <h2 style="text-align:center; color:#000; margin-bottom:0;">
                Visa Entitlement Verification Online (VEVO)
            </h2>
            <h3 style="text-align:center; color:#333; margin-top:5px;">
                Visa Details Check
            </h3>

            <p>Dear Sir / Madam,</p>
            <p>
                The visa holder has provided you with a copy of their visa details from the Department's 
                Visa Entitlement Verification Online (VEVO) service for your information.
            </p>

            <p><b>VEVO does not provide evidence of the identity of a person.</b></p>
            <p>
                Always sight the passport or the identity document, such as ImmiCard, that was used by the visa holder 
                for the VEVO visa details check; to confirm their identity and ensure that it matches the details 
                shown in the attached document.
            </p>

            <h4>Important information about VEVO</h4>
            <p>
                A VEVO check shows the visa status and conditions associated with a particular visa holder, 
                such as work or study rights.
            </p>

            <h4>Further Information for Employers</h4>
            <p>
                Employers are strongly encouraged to conduct their own VEVO visa details check, 
                as it is a criminal offence to hire or refer illegal workers in Australia.
            </p>
            <p>
                It is the responsibility of all employers to employ legal workers. 
                This includes both paid and unpaid work.
            </p>
            <p>
                For further information about employing visa holders, please go to: 
                <a href="https://immi.homeaffairs.gov.au/visas/employing-and-sponsoring-someone/learn-about-employing-migrants">
                    Employing legal workers
                </a>
            </p>

            <h4>Further Information for Visa Holders</h4>
            <p>
                All employees in Australia are protected by workplace laws, including visa holders.
            </p>
            <p>
                The Department is working with the Fair Work Ombudsman to help employers understand and follow Australian Workplace laws. 
                The <a href="https://calculate.fairwork.gov.au">Pay and Conditions Tool (PACT)</a> provides information 
                on pay rates, shift calculations, leave arrangements and redundancy entitlements.
            </p>
            <p>
                For further information about working in Alia, please go to: 
                <a href="https://immi.homeaffairs.gov.au/visas/working-in-australia/work-rights-and-exploitation">
                    Working in Australia – your rights and protections
                </a>
            </p>

            <hr style="margin:20px 0;"/>

            <p style="font-size:12px; color:#555;">
                Important Notice: The content of this email is intend.ed only for the individual or entity to whom it is addressed. 
                If you have received this email. in error, the sender and delete the message immediately. 
                The Department of Home Affairs, the ABF and the National Emergency Management Agency respect your privacy 
                and have obligations under the Privacy Act 1988.
            </p>

            <p style="font-size:12px; color:#555;">
                One attachment – Visa grant notice (PDF).
            </p>
        </div>
        """

        current_time = datetime.now(ZoneInfo("Australia/Canberra"))
        formatted_time = current_time.strftime("%A %B %d, %Y %H:%M:%S")

        # Create subject line using the email from payload, not from record
        subject = f"VEVO Visa Details Check for {record.get('familyName', '')} as of {formatted_time} (AEST) Canberra, Australia (GMT +1000)"

        background_tasks.add_task(
            send_email_with_pdf,
            subject=subject,
            recipient=email,  # Use the email from payload
            html_content=html_content,
            pdf_bytes=pdf_bytes,
            pdf_filename=pdf_filename
        )

        return JSONResponse(content={"message": "Email sent successfully"}, status_code=200)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
