import razorpay
import os
from dotenv import load_dotenv

load_dotenv()

# Default fallback values
DEFAULT_RAZORPAY_KEY_ID = "rzp_test_y7QL8rNOwvE7FE"
DEFAULT_RAZORPAY_KEY_SECRET = "b078saybQfV62siai1HmrkaN"

RAZORPAY_KEY_ID = os.getenv("RAZORPAY_KEY_ID", DEFAULT_RAZORPAY_KEY_ID)
RAZORPAY_KEY_SECRET = os.getenv("RAZORPAY_KEY_SECRET", DEFAULT_RAZORPAY_KEY_SECRET)

client = razorpay.Client(auth=(RAZORPAY_KEY_ID, RAZORPAY_KEY_SECRET))



# admin 


# DEFAULT_RAZORPAY_KEY_ID = "rzp_test_y7QL8rNOwvE7FE"
# DEFAULT_RAZORPAY_KEY_SECRET = "b078saybQfV62siai1HmrkaN"