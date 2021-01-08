# Ensure port is public
from django.http import HttpResponse
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings


from .models import Order, OrderLineItem
from products.models import Product, Material, Colour, Size
from profiles.models import UserProfile

import json
import time


class StripeWH_Handler():
    """ Handle Stripe webhooks """

    def __init__(self, request):
        self.request = request

    def _send_confirmation_email(self, order):
        """ Send the user a confirmation email """

        cust_email = order.email
        subject = render_to_string(
                'checkout/confirmation_emails/confirmation_email_subject.txt',
                {'order': order}
            )

        body = render_to_string(
                'checkout/confirmation_emails/confirmation_email_body.txt',
                {'order': order, 'contact_email': settings.DEFAULT_FROM_EMAIL}
            )

        send_mail(
            subject,
            body,
            settings.DEFAULT_FROM_EMAIL,
            [cust_email]
        )

    def handle_event(self, event):
        """ Hande Generic/unknown/unexpected webhook event """

        return HttpResponse(
            content=f'Uhandled Webhook recieved. {event["type"]}',
            status=200
        )

    def handle_payment_intent_succeeded(self, event):
        """ Hande the payment_intent_succeeded webhook from Stripe """
        intent = event.data.object
        pid = intent.id
        bag_dict = intent.metadata
        save_info = bag_dict['save_info']
        username = bag_dict['username']
        bag_dict.pop('save_info')
        bag_dict.pop('username')
        bag = bag_dict.items()

        billing_details = intent.charges.data[0].billing_details
        shipping_details = intent.shipping
        grand_total = intent.charges.data[0].amount

        for field, value in shipping_details.address.items():
            if value == "":
                shipping_details.address[field] = None

        # Update profile information if save_info was checked
        profile = None
        if username != 'AnonymousUser':
            profile = UserProfile.objects.get(user__username=username)
            if save_info:
                profile.default_phone_number = shipping_details.phone
                profile.default_country = shipping_details.address.country
                profile.default_postcode = shipping_details.address.postal_code
                profile.default_town_or_city = shipping_details.address.city
                profile.default_street_address1 = (shipping_details
                                                   .address.line1)
                profile.default_street_address2 = (shipping_details
                                                   .address.line2)
                profile.default_county = shipping_details.address.state
                profile.save()

        """ Check if the order exists from the view,
        if not, try again upto 5 times.
        if the order exists send the confirmation email """

        order_exists = False
        attempt = 1
        while attempt <= 15:
            try:
                order = Order.objects.get(
                    full_name__iexact=shipping_details.name,
                    email__iexact=billing_details.email,
                    phone_number__iexact=shipping_details.phone,
                    country__iexact=shipping_details.address.country,
                    postcode__iexact=shipping_details.address.postal_code,
                    town_or_city__iexact=shipping_details.address.city,
                    street_address1__iexact=shipping_details.address.line1,
                    street_address2__iexact=shipping_details.address.line2,
                    county__iexact=shipping_details.address.state,
                    grand_total=grand_total,
                    stripe_pid=pid,
                )
                order_exists = True
                break
            except Order.DoesNotExist:
                attempt += 1
                time.sleep(1)
        if order_exists:
            self._send_confirmation_email(order)
            return HttpResponse(
                content=f'Webhook recieved. {event["type"]} |'
                ' SUCCESS: Verified order already exists',
                status=200
                )
        else:
            """ Try and create the order and OrderLineItem here in the webhook handler
                and send the confirmation email """
            order = None
            try:
                order = Order.objects.create(
                    full_name=shipping_details.name,
                    user_profile=profile,
                    email=billing_details.email,
                    phone_number=shipping_details.phone,
                    country=shipping_details.address.country,
                    postcode=shipping_details.address.postal_code,
                    town_or_city=shipping_details.address.city,
                    street_address1=shipping_details.address.line1,
                    street_address2=shipping_details.address.line2,
                    county=shipping_details.address.state,
                    original_bag=bag,
                    stripe_pid=pid,
                )
                for identifier, item in bag:
                    item = json.loads(item)
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
            except Exception as e:
                if order:
                    order.delete()
                    return HttpResponse(content='Webhooked recieved: '
                                                f'{event["type"]}| ERROR: {e}',
                                        status=500)
        self._send_confirmation_email(order)
        return HttpResponse(
            content=f'Webhook recieved. {event["type"]}'
            ' | SUCCESS: Created order in webhook',
            status=200
        )

    def handle_payment_intent_payment_failed(self, event):
        """ Hande the payment_intent_payment_failed webhook from stripe """

        return HttpResponse(
            content=f'Webhook recieved. {event["type"]}',
            status=200
        )
