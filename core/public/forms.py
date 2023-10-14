from django import forms
import public.models as model

class NotificationForm(forms.ModelForm):
    class Meta:
        model = model.AccountNotification
        fields = ['read', 'archived']

class MessagesForm(forms.ModelForm):
    class Meta:
        model = model.Messages
        fields = ['account','email','first_name', 'last_name', 'type', 'messages']

