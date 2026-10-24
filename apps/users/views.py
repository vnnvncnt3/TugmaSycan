from django.shortcuts import render, redirect
from django.contrib.auth import get_user_model

User = get_user_model()

def register_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        if User.objects.filter(username=username).exists():
            return render(request, "register/register.html", {
                "error": "Username already exists."
            })
        User.objects.create_user(username=username, password=password)
        return redirect("login:login")
    return render(request, "register/register.html")