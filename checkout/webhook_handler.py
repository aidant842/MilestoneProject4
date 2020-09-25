# Ensure port is public
from django.http import HttpResponse


from .models import Order, OrderLineItem
from products.models import Product, Material, Colour, Size

import json
import time


class StripeWH_Handler:
    """ Handle Stripe webhooks """

    def __init__(self, request):
        self.request = request

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
        bag = intent.metadata.bag
        save_info = intent.metadata.save_info

        billing_details = intent.charges.data[0].billing_details
        shipping_details = intent.shipping
        grand_total = intent.charges.data[0].amount

        for field, value in shipping_details.items():
            if value == "":
                shipping_details.address[field] = None

        order_exists = False
        attempt = 1
        while attempt <= 5:
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
                    original_bag=bag,
                    stripe_pid=pid,
                )
                order_exists = True
                break
            except Order.DoesNotExist:
                attempt += 1
                time.sleep(1)
        if order_exists:
            return HttpResponse(
                content=f'Webhook recieved. {event["type"]} | SUCCESS: Verified order already exists',
                status=200
                )
        else:
            order = None
            try:
                order = Order.objects.create(
                    full_name=shipping_details.name,
                    email=shipping_details.email,
                    phone_number=shipping_details.phone,
                    country=shipping_details.country,
                    postcode=shipping_details.postal_code,
                    town_or_city=shipping_details.city,
                    street_address1=shipping_details.line1,
                    street_address2=shipping_details.line2,
                    county=shipping_details.state,
                    original_bag=bag,
                    stripe_pid=pid,
                )
                for item in json.loads(bag).items:
                    product = Product.objects.get(id=item['item_id'])
                    size = Size.objects.get(value=item['item_size'])
                    material = Material.objects.get(value=item['item_material'])
                    colour = Colour.objects.get(name=item['item_colour'])
                    order_line_item = OrderLineItem(
                        order=order,
                        product=product,
                        product_size=Size(size.id),
                        product_material=Material(material.id),
                        product_colour=Colour(colour.id),
                        quantity=item["quantity"],
                    )
                    order_line_item.save()
            except Exception as e:
                if order:
                    order.delete()
                    return HttpResponse(content=f'Webhooked recieved: {event["type"]} | ERROR: {e}',
                                        status=500)

        return HttpResponse(
            content=f'Webhook recieved. {event["type"]} | SUCCESS: Created order in webhook',
            status=200
        )

    def handle_payment_intent_payment_failed(self, event):
        """ Hande the payment_intent_payment_failed webhook from stripe """

        return HttpResponse(
            content=f'Webhook recieved. {event["type"]}',
            status=200
        )
