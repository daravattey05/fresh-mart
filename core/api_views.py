from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Category, Product, Blog, Order, OrderItem
from .serializers import (
    CategorySerializer, ProductSerializer, BlogSerializer, 
    OrderSerializer, OrderItemSerializer
)

class ProductViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Public API for listing and retrieving products.
    """
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [permissions.AllowAny]

    @action(detail=False, methods=['get'], url_path='category/(?P<category_id>\d+)')
    def by_category(self, request, category_id=None):
        products = self.queryset.filter(category_id=category_id)
        serializer = self.get_serializer(products, many=True)
        return Response(serializer.data)

class BlogViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Public API for listing and retrieving blogs.
    """
    queryset = Blog.objects.all()
    serializer_class = BlogSerializer
    permission_classes = [permissions.AllowAny]

class OrderViewSet(viewsets.ModelViewSet):
    """
    API for managing Orders. Requires Authentication.
    """
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=False, methods=['post'])
    def add_to_cart(self, request):
        """
        Custom endpoint to add items to an 'active' order (cart).
        """
        product_id = request.data.get('product_id')
        quantity = int(request.data.get('quantity', 1))

        if not product_id:
            return Response({"error": "Product ID required"}, status=status.HTTP_400_BAD_REQUEST)

        # Get or create active order for user
        order, created = Order.objects.get_or_create(
            user=request.user, 
            is_ordered=False
        )

        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            return Response({"error": "Product not found"}, status=status.HTTP_404_NOT_FOUND)

        # Update or create order item
        item, created_item = OrderItem.objects.get_or_create(
            order=order, product=product
        )
        if not created_item:
            item.quantity += quantity
        else:
            item.quantity = quantity
        item.save()

        # Update order total
        order.total_price = sum(i.get_total_price() for i in order.items.all())
        order.save()

        return Response(OrderSerializer(order).data)

    @action(detail=False, methods=['post'])
    def place_order(self, request):
        """
        Mark the active order as ordered.
        """
        try:
            order = Order.objects.get(user=request.user, is_ordered=False)
            if not order.items.exists():
                 return Response({"error": "Cart is empty"}, status=status.HTTP_400_BAD_REQUEST)
            
            order.is_ordered = True
            order.save()
            return Response({"message": "Order placed successfully", "order_id": order.id})
        except Order.DoesNotExist:
            return Response({"error": "No active order found"}, status=status.HTTP_404_NOT_FOUND)
