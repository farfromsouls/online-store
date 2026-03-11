from django.shortcuts import render
from django.http.response import HttpResponse


def mainview(request):
    return HttpResponse("Hello world")