import os
from pathlib import Path

# Base directory
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
# PUBLIC_INTERFACE
def get_env(name: str, default: str = ""):
    """Get environment variable with default fallback."""
    return os.environ.get(name, default)

# PUBLIC_INTERFACE
def get_bool(name: str, default: bool = False) -> bool:
    """Get boolean env var by interpreting common truthy/falsey strings."""
    val = os.environ.get(name)
    if val is None:
        return default
    return str(val).strip().lower() in {"1", "true", "yes", "on"}

SECRET_KEY = get_env("DJANGO_SECRET_KEY", "dev-not-secure")
DEBUG = get_bool("DJANGO_DEBUG", True)

ALLOWED_HOSTS = [h.strip() for h in get_env("DJANGO_ALLOWED_HOSTS", "localhost,127.0.0.1").split(",") if h.strip()]
# Ensure dev frontend host:port is allowed (React default is 3000)
if "localhost" not in ALLOWED_HOSTS:
    ALLOWED_HOSTS.append("localhost")
if "127.0.0.1" not in ALLOWED_HOSTS:
    ALLOWED_HOSTS.append("127.0.0.1")

# Application definition
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # CORS support
    "corsheaders",
    # app-specific entries can be added here (e.g., "quiz")
]

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",  # must be high in the list
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"

# Database
# Expect environment variables to be provided; we default to Postgres on port 5001 for local dev.
DB_NAME = get_env("POSTGRES_DB", "quizdb")
DB_USER = get_env("POSTGRES_USER", "postgres")
DB_PASSWORD = get_env("POSTGRES_PASSWORD", "postgres")
DB_HOST = get_env("POSTGRES_HOST", "localhost")
DB_PORT = get_env("POSTGRES_PORT", "5001")  # default to 5001 per integration requirement

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": DB_NAME,
        "USER": DB_USER,
        "PASSWORD": DB_PASSWORD,
        "HOST": DB_HOST,
        "PORT": DB_PORT,
    }
}

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# Internationalization
LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

# Static files
STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# CORS configuration
# PUBLIC_INTERFACE
def _parse_list(value: str):
    """Parse a comma-separated list into a list of trimmed entries."""
    return [v.strip() for v in (value or "").split(",") if v.strip()]

# Allow specific origins from env; default allow localhost:3000
CORS_ALLOWED_ORIGINS = _parse_list(get_env("CORS_ALLOWED_ORIGINS", "http://localhost:3000,http://127.0.0.1:3000"))

# For dev, we also extend trusted origins for CSRF if needed
CSRF_TRUSTED_ORIGINS = _parse_list(get_env("CSRF_TRUSTED_ORIGINS", "http://localhost:3000,http://127.0.0.1:3000"))

# If broad CORS is desired in development:
CORS_ALLOW_CREDENTIALS = get_bool("CORS_ALLOW_CREDENTIALS", True)
