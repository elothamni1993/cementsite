from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.paginator import Paginator
from django.http import HttpResponse, HttpResponseForbidden
from django.urls import reverse, reverse_lazy
from django.utils.timezone import now
from django.views.generic import CreateView, UpdateView

from .models import Article, Plan, Subscription
from .decorators import require_access
from .payments import create_checkout_session
from .forms import ArticleForm, ArticleEditorForm


# ---------- Public pages ----------

def home(request):
    free = Article.objects.filter(published=True, access_level="free").order_by("-created_at")[:6]
    pro_teasers = Article.objects.filter(published=True).exclude(access_level="free").order_by("-created_at")[:3]
    return render(request, "home.html", {"free": free, "pro_teasers": pro_teasers})

def blog_list(request):
    qs = Article.objects.filter(published=True, access_level="free").order_by("-created_at")
    return render(request, "blog_list.html", {"articles": qs})

@require_access(lambda slug: Article.objects.get(slug=slug))
def article_detail(request, slug):
    article = get_object_or_404(Article, slug=slug, published=True)
    return render(request, "article_detail.html", {"article": article})

def premium_list(request):
    qs = Article.objects.filter(published=True).exclude(access_level="free").order_by("-created_at")
    return render(request, "premium_list.html", {"articles": qs})

def pricing(request):
    plans = Plan.objects.all().order_by("price_usd_month")
    return render(request, "pricing.html", {"plans": plans})


# ---------- Checkout ----------

@login_required
def buy(request, plan_code):
    plan = get_object_or_404(Plan, code=plan_code)
    return create_checkout_session(request, plan.stripe_price_id)

def checkout_success(request):
    return render(request, "checkout_success.html")

def checkout_cancel(request):
    return render(request, "checkout_cancel.html")


# ---------- Auth: signup + dashboard ----------

def signup(request):
    if request.user.is_authenticated:
        return redirect("dashboard")
    form = UserCreationForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Account created. Please log in.")
        return redirect("login")
    return render(request, "signup.html", {"form": form})



# ---------- SEO helpers ----------

def robots_txt(request):
    sitemap_url = request.build_absolute_uri(reverse("sitemap"))
    content = f"User-agent: *\nAllow: /\nSitemap: {sitemap_url}\n"
    return HttpResponse(content, content_type="text/plain")
@login_required
def dashboard(request):
    sub = Subscription.objects.filter(user=request.user).first()
    is_premium = bool(sub and sub.is_active())
    tier = "Premium" if is_premium else "Free"
    expires = sub.current_period_end if (sub and sub.current_period_end) else None
    recent = Article.objects.filter(published=True).order_by("-created_at")[:6]
    return render(request, "account/dashboard.html", {
        "tier": tier, "expires": expires, "now": now(), "recent": recent
    })


# ---------- In-browser authoring (only staff can publish) ----------

@login_required
def my_articles(request):
    qs = Article.objects.filter(author=request.user).order_by("-created_at")

    # Filters
    q = request.GET.get("q")
    if q:
        qs = qs.filter(title__icontains=q)

    status = request.GET.get("status")
    if status == "published":
        qs = qs.filter(published=True)
    elif status == "draft":
        qs = qs.filter(published=False)

    # Pagination
    paginator = Paginator(qs, 10)
    page_obj = paginator.get_page(request.GET.get("page"))

    return render(request, "editor/my_articles.html", {"page_obj": page_obj})


class ArticleCreatePublicView(LoginRequiredMixin, CreateView):
    model = Article
    template_name = "editor/article_form.html"
    success_url = reverse_lazy("my_articles")

    def get_form_class(self):
        # Staff/admin see 'published' field; normal users do not
        return ArticleEditorForm if self.request.user.is_staff else ArticleForm

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        # AttachmentFormSet removed
        return ctx

    def form_valid(self, form):
        obj = form.save(commit=False)
        obj.author = self.request.user
        # Non-staff cannot publish
        if not self.request.user.is_staff:
            obj.published = False
        obj.save()

    # AttachmentFormSet removed
        messages.success(self.request, "Article enregistré.")
        return super().form_valid(form)


class ArticleUpdatePublicView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Article
    slug_field = "slug"
    slug_url_kwarg = "slug"
    template_name = "editor/article_form.html"
    success_url = reverse_lazy("my_articles")

    def get_form_class(self):
        return ArticleEditorForm if self.request.user.is_staff else ArticleForm

    def test_func(self):
        obj = self.get_object()
        # Authors can edit their own; staff can edit all
        return (obj.author_id == self.request.user.id) or self.request.user.is_staff

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        # AttachmentFormSet removed
        return ctx

    def form_valid(self, form):
        if not self.request.user.is_staff:
            form.instance.published = False
        response = super().form_valid(form)

    # AttachmentFormSet removed
        messages.success(self.request, "Article mis à jour.")
        return response


@login_required
def article_delete_public(request, slug):
    article = get_object_or_404(Article, slug=slug)
    if not (request.user.is_staff or article.author_id == request.user.id):
        return HttpResponseForbidden("You cannot delete this article.")
    if request.method == "POST":
        title = article.title
        article.delete()
        messages.success(request, f"Deleted “{title}”.")
    return redirect("my_articles")


# Optional: quick publish endpoint for staff
@login_required
def article_publish(request, slug):
    if not request.user.is_staff:
        return HttpResponseForbidden("Only staff can publish.")
    article = get_object_or_404(Article, slug=slug)
    if request.method == "POST":
        article.published = True
        article.save(update_fields=["published"])
        messages.success(request, f'Published “{article.title}”.')
    return redirect("my_articles")
