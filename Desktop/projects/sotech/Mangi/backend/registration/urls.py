from django.urls import path

from . import views

app_name ='Registration'


urlpatterns =[
path('register', views.Register, name ='register'),
path('login', views.Login, name ='login'),
path('forget', views.Forget, name ='forget'),
path('index', views.index, name ='index'),

]