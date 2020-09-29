from django.shortcuts import render, get_object_or_404
from .models import UserProfile

def profile(request):
    """ Display User's Profile """
    
    template = 'profiles/profiles.html'

    profile = get_object_or_404(UserProfile, user=request.user)

    context = {
        'profile': profile,
    }

    return render(request, template, context)
