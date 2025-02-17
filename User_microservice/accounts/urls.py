from django.urls import path
from .views import UserRegisterView, UserLoginView, UserDetailView, AuthMicroserviceView, UserGetOrdersView

app_name = "user"

urlpatterns = [
    path("register/", UserRegisterView.as_view()),
    path("login/", UserLoginView.as_view()),
    path('detail/<str:user_id>/', UserDetailView.as_view()),
    path('auth/', AuthMicroserviceView.as_view()),
    path('order-list/<user_id>', UserGetOrdersView.as_view())
]