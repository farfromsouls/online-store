import os

from django.shortcuts import render, redirect
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import JsonResponse
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

    products = Product.objects.filter(Available=True).order_by("-Rating")[:16]
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
    
    all_products = Product.objects.filter(Available=True).order_by("-Rating")
    paginator = Paginator(all_products, products_per_page)

    try:
        products_page = paginator.page(page)
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
    authenticated = request.user.is_authenticated
    key = f"product_{id}"
    
    product = Product.objects.get(id=id)
    reviews = Review.objects.filter(Product=product)
    
    if authenticated:
        bucket = CustomUser.objects.get(username=request.user).Bucket
    else:
        bucket = request.session.get('bucket', {})
    
    lookfor_now = []
    keys = redis_conn.keys("product_*")
    
    can_review = False
    
    if authenticated:
        can_review = True
        for review in reviews:
            if review.Author.username == request.user.username:
                can_review = False
                break
    
    for key_item in keys:
        if key_item.decode('utf-8') != f"product_{id}" and len(lookfor_now)<4:
            cached_data = redis_conn.get(key_item)
            cached_product = json.loads(cached_data)
            if 'product' in cached_product:
                product_id = int(key_item.decode('utf-8').split('_')[1])
                lookfor_product = Product.objects.get(id=product_id)
                lookfor_now.append(lookfor_product)
    
    context = {
        'product': product,
        'reviews': reviews,
        'bucket': [str(k) for k in bucket.keys()],
        'lookfor_now': lookfor_now,
        'can_review': can_review
    }
    
    try:
        product_dict = product.to_dict()
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
        
        cache_data = {
            "product": product_dict,
            "reviews": reviews_list,
            "bucket": bucket,
        }
        redis_conn.setex(key, REDIS_TTL, json.dumps(cache_data, cls=DjangoJSONEncoder))
    except Exception as e:
        print(f"Error caching product {id}: {e}")
        
    return render(request, "product.html", context=context)

def AddToBucket(request, id, amount):

    product = Product.objects.get(id=id)
    if product.Amount < amount:
        return JsonResponse({"success": False})
    
    if request.user.is_authenticated:
        user = CustomUser.objects.get(username=request.user)
        if amount == 0:
            del user.Bucket[str(id)]
        else:
            user.Bucket[str(id)] = amount
        user.save()
        return JsonResponse({"success": True})
    
    bucket = request.session.get('bucket', {})
    if amount == 0:
        del bucket[str(id)]
    else:
        bucket[str(id)] = amount
    request.session['bucket'] = bucket
    request.session.modified = True
    return JsonResponse({"success": True})

def Bucket(request):
    if request.user.is_authenticated:
        bucket = request.user.Bucket
    else:
        bucket = request.session.get('bucket', {})
        
    bucket_products = []
    total_cost = 0  
    
    for product_id, amount in bucket.items():
        product = Product.objects.get(id=product_id)
        product.bucket_amount = amount
        product.total_price = product.Cost * amount
        total_cost += product.total_price
        bucket_products.append(product)
    
    data = {
        "bucket_products": bucket_products,
        "total_cost": total_cost,
        "can_buy": request.user.is_authenticated
    }
    return render(request, "bucket.html", context=data)

def AddReview(request, product_id):
    if request.method == 'POST' and request.user.is_authenticated:
        rating = int(request.POST.get('rating', 0))
        text = request.POST.get('text', '').strip()
        user = CustomUser.objects.get(username=request.user.username)
        product = Product.objects.get(id=product_id)
        
        if 1 <= rating <= 5 and text:
            Review.objects.create(
                Product=product,
                Author=user,
                Rating=rating,
                Text=text
            )
    
    return redirect(f'/product/{product_id}/', product_id=product_id)

def Buy(request):
    if request.method == 'POST' and request.user.is_authenticated:
        user = CustomUser.objects.get(username=request.user)
        for key, val in user.Bucket.items():
            product = Product.objects.get(id=key)
            product.update_amount(int(val))
        user.Bucket = {}
        user.save()
    
    return redirect(f'/bucket/')