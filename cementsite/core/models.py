from django.conf import settings
from django.db import models
from django.utils import timezone
from django.utils.text import slugify

try:
    # If you installed ckeditor/ckeditor_uploader
    from ckeditor_uploader.fields import RichTextUploadingField
    _HAS_CK = True
except Exception:
    _HAS_CK = False


class Plan(models.Model):
    BASIC = "basic"
    PRO = "pro"
    TIERS = [(BASIC, "Basic"), (PRO, "Pro")]

    code = models.CharField(max_length=20, choices=TIERS, unique=True)
    name = models.CharField(max_length=50)
    price_usd_month = models.DecimalField(max_digits=6, decimal_places=2)
    stripe_price_id = models.CharField(max_length=200, help_text="Stripe Price ID")

    def __str__(self):
        return f"{self.name} ({self.code})"


class Subscription(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    plan = models.ForeignKey(Plan, on_delete=models.SET_NULL, null=True, blank=True)
    active = models.BooleanField(default=False)
    current_period_end = models.DateTimeField(null=True, blank=True)
    stripe_customer_id = models.CharField(max_length=200, blank=True, default="")
    stripe_subscription_id = models.CharField(max_length=200, blank=True, default="")

    def is_active(self):
        return self.active and (self.current_period_end is None or self.current_period_end > timezone.now())


def _unique_slug(model_cls, instance_pk, value: str) -> str:
    base = slugify(value)[:80] or "post"
    slug = base
    i = 2
    qs = model_cls.objects.all()
    if instance_pk:
        qs = qs.exclude(pk=instance_pk)
    while qs.filter(slug=slug).exists():
        slug = f"{base}-{i}"
        i += 1
    return slug


class Article(models.Model):
    FREE = "free"
    BASIC = "basic"
    PRO = "pro"
    ACCESS = [(FREE, "Free"), (BASIC, "Basic"), (PRO, "Pro")]

    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, blank=True)
    excerpt = models.TextField(blank=True)
    body = RichTextUploadingField() if _HAS_CK else models.TextField()
    access_level = models.CharField(max_length=10, choices=ACCESS, default=FREE)
    published = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="articles", null=True, blank=True
    )

    def requires_subscription(self):
        return self.access_level in [self.BASIC, self.PRO]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = _unique_slug(Article, getattr(self, "pk", None), self.title)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title


class Visit(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    path = models.CharField(max_length=512)
    ip = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.CharField(max_length=512, blank=True)
    referer = models.CharField(max_length=512, blank=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL)

    def __str__(self):
        return f"{self.ip} {self.path} {self.created_at:%Y-%m-%d %H:%M}"

class Attachment(models.Model):
    article = models.ForeignKey(Article, on_delete=models.CASCADE, related_name="attachments")
    title = models.CharField(max_length=200, blank=True)
    file = models.FileField(upload_to="attachments/%Y/%m/")
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title or (self.file.name if self.file else "Attachment")
