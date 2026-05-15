from django.urls import path
from . import views

app_name = 'store'

urlpatterns = [
    # ═══════════════════════════════════════════════════════════
    # HOME
    # ═══════════════════════════════════════════════════════════
    path('', views.home_view, name='home'),
    
    # ═══════════════════════════════════════════════════════════
    # AUTHENTICATION
    # ═══════════════════════════════════════════════════════════
    path('signup/', views.signup_view, name='signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile_view, name='profile'),
    
    # ═══════════════════════════════════════════════════════════
    # PRODUCTS
    # ═══════════════════════════════════════════════════════════
    path('products/', views.product_list_view, name='product_list'),
    path('product/<int:pk>/', views.product_detail_view, name='product_detail'),
    path('category/<slug:slug>/', views.category_products_view, name='category_products'),
    path('search/', views.search_view, name='search'),
    
    # ═══════════════════════════════════════════════════════════
    # AI RECOMMENDATIONS
    # ═══════════════════════════════════════════════════════════
    path('recommendations/', views.recommendations_view, name='recommendations'),
    path('recommendations/refresh/', views.refresh_recommendations_view, name='refresh_recommendations'),

    # ═══════════════════════════════════════════════════════════
    # APIs
    # ═══════════════════════════════════════════════════════════
    path('api/search-suggestions/', views.search_suggestions_api_view, name='api_search_suggestions'),
    path('track/', views.track_interaction_api_view, name='track_interaction'),
    path('cart/update/<int:product_id>/', views.update_cart_api_view, name='cart_update'),
    path('api/recommendations/', views.recommendations_api_view, name='api_recommendations'),
    path('api/products/<int:product_id>/', views.product_quick_view_api_view, name='api_product_quick_view'),
    
    # ═══════════════════════════════════════════════════════════
    # CART (session-based)
    # ═══════════════════════════════════════════════════════════
    path('cart/', views.view_cart_view, name='cart'),
    path('cart/add/<int:product_id>/', views.add_to_cart_view, name='add_to_cart'),
    path('cart/remove/<int:product_id>/', views.remove_from_cart_view, name='remove_from_cart'),
    
    # ═══════════════════════════════════════════════════════════
    # ORDERS
    # ═══════════════════════════════════════════════════════════
    path('order/<int:product_id>/', views.place_order_view, name='place_order'),
    path('orders/', views.order_history_view, name='order_history'),
    
    # ═══════════════════════════════════════════════════════════
    # FEEDBACK
    # ═══════════════════════════════════════════════════════════
    path('feedback/<int:product_id>/', views.submit_feedback_view, name='submit_feedback'),
    
    # ═══════════════════════════════════════════════════════════
    # ADMIN PANEL (custom — separate from django-admin)
    # ═══════════════════════════════════════════════════════════
    path('admin-panel/', views.admin_dashboard_view, name='admin_dashboard'),
    path('admin-panel/products/', views.admin_product_list_view, name='admin_products'),
    path('admin-panel/products/add/', views.admin_add_product_view, name='admin_add_product'),
    path('admin-panel/products/edit/<int:product_id>/', views.admin_edit_product_view, name='admin_edit_product'),
    path('admin-panel/products/delete/<int:product_id>/', views.admin_delete_product_view, name='admin_delete_product'),
    path('admin-panel/users/', views.admin_user_list_view, name='admin_users'),
    path('admin-panel/orders/', views.admin_order_management_view, name='admin_orders'),
    path('admin-panel/analytics/', views.admin_analytics_view, name='admin_analytics'),
]
