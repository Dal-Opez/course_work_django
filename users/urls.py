from django.urls import path
from users.apps import UsersConfig
from users.views import RegisterView, email_verification, PasswordRecoveryView
from django.contrib.auth.views import LoginView, LogoutView

app_name = UsersConfig.name

urlpatterns = [
    path("register/", RegisterView.as_view(), name="register"),
    path("login/", LoginView.as_view(template_name="users/login.html", next_page="mailing:home_page"),name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("email-confirm/<str:token>/", email_verification, name="email-confirm"),
    path("password-recovery/", PasswordRecoveryView.as_view(), name="password_recovery"),
]

