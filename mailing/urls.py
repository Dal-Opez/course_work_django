from django.urls import path
from mailing.apps import MailingConfig
from .views import HomePageView, MailingListView, MailingCreateView, MailingUpdateView, ClientListView, \
    ClientCreateView, ClientUpdateView, ClientDetailView, ClientDeleteView, MessageListView, MessageCreateView, \
    MessageUpdateView, MessageDetailView, MessageDeleteView, MailingAttemptListView, start_mailing, MailingDetailView

app_name = MailingConfig.name

urlpatterns = [
    path('', HomePageView.as_view(), name='home_page'),
    path('mailing/', MailingListView.as_view(), name='mailing_list'),
    path('mailing/create', MailingCreateView.as_view(), name='mailing_create'),
    path('mailing/update/<int:pk>/', MailingUpdateView.as_view(), name='mailing_update'),
    path('mailing/<int:pk>/', MailingDetailView.as_view(), name='mailing_detail'),
    path('mailing/<int:pk>/start/', start_mailing, name='mailing_start'),
    path('clients/', ClientListView.as_view(), name='client_list'),
    path('clients/create', ClientCreateView.as_view(), name='client_create'),
    path('clients/update/<int:pk>/', ClientUpdateView.as_view(), name='client_update'),
    path('clients/detail/<int:pk>/', ClientDetailView.as_view(), name='client_detail'),
    path('clients/delete/<int:pk>/', ClientDeleteView.as_view(), name='client_delete'),
    path('messages/', MessageListView.as_view(), name='message_list'),
    path('messages/create/', MessageCreateView.as_view(), name='message_create'),
    path('messages/update/<int:pk>/', MessageUpdateView.as_view(), name='message_update'),
    path('messages/detail/<int:pk>/', MessageDetailView.as_view(), name='message_detail'),
    path('messages/delete/<int:pk>/', MessageDeleteView.as_view(), name='message_delete'),
    path("mailing_attempt/", MailingAttemptListView.as_view(), name="mailing_attempt_list"),
]