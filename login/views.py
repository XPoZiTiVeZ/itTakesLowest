from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import login, logout
from .models import CustomUser
from .backends import CustomBackend

def registerUser(request):
    if not request.user.is_authenticated:
        if request.method == 'POST':
            username = request.POST.get('username')
            password = request.POST.get('password')
            password2 = request.POST.get('repeat-password')
        
            if password != password2:
                messages.error(request, 'Пароли не совпадают')
                return render(request, 'login/register.html')
            
            if CustomUser.objects.filter(username=username).exists():
                messages.error(request, 'Имя пользователя уже занято')
                return render(request, 'login/register.html')
            
            user = CustomUser.objects.create_user(username=username, password=password)
            user.username = username
            user.save()
            
            user = CustomBackend.authenticate(request, username=username, password=password)
            login(request, user, 'login.backends.CustomBackend')
            return redirect('home')
        return render(request, 'login/register.html')
    else:
        messages.warning(request, 'Вы уже имеете аккаунт')
        return redirect('home')

def loginUser(request):
    if not request.user.is_authenticated:
        if request.method == 'POST':
            username = request.POST.get('username')
            password = request.POST.get('password')

            user = CustomBackend.authenticate(request, username=username, password=password)
            
            print(user)
            if not user:
                messages.error(request, 'Неправильная почта или пароль')
                return render(request, 'login/login.html')
            
            login(request, user, 'login.backends.CustomBackend')
            messages.success(request, f'Добро пожаловать, {user.username}')
            print('in')
            return redirect('home')
        return render(request, 'login/login.html')
    else:
        messages.warning(request, 'Вы уже вошли аккаунт')
        return redirect('home')

def logoutUser(request):
    if request.user.is_authenticated:
        logout(request)
        return redirect('home')
    return redirect('home')

def profile(request):
    pass