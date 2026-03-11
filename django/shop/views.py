from django.shortcuts import render
from .models import *


def MainPageView(request):
    books = Book.objects.all()
    data = {book.title: [] for book in books}
    return render(request, "index.html", context=data)