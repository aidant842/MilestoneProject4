from django.shortcuts import render, redirect, reverse, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required

from .models import Inbox
from profiles.models import UserProfile


def contact_page(request):
    """ A view to return the index page """

    profile = ''

    if request.user.is_authenticated:
        profile = get_object_or_404(UserProfile, user=request.user)


    if request.method == 'POST':
        contact = Inbox()
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

    return render(request, 'contact_us/contact_us.html', context)


@login_required
def inbox(request):
    """ A view to return inbox messages for admin users """

    if not request.user.is_superuser:
        messages.error(request, 'Sorry, only owners can access this.')
        return redirect(reverse('home'))

    inbox = Inbox.objects.all()

    template = 'contact_us/inbox.html'

    context = {
        'inbox': inbox
    }

    return render(request, template, context)


@login_required
def message(request, message_id):
    """ A view to show the full message """

    if not request.user.is_superuser:
        messages.error(request, 'Sorry, only owners can access this.')
        return redirect(reverse('home'))

    template = 'contact_us/message_page.html'

    inbox = get_object_or_404(Inbox, pk=message_id)

    context = {
        'inbox': inbox,
    }

    return render(request, template, context)
