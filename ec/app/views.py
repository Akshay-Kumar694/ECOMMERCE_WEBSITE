from urllib import request
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from django.http import HttpResponseBadRequest 
from django.views import View
import razorpay
from . models import Product, Cart, Payment, OrderPlaced,Wishlist
from django.db.models import Count
from . forms import CustomerRegistrationForm, CustomerProfileForm, Customer
from django.contrib import messages
from django.db.models import Q
from django.conf import settings

# Create your views here.

def home(request):
    totalitem=0
    wishitem=0
    if request.user.is_authenticated:
        totalitem=len(Cart.objects.filter(user=request.user))
        wishitem=len(Cart.objects.filter(user=request.user))
    return render(request,"app/home.html",locals())

@login_required
def about(request):
    totalitem=0
    wishitem=0
    if request.user.is_authenticated:
        totalitem=len(Cart.objects.filter(user=request.user))
        wishitem=len(Cart.objects.filter(user=request.user))
    return render(request,"app/about.html",locals())

@login_required
def contact(request):
    totalitem=0
    wishitem=0
    if request.user.is_authenticated:
        totalitem=len(Cart.objects.filter(user=request.user))
        wishitem=len(Cart.objects.filter(user=request.user))
    return render(request,"app/contact.html",locals())

@method_decorator(login_required,name='dispatch')
class CategoryView(View):
    def get(self,request,val):
        totalitem=0
        wishitem=0
        if request.user.is_authenticated:
            totalitem=len(Cart.objects.filter(user=request.user))
            wishitem=len(Cart.objects.filter(user=request.user))
        product=Product.objects.filter(category=val)
        title=Product.objects.filter(category=val).values('title')
        return render(request,"app/category.html",locals())
    
@method_decorator(login_required,name='dispatch')    
class CategoryTitle(View):
    def get(self,request,val):
        product=Product.objects.filter(title=val)
        title=Product.objects.filter(category=product[0].category).values('title')
        totalitem=0
        wishitem=0
        if request.user.is_authenticated:
            totalitem=len(Cart.objects.filter(user=request.user))
            wishitem=len(Cart.objects.filter(user=request.user))
        return render(request,"app/category.html",locals())
    
@method_decorator(login_required,name='dispatch')        
class ProductDetail(View):
    def get(self, request, pk):
        product = Product.objects.get(pk=pk)
        wishlist = None
        totalitem = 0
        wishitem=0
        if request.user.is_authenticated:
            wishlist = Wishlist.objects.filter(Q(product=product) & Q(user=request.user))
            totalitem = len(Cart.objects.filter(user=request.user))
            wishitem=len(Cart.objects.filter(user=request.user))
        return render(request, "app/productdetail.html", locals())
  
    
   
class CustomerRegistrationView(View):
    def get(self, request):
        form = CustomerRegistrationForm()
        totalitem = 0
        wishitem = 0
        if request.user.is_authenticated:
            totalitem = len(Cart.objects.filter(user=request.user))
            wishitem = len(Wishlist.objects.filter(user=request.user))  # Assuming Wishlist model exists
        return render(request, 'app/customerregistration.html', {
            'form': form,
            'totalitem': totalitem,
            'wishitem': wishitem
        })

    def post(self, request):
        form = CustomerRegistrationForm(request.POST)
        totalitem = 0
        wishitem = 0
        if request.user.is_authenticated:
            totalitem = len(Cart.objects.filter(user=request.user))
            wishitem = len(Wishlist.objects.filter(user=request.user))
    
        if form.is_valid():
            form.save()
            messages.success(request, "Congratulations! User registration successful.")
            return redirect('login')
        else:
            print(form.errors)  # 🔍 Print form errors to console
            messages.warning(request, "Invalid input data")
    
        return render(request, 'app/customerregistration.html', {
        'form': form,
        'totalitem': totalitem,
        'wishitem': wishitem
    })
         
@method_decorator(login_required,name='dispatch')         
class ProfileView(View):
    def get(self,request):
        form=CustomerProfileForm()
        totalitem=0
        wishitem=0
        if request.user.is_authenticated:
            totalitem=len(Cart.objects.filter(user=request.user))
            wishitem=len(Cart.objects.filter(user=request.user))
        return render(request, 'app/profile.html',locals())
    def post(self,request):
        form=CustomerProfileForm(request.POST)
        if form.is_valid():
            user=request.user
            name=form.cleaned_data['name']
            locality=form.cleaned_data['locality']
            city=form.cleaned_data['city']
            mobile=form.cleaned_data['mobile']
            state=form.cleaned_data['state']
            zipcode=form.cleaned_data['zipcode']
            
            reg=Customer(user=user,name=name,locality=locality,mobile=mobile,city=city,state=state,zipcode=zipcode)
            reg.save()
            messages.success(request, "Congratulation! Profile Save Successfully")
        else:
            messages.warning(request, "Invalid Input Data")    
        return render(request, 'app/profile.html',locals())
    
@login_required    
def address(request):
    add=Customer.objects.filter(user=request.user)
    totalitem=0
    wishitem=0
    if request.user.is_authenticated:
        totalitem=len(Cart.objects.filter(user=request.user))
        wishitem=len(Cart.objects.filter(user=request.user))
    return render(request, 'app/address.html',locals()) 
 
@method_decorator(login_required,name='dispatch')
class updateAddress(View):
    def get(self,request,pk):
        add=Customer.objects.get(pk=pk)
        form=CustomerProfileForm(instance=add)
        totalitem=0
        wishitem=0
        if request.user.is_authenticated:
            totalitem=len(Cart.objects.filter(user=request.user))
            wishitem=len(Cart.objects.filter(user=request.user))
        return render(request,'app/updateAddress.html',locals())
    def post(self,request,pk):
        form=CustomerProfileForm(request.POST)
        if form.is_valid():
            add=Customer.objects.get(pk=pk)
            add.name=form.cleaned_data['name']
            add.locality=form.cleaned_data['locality']
            add.city=form.cleaned_data['city']
            add.mobile=form.cleaned_data['mobile']
            add.state=form.cleaned_data['state']
            add.zipcode=form.cleaned_data['zipcode']
            add.save()
            messages.success(request,"Congratulation! Profile Update Successfully")
        else: 
            messages.warning(request,"Invalid Input Data")   
        return redirect("address")
    
@login_required
def add_to_cart(request):
    if request.method == "POST":
        product_id = request.POST.get("prod_id")
        if not product_id:
            messages.error(request, "Product ID missing!")
            return redirect("home")
        
        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            messages.error(request, "Product does not exist!")
            return redirect("home")

        # Add product to cart logic
        cart_item, created = Cart.objects.get_or_create(product=product, user=request.user)
        if not created:
            cart_item.quantity += 1
            cart_item.save()

        messages.success(request, "Added to cart!")
        return redirect("showcart")

    return redirect("home")  


@login_required
def show_cart(request):
    if not request.user.is_authenticated:
        return redirect('login')  # or show a custom "Please log in" message

    user = request.user
    cart = Cart.objects.filter(user=user)
    
    amount = 0
    for p in cart:
        value = p.quantity * p.product.discounted_price
        amount += value

    totalamount = amount + 40
    totalitem = len(cart)

    return render(request, 'app/addtocart.html', locals())
 
@method_decorator(login_required,name='dispatch')
class checkout(View):
    def get(self, request):
        totalitem=0
        wishitem=0
        if request.user.is_authenticated:
            totalitem=len(Cart.objects.filter(user=request.user))
            wishitem=len(Cart.objects.filter(user=request.user))
        user = request.user
        add = Customer.objects.filter(user=user)
        cart_items = Cart.objects.filter(user=user)
        famount = 0
        for p in cart_items:
            famount += p.quantity * p.product.discounted_price
        totalamount = famount + 40
        razoramount = int(totalamount * 100)  # in paise

        try:
            client = razorpay.Client(auth=(settings.RAZOR_KEY_ID, settings.RAZOR_KEY_SECRET))
            data = {
                'amount': razoramount,
                'currency': 'INR',
                'receipt': 'order_rcptid_12'
            }
            payment_response = client.order.create(data=data)

            # Pass order ID and key to the template
            context = {
                'order_id': payment_response['id'],
                'razor_key_id': settings.RAZOR_KEY_ID,
                'amount': razoramount,
                'cart_items': cart_items,
                'add': add,
                'totalamount': totalamount,
            }

            return render(request, 'app/checkout.html', context)

        except razorpay.errors.BadRequestError as e:
            return HttpResponse("Razorpay Authentication Failed. Check your keys.", status=400)

    
@login_required
def payment_done(request):
    # Use GET instead of POST
    payment_id = request.GET.get('payment_id')
    order_id = request.GET.get('order_id')
    cust_id = request.GET.get('cust_id')
    user = request.user

    client = razorpay.Client(auth=(settings.RAZOR_KEY_ID, settings.RAZOR_KEY_SECRET))
    params_dict = {
        'razorpay_order_id': order_id,
        'razorpay_payment_id': payment_id,
        'razorpay_signature': request.GET.get('razorpay_signature', '')  # optional
    }

    try:
        client.utility.verify_payment_signature(params_dict)

        payment = Payment.objects.create(
            user=user,
            razorpay_order_id=order_id,
            razorpay_payment_id=payment_id,
            paid=True
        )

        customer = Customer.objects.get(id=cust_id)
        cart_items = Cart.objects.filter(user=user)
        for item in cart_items:
            OrderPlaced.objects.create(
                user=user,
                customer=customer,
                product=item.product,
                quantity=item.quantity,
                payment=payment
            )
            item.delete()

        return redirect("orders")

    except razorpay.errors.SignatureVerificationError:
        return HttpResponse("Payment Verification Failed!", status=400) 
    
@login_required    
def orders(request):
    order_placed=OrderPlaced.objects.filter(user=request.user)
    totalitem=0
    wishitem=0
    if request.user.is_authenticated:
        totalitem=len(Cart.objects.filter(user=request.user))
        wishitem=len(Cart.objects.filter(user=request.user))
    return render(request,'app/orders.html',locals())    


def plus_cart(request):
    if request.method == "GET":
        prod_id = request.GET.get("prod_id")
        try:
            cart_item = Cart.objects.get(Q(product=prod_id) & Q(user=request.user))  # ✅ Correct field name
            cart_item.quantity += 1
            cart_item.save()
            
            amount = sum(item.product.discounted_price * item.quantity for item in Cart.objects.filter(user=request.user))
            totalamount = amount + 40  
            
            return JsonResponse({
                "quantity": cart_item.quantity,
                "amount": amount,
                "totalamount": totalamount
            })
        except Cart.DoesNotExist:
            return JsonResponse({"error": "Cart item not found"}, status=400)
    return JsonResponse({"error": "Invalid request"}, status=400)

def minus_cart(request):
    if request.method == "GET":
        prod_id = request.GET.get("prod_id")
        try:
            cart_item = Cart.objects.get(Q(product=prod_id) & Q(user=request.user))  # ✅ Correct field name
            cart_item.quantity -= 1
            cart_item.save()
            
            amount = sum(item.product.discounted_price * item.quantity for item in Cart.objects.filter(user=request.user))
            totalamount = amount + 40  
            
            return JsonResponse({
                "quantity": cart_item.quantity,
                "amount": amount,
                "totalamount": totalamount
            })
        except Cart.DoesNotExist:
            return JsonResponse({"error": "Cart item not found"}, status=400)
    return JsonResponse({"error": "Invalid request"}, status=400)


def remove_cart(request):
    if request.method == "GET":
        prod_id = request.GET.get("prod_id")
        try:
            cart_items = Cart.objects.filter(Q(product=prod_id) & Q(user=request.user))  # 🔹 Use `.filter()` instead of `.get()`
            
            if cart_items.exists():
                cart_items.delete()  # Deletes all instances of the product in the cart
                amount = sum(item.product.discounted_price * item.quantity for item in Cart.objects.filter(user=request.user))
                totalamount = amount + 40  # Assuming Rs. 40 shipping charge
                
                return JsonResponse({
                    "amount": amount,
                    "totalamount": totalamount
                })
            else:
                return JsonResponse({"error": "Cart item not found"}, status=400)

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "Invalid request"}, status=400)


def plus_wishlist(request):
    if request.method == "GET":
        prod_id=request.GET['prod_id']
        product=Product.objects.get(id=prod_id)
        user=request.user
        Wishlist(user=user,product=product).save()
        data={
            'message':'Wishlist Added Successfully',
        }
        return JsonResponse(data)
    
def minus_wishlist(request):
    if request.method == "GET":
        prod_id=request.GET['prod_id']
        product=Product.objects.get(id=prod_id)
        user=request.user
        Wishlist(user=user,product=product).delete()
        data={
            'message':'Wishlist Remove Successfully',
        }
        return JsonResponse(data)    
             
@login_required    
def search(request):
    query = request.GET.get('search', '')
    product = Product.objects.filter(title__icontains=query)

    totalitem = 0
    wishitem = 0
    if request.user.is_authenticated:
        totalitem = Cart.objects.filter(user=request.user).count()
        wishitem = Wishlist.objects.filter(user=request.user).count()

    if not product.exists():
        messages.info(request, f"No results found for '{query}'")

    context = {
        'product': product,
        'query': query,
        'totalitem': totalitem,
        'wishitem': wishitem,
    }

    return render(request, 'app/search.html', context)              
    
