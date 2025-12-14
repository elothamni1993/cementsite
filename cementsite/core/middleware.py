from django.utils.deprecation import MiddlewareMixin
from django.utils import timezone
from .models import Visit
import re
from urllib.parse import urlparse


class VisitorTrackingMiddleware(MiddlewareMixin):
    def process_request(self, request):
        # Skip tracking for authenticated users
        if request.user.is_authenticated:
            return
        
        try:
            # Get basic info
            ip = request.META.get("HTTP_X_FORWARDED_FOR", "").split(",")[0].strip() or request.META.get("REMOTE_ADDR")
            ua = request.META.get("HTTP_USER_AGENT", "")
            referer = request.META.get("HTTP_REFERER", "")
            path = request.path
            
            # Get or create session key
            if not request.session.session_key:
                request.session.create()
            session_key = request.session.session_key
            
            # Check if returning visitor (has previous visits with this session)
            is_returning = Visit.objects.filter(session_key=session_key).exists()
            
            # Calculate time spent on previous page
            time_spent = 0
            if 'last_visit_time' in request.session:
                time_spent = int((timezone.now() - timezone.datetime.fromisoformat(request.session['last_visit_time'])).total_seconds())
                # Cap at 30 minutes to avoid overnight sessions
                time_spent = min(time_spent, 1800)
            
            # Detect if clicking on premium content
            clicked_premium = '/premium/' in path or 'access_level' in path.lower()
            
            # Parse traffic source from referer
            traffic_source = self._parse_traffic_source(referer, request.get_host())
            
            # Create visit record
            Visit.objects.create(
                path=path,
                ip=ip,
                user_agent=ua[:512],
                referer=referer[:512],
                user=None,
                session_key=session_key,
                is_returning=is_returning,
                time_spent=time_spent,
                clicked_premium=clicked_premium,
                traffic_source=traffic_source,
            )
            
            # Store current time for next request
            request.session['last_visit_time'] = timezone.now().isoformat()
            
        except Exception:
            # Never break the request flow due to tracking
            pass
    
    def _parse_traffic_source(self, referer, current_host):
        """Parse traffic source from referer URL"""
        if not referer:
            return "direct"
        
        try:
            parsed = urlparse(referer)
            domain = parsed.netloc.lower()
            
            # Same site = internal navigation
            if current_host in domain:
                return "internal"
            
            # Search engines
            if any(x in domain for x in ['google', 'bing', 'yahoo', 'duckduckgo', 'baidu']):
                return "search"
            
            # Social media
            if any(x in domain for x in ['facebook', 'fb.com', 'twitter', 't.co', 'linkedin', 'instagram', 'tiktok', 'reddit']):
                return "social"
            
            # Extract main domain
            parts = domain.split('.')
            if len(parts) >= 2:
                return parts[-2]  # e.g., "example" from "www.example.com"
            
            return domain[:50]
        except Exception:
            return "unknown"