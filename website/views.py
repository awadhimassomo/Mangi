
import logging
from django.shortcuts import get_object_or_404, render
from django.http import HttpResponse
from django.template.loader import render_to_string
from weasyprint import HTML
from inventory.models import Order
from registration.models import BusinessProfile

 #Suppress WeasyPrint and fontTools INFO level logging
logging.getLogger('weasyprint').setLevel(logging.WARNING)
logging.getLogger('fontTools.subset').setLevel(logging.WARNING)




def index(request):
    return render(request, 'index.html')

# Create your view here
def developer_view(request):
    return render(request, 'developer.html')

def order_detail(request, token):
    # Fetch the order based on the token
    order = get_object_or_404(Order, token=token)
    
    # Pass the order to the template
    return render(request, 'order.html', {'order': order})

def generate_order_pdf(request, token):
    order = get_object_or_404(Order, token=token)
    items = order.items.all()  # Get the list of related items
    business_profile = get_object_or_404(BusinessProfile, business=order.business)

    html_string = render_to_string('order_pdf.html', {
        'order': order,
        'items': items,
        'business_profile': business_profile
    })
    
    html = HTML(string=html_string)
    pdf = html.write_pdf()

    response = HttpResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] = f'inline; filename="order_{order.order_number}.pdf"'
    return response