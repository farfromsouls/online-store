from django.contrib.auth import login, logout, authenticate
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_protect
from .models import CustomUser

# Create your views here.
def Account(request):
    return render(request, "account.html")

@csrf_protect
def Login(request):
    if request.method == "POST":
        username=request.POST.get("username")
        password=request.POST.get("password")
        
        user = authenticate(request, username=username, password=password)
        
        if user == None:
            return redirect('account')
        login(request, user)
        return redirect('account')

@csrf_protect
def Register(request):
    print(request.POST)
    username=request.POST.get("username")
    email=request.POST.get("email")
    password1=request.POST.get("password1")
    password2=request.POST.get("password2")
    
    if password1 == password2:
        new_user = CustomUser.objects.create_user(
            username=username,
            email=email,
            password=password1
        )
    return redirect('account')

@csrf_protect
def Logout(request):
    logout(request)
    return redirect('account')