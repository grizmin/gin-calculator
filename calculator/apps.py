from django.apps import AppConfig


class CalculatorConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'calculator'

    def ready(self):
        try:
            from gin_calculator import __version__
            from calculator.models import AppVersion
            latest = AppVersion.objects.first()
            if latest is None or latest.version != __version__:
                AppVersion.objects.create(version=__version__)
        except Exception:
            # Table may not exist yet during initial migration
            pass
