import os

from django.db.models import Sum
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.utils import timezone
from django.conf import settings
from dateutil.relativedelta import relativedelta

from .models import Account, AccountBilling, RequestFiles, AccountFiles, Files, AccountBillingAddons

@receiver(pre_save, sender= Account)
def accountBilling_edit_record(sender, instance, **kwargs):
    try:
        setToday = timezone.now().astimezone(timezone.get_current_timezone())
        datToday = setToday + relativedelta(months=1)
        extToday = setToday + relativedelta(months=1, days=5)

        if not AccountBilling.objects.filter(account=instance).exists():
            instance.payment_date = datToday
            instance.due_date = extToday
        
    except Exception as e:
        with open(os.path.join(settings.BASE_DIR, 'logs/signals.log'), 'a') as f:
            eDate = timezone.now().strftime("%Y-%m-%d %H:%M")
            f.write("Undefined accountBillingEdit--> Date: {} Error: {}\n".format(eDate, str(e)))

@receiver(post_save, sender= Account)
def accountBilling_add_record(sender, instance, **kwargs):
    try:
        if not instance.is_inspector and not instance.is_staff:
            setToday = timezone.now().astimezone(timezone.get_current_timezone())
            datToday = setToday + relativedelta(months=1)
            extToday = setToday + relativedelta(months=1, days=5)

            accountPayment = instance.payment

            if not AccountBilling.objects.filter(account=instance).exists():
                AccountBilling.objects.create(
                    account=instance,
                    company_id=instance.company_id,
                    company= instance.company,
                    payment = accountPayment,
                    payment_total = accountPayment,
                    date_payment = datToday,
                    date_dolimit = extToday
                )
        
    except Exception as e:
        with open(os.path.join(settings.BASE_DIR, 'logs/signals.log'), 'a') as f:
            eDate = timezone.now().strftime("%Y-%m-%d %H:%M")
            f.write("Undefined accountBillingAdd--> Date: {} Error: {}\n".format(eDate, str(e)))

@receiver(pre_save, sender= RequestFiles)
def requestFiles_add_record(sender, instance, **kwargs):
    try:
        nameFile = Files.objects.get(code=instance.code).filename
        instance.filename = nameFile
        
    except Exception as e:
        with open(os.path.join(settings.BASE_DIR, 'logs/signals.log'), 'a') as f:
            eDate = timezone.now().strftime("%Y-%m-%d %H:%M")
            f.write("Undefined requestfilesAdd--> Date: {} Error: {}\n".format(eDate, str(e)))

@receiver(post_save, sender= RequestFiles)
def requestFiles_edit_record(sender, instance, **kwargs):
    if instance.do == "send":
        try:
            obj, requestFile = AccountFiles.objects.get_or_create(
                account=instance.account,
                code=instance.code,
                filename= instance.filename,
                file_validity=instance.file_validity,
                files=instance.file
            )

        except Exception as e:
            with open(os.path.join(settings.BASE_DIR, 'logs/signals.log'), 'a') as f:
                eDate = timezone.now().strftime("%Y-%m-%d %H:%M")
                f.write("Undefined requestfilesSendEdit--> Date: {} Error: {}\n".format(eDate, str(e)))

    if instance.do == "bill":
        try:
            accountBilling = AccountBilling.objects.filter(account=instance.account).order_by('-id').first()
            if accountBilling.state == "paid":
                accountBilling = AccountBilling.objects.create(
                    account=instance.account,
                    company_id=accountBilling.company_id,
                    company= accountBilling.company,
                    payment = 0,
                    date_invoice = accountBilling.date_invoice,
                    date_payment = accountBilling.date_payment,
                    date_dolimit = accountBilling.date_dolimit
                )

            obj, addBilling = AccountBillingAddons.objects.get_or_create(
                billing = accountBilling,
                code = instance.code,
                price = instance.price,
                file = instance.file,
                filename= instance.filename,
                date_request = instance.date_request,
                file_validity = instance.file_validity
            )
        
            totalAddons = AccountBillingAddons.objects.filter(billing=accountBilling).aggregate(sumTotal=Sum('price'))
            accountBilling.others = int(totalAddons['sumTotal'])
            accountBilling.save()


        except Exception as e:
            with open(os.path.join(settings.BASE_DIR, 'logs/signals.log'), 'a') as f:
                eDate = timezone.now().strftime("%Y-%m-%d %H:%M")
                f.write("Undefined requestfilesBillEdit--> Date: {} Error: {}\n".format(eDate, str(e)))


@receiver(pre_save, sender=AccountBilling)
def accountBilling_update_record(sender, instance, **kwargs):
        try:
            instance.payment_total = instance.debt + instance.payment + instance.others - (instance.balance + instance.discount)
        except Exception as e:
            with open(os.path.join(settings.BASE_DIR, 'logs/signals.log'), 'a') as f:
                eDate = timezone.now().strftime("%Y-%m-%d %H:%M")
                f.write("Undefined accountBillingAct--> Date: {} Error: {}\n".format(eDate, str(e)))


@receiver(post_save, sender= AccountBilling)
def accountBilling_send_record(sender, instance, **kwargs):
    if instance.state == "paid":
        try:
            accountID = instance.account
            accountAddons = AccountBillingAddons.objects.filter(billing=instance).order_by("id")
            for i in accountAddons:
                obj, requestFile = AccountFiles.objects.get_or_create(
                    account=accountID,
                    code=i.code,
                    filename= i.filename,
                    files= i.file,
                    file_date=timezone.now(),
                    file_validity=i.file_validity,
                    file_state=True
                )
             
            instance.date_succes = timezone.now()

        except Exception as e:
            with open(os.path.join(settings.BASE_DIR, 'logs/signals.log'), 'a') as f:
                eDate = timezone.now().strftime("%Y-%m-%d %H:%M")
                f.write("Undefined requestfilesSendEdit--> Date: {} Error: {}\n".format(eDate, str(e)))
