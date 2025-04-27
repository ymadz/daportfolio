from django.apps import AppConfig

class TrackerConfig(AppConfig):
    name = 'tracker'

    def ready(self):
        import tracker.signals  # This will ensure that the signal is connected.
