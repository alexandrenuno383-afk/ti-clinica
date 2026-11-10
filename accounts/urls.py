from django.urls import path

from .views import UserDetailCached, UserDetailDirect

urlpatterns = [
    path("users/<int:pk>/", UserDetailDirect.as_view()),
    path("users-cached/<int:pk>/", UserDetailCached.as_view()),
]
