# Generated by Django 5.1.7 on 2025-03-29 09:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0003_lesson'),
    ]

    operations = [
        migrations.AddField(
            model_name='lesson',
            name='can_preview',
            field=models.BooleanField(default=False, help_text='If user is allowed to see this'),
        ),
        migrations.AddField(
            model_name='lesson',
            name='status',
            field=models.CharField(choices=[('publish', 'Published'), ('soon', 'Coming Soon'), ('draft', 'Draft')], default='publish', max_length=10),
        ),
    ]
