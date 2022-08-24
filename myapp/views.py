# from django.contrib.sessions import session
from django.shortcuts import redirect, render
from django.http import HttpResponse
from .models import OrderDetail, Product
from django.contrib.auth.decorators import login_required
from django.views.generic import ListView,DetailView,TemplateView
from django.views.generic.edit import CreateView,UpdateView,DeleteView
from django.urls import reverse_lazy,reverse
from django.core.paginator import Paginator
from django.http.response import HttpResponseNotFound,JsonResponse
from django.shortcuts import get_object_or_404
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
# from django.views import View
import json
import stripe

# Create your views here.
def index(request):
    return HttpResponse("Hello sagar")

def product(request):
    # from database
    page_obj=products=Product.objects.all()
    product_name = request.GET.get('product_name')
    if product_name !=' ' and product_name is not None:
        page_obj=products.filter(name__icontains=product_name)


    paginator = Paginator(page_obj,3)
    page_number = request.GET.get('page')
    page_obj=paginator.get_page(page_number)
#after applying paginator these context no longer there
    # context={
    #     'products':products
    # }
#after applying paginator new context will be
    context={
        'page_obj':page_obj
    }
    return render(request, 'myapp/index.html',context)  

#class based view for above products view[ListView]
class ProductListView(ListView):
    model = Product
    template_name='myapp/index.html'
    context_object_name='products'
    paginate_by = 3

#Function Based Views
def product_detail(request,id):
    product=Product.objects.get(id=id)
    context={
        'product' : product
    }
    return render(request, 'myapp/detail.html',context)

#Class Based view for above details function view 
class ProductdDetailView(DetailView):
    model = Product
    template_name='myapp/detail.html'
    context_object_name = 'product'
    pk_url_kwarg = 'pk'

    def get_context_data(self, **kwargs):
        context = super(ProductdDetailView,self).get_context_data(**kwargs)
        context['stripe_publishable_key']=settings.STRIPE_PUBLISHABLE_KEY
        return context

@login_required
#for function based view 
def add_product(request):
    if request.method == 'POST':
           name=request.POST.get('name')
           price=request.POST.get('price')
           desc=request.POST.get('desc')
           image=request.FILES['upload']
           seller_name = request.user
           product=Product(name=name,price=price,desc=desc,image=image, seller_name= seller_name)
           product.save()
    return render(request,'myapp/addproduct.html')

#Class based view for above add_product function views
class ProductCreateView(CreateView):
    model= Product
    fields = ['name','price','desc','image','seller_name']
    # product_form.html


#for function based views
def update_product(request,id):
    product=Product.objects.get(id=id)
    
    if request.method=='POST':
        product.name=request.POST.get('name')
        product.price=request.POST.get('price')
        product.desc=request.POST.get('desc')
        product.image=request.FILES['upload']
        product.save()
        return redirect('/myapp/products')
    context={
        'product':product,
    }
    return render(request,'myapp/updateProduct.html',context)

#Class based views of above update product function views
#  
class ProductUpdateView(UpdateView):
    model= Product
    fields = ['name','price','desc','image','seller_name']
    template_name_suffix = '_update_form'


def delete_product(request,id):
    product = Product.objects.get(id=id)
    context = {
        'product':product,
    }
    if request.method == 'POST':
        product.delete()
        return redirect('/myapp/products')
    
    return render(request,'myapp/delete.html',context)

#Class Based View for Above Delete function based views
class ProductDelete(DeleteView):
    model = Product
    success_url = reverse_lazy('myapp:products')



def my_listings(request):
    product = Product.objects.filter(seller_name=request.user) 
    context = {
        'product':product,
    }
    return render(request,'myapp/mylistings.html',context)

@csrf_exempt
def create_checkout_session(request,id):
    # request_data = json.loads(request.body)
    product=get_object_or_404(Product,pk=id)
    stripe.api_key=settings.STRIPE_SECRET_KEY
    checkout_session = stripe.checkout.Session.create(
        customer_email = request.user.email,
        payment_method_types = ['card'],
        line_items = [
            {
                'price_data':{
                    'currency':'usd',
                    'product_data' : {
                        'name' : product.name,
                    },
                    'unit_amount' : int(product.price*100),
                },
                'quantity' : 1,
            }
        ],
        mode = 'payment', 
        success_url=request.build_absolute_uri(reverse('myapp:success'))+"?session_id={CHECKOUT_SESSION_ID}",
        cancel_url=request.build_absolute_uri(reverse('myapp:failed')),
    )

    order = OrderDetail()
    order.customer_username =request.user.username
    order.product = product
    order.stripe_payment_intent = checkout_session['payment_intent']
    order.amount = int(product.price*100)
    order.save()
    return JsonResponse({'sessionId':checkout_session.id})

# class CreateCheckoutSessionView(View):
#     def post(self, request, *args, **kwargs):
#         product=get_object_or_404(Product,pk=id)
#         price = price.objects.get(id=self.kwargs["pk"])
#         stripe.api_key=settings.STRIPE_SECRET_KEY
#         checkout_session = stripe.checkout.Session.create(
#             customer_email =product.email,
#             payment_method_types = ['card'],
#             line_items = [
#                 {
#                     'price_data':{
#                         'currency':'usd',
#                         'product_data' : {
#                             'name' : product.name,
#                         },
#                         'unit_amount' : int(product.price *100),
#                     },
#                     'quantity' : 1,
#                 }
#             ],
#             mode = 'payment', 
#             success_url=reverse('myapp:success')+ "?session_id={CHECKOUT_SESSION_ID}",

        #     cancel_url=reverse('myapp:failed'),
        # )

        # order = OrderDetail()
        # order.customer_username=request.user.username
        # order.product = product
        # order.stripe_payment_intent = checkout_session('payment_intent')
        # order.amount = int(price.price *100)
        # order.save()
        # return JsonResponse({'sessionId':checkout_session.id})

class PaymentSuccessView(TemplateView):
    template_name ='myapp/payment_success.html'
    
    def get(self,request,*args,**kwargs):
        session_id = request.GET.get('session_id')
        if session_id is None:
            return HttpResponseNotFound
        session=stripe.checkout.Session.retrieve(session_id)
        stripe.api_key=settings.STRIPE_SECRET_KEY
        order = get_object_or_404(OrderDetail,stripe_payment_intent = session.payment_intent)
        order.has_paid  = True
        order.save()
        return render(request,self.template_names)

class PaymentFailedView(TemplateView):
    template_name = 'myapp/payment_failed.html'