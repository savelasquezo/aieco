from django import forms
import public.models as model

class MessagesForm(forms.ModelForm):
    class Meta:
        model = model.Messages
        fields = ['first_name', 'last_name', 'type', 'messages']