from rest_framework import viewsets
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticatedOrReadOnly,IsAuthenticated
from rest_framework.pagination import PageNumberPagination
from .models import Product,Cart,CartItem,OrderItem,Order
from .serializer import ProductSerializer,SearchProductSerializer,CartItemSerializer,CartSerializer,OrderSerializer
from rest_framework import filters


# custom pagination for the frontpage
class CustomPagination(PageNumberPagination):
    page_size = 5
    page_size_query_param = 'page_size'




# product view
class ProductView(viewsets.ModelViewSet):
    queryset=Product.objects.all()
    serializer_class=ProductSerializer
    permission_classes=[IsAuthenticatedOrReadOnly]
    pagination_class=CustomPagination



#search product 
class SearchProductView(APIView):
    def get(self,request):
        query=request.query_params.get("q")
        if not query:
            return Response({"details":"Search query (q) is required"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            products = Product.objects.filter(product_name__icontains=query)
            if products.exists():
                serializer= ProductSerializer(products,many=True)
                return Response(serializer.data, status=status.HTTP_200_OK)
            else:
                return Response({'details':"Product not found"}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"details":f"An error {e} occurred while fetching data from the Api"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



#carts item 
class CartItemView(viewsets.ModelViewSet):
    serializer_class=CartItemSerializer
    permission_classes=[IsAuthenticatedOrReadOnly]
    
    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False) or self.request.user.is_anonymous:
            return CartItem.objects.none()
        return CartItem.objects.filter(cart__user=self.request.user)
    
    def perform_create(self, serializer):
        cart, _=Cart.objects.get_or_create(user=self.request.user)
        serializer.save(cart=cart)



#cart(all items) 
class CartView(viewsets.ModelViewSet):
    serializer_class=CartSerializer
    permission_classes=[IsAuthenticated]
    
    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False) or self.request.user.is_anonymous:
            return Cart.objects.none()
        return Cart.objects.filter(user=self.request.user)




#orders
class OrdersView(viewsets.ModelViewSet):
    serializer_class=OrderSerializer
    permission_classes=[IsAuthenticated]
    
    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False) or self.request.user.is_anonymous:
            return Order.objects.none()
        return Order.objects.filter(user=self.request.user)