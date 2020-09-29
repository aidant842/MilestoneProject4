from django.shortcuts import render

def profile(request):
    """ Display User's Profile """
    template ='profiles/profiles.html'
    context = {}

    return render(request, template, context)