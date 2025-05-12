from django.urls import path
from mailing.apps import MailingConfig
from .views import HomePageView, MailingListView, MailingCreateView, MailingUpdateView


app_name = MailingConfig.name

urlpatterns = [
    path('', HomePageView.as_view(), name='home_page'),
    path("mailing/", MailingListView.as_view(), name="mailing_list"),
    path("mailing/create", MailingCreateView.as_view(), name="mailing_create"),
    path("mailing/update/<int:pk>//", MailingUpdateView.as_view(), name="mailing_update"),
]