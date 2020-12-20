from django.shortcuts import (render, redirect,
                              reverse, get_object_or_404, HttpResponse)
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.forms import inlineformset_factory
from django.template.loader import render_to_string
from django.core.mail import send_mail

from .forms import OrderForm, DeliveryEditForm
from .models import Order, OrderLineItem
from products.models import Product, Material, Colour, Size
from profiles.models import UserProfile
from profiles.forms import UserProfileForm
from bag.contexts import bag_contents

import stripe
import json


@require_POST
def cache_checkout_data(request):
    """ cache checkout data  """

    """ Grab the payment ID, assign the stripe.api_key
        to the secret key from the settings
        cache values in the stripe payment intent.
        otherwise return an error """
    try:
        pid = request.POST.get('client_secret').split('_secret')[0]
        stripe.api_key = settings.STRIPE_SECRET_KEY
        stripe.PaymentIntent.modify(pid, metadata={
            'bag': json.dumps(request.session.get('bag', [])),
            'save_info': request.POST.get('save_info'),
            'username': request.user,
        })
        return HttpResponse(status=200)
    except Exception as e:
        messages.error(request, 'Sorry your payment cannot be'
                                ' processed right now.'
                                ' Please try again later.')
        return HttpResponse(content=e, status=400)


def checkout(request):
    stripe_public_key = settings.STRIPE_PUBLIC_KEY
    stripe_secret_key = settings.STRIPE_SECRET_KEY

    """ if submitting the checkout form,
        grab the form data and assign it to form_data
        and create an instance of the OrderForm using form_data."""

    if request.method == 'POST':
        bag = request.session.get('bag', [])

        form_data = {
            'full_name': request.POST['full_name'],
            'email': request.POST['email'],
            'phone_number': request.POST['phone_number'],
            'country': request.POST['country'],
            'postcode': request.POST['postcode'],
            'town_or_city': request.POST['town_or_city'],
            'street_address1': request.POST['street_address1'],
            'street_address2': request.POST['street_address2'],
            'county': request.POST['county'],
        }
        order_form = OrderForm(form_data)

        """ Check if the form is valid, if so, save the order. """

        if order_form.is_valid():
            order = order_form.save(commit=False)
            pid = request.POST.get('client_secret').split('_secret')[0]
            order.stripe_pid = pid
            order.original_bag = json.dumps(bag)
            order.save()

            """ From there create an OrderLineItem with the
                product details and save it.
                Handle Errors """

            for item in bag:
                try:
                    product = Product.objects.get(id=item['item_id'])
                    size = Size.objects.get(value=item['item_size'])
                    material = (Material.objects.get
                                (value=item['item_material']))
                    colour = Colour.objects.get(name=item['item_colour'])
                    quantity = item["quantity"]
                    order_line_item = OrderLineItem(
                        order=order,
                        product=product,
                        product_size=size,
                        product_material=material,
                        product_colour=colour,
                        quantity=quantity,
                    )
                    order_line_item.save()
                except Product.DoesNotExist:
                    messages.error(request,
                                   ("One of the products in your bag wasn't "
                                    "found in the database, "
                                    "Please call us for assistance.")
                                   )
                    order.delete()
                    return redirect(reverse('view_bag'))
            request.session['save_info'] = 'save-info' in request.POST
            return redirect(reverse('checkout_success',
                                    args=[order.order_number]))
        else:
            messages.error(request, 'There was an error with your form.'
                                    ' Please double check'
                                    ' your information.')

    else:
        """ if not working from POST Data render checkout page
            and handle possible errors """
        bag = request.session.get('bag', [])
        if not bag:
            messages.error(request,
                           "There's nothing in your bag at the moment")
            return redirect(reverse('products'))

        current_bag = bag_contents(request)
        stripe_total = current_bag['grand_total']
        stripe.api_key = stripe_secret_key
        intent = stripe.PaymentIntent.create(
            amount=stripe_total,
            currency=settings.STRIPE_CURRENCY,
        )

        if request.user.is_authenticated:
            try:
                profile = UserProfile.objects.get(user=request.user)
                order_form = OrderForm(initial={
                    'full_name': profile.user.get_full_name(),
                    'email': profile.user.email,
                    'phone_number': profile.default_phone_number,
                    'country': profile.default_country,
                    'postcode': profile.default_postcode,
                    'town_or_city': profile.default_town_or_city,
                    'street_address1': profile.default_street_address1,
                    'street_address2': profile.default_street_address2,
                    'county': profile.default_county,
                })
            except UserProfile.DoesNotExist:
                order_form = OrderForm()
        else:
            order_form = OrderForm()

    if not stripe_public_key:
        messages.warning(request, 'No stripe public key found')

    template = 'checkout/check_out.html'
    context = {
        'order_form': order_form,
        'stripe_public_key': stripe_public_key,
        'client_secret': intent.client_secret,
    }

    return render(request, template, context)


def checkout_success(request, order_number):
    """ A view to handle successful checkout """

    """ assign variables """

    save_info = request.session.get('save_info')
    order = get_object_or_404(Order, order_number=order_number)

    """ if the user is logged in, save the order to the profile
        so as the user has access to order history """

    if request.user.is_authenticated:
        profile = UserProfile.objects.get(user=request.user)
        order.user_profile = profile
        order.save()

        """ if the user requested to save info from checkout
            save the info to the profile so as the form
            is automatically filled out for the next order
            if the user is logged in """

        if save_info:
            profile_data = {
                'default_phone_number': order.phone_number,
                'default_country': order.country,
                'default_postcode': order.postcode,
                'default_town_or_city': order.town_or_city,
                'default_street_address1': order.street_address1,
                'default_street_address2': order.street_address2,
                'default_county': order.county,
            }

            user_profile_form = UserProfileForm(profile_data, instance=profile)
            if user_profile_form.is_valid():
                user_profile_form.save()

    messages.success(request, 'Order successfully processed. '
                     f'Your order number is { order_number }.'
                     f' A confirmation email will be sent to { order.email }')

    if 'bag' in request.session:
        del request.session['bag']

    template = 'checkout/checkout_success.html'
    context = {
        'order': order,
    }

    return render(request, template, context)


@login_required
def order_admin(request):
    """ A view to see all orders, for admin use """

    if not request.user.is_superuser:
        messages.error(request, 'Sorry, only owners can access this.')
        return redirect(reverse('home'))

    order_items = OrderLineItem.objects.all()
    orders = Order.objects.all()

    template = 'checkout/order_admin.html'

    context = {
        'order_items': order_items,
        'orders': orders,
    }
    return render(request, template, context)


@login_required
def order_detail(request, order_id):
    """ A view to see order details """

    if not request.user.is_superuser:
        messages.error(request, 'Sorry, only owners can access this.')
        return redirect(reverse('home'))

    """ Declare Variables """

    order = get_object_or_404(Order, pk=order_id)
    items_formset = inlineformset_factory(Order,
                                          OrderLineItem, extra=1,
                                          fields=('product',
                                                  'product_size',
                                                  'product_material',
                                                  'product_colour',
                                                  'quantity',))

    cust_email = order.email
    subject = render_to_string(
            'checkout/dispatched_emails/dispatched_email_subject.txt',
            {'order': order}
        )

    body = render_to_string(
            'checkout/dispatched_emails/dispatched_email_body.txt',
            {'order': order, 'contact_email': settings.DEFAULT_FROM_EMAIL}
        )

    """ If working with POST create an instance of items_formset
        and deliveryEditForm with the order.
        If both forms are valid save and flash message to the user. """

    if request.method == 'POST':
        formset = items_formset(request.POST, instance=order)
        order_detail_delivery_form = DeliveryEditForm(request.POST,
                                                      instance=order)
        if formset.is_valid() and order_detail_delivery_form.is_valid():
            formset.save()
            order_detail_delivery_form.save()
            messages.success(request, 'Order updated successfully.')

            """ If the user marks the order as dispatched and the
                confirmation email hasn't previously been sent
                send a confirmation email to the shopper. """

            if order.dispatched is True and order.email_sent is False:
                send_mail(
                    subject,
                    body,
                    settings.DEFAULT_FROM_EMAIL,
                    [cust_email]
                )
                order.email_sent = True
                order_detail_delivery_form.save()
                messages.success(request, 'Dispatch E-mail sent to user.')
        else:
            messages.error(request,
                           'Update failed, please ensure the'
                           ' product form is valid.')

    formset = items_formset(instance=order)

    order_detail_delivery_form = DeliveryEditForm(initial={
        'full_name': order.full_name,
        'email': order.email,
        'phone_number': order.phone_number,
        'country': order.country,
        'postcode': order.postcode,
        'town_or_city': order.town_or_city,
        'street_address1': order.street_address1,
        'street_address2': order.street_address2,
        'county': order.county,
        'dispatched': order.dispatched,
    })

    template = 'checkout/order_detail.html'

    context = {
        'order_delivery': order_detail_delivery_form,
        'order': order,
        'line_items': formset,
    }

    return render(request, template, context)
