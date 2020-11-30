from django.shortcuts import (render, redirect, reverse,
                              HttpResponse, get_object_or_404)
from django.contrib import messages

from products.models import Product


def view_bag(request):
    """ A view to return the bag contents page """

    return render(request, 'bag/bag.html')


def add_to_bag(request, item_id):
    """ Add a quantity of an item to the bag """
    product = Product.objects.get(pk=item_id)
    quantity = int(request.POST.get('quantity'))
    redirect_url = request.POST.get('redirect_url')
    bag = request.session.get('bag', [])
    size = request.POST.get('size', None)
    material = request.POST.get('material', None)
    colour = request.POST.get('colour', None)
    new_item = True

    for item in bag:

        if (item["item_id"] == item_id and item["item_size"] == size
            and item["item_material"] == material
                and item["item_colour"] == colour):
            item["quantity"] += quantity
            item["total"] = product.price * item["quantity"]
            new_item = False
            messages.success(request, "Updated the quantity"
                             f"of {product.name} in you're bag")
            break

    if new_item:
        bag.append({
            "item_id": item_id,
            "item_size": size,
            "item_material": material,
            "item_colour": colour,
            "quantity": quantity,
            "total": product.price * quantity
        })
        messages.success(request, f'Added { quantity }'
                         f'of { product.name } to the bag')

    request.session['bag'] = bag
    return redirect(redirect_url)


def adjust_bag(request, item_id):
    """ Adjust a specific item in the bag """

    bag_item = get_object_or_404(Product, pk=item_id)
    quantity = int(request.POST.get('quantity', 0))
    bag = request.session.get('bag', [])
    size = request.POST.get('product_size', None)
    material = request.POST.get('product_material', None)
    colour = request.POST.get('product_colour', None)

    for item in bag:
        if (item["item_id"] == item_id and item["item_size"] == size
            and item["item_material"] == material
                and item["item_colour"] == colour):
            product = item

            if quantity > 0:
                product['quantity'] = quantity
                product["total"] = bag_item.price * quantity
                messages.success(
                    request, f'Quantity of { bag_item.name }'
                    f' updated to { item["quantity"] }')

            else:
                bag.remove(product)
                messages.success(
                    request, f"{ bag_item.name } was removed from you're bag")

    request.session['bag'] = bag

    return redirect(reverse('view_bag'))


def remove_from_bag(request, item_id):
    """ A view to remove a product from the bag """

    try:
        bag = request.session.get('bag', [])
        bag_item = get_object_or_404(Product, pk=item_id)
        size = request.POST['size']
        material = request.POST['material']
        colour = request.POST['colour']

        for item in bag:
            if (item["item_id"] == item_id and item["item_size"] == size
                and item["item_material"] == material
                    and item["item_colour"] == colour):
                product = item

                bag.remove(product)
                messages.success(
                    request, f"{ bag_item.name } was removed from you're bag")

        request.session['bag'] = bag
        return HttpResponse(status=200)
    except Exception as e:
        messages.error(request, f'Error removing item from the bag: {e}')
        return HttpResponse(status=500)
