from django import forms
from .models import Mailing, Client, Message


class MailingForm(forms.ModelForm):
    class Meta:
        model = Mailing
        fields = ['start_sending', 'end_sending', 'status', 'is_active', 'message', 'client']

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super(MailingForm, self).__init__(*args, **kwargs)

        if self.user:
            self.fields['message'].queryset = Message.objects.filter(owner=self.user)
            self.fields['client'].queryset = Client.objects.filter(owner=self.user)


class ClientForm(forms.ModelForm):
    class Meta:
        model = Client
        fields = "__all__"
        exclude = ('owner',)


class MessageForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = ['title', 'letter_body']