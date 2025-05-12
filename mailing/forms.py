from django import forms
from .models import Mailing, Client, Message


class MailingForm(forms.ModelForm):
    class Meta:
        model = Mailing
        fields = '__all__'


class ClientForm(forms.ModelForm):
    class Meta:
        model = Client
        fields = "__all__"
        exclude = ('owner',)


class MessageForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = "__all__"