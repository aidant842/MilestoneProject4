from django.shortcuts import render, redirect, reverse, HttpResponse


def view_bag(request):
    """ A view to return the bag contents page """

    return render(request, 'bag/bag.html')


def add_to_bag(request, item_id):
    """ Add a quantity of an item to the bag """

    quantity = int(request.POST.get('quantity', 0))
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
            new_item = False
            break

    if new_item:
        bag.append({
            "item_id": item_id,
            "item_size": size,
            "item_material": material,
            "item_colour": colour,
            "quantity": quantity
        })

    request.session['bag'] = bag

    return redirect(redirect_url)


def adjust_bag(request, item_id):
    """ Adjust a specific item in the bag """

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

            else:
                bag.remove(product)

    request.session['bag'] = bag

    return redirect(reverse('view_bag'))


def remove_from_bag(request, item_id):
    """ A view to remove a product from the bag """

    try:
        bag = request.session.get('bag', [])
        size = request.POST.get('size', None)
        material = request.POST.get('material', None)
        colour = request.POST.get('colour', None)
        print(size, material, colour)

        for item in bag:
            if (item["item_id"] == item_id and item["item_size"] == size
               and item["item_material"] == material
               and item["item_colour"] == colour):
                product = item

                bag.remove(product)

        request.session['bag'] = bag
        return HttpResponse(status=200)
    except Exception as e:
        print(e)
        return HttpResponse(status=500)

