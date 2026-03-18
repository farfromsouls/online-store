import os

from django.shortcuts import render
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import JsonResponse, HttpResponse
from django.core.serializers.json import DjangoJSONEncoder
from django.forms.models import model_to_dict

from django_redis import get_redis_connection

from .models import *


REDIS_TTL = os.environ.get('REDIS_TTL')

def MainPageView(request):
    redis_conn = get_redis_connection('default')
    key = "first_by_rating"

    if request.user.is_authenticated:
        bucket = CustomUser.objects.get(username=request.user).Bucket
    else:
        bucket = request.session.get('bucket', {})

    if redis_conn.exists(key):
        ids = json.loads(redis_conn.get(key))
        products = Product.objects.filter(id__in=ids).order_by("-Rating")
        data = {"products": products, "bucket": bucket}
        return render(request, "index.html", context=data)

    products = Product.objects.order_by("-Rating")[:16]
    ids = list(products.values_list('id', flat=True))
    data = {"products": products, "bucket": bucket}

    redis_conn.setex(key, REDIS_TTL, json.dumps(ids))
    return render(request, "index.html", context=data)

def LoadMoreProducts(request):
    redis_conn = get_redis_connection('default')
    page = int(request.GET.get('page', 1))
    key = f"products_page_{page}"
    products_per_page = 16
    
    if request.user.is_authenticated:
        bucket = CustomUser.objects.get(username=request.user).Bucket
    else:
        bucket = request.session.get('bucket', {})

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
        product_id_str = str(product.id)
        products_data.append({
            'id': product.id,
            'Name': product.Name,
            'Cost': str(product.Cost),
            'Image_url': product.Image.url if product.Image else '',
            'in_bucket': product_id_str in bucket,    
        })

    response_data = {
        'products': products_data,
        'has_next': products_page.has_next()
    }

    redis_conn.setex(key, REDIS_TTL, json.dumps(response_data))
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
    
    stars = int(product_dict["Rating"])
    product_dict["Stars"] = "★"*stars + "☆"*(5-stars)
    
    for field_name, value in product_dict.items():
        if hasattr(value, 'url'):       
            product_dict[field_name] = value.url if value else None
        
    reviews_list = []
    for review in reviews:
        review_dict = model_to_dict(review)
        for field_name, value in review_dict.items():
            if hasattr(value, 'url'):
                review_dict[field_name] = value.url if value else None
            if field_name == "Author":
                review_dict[field_name] = review.Author.username
        reviews_list.append(review_dict)
        
    bucket = request.session.get('bucket', {})
    data = {"product": product_dict, "reviews": reviews_list, "bucket": bucket}

    redis_conn.setex(key, REDIS_TTL, json.dumps(data, cls=DjangoJSONEncoder))
    return render(request, "product.html", context=data)

def AddToBucket(request, id, amount):
    if request.user.is_authenticated:
        user = CustomUser.objects.get(username=request.user)
        user.Bucket[str(id)] = amount
        user.save()
        return JsonResponse({"success": True})
    
    bucket = request.session.get('bucket', {})
    bucket[str(id)] = amount
    request.session['bucket'] = bucket
    request.session.modified = True
    return JsonResponse({"success": True})

def Bucket(request):
    if request.user.is_authenticated:
        bucket = request.user.Bucket
    else:
        bucket = request.session.get('bucket', {})
        
    data = {"bucket_products": []}
    total_cost = 0  
    
    for product_id, amount in bucket.items():
        product = Product.objects.get(id=product_id)
        product_data = model_to_dict(product)
        product_data["bucket_amount"] = amount
        product_data["total_price"] = product.Cost * amount 
        total_cost += product_data["total_price"]
        data["bucket_products"].append(product_data)
    
    data["total_cost"] = total_cost  
    return render(request, "bucket.html", context=data)

    
    