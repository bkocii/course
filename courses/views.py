from django.shortcuts import render, redirect
from django.http import Http404, JsonResponse, HttpResponseBadRequest, HttpResponseNotFound, HttpResponseForbidden
from . import services
import helpers
from courses.models import Lesson, Students
# Create your views here.


def course_list_view(request):
    queryset = services.get_publish_courses()
    context = {
        'object_list': queryset
    }
    template_name = 'courses/list.html'
    if request.htmx:
        template_name = 'courses/snippets/list-display.html'
        context['queryset'] = queryset[:3]
    return render(request, template_name, context)


def course_detail_view(request, course_id=None, *args, **kwargs):
    course_obj = services.get_course_detail(course_id=course_id)
    if course_obj is None:
        return Http404
    lesson_queryset = course_obj.lesson_set.all()
    context = {
        'object': course_obj,
        'lesson_queryset': services.get_course_lessons(course_obj)
    }
    # return JsonResponse({'data': course_obj.id, 'lesson_ids': [x.path for x in lesson_queryset]})
    return render(request, 'courses/detail.html', context)


def lesson_detail_view(request, course_id=None, lesson_id=None, *args, **kwargs):
    lesson_obj = services.get_lesson_detail(course_id=course_id, lesson_id=lesson_id)
    course_obj = services.get_course_detail(course_id=course_id)
    if lesson_obj is None:
        return Http404
    email_id_exists = request.session.get('email_id')
    if lesson_obj.requires_email and not email_id_exists:
        request.session['next_url'] = request.path
        request.session['lesson_obj_id'] = lesson_obj.public_id
        request.session['course_obj_id'] = course_obj.public_id
        return render(request, 'courses/email-required.html')

    template_name = 'courses/lesson-coming-soon.html'
    context = {
        'object': lesson_obj
    }
    if not lesson_obj.is_coming_soon and lesson_obj.has_video:
        """
        Lesson is published
        Video is available
        go forward
        """
        template_name = 'courses/lesson.html'
        video_embed_html = helpers.get_cloudinary_video_object(
            lesson_obj,
            as_html=True,
            field_name='video',
            width=750)
        context['video_embed'] = video_embed_html
    return render(request, template_name, context)
