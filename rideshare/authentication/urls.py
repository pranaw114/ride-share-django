from django.urls import path
from .views import UserRegistrationViewSet, Lognin


urlpatterns = [
    path('register', UserRegistrationViewSet.as_view({'post': 'create'}), name="register" ),
    path('login', Lognin.as_view(), name='login'),
]