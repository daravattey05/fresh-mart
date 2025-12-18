from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib import messages

from .models import Product, Blog, Category, Order, OrderItem
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required

def index(request):
    featured_products = Product.objects.filter(is_featured=True).order_by('-created_at')[:40]
    latest_products = Product.objects.order_by('-created_at')[:6]
    top_rated_products = Product.objects.order_by('?')[:6]
    review_products = Product.objects.order_by('?')[:6]
    blogs = Blog.objects.order_by('-created_at')[:3]
    categories = Category.objects.all()
    
    context = {
        'featured_products': featured_products,
        'latest_products': latest_products,
        'top_rated_products': top_rated_products,
        'review_products': review_products,
        'blogs': blogs,
        'categories': categories,
    }
    return render(request, 'index.html', context)

def shop_grid(request, category_slug=None):
    products = Product.objects.all()
    categories = Category.objects.all()
    current_category = None
    
    # Filter by category if provided
    if category_slug:
        current_category = get_object_or_404(Category, slug=category_slug)
        products = products.filter(category=current_category)
    
    context = {
        'products': products,
        'categories': categories,
        'current_category': current_category,
    }
    return render(request, 'shop-grid.html', context)

def shop_details(request, slug):
    product = get_object_or_404(Product, slug=slug)
    related_products = Product.objects.filter(category=product.category).exclude(slug=slug)[:4]
    categories = Category.objects.all()
    context = {
        'product': product,
        'related_products': related_products,
        'categories': categories,
    }
    return render(request, 'shop-details.html', context)

def blog(request):
    blogs = Blog.objects.all().order_by('-created_at')
    categories = Category.objects.all()
    context = {
        'blogs': blogs,
        'categories': categories
    }
    return render(request, 'blog.html', context)

def blog_details(request, slug):
    blog = Blog.objects.get(slug=slug)
    categories = Category.objects.all()
    context = {
        'blog': blog,
        'categories': categories
    }
    return render(request, 'blog-details.html', context)

def contact(request):
    categories = Category.objects.all()
    context = {
        'categories': categories
    }
    return render(request, 'contact.html', context)

def register_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')

        if password != confirm_password:
            messages.error(request, "Passwords do not match")
            return redirect('core:register')
        
        try:
            user = User.objects.create_user(username=username, email=email, password=password)
            login(request, user)
            messages.success(request, "Registration successful")
            return redirect('core:index')
        except Exception as e:
            messages.error(request, f"Registration failed: {e}")
            return redirect('core:register')
            
    return render(request, 'register.html')

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f"Welcome back, {user.username}!")
            return redirect('core:index')
        else:
            messages.error(request, "Invalid username or password")
    return render(request, 'login.html')

def logout_view(request):
    logout(request)
    messages.info(request, "You have been logged out")
    return redirect('core:index')

@login_required
def add_to_cart(request, slug):
    product = get_object_or_404(Product, slug=slug)
    # Get or create an open order for the user
    order, created = Order.objects.get_or_create(user=request.user, is_ordered=False)
    
    # Check if item is already in cart
    order_item, item_created = OrderItem.objects.get_or_create(order=order, product=product)
    
    quantity = int(request.POST.get('quantity', 1))
    
    if not item_created:
        order_item.quantity += quantity
        order_item.save()
        messages.success(request, f"Updated quantity for {product.name}")
    else:
        order_item.quantity = quantity
        order_item.save()
        messages.success(request, f"Added {product.name} to your cart")
    
    return redirect('core:product_detail', slug=slug)

@login_required
def view_cart(request):
    order = Order.objects.filter(user=request.user, is_ordered=False).first()
    order_items = []
    
    if order:
        order_items = order.items.all()
        # Calculate total price
        total = sum(item.get_total_price() for item in order_items)
        order.total_price = total
        order.save()
    
    context = {
        'order': order,
        'order_items': order_items,
    }
    return render(request, 'cart.html', context)

@login_required
def update_cart_item(request, item_id):
    from django.http import JsonResponse
    
    order_item = get_object_or_404(OrderItem, id=item_id, order__user=request.user)
    
    if request.method == 'POST':
        quantity = int(request.POST.get('quantity', 1))
        
        # Check if this is an AJAX request
        is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
        
        if quantity > 0:
            order_item.quantity = quantity
            order_item.save()
            
            # Calculate new totals
            item_total = order_item.get_total_price()
            order = order_item.order
            cart_total = sum(item.get_total_price() for item in order.items.all())
            order.total_price = cart_total
            order.save()
            
            if is_ajax:
                return JsonResponse({
                    'success': True,
                    'item_total': float(item_total),
                    'cart_total': float(cart_total),
                    'quantity': quantity,
                    'message': f'Updated {order_item.product.name} quantity'
                })
            else:
                messages.success(request, f"Updated {order_item.product.name} quantity")
        else:
            product_name = order_item.product.name
            order_item.delete()
            
            # Recalculate cart total
            order = Order.objects.filter(user=request.user, is_ordered=False).first()
            cart_total = 0
            if order:
                cart_total = sum(item.get_total_price() for item in order.items.all())
                order.total_price = cart_total
                order.save()
            
            if is_ajax:
                return JsonResponse({
                    'success': True,
                    'removed': True,
                    'cart_total': float(cart_total),
                    'message': f'Removed {product_name} from cart'
                })
            else:
                messages.info(request, f"Removed {product_name} from cart")
    
    return redirect('core:view_cart')

@login_required
def remove_from_cart(request, item_id):
    order_item = get_object_or_404(OrderItem, id=item_id, order__user=request.user)
    product_name = order_item.product.name
    order_item.delete()
    messages.success(request, f"Removed {product_name} from your cart")
    return redirect('core:view_cart')

@login_required
def checkout(request):
    order = Order.objects.filter(user=request.user, is_ordered=False).first()
    
    if not order or not order.items.exists():
        messages.warning(request, "Your cart is empty")
        return redirect('core:shop')
    
    # Calculate total
    total = sum(item.get_total_price() for item in order.items.all())
    order.total_price = total
    order.save()
    
    if request.method == 'POST':
        # Save billing details
        order.full_name = request.POST.get('full_name')
        order.phone = request.POST.get('phone')
        order.address = request.POST.get('address')
        order.city = request.POST.get('city')
        order.province = request.POST.get('province')
        order.note = request.POST.get('notes')
        order.save()

        payment_method = request.POST.get('payment_method')
        
        if payment_method == 'khqr':
            # Generate KHQR payment
            return redirect('core:khqr_payment', order_id=order.id)
        else:
            # Mark order as completed
            order.is_ordered = True
            order.save()
            messages.success(request, "Order placed successfully!")
            return redirect('core:order_success', order_id=order.id)
    
    context = {
        'order': order,
        'order_items': order.items.all(),
    }
    return render(request, 'checkout.html', context)

@login_required
def khqr_payment(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user, is_ordered=False)
    
    # ABA PayWay payment link configuration
    # Base URL with all necessary parameters
    aba_payway_base = "https://link.payway.com.kh/aba"
    
    # Build the payment URL with amount parameter
    order_total = float(order.total_price)
    
    payment_params = {
        'id': '52993998C8B8',
        'dynamic': 'true',
        'source_caller': 'sdk',
        'pid': 'af_app_invites',
        'link_action': 'abaqr',
        'shortlink': '6ic5my80',
        'created_from_app': 'true',
        'acc': '002299917',
        'af_siteid': '968860649',
        'userid': '52993998C8B8',
        'code': '549767',
        'c': 'abaqr',
        'af_referrer_uid': '1700729895453-8638212',
        'amount': f'{order_total:.2f}'  # Add the dynamic amount
    }
    
    # Build query string
    from urllib.parse import urlencode
    payment_url = f"{aba_payway_base}?{urlencode(payment_params)}"
    
    # Generate QR code server-side
    import qrcode
    import io
    import base64
    
    # Create QR code instance
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=10,
        border=4,
    )
    qr.add_data(payment_url)
    qr.make(fit=True)
    
    # Create image
    img = qr.make_image(fill_color="black", back_color="white")
    
    # Convert to base64
    buffer = io.BytesIO()
    img.save(buffer, format='PNG')
    qr_code_base64 = base64.b64encode(buffer.getvalue()).decode()
    
    context = {
        'order': order,
        'order_items': order.items.all(),
        'merchant_name': 'BUN DARAVATTEY',
        'account_number': '002 299 917',
        'payment_url': payment_url,
        'qr_code_base64': qr_code_base64,  # Pass the QR code image as base64
        'aba_base_url': aba_payway_base,
    }
    return render(request, 'khqr_payment.html', context)

@login_required
def order_success(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    context = {
        'order': order,
    }
    return render(request, 'order_success.html', context)
