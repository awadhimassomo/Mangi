from django.urls import path
from . import views
from django.views.generic import TemplateView

urlpatterns = [
    path('', views.index, name='index'),  # Example URL pattern
    path('developer/', TemplateView.as_view(template_name='developer.html'), name='developer'),
]
