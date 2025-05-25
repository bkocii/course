from django.db import models
import uuid
from cloudinary.models import CloudinaryField
import helpers
from django.utils.text import slugify
from django.utils import timezone

helpers.cloudinary_init()

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


# Updated generate_public_id function
def generate_public_id(instance, *args, **kwargs):
    # Check for title or text field
    identifier = getattr(instance, 'title', None) or getattr(instance, 'text', None)
    unique_id = str(uuid.uuid4()).replace("-", "")
    if not identifier:
        return unique_id  # Fallback to UUID if neither title nor text exists
    slug = slugify(identifier[:50])  # Limit length to avoid overly long slugs
    unique_id_short = unique_id[:5]
    return f"{slug}-{unique_id_short}"


def get_public_id_prefix(instance, *args, **kwargs):
    if hasattr(instance, 'path'):
        path = instance.path
        if path.startswith("/"):
            path = path[1:]
        if path.endswith("/"):
            path = path[:-1]
        return path
    public_id = instance.public_id
    model_class = instance.__class__
    model_name = model_class.__name__
    model_name_slug = slugify(model_name)
    if not public_id:
        return f"{model_name_slug}"
    return f"{model_name_slug}/{public_id}"


def get_display_name(instance, *args, **kwargs):
    if hasattr(instance, 'get_display_name'):
        return instance.get_display_name()
    elif hasattr(instance, 'title'):
        return instance.title
    elif hasattr(instance, 'text'):  # Added for Question and Answer
        return instance.text
    model_class = instance.__class__
    model_name = model_class.__name__
    return f"{model_name} Upload"


class Course(models.Model):
    title = models.CharField(max_length=120, blank=True)
    description = models.TextField(blank=True, null=True)
    public_id = models.CharField(max_length=130, null=True, blank=True, db_index=True)
    # image = models.ImageField(upload_to=handle_upload, blank=True, null=True)
    image = CloudinaryField('image',
                            null=True,
                            public_id_prefix=get_public_id_prefix,
                            display_name=get_display_name,
                            tags=["course", "thumbnail"])
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
    timestamp = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        #before save
        if self.public_id == "" or self.public_id is None:
            self.public_id = generate_public_id(self)
        super().save(*args, **kwargs)
        #after save

    def get_absolute_url(self):
        return self.path

    @property
    def path(self):
        return f"/courses/{self.public_id}"

    def get_display_name(self):
        return f"{self.title} - Course"

    def get_thumbnail(self):
        if not self.image:
            return None
        return helpers.get_cloudinary_image_object(
            self,
            as_html=False,
            field_name='image',
            width=382)

    def get_display_image(self):
        if not self.image:
            return None
        return helpers.get_cloudinary_image_object(
            self,
            as_html=False,
            field_name='image',
            width=750)

    # this sets is_published as a class variable
    @property
    def is_published(self):
        return self.status == PublishStatus.PUBLISHED


class Lesson(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    title = models.CharField(max_length=120)
    description = models.TextField(blank=True, null=True)
    public_id = models.CharField(max_length=130, null=True, blank=True, db_index=True)
    thumbnail = CloudinaryField('image',
                                public_id_prefix=get_public_id_prefix,
                                display_name=get_display_name,
                                tags=["thumbnail", "lessons"],
                                blank=True, null=True)
    video = CloudinaryField('video',
                            public_id_prefix=get_public_id_prefix,
                            display_name=get_display_name,
                            tags=["video", "lessons"],
                            blank=True,
                            null=True,
                            type='private',
                            resource_type='video')
    order = models.IntegerField(default=0)
    can_preview = models.BooleanField(default=False, help_text='If user is allowed to see this')
    status = models.CharField(
        max_length=10,
        choices=PublishStatus.choices,
        default=PublishStatus.PUBLISHED
    )
    timestamp = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    has_quiz = models.BooleanField(default=False, help_text='If this lesson has a quiz')
    class Meta:
        ordering = ['order', '-updated']

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        #before save
        if self.public_id == "" or self.public_id is None:
            self.public_id = generate_public_id(self)
        super().save(*args, **kwargs)
        #after save

    @property
    def path(self):
        course_path = self.course.path
        if course_path.endswith("/"):
            course_path = course_path[:-1]
        return f"{course_path}/lessons/{self.public_id}"

    @property
    def requires_email(self):
        return self.course.access == AccessRequirement.EMAIL_REQUIRED

    def get_display_name(self):
        return f"{self.title} - {self.course.get_display_name()}"

    def get_absolute_url(self):
        return self.path

    @property
    def is_coming_soon(self):
        return self.status == PublishStatus.COMING_SOON

    @property
    def has_video(self):
        return self.video is not None

    def get_thumbnail(self):
        width = 382
        if self.thumbnail:
            return helpers.get_cloudinary_image_object(
                self,
                as_html=False,
                field_name='thumbnail',
                format='jpg',
                width=width)
        elif self.video:
            return helpers.get_cloudinary_image_object(
                self,
                as_html=False,
                field_name='video',
                format='jpg',
                width=width)
        else:
            return None


class Students(models.Model):
    course = models.ForeignKey(Course, null=False, on_delete=models.CASCADE)
    email = models.EmailField()

    class Meta:
        unique_together = ('course', 'email')
        verbose_name_plural = "students"

    def __str__(self):
        return self.email


class Quiz(models.Model):
    lesson = models.OneToOneField('Lesson', on_delete=models.CASCADE, related_name='quiz')
    title = models.CharField(max_length=120)
    public_id = models.CharField(max_length=130, null=True, blank=True, db_index=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "quizzes"

    def __str__(self):
        return f"Quiz for {self.lesson.title}"

    def save(self, *args, **kwargs):
        if self.public_id == "" or self.public_id is None:
            self.public_id = generate_public_id(self)
        super().save(*args, **kwargs)

    @property
    def path(self):
        lesson_path = self.lesson.path
        if lesson_path.endswith("/"):
            lesson_path = lesson_path[:-1]
        return f"{lesson_path}/quiz/"

    def get_display_name(self):
        return f"{self.title} - {self.lesson.get_display_name()}"

class Question(models.Model):
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='questions')
    text = models.CharField(max_length=500)
    order = models.IntegerField(default=0)
    public_id = models.CharField(max_length=130, null=True, blank=True, db_index=True)

    def __str__(self):
        return self.text

    def save(self, *args, **kwargs):
        if self.public_id == "" or self.public_id is None:
            self.public_id = generate_public_id(self)
        super().save(*args, **kwargs)

class Answer(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='answers')
    text = models.CharField(max_length=200)
    is_correct = models.BooleanField(default=False)
    public_id = models.CharField(max_length=130, null=True, blank=True, db_index=True)

    def __str__(self):
        return self.text

    def save(self, *args, **kwargs):
        if self.public_id == "" or self.public_id is None:
            self.public_id = generate_public_id(self)
        super().save(*args, **kwargs)
