from django.shortcuts import render

# Create your views here.

def Register(request):
    return render(request,'registration\Register.html')

def Login(request):
    return render(request,'registration\Login.html' )

def Forget(request):
    return render(request,'registration\Forget.html' )


def index(request):
    return render(request,'registration\index.html' )

