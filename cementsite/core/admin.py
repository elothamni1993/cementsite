from django.contrib import admin
from .models import Plan, Subscription, Article
from .models import Visit

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
@admin.register(Visit)
class VisitAdmin(admin.ModelAdmin):
    list_display = (
        "created_at", 
        "visitor_type", 
        "page", 
        "traffic_badge",
        "time_display",
        "premium_badge",
        "ip_short"
    )
    list_filter = (
        "traffic_source",
        "is_returning",
        "clicked_premium",
        ("created_at", admin.DateFieldListFilter),
    )
    search_fields = ("path", "ip", "user_agent", "referer", "session_key")
    readonly_fields = (
        "created_at", 
        "path", 
        "ip", 
        "user_agent", 
        "referer", 
        "session_key",
        "is_returning",
        "time_spent",
        "clicked_premium",
        "traffic_source"
    )
    date_hierarchy = "created_at"
    ordering = ("-created_at",)
    list_per_page = 50
    
    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False
    
    def visitor_type(self, obj):
        if obj.is_returning:
            return "🔄 Returning"
        return "🆕 New"
    visitor_type.short_description = "Visitor"
    visitor_type.admin_order_field = "is_returning"
    
    def page(self, obj):
        path = obj.path[:40]
        if len(obj.path) > 40:
            path += "..."
        return path
    page.short_description = "Page"
    page.admin_order_field = "path"
    
    def traffic_badge(self, obj):
        colors = {
            "search": "🔍",
            "social": "📱",
            "direct": "🔗",
            "internal": "🏠",
        }
        icon = colors.get(obj.traffic_source, "🌐")
        return f"{icon} {obj.traffic_source.title()}"
    traffic_badge.short_description = "Source"
    traffic_badge.admin_order_field = "traffic_source"
    
    def time_display(self, obj):
        if obj.time_spent == 0:
            return "-"
        mins = obj.time_spent // 60
        secs = obj.time_spent % 60
        if mins > 0:
            return f"{mins}m {secs}s"
        return f"{secs}s"
    time_display.short_description = "Time Spent"
    time_display.admin_order_field = "time_spent"
    
    def premium_badge(self, obj):
        return "⭐ Yes" if obj.clicked_premium else "—"
    premium_badge.short_description = "Premium"
    premium_badge.admin_order_field = "clicked_premium"
    
    def ip_short(self, obj):
        if not obj.ip:
            return "—"
        parts = str(obj.ip).split(".")
        if len(parts) == 4:
            return f"{parts[0]}.{parts[1]}.*.* "
        return obj.ip
    ip_short.short_description = "IP"
    ip_short.admin_order_field = "ip"
