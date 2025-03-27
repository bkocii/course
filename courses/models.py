from django.db import models

# Create your models here.


class AccessRequirement(models.TextChoices):
    ANYONE = 'any', 'Anyone'
    EMAIL_REQUIRED = 'email_required', 'Email Required'


# 1st = short name for database efficiency
# 2nd = name
class PublishStatus(models.TextChoices):
    PUBLISHED = 'publish', 'Published'
    COMING_SOON = 'soon', 'Coming Soon'
    DRAFT = 'draft', 'Draft'


# a function we can use for handling uploaded images
def handle_upload(instance, filename):
    return f'{filename}'


class Course(models.Model):
    title = models.CharField(max_length=120)
    description = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to=handle_upload, blank=True, null=True)
    access = models.CharField(
        max_length=15,
        choices=AccessRequirement.choices,
        default=AccessRequirement.EMAIL_REQUIRED
    )
    status = models.CharField(
        max_length=10,
        choices=PublishStatus.choices,
        default=PublishStatus.DRAFT
    )

    # this sets is_published as a class variable
    @property
    def is_published(self):
        return self.status == PublishStatus.PUBLISHED

