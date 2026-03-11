from django.shortcuts import render
from .models import *


def MainPageView(request):
    products = Product.objects.all()
    return render(request, "index.html", context={"products": products})