# 🤖 AI Shop - AI-Powered Personalized Product Platform

## Project by: Ayesha Khan (S23BINFT1M01014)
**IUB — Dept. of IT — Supervisor: Ms. Sara Farid**

---

## 🚀 Tech Stack
- **Backend:** Django 4.2.16
- **Database:** SQLite (upgradeable to PostgreSQL)
- **ML Engine:** Scikit-learn (Collaborative + Content-Based + Hybrid)
- **Frontend:** HTML5, CSS3, Bootstrap 5, JavaScript
- **Image Storage:** Django MediaFiles

---

## 📋 Setup Instructions

### 1. Virtual Environment (Already Created)
```bash
python -m venv venv
```

### 2. Activate Virtual Environment
**Windows:**
```bash
.\venv\Scripts\Activate.ps1
```

**Linux/Mac:**
```bash
source venv/bin/activate
```

### 3. Install Dependencies (Already Installed)
```bash
pip install -r requirements.txt
```

### 4. Run Migrations (Next Step)
```bash
python manage.py makemigrations
python manage.py migrate
```

### 5. Create Superuser
```bash
python manage.py createsuperuser
```

### 6. Run Development Server
```bash
python manage.py runserver
```

Visit: http://127.0.0.1:8000/

---

## 📁 Project Structure

```
ai_product_platform/
│
├── ai_product_platform/          # Main project settings
│   ├── settings.py               # ✅ Configured
│   ├── urls.py                   # ✅ Configured
│   ├── wsgi.py
│   └── asgi.py
│
├── store/                        # Main app
│   ├── models.py                 # ⏳ PROMPT 2
│   ├── views.py                  # ⏳ PROMPT 5
│   ├── forms.py                  # ⏳ PROMPT 4
│   ├── urls.py                   # ✅ Basic setup
│   ├── admin.py                  # ⏳ PROMPT 2
│   ├── signals.py                # ⏳ PROMPT 2
│   ├── recommendation_engine.py  # ⏳ PROMPT 3
│   │
│   ├── management/commands/      # ✅ Created
│   ├── templates/                # ✅ Created
│   └── templatetags/             # ✅ Created
│
├── static/                       # ✅ Created
│   ├── css/style.css
│   ├── js/main.js
│   └── images/
│
├── media/                        # ✅ Created (for product images)
│
├── venv/                         # ✅ Virtual environment
├── manage.py
└── requirements.txt              # ✅ Created

```

---

## ✅ PROMPT 1 - COMPLETED

### What Was Created:
1. ✅ Virtual environment setup
2. ✅ All required packages installed
3. ✅ Django project created
4. ✅ Store app created
5. ✅ Complete folder structure
6. ✅ Settings.py fully configured
7. ✅ Main URLs configured with MEDIA serving
8. ✅ Apps.py configured with signals
9. ✅ Placeholder files for future prompts

### Key Configurations:
- **INSTALLED_APPS:** Added store, crispy_forms, crispy_bootstrap5
- **MIDDLEWARE:** Added WhiteNoiseMiddleware for static files
- **TEMPLATES:** Configured to use store/templates
- **STATIC_URL & MEDIA_URL:** Properly configured
- **LOGIN/LOGOUT URLs:** Set up
- **MESSAGE_TAGS:** Bootstrap 5 classes
- **SESSION:** 2 weeks expiry

### Critical Setup:
```python
# In main urls.py - MANDATORY for image display
urlpatterns = [
    path('django-admin/', admin.site.urls),
    path('', include('store.urls', namespace='store')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
```

---

## 📝 Next Steps

### PROMPT 2 - Database Models
- Create all 7 models (Category, Product, UserInteraction, Recommendation, Order, Feedback, UserProfile)
- Set up signals
- Configure admin panel

### PROMPT 3 - AI Recommendation Engine
- Build ML engine with scikit-learn
- Implement Collaborative Filtering
- Implement Content-Based Filtering
- Create Hybrid recommendation system

---

## 🔧 Useful Commands

```bash
# Check project
python manage.py check

# Make migrations
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Run server
python manage.py runserver

# Import real products from CSV
python manage.py import_products

# Clear and re-import safely
python manage.py import_products --clear

# Generate recommendations (after PROMPT 3)
python manage.py generate_recommendations
```

## 📦 Product Import

```bash
# Verify imported data
python manage.py shell
```

```python
from store.models import Product, Category
print(Product.objects.count())
print(Category.objects.count())
```

If you need a repeat import, use `python manage.py import_products --clear` first.  
The importer reads the real CSV files from `BASE_DIR` and updates existing products instead of duplicating them.

---

## 📦 Installed Packages

- Django 4.2.16
- Pillow (for images)
- scikit-learn (for ML)
- pandas (for data manipulation)
- numpy (for numerical operations)
- django-crispy-forms
- crispy-bootstrap5
- whitenoise (for static files)

---

## 🎯 Project Goals

1. ✅ Full-stack e-commerce platform
2. ⏳ AI-powered product recommendations
3. ⏳ User behavior tracking
4. ⏳ Machine Learning integration
5. ⏳ Professional UI/UX
6. ⏳ Admin dashboard
7. ⏳ Order management
8. ⏳ Product reviews & ratings

---

**Status:** PROMPT 1 ✅ COMPLETED
**Next:** PROMPT 2 - Database Models & Signals
