from django.urls import path
from .views import ClientDetailDirect, client_detail_cached

urlpatterns = [
    path("clients/<int:pk>/", ClientDetailDirect.as_view()),
    path("clients-cached/<int:pk>/", client_detail_cached),
]
