from django.db import models
from django.db.models import Q
from django.contrib.auth.models import User
from django.utils.text import slugify
import uuid

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

