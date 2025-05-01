import os
import requests

KIRIMKAN_URL = os.environ.get('KIRIMKAN_URL')
KIRIMKAN_API_KEY = os.environ.get('KIRIMKAN_API_KEY')

def send_wa(phone_number, verification_code):
    message = f"*Pegon AI*\nYour otp verification code is *{verification_code}*\nDon't share this code with anyone."

    try:
        requests.post(
            KIRIMKAN_URL + '/send-message', 
            json = {
                'number' : phone_number,
                'message': message,
                'api_key': KIRIMKAN_API_KEY,
            },
            timeout = 5
        )
    except Exception as e:
        pass