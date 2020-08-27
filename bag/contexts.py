from django.shortcuts import get_object_or_404
from products.models import Product


def bag_contents(request):

    bag_items = []
    total = 0
    delivery = total * .10
    bag = request.session.get('bag', {})

    for item_id in list(bag.keys()):
        product = get_object_or_404(Product, pk=item_id)
        quantity = bag[item_id]['item_data']['quantity']
        size = bag[item_id]['item_data']['size']
        material = bag[item_id]['item_data']['material']
        colour = bag[item_id]['item_data']['colour']

        bag_items.append({
            'product': product,
            'quantity': quantity,
            'size': size,
            'material': material,
            'colour': colour
        })

    grand_total = total + delivery

    context = {
        'bag_items': bag_items,
        'total': total,
        'delivery': delivery,
        'grand_total': grand_total,
    }

    return context
