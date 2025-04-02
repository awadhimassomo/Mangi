import logging
import os
from django.shortcuts import get_object_or_404, render
from django.http import HttpResponse
from django.template.loader import render_to_string
from weasyprint import HTML
from inventory.models import Order
from registration.models import BusinessProfile
from django.views.generic import TemplateView

# Suppress WeasyPrint and fontTools INFO level logging
logging.getLogger('weasyprint').setLevel(logging.WARNING)
logging.getLogger('fontTools.subset').setLevel(logging.WARNING)



def index(request):
    return render(request, 'index.html')

# Developer View
def developer_view(request):
    return render(request, 'developer.html')

# Order Detail View
def order_detail(request, token):
    # Fetch the order based on the token
    order = get_object_or_404(Order, token=token)
    
    # Pass the order to the template
    return render(request, 'order.html', {'order': order})

# Generate Order PDF
def generate_order_pdf(request, token):
    try:
        # Fetch the order and related data
        order = get_object_or_404(Order, token=token)
        items = order.items.all()  # Get the list of related items
        business_profile = get_object_or_404(BusinessProfile, business=order.business)

        # Render the template to an HTML string
        html_string = render_to_string('order_pdf.html', {
            'order': order,
            'items': items,
            'business_profile': business_profile
        })

        # Generate the PDF using WeasyPrint
        html = HTML(string=html_string)
        pdf = html.write_pdf()

        # Return the PDF as an HTTP response
        response = HttpResponse(pdf, content_type='application/pdf')
        response['Content-Disposition'] = f'inline; filename="order_{order.order_number}.pdf"'
        return response
    except Exception as e:
        logging.error(f"Error generating PDF: {e}")
        return HttpResponse("An error occurred while generating the PDF.", status=500)
    
class PrivacyPolicyView(TemplateView):
    """
    View for rendering the privacy policy page.
    """
    template_name = 'policy.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # No need to query BusinessProfile - just pass a template context
        # The privacy policy will use static data instead of dynamic user data
        context['company_name'] = "Mangi"  # Replace with your company name
        context['company_email'] = "info@sotech.com"
        context['company_address'] = "1730 Dodoma,"
        context['company_phone'] = "+255687046323"
        
        return context
