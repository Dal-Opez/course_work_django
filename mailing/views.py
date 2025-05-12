from django.shortcuts import render
from django.views.generic import TemplateView, ListView, CreateView, UpdateView
from django.urls import reverse_lazy

from mailing.forms import MailingForm
from mailing.models import Mailing


# Create your views here.
class HomePageView(TemplateView):
    template_name = 'mailing/home_page.html'


class MailingListView(ListView):
    model = Mailing
    template_name = "mailing/mailing_list.html"


class MailingCreateView(CreateView):
    model = Mailing
    form_class = MailingForm
    template_name = 'mailing/mailing_form.html'
    success_url = reverse_lazy("mailing:mailing_list")


class MailingUpdateView(UpdateView):
    model = Mailing
    form_class = MailingForm
    success_url = reverse_lazy("mailing:mailing_list")