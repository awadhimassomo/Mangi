from django.shortcuts import render
from rest_framework import viewsets
from .models import CustomUser
from .serializers import CustomUserSerializer
from rest_framework import generics


# Create your views here.

def Register(request):
    return render(request,'registration\Register.html')

def Login(request):
    return render(request,'registration\Login.html' )

def Forget(request):
    return render(request,'registration\Forget.html' )


def index(request):
    return render(request,'registration\index.html' )




class UserListView(generics.ListCreateAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer

class UserDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer

class UserCreateView(generics.CreateAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer


