from django.shortcuts import render, redirect


def view_bag(request):
    """ A view to return the bag contents page """

    return render(request, 'bag/bag.html')


def add_to_bag(request, item_id):
    """ Add a quantity of an item to the bag """

    quantity = int(request.POST.get('quantity', 0))
    redirect_url = request.POST.get('redirect_url')
    bag = request.session.get('bag', {})
    size = request.POST.get('size', None)
    material = request.POST.get('material', None)
    colour = request.POST.get('colour', None)

    # Check to see if the product in already in the bag
    if item_id in list(bag.keys()):
        print('An item with this ID is already in the bag')
        # Check to see if the product options are the same
        # if so, increment quantity
        if (size == bag[item_id]['item_data']['size'] and
           material == bag[item_id]['item_data']['material'] and
           colour == bag[item_id]['item_data']['colour']):
            print('Product options are the same')
            bag[item_id]['item_data']['quantity'] += quantity
        else:
            print('need logic to not overwrite current'
                  f'item with this ID: { item_id }')

            bag[item_id] = {'item_data': {'size': size,
                                          'material': material,
                                          'colour': colour,
                                          'quantity': quantity
                                          }
                            }

    # if bag is empty, or product with a new ID, add it to the bag
    else:
        bag[item_id] = {'item_data': {'size': size,
                                      'material': material,
                                      'colour': colour,
                                      'quantity': quantity
                                      }
                        }

    print(bag)
    request.session['bag'] = bag

    return redirect(redirect_url)
