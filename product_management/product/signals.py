from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Product
import logging

logger = logging.getLogger(__name__)

@receiver(post_save, sender=Product)
def log_product_changes(sender, instance, created, **kwargs):
    if created:
        logger.info(f"Product created: {instance.title} (ID: {instance.id})")
    else:
        logger.info(f"Product updated: {instance.title} (ID: {instance.id})")

@receiver(post_delete, sender=Product)
def log_product_deletion(sender, instance, **kwargs):
    logger.info(f"Product deleted: {instance.title} (ID: {instance.id})")
