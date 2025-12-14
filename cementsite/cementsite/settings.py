import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

# Environment via os.environ only (simple starter); you can add python-dotenv later if you want.
SECRET_KEY = os.environ.get("SECRET_KEY", "change_me")
DEBUG = os.environ.get("DEBUG", "True") == "True"
ALLOWED_HOSTS = [h for h in os.environ.get("ALLOWED_HOSTS","127.0.0.1,localhost,cementsite.onrender.com").split(",") if h]

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "core",
    "ckeditor",
    "ckeditor_uploader",
    
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "cementsite.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "core" / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "core.context.adsense_keys",
                "core.context.stripe_keys",
                "core.context.user_tier",

            ],
        },
    },
]

WSGI_APPLICATION = "cementsite.wsgi.application"

# Database: default to SQLite; switch to DATABASE_URL if provided
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

_db_url = os.environ.get("DATABASE_URL")
if _db_url:
    try:
        import dj_database_url
        DATABASES["default"] = dj_database_url.parse(
            _db_url,
            conn_max_age=600,
            ssl_require=True,
        )
    except Exception:
        # Fall back to SQLite if parsing fails
        pass

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",},
]

LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

STATIC_URL = "static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# add near the bottom
LOGIN_URL = "/accounts/login/"
LOGIN_REDIRECT_URL = "/dashboard/"
LOGOUT_REDIRECT_URL = "/"


# CKEditor config (simple, focused toolbar)
CKEDITOR_UPLOAD_PATH = "uploads/"
CKEDITOR_IMAGE_BACKEND = "pillow"
CKEDITOR_CONFIGS = {
    "default": {
        "toolbar": [
            {"name": "basicstyles", "items": ["Bold", "Italic", "Underline", "-", "RemoveFormat"]},
            {"name": "paragraph", "items": ["NumberedList", "BulletedList", "-", "Outdent", "Indent"]},
            {"name": "links", "items": ["Link", "Unlink"]},
            {"name": "insert", "items": ["Image", "Table"]},
            {"name": "editing", "items": ["Scayt"]},
            {"name": "document", "items": ["Source"]},
        ],
        "height": 320,
        "width": "100%",
        "removePlugins": "exportpdf",
    }
}
