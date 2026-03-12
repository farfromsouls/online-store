from django.urls import path
from . import views

urlpatterns = [
    path('', views.MainPageView, name='main'),
    path('load-more-products/', views.LoadMoreProducts, name='load_more_products'),
    path('product/<int:id>/', views.ProductPageView, name='product'),
]