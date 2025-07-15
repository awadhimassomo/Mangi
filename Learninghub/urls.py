from django.urls import path
from . import views

app_name = 'learninghub'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('courses/', views.course_list, name='course_list'),
    path('courses/<int:course_id>/', views.course_detail, name='course_detail'),
    path('lesson/<int:lesson_id>/', views.lesson_detail, name='lesson_detail'),
    path('progress/', views.progress_view, name='progress'),
    path('sponsors/', views.sponsor_list, name='sponsor_list'),
    path('sponsors/<int:sponsor_id>/', views.sponsor_detail, name='sponsor_detail'),
    path('resources/', views.resources, name='resources'),
    path('tutorials/', views.tutorials, name='tutorials'),
    path('workshops/', views.workshops, name='workshops'),
    path('certifications/', views.certifications, name='certifications'),
    path('community/', views.community, name='community'),
]
