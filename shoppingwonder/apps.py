from django.apps import AppConfig


class ShoppingwonderConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'shoppingwonder'

    def ready(self):
        # Implicitly connect a signal handlers decorated with @receiver.
        from . import signals