import secrets
from django.views.generic import CreateView
from users.forms import UserRegisterForm
from django.urls import reverse_lazy, reverse
from config.settings import EMAIL_HOST_USER
from django.core.mail import send_mail
from .models import User
from django.shortcuts import get_object_or_404, redirect
from django.http import HttpResponse

# Create your views here.
class RegisterView(CreateView):
    template_name = 'users/register.html'
    form_class = UserRegisterForm
    success_url = reverse_lazy('mailing:home_page')

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

def email_verification(request, token):
    user = get_object_or_404(User, token=token)
    user.is_active = True
    user.save()
    return redirect(reverse('users:login'))
