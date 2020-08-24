from django.shortcuts import render

# Create your views here.


def all_products(request):
    """ A view to return the all products page """

    context = {

    }

    return render(request, 'products/products.html', context)
