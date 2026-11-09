from django.urls import path

from .views import UserDetailDirect, user_detail_cached

urlpatterns = [
    path("users/<int:pk>/", UserDetailDirect.as_view()),
    path("users-cached/<int:pk>/", user_detail_cached),
]
