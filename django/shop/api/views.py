from rest_framework import generics
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework import serializers

from shop.models import Product, REDIS_TTL

from django_redis import get_redis_connection

import json


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = '__all__' 

class AdminProductDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [IsAdminUser]
    lookup_field = 'id'
    
    def update(self, request, *args, **kwargs):
        response = super().update(request, *args, **kwargs)
        
        redis_conn = get_redis_connection("default")
        key = f"product_{kwargs['id']}"
        redis_conn.delete(key)
        
        return response
    
    def retrieve(self, request, *args, **kwargs):
        redis_conn = get_redis_connection("default")
        key = f"product_{kwargs['id']}"
        
        if redis_conn.exists(key):
            product = redis_conn.get(key)
            return Response(json.loads(product))
        
        response = super().retrieve(request, *args, **kwargs)
        redis_conn.setex(key, REDIS_TTL, json.dumps(response.data))
        
        return response

class AdminProductListView(generics.ListCreateAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [IsAdminUser]
    
    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        
        redis_conn = get_redis_connection("default")
        redis_conn.delete("products_list")
        
        return response