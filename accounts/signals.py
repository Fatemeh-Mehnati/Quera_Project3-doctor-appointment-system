from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import User, Wallet


@receiver(post_save, sender=User)
def create_wallet_for_new_user(sender, instance, created, **kwargs):
    """
    بلافاصله بعد از ساخت هر کاربر جدید، یک کیف پول با موجودی صفر
    برایش ساخته می‌شود (AC اول تیکت WP7).
    """
    if created:
        Wallet.objects.get_or_create(user=instance)
