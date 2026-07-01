from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.decorators import api_view, permission_classes, throttle_classes
from rest_framework.throttling import AnonRateThrottle, UserRateThrottle
from django.contrib.auth.models import User, Group
from django.shortcuts import get_object_or_404
from django.core.paginator import Paginator, EmptyPage

from .models import Category, MenuItem, Cart, Order, OrderItem
from .serializers import (
    CategorySerializer, MenuItemSerializer, UserSerializer,
    CartSerializer, OrderSerializer
)


# ─── Helpers ────────────────────────────────────────────────────────────────

def is_manager(user):
    return user.groups.filter(name='Manager').exists()

def is_delivery_crew(user):
    return user.groups.filter(name='Delivery crew').exists()


# ─── Menu Items ─────────────────────────────────────────────────────────────

class MenuItemListView(generics.ListCreateAPIView):
    queryset = MenuItem.objects.select_related('category').all()
    serializer_class = MenuItemSerializer
    throttle_classes = [AnonRateThrottle, UserRateThrottle]

    def get_permissions(self):
        if self.request.method == 'GET':
            return [IsAuthenticated()]
        return [IsAuthenticated()]

    def list(self, request):
        queryset = MenuItem.objects.select_related('category').all()

        # Filtering
        category = request.query_params.get('category')
        featured = request.query_params.get('featured')
        if category:
            queryset = queryset.filter(category__title__icontains=category)
        if featured is not None:
            queryset = queryset.filter(featured=(featured.lower() == 'true'))

        # Searching
        search = request.query_params.get('search')
        if search:
            queryset = queryset.filter(title__icontains=search)

        # Sorting
        ordering = request.query_params.get('ordering', 'id')
        allowed = ['price', '-price', 'title', '-title', 'id', '-id']
        if ordering in allowed:
            queryset = queryset.order_by(ordering)

        # Pagination
        page_size = int(request.query_params.get('perpage', 10))
        page = int(request.query_params.get('page', 1))
        paginator = Paginator(queryset, page_size)
        try:
            items = paginator.page(page)
        except EmptyPage:
            items = []
        serializer = MenuItemSerializer(items, many=True)
        return Response(serializer.data)

    def create(self, request):
        if not is_manager(request.user) and not request.user.is_staff:
            return Response({'message': 'Forbidden'}, status=status.HTTP_403_FORBIDDEN)
        serializer = MenuItemSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class MenuItemDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = MenuItem.objects.select_related('category').all()
    serializer_class = MenuItemSerializer
    throttle_classes = [AnonRateThrottle, UserRateThrottle]

    def get_permissions(self):
        return [IsAuthenticated()]

    def update(self, request, *args, **kwargs):
        if not is_manager(request.user) and not request.user.is_staff:
            return Response({'message': 'Forbidden'}, status=status.HTTP_403_FORBIDDEN)
        return super().update(request, *args, **kwargs)

    def partial_update(self, request, *args, **kwargs):
        if not is_manager(request.user) and not request.user.is_staff:
            return Response({'message': 'Forbidden'}, status=status.HTTP_403_FORBIDDEN)
        kwargs['partial'] = True
        return self.update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        if not is_manager(request.user) and not request.user.is_staff:
            return Response({'message': 'Forbidden'}, status=status.HTTP_403_FORBIDDEN)
        return super().destroy(request, *args, **kwargs)


# ─── Categories ─────────────────────────────────────────────────────────────

class CategoryListView(generics.ListCreateAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    throttle_classes = [AnonRateThrottle, UserRateThrottle]

    def get_permissions(self):
        if self.request.method == 'GET':
            return [IsAuthenticated()]
        return [IsAuthenticated()]

    def create(self, request):
        if not is_manager(request.user) and not request.user.is_staff:
            return Response({'message': 'Forbidden'}, status=status.HTTP_403_FORBIDDEN)
        return super().create(request)


# ─── User Group Management ───────────────────────────────────────────────────

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def manager_list(request):
    if not is_manager(request.user) and not request.user.is_staff:
        return Response({'message': 'Forbidden'}, status=status.HTTP_403_FORBIDDEN)
    manager_group = Group.objects.get(name='Manager')
    if request.method == 'GET':
        managers = manager_group.user_set.all()
        serializer = UserSerializer(managers, many=True)
        return Response(serializer.data)
    elif request.method == 'POST':
        username = request.data.get('username')
        user = get_object_or_404(User, username=username)
        manager_group.user_set.add(user)
        return Response({'message': 'User added to the manager group'}, status=status.HTTP_201_CREATED)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def manager_remove(request, userId):
    if not is_manager(request.user) and not request.user.is_staff:
        return Response({'message': 'Forbidden'}, status=status.HTTP_403_FORBIDDEN)
    user = get_object_or_404(User, id=userId)
    manager_group = Group.objects.get(name='Manager')
    manager_group.user_set.remove(user)
    return Response({'message': 'User removed from manager group'}, status=status.HTTP_200_OK)


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def delivery_crew_list(request):
    if not is_manager(request.user) and not request.user.is_staff:
        return Response({'message': 'Forbidden'}, status=status.HTTP_403_FORBIDDEN)
    delivery_group = Group.objects.get(name='Delivery crew')
    if request.method == 'GET':
        crew = delivery_group.user_set.all()
        serializer = UserSerializer(crew, many=True)
        return Response(serializer.data)
    elif request.method == 'POST':
        username = request.data.get('username')
        user = get_object_or_404(User, username=username)
        delivery_group.user_set.add(user)
        return Response({'message': 'User added to the delivery crew group'}, status=status.HTTP_201_CREATED)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delivery_crew_remove(request, userId):
    if not is_manager(request.user) and not request.user.is_staff:
        return Response({'message': 'Forbidden'}, status=status.HTTP_403_FORBIDDEN)
    user = get_object_or_404(User, id=userId)
    delivery_group = Group.objects.get(name='Delivery crew')
    delivery_group.user_set.remove(user)
    return Response({'message': 'User removed from delivery crew'}, status=status.HTTP_200_OK)


# ─── Cart ────────────────────────────────────────────────────────────────────

@api_view(['GET', 'POST', 'DELETE'])
@permission_classes([IsAuthenticated])
def cart_menu_items(request):
    if is_manager(request.user) or is_delivery_crew(request.user):
        return Response({'message': 'Forbidden'}, status=status.HTTP_403_FORBIDDEN)

    if request.method == 'GET':
        items = Cart.objects.filter(user=request.user).select_related('menuitem__category')
        serializer = CartSerializer(items, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        serializer = CartSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(user=request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    elif request.method == 'DELETE':
        Cart.objects.filter(user=request.user).delete()
        return Response({'message': 'Cart cleared'}, status=status.HTTP_200_OK)


# ─── Orders ─────────────────────────────────────────────────────────────────

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def order_list(request):
    if request.method == 'GET':
        if is_manager(request.user) or request.user.is_staff:
            orders = Order.objects.all().select_related('user', 'delivery_crew').prefetch_related('order_items__menuitem')
        elif is_delivery_crew(request.user):
            orders = Order.objects.filter(delivery_crew=request.user).select_related('user', 'delivery_crew').prefetch_related('order_items__menuitem')
        else:
            orders = Order.objects.filter(user=request.user).select_related('user', 'delivery_crew').prefetch_related('order_items__menuitem')

        # Pagination
        page_size = int(request.query_params.get('perpage', 10))
        page = int(request.query_params.get('page', 1))
        paginator = Paginator(orders, page_size)
        try:
            paged = paginator.page(page)
        except EmptyPage:
            paged = []
        serializer = OrderSerializer(paged, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        if is_manager(request.user) or is_delivery_crew(request.user):
            return Response({'message': 'Forbidden'}, status=status.HTTP_403_FORBIDDEN)

        cart_items = Cart.objects.filter(user=request.user).select_related('menuitem')
        if not cart_items.exists():
            return Response({'message': 'Cart is empty'}, status=status.HTTP_400_BAD_REQUEST)

        total = sum(item.price for item in cart_items)
        order = Order.objects.create(user=request.user, total=total)

        order_items = [
            OrderItem(
                order=order,
                menuitem=item.menuitem,
                quantity=item.quantity,
                unit_price=item.unit_price,
                price=item.price,
            )
            for item in cart_items
        ]
        OrderItem.objects.bulk_create(order_items)
        cart_items.delete()

        serializer = OrderSerializer(order)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


@api_view(['GET', 'PUT', 'PATCH', 'DELETE'])
@permission_classes([IsAuthenticated])
def order_detail(request, orderId):
    order = get_object_or_404(Order, id=orderId)

    if request.method == 'GET':
        if not is_manager(request.user) and not request.user.is_staff:
            if is_delivery_crew(request.user):
                if order.delivery_crew != request.user:
                    return Response({'message': 'Forbidden'}, status=status.HTTP_403_FORBIDDEN)
            else:
                if order.user != request.user:
                    return Response({'message': 'Forbidden'}, status=status.HTTP_403_FORBIDDEN)
        serializer = OrderSerializer(order)
        return Response(serializer.data)

    elif request.method in ['PUT', 'PATCH']:
        if is_manager(request.user) or request.user.is_staff:
            # Manager can update delivery crew and status
            delivery_crew_id = request.data.get('delivery_crew')
            order_status = request.data.get('status')
            if delivery_crew_id is not None:
                crew = get_object_or_404(User, id=delivery_crew_id)
                order.delivery_crew = crew
            if order_status is not None:
                order.status = order_status
            order.save()
            serializer = OrderSerializer(order)
            return Response(serializer.data)
        elif is_delivery_crew(request.user):
            if order.delivery_crew != request.user:
                return Response({'message': 'Forbidden'}, status=status.HTTP_403_FORBIDDEN)
            order_status = request.data.get('status')
            if order_status is not None:
                order.status = order_status
                order.save()
            serializer = OrderSerializer(order)
            return Response(serializer.data)
        else:
            return Response({'message': 'Forbidden'}, status=status.HTTP_403_FORBIDDEN)

    elif request.method == 'DELETE':
        if not is_manager(request.user) and not request.user.is_staff:
            return Response({'message': 'Forbidden'}, status=status.HTTP_403_FORBIDDEN)
        order.delete()
        return Response({'message': 'Order deleted'}, status=status.HTTP_200_OK)
