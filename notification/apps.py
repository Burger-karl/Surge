# from django.apps import AppConfig


# class NotificationConfig(AppConfig):
#     default_auto_field = 'django.db.models.BigAutoField'
#     name = 'notification'


from django.apps import AppConfig

class NotificationConfig(AppConfig):
    name = 'notification'

    def ready(self):
        import notification.signals
