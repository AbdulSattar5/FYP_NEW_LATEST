from django.db import models
from django.db.models import Q
from django.contrib.auth.models import User
from django.utils.text import slugify
import uuid

from store.utils.commerce import (
    external_source_key_from_attributes,
    is_demo_api_source,
    is_local_checkout_source,
    resolve_buy_on_source_url,
)

# ═══════════════════════════════════════════════════════════
# CATEGORY MODEL
# ═══════════════════════════════════════════════════════════

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True, blank=True)
    description = models.TextField(blank=True)
    icon = models.CharField(
        max_length=50, 
        default='fa-tag',
        help_text='FontAwesome icon class e.g. fa-laptop, fa-shirt, fa-mobile'
    )
    color = models.CharField(
        max_length=7, 
        default='#6C63FF',
        help_text='Hex color for category card background'
    )
    image = models.ImageField(upload_to='categories/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name_plural = "Categories"
        ordering = ['name']
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    
    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('store:category_products', kwargs={'slug': self.slug})


# ═══════════════════════════════════════════════════════════
# PRODUCT MODEL
# ═══════════════════════════════════════════════════════════

class ExternalSource(models.Model):
    SOURCE_KEYS = [
        ('dummyjson', 'DummyJSON'),
        ('platzi', 'Platzi Fake Store'),
        ('bestbuy', 'Best Buy'),
        ('demo_generated', 'Demo Generated (local)'),
    ]

    key = models.CharField(max_length=50, unique=True, choices=SOURCE_KEYS)
    name = models.CharField(max_length=120)
    base_url = models.URLField(blank=True)
    is_active = models.BooleanField(default=True)
    last_synced_at = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class Product(models.Model):
    product_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True, blank=True)
    category = models.ForeignKey(
        Category, 
        on_delete=models.CASCADE, 
        related_name='products'
    )
    description = models.TextField()
    
    # Pricing
    price = models.DecimalField(max_digits=10, decimal_places=2)
    original_price = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        blank=True, 
        null=True,
        help_text='Price before discount'
    )
    is_on_discount = models.BooleanField(default=False)
    discount_percentage = models.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        default=0,
        help_text='e.g. 20 for 20% off'
    )
    
    # Image — stores in media/products/
    image = models.ImageField(upload_to='products/', blank=True, null=True)
    
    # Inventory
    stock_level = models.IntegerField(default=0)
    is_available = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)
    is_external = models.BooleanField(default=False)
    manages_local_stock = models.BooleanField(
        default=True,
        help_text='If false, this product is sourced externally and checkout happens on partner site.',
    )
    external_url = models.URLField(blank=True)
    
    # Stats (auto-calculated)
    rating = models.DecimalField(max_digits=3, decimal_places=1, default=0.0)
    
    # Product attributes (flexible JSON for brand, color, size, etc.)
    attributes = models.JSONField(
        default=dict, 
        blank=True,
        help_text='{"brand": "Samsung", "color": "Black", "warranty": "1 Year"}'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return self.name
    
    @property
    def discount_price(self):
        """Calculate discounted price"""
        if self.is_on_discount and self.discount_percentage:
            discount = self.price * (self.discount_percentage / 100)
            return round(self.price - discount, 2)
        return self.price
    
    @property
    def is_in_stock(self):
        """Check if product is in stock"""
        return self.stock_level > 0 and self.is_available

    @property
    def external_source_key(self) -> str:
        return external_source_key_from_attributes(self.attributes)

    @property
    def is_demo_api_product(self) -> bool:
        """DummyJSON / Platzi / demo-generated products use local checkout."""
        if is_local_checkout_source(self.external_source_key):
            return True
        if isinstance(self.attributes, dict) and self.attributes.get('generated'):
            return True
        return False

    @property
    def buy_on_source_url(self) -> str:
        """Safe storefront URL for affiliate checkout, never an API JSON endpoint."""
        if self.is_demo_api_product:
            return ''
        return resolve_buy_on_source_url(self.external_url, self.attributes)

    @property
    def is_affiliate_product(self):
        """True only when checkout happens on a real external storefront."""
        if self.is_demo_api_product or self.manages_local_stock:
            return False
        return bool(self.buy_on_source_url)

    @property
    def can_add_to_cart(self):
        """Allow local cart when product is available and not affiliate-only."""
        if not self.is_available:
            return False
        if self.is_affiliate_product:
            return False
        return self.stock_level > 0

    @property
    def stock_status_label(self):
        """Human readable stock/source label for cards and details."""
        if not self.is_available:
            return 'Unavailable'
        if self.is_affiliate_product:
            return 'Available on source'
        if self.stock_level > 0:
            return 'In stock'
        return 'Out of stock'

    @property
    def external_image_url(self):
        """Remote image URL stored in attributes when product is imported externally."""
        if not isinstance(self.attributes, dict):
            return ''
        value = self.attributes.get('external_image_url') or self.attributes.get('image_url')
        return str(value).strip() if value else ''
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name) + '-' + str(uuid.uuid4())[:8]
        super().save(*args, **kwargs)
    
    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('store:product_detail', kwargs={'pk': self.product_id})


# ═══════════════════════════════════════════════════════════
# USER INTERACTION MODEL (feeds the ML engine)
# ═══════════════════════════════════════════════════════════

class ExternalProduct(models.Model):
    source = models.ForeignKey(
        ExternalSource,
        on_delete=models.CASCADE,
        related_name='external_products',
    )
    external_id = models.CharField(max_length=120)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    category_name = models.CharField(max_length=120, blank=True)
    price = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    currency = models.CharField(max_length=10, default='USD')
    image_url = models.URLField(blank=True)
    rating = models.DecimalField(max_digits=3, decimal_places=1, blank=True, null=True)
    stock = models.IntegerField(blank=True, null=True)
    availability = models.CharField(max_length=120, blank=True)
    product_url = models.URLField(blank=True)
    raw_data = models.JSONField(default=dict, blank=True)
    is_published = models.BooleanField(default=False)
    published_product = models.OneToOneField(
        Product,
        on_delete=models.SET_NULL,
        related_name='external_product',
        blank=True,
        null=True,
    )
    last_synced_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-updated_at']
        constraints = [
            models.UniqueConstraint(
                fields=['source', 'external_id'],
                name='unique_external_source_product',
            ),
        ]
        indexes = [
            models.Index(fields=['source', 'external_id']),
            models.Index(fields=['is_published']),
        ]

    def __str__(self):
        return f"{self.source.key}:{self.external_id} - {self.title}"


class ProductSyncLog(models.Model):
    STATUS_CHOICES = [
        ('success', 'Success'),
        ('partial', 'Partial'),
        ('failed', 'Failed'),
    ]

    source = models.ForeignKey(
        ExternalSource,
        on_delete=models.SET_NULL,
        related_name='sync_logs',
        blank=True,
        null=True,
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='success')
    publish_enabled = models.BooleanField(default=False)
    started_at = models.DateTimeField(auto_now_add=True)
    finished_at = models.DateTimeField(blank=True, null=True)
    fetched_count = models.PositiveIntegerField(default=0)
    normalized_count = models.PositiveIntegerField(default=0)
    created_external_count = models.PositiveIntegerField(default=0)
    updated_external_count = models.PositiveIntegerField(default=0)
    created_products_count = models.PositiveIntegerField(default=0)
    updated_products_count = models.PositiveIntegerField(default=0)
    skipped_count = models.PositiveIntegerField(default=0)
    error_count = models.PositiveIntegerField(default=0)
    summary = models.JSONField(default=dict, blank=True)
    message = models.TextField(blank=True)

    class Meta:
        ordering = ['-started_at']

    def __str__(self):
        source_key = self.source.key if self.source_id else 'unknown'
        return f"{source_key} sync @ {self.started_at:%Y-%m-%d %H:%M:%S}"


INTERACTION_TYPES = [
    ('view', 'Viewed'),
    ('click', 'Clicked'),
    ('cart', 'Added to Cart'),
    ('purchase', 'Purchased'),
    ('like', 'Liked/Feedback'),
    ('search', 'Searched'),
]

class UserInteraction(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='interactions',
        null=True,
        blank=True,
    )
    session_key = models.CharField(max_length=64, blank=True, null=True, db_index=True)
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='interactions',
        null=True,
        blank=True,
    )
    interaction_type = models.CharField(max_length=20, choices=INTERACTION_TYPES)
    interaction_count = models.IntegerField(default=1)
    query = models.CharField(max_length=255, blank=True)
    metadata = models.JSONField(default=dict, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        constraints = [
            models.CheckConstraint(
                check=Q(user__isnull=False) | Q(session_key__isnull=False),
                name='interaction_user_or_session_present',
            ),
        ]
        indexes = [
            models.Index(fields=['timestamp']),
            models.Index(fields=['interaction_type', 'timestamp']),
            models.Index(fields=['user', 'timestamp']),
            models.Index(fields=['session_key', 'timestamp']),
            models.Index(fields=['product', 'timestamp']),
        ]
        ordering = ['-timestamp']

    def __str__(self):
        actor = self.user.username if self.user_id else f"session:{self.session_key}"
        product_name = self.product.name if self.product_id else 'n/a'
        return f"{actor} -> {product_name} ({self.interaction_type})"


# ═══════════════════════════════════════════════════════════
# RECOMMENDATION MODEL (stores ML-generated results)
# ═══════════════════════════════════════════════════════════

class Recommendation(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recommendations',
        null=True,
        blank=True,
    )
    session_key = models.CharField(max_length=64, blank=True, null=True, db_index=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    score = models.FloatField(
        default=0.0,
        help_text='Relevance score 0.0 to 1.0 from ML engine'
    )
    reason = models.CharField(
        max_length=200,
        default='Based on your activity',
        help_text='Human-readable reason for recommendation'
    )
    timestamp = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-score']
        constraints = [
            models.CheckConstraint(
                check=Q(user__isnull=False) | Q(session_key__isnull=False),
                name='recommendation_user_or_session_present',
            ),
            models.UniqueConstraint(
                fields=['user', 'product'],
                condition=Q(user__isnull=False),
                name='unique_recommendation_user_product',
            ),
            models.UniqueConstraint(
                fields=['session_key', 'product'],
                condition=Q(session_key__isnull=False),
                name='unique_recommendation_session_product',
            ),
        ]

    def __str__(self):
        actor = self.user.username if self.user_id else f"session:{self.session_key}"
        return f"Rec for {actor}: {self.product.name} ({self.score:.2f})"
    
    @property
    def score_percentage(self):
        """Convert score to percentage"""
        return int(self.score * 100)


# ═══════════════════════════════════════════════════════════
# ORDER MODEL
# ═══════════════════════════════════════════════════════════

ORDER_STATUS = [
    ('pending', 'Pending'),
    ('confirmed', 'Confirmed'),
    ('processing', 'Processing'),
    ('shipped', 'Shipped'),
    ('delivered', 'Delivered'),
    ('cancelled', 'Cancelled'),
]

class Order(models.Model):
    order_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='orders'
    )
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)
    
    # Delivery details
    delivery_address = models.TextField()
    city = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=15)
    
    # Pricing snapshot (keep original price at order time)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    
    status = models.CharField(
        max_length=20, 
        choices=ORDER_STATUS, 
        default='pending'
    )
    notes = models.TextField(blank=True)
    ordered_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-ordered_at']
    
    def __str__(self):
        return f"Order #{self.order_id} — {self.user.username} — {self.product.name}"
    
    def save(self, *args, **kwargs):
        self.total_price = self.unit_price * self.quantity
        super().save(*args, **kwargs)


# ═══════════════════════════════════════════════════════════
# FEEDBACK MODEL
# ═══════════════════════════════════════════════════════════

class Feedback(models.Model):
    RATING_CHOICES = [(i, f'{i} Star{"s" if i > 1 else ""}') for i in range(1, 6)]
    
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='feedbacks'
    )
    product = models.ForeignKey(
        Product, 
        on_delete=models.CASCADE, 
        related_name='feedbacks'
    )
    rating = models.IntegerField(choices=RATING_CHOICES)
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['user', 'product']
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.username} rated {self.product.name}: {self.rating}/5"


# ═══════════════════════════════════════════════════════════
# USER PROFILE MODEL (extends Django User)
# ═══════════════════════════════════════════════════════════

class UserProfile(models.Model):
    user = models.OneToOneField(
        User, 
        on_delete=models.CASCADE, 
        related_name='profile'
    )
    profile_picture = models.ImageField(
        upload_to='profiles/', 
        blank=True, 
        null=True
    )
    phone_number = models.CharField(max_length=15, blank=True)
    address = models.TextField(blank=True)
    
    SUBSCRIPTION_TYPES = [
        ('free', 'Free'),
        ('premium', 'Premium'),
    ]
    subscription_type = models.CharField(
        max_length=10,
        choices=SUBSCRIPTION_TYPES,
        default='free'
    )
    subscription_start = models.DateField(null=True, blank=True)
    subscription_end = models.DateField(null=True, blank=True)
    
    bio = models.TextField(blank=True, max_length=500)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Profile of {self.user.username}"

