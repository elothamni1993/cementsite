from django.shortcuts import redirect
from django.urls import reverse
from functools import wraps
from .models import Subscription, Article

def require_access(article_getter):
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped(request, *args, **kwargs):
            article = article_getter(*args, **kwargs)
            if not article.requires_subscription():
                return view_func(request, *args, **kwargs)

            if not request.user.is_authenticated:
                return redirect(f"{reverse('login')}?next={request.path}")

            sub = Subscription.objects.filter(user=request.user).first()
            if not sub or not sub.is_active():
                return redirect("pricing")

            if article.access_level == Article.PRO and (not sub.plan or sub.plan.code != "pro"):
                return redirect("pricing")

            return view_func(request, *args, **kwargs)
        return _wrapped
    return decorator
