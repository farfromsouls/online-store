from django.contrib.auth import login, logout, authenticate
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_protect, csrf_exempt
from django.http.response import JsonResponse
from .models import CustomUser


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
        
        session_bucket = request.session.get('bucket', {})
        
        result_bucket = {}
        for key in set(session_bucket) | set(user.Bucket):  
            result_bucket[key] = session_bucket.get(key, 0) + user.Bucket.get(key, 0)
        user.Bucket = result_bucket
        user.save()
        if 'bucket' in request.session:
            del request.session['bucket']
        
        login(request, user)
        
    return redirect('account')

@csrf_protect
def Register(request):
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

@csrf_exempt
def Auth(request):
    if request.method == "POST":
        login = request.POST.get("login")
        password = request.POST.get("password")
        admin = authenticate(request, username=login, password=password)
        
        if admin == None:
            return JsonResponse({"success": False})
        return JsonResponse({"success": True})
    return JsonResponse({"Error": "Method not allowed"})