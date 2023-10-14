import re, os, io

from django.conf import settings
from django.urls import reverse
from django.shortcuts import redirect, render
from django.db.models.query_utils import Q
from django.template.loader import render_to_string
from django.http import HttpResponse
from django.core.mail import BadHeaderError,send_mail
from django.core.paginator import Paginator
from django.utils import timezone
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.views import View
from django.views.generic.base import TemplateView
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.forms import PasswordResetForm
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.views import LoginView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin

from xhtml2pdf import pisa
from .tools import gToken

import public.models as model
import public.forms as forms


class IndexView(TemplateView):
    template_name = 'index.html'

    def get(self, request, *args, **kwargs):
        context = super().get_context_data(**kwargs)

        try:
            arrayLegalLinks = model.Information.objects.all().order_by("id")[:2]
            context.update({
                'arrayLegalLinks':arrayLegalLinks,
            })

        except Exception as e:
            with open(os.path.join(settings.BASE_DIR, 'logs/django.log'), 'a') as f:
                arrayLegalLinks = []
                eDate = timezone.now().strftime("%Y-%m-%d %H:%M")
                f.write("Undefined arrayLegalLinks--> Date: {} Error: {}\n".format(eDate, str(e)))

        return self.render_to_response(context)


class AccountView(LoginRequiredMixin, TemplateView):
    template_name = 'admin/admin.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = forms.NotificationForm()
        return context

    def get(self, request, *args, **kwargs):
        context = super().get_context_data(**kwargs)

        try:
            arrayAnnouncements = model.Announcements.objects.filter(is_active=True).order_by("id")[:4]
            arrayNotifications = model.AccountNotification.objects.filter(account=request.user, archived=False).order_by("id")
            context.update({
                'arrayAnnouncements':arrayAnnouncements,
                'arrayNotifications':arrayNotifications,
            })

        except Exception as e:
            with open(os.path.join(settings.BASE_DIR, 'logs/django.log'), 'a') as f:
                arrayAnnouncements = []
                arrayNotifications = []
                eDate = timezone.now().strftime("%Y-%m-%d %H:%M")
                f.write("Undefined arrayNotifications/arrayAnnouncements--> Date: {} Error: {}\n".format(eDate, str(e)))

        return self.render_to_response(context)

    def post(self, request, *args, **kwargs):
        dialogID = request.POST.get('dialogID')

        try:
            dialogNotification = model.AccountNotification.objects.get(id=dialogID)
            dialogNotification.read = True if 'read' in request.POST else False
            dialogNotification.archived = True if 'archived' in request.POST else False
            dialogNotification.save()

        except Exception as e:
            with open(os.path.join(settings.BASE_DIR, 'logs/django.log'), 'a') as f:
                eDate = timezone.now().strftime("%Y-%m-%d %H:%M")
                f.write("Undefined dialogNotification/dialogNotification--> Date: {} Error: {}\n".format(eDate, str(e)))

        return redirect(reverse('admin'))


class AccountSearchView(LoginRequiredMixin, TemplateView):
    template_name = 'admin/search.html'

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated or not request.user.is_inspector:
            return redirect(reverse('admin'))

        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        nitCompany = self.request.GET.get('nitCompany')

        try:
    
            ITEMS = 7
            MAXPAGES = 10

            nitAccount = model.Account.objects.get(nit=nitCompany)
            iFiles = model.AccountFiles.objects.filter(account=nitAccount).order_by("id")[:ITEMS*MAXPAGES]
            for i in iFiles:
                if not i.file_state:
                    i.files = None
                    i.save()

            iListFiles = Paginator(iFiles,ITEMS).get_page(self.request.GET.get('page'))

            iFileFix = ITEMS - len(iFiles)%ITEMS

            if iFileFix == ITEMS and len(iFiles) != 0:
                iFileFix = 0

            context = super().get_context_data(**kwargs)
            context.update({
                'nitAccount':nitAccount,
                "iFiles": iFiles,
                'iListFiles':iListFiles,
                'FixListPage':range(0,iFileFix)
            })

            return context

        except Exception as e:
            context['nitAccount'] = None
            with open(os.path.join(settings.BASE_DIR, 'logs/django.log'), 'a') as f:
                eDate = timezone.now().strftime("%Y-%m-%d %H:%M")
                f.write("Undefined AccountSearchView/AccountSearchView--> Date: {} Error: {}\n".format(eDate, str(e)))
           

        return context

class AccountFilesView(LoginRequiredMixin, TemplateView):
    template_name = 'admin/files.html'

    def get(self, request, *args, **kwargs):

        ITEMS = 7
        MAXPAGES = 10

        accountFiles = model.AccountFiles.objects.filter(account=request.user)

        nameFile = ""

        if request.GET.get('nameFile'):
            nameFile = request.GET.get('nameFile')
            accountFiles = accountFiles.filter(filename__icontains=nameFile)

        iFiles = accountFiles.order_by("id")[:ITEMS*MAXPAGES]
        for i in iFiles:
            if not i.file_state:
                i.files = None
                i.save()

        iListFiles = Paginator(iFiles,ITEMS).get_page(request.GET.get('page'))

        iFileFix = ITEMS - len(iFiles)%ITEMS

        if iFileFix == ITEMS and len(iFiles) != 0:
            iFileFix = 0

        context = super().get_context_data(**kwargs)
        context.update({
            'nameFile': nameFile,
            "iFiles": iFiles,
            'iListFiles':iListFiles,
            'FixListPage':range(0,iFileFix)
        })

        return self.render_to_response(context)


    def post(self, request, *args, **kwargs):
        codeFile = request.POST.get('codeFile')
        codeFile = model.Files.objects.get(code=codeFile)
        try:
            iFile = model.AccountFiles.objects.get(code=codeFile,account=request.user)
            iFile.delete()

            newFileRequest = model.RequestFiles.objects.create(
                account = request.user,
                code = codeFile,
                filename = codeFile.filename,
            )
            newFileRequest.save()
            messages.success(request, '¡Solicitud Realizada!', extra_tags="title")
            
        except Exception as e:
            messages.error(request, '¡Solicitud Incompleta!', extra_tags="title")
            with open(os.path.join(settings.BASE_DIR, 'logs/django.log'), 'a') as f:
                eDate = timezone.now().strftime("%Y-%m-%d %H:%M")
                f.write("Undefined renewRequestFile--> Date: {} Error: {}\n".format(eDate, str(e)))

        return redirect(reverse('files'))


class AccountGaleryView(LoginRequiredMixin, TemplateView):
    template_name = 'admin/galery.html'

    def get(self, request, *args, **kwargs):

        ITEMS = 6
        MAXPAGES = 10

        iFiles = model.MediaFiles.objects.filter(is_active=True).order_by("id")[:ITEMS*MAXPAGES]
        iListFiles = Paginator(iFiles,ITEMS).get_page(request.GET.get('page'))

        iFileFix = ITEMS - len(iFiles)%ITEMS

        if iFileFix == ITEMS and len(iFiles) != 0:
            iFileFix = 0

        context = super().get_context_data(**kwargs)
        context.update({
            "iFiles": iFiles,
            'iListFiles':iListFiles,
            'FixListPage':range(0,iFileFix)
        })

        return self.render_to_response(context)

class AccountBillingView(LoginRequiredMixin, TemplateView):
    template_name = 'admin/billing.html'

    def get(self, request, *args, **kwargs):

        accountInvoice = model.AccountBilling.objects.filter(account=request.user).order_by("-id").first()
        accountAddons = model.AccountBillingAddons.objects.filter(billing=accountInvoice).order_by("id")

        context = super().get_context_data(**kwargs)
        context.update({
            "accountInvoice": accountInvoice,
            "accountAddons":accountAddons
        })

        return self.render_to_response(context)

class AccountHistoryView(LoginRequiredMixin, TemplateView):
    template_name = 'admin/billing-history.html'

    def get(self, request, *args, **kwargs):

        ITEMS = 7
        MAXPAGES = 10

        accountBills = model.AccountBilling.objects.filter(account=request.user).exclude(state="current")
        iFiles = accountBills.order_by("-id")[:ITEMS*MAXPAGES]
        iListFiles = Paginator(iFiles,ITEMS).get_page(request.GET.get('page'))

        iFileFix = ITEMS - len(iFiles)%ITEMS

        if iFileFix == ITEMS and len(iFiles) != 0:
            iFileFix = 0

        context = super().get_context_data(**kwargs)
        context.update({
            "iFiles": iFiles,
            'iListFiles':iListFiles,
            'FixListPage':range(0,iFileFix)
        })

        return self.render_to_response(context)



class AccountMethodsView(LoginRequiredMixin, TemplateView):
    template_name = 'admin/billing-methods.html'

    def get(self, request, *args, **kwargs):

        ITEMS = 5
        iSettings = model.Settings.objects.first()
        iMethods = model.PaymentMethods.objects.filter(settings=iSettings, is_active=True).order_by("id")[:ITEMS]

        context = super().get_context_data(**kwargs)
        context.update({
            "iMethods": iMethods,
        })

        return self.render_to_response(context)


class AccountSupportView(LoginRequiredMixin, TemplateView):
    template_name = 'admin/support.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = forms.MessagesForm()
        return context

    def post(self, request, *args, **kwargs):
        form = forms.MessagesForm(request.POST)
        if form.is_valid():
            try:
                form.save()
                messages.success(request, '¡Mensaje Enviado!', extra_tags="title")
                messages.success(request, f'¡Gracias por contactarnos, Tu solicitud ha sido recibida!', extra_tags="info")
            
            except Exception as e:

                messages.error(request, '¡Error!',extra_tags="title")
                messages.error(request, f'Lamentablemente, se produjo un error al procesar tu solicitud. Intentalo nuevamente!', extra_tags="info")
                with open(os.path.join(settings.BASE_DIR, 'logs/django.log'), 'a') as f:
                    eDate = timezone.now().strftime("%Y-%m-%d %H:%M")
                    f.write("Undefined newMessages--> Date: {} Error: {}\n".format(eDate, str(e)))

            return redirect(reverse('support'))

        return self.render_to_response({'form': form})



class AccountShopView(LoginRequiredMixin, TemplateView):
    template_name = 'admin/shop.html'

    def get(self, request, *args, **kwargs):
        ITEMS = 7
        MAXPAGES = 10

        requestFiles = model.RequestFiles.objects.filter(account=request.user).values_list('code__code', flat=True)
        accountFiles = model.AccountFiles.objects.filter(account=request.user).values_list('code__code', flat=True)

        AllFiles = model.Files.objects.filter(is_active=True)
        nameFile = ""

        if request.GET.get('nameFile'):
            nameFile = request.GET.get('nameFile')
            AllFiles = AllFiles.filter(filename__icontains=nameFile)

        iFiles = AllFiles.exclude(Q(code__in=accountFiles) | Q(code__in=requestFiles)).order_by("id")[:ITEMS * MAXPAGES]
        iListFiles = Paginator(iFiles, ITEMS).get_page(request.GET.get('page'))

        iFileFix = ITEMS - len(iFiles) % ITEMS

        if iFileFix == ITEMS and len(iFiles) != 0:
            iFileFix = 0

        context = super().get_context_data(**kwargs)
        context.update({
            'nameFile': nameFile,
            'iFiles': iFiles,
            'iListFiles': iListFiles,
            'FixListPage': range(0, iFileFix),
        })

        return self.render_to_response(context)


    def post(self, request, *args, **kwargs):
        codeFile = request.POST.get('codeFile')

        codeFile = model.Files.objects.get(code=codeFile)

        try:
            newFileRequest = model.RequestFiles.objects.create(
                account = request.user,
                code = codeFile,
                filename = codeFile.filename,
            )

            newFileRequest.save()
            messages.success(request, '¡Solicitud Realizada!', extra_tags="title")
            
        except Exception as e:
            messages.error(request, '¡Solicitud Incompleta!', extra_tags="title")
            with open(os.path.join(settings.BASE_DIR, 'logs/django.log'), 'a') as f:
                eDate = timezone.now().strftime("%Y-%m-%d %H:%M")
                f.write("Undefined NewRequestFile--> Date: {} Error: {}\n".format(eDate, str(e)))

        return redirect(reverse('shop'))


class AccountShopTicketsView(LoginRequiredMixin, TemplateView):
    template_name = 'admin/shop-tickets.html'

    def get(self, request, *args, **kwargs):

        ITEMS = 7
        MAXPAGES = 10

        requestFiles = model.RequestFiles.objects.filter(account=request.user)
        nameFile = ""

        if request.GET.get('nameFile'):
            nameFile = request.GET.get('nameFile')
            requestFiles = requestFiles.filter(filename__icontains=nameFile)

        iFiles = requestFiles.order_by("id")[:ITEMS*MAXPAGES]
        iListFiles = Paginator(iFiles,ITEMS).get_page(request.GET.get('page'))

        iFileFix = ITEMS - len(iFiles)%ITEMS

        if iFileFix == ITEMS and len(iFiles) != 0:
            iFileFix = 0

        context = super().get_context_data(**kwargs)
        context.update({
            'nameFile':nameFile,
            'iFiles': iFiles,
            'iListFiles':iListFiles,
            'FixListPage':range(0,iFileFix),
        })

        return self.render_to_response(context)


    def post(self, request, *args, **kwargs):
        idFile = request.POST.get('idFile')
        try:
            iFile = model.RequestFiles.objects.get(id=idFile,account=request.user)
            iFile.delete()
            messages.success(request, '¡Solicitud Cancelada!', extra_tags="title")
            
        except Exception as e:
            messages.error(request, '¡Solicitud Incompleta!', extra_tags="title")
            with open(os.path.join(settings.BASE_DIR, 'logs/django.log'), 'a') as f:
                eDate = timezone.now().strftime("%Y-%m-%d %H:%M")
                f.write("Undefined NewRequestFile--> Date: {} Error: {}\n".format(eDate, str(e)))

        return redirect(reverse('tickets'))



class LegalView(TemplateView):
    template_name='pages/legal.html'

    def get(self, request, *args, **kwargs):

        context = super().get_context_data(**kwargs)

        try:        
            infoLegalLink = model.Information.objects.get(url=self.kwargs.get('iURL'))
            arrayLegalLinks = model.Information.objects.all().order_by("id")[:2]

            context.update({
                'infoLegalLink':infoLegalLink,
                'arrayLegalLinks':arrayLegalLinks,
            })
        except Exception as e:
            with open(os.path.join(settings.BASE_DIR, 'logs/django.log'), 'a') as f:
                infoLegalLink = None
                arrayLegalLinks = None
                eDate = timezone.now().strftime("%Y-%m-%d %H:%M")
                f.write("Undefined infoLegalLink/arrayLegalLinks--> Date: {} Error: {}\n".format(eDate, str(e)))

        return self.render_to_response(context)


class AboutUsView(TemplateView):
    template_name='pages/about-us.html'

    def get(self, request, *args, **kwargs):

        context = super().get_context_data(**kwargs)

        try:        
            arrayLegalLinks = model.Information.objects.all().order_by("id")[:2]
            context.update({
                'arrayLegalLinks':arrayLegalLinks,
            })
        except Exception as e:
            with open(os.path.join(settings.BASE_DIR, 'logs/django.log'), 'a') as f:
                arrayLegalLinks = None
                eDate = timezone.now().strftime("%Y-%m-%d %H:%M")
                f.write("Undefined arrayLegalLinks--> Date: {} Error: {}\n".format(eDate, str(e)))

        return self.render_to_response(context)

class SingupView(UserPassesTestMixin, TemplateView):
    template_name = 'registration/singup.html'

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
            messages.error(request, '¡Registro Incompleto!',extra_tags="title")
            messages.error(request, f'El Nombre de Usuario no es Valido', extra_tags="info")
            return redirect(reverse('Singup'))

        if model.Account.objects.filter(username=iUsername):
            messages.error(request, '¡Registro Incompleto!',extra_tags="title")
            messages.error(request, f'El Nombre de Usuario no esta Disponible', extra_tags="info")
            return redirect(reverse('Singup'))

        if model.Account.objects.filter(email=iEmail):
            messages.error(request, '¡Registro Incompleto!',extra_tags="title")
            messages.error(request, f'El Email no esta Disponible', extra_tags="info")
            return redirect(reverse('Singup'))

        request.session['django_messages'] = []

        try:
            nUser = model.Account.objects.create(
                username=iUsername,
                full_name=iFullName,
                email=iEmail
            )

            nUser.set_password(iPass)
            nUser.save()

            login(request, nUser)

            messages.success(request, '¡Registro Exitoso!', extra_tags="title")
            messages.success(request, f'Hemos enviado un Email para verificar su cuenta', extra_tags="info")

            try:
                cUser = model.Account.objects.get(username=iUsername)

                subject = "Activacion - Usuario"
                email_template_name = "email/email_confirm.html"
                c = {
                    'username': iUsername,
                    "uid": urlsafe_base64_encode(force_bytes(cUser.pk)),
                    "user": cUser,
                    'token': gToken.make_token(cUser),
                    'site_name': 'aieco',
                    'protocol': 'https',
                    'domain': '127.0.0.1:8000',
                }
                email = render_to_string(email_template_name, c)
                try:
                    send_mail(subject, message=None, from_email='noreply@aieco.com',
                              recipient_list=[iEmail], fail_silently=False, html_message=email)
                except BadHeaderError:
                    with open(os.path.join(settings.BASE_DIR, 'logs/email_err.txt'), 'a') as f:
                        eDate = timezone.now().strftime("%Y-%m-%d %H:%M")
                        f.write(
                            "EmailError {} SingupEmail--> Error: {}\n".format(eDate, str(e)))
                    return HttpResponse('InvalidHeader-Found')

            except Exception as e:
                with open(os.path.join(settings.BASE_DIR, 'logs/email_err.txt'), 'a') as f:
                    eDate = timezone.now().strftime("%Y-%m-%d %H:%M")
                    f.write(
                        "EmailError {} SingupConfig--> Error: {}\n".format(eDate, str(e)))

        except Exception as e:
            messages.error(request, '¡Registro Incompleto!',
                           extra_tags="title")
            messages.error(
                request, f'Ha ocurrido un error durante el registro', extra_tags="info")

        return redirect(reverse('singup'))


class iLoginView(UserPassesTestMixin, LoginView):
    template_name = 'registration/login.html'

    def test_func(self):
        return not self.request.user.is_authenticated

    def handle_no_permission(self):
        return redirect(reverse('index'))

    def form_invalid(self, form):
        messages.error(
            self.request, 'Usuario/Contraseña Incorrectos', extra_tags="title")
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
                    subject = "Solicitud - Restablecer Contraseña"
                    email_template_name = "email/password_reset_email.html"
                    c = {
                        'username': user.username,
                        "uid": urlsafe_base64_encode(force_bytes(user.pk)),
                        "user": user,
                        'token': default_token_generator.make_token(user),
                        'site_name': 'Aieco',
                        'protocol': 'https',
                        'domain': '127.0.0.1:8000',
                    }
                    email = render_to_string(email_template_name, c)
                    try:
                        send_mail(subject, message=None, from_email='noreply@aieco.com',
                                  recipient_list=[user.email], fail_silently=False, html_message=email)
                    except BadHeaderError:
                        with open(os.path.join(settings.BASE_DIR, 'logs/email_err.txt'), 'a') as f:
                            eDate = timezone.now().strftime("%Y-%m-%d %H:%M")
                            f.write(
                                "EmailError {} PasswordResetEmail--> Error: BadHeaderError\n".format(eDate))
                        return HttpResponse('InvalidHeader-Found')

                    return redirect("/accounts/password_reset/done/")

    password_reset_form = PasswordResetForm()
    return render(request=request, template_name="registration/password/password_reset.html", context={"password_reset_form": password_reset_form})


class MakePDFView(View):
    def get(self, request):
        template = 'admin/billing-pdf.html'
        context = {'user': request.user}

        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="archivo.pdf"'

        buffer = io.BytesIO()
        pdf = pisa.pisaDocument(io.BytesIO(render(request, template, context).content), buffer)
        
        if not pdf.err:
            response.write(buffer.getvalue())
            buffer.close()
            return response
        
        return HttpResponse('Invalid File!', content_type='text/plain')




def ComingSoonView(request):
    return render(request, 'admin/billing-pdf.html')