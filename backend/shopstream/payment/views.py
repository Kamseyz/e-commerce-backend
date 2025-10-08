from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from product.models import Cart,CartItem,Product
from .models import PaymentItem,PaymentModel
from django.db import transaction
from rest_framework import status
from .paystack import Paystack
from django.conf import settings
import logging
from rest_framework.decorators import api_view, permission_classes
from django.shortcuts import get_object_or_404


logger = logging.getLogger(__name__)

# Create your views here.

# checkout
class Checkout(APIView):
    permission_classes = [IsAuthenticated]
    
    
    @transaction.atomic
    def post(self,request):
        user=request.user
        if request.method != 'POST':
            return Response({"details":False, "message":"Method is not allowed"},status=status.HTTP_400_BAD_REQUEST)
        
        try:
            cart=Cart.objects.get(user=user)
        except Cart.DoesNotExist:
            return Response({"details":False, "message":"Cart not found"}, status=status.HTTP_404_NOT_FOUND)

        
        cart_items = CartItem.objects.filter(cart=cart)
        if not cart_items.exists():
            return Response({"details":False, "message":"Your cart is empty"}, status=status.HTTP_400_BAD_REQUEST) 
        
        #calculate the total 
        total = sum(item.product.product_price * item.quantity for item in cart_items) 
        
        #create payment
        payment = PaymentModel.objects.create(user=user, total=total)
        
        for item in cart_items:
            PaymentItem.objects.create(
                payment=payment,
                product=item.product,
                quantity=item.quantity
            )

        
        #intialize the payment 
        try:
            servies = Paystack()
            result=servies.initialize_paystack(
                email=user.email,
                amount=total,
                reference=str(payment.reference),
                callback_url=settings.FRONTEND_URL,
            )
            
            if result['status']:
                paystack_ref = result["data"]["data"]["reference"] 
                payment.paystack_reference = paystack_ref
                payment.status = "pending"
                payment.save()
                
                return Response({
                    "details":True,
                    "message":"Payment Initialized",
                    'data':{
                            'reference': paystack_ref,
                            'authorization_url': result['data']['data']['authorization_url'],
                            'access_code': result['data']['data'].get('access_code')
                        }
                },status=status.HTTP_200_OK)
                   
            else:
                payment.status = "failed"
                payment.save()
                return Response({
                    "details":False,
                    "message":"Payment Initiailization failed",
                    "data":result,
                    
                },status=status.HTTP_400_BAD_REQUEST)
                
                
        except Exception as e:
            logger.error(f"Payment Initialized error {e}", exc_info=True)
            payment.status = "failed"
            payment.save()
            return Response({
                "details":False,
                "message":f"An internal error {e} occured"
            },status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
            
            
            
                      


#verify payment
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def verify_checkout(request,reference):  
    try:
        payment=get_object_or_404(PaymentModel,user=request.user, reference=reference)
        service = Paystack()
        result = service.verify_payment(reference)
        
        if not result.get("status"):
            return Response({"details":False, "message":"Unable to verify payment"}, status=status.HTTP_400_BAD_REQUEST)
        
        paystack_data = result.get("data", {}).get("data", {})
        pay_staus=paystack_data.get('status')
        
        if pay_staus == "success":
            payment.status = "success"
            payment.paystack_reference = paystack_data.get("reference")
            payment.save()
            
            # Deduct stock after successful payment
            for item in payment.items.all():
                item.deduct_stock()
                
            return Response({"details":True, "message":"Payment was verified successfully"}, status=status.HTTP_200_OK)
        
        else:
            payment.status = "failed"
            payment.save()
            return Response({"detials":False, "message":"Unable to verify payment"}, status=status.HTTP_400_BAD_REQUEST)
            
                
    except PaymentModel.DoesNotExist:
        logger.error("Checkout doesn't exist")
        return Response({
            "details":False,
            "message":"Checkout doesnt exist"
        },status=status.HTTP_404_NOT_FOUND)
        
        
    except Exception as e:
        logger.error(f"An error {e} occurred while verifying the checkout")
        return Response({
            "details":False,
            "message":f"An error {e} occurred while trying to verify the payment"
        }, status=status.HTTP_400_BAD_REQUEST)