from django.apps import AppConfig
import helpers


class CoursesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'courses'

    def ready(self):
        helpers.cloudinary_init()