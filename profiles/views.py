from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from django.contrib.auth.models import User

from .models import UserProfile
from .forms import UserProfileForm, UserEditForm
from checkout.models import Order


@login_required
def profile(request):
    """ Display User's Profile """

    profile = get_object_or_404(UserProfile, user=request.user)

    orders = profile.orders.all()

    template = 'profiles/profiles.html'
    context = {
        'orders': orders,
        'profile': profile,
    }

    return render(request, template, context)


@login_required
def update_profile(request):

    profile = get_object_or_404(UserProfile, user=request.user)
    user = get_object_or_404(User, id=request.user.id)

    if request.method == 'POST':
        user_profile_form = UserProfileForm(request.POST, instance=profile)
        user_edit_form = UserEditForm(request.POST, instance=user)
        if user_profile_form.is_valid() and user_edit_form.is_valid():
            user_profile_form.save()
            user_edit_form.save()
            messages.success(request, 'Profile updated successfully.')
            return redirect('profile')
        else:
            messages.error(request, 'Updated failed, please ensure the form is valid.')

    user_profile_form = UserProfileForm(instance=profile)
    user_edit_form = UserEditForm(instance=user)

    template = 'profiles/update_profile.html'
    context = {
        'user_profile_form': user_profile_form,
        'user_edit_form': user_edit_form
    }

    return render(request, template, context)


def order_history(request, order_number):
    order = get_object_or_404(Order, order_number=order_number)

    messages.info(request, (
        f'This is a post confirmation for order number {order_number}.'
        'A confirmation email was on the order date.'
        ))

    template = 'checkout/checkout_success.html'

    context = {
        'order': order,
        'from_profile': True,
    }

    return render(request, template, context)
