from django.shortcuts import get_object_or_404
from products.models import Product


def bag_contents(request):

    total = 0
    bag = request.session.get('bag', [])

    for item in bag:
        product = get_object_or_404(Product, pk=item["item_id"])
        total += product.price * item["quantity"]
        item["product"] = product
        item["total"] = product.price * item["quantity"]

    delivery = int(total * .1)
    grand_total = total + delivery

    context = {
        'bag_items': bag,
        'delivery': delivery,
        'grand_total': grand_total,
    }
    print("context", context)

    return context
