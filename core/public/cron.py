import os
from dateutil.relativedelta import relativedelta

from django.conf import settings
from django.db.models import Sum
from django_cron import CronJobBase, Schedule
from django.utils import timezone
from django.template.loader import render_to_string
from django.core.mail import send_mail

from .models import Account, AccountFiles, Settings, AccountBilling, AccountBillingAddons, AccountNotification

class AiecoCronJob(CronJobBase):
    RUN_EVERY_MINS = 1

    schedule = Schedule(run_every_mins=RUN_EVERY_MINS)
    code = 'public.AiecoCronJob'
    
    #crontab -e
    #* * * * * /home/savelasquezo/savelasquezo/aieco/venv/bin/python /home/savelasquezo/savelasquezo/aieco/core/manage.py runcrons
    def do(self):

        utcToday = timezone.now()
        datToday = utcToday.astimezone(timezone.get_current_timezone())

        Accounts = Account.objects.filter(is_active=True).order_by("id")

        for i in Accounts:

            accountFiles = AccountFiles.objects.filter(account=i, file_state=True).order_by("id")
            for j in accountFiles:

                if j.is_forever:
                    break 

                dateValidity = j.file_validity

                mValidity = (datToday - timezone.timedelta(days=30)).date()
                wValidity = (datToday - timezone.timedelta(days=7)).date()
                dValidity = (datToday - timezone.timedelta(days=1)).date()

                if dateValidity < datToday.date():
                    try:
                        infoMessage = f"El Documento {j.code}-{j.filename} está próximo a vencer!\n Fecha de Vencimiento: {dateValidity}\n\n ¡Comunícate con Nuestro servicio de soporte para agendar la renovación!"
                        newNotification = AccountNotification.objects.create(
                            account=i,
                            subject="Advertencia de Vencimiento",
                            message=infoMessage,
                        )

                        j.file_state = False
                        j.save()

                    except Exception as e:
                        with open(os.path.join(settings.BASE_DIR, 'logs/cron.log'), 'a') as f:
                            f.write("EmailError {} AccountNotification--> Error: {}\n".format(datToday.strftime("%Y-%m-%d %H:%M"), str(e)))
                
                if dateValidity == mValidity or dateValidity == wValidity or dateValidity == dValidity:
                    try:

                        settings = Settings.objects.first()
                        days = dateValidity

                        subject = "Alerta - Vencimiento de Documentacion"
                        email_template_name = "email/alert.txt"
                        c = {
                            'username': i.username,
                            'file': j.filename,
                            'days' :days,
                            'id_file': j.id,
                            'date_validity': j.file_validity,
                            'site_name': 'Aieco',
                            'email_site': settings.email,
                            'idx': settings.idx,
                            'phone_site': settings.phone,
                            'protocol': 'https',
                            'domain': 'aieco.com.co',
                        }
                        email = render_to_string(email_template_name, c)
                        try:
                            send_mail(subject, message=None, from_email='noreply@aieco.com',
                                    recipient_list=[i.email,"info@aieco.com.co"], fail_silently=False, html_message=email)
                        except Exception as e:
                            with open(os.path.join(settings.BASE_DIR, 'logs/cron.log'), 'a') as f:
                                f.write("EmailError {} EmailSendAlert--> Error: {}\n".format(datToday.strftime("%Y-%m-%d %H:%M"), str(e)))

                    except Exception as e:
                            with open(os.path.join(settings.BASE_DIR, 'logs/cron.log'), 'a') as f:
                                f.write("EmailError {} AlertValidity--> Error: {}\n".format(datToday.strftime("%Y-%m-%d %H:%M"), str(e)))

            if i.due_date == datToday.date():

                dueBilling = datToday + relativedelta(months=1)
                extBilling = datToday + relativedelta(months=1, days=5)

                i.last_due_date = utcToday
                i.payment_date = dueBilling
                i.due_date = extBilling
                i.save()

                accounBill = AccountBilling.objects.filter(account=i).order_by('-id').first()
                if accounBill.state != "paid":
                    accounBill.date_succes = timezone.now()
                    accounBill.state = "overdue"
                    accounBill.others = 0
                    accounBill.save()

                debtAccount = accounBill.payment if accounBill.state != "paid" else 0

                try:
                    newBill = AccountBilling.objects.create(
                        account=i,
                        company_id=i.company_id,
                        company= i.company,
                        debt = debtAccount,
                        payment = i.payment,
                        date_invoice = utcToday,
                        date_payment = dueBilling,
                        date_dolimit = extBilling
                    )

                    accountAddons = AccountBillingAddons.objects.filter(billing=accounBill)
                    for k in accountAddons:
                        k.billing = newBill
                        k.save()

                    totalAddons = AccountBillingAddons.objects.filter(billing=newBill).aggregate(sumTotal=Sum('price'))
                    newBill.others = int(totalAddons['sumTotal'])
                    newBill.save()
                        
                except Exception as e:
                    with open(os.path.join(settings.BASE_DIR, 'logs/cron.log'), 'a') as f:
                        f.write("EmailError {} CronBilling--> Error: {}\n".format(datToday.strftime("%Y-%m-%d %H:%M"), str(e)))

