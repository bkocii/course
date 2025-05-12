from django.shortcuts import render
from emails.forms import EmailForm
from django.conf import settings
from emails import services as emails_services
from emails.models import Email, EmailVerificationEvent


def login_logout_view(request):
    return render(request, 'auth/login-logout.html', {})


EMAIL_ADDRESS = settings.EMAIL_ADDRESS


def home_view(request, *args, **kwargs):
    template_name = 'home.html'
    print(request.POST)
    form = EmailForm(request.POST or None)
    context = {
        'form': form,
        'message': ''
    }
    if form.is_valid():
        email_val = form.cleaned_data.get('email')
        obj = emails_services.start_verification_event(email_val)
        print(obj)
        context['form'] = EmailForm()
        context['message'] = f'success you have access. message from {EMAIL_ADDRESS}'
    else:
        print(form.errors)
    print('email_id', request.session.get('email_id'))
    return render(request, template_name, context)

