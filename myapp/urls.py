from urllib import request
from django.contrib import admin
from django.urls import path
from . import views

app_name= 'myapp'

urlpatterns = [
    path('',views.index), 
#using function based view
    path('products/',views.product,name='products'),
#Using Class based view
    # path('products/',views.ProductListView.as_view(),name='products'),

#Using function based views
    # path('products/<int:id>/',views.product_detail,name='product_detail'),
#for Class based View
    path('products/<int:pk>/',views.ProductdDetailView.as_view(),name='product_detail'),
#for function Based views of add products
    # path('products/add/',views.add_product,name='add_product'),
#for Class Based views of create products
    path('products/add/',views.ProductCreateView.as_view(),name='add_product'),

#for function Based view
    # path('products/update/<int:id>',views.update_product,name='update_product'),

#for Class Based View
    path('products/update/<int:pk>',views.ProductUpdateView.as_view(),name='update_product'),

#for function Based view of delete
    # path('products/delete/<int:id>',views.delete_product,name='delete_product'),

#for Class Based view of Delete
    path('products/delete/<int:pk>',views.ProductDelete.as_view(),name='delete_product'),

    path('products/mylistings',views.my_listings,name='mylistings'),

    path('success/',views.PaymentSuccessView.as_view(),name='success'),

    path('failed/',views.PaymentFailedView.as_view(),name='failed'),

    path('api/checkout-session/<id>',views.create_checkout_session,name='api_checkout_session'),
    
]