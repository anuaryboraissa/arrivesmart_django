from django.urls import path
from .views import ObtainTokenView, CustomTokenRefreshView, SomeSecuredView,UserManagementAPIView,BusManagementView,PassengerManagementView,PostManagementView,RouteManagementView,UploadImageApiView,TicketManagementView,UserTicketNotificationApi,NotificationApi

urlpatterns = [
    path('login/', ObtainTokenView.as_view(), name='token_obtain_pair'),
    path('register/', UserManagementAPIView.as_view(), name='token_obtain'),
    path('token/refresh/', CustomTokenRefreshView.as_view(), name='token_refresh'),
    path('secured/', SomeSecuredView.as_view(), name='secured_view'),
    path('passenger/', PassengerManagementView.as_view(), name='passenger_view'),
    path('upload/', UploadImageApiView.as_view(), name='upload_view'),
    path('bus/', BusManagementView.as_view(), name='bus_view'),
    path('ticket/', TicketManagementView.as_view(), name='ticket_view'),
    path('post/', PostManagementView.as_view(), name='post_view'),
    path('route/', RouteManagementView.as_view(), name='route_view'),
    path('notification/', NotificationApi.as_view(), name='notification_view'),
    path('notification_ticket/', UserTicketNotificationApi.as_view(), name='notification_ticket_view')
]