from django.core.exceptions import PermissionDenied
from django.shortcuts import render, get_object_or_404, redirect
from django.views import View
from django.views.generic import TemplateView, ListView, CreateView, UpdateView, DetailView, DeleteView
from django.urls import reverse_lazy
from django.contrib import messages
from mailing.forms import MailingForm, ClientForm, MessageForm
from mailing.models import Mailing, Client, Message, MailingAttempt
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils.decorators import method_decorator
from mailing.services import send_mailing
from django.views.decorators.cache import cache_page
from django.core.cache import cache

# Create your views here.
class HomePageView(TemplateView):
    template_name = 'mailing/home_page.html'

    @method_decorator(cache_page(60 * 5))
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['mailing_count'] = Mailing.objects.count()
        context['active_mailing_count'] = Mailing.objects.filter(is_active=True).count()
        context['client_count'] = Client.objects.count()
        context['is_manager'] = self.request.user.has_perm('mailing.view_all_mailings')
        return context


class MailingListView(LoginRequiredMixin, ListView):
    model = Mailing
    template_name = "mailing/mailing_list.html"

    def get_queryset(self):
        if self.request.user.has_perm('mailing.view_all_mailings'):
            queryset = cache.get('manager_mailing_list_queryset')
            if not queryset:
                queryset = Mailing.objects.all()
                cache.set('manager_mailing_list_queryset', queryset, 60 * 5)
            return queryset
        queryset = cache.get('mailing_list_queryset')
        if not queryset:
            queryset = Mailing.objects.filter(owner=self.request.user)
            cache.set('manager_mailing_list_queryset', queryset, 60 * 5)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_manager'] = self.request.user.has_perm('mailing.view_all_mailings')
        return context

class MailingCreateView(LoginRequiredMixin, CreateView):
    model = Mailing
    form_class = MailingForm
    template_name = 'mailing/mailing_form.html'
    success_url = reverse_lazy("mailing:mailing_list")

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        mailing = form.save(commit=False)
        mailing.owner = self.request.user
        mailing.save()
        form.save_m2m()
        return super().form_valid(form)


class MailingUpdateView(LoginRequiredMixin, UpdateView):
    model = Mailing
    form_class = MailingForm
    template_name = 'mailing/mailing_form.html'
    success_url = reverse_lazy("mailing:mailing_list")

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def dispatch(self, request, *args, **kwargs):
        obj = self.get_object()
        if obj.owner != self.request.user:
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)


class MailingDetailView(DetailView):
    model = Mailing
    template_name = 'mailing/mailing_detail.html'
    context_object_name = 'mailing'


class MailingDeleteView(LoginRequiredMixin, DeleteView):
    model = Mailing
    template_name = 'mailing/mailing_confirm_delete.html'
    success_url = reverse_lazy('mailing:mailing_list')

    def dispatch(self, request, *args, **kwargs):
        obj = self.get_object()
        if obj.owner != request.user:
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)


class ClientListView(LoginRequiredMixin, ListView):
    model = Client
    template_name = 'mailing/client_list.html'  # явное указание шаблона
    context_object_name = 'client_list'  # для ясности (необязательно)

    def get_queryset(self):
        if self.request.user.has_perm('mailing.view_all_clients'):
            return Client.objects.order_by('email').distinct('email')
        queryset = super().get_queryset().filter(owner=self.request.user)
        print("Клиенты пользователя:", queryset)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_manager'] = self.request.user.has_perm('mailing.view_all_mailings')
        return context


class ClientCreateView(LoginRequiredMixin, CreateView):
    model = Client
    form_class = ClientForm
    template_name = "mailing/client_form.html"
    success_url = reverse_lazy("mailing:client_list")

    def form_valid(self, form):
        if Client.objects.filter(
                email=form.cleaned_data['email'],
                owner=self.request.user
        ).exists():
            form.add_error('email', 'У вас уже есть клиент с таким email')
            return self.form_invalid(form)

        form.instance.owner = self.request.user
        return super().form_valid(form)


class ClientUpdateView(LoginRequiredMixin , UpdateView):
    model = Client
    form_class = ClientForm
    success_url = reverse_lazy("mailing:client_list")


class ClientDetailView(LoginRequiredMixin, DetailView):
    model = Client


class ClientDeleteView(LoginRequiredMixin , DeleteView):
    model = Client
    template_name = "mailing/client_confirm_delete.html"
    success_url = reverse_lazy("mailing:client_list")


class MessageListView(LoginRequiredMixin, ListView):
    model = Message
    template_name = 'mailing/message_list.html'
    context_object_name = 'message_list'

    def get_queryset(self):
        return Message.objects.filter(owner=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_manager'] = self.request.user.has_perm('mailing.view_all_mailings')
        return context


class MessageCreateView(LoginRequiredMixin, CreateView):
    model = Message
    form_class = MessageForm
    template_name = 'mailing/message_form.html'
    success_url = reverse_lazy('mailing:message_list')  # Важно!

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)


class MessageUpdateView(LoginRequiredMixin, UpdateView):
    model = Message
    form_class = MessageForm
    template_name = 'mailing/message_form.html'
    success_url = reverse_lazy('mailing:message_list')

    def dispatch(self, request, *args, **kwargs):
        obj = self.get_object()
        if obj.owner != request.user:
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)


class MessageDetailView(LoginRequiredMixin, DetailView):
    model = Message
    template_name = 'mailing/message_detail.html'

    def dispatch(self, request, *args, **kwargs):
        obj = self.get_object()
        if obj.owner != request.user:
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)


class MessageDeleteView(LoginRequiredMixin, DeleteView):
    model = Message
    template_name = 'mailing/message_confirm_delete.html'
    success_url = reverse_lazy('mailing:message_list')

    def dispatch(self, request, *args, **kwargs):
        obj = self.get_object()
        if obj.owner != request.user:
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)


class MailingAttemptCreateView(CreateView):
    model = MailingAttempt


class MailingAttemptListView(LoginRequiredMixin, ListView):
    model = MailingAttempt
    template_name = 'mailing/mailing_attempt_list.html'
    context_object_name = 'object_list'

    def get_queryset(self):
        return MailingAttempt.objects.filter(owner=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        attempts = self.get_queryset()  # Используем уже отфильтрованный queryset
        context['total_attempts'] = attempts.count()
        context['success_count'] = attempts.filter(status='Успешно').count()
        context['failure_count'] = attempts.filter(status='Не успешно').count()
        return context


class MailingToggleView(View):
    def post(self, request, pk):
        mailing = get_object_or_404(Mailing, pk=pk)
        mailing.is_active = not mailing.is_active
        mailing.save()
        messages.success(request, f'Рассылка #{mailing.id} {"отключена" if not mailing.is_active else "включена"}')
        return redirect('mailing:mailing_list')


def start_mailing(request, pk):
    if request.method == 'POST':
        mailing = get_object_or_404(Mailing, pk=pk)
        try:
            send_mailing(mailing)
            messages.success(request, f'Рассылка #{mailing.id} запущена! Проверьте попытки отправки.')
        except Exception as e:
            messages.error(request, f'Ошибка: {str(e)}')

    return redirect('mailing:mailing_list')