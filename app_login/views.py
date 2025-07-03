from django.shortcuts import render

# Create your views here.
from django.shortcuts import render, redirect
from django.views.decorators.cache import never_cache
from django.contrib.auth import logout as auth_logout, authenticate, login as auth_login

# Create your views here.
@never_cache
def login_page(request):
    auth_logout(request)  # Log out the user
    return render(request, 'login.html')

@never_cache
def login(request):
    auth_logout(request)  # Log out the user
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            auth_login(request, user)
            return redirect('menu')
        else:
            return render(request, 'login.html', {'error': 'Credenciales Invalidas'})
    return render(request, 'login.html')

def logout(request):
    auth_logout(request)
    return redirect('login')