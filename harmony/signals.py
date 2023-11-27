from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .utils import log
from django.apps import apps

@receiver(post_save)
def generic_post_save(sender, instance, created, **kwargs):
    if created:
        log('debug', sender.__name__, f'{sender.__name__} {instance.id} created.')
    else:
        log('debug', sender.__name__, f'{sender.__name__} {instance.id} modified.')

@receiver(post_delete)
def generic_post_delete(sender, instance, **kwargs):
    log('debug', sender.__name__, f'{sender.__name__} {instance.id} deleted.')

# Connect the signal handler to all models
for model in apps.get_models():
    post_save.connect(generic_post_save, sender=model)
    post_delete.connect(generic_post_delete, sender=model)
