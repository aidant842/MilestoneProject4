from django.shortcuts import render, redirect


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

    print(bag)
    request.session['bag'] = bag

    return redirect(redirect_url)
