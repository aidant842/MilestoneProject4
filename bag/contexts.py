from django.shortcuts import get_object_or_404
from products.models import Product


def bag_contents(request):

    bag_items = []
    total = 0
    delivery = total * .10
    bag = request.session.get('bag', {})

    for item_id, value in bag.items():
        quantity = value['quantity']
        material = value['material']
        colour = value['colour']
        size = value['size']
        product = get_object_or_404(Product, pk=item_id)

        bag_items.append({
            'item_id': item_id,
            'quantity': quantity,
            'size': size,
            'material': material,
            'colour': colour,
            'product': product,
        })

        total += quantity * product.price
    print(bag)
    grand_total = total + delivery

    context = {
        'bag_items': bag_items,
        'total': total,
        'delivery': delivery,
        'grand_total': grand_total,
    }

    return context