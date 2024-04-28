from django.urls import path
from . import views
from .views import CreateProduct

app_name = 'inventory'

urlpatterns = [
    path('',views.getRoutes,name="routes"),
    path('products/',views.getProducts,name="products"),
    path('products/create/',CreateProduct.as_view(),name="create-product"),
    path('products/<str:pk>/update/',views.updateProduct,name="update-product"),
    path('products/<str:pk>/delete/',views.deleteProduct,name="delete-product"),

#Supplierpath
    path('suppliers/',views.getSuppliers,name="suppliers"),
    path('suppliers/create/',views.createSupplier,name="create-supplier"),
    path('suppliers/<str:pk>/update/',views.updateSupplier,name="update-supplier"),
    path('suppliers/<str:pk>/delete/',views.deleteSupplier,name="delete-supplier"),

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

#Warehousepath
    path('warehouses/',views.getWarehouses,name="warehouses"),
    path('warehouses/create/',views.CreateWarehouses.as_view(),name="create-warehouse"),
    path('warehouses/<str:pk>/update/',views.updateWarehouse,name="update-warehouse"),
    path('warehouses/<str:pk>/delete/',views.deleteWarehouse,name="delete-warehouse"),

#Filterpath
    path('products/filter/',views.ProductViewSet.as_view(),name="filter-products"),

]
