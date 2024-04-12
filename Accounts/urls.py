from django.urls import path
from .views import ObtainTokenView, CustomTokenRefreshView, SomeSecuredView,UserRegistrationAPIView

urlpatterns = [
    path('login/', ObtainTokenView.as_view(), name='token_obtain_pair'),
    path('register/', UserRegistrationAPIView.as_view(), name='token_obtain'),
    path('token/refresh/', CustomTokenRefreshView.as_view(), name='token_refresh'),
    path('secured/', SomeSecuredView.as_view(), name='secured_view'),
    # other paths
]