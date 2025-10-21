from django.apps import AppConfig


class ChatConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'chat'
    
    def ready(self):
        import chat.signals
        
        # Auto-setup application if needed
        from .setup_service import auto_setup_on_ready
        auto_setup_on_ready()