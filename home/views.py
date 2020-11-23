from django.shortcuts import render
from products.models import Product

# Create your views here.


def index(request):
    """ A view to return the index page """

    products = Product.objects.all()

    context = {
        'products': products,
    }

    return render(request, 'home/index.html', context)


def error_404_view(request, exception):
    """ A view to return custom 404 page """

    template = 'home/404.html'

    return render(request, template, status=404)


def error_500_view(request):
    """ A view to return custom 500 page """

    template = 'home/500.html'

    return render(request, template, status=500)
