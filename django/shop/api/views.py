from rest_framework.views import APIView
from rest_framework.response import Response
from django_redis import get_redis_connection

from shop.models import Product, REDIS_TTL

import json


class ProductView(APIView):
    authentication_classes = []
    permission_classes = []
    
    def get(self, request, id):
        redis_conn = get_redis_connection("default")
        key = f"product_{id}"
        
        if redis_conn.exists(key):
            product = redis_conn.get(key)
            product = json.loads(product)
            return Response(product)
        
        product = Product.objects.get(id=id).to_dict()
        redis_conn.setex(key, REDIS_TTL, json.dumps(product))
        return Response(product)