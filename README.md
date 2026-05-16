# AI product store (Django)

E-commerce-style storefront with session cart, orders, interaction tracking, and a TF–IDF / popularity-aware recommender trained from your data.

## Prerequisites

- Python 3.10+
- (Optional) Product CSV files in the project root for `import_products` — see `store/product_importer.py` for expected formats.

## Environment setup

Create and activate a virtual environment so dependencies do not clash with other tools on your machine:

```bash
python -m venv .venv

# Windows (PowerShell)
.\.venv\Scripts\Activate.ps1

# Windows (cmd) / Linux / macOS
# .venv\Scripts\activate   or   source .venv/bin/activate

pip install --upgrade pip
pip install -r requirements.txt
```

`requirements.txt` is the lightweight production/runtime install. It is intended for small hosts such as PythonAnywhere and keeps the storefront, cart, checkout, API sync, and fallback recommendations working.

Optional installs:

```bash
# Only needed when training the full ML recommender locally or on a larger server
pip install -r requirements-ml.txt

# Only needed when USE_CLOUDINARY_STORAGE=true
pip install -r requirements-cloudinary.txt
```

Copy the example environment file and edit values:

```bash
copy .env.example .env   # Windows
# cp .env.example .env    # Linux / macOS
```

### `.env` variables

| Variable | Purpose |
|----------|---------|
| `SECRET_KEY` | Django secret. Required when `DEBUG=false`. |
| `DEBUG` | `true` / `false` (default in code: `true` if unset). |
| `ALLOWED_HOSTS` | Comma-separated hostnames (no spaces). |
| `CLOUDINARY_*` | Optional; all three must be set to enable Cloudinary SDK config. |
| `USE_CLOUDINARY_STORAGE` | `true` to use Cloudinary as default file storage for uploads. |
| `DEFAULT_PRODUCT_SOURCE` | Default provider for sync: `dummyjson`, `platzi`, or `bestbuy`. |
| `BESTBUY_API_KEY` | API key for Best Buy product sync (optional). |

See `.env.example` for a template.

## Database migrations

```bash
python manage.py migrate
```

## Import products (CSV)

Requires a compatible CSV in the project root (auto-detects cleaned / products / UK format). Optional category file `amazon_categories.csv` helps UK imports.

```bash
python manage.py import_products
# Options: --source auto|cleaned|products|uk --clear --limit N
```

## Sync products from external APIs

Products are fetched from the provider, normalized, stored in `ExternalProduct`, and optionally published to the local `Product` table. The site always reads from the database, not live APIs.

Supported sources (in priority order for testing):

1. **DummyJSON** — `https://dummyjson.com/products` (no API key)
2. **Platzi Fake Store** — `https://api.escuelajs.co/api/v1/products`
3. **Best Buy** — requires `BESTBUY_API_KEY` in `.env` ([Best Buy Developer](https://developer.bestbuy.com/apis))

```bash
# Default source from DEFAULT_PRODUCT_SOURCE (dummyjson)
python manage.py sync_external_products --source dummyjson --limit 100 --publish true

# Other providers
python manage.py sync_external_products --source platzi --limit 50 --publish true
python manage.py sync_external_products --source bestbuy --limit 25 --publish true
```

Affiliate imports use **Buy on Source** (external URL). Local inventory products still use **Add to Cart**.

## Train recommender and generate recommendations

Artifacts are written under `models/recommender/` (ignored by git by default). Training needs the optional ML stack:

```bash
pip install -r requirements-ml.txt
python manage.py train_recommender
python manage.py generate_recommendations
```

If the ML stack is not installed, the live site still works and serves popularity/category fallback recommendations from database products.

Options are documented on each command (`--help`).

## Run the development server

```bash
python manage.py runserver
```

Visit `http://127.0.0.1:8000/`. Use `django-admin/` for the built-in admin (create a superuser with `python manage.py createsuperuser`).

## Run tests

```bash
python manage.py check
python manage.py makemigrations --check
python manage.py test
```

The suite covers APIs (search suggestions, track, cart, recommendations), checkout and idempotency, product import (minimal CSV), templates, and the recommender pipeline (`store/test_recommender_pipeline.py`).

## Deployment notes

1. **Never commit** `.env`, `db.sqlite3`, virtualenv folders, or generated `models/recommender/` artifacts.
2. Set `DEBUG=false`, set a strong `SECRET_KEY`, and set `ALLOWED_HOSTS` to your domain(s).
3. Use a production database (PostgreSQL, etc.) instead of SQLite when handling real traffic.
4. Collect static files: `python manage.py collectstatic` (WhiteNoise is enabled).
5. On disk-limited hosts, install only `requirements.txt`; do not install `requirements-ml.txt` unless you have enough quota.
6. Regenerate recommender artifacts on a larger machine after significant new interaction/product data, then deploy artifacts if desired.
7. If you use Cloudinary, install `requirements-cloudinary.txt`, set all three Cloudinary variables, and optionally `USE_CLOUDINARY_STORAGE=true`.
8. Rotating credentials: the previous Cloudinary keys that were hard-coded in settings have been removed; create new keys in the Cloudinary dashboard if those were ever exposed.

## Project layout (high level)

- `ai_product_platform/` — Django settings and root URLs
- `store/` — models, views, templates, recommender engine, management commands
- `static/`, `media/` — static assets and user/media uploads in development
