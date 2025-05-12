from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import TemplateView, ListView, CreateView, UpdateView, DetailView, DeleteView
from django.urls import reverse_lazy
from django.contrib import messages
from mailing.forms import MailingForm, ClientForm, MessageForm
from mailing.models import Mailing, Client, Message, MailingAttempt
from django.contrib.auth.mixins import LoginRequiredMixin

from mailing.services import send_mailing


# Create your views here.
class HomePageView(TemplateView):
    template_name = 'mailing/home_page.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['mailing_count'] = Mailing.objects.count()
        context['active_mailing_count'] = Mailing.objects.filter(is_active=True).count()
        context['client_count'] = Client.objects.count()
        return context


class MailingListView(ListView):
    model = Mailing
    template_name = "mailing/mailing_list.html"


class MailingCreateView(LoginRequiredMixin, CreateView):
    model = Mailing
    form_class = MailingForm
    template_name = 'mailing/mailing_form.html'
    success_url = reverse_lazy("mailing:mailing_list")

    def form_valid(self, form):
        client = form.save()
        client.owner = self.request.user
        client.save()
        return super().form_valid(form)


class MailingUpdateView(UpdateView):
    model = Mailing
    form_class = MailingForm
    success_url = reverse_lazy("mailing:mailing_list")


class MailingDetailView(DetailView):
    model = Mailing
    template_name = 'mailing/mailing_detail.html'
    context_object_name = 'mailing'


class ClientListView(ListView):
    model = Client


class ClientCreateView(CreateView):
    model = Client
    form_class = ClientForm
    template_name = "mailing/client_form.html"
    success_url = reverse_lazy("mailing:client_list")


class ClientUpdateView(UpdateView):
    model = Client
    form_class = ClientForm
    success_url = reverse_lazy("mailing:client_list")


class ClientDetailView(DetailView):
    model = Client


class ClientDeleteView(DeleteView):
    model = Client
    template_name = "mailing/client_confirm_delete.html"
    success_url = reverse_lazy("mailing:client_list")


class MessageListView(ListView):
    model = Message
    form_class = MessageForm
    template_name = 'mailing/message_list.html'


class MessageCreateView(CreateView):
    model = Message
    form_class = MessageForm
    template_name = "mailing/message_form.html"
    success_url = reverse_lazy("mailing:message_list")


class MessageUpdateView(UpdateView):
    model = Message
    form_class = MessageForm
    success_url = reverse_lazy("mailing:message_list")


class MessageDetailView(DetailView):
    model = Message


class MessageDeleteView(DeleteView):
    model = Message
    template_name = "mailing/message_confirm_delete.html"
    success_url = reverse_lazy("mailing:message_list")


class MailingAttemptCreateView(CreateView):
    model = MailingAttempt


class MailingAttemptListView(ListView):
    model = MailingAttempt
    template_name = 'mailing/mailing_attempt_list.html'
    context_object_name = 'object_list'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        attempts = MailingAttempt.objects.all()
        context['total_attempts'] = attempts.count()
        context['success_count'] = attempts.filter(status='Успешно').count()
        context['failure_count'] = attempts.filter(status='Не успешно').count()
        return context


def start_mailing(request, pk):
    if request.method == 'POST':
        mailing = get_object_or_404(Mailing, pk=pk)
        try:
            send_mailing(mailing)
            messages.success(request, f'Рассылка #{mailing.id} запущена! Проверьте попытки отправки.')
        except Exception as e:
            messages.error(request, f'Ошибка: {str(e)}')

    return redirect('mailing:mailing_list')