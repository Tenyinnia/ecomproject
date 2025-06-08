from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
from .models import OtpToken
from django.core.mail import send_mail
from django.utils import timezone
from django.contrib.auth.signals import user_logged_in, user_logged_out
from django.dispatch import receiver
from django.shortcuts import render, redirect
from django.contrib.auth import login, logout

# @receiver(post_save, sender=settings.AUTH_USER_MODEL)
# def create_user_profile(sender, instance, created, **kwargs):
#    if created:
#        if instance.user_type == 'student':
#            StudentProfile.objects.create(user=instance)
#        elif instance.user_type == 'teacher':
#            TutorProfile.objects.create(user=instance)
#        #elif instance.user_type == 'admin':
#            #AdminProfile.objects.create(user=instance)
# post_save.connect(create_user_profile, sender=settings.AUTH_USER_MODEL)

@receiver(post_save, sender = settings.AUTH_USER_MODEL)
def create_token(sender, instance, created, **kwargs):
    if created:
        if instance.is_superuser:
            pass
        else:
            OtpToken.objects.create(user = instance, otp_expires_at = timezone.now() + timezone.timedelta(minutes = 5))
            instance.is_active = False
            instance.save()
            otp = OtpToken.objects.filter(user = instance).last()
            subject = "Email Verification"
            message = f"""
                        Hi {instance.username}, here is your otp {otp.otp_code}
                        It expires in 5 minutes, use the url below to redirect back 
                        to the website to complete your registration.
                        
                        http://127.0.0.1:8000/verify_email/{instance.username}
                    """
            sender = "smartlearnk12@gmail.com"
            receiver = [instance.email]
            
            send_mail (
                subject,
                message,
                sender,
                receiver,
                fail_silently=False
            )                  
            