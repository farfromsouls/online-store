from django.urls import path
from . import views

urlpatterns = [
    path('', views.MainPageView, name='main'),
    path('load-more-products/', views.LoadMoreProducts, name='load_more_products'),
    path('bucket/', views.Bucket, name='bucket'),
    path('product/<int:id>/', views.ProductPageView, name='product'),
    path('add_to_bucket/<int:id>_<int:amount>', views.AddToBucket, name='add_to_bucket')
]