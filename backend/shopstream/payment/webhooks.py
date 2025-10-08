import hmac, hashlib, json, logging
from decimal import Decimal
from django.conf import settings
from django.http import JsonResponse
from rest_framework.views import APIView
from .models import PaymentModel
from datetime import timedelta
from django.utils.timezone import now
from .paystack import Paystack

logger = logging.getLogger(__name__)



class PaystackWebhook(APIView):
    def post(self, request):
        signature = request.headers.get("x-paystack-signature")
        body = request.body

        if not body:
            return JsonResponse({"status": False, "message": "Empty body"}, status=400)

        # Verify signature (only in production)
        if not settings.DEBUG:
            if not signature or not verify_signature(signature, body):
                return JsonResponse({"status": False, "message": "Invalid signature"}, status=400)

        try:
            event = json.loads(body.decode("utf-8"))
        except json.JSONDecodeError as e:
            logger.error(f"JSON decode error: {e}")
            return JsonResponse({"status": False, "message": "Invalid JSON"}, status=400)

        event_name = event.get("event")

        if event_name == "charge.success":
            return handle_charge_success(event)

        return JsonResponse({"status": True, "message": "Event ignored"}, status=200)


def verify_signature(signature, body):
    #Verify Paystack HMAC SHA512 signature
    computed = hmac.new(
        settings.PAYSTACK_SECRET_KEY.encode("utf-8"),
        body,
        hashlib.sha512
    ).hexdigest()
    return hmac.compare_digest(computed, signature)


def handle_charge_success(event):
    #Process successful payment
    data = event.get("data", {})
    paystack_ref = data.get("reference")   # Paystack's reference
    amount_kobo = data.get("amount", 0)
    amount_naira = Decimal(str(amount_kobo)) / Decimal("100")

    try:
        #Look up by Paystack reference
        payment = PaymentModel.objects.get(paystack_reference=paystack_ref)

        if payment.status == "success":
            return JsonResponse({"status": True, "message": "Already processed"}, status=200)

        # Update payment
        payment.status = "success"
        payment.total = amount_naira
        payment.save()

        #Deduct stock for all related items
        for item in payment.items.all():
            item.deduct_stock()

        return JsonResponse({"status": True, "message": "Payment processed successfully"}, status=200)

    except PaymentModel.DoesNotExist:
        logger.error(f"Payment with Paystack ref {paystack_ref} not found")
        return JsonResponse({"status": False, "message": "Payment not found"}, status=404)
    except Exception as e:
        logger.error(f"Webhook processing error: {e}", exc_info=True)
        return JsonResponse({"status": False, "message": str(e)}, status=500)


#failed    
def handle_charges_failed(event):
    data = event.get("data", {})
    paystack_ref= data.get("reference")
    
    try:
        payment = PaymentModel.objects.get(paystack_reference=paystack_ref)
        
        if payment.status == 'failed':
            return JsonResponse({"status":True, "message":"Already marked as failed"},status=200)
        
        payment.status = "failed"
        payment.save()
        
        return JsonResponse({"status":True, "message":"Payment already marked as failed"}, status=200)
    
    except PaymentModel.DoesNotExist:
        return JsonResponse({'status':False, "message":"Payment not found"},status=400)
        
        
        

#abandoned
def marked_abandoned_payment(event):
    cutoff = now() - timedelta(minutes=15)
    pending= PaymentModel.objects.get(status="pending",created_at__lt=cutoff)
    
    for payment in pending:
        response = Paystack().verify_payment(payment.paystack_reference)

        if not response["status"] or response["data"]["data"]["status"] != "success":
            payment.status = "abandoned"
            payment.save()

#reversed
def handle_charge_reversed(event):
    data = event.get("data", {})
    paystack_ref = data.get("reference")

    try:
        payment = PaymentModel.objects.get(paystack_reference=paystack_ref)

        if payment.status == "reversed":
            return JsonResponse({"status": True, "message": "Already marked reversed"}, status=200)

        payment.status = "reversed"
        payment.save()

        # Restore stock if already deducted
        for item in payment.items.all():
            item.product.product_quantity += item.quantity
            item.product.save()

        return JsonResponse({"status": True, "message": "Payment reversed and stock restored"}, status=200)

    except PaymentModel.DoesNotExist:
        return JsonResponse({"status": False, "message": "Payment not found"}, status=404)
