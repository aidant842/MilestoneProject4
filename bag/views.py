from django.shortcuts import render, redirect, get_object_or_404
from products.models import Product


def view_bag(request):
    """ A view to return the bag contents page """

    return render(request, 'bag/bag.html')
