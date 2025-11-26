from django.db.models.signals import post_save
from django.contrib.auth.models import User, Permission
from django.dispatch import receiver

@receiver(post_save, sender=User)
def add_can_mark_returned_permission(sender, instance, created, **kwargs):
    """
    Автоматически добавляет разрешение 'can_mark_returned'
    всем пользователям со статусом staff.
    """
    if instance.is_staff:
        try:
            permission = Permission.objects.get(codename='can_mark_returned')
            instance.user_permissions.add(permission)
        except Permission.DoesNotExist:
            pass
