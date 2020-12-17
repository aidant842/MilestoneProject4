from django.shortcuts import get_object_or_404
from products.models import Product


def bag_contents(request):
    """ a context processor to allow for these values
        to be easily accessible throghout the site """

    bag_items = []
    total = 0
    bag = request.session.get('bag', [])

    for item in bag:
        product = get_object_or_404(Product, pk=item["item_id"])
        total += product.price * item["quantity"]
        bag_items.append({
            'item_id': product.id,
            'product': product,
            'quantity': item["quantity"],
            'material': item["item_material"],
            'colour': item["item_colour"],
            'size': item["item_size"],
            'total': item["total"],
        })
    delivery = int(total * .1)
    grand_total = total + delivery

    context = {
        'bag_items': bag_items,
        'delivery': delivery,
        'total': int(total),
        'grand_total': grand_total,
    }

    return context
