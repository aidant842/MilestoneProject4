from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Messages
from profiles.models import UserProfile


def contact_page(request):
    """ A view to return the index page """

    if request.user.is_authenticated:
        profile = get_object_or_404(UserProfile, user=request.user)

    if request.method == 'POST':
        contact = Messages()
        name = request.POST.get('name')
        email = request.POST.get('email')
        subject = request.POST.get('subject')
        enquiry = request.POST.get('enquiry')
        contact.name = name
        contact.email = email
        contact.subject = subject
        contact.enquiry = enquiry

        contact.save()
        messages.success(request, 'Thank you, messaged recieved')
        return redirect('contact')

    context = {
        'profile': profile,
    }

    return render(request, 'contact/contact.html', context)
