import secrets

from django.contrib.auth.mixins import PermissionRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib.auth.views import PasswordResetConfirmView, PasswordResetView
from django.views.generic import CreateView, FormView, ListView
from users.forms import UserForgotPasswordForm, UserRegisterForm, PasswordRecoveryForm
from django.urls import reverse_lazy, reverse
from config.settings import EMAIL_HOST_USER
from django.core.mail import send_mail
from .models import User
from django.shortcuts import get_object_or_404, redirect
from django.utils.crypto import get_random_string
from django.contrib import messages



# Create your views here.
class RegisterView(CreateView):
    template_name = "users/register.html"
    form_class = UserRegisterForm
    success_url = reverse_lazy("mailing:home_page")

    def form_valid(self, form):
        user = form.save()
        user.is_active = False
        token = secrets.token_hex(16)
        user.token = token
        user.save()
        host = self.request.get_host()
        url = f"http://{host}/users/email-confirm/{token}/"
        send_mail(
            subject="Потверждение регистрации",
            message=f"Спасибо за регистрацию!Перейдите по ссылке для подтверждения почты: {url}",
            from_email=EMAIL_HOST_USER,
            recipient_list=[user.email],
        )
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_manager'] = self.request.user.has_perm('mailing.view_all_mailings')
        return context


def email_verification(request, token):
    user = get_object_or_404(User, token=token)
    user.is_active = True
    user.save()
    return redirect(reverse("users:login"))


class UserForgotPasswordView(SuccessMessageMixin, PasswordResetView):
    form_class = UserForgotPasswordForm
    template_name = "users/password_reset.html"
    success_url = reverse_lazy("users:login")
    success_message = (
        "Письмо с инструкцией по восстановлению пароля отправлено на ваш email"
    )
    subject_template_name = "users/email/password_subject_reset_mail.txt"
    email_template_name = "users/email/password_reset_mail.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Запрос на восстановление пароля"
        context['is_manager'] = self.request.user.has_perm('mailing.view_all_mailings')
        return context


class PasswordRecoveryView(FormView):
    template_name = "users/password_recovery.html"
    form_class = PasswordRecoveryForm
    success_url = reverse_lazy("users:login")

    def form_valid(self, form):
        email = form.cleaned_data["email"]
        user = User.objects.get(email=email)
        length = 12
        alphabet = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
        password = get_random_string(length, alphabet)
        user.set_password(password)
        user.save()
        send_mail(
            subject="Восстановление пароля",
            message=f"Ваш новый пароль: {password}",
            from_email=EMAIL_HOST_USER,
            recipient_list=[user.email],
            fail_silently=False,
        )
        return super().form_valid(form)


class UserListView(PermissionRequiredMixin, ListView):
    model = User
    template_name = 'users/user_list.html'
    context_object_name = 'user_list'
    permission_required = 'users.can_view_all_users'

    def get_queryset(self):
        return User.objects.all().order_by('email')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_manager'] = True
        return context


def toggle_block_user(request, pk):
    if not request.user.has_perm('users.can_block_user'):
        return redirect('users:user_list')

    user = get_object_or_404(User, pk=pk)
    user.is_blocked = not user.is_blocked
    user.save()

    messages.success(request,
                     f'Пользователь {user.email} {"разблокирован" if not user.is_blocked else "заблокирован"}')
    return redirect('users:user_list')