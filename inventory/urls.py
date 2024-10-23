from django.urls import path
from . import views
from .views import CreateProduct, InstallmentListView, NotifySupplierAPIView, PreOrderNotificationAPIView, SyncProductsView, SyncSaleView, SyncSupplierView, SyncTransactionView, create_sales, product_suggestions

app_name = 'inventory'

urlpatterns = [
    path('',views.getRoutes,name="routes"),
    path('products/',views.getProducts,name="products"),
    path('products/create/',CreateProduct.as_view(),name="create-product"),
    path('products/<str:pk>/update/',views.updateProduct,name="update-product"),
    path('products/<str:pk>/delete/',views.deleteProduct,name="delete-product"),
    path('products/sync/', SyncProductsView.as_view(), name='sync_products'),


    
    #search
    path('products/suggestions/',product_suggestions, name='product_suggestions'),
    

  

#Supplierpath
    path('suppliers/',views.getSuppliers,name="suppliers"),
    path('suppliers/create/',views.createSupplier,name="create-supplier"),
    path('suppliers/<uuid:id>/update/',views.updateSupplier,name="update-supplier"),
    path('suppliers/<str:pk>/delete/',views.deleteSupplier,name="delete-supplier"),
    path('suppliers/sync/', SyncSupplierView.as_view(), name='sync_suppliers'),
#Categorypath
    path('categories/',views.getCategories,name="categories"),
    path('categories/create/',views.createCategory,name="create-category"),
    path('categories/<str:pk>/update/',views.updateCategory,name="update-category"),
    path('categories/<str:pk>/delete/',views.deleteCategory,name="delete-category"),

#Transactionpath
    path('transactions/',views.getTransactions,name="transactions"),
    path('transactions/create/',views.createTransaction,name="create-transaction"),
    path('transactions/<str:pk>/update/',views.updateTransaction,name="update-transaction"),
    path('transactions/<str:pk>/delete/',views.deleteTransaction,name="delete-transaction"),
    path('sync-transaction/', SyncTransactionView.as_view(), name='sync-transaction'),

  
#Warehousepath
    path('warehouses/',views.getWarehouses,name="warehouses"),
    path('warehouses/create/',views.CreateWarehouses,name="create-warehouse"),
    path('warehouses/<str:pk>/update/',views.updateWarehouse,name="update-warehouse"),
    path('warehouses/<str:pk>/delete/',views.deleteWarehouse,name="delete-warehouse"),

#Filterpath
    path('products/create/', CreateProduct.as_view(), name='create-product'),


    path('purchase/',views.list_purchases,name="purchase"),
    path('sync-sale/', SyncSaleView.as_view(), name='sync-sale'),
    path('purchase/<int:pk>/delete/', views.delete_purchase, name='delete_purchase'),
    path('sales/create/', create_sales, name='create_sales'),
    path('installments/create/', views.create_installment, name='create_installment'),
    path('installments/', InstallmentListView.as_view(), name='installment-list'),
    # Other URL patterns...


#expense

    path('expenses/', views.list_expenses, name='list_expenses'),
    path('expenses/create/', views.create_expense, name='create_expense'),
    path('expenses/<int:pk>/', views.get_expense, name='get_expense'),
    path('expenses/<int:pk>/update/', views.update_expense, name='update_expense'),
    path('expenses/<int:pk>/delete/', views.delete_expense, name='delete_expense'),




#Preordering and Ordering
   path('preorder-notification/', PreOrderNotificationAPIView.as_view(), name='preorder-notification'),
   path('notify-supplier/', NotifySupplierAPIView.as_view(), name='notify-supplier'),  # Create order endpoint
    path('complete_order/<str:token>/', views.complete_order_view, name='complete_order'),
    path('process_order/<str:token>/', views.process_order, name='process_order'),
    path('cancel_order/<str:token>/', views.cancel_order, name='cancel_order'),
    path('send_order/<str:token>/', views.send_order, name='send_order'),
    path('orders/create/', views.CreateOrderAPIView.as_view(), name='create_order'), 

]
