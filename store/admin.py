from django.contrib import admin
from django.utils.html import format_html
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from .models import (
    Category, Product, UserInteraction, Recommendation,
    Order, Feedback, UserProfile, ExternalSource, ExternalProduct, ProductSyncLog
)

# ═══════════════════════════════════════════════════════════
# CATEGORY ADMIN
# ═══════════════════════════════════════════════════════════

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'icon', 'color', 'product_count', 'created_at']
    list_filter = ['created_at']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ['created_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'slug', 'description')
        }),
        ('Display Settings', {
            'fields': ('icon', 'color', 'image')
        }),
        ('Metadata', {
            'fields': ('created_at',)
        }),
    )
    
    def product_count(self, obj):
        """Display number of products in this category"""
        count = obj.products.count()
        return format_html(
            '<span style="background:#6C63FF;color:white;padding:3px 10px;border-radius:10px;">{}</span>',
            count
        )
    product_count.short_description = 'Products'


# ═══════════════════════════════════════════════════════════
# PRODUCT ADMIN
# ═══════════════════════════════════════════════════════════

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = [
        'show_image', 'name', 'category', 'price', 'get_discount_price',
        'stock_level', 'is_featured', 'is_on_discount', 'rating', 'is_available',
        'is_external', 'manages_local_stock'
    ]
    list_editable = [
        'price', 'stock_level', 'is_featured', 'is_on_discount', 'is_available',
        'is_external', 'manages_local_stock'
    ]
    list_filter = ['category', 'is_featured', 'is_on_discount', 'is_available', 'is_external', 'manages_local_stock', 'created_at']
    search_fields = ['name', 'description']
    readonly_fields = ['show_image', 'rating', 'created_at', 'updated_at', 'product_id']
    prepopulated_fields = {'slug': ('name',)}
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('product_id', 'name', 'slug', 'category', 'description')
        }),
        ('Pricing', {
            'fields': ('price', 'original_price', 'is_on_discount', 'discount_percentage')
        }),
        ('Inventory', {
            'fields': ('stock_level', 'is_available', 'is_featured')
        }),
        ('External Source', {
            'fields': ('is_external', 'manages_local_stock', 'external_url')
        }),
        ('Media', {
            'fields': ('image', 'show_image')
        }),
        ('Attributes', {
            'fields': ('attributes',),
            'description': 'JSON format: {"brand": "Samsung", "color": "Black"}'
        }),
        ('Statistics', {
            'fields': ('rating', 'created_at', 'updated_at')
        }),
    )
    
    def show_image(self, obj):
        """Display product image thumbnail in admin"""
        if obj.image:
            return format_html(
                '<img src="{}" width="60" height="60" style="object-fit:cover;border-radius:5px;"/>',
                obj.image.url
            )
        return format_html(
            '<div style="width:60px;height:60px;background:#f0f0f0;display:flex;align-items:center;justify-content:center;border-radius:5px;">No Image</div>'
        )
    show_image.short_description = 'Preview'
    
    def get_discount_price(self, obj):
        """Display discounted price"""
        if obj.is_on_discount:
            return format_html(
                '<span style="color:#F72585;font-weight:bold;">Rs. {}</span>',
                obj.discount_price
            )
        return f"Rs. {obj.price}"
    get_discount_price.short_description = 'Discount Price'


# ═══════════════════════════════════════════════════════════
# ORDER ADMIN
# ═══════════════════════════════════════════════════════════

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = [
        'order_id', 'user', 'product', 'quantity', 
        'total_price', 'status', 'ordered_at'
    ]
    list_filter = ['status', 'ordered_at', 'city']
    list_editable = ['status']
    search_fields = ['user__username', 'product__name', 'phone_number']
    readonly_fields = ['order_id', 'total_price', 'ordered_at', 'updated_at']
    date_hierarchy = 'ordered_at'
    
    fieldsets = (
        ('Order Information', {
            'fields': ('order_id', 'user', 'product', 'quantity', 'status')
        }),
        ('Delivery Details', {
            'fields': ('delivery_address', 'city', 'phone_number', 'notes')
        }),
        ('Pricing', {
            'fields': ('unit_price', 'total_price')
        }),
        ('Timestamps', {
            'fields': ('ordered_at', 'updated_at')
        }),
    )
    
    def status_badge(self, obj):
        """Display colored status badge"""
        colors = {
            'pending': '#F8961E',
            'confirmed': '#3F8EFC',
            'processing': '#FF6584',
            'shipped': '#6C63FF',
            'delivered': '#43AA8B',
            'cancelled': '#F72585',
        }
        color = colors.get(obj.status, '#6C63FF')
        return format_html(
            '<span style="background:{};color:white;padding:3px 10px;border-radius:10px;font-weight:bold;">{}</span>',
            color,
            obj.get_status_display()
        )
    status_badge.short_description = 'Status'


# ═══════════════════════════════════════════════════════════
# FEEDBACK ADMIN
# ═══════════════════════════════════════════════════════════

@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    list_display = ['user', 'product', 'rating_stars', 'comment_preview', 'created_at']
    list_filter = ['rating', 'created_at']
    search_fields = ['user__username', 'product__name', 'comment']
    readonly_fields = ['created_at']
    date_hierarchy = 'created_at'
    
    def rating_stars(self, obj):
        """Display rating as stars"""
        stars = '⭐' * obj.rating
        return format_html('<span style="font-size:16px;">{}</span>', stars)
    rating_stars.short_description = 'Rating'
    
    def comment_preview(self, obj):
        """Display truncated comment"""
        if obj.comment:
            return obj.comment[:50] + '...' if len(obj.comment) > 50 else obj.comment
        return '-'
    comment_preview.short_description = 'Comment'


# ═══════════════════════════════════════════════════════════
# USER INTERACTION ADMIN
# ═══════════════════════════════════════════════════════════

@admin.register(UserInteraction)
class UserInteractionAdmin(admin.ModelAdmin):
    list_display = [
        'user', 'product', 'interaction_type_badge', 
        'interaction_count', 'timestamp'
    ]
    list_filter = ['interaction_type', 'timestamp']
    search_fields = ['user__username', 'product__name']
    readonly_fields = ['timestamp']
    date_hierarchy = 'timestamp'
    
    def interaction_type_badge(self, obj):
        """Display colored interaction type badge"""
        colors = {
            'view': '#3F8EFC',
            'cart': '#F8961E',
            'purchase': '#43AA8B',
            'like': '#F72585',
            'search': '#6C63FF',
        }
        icons = {
            'view': '👁️',
            'cart': '🛒',
            'purchase': '💰',
            'like': '❤️',
            'search': '🔍',
        }
        color = colors.get(obj.interaction_type, '#6C63FF')
        icon = icons.get(obj.interaction_type, '📌')
        return format_html(
            '<span style="background:{};color:white;padding:3px 10px;border-radius:10px;">{} {}</span>',
            color,
            icon,
            obj.get_interaction_type_display()
        )
    interaction_type_badge.short_description = 'Type'


# ═══════════════════════════════════════════════════════════
# RECOMMENDATION ADMIN
# ═══════════════════════════════════════════════════════════

@admin.register(Recommendation)
class RecommendationAdmin(admin.ModelAdmin):
    list_display = [
        'user', 'product', 'score_bar', 'reason', 'timestamp'
    ]
    list_filter = ['timestamp']
    search_fields = ['user__username', 'product__name']
    readonly_fields = ['timestamp']
    date_hierarchy = 'timestamp'
    
    def score_bar(self, obj):
        """Display score as progress bar"""
        percentage = obj.score_percentage
        color = '#43AA8B' if percentage >= 70 else '#F8961E' if percentage >= 40 else '#F72585'
        return format_html(
            '<div style="width:100px;background:#f0f0f0;border-radius:10px;overflow:hidden;">'
            '<div style="width:{}%;background:{};color:white;text-align:center;padding:2px;font-size:11px;font-weight:bold;">'
            '{}%</div></div>',
            percentage,
            color,
            percentage
        )
    score_bar.short_description = 'AI Score'


# ═══════════════════════════════════════════════════════════
# USER PROFILE ADMIN (Inline with User)
# ═══════════════════════════════════════════════════════════

@admin.register(ExternalSource)
class ExternalSourceAdmin(admin.ModelAdmin):
    list_display = ['key', 'name', 'is_active', 'last_synced_at', 'updated_at']
    list_filter = ['is_active', 'key']
    search_fields = ['key', 'name']
    readonly_fields = ['last_synced_at', 'created_at', 'updated_at']


@admin.register(ExternalProduct)
class ExternalProductAdmin(admin.ModelAdmin):
    list_display = [
        'source', 'external_id', 'title', 'price', 'currency',
        'stock', 'is_published', 'published_product', 'updated_at'
    ]
    list_filter = ['source', 'is_published', 'currency']
    search_fields = ['external_id', 'title', 'category_name']
    readonly_fields = ['created_at', 'updated_at', 'last_synced_at']


@admin.register(ProductSyncLog)
class ProductSyncLogAdmin(admin.ModelAdmin):
    list_display = [
        'source', 'status', 'publish_enabled', 'fetched_count',
        'normalized_count', 'created_products_count', 'updated_products_count',
        'error_count', 'started_at', 'finished_at'
    ]
    list_filter = ['status', 'publish_enabled', 'source']
    readonly_fields = [
        'source', 'status', 'publish_enabled', 'started_at', 'finished_at',
        'fetched_count', 'normalized_count', 'created_external_count',
        'updated_external_count', 'created_products_count',
        'updated_products_count', 'skipped_count', 'error_count', 'summary', 'message'
    ]


class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'Profile'
    fields = [
        'profile_picture_preview', 'profile_picture', 'phone_number', 
        'address', 'subscription_type', 'subscription_start', 
        'subscription_end', 'bio'
    ]
    readonly_fields = ['profile_picture_preview']
    
    def profile_picture_preview(self, obj):
        """Display profile picture preview"""
        if obj.profile_picture:
            return format_html(
                '<img src="{}" width="100" height="100" style="object-fit:cover;border-radius:50%;"/>',
                obj.profile_picture.url
            )
        return format_html(
            '<div style="width:100px;height:100px;background:#f0f0f0;border-radius:50%;display:flex;align-items:center;justify-content:center;">No Image</div>'
        )
    profile_picture_preview.short_description = 'Current Picture'


# Extend User Admin to include UserProfile
class UserAdmin(BaseUserAdmin):
    inlines = (UserProfileInline,)


# Re-register UserAdmin
admin.site.unregister(User)
admin.site.register(User, UserAdmin)


# ═══════════════════════════════════════════════════════════
# ADMIN SITE CUSTOMIZATION
# ═══════════════════════════════════════════════════════════

admin.site.site_header = "🤖 AI Shop Admin Panel"
admin.site.site_title = "AI Shop Admin"
admin.site.index_title = "Welcome to AI Shop Administration"
