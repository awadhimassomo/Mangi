

from django.shortcuts import render

def index(request):
    return render(request, 'index.html')

# Create your view here
def developer_view(request):
    return render(request, 'developer.html')
