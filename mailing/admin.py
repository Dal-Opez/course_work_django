from django.contrib import admin
from mailing.models import Client


# Register your models here.
@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ('id', 'email', 'full_name',)
    list_filter = ('id',)