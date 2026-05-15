from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from store.models import UserProfile, Order, Feedback, Product, Category
import re


# ═══════════════════════════════════════════════════════════
# 1. USER SIGNUP FORM
# ═══════════════════════════════════════════════════════════

class UserSignupForm(UserCreationForm):
    """Complete signup form with profile fields"""
    
    first_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'First Name'
        })
    )
    
    last_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Last Name'
        })
    )
    
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Email Address'
        })
    )
    
    phone_number = forms.CharField(
        max_length=15,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '+92 300 1234567'
        })
    )
    
    profile_picture = forms.ImageField(
        required=False,
        widget=forms.FileInput(attrs={
            'class': 'form-control',
            'accept': 'image/*'
        })
    )
    
    subscription_type = forms.ChoiceField(
        choices=[('free', 'Free'), ('premium', 'Premium')],
        initial='free',
        widget=forms.Select(attrs={
            'class': 'form-select'
        })
    )
    
    agree_terms = forms.BooleanField(
        required=True,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        }),
        label='I agree to Terms and Privacy Policy'
    )
    
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password1', 'password2']
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Choose username'
            })
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Password'
        })
        self.fields['password2'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Confirm Password'
        })
    
    def clean_email(self):
        """Check if email is unique"""
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise ValidationError('This email is already registered.')
        return email
    
    def clean_username(self):
        """Check username has no special characters"""
        username = self.cleaned_data.get('username')
        if not re.match(r'^[a-zA-Z0-9_]+$', username):
            raise ValidationError('Username can only contain letters, numbers, and underscores.')
        return username


# ═══════════════════════════════════════════════════════════
# 2. USER LOGIN FORM
# ═══════════════════════════════════════════════════════════

class UserLoginForm(AuthenticationForm):
    """Custom login form with Bootstrap styling"""
    
    username = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Username or Email',
            'autofocus': True
        })
    )
    
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Password'
        })
    )
    
    remember_me = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        }),
        label='Remember Me'
    )


# ═══════════════════════════════════════════════════════════
# 3. USER PROFILE UPDATE FORM
# ═══════════════════════════════════════════════════════════

class UserProfileUpdateForm(forms.ModelForm):
    """Form to update user profile information"""
    
    first_name = forms.CharField(
        max_length=30,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'First Name'
        })
    )
    
    last_name = forms.CharField(
        max_length=30,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Last Name'
        })
    )
    
    email = forms.EmailField(
        required=False,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Email Address'
        })
    )
    
    class Meta:
        model = UserProfile
        fields = ['profile_picture', 'phone_number', 'address', 'bio']
        widgets = {
            'profile_picture': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            }),
            'phone_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '+92 300 1234567'
            }),
            'address': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Full Address'
            }),
            'bio': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'maxlength': 500,
                'placeholder': 'Tell us about yourself (max 500 characters)'
            })
        }


# ═══════════════════════════════════════════════════════════
# 4. PRODUCT SEARCH FORM
# ═══════════════════════════════════════════════════════════

class ProductSearchForm(forms.Form):
    """Advanced product search form"""
    
    query = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Search products...',
            'autofocus': True
        })
    )
    
    category = forms.ModelChoiceField(
        queryset=Category.objects.all(),
        required=False,
        empty_label='All Categories',
        widget=forms.Select(attrs={
            'class': 'form-select'
        })
    )
    
    min_price = forms.DecimalField(
        required=False,
        min_value=0,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Min Price',
            'min': 0
        })
    )
    
    max_price = forms.DecimalField(
        required=False,
        min_value=0,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Max Price',
            'min': 0
        })
    )
    
    sort_by = forms.ChoiceField(
        required=False,
        choices=[
            ('newest', 'Newest First'),
            ('price_asc', 'Price: Low to High'),
            ('price_desc', 'Price: High to Low'),
            ('rating', 'Highest Rated'),
            ('discount', 'Biggest Discount')
        ],
        widget=forms.Select(attrs={
            'class': 'form-select'
        })
    )


# ═══════════════════════════════════════════════════════════
# 5. ORDER FORM
# ═══════════════════════════════════════════════════════════

class OrderForm(forms.ModelForm):
    """Form for placing orders"""
    
    class Meta:
        model = Order
        fields = ['quantity', 'delivery_address', 'city', 'phone_number', 'notes']
        widgets = {
            'quantity': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 1,
                'value': 1
            }),
            'delivery_address': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Full delivery address'
            }),
            'city': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'City'
            }),
            'phone_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '+92 300 1234567'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Special instructions (optional)'
            })
        }
    
    def __init__(self, *args, product=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.product = product
    
    def clean_quantity(self):
        """Validate quantity against stock"""
        quantity = self.cleaned_data.get('quantity')
        if self.product and quantity > self.product.stock_level:
            raise ValidationError(
                f'Only {self.product.stock_level} items available in stock.'
            )
        if quantity < 1:
            raise ValidationError('Quantity must be at least 1.')
        return quantity
    
    def clean_phone_number(self):
        """Validate Pakistani phone format"""
        phone = self.cleaned_data.get('phone_number')
        # Accept formats: +92 300 1234567, 0300 1234567, 03001234567
        pattern = r'^(\+92|0)?3[0-9]{9}$'
        cleaned = phone.replace(' ', '').replace('-', '')
        if not re.match(pattern, cleaned):
            raise ValidationError(
                'Please enter a valid Pakistani phone number (e.g., +92 300 1234567 or 0300 1234567)'
            )
        return phone


# ═══════════════════════════════════════════════════════════
# 6. FEEDBACK FORM
# ═══════════════════════════════════════════════════════════

class FeedbackForm(forms.ModelForm):
    """Form for product feedback/reviews"""
    
    class Meta:
        model = Feedback
        fields = ['rating', 'comment']
        widgets = {
            'rating': forms.RadioSelect(
                choices=[(i, f'{i}') for i in range(1, 6)],
                attrs={'class': 'rating-radio'}
            ),
            'comment': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Tell us about this product...'
            })
        }
        labels = {
            'rating': 'Your Rating',
            'comment': 'Your Review (Optional)'
        }


# ═══════════════════════════════════════════════════════════
# 7. PRODUCT FORM (Admin Panel)
# ═══════════════════════════════════════════════════════════

class ProductForm(forms.ModelForm):
    """Complete product form for admin panel"""
    
    class Meta:
        model = Product
        fields = [
            'name', 'category', 'description', 'price', 'original_price',
            'discount_percentage', 'stock_level', 'image', 'is_available',
            'is_featured', 'is_on_discount', 'attributes'
        ]
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Product Name'
            }),
            'category': forms.Select(attrs={
                'class': 'form-select'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Product description...'
            }),
            'price': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 0,
                'step': 0.01
            }),
            'original_price': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 0,
                'step': 0.01
            }),
            'discount_percentage': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 0,
                'max': 100,
                'step': 0.01
            }),
            'stock_level': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 0
            }),
            'image': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            }),
            'is_available': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'is_featured': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'is_on_discount': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'attributes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': '{"brand": "Samsung", "color": "Black", "warranty": "1 Year"}'
            })
        }
    
    def clean_discount_percentage(self):
        """Ensure discount is between 0-100"""
        discount = self.cleaned_data.get('discount_percentage')
        if discount < 0 or discount > 100:
            raise ValidationError('Discount percentage must be between 0 and 100.')
        return discount
    
    def clean_price(self):
        """Ensure price is positive"""
        price = self.cleaned_data.get('price')
        if price <= 0:
            raise ValidationError('Price must be greater than 0.')
        return price
    
    def clean(self):
        """Cross-field validation"""
        cleaned_data = super().clean()
        is_on_discount = cleaned_data.get('is_on_discount')
        original_price = cleaned_data.get('original_price')
        price = cleaned_data.get('price')
        
        if is_on_discount:
            if not original_price:
                raise ValidationError({
                    'original_price': 'Original price is required when product is on discount.'
                })
            if original_price <= price:
                raise ValidationError({
                    'original_price': 'Original price must be greater than current price.'
                })
        
        return cleaned_data


# ═══════════════════════════════════════════════════════════
# 8. CONTACT FORM
# ═══════════════════════════════════════════════════════════

class ContactForm(forms.Form):
    """Contact/feedback form"""
    
    name = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Your Name'
        })
    )
    
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Your Email'
        })
    )
    
    subject = forms.CharField(
        max_length=200,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Subject'
        })
    )
    
    message = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 5,
            'placeholder': 'Your Message'
        })
    )
