from django.urls import path
from .views import UserRegisterView, UserLoginView, UserDetailView


urlpatterns = [
    path("register/", UserRegisterView.as_view()),
    path("login/", UserLoginView.as_view()),
    path('detail/<str:user_id>/', UserDetailView.as_view())
]