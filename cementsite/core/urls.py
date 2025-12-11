from django.urls import path, reverse_lazy
from django.contrib.auth import views as auth_views
from django.views.generic import RedirectView
from . import views, webhooks

urlpatterns = [
    # Public pages
    path("", views.home, name="home"),
    path("blog/", views.blog_list, name="blog_list"),
    path("a/<slug:slug>/", views.article_detail, name="article_detail"),
    path("premium/", views.premium_list, name="premium_list"),
    path("pricing/", views.pricing, name="pricing"),

    # Checkout / Stripe
    path("buy/<str:plan_code>/", views.buy, name="buy"),
    path("checkout/success/", views.checkout_success, name="checkout_success"),
    path("checkout/cancel/", views.checkout_cancel, name="checkout_cancel"),
    path("stripe/webhook/", webhooks.stripe_webhook, name="stripe_webhook"),

    # In-browser authoring
    path("me/articles/", views.my_articles, name="my_articles"),
    path("me/articles/new/", views.ArticleCreatePublicView.as_view(), name="article_new_public"),
    path("me/articles/<slug:slug>/edit/", views.ArticleUpdatePublicView.as_view(), name="article_edit_public"),
    path("me/articles/<slug:slug>/delete/", views.article_delete_public, name="article_delete_public"),
    path("me/articles/<slug:slug>/publish/", views.article_publish, name="article_publish"),  # optional quick-publish

    # Auth (root-level)
    path("login/",  auth_views.LoginView.as_view(template_name="login.html"), name="login"),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
    path("signup/", views.signup, name="signup"),
    path("dashboard/", views.dashboard, name="dashboard"),

    # Compatibility redirects if older templates still point to /accounts/...
    path("accounts/login/",  RedirectView.as_view(url=reverse_lazy("login"),  permanent=False)),
    path("accounts/logout/", RedirectView.as_view(url=reverse_lazy("logout"), permanent=False)),
    path("accounts/signup/", RedirectView.as_view(url=reverse_lazy("signup"), permanent=False)),
]
