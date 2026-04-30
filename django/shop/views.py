import json

from django.shortcuts import render, redirect
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import JsonResponse

from django_redis import get_redis_connection

from .models import Product, Review


def get_bucket(request):
    if request.user.is_authenticated:
        return request.user.Bucket
    return request.session.get('bucket', {})

def MainPageView(request):
    bucket = get_bucket(request)

    products = Product.objects.filter(Available=True).order_by("-Rating")[:16]
    
    data = {"products": products, "bucket": bucket}
    return render(request, "index.html", context=data)

def LoadMoreProducts(request):
    page = int(request.GET.get('page', 1))
    products_per_page = 16
    bucket = get_bucket(request)
    
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
    
    return JsonResponse(response_data) 

def ProductPageView(request, id):
    authenticated = request.user.is_authenticated
    
    bucket = get_bucket(request)
    product = Product.objects.get(id=id)
    reviews = Review.objects.filter(Product=product).select_related('Author')
    
    lookfor_now = []
    can_review = False
    
    if authenticated:
        can_review = True
        for review in reviews:
            if review.Author.username == request.user.username:
                can_review = False
                break
    
    response_data = {
        'product': product,
        'reviews': reviews,
        'bucket': [str(k) for k in bucket.keys()],
        'lookfor_now': lookfor_now,
        'can_review': can_review
    }
        
    return render(request, "product.html", context=response_data)

def AddToBucket(request, id, amount):

    product_obj = Product.objects.get(id=id)
    available = product_obj.Amount
        
    if available < amount:
        return JsonResponse({"success": False})
    
    if request.user.is_authenticated:
        user = request.user
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
    bucket = get_bucket(request)
    
    product_ids = [int(id_str) for id_str in bucket.keys()] if bucket else []
    bucket_products = Product.objects.filter(id__in=product_ids)
    amount_dict = {int(k): int(v) for k, v in bucket.items()}
    
    bucket_products_with_amounts = []
    total_cost = 0
    
    for product in bucket_products:
        amount = amount_dict.get(product.id, 0) 
        product.bucket_amount = amount
        product.total_price = product.Cost * amount
        total_cost += product.total_price 
        bucket_products_with_amounts.append(product)
    
    data = {
        "bucket_products": bucket_products_with_amounts,
        "total_cost": total_cost,
        "can_buy": request.user.is_authenticated
    }
    return render(request, "bucket.html", context=data)

def AddReview(request, product_id):
    if request.method == 'POST' and request.user.is_authenticated:
        rating = int(request.POST.get('rating', 0))
        text = request.POST.get('text', '').strip()
        user = request.user
        product = Product.objects.get(id=product_id)
        has_review = Review.objects.filter(
            Product_id=product_id, 
            Author=user
        ).exists()
        
        if not has_review:
            if 1 <= rating <= 5 and text:
                Review.objects.create(
                    Product=product,
                    Author=user,
                    Rating=rating,
                    Text=text
                )
        else:
            old_review = Review.objects.filter(Product=product, Author=user)
            old_review.update(Text=text, Rating=rating)
    
    return redirect(f'/product/{product_id}/', product_id=product_id)

def Buy(request):
    if request.method == 'POST' and request.user.is_authenticated:
        user = request.user
        bucket_items = user.Bucket.items()  
        
        if bucket_items:
            notification = {
                'user': user.username,
                'items': dict(bucket_items),  
            }
            
            redis_queue = get_redis_connection("queue")
            redis_queue.rpush("bot:notifications", json.dumps(notification))
            
            for product_id, qty in bucket_items:
                product = Product.objects.get(id=int(product_id))
                product.update_amount(int(qty)) 
            
            user.Bucket = {}
            user.save()
    
    return redirect('/bucket/')