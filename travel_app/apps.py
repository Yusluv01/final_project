from django.apps import AppConfig

class TravelAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'travel_app'
    verbose_name = 'Travel Management System'
    
    def ready(self):
        import travel_app.signals