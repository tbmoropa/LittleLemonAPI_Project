from django.urls import path
from . import views

urlpatterns = [
    # Menu items
    path('menu-items', views.MenuItemListView.as_view(), name='menu-items'),
    path('menu-items/<int:pk>', views.MenuItemDetailView.as_view(), name='menu-item-detail'),

    # Categories
    path('categories', views.CategoryListView.as_view(), name='categories'),

    # User group management
    path('groups/manager/users', views.manager_list, name='manager-list'),
    path('groups/manager/users/<int:userId>', views.manager_remove, name='manager-remove'),
    path('groups/delivery-crew/users', views.delivery_crew_list, name='delivery-crew-list'),
    path('groups/delivery-crew/users/<int:userId>', views.delivery_crew_remove, name='delivery-crew-remove'),

    # Cart
    path('cart/menu-items', views.cart_menu_items, name='cart-menu-items'),

    # Orders
    path('orders', views.order_list, name='orders'),
    path('orders/<int:orderId>', views.order_detail, name='order-detail'),
]
