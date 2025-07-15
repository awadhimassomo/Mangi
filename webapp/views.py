from django.shortcuts import render
import os
import json
from django.http import JsonResponse
from django.views.decorators.csrf import ensure_csrf_cookie

# Create your views here.
def dashboard(request):
    """
    View function for the dashboard page
    """
    from inventory.models import Product, Category, Sales, SalesItem
    from registration.models import Business
    from django.db.models import Sum, Count
    from django.utils import timezone
    import datetime
    
    # Fetch the business data - just taking the first one for demonstration
    business = None
    try:
        business = Business.objects.first()
    except:
        pass
    
    # Fetch categories for the tabs
    categories = Category.objects.all().order_by('categoryName')[:5]
    
    # Fetch products for display
    products = Product.objects.all().order_by('-date_created')[:8]
    
    # Get low-stock products
    low_stock_products = Product.objects.filter(quantity__lte=10).order_by('quantity')[:5]
    
    # Get real sales stats from the database
    today = timezone.now().date()
    week_start = today - datetime.timedelta(days=today.weekday())
    month_start = today.replace(day=1)
    
    # Daily sales
    daily_sales = Sales.objects.filter(
        transaction_id__transaction_date=today,
        isDeleted=False
    ).aggregate(total=Sum('total_amount'))
    
    # Weekly sales
    weekly_sales = Sales.objects.filter(
        transaction_id__transaction_date__gte=week_start,
        transaction_id__transaction_date__lte=today,
        isDeleted=False
    ).aggregate(total=Sum('total_amount'))
    
    # Monthly sales
    monthly_sales = Sales.objects.filter(
        transaction_id__transaction_date__gte=month_start,
        transaction_id__transaction_date__lte=today,
        isDeleted=False
    ).aggregate(total=Sum('total_amount'))
    
    # Find top selling products
    top_selling = SalesItem.objects.filter(
        sale__isDeleted=False
    ).values('product').annotate(
        total_sold=Sum('quantity')
    ).order_by('-total_sold')[:3]
    
    top_products = []
    for item in top_selling:
        if item['product']:
            try:
                product = Product.objects.get(id=item['product'])
                top_products.append({
                    'product': product,
                    'total_sold': item['total_sold']
                })
            except Product.DoesNotExist:
                pass
    
    # Combine the stats in a dictionary
    sales_stats = {
        'daily_sales': daily_sales['total'] or 0,
        'weekly_sales': weekly_sales['total'] or 0,
        'monthly_sales': monthly_sales['total'] or 0,
        'top_products': top_products,
        'top_regular_products': products[:3],  # Fallback products if top_products is empty
    }
    
    context = {
        'title': 'Business Dashboard',
        'business': business,
        'categories': categories,
        'products': products,
        'low_stock_products': low_stock_products,
        'sales_stats': sales_stats,
    }
    
    # Use a more specific template path
    template_path = os.path.join('webapp', 'dashboard.html')
    print(f"Looking for template at: {template_path}")
    
    return render(request, template_path, context)

def sales(request):
    """
    View function for the sales page.
    """
    from inventory.models import Sales, SalesItem, Product
    from django.db.models import Sum, Count, Avg
    from django.utils import timezone
    import datetime
    
    # Get date ranges
    today = timezone.now().date()
    week_start = today - datetime.timedelta(days=today.weekday())
    month_start = today.replace(day=1)
    
    # Previous period calculations (for growth metrics)
    prev_month_start = (month_start - datetime.timedelta(days=1)).replace(day=1)
    prev_month_end = month_start - datetime.timedelta(days=1)
    
    # Total Sales Amount
    total_sales = Sales.objects.filter(
        isDeleted=False
    ).aggregate(total=Sum('total_amount'))
    
    # Previous period sales
    prev_period_sales = Sales.objects.filter(
        transaction_id__transaction_date__gte=prev_month_start,
        transaction_id__transaction_date__lte=prev_month_end,
        isDeleted=False
    ).aggregate(total=Sum('total_amount'))
    
    # Calculate growth percentage
    current_total = total_sales['total'] or 0
    prev_total = prev_period_sales['total'] or 1  # Avoid division by zero
    sales_growth = ((current_total - prev_total) / prev_total) * 100 if prev_total > 0 else 0
    sales_growth_abs = abs(sales_growth)  # Calculate absolute value
    
    # Total Orders
    total_orders = Sales.objects.filter(isDeleted=False).count()
    
    # Previous period orders
    prev_period_orders = Sales.objects.filter(
        transaction_id__transaction_date__gte=prev_month_start,
        transaction_id__transaction_date__lte=prev_month_end,
        isDeleted=False
    ).count()
    
    # Calculate orders growth percentage
    orders_growth = ((total_orders - prev_period_orders) / prev_period_orders) * 100 if prev_period_orders > 0 else 0
    orders_growth_abs = abs(orders_growth)  # Calculate absolute value
    
    # Average Order Value
    avg_order = Sales.objects.filter(isDeleted=False).aggregate(avg=Avg('total_amount'))
    
    # Previous period average
    prev_avg_order = Sales.objects.filter(
        transaction_id__transaction_date__gte=prev_month_start,
        transaction_id__transaction_date__lte=prev_month_end,
        isDeleted=False
    ).aggregate(avg=Avg('total_amount'))
    
    # Calculate AOV growth percentage
    current_avg = avg_order['avg'] or 0
    prev_avg = prev_avg_order['avg'] or 1  # Avoid division by zero
    aov_growth = ((current_avg - prev_avg) / prev_avg) * 100 if prev_avg > 0 else 0
    aov_growth_abs = abs(aov_growth)  # Calculate absolute value
    
    # Recent Sales
    recent_sales = Sales.objects.filter(isDeleted=False).order_by('-transaction_id__transaction_date')[:10]
    
    # Top selling products
    top_products = SalesItem.objects.filter(
        sale__isDeleted=False
    ).values('product').annotate(
        total_sold=Sum('quantity'),
        revenue=Sum('total_price')
    ).order_by('-total_sold')[:5]
    
    # Get product details
    top_selling_products = []
    max_revenue = 0
    
    # First find the maximum revenue for percentage calculations
    for item in top_products:
        if item['product'] and item['revenue']:
            if item['revenue'] > max_revenue:
                max_revenue = item['revenue']
    
    # Now prepare the products with percentage data
    for item in top_products:
        if item['product']:
            try:
                product = Product.objects.get(id=item['product'])
                # Calculate percentage for the progress bar width
                percentage = 0
                if max_revenue > 0 and item['revenue']:
                    percentage = (item['revenue'] / max_revenue) * 100
                    
                top_selling_products.append({
                    'product': product,
                    'total_sold': item['total_sold'],
                    'revenue': item['revenue'],
                    'percentage': percentage
                })
            except Product.DoesNotExist:
                pass
    
    # Monthly sales data for chart
    # Get the last 6 months
    months_data = []
    for i in range(5, -1, -1):
        # Calculate month date range
        target_month = today.replace(day=1) - datetime.timedelta(days=i*30)
        month_name = target_month.strftime('%b')  # Short month name
        
        # Get sales for this month
        month_sales = Sales.objects.filter(
            transaction_id__transaction_date__year=target_month.year,
            transaction_id__transaction_date__month=target_month.month,
            isDeleted=False
        ).aggregate(total=Sum('total_amount'))
        
        months_data.append({
            'month': month_name,
            'sales': month_sales['total'] or 0
        })
    
    context = {
        'title': 'Sales Analytics',
        'total_sales': current_total,
        'sales_growth': round(sales_growth, 1),
        'sales_growth_abs': round(sales_growth_abs, 1),  # Add absolute value
        'total_orders': total_orders,
        'orders_growth': round(orders_growth, 1),
        'orders_growth_abs': round(orders_growth_abs, 1),  # Add absolute value
        'avg_order': current_avg,
        'aov_growth': round(aov_growth, 1),
        'aov_growth_abs': round(aov_growth_abs, 1),  # Add absolute value
        'recent_sales': recent_sales,
        'top_selling_products': top_selling_products,
        'months_data': months_data,
        'is_growth_positive': {
            'sales': sales_growth >= 0,
            'orders': orders_growth >= 0,
            'aov': aov_growth >= 0,
        }
    }
    
    return render(request, 'webapp/sales.html', context)


def stocks(request):
    """
    View function for the stocks page.
    """
    from registration.models import Business
    from inventory.models import Product, Category
    from django.db.models import Sum, F, ExpressionWrapper, DecimalField
    from django.core.paginator import Paginator
    
    business = None
    try:
        business = Business.objects.first()
    except:
        pass
    
    # Get all products for the business
    all_products = Product.objects.all().order_by('-date_updated')
    
    # Calculate stock statistics from all products
    total_items = all_products.count()
    low_stock_items = all_products.filter(quantity__lte=F('min_stock')).count()
    out_of_stock = all_products.filter(quantity=0).count()
    
    # Calculate total stock value (price * quantity)
    stock_value = all_products.aggregate(
        total_value=Sum(ExpressionWrapper(F('price') * F('quantity'), output_field=DecimalField()))
    )['total_value'] or 0
    
    # Filter by category if requested
    category_id = request.GET.get('category')
    if category_id and category_id.isdigit() and category_id != 'all':
        all_products = all_products.filter(category_id=category_id)
    
    # Pagination
    paginator = Paginator(all_products, 10)  # Show 10 products per page
    page_number = request.GET.get('page')
    products = paginator.get_page(page_number)
    
    # Calculate total value for each product on current page
    for product in products:
        product.total_value = product.price * product.quantity
    
    # Get all product categories
    categories = Category.objects.all().order_by('categoryName')
    
    context = {
        'business': business,
        'products': products,
        'categories': categories,
        'total_items': total_items,
        'low_stock_items': low_stock_items,
        'out_of_stock': out_of_stock,
        'stock_value': stock_value
    }
    
    return render(request, 'webapp/stocks.html', context)


def expenses(request):
    """
    View function for the expenses page with dynamic data.
    """
    from registration.models import Business
    from inventory.models import Expense, ExpenseCategory
    from django.db.models import Sum, Count, F, Q
    from django.utils import timezone
    from django.core.paginator import Paginator
    import datetime
    
    # Get query parameters for filtering
    category_filter = request.GET.get('category', '')
    status_filter = request.GET.get('status', '')
    date_from = request.GET.get('date_from', '')
    date_to = request.GET.get('date_to', '')
    search_query = request.GET.get('search', '')
    page_number = request.GET.get('page', 1)
    
    # Get the business
    business = None
    try:
        business = Business.objects.first()
    except:
        pass
    
    # Base queryset
    expenses_queryset = Expense.objects.all().order_by('-date')
    
    # Apply filters
    if category_filter:
        expenses_queryset = expenses_queryset.filter(category=category_filter)
    
    if status_filter:
        if status_filter == 'approved':
            expenses_queryset = expenses_queryset.filter(approval_status=True)
        elif status_filter == 'pending':
            expenses_queryset = expenses_queryset.filter(approval_status=False)
    
    if date_from:
        try:
            date_from_obj = datetime.datetime.strptime(date_from, '%Y-%m-%d').date()
            expenses_queryset = expenses_queryset.filter(date__gte=date_from_obj)
        except ValueError:
            pass
    
    if date_to:
        try:
            date_to_obj = datetime.datetime.strptime(date_to, '%Y-%m-%d').date()
            expenses_queryset = expenses_queryset.filter(date__lte=date_to_obj)
        except ValueError:
            pass
    
    if search_query:
        expenses_queryset = expenses_queryset.filter(
            Q(vendor__icontains=search_query) |
            Q(notes__icontains=search_query)
        )
    
    # Calculate statistics
    total_expenses = expenses_queryset.count()
    approved_expenses = expenses_queryset.filter(approval_status=True).count()
    pending_expenses = expenses_queryset.filter(approval_status=False).count()
    
    # Calculate total spend
    total_spend = expenses_queryset.aggregate(total=Sum('total'))['total'] or 0
    
    # Calculate this month's spend
    current_month = timezone.now().month
    current_year = timezone.now().year
    first_day_of_month = datetime.date(current_year, current_month, 1)
    
    monthly_spend = expenses_queryset.filter(
        date__gte=first_day_of_month
    ).aggregate(total=Sum('total'))['total'] or 0
    
    # Calculate previous month's spend for comparison
    previous_month = current_month - 1 if current_month > 1 else 12
    previous_year = current_year if current_month > 1 else current_year - 1
    first_day_of_prev_month = datetime.date(previous_year, previous_month, 1)
    last_day_of_prev_month = first_day_of_month - datetime.timedelta(days=1)
    
    prev_monthly_spend = Expense.objects.filter(
        date__gte=first_day_of_prev_month,
        date__lte=last_day_of_prev_month
    ).aggregate(total=Sum('total'))['total'] or 0
    
    # Calculate spend change percentage
    if prev_monthly_spend > 0:
        spend_change_percent = ((monthly_spend - prev_monthly_spend) / prev_monthly_spend) * 100
    else:
        spend_change_percent = 100 if monthly_spend > 0 else 0
    
    spend_change_percent_abs = abs(spend_change_percent)
    
    # Get expense categories for filter dropdown
    expense_categories = [category[0] for category in Expense.CATEGORY_CHOICES]
    
    # Get expenses by category for the current month
    category_expenses = []
    for category in expense_categories:
        category_total = expenses_queryset.filter(
            category=category,
            date__gte=first_day_of_month
        ).aggregate(total=Sum('total'))['total'] or 0
        
        # Get previous month's category total for comparison
        prev_category_total = Expense.objects.filter(
            category=category,
            date__gte=first_day_of_prev_month,
            date__lte=last_day_of_prev_month
        ).aggregate(total=Sum('total'))['total'] or 0
        
        # Calculate percentage change
        if prev_category_total > 0:
            category_change_percent = ((category_total - prev_category_total) / prev_category_total) * 100
        else:
            category_change_percent = 100 if category_total > 0 else 0
        
        category_expenses.append({
            'name': category,
            'total': category_total,
            'change_percent': category_change_percent,
            'is_increase': category_change_percent > 0
        })
    
    # Paginate expenses
    paginator = Paginator(expenses_queryset, 10)  # 10 expenses per page
    expenses_page = paginator.get_page(page_number)
    
    context = {
        'business': business,
        'expenses': expenses_page,
        'total_expenses': total_expenses,
        'approved_expenses': approved_expenses,
        'pending_expenses': pending_expenses,
        'total_spend': total_spend,
        'monthly_spend': monthly_spend,
        'spend_change_percent': spend_change_percent,
        'spend_change_percent_abs': spend_change_percent_abs,
        'expense_categories': expense_categories,
        'category_expenses': category_expenses,
        'category_filter': category_filter,
        'status_filter': status_filter,
        'date_from': date_from,
        'date_to': date_to,
        'search_query': search_query,
    }

    return render(request, 'webapp/Expenses.html', context)


def suppliers(request):
    """
    View function for the suppliers management page
    """
    from inventory.models import Supplier
    from registration.models import Business
    from django.db.models import Sum, Count, F, Q
    from django.utils import timezone
    from django.core.paginator import Paginator
    import datetime
    
    # Get the business (taking the first one for demonstration)
    business = None
    try:
        business = Business.objects.first()
    except:
        pass
    
    # Get search query if present
    search_query = request.GET.get('search', '')
    supplier_type_filter = request.GET.get('supplier_type', 'all')
    page_number = request.GET.get('page', 1)
    
    # Base queryset
    suppliers_queryset = Supplier.objects.filter(isDeleted=False)
    if business:
        suppliers_queryset = suppliers_queryset.filter(business=business)
    
    # Apply supplier type filter if provided
    if supplier_type_filter and supplier_type_filter != 'all':
        suppliers_queryset = suppliers_queryset.filter(supplierType=supplier_type_filter)
        
    # Apply search filter if provided
    if search_query:
        suppliers_queryset = suppliers_queryset.filter(
            Q(supplierName__icontains=search_query) | 
            Q(contactPerson__icontains=search_query) |
            Q(contactEmail__icontains=search_query) |
            Q(contactPhone__icontains=search_query)
        )
    
    # Calculate statistics
    today = timezone.now().date()
    current_month = today.replace(day=1)
    last_month = (current_month - datetime.timedelta(days=1)).replace(day=1)
    
    # Total suppliers
    total_suppliers = suppliers_queryset.count()
    
    # Suppliers added this month
    new_suppliers_this_month = 0
    if hasattr(Supplier, 'date_created'):
        new_suppliers_this_month = Supplier.objects.filter(
            isDeleted=False,
            date_created__gte=current_month
        ).count()
    
    # Active suppliers (not marked as deleted)
    active_suppliers = suppliers_queryset.filter(isDeleted=False).count()
    
    # Active suppliers last month
    last_month_active = 0
    if hasattr(Supplier, 'date_created'):
        last_month_active = Supplier.objects.filter(
            isDeleted=False,
            date_created__lt=current_month
        ).count()
    
    active_change_percent = 0
    if last_month_active > 0:
        active_change_percent = ((active_suppliers - last_month_active) / last_month_active) * 100
    
    # Paginate suppliers
    paginator = Paginator(suppliers_queryset, 10)  # 10 suppliers per page
    suppliers_page = paginator.get_page(page_number)
    
    # Get supplier type choices from model
    supplier_type_choices = dict(Supplier.supplierType_CHOICES)
    
    # Calculate orders this month (placeholder - replace with actual order data when available)
    try:
        from inventory.models import PurchaseOrder
        orders_this_month = PurchaseOrder.objects.filter(
            date_created__gte=current_month,
            isDeleted=False
        ).count()
        
        last_month_orders = PurchaseOrder.objects.filter(
            date_created__gte=last_month,
            date_created__lt=current_month,
            isDeleted=False
        ).count()
        
        orders_change_percent = 0
        if last_month_orders > 0:
            orders_change_percent = ((orders_this_month - last_month_orders) / last_month_orders) * 100
        
        # Calculate amount spent MTD (Month to Date)
        amount_spent_mtd = PurchaseOrder.objects.filter(
            date_created__gte=current_month,
            isDeleted=False
        ).aggregate(total=Sum('total_amount'))['total'] or 0
        
        last_month_amount = PurchaseOrder.objects.filter(
            date_created__gte=last_month,
            date_created__lt=current_month,
            isDeleted=False
        ).aggregate(total=Sum('total_amount'))['total'] or 0
        
        amount_change_percent = 0
        if last_month_amount > 0:
            amount_change_percent = ((amount_spent_mtd - last_month_amount) / last_month_amount) * 100
    except Exception as e:
        # If PurchaseOrder model doesn't exist or there's another error, use placeholders
        orders_this_month = 0
        orders_change_percent = 0
        amount_spent_mtd = 0
        amount_change_percent = 0
    
    # Format the amount spent for display
    if amount_spent_mtd >= 1000000:
        amount_spent_formatted = f"TZS {amount_spent_mtd/1000000:.1f}M"
    elif amount_spent_mtd >= 1000:
        amount_spent_formatted = f"TZS {amount_spent_mtd/1000:.1f}K"
    else:
        amount_spent_formatted = f"TZS {amount_spent_mtd}"
    
    context = {
        'business': business,
        'suppliers': suppliers_page,
        'total_suppliers': total_suppliers,
        'new_suppliers_this_month': new_suppliers_this_month,
        'active_suppliers': active_suppliers,
        'active_change_percent': round(active_change_percent, 1),
        'active_change_percent_abs': round(abs(active_change_percent), 1),
        'orders_this_month': orders_this_month,
        'orders_change_percent': round(orders_change_percent, 1),
        'orders_change_percent_abs': round(abs(orders_change_percent), 1),
        'amount_spent_mtd': amount_spent_formatted,
        'amount_change_percent': round(amount_change_percent, 1),
        'amount_change_percent_abs': round(abs(amount_change_percent), 1),
        'supplier_type_choices': supplier_type_choices,
        'supplier_type_filter': supplier_type_filter,
        'search_query': search_query
    }
    
    return render(request, 'webapp/suppliers.html', context)


def customers(request):
    """
    View function for the customers management page
    """
    from registration.models import Customer, Business
    from django.db.models import Sum, Count, F, Q, Avg
    from django.utils import timezone
    from django.core.paginator import Paginator
    import datetime
    
    # Get the business (taking the first one for demonstration)
    business = None
    try:
        business = Business.objects.first()
    except:
        pass
    
    # Get search query if present
    search_query = request.GET.get('search', '')
    customer_type = request.GET.get('customer_type', 'all')
    page_number = request.GET.get('page', 1)
    
    # Base queryset
    customers_queryset = Customer.objects.filter(isDeleted=False)
    if business:
        customers_queryset = customers_queryset.filter(business=business)
    
    # Apply customer type filter
    if customer_type and customer_type != 'all':
        # For now we don't have a customer type field in the model
        # We'll use frequency as a proxy for different types
        if customer_type == 'vip':
            customers_queryset = customers_queryset.filter(frequency__gte=5)
        elif customer_type == 'regular':
            customers_queryset = customers_queryset.filter(frequency__lt=5, frequency__gt=1)
        elif customer_type == 'corporate':
            # This would be handled properly when a proper customer_type field is added
            pass
            
    # Apply search filter if provided
    if search_query:
        customers_queryset = customers_queryset.filter(
            Q(name__icontains=search_query) | 
            Q(phoneNumber__icontains=search_query)
        )
    
    # Calculate statistics
    today = timezone.now().date()
    current_month = today.replace(day=1)
    last_month = (current_month - datetime.timedelta(days=1)).replace(day=1)
    
    # Total customers
    total_customers = customers_queryset.count()
    
    # Customers added this month
    new_customers_this_month = customers_queryset.filter(date_added__gte=current_month).count()
    
    # VIP customers (using frequency as proxy)
    vip_customers = customers_queryset.filter(frequency__gte=5).count()
    
    # VIP customers last month
    vip_customers_last_month = customers_queryset.filter(
        frequency__gte=5, 
        date_added__lt=current_month
    ).count()
    
    new_vip_this_month = customers_queryset.filter(
        frequency__gte=5,
        date_added__gte=current_month
    ).count()
    
    # Calculate customer lifetime value and revenue (placeholder implementation)
    # In a real implementation, this would come from sales/transaction data
    try:
        from sales.models import Sale
        # Calculate average lifetime value
        avg_lifetime_value = Sale.objects.filter(
            customer__in=customers_queryset,
            isDeleted=False
        ).values('customer').annotate(
            total_spent=Sum('total_amount')
        ).aggregate(avg=Avg('total_spent'))['avg'] or 0
        
        # Average lifetime value last period
        avg_lifetime_value_last_period = Sale.objects.filter(
            customer__in=customers_queryset.filter(date_added__lt=current_month),
            isDeleted=False
        ).values('customer').annotate(
            total_spent=Sum('total_amount')
        ).aggregate(avg=Avg('total_spent'))['avg'] or 0
        
        # Calculate revenue this month
        revenue_this_month = Sale.objects.filter(
            date__gte=current_month,
            isDeleted=False
        ).aggregate(total=Sum('total_amount'))['total'] or 0
        
        # Revenue last month
        revenue_last_month = Sale.objects.filter(
            date__gte=last_month,
            date__lt=current_month,
            isDeleted=False
        ).aggregate(total=Sum('total_amount'))['total'] or 0
        
        # Calculate percentage changes
        avg_change_percent = 0
        if avg_lifetime_value_last_period > 0:
            avg_change_percent = ((avg_lifetime_value - avg_lifetime_value_last_period) / avg_lifetime_value_last_period) * 100
            
        revenue_change_percent = 0
        if revenue_last_month > 0:
            revenue_change_percent = ((revenue_this_month - revenue_last_month) / revenue_last_month) * 100
    except Exception as e:
        # If Sale model doesn't exist or there's another error, use placeholders
        avg_lifetime_value = 0
        avg_change_percent = 0
        revenue_this_month = 0
        revenue_change_percent = 0
    
    # Format monetary values
    def format_currency(amount):
        if amount >= 1000000:
            return f"TZS {amount/1000000:.1f}M"
        elif amount >= 1000:
            return f"TZS {amount/1000:.1f}K"
        else:
            return f"TZS {amount}"
    
    # Paginate customers
    paginator = Paginator(customers_queryset, 10)  # 10 customers per page
    customers_page = paginator.get_page(page_number)
    
    # Customer type options
    customer_type_choices = {
        'all': 'All Customers',
        'regular': 'Regular',
        'vip': 'VIP',
        'corporate': 'Corporate'
    }
    
    context = {
        'business': business,
        'customers': customers_page,
        'total_customers': total_customers,
        'new_customers_this_month': new_customers_this_month,
        'vip_customers': vip_customers,
        'new_vip_this_month': new_vip_this_month,
        'avg_lifetime_value': format_currency(avg_lifetime_value),
        'avg_change_percent': round(avg_change_percent, 1),
        'avg_change_percent_abs': round(abs(avg_change_percent), 1),
        'revenue_this_month': format_currency(revenue_this_month),
        'revenue_change_percent': round(revenue_change_percent, 1),
        'revenue_change_percent_abs': round(abs(revenue_change_percent), 1),
        'customer_type_choices': customer_type_choices,
        'customer_type': customer_type,
        'search_query': search_query
    }
    
    return render(request, 'webapp/customers.html', context)


def loans(request):
    """
    View function for the loans page.
    """
    from registration.models import Business
    from inventory.models import Loan
    from django.db.models import Sum, Count, F, Q
    from django.utils import timezone
    from django.core.paginator import Paginator
    import datetime
    
    # Get query parameters for filtering
    loan_type_filter = request.GET.get('loan_type', 'all')
    status_filter = request.GET.get('status', 'all')
    borrower_type_filter = request.GET.get('borrower_type', 'all')
    search_query = request.GET.get('search', '')
    date_from = request.GET.get('date_from', '')
    date_to = request.GET.get('date_to', '')
    page_number = request.GET.get('page', 1)
    
    # Fetch the business
    business = None
    try:
        business = Business.objects.first()
    except:
        pass
    
    # Base query: get all loans for the business that aren't deleted
    loans_queryset = Loan.objects.filter(business=business, is_deleted=False)
    
    # Apply filters
    if loan_type_filter and loan_type_filter != 'all':
        loans_queryset = loans_queryset.filter(loan_type=loan_type_filter)
    
    if status_filter and status_filter != 'all':
        loans_queryset = loans_queryset.filter(status=status_filter)
    
    if borrower_type_filter and borrower_type_filter != 'all':
        loans_queryset = loans_queryset.filter(borrower_type=borrower_type_filter)
    
    if search_query:
        loans_queryset = loans_queryset.filter(
            Q(loan_id__icontains=search_query) | 
            Q(borrower_name__icontains=search_query)
        )
    
    if date_from:
        try:
            date_from_obj = datetime.datetime.strptime(date_from, '%Y-%m-%d').date()
            loans_queryset = loans_queryset.filter(date_issued__gte=date_from_obj)
        except ValueError:
            pass
    
    if date_to:
        try:
            date_to_obj = datetime.datetime.strptime(date_to, '%Y-%m-%d').date()
            loans_queryset = loans_queryset.filter(date_issued__lte=date_to_obj)
        except ValueError:
            pass
    
    # Calculate statistics
    today = timezone.now().date()
    current_month = today.replace(day=1)
    last_month = (current_month - datetime.timedelta(days=1)).replace(day=1)
    
    # Calculate total outstanding (total amount - paid amount)
    total_outstanding = loans_queryset.aggregate(
        total=Sum(F('amount') - F('paid_amount'))  
    )['total'] or 0
    
    # Calculate total repaid
    total_repaid = loans_queryset.aggregate(total=Sum('paid_amount'))['total'] or 0
    
    # Active loans count
    active_loans = loans_queryset.filter(status='active').count()
    
    # Overdue loans count
    overdue_loans = loans_queryset.filter(status='overdue').count()
    
    # Calculate month-over-month changes
    last_month_outstanding = Loan.objects.filter(
        business=business,
        is_deleted=False,
        created_at__lt=current_month
    ).aggregate(total=Sum(F('amount') - F('paid_amount')))['total'] or 0
    
    if last_month_outstanding > 0:
        outstanding_change_percent = ((total_outstanding - last_month_outstanding) / last_month_outstanding) * 100
    else:
        outstanding_change_percent = 100 if total_outstanding > 0 else 0
    
    last_month_repaid = Loan.objects.filter(
        business=business,
        is_deleted=False,
        updated_at__lt=current_month,
        paid_amount__gt=0
    ).aggregate(total=Sum('paid_amount'))['total'] or 0
    
    if last_month_repaid > 0:
        repaid_change_percent = ((total_repaid - last_month_repaid) / last_month_repaid) * 100
    else:
        repaid_change_percent = 100 if total_repaid > 0 else 0
    
    # Get last month's active loans for comparison
    last_month_active = Loan.objects.filter(
        business=business,
        is_deleted=False,
        created_at__lt=current_month,
        status='active'
    ).count()
    
    active_change_percent = 0
    if last_month_active > 0:
        active_change_percent = ((active_loans - last_month_active) / last_month_active) * 100
    
    # Get new overdue loans this month
    new_overdue_this_month = Loan.objects.filter(
        business=business,
        is_deleted=False,
        status='overdue',
        updated_at__gte=current_month
    ).count()
    
    # Paginate loans
    paginator = Paginator(loans_queryset, 10)  # 10 loans per page
    loans_page = paginator.get_page(page_number)
    
    context = {
        'business': business,
        'loans': loans_page,
        'total_outstanding': total_outstanding,
        'total_repaid': total_repaid,
        'active_loans': active_loans,
        'overdue_loans': overdue_loans,
        'outstanding_change_percent': round(outstanding_change_percent, 1),
        'outstanding_change_percent_abs': round(abs(outstanding_change_percent), 1),
        'repaid_change_percent': round(repaid_change_percent, 1),
        'repaid_change_percent_abs': round(abs(repaid_change_percent), 1),
        'active_change_percent': round(active_change_percent, 1),
        'active_change_percent_abs': round(abs(active_change_percent), 1),
        'new_overdue_this_month': new_overdue_this_month,
        'loan_type_filter': loan_type_filter,
        'status_filter': status_filter,
        'borrower_type_filter': borrower_type_filter,
        'search_query': search_query,
        'date_from': date_from,
        'date_to': date_to,
        'loan_type_choices': dict(Loan.LOAN_TYPE_CHOICES),
        'status_choices': dict(Loan.STATUS_CHOICES),
        'borrower_type_choices': dict(Loan.BORROWER_TYPE_CHOICES),
    }
    
    return render(request, 'webapp/loans.html', context)


def suppliers(request):
    """
    View function for the suppliers page.
    """
    return render(request, 'webapp/suppliers.html')


def customers(request):
    """
    View function for the customers page.
    """
    return render(request, 'webapp/customers.html')


def orders(request):
    """
    View function for the purchase orders page (orders to suppliers).
    """
    from registration.models import Business
    from inventory.models import Order, OrderItem, Supplier
    from django.db.models import Count, Sum, F
    from django.utils import timezone
    from django.core.paginator import Paginator
    import datetime
    
    # Get query parameters
    status_filter = request.GET.get('status', 'all')
    search_query = request.GET.get('search', '')
    page_number = request.GET.get('page', 1)
    
    # Fetch the business
    business = None
    try:
        business = Business.objects.first()
    except:
        pass
    
    # Base queryset
    orders_queryset = Order.objects.all()
    
    # Apply status filter if specified
    if status_filter and status_filter != 'all':
        orders_queryset = orders_queryset.filter(status=status_filter)
    
    # Apply search filter if provided
    if search_query:
        orders_queryset = orders_queryset.filter(
            order_number__icontains=search_query
        ) | orders_queryset.filter(
            supplier__supplierName__icontains=search_query
        )
    
    # Order by most recent first
    orders_queryset = orders_queryset.order_by('-order_date')
    
    # Count total orders
    total_orders = Order.objects.count()
    
    # Count orders by status
    pending_orders = Order.objects.filter(status='Pending').count()
    approved_orders = Order.objects.filter(status='Completed').count()
    cancelled_orders = Order.objects.filter(status='Cancelled').count()
    
    # Calculate total spend for current month
    current_month = timezone.now().month
    current_year = timezone.now().year
    
    # Calculate the first day of the current month
    first_day_of_month = datetime.date(current_year, current_month, 1)
    
    # Get orders for the current month that are completed
    monthly_orders = Order.objects.filter(
        order_date__gte=first_day_of_month,
        status='Completed'
    )
    
    # Calculate total spend by summing the order items
    monthly_spend = OrderItem.objects.filter(
        order__in=monthly_orders
    ).aggregate(total=Sum(F('unit_price') * F('quantity')))['total'] or 0
    
    # Calculate previous month's spend for comparison
    previous_month = current_month - 1 if current_month > 1 else 12
    previous_year = current_year if current_month > 1 else current_year - 1
    first_day_of_prev_month = datetime.date(previous_year, previous_month, 1)
    last_day_of_prev_month = first_day_of_month - datetime.timedelta(days=1)
    
    prev_monthly_orders = Order.objects.filter(
        order_date__gte=first_day_of_prev_month,
        order_date__lte=last_day_of_prev_month,
        status='Completed'
    )
    
    prev_monthly_spend = OrderItem.objects.filter(
        order__in=prev_monthly_orders
    ).aggregate(total=Sum(F('unit_price') * F('quantity')))['total'] or 0
    
    # Calculate spend change percentage
    if prev_monthly_spend > 0:
        spend_change_percent = ((monthly_spend - prev_monthly_spend) / prev_monthly_spend) * 100
    else:
        spend_change_percent = 100 if monthly_spend > 0 else 0
    
    # Calculate absolute value for template display
    spend_change_percent_abs = abs(spend_change_percent)
    
    # Count new orders this month
    new_orders_count = Order.objects.filter(
        order_date__gte=first_day_of_month
    ).count()
    
    # Count active suppliers
    active_suppliers_count = Supplier.objects.count()
    
    # Count new suppliers this month
    # Note: Since Supplier model doesn't have a date_created field, we'll set this to 0
    # This could be enhanced in the future by adding a date_created field to the Supplier model
    new_suppliers_count = 0
    
    # Paginate the orders
    paginator = Paginator(orders_queryset, 10)  # 10 orders per page
    orders_page = paginator.get_page(page_number)
    
    # Prepare context
    context = {
        'business': business,
        'orders': orders_page,
        'total_orders': total_orders,
        'pending_orders': pending_orders,
        'approved_orders': approved_orders,
        'cancelled_orders': cancelled_orders,
        'monthly_spend': monthly_spend,
        'spend_change_percent': spend_change_percent,
        'spend_change_percent_abs': spend_change_percent_abs,
        'active_suppliers_count': active_suppliers_count,
        'new_orders_count': new_orders_count,
        'new_suppliers_count': new_suppliers_count,
        'status_filter': status_filter,
        'search_query': search_query,
    }
    
    return render(request, 'webapp/orders.html', context)


def reports(request):
    """
    View function for the reports and analytics page.
    """
    from registration.models import Business
    business = None
    try:
        business = Business.objects.first()
    except:
        pass
    return render(request, 'webapp/reports.html', {'business': business})


@ensure_csrf_cookie
def login(request):
    """
    View function for the login page.
    """
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            phone_number = data.get('phoneNumber')
            password = data.get('password')
            remember_me = data.get('rememberMe', False)
            
            # Here you would typically authenticate the user
            # For now, we'll just return dummy successful response
            # In a real app, you'd verify credentials and generate tokens
            
            # Set session expiration based on remember_me flag
            if remember_me:
                # Set session to expire in 30 days (or your preferred duration)
                request.session.set_expiry(60 * 60 * 24 * 30)  # 30 days in seconds
            else:
                # Use default session expiration (browser close)
                request.session.set_expiry(0)
            
            # Dummy success response for testing
            return JsonResponse({
                'access': 'dummy_access_token',
                'refresh': 'dummy_refresh_token',
                'username': 'Test User',
                'email': 'test@example.com',
                'phoneNumber': phone_number,
                'role': 'owner',
                'is_staff': True,
                'owner_id': 1,
                'businesses': [
                    {
                        'id': 1,
                        'name': 'Test Business',
                        'type': 'retail'
                    }
                ]
            })
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    else:
        # For GET requests, render the login template
        return render(request, 'webapp/login.html')


def signup(request):
    """
    View function for the signup page.
    """
    return render(request, 'webapp/Signup.html')


def forgot_password_page(request):
    """
    View function for the forgot password page.
    This only renders the template. The actual API calls are made directly to the SMS app endpoints.
    """
    return render(request, 'webapp/forgot_password.html')


def reset_password_page(request):
    """
    View function for the reset password page.
    This only renders the template. The actual API calls are made directly to the SMS app endpoints.
    """
    return render(request, 'webapp/reset_password.html')


def phone_format_help(request):
    """
    Developer helper view to show valid phone numbers in the database.
    This helps when testing the password reset functionality.
    Only available in DEBUG mode.
    """
    from django.conf import settings
    from django.http import JsonResponse
    from django.contrib.auth import get_user_model
    
    if not settings.DEBUG:
        return JsonResponse({'error': 'This view is only available in DEBUG mode'}, status=403)
    
    User = get_user_model()
    # Get a sample of phone numbers from the database (for testing only)
    sample_users = User.objects.all().values('phoneNumber')[:5]
    
    return JsonResponse({
        'message': 'This is a developer helper to show valid phone formats in the database.',
        'note': 'Use these phone numbers when testing the password reset functionality.',
        'phone_format_tips': [
            'Phone numbers should be entered in the format: 255XXXXXXXXX',
            'Do not use a leading + sign',
            'Do not use a leading 0',
            'Do not include spaces or dashes',
        ],
        'sample_phone_numbers': [user['phoneNumber'] for user in sample_users if user['phoneNumber']]
    })


def test_reset_page(request):
    """
    Developer tool page for testing the SMS app's password reset API with different phone number formats.
    """
    return render(request, 'webapp/test_reset.html')
