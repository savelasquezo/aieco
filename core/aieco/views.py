import re

from django.utils import timezone
from django.views.generic.base import TemplateView

from django.shortcuts import redirect, render
from django.urls import reverse

from django.contrib import messages
from django.contrib.auth.mixins import UserPassesTestMixin

from django.contrib.auth.forms import PasswordResetForm
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_bytes, force_str
from django.db.models.query_utils import Q
from django.http import HttpResponse
from django.core.mail import send_mail, BadHeaderError
from django.template.loader import render_to_string
from django.contrib.auth.views import LoginView
from django.contrib.auth import login

import aieco.models as model

from .tools import gToken

class IndexView(TemplateView):
    template_name='aieco/index.html'

class SingupView(UserPassesTestMixin, TemplateView):
    template_name='aieco/registration/singup.html'

    def test_func(self):
        return not self.request.user.is_authenticated

    def handle_no_permission(self):
        return redirect(reverse('Index'))

    def post(self, request, *args, **kwargs):
        
        iUsername = request.POST['username']
        iPass = request.POST['password']
        iFullName = request.POST['name']
        iEmail = request.POST['email']

        if not re.match(r'^[a-zA-Z0-9]+$', iUsername):
            messages.error(request, '┬íRegistro Incompleto!', extra_tags="title")
            messages.error(request, f'El Nombre de Usuario no es Valido', extra_tags="info") 
            return redirect(reverse('Singup'))

        if model.Account.objects.filter(username=iUsername):
            messages.error(request, '┬íRegistro Incompleto!', extra_tags="title")
            messages.error(request, f'El Nombre de Usuario no esta Disponible', extra_tags="info") 
            return redirect(reverse('Singup'))

        if model.Account.objects.filter(email=iEmail):
            messages.error(request, '┬íRegistro Incompleto!', extra_tags="title")
            messages.error(request, f'El Email no esta Disponible', extra_tags="info") 
            return redirect(reverse('Singup'))
        
        request.session['django_messages'] = []

        try:
            nUser = model.Account.objects.create(
                username = iUsername,
                full_name = iFullName,
                email = iEmail
            )
            
            nUser.set_password(iPass)
            nUser.save()

            login(request, nUser)
            
            messages.success(request, '┬íRegistro Exitoso!', extra_tags="title")
            messages.success(request, f'Hemos enviado un Email para verificar su cuenta', extra_tags="info")
            
            try:
                cUser = model.Account.objects.get(username=iUsername)
                
                subject = "Activacion - Usuario"
                email_template_name = "registration/email_confirm.txt"
                c = {
                'username': iUsername,
                "uid": urlsafe_base64_encode(force_bytes(cUser.pk)),
                "user": cUser,
                'token': gToken.make_token(cUser),
                'site_name': 'aieco',
                'protocol': 'https',# http
                'domain':'Dominio',# 127.0.0.1:8000
                }
                email = render_to_string(email_template_name, c)
                try:
                    send_mail(subject, email, 'noreply@aieco.com.co' , [iEmail], fail_silently=False)
                except BadHeaderError:
                    with open("/home/apps/aieco/core/logs/email_err.txt", "a") as f:
                        eDate = timezone.now().strftime("%Y-%m-%d %H:%M")
                        f.write("EmailError SingupEmail--> {} Error: {}\n".format(eDate, str(e)))
                    return HttpResponse('Invalid Header Found')
                
            except Exception as e:
                    with open("/home/apps/aieco/core/logs/email_err.txt", "a") as f:
                        eDate = timezone.now().strftime("%Y-%m-%d %H:%M")
                        f.write("EmailError SingupConfig--> {} Error: {}\n".format(eDate, str(e)))

        except Exception as e:
            messages.error(request, '┬íRegistro Incompleto!', extra_tags="title")
            messages.error(request, f'Ha ocurrido un error durante el registro', extra_tags="info")         
        
        return redirect(reverse('Singup'))


class UserLoginView(UserPassesTestMixin, LoginView):
    template_name='aieco/registration/login.html'

    def test_func(self):
        return not self.request.user.is_authenticated

    def handle_no_permission(self):
        return redirect(reverse('Index'))

    def form_invalid(self, form):
        messages.error(self.request, 'Usuario/Contrase├▒a Incorrectos', extra_tags="title")
        messages.error(self.request, 'Intentelo Nuevamente', extra_tags="info")
        return super().form_invalid(form)

def PasswordResetRequestView(request):
	if request.method == "POST":
		password_reset_form = PasswordResetForm(request.POST)
		if password_reset_form.is_valid():
			data = password_reset_form.cleaned_data['email']
			associated_users = model.Account.objects.filter(Q(email=data))
			if associated_users.exists():
				for user in associated_users:
					subject = "Solicitud - Restablecer Contrase├▒a"
					email_template_name = "password/password_reset_email.txt"
					c = {
                    'username': user.username,
					"uid": urlsafe_base64_encode(force_bytes(user.pk)),
					"user": user,
					'token': default_token_generator.make_token(user),
     				'site_name': 'VRT-Fund',
					'protocol': 'https',# http
                    'domain':'aieco.com',# 127.0.0.1:8000
					}
					email = render_to_string(email_template_name, c)
					try:
						send_mail(subject, email, 'noreply@aieco.com.co' , [user.email], fail_silently=False)
					except BadHeaderError:
						return HttpResponse('Invalid Header Found')
					return redirect ("/accounts/password_reset/done/")
 
	password_reset_form = PasswordResetForm()
	return render(request=request, template_name="registration/password/password_reset.html", context={"password_reset_form":password_reset_form})



def EmailConfirmView(request, uidb64, token):
   
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            nUser = model.Account.objects.get(pk=uid)

            if nUser and gToken.check_token(nUser, token):
                nUser.is_active = True
                nUser.save()

                return render(request, 'registration/email/email_confirm.html', {"user": nUser})
            
        except Exception as e:
            nUser = None
            with open("/home/apps/aieco/core/logs/email_err.txt", "a") as f:
                eDate = timezone.now().strftime("%Y-%m-%d %H:%M")
                f.write("EmailConfirm--> {} Error: {}\n".format(eDate, str(e)))

        return render(request, 'registration/email/email_confirm-failed.html', {"user": nUser})

def ComingSoonView(request):
    return render(request, '000.html')