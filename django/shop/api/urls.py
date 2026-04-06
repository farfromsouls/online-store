from django.urls import path
from . import views

urlpatterns = [
    path('product/<int:id>/', views.AdminProductDetailView.as_view(), name='product'), #GET, PUT, PATCH, DELETE
    path('products/', views.AdminProductListView.as_view(), name='products')           #GET, POST
]