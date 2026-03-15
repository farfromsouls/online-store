import json

from django.shortcuts import render
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import JsonResponse
from django.core.serializers.json import DjangoJSONEncoder
from django.forms.models import model_to_dict

from django_redis import get_redis_connection

from .models import *


def MainPageView(request):
    redis_conn = get_redis_connection('default') 
    key = "first_by_rating"
    
    if redis_conn.exists(key):
        ids = json.loads(redis_conn.get(key))
        products = Product.objects.filter(id__in=ids).order_by("-Rating")
        data = {"products": products}  
        return render(request, "index.html", context=data) 
    
    products = Product.objects.order_by("-Rating")[:16]
    ids = list(products.values_list('id', flat=True))
    data = {"products": products}  
    
    redis_conn.setex(key, 60, json.dumps(ids))
    return render(request, "index.html", context=data)

def LoadMoreProducts(request):
    redis_conn = get_redis_connection('default')
    page = int(request.GET.get('page', 1))
    key = f"products_page_{page}"
    products_per_page = 16

    if redis_conn.exists(key):
        cached_data = redis_conn.get(key)
        response_data = json.loads(cached_data)
        return JsonResponse(response_data)
    
    all_products = Product.objects.order_by("-Rating")
    paginator = Paginator(all_products, products_per_page)

    try:
        products_page = paginator.page(page + 1)
    except (EmptyPage, PageNotAnInteger):
        return JsonResponse({'products': [], 'has_next': False})

    products_data = []
    for product in products_page:
        products_data.append({
            'id': product.id,
            'Name': product.Name,
            'Cost': str(product.Cost), 
            'Image_url': product.Image.url if product.Image else '',
        })

    response_data = {
        'products': products_data,
        'has_next': products_page.has_next()
    }

    redis_conn.setex(key, 60, json.dumps(response_data))
    return JsonResponse(response_data)

def ProductPageView(request, id):
    redis_conn = get_redis_connection('default')
    key = f"product_{id}"

    if redis_conn.exists(key):
        cached_data = redis_conn.get(key)
        data = json.loads(cached_data)
        return render(request, "product.html", context=data)

    product = Product.objects.get(id=id)
    reviews = Review.objects.filter(Product=product)
    product_dict = model_to_dict(product)
    for field_name, value in product_dict.items():
        if hasattr(value, 'url'):       
            product_dict[field_name] = value.url if value else None
        
    reviews_list = []
    for review in reviews:
        review_dict = model_to_dict(review)
        for field_name, value in review_dict.items():
            if hasattr(value, 'url'):
                review_dict[field_name] = value.url if value else None
        reviews_list.append(review_dict)
    
    data = {"product": product_dict, "reviews": reviews_list}

    redis_conn.setex(key, 60, json.dumps(data, cls=DjangoJSONEncoder))
    return render(request, "product.html", context=data)