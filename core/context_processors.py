from .models import Order

def cart_info(request):
    cart_item_count = 0
    cart_total_price = 0
    
    if request.user.is_authenticated:
        order = Order.objects.filter(user=request.user, is_ordered=False).first()
        if order:
            cart_item_count = order.items.count()
            cart_total_price = sum(item.get_total_price() for item in order.items.all())
    
    return {
        'cart_item_count': cart_item_count,
        'cart_total_price': cart_total_price
    }
