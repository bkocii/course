# Generated by Django 5.2 on 2025-05-27 07:21

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0014_question_lesson_has_quiz_answer_quiz_question_quiz'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='quiz',
            options={'verbose_name_plural': 'quizzes'},
        ),
        migrations.AlterModelOptions(
            name='students',
            options={'verbose_name_plural': 'students'},
        ),
    ]
