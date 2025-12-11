from django.contrib import admin
from .models import Plan, Subscription, Article

@admin.register(Plan)
class PlanAdmin(admin.ModelAdmin):
    list_display = ("name","code","price_usd_month","stripe_price_id")
    list_display_links = ("name",)
    list_editable = ("price_usd_month",)
    search_fields = ("name","code","stripe_price_id")
    ordering = ("name",)
    readonly_fields = ("stripe_price_id",)

@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ("user","plan","active","current_period_end","stripe_customer_id","stripe_subscription_id")
    list_display_links = ("user",)
    list_editable = ("active",)
    list_filter = ("active","plan")
    ordering = ("-current_period_end",)
    readonly_fields = ("stripe_customer_id","stripe_subscription_id")
    autocomplete_fields = ["plan"]
    date_hierarchy = "current_period_end"

@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ("title","access_level","published","created_at")
    list_display_links = ("title",)
    list_editable = ("access_level","published",)
    list_filter = ("access_level","published")
    ordering = ("-created_at",)
    readonly_fields = ("created_at",)
    prepopulated_fields = {"slug": ("title",)}
    date_hierarchy = "created_at"
