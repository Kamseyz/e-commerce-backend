from django.conf import settings
import requests
import logging

logger = logging.getLogger(__name__)

# initize
class Paystack:
    def __init__(self):
        self.base_url = "https://api.paystack.co"
        self.base_headers ={
            "Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}",
            "Content-Type": "application/json"
        }
        
    def initialize_paystack(self,amount,email,reference,callback_url=None):
        url = f"{self.base_url}/transaction/initialize"
        data={
            "amount": int(amount * 100),
            "email":email,
            "currency":"NGN",
            "reference":reference
        }
        
        if callback_url:
            data['callback_url'] = callback_url
            
        try:
            res = requests.post(url, json=data, headers=self.base_headers)
            res_data = res.json()
            
            if res.status_code != 200:
                logger.error("Payment failed to reach paystack")
                return{
                    "status":False,
                    "details":res_data
                }
                
                
            elif res.status_code==200 and res_data.get("status"):
                return {
                    "status": True,
                    "message": "Paystack Initialization was successful",
                    "data": res_data
                }
        
        except requests.exceptions.RequestException as e:
            logger.error(f"An error {e} occured")
            return{
                "details": f"An error {e} occured with the api",
                "status":False
            }
                
            
   #verify payment
    def verify_payment(self,reference):
        url = f"{self.base_url}/transaction/verify/{reference}"
        
        try:
            res = requests.get(url,headers=self.base_headers)
            res_data = res.json()
            
            if res.status_code==200 and res_data.get("status"):
                return{
                    "status": True,
                    "message": "Payment was verified successfully",
                    "data": res_data
                }
                
            else:
                logger.error("Unable to verify payment")
                return{
                    "details": "Unable to verify payment",
                    "status":False
                }
                
        except requests.exceptions.RequestException as e:
            logger.error(f"An errorr {e} occurred while trying to verify the paystack reference")
            return{
                "details": f"An error {e} occurred while trying to verify paystack reference"
            }
