from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from django.db.models import Avg
from .models import UserProfile, Feedback, Order, Product, UserInteraction

# ═══════════════════════════════════════════════════════════
# SIGNAL 1: Auto-create UserProfile when User is created
# ═══════════════════════════════════════════════════════════

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """
    Automatically create a UserProfile when a new User is created.
    This ensures every user has a profile.
    """
    if created:
        UserProfile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """
    Save the UserProfile whenever the User is saved.
    """
    if hasattr(instance, 'profile'):
        instance.profile.save()


# ═══════════════════════════════════════════════════════════
# SIGNAL 2: Auto-update product rating when Feedback is submitted
# ═══════════════════════════════════════════════════════════

@receiver(post_save, sender=Feedback)
def update_product_rating(sender, instance, created, **kwargs):
    """
    Automatically recalculate and update product rating
    when new feedback is submitted.
    """
    if created:
        product = instance.product
        # Calculate average rating from all feedbacks
        avg_rating = Feedback.objects.filter(
            product=product
        ).aggregate(Avg('rating'))['rating__avg']
        
        if avg_rating:
            product.rating = round(avg_rating, 1)
            product.save(update_fields=['rating'])


# ═══════════════════════════════════════════════════════════
# SIGNAL 3: Auto-update product stock when Order is confirmed
# ═══════════════════════════════════════════════════════════

@receiver(post_save, sender=Order)
def update_product_stock(sender, instance, created, **kwargs):
    """
    Automatically decrease product stock when order is confirmed.
    Only triggers on order creation, not updates.
    """
    if created:
        product = instance.product
        if product.stock_level >= instance.quantity:
            product.stock_level -= instance.quantity
            product.save(update_fields=['stock_level'])


# ═══════════════════════════════════════════════════════════
# SIGNAL 4: Log purchase interaction after order creation
# ═══════════════════════════════════════════════════════════

@receiver(post_save, sender=Order)
def log_purchase_interaction(sender, instance, created, **kwargs):
    """
    Automatically log a 'purchase' interaction when order is created.
    This feeds data to the ML recommendation engine.
    """
    if created:
        interaction, int_created = UserInteraction.objects.get_or_create(
            user=instance.user,
            product=instance.product,
            interaction_type='purchase',
            defaults={'interaction_count': instance.quantity}
        )
        
        if not int_created:
            # If interaction already exists, increment count
            interaction.interaction_count += instance.quantity
            interaction.save(update_fields=['interaction_count'])
