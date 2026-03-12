from django.shortcuts import render
from django.core.paginator import Paginator
from django.http import JsonResponse
from .models import *

def MainPageView(request):
    products = Product.objects.order_by("-Rating")[:16]
    return render(request, "index.html", context={"products": products})

def LoadMoreProducts(request):
    page = int(request.GET.get('page', 1))
    products_per_page = 16
    all_products = Product.objects.order_by("-Rating")
    paginator = Paginator(all_products, products_per_page)
    
    try:
        products_page = paginator.page(page + 1) 
    except:
        return JsonResponse({'products': [], 'has_next': False})
    
    products_data = []
    for product in products_page:
        products_data.append({
            'id': product.id,
            'Name': product.Name,
            'Cost': product.Cost,
            'Image_url': product.Image.url if product.Image else '',
        })
    
    return JsonResponse({
        'products': products_data,
        'has_next': products_page.has_next()
    })

def ProductPageView(request, id):
    product = Product.objects.get(id=id)
    reviews = Review.objects.filter(Product=product)
    
    data = {"product": product, "reviews": reviews}
    return render(request, "product.html", context=data)