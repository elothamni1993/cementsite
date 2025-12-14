from django.utils.deprecation import MiddlewareMixin
from .models import Visit


class VisitorTrackingMiddleware(MiddlewareMixin):
    def process_request(self, request):
        try:
            ip = request.META.get("HTTP_X_FORWARDED_FOR", "").split(",")[0].strip() or request.META.get("REMOTE_ADDR")
            ua = request.META.get("HTTP_USER_AGENT", "")
            referer = request.META.get("HTTP_REFERER", "")
            Visit.objects.create(
                path=request.path,
                ip=ip,
                user_agent=ua[:512],
                referer=referer[:512],
                user=request.user if request.user.is_authenticated else None,
            )
        except Exception:
            # Never break the request flow due to tracking
            pass