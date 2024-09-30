from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Business, BusinessProfile

@receiver(post_save, sender=Business)
def create_business_profile(sender, instance, created, **kwargs):
    if created:
        BusinessProfile.objects.create(business=instance)

@receiver(post_save, sender=Business)
def save_business_profile(sender, instance, **kwargs):
    instance.profile.save()
