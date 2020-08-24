from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from .models import Product, Category, Colour, Size, Material

# Create your views here.


def all_products(request):
    """ A view to return the products page """

    selected_category = request.GET.get('category', None)

    if selected_category:
        products = Product.objects.filter(category__name=selected_category)
    else:
        products = Product.objects.all()

    categories = Category.objects.all()
    paginator = Paginator(products, 6)
    page = request.GET.get('page')

    try:
        products = paginator.page(page)
    except PageNotAnInteger:
        products = paginator.page(1)

    except EmptyPage:
        products = paginator.page(paginator.num_pages)

    context = {
        'products': products,
        'categories': categories,
        'selected_category': selected_category,
        'page': page,
    }

    return render(request, 'products/products.html', context)


def product_detail(request, product_id):
    """ A view to show individual product details """

    product = get_object_or_404(Product, pk=product_id)
    colours = Colour.objects.all()
    sizes = Size.objects.all()
    materials = Material.objects.all()

    context = {
        'product': product,
        'sizes': sizes,
        'colours': colours,
        'materials': materials,
    }

    return render(request, 'products/product_detail.html', context)
