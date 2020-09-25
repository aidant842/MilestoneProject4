# Ensure port is public
from django.http import HttpResponse


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

        return HttpResponse(
            content=f'Webhook recieved. {event["type"]}',
            status=200
        )

    def handle_payment_intent_payment_failed(self, event):
        """ Hande the payment_intent_payment_failed webhook from stripe """

        return HttpResponse(
            content=f'Webhook recieved. {event["type"]}',
            status=200
        )
