from django.apps import AppConfig


class SchedulingDataConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "scheduling_data"
    
    def ready(self) -> None:
        import scheduling_data.utils.signals
