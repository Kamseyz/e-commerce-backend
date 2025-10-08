from django.urls import path
from .views import RegistrationView,LoginView, ConsumeLink, RefreshAccessToken,Logout

urlpatterns = [
    path('register/', RegistrationView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('consume-link/', ConsumeLink.as_view(), name='consumer'),
    path('refresh/', RefreshAccessToken.as_view(), name='refresh'),
    path('logout/', Logout.as_view(), name='logout'),
]
