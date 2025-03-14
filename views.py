from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, JsonResponse
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.utils.timezone import now
from .models import Product, Cart, Category, Review
from .forms import SignUpForm, LoginForm
import stripe
from django.contrib import messages

# Set up Stripe secret key
stripe.api_key = settings.STRIPE_SECRET_KEY


# Home Page - Display all products
def home(request):
    products = Product.objects.all()
    return render(request, 'home.html', {'products': products})

# Product Detail View
def product_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    related_products = Product.objects.filter(category=product.category).exclude(id=product_id)
    reviews = Review.objects.filter(product=product)
    return render(request, 'product_detail.html', {
        'product': product,
        'related_products': related_products,
        'reviews': reviews
    })

# Product List with Search Functionality
def product_list(request):
    query = request.GET.get('search', '')
    products = Product.objects.filter(name__icontains=query) if query else Product.objects.all()
    return render(request, 'product_list.html', {'products': products, 'search_query': query})

# Add a New Product
@login_required
def add_product(request):
    if request.method == 'POST':
        name = request.POST['name']
        description = request.POST['description']
        price = request.POST['price']
        stock = request.POST['stock']
        category_id = request.POST['category']
        image = request.FILES.get('image')
        category = get_object_or_404(Category, id=category_id)
        
        Product.objects.create(
            name=name, description=description, price=price, 
            stock=stock, category=category, image=image
        )
        return redirect('product_list')

    categories = Category.objects.all()
    return render(request, 'add_product.html', {'categories': categories})

# Update Product Details
@login_required
def update_product(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    if request.method == 'POST':
        product.name = request.POST['name']
        product.description = request.POST['description']
        product.price = request.POST['price']
        product.stock = request.POST['stock']
        category_id = request.POST['category']
        product.category = get_object_or_404(Category, id=category_id)
        if 'image' in request.FILES:
            product.image = request.FILES['image']
        product.save()
        return redirect('product_list')

    categories = Category.objects.all()
    return render(request, 'update_product.html', {'product': product, 'categories': categories})

# Delete a Product
@login_required
def delete_product(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    product.delete()
    return redirect('product_list')

# Add Product to Cart
@login_required
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    cart, created = Cart.objects.get_or_create(user=request.user, product=product)
    cart.quantity += 1
    cart.save()
    return redirect('cart')

# Display Cart
def cart(request):
    if not request.user.is_authenticated:
        messages.error(request, "You need to log in to view your cart.")
        return redirect("login")  # Redirect to the login page

    cart_items = Cart.objects.filter(user=request.user)
    total = sum(item.total_price() for item in cart_items)
    return render(request, 'cart.html', {'cart_items': cart_items, 'total': total})


def user_login(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        print(f"Username: {username}, Password: {password}")  # ✅ Debugging
        
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            print("Login successful!")  # ✅ Debugging
            return JsonResponse({"redirect_url": "/home/"})  # ✅ Redirect JSON Response
        else:
            print("Invalid credentials!")  # ✅ Debugging
            return JsonResponse({"error": "Invalid username or password"}, status=400)

    return render(request, "login.html")


def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()
            login(request, user)
            return redirect('home')
    else:
        form = SignUpForm()
    return render(request, 'signup.html', {'form': form})

def user_logout(request):
    logout(request)
    return redirect('home')

# Add a Review to a Product
@login_required
def add_review(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    if request.method == 'POST':
        Review.objects.create(
            product=product,
            user=request.user,
            rating=request.POST['rating'],
            comment=request.POST['comment']
        )
        return redirect('product_detail', product_id=product.id)
    return render(request, 'add_review.html', {'product': product})

# Checkout and Stripe Payment
@login_required
def checkout(request):
    cart_items = Cart.objects.filter(user=request.user)
    total = sum(item.total_price() for item in cart_items) * 100  # Convert to cents

    if request.method == "POST":
        try:
            # Create a Stripe PaymentIntent
            intent = stripe.PaymentIntent.create(
                amount=int(total),  # Amount in cents
                currency="usd",
                description=f"Order by {request.user.username}",
                metadata={"user_id": request.user.id},
            )
            return JsonResponse({"clientSecret": intent.client_secret})
        except stripe.error.StripeError as e:
            return JsonResponse({"error": str(e)}, status=400)

    return render(request, "checkout.html", {
        "stripe_public_key": settings.STRIPE_TEST_PUBLIC_KEY,
        "total": total / 100,  # Convert back to dollars for display
    })

# Payment Success
def payment_success(request):
    cart_items = Cart.objects.filter(user=request.user)
    cart_items.delete()  # Clear the cart after successful payment
    return render(request, 'payment_success.html')

# Payment Error
def payment_error(request):
    return render(request, 'payment_error.html')

# Save User Location
@csrf_exempt
def save_location(request):
    if request.method == 'POST':
        import json
        data = json.loads(request.body)
        latitude, longitude = data.get('latitude'), data.get('longitude')
        return JsonResponse({'status': 'success', 'latitude': latitude, 'longitude': longitude})
    return JsonResponse({'status': 'error'}, status=400)

# Chat Feature
def chat_view(request):
    messages = ChatMessage.objects.all()
    return render(request, 'shop/chat.html', {'messages': messages})

# KYC Verification
def kyc_verification(request):
    return render(request, 'shop/kyc_verification.html') 

# Deals Page
def deals(request):
    return render(request, 'deals.html')  

# Wishlist Page
def wishlist(request):
    return render(request, 'wishlist.html')

# Contact Page
def contact(request):
    return render(request, 'contact.html') 

# FAQ Page
def faq(request):
    return render(request, 'faq.html') 

# Subscribe to Newsletter
def subscribe_newsletter(request):
    if request.method == "POST":
        email = request.POST.get('email')
        # Process the email (e.g., save to database)
        return HttpResponse("Subscription successful!")  # Or redirect to a success page
    return redirect('/')

# Login View
def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            # Redirect to Checkout if coming from Cart
            next_url = request.GET.get('next', 'checkout')  
            return redirect(next_url)
        else:
            return render(request, 'login.html', {'error': 'Invalid credentials'})

    return render(request, 'login.html')


# Add to Wishlist
def add_to_wishlist(request):
    return render(request, 'shop/wishlist.html')

def cart_view(request):
    # Get user's cart
    cart, created = Cart.objects.get_or_create(user=request.user)
    cart_products = cart.products.all()

    # Calculate total for each product and the entire cart
    for product in cart_products:
        product.total_price = product.quantity * product.price  # Calculate total for each product

    cart_total = sum(product.total_price for product in cart_products)

    context = {
        "cart": cart,
        "cart_products": cart_products,
        "cart_total": cart_total,
        "STRIPE_PUBLIC_KEY": settings.STRIPE_PUBLIC_KEY,
    }
    return render(request, "cart.html", context)

def update_cart(request):
    """ Update product quantity in cart """
    if request.method == "POST":
        import json
        data = json.loads(request.body)
        product_id = data.get("product_id")
        action = data.get("action")

        product = get_object_or_404(Product, id=product_id)
        cart, created = Cart.objects.get_or_create(user=request.user)

        if action == "increase":
            product.quantity += 1
        elif action == "decrease" and product.quantity > 1:
            product.quantity -= 1

        product.save()

        # Recalculate totals
        product_total = product.quantity * product.price
        cart_total = sum(p.quantity * p.price for p in cart.products.all())

        return JsonResponse({"quantity": product.quantity, "product_total": product_total, "cart_total": cart_total})

def checkout_view(request):
    return render(request, 'shop/checkout.html')