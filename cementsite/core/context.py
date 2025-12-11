import os
from .models import Subscription
def adsense_keys(request):
    return {"ADSENSE_CLIENT": os.environ.get("ADSENSE_CLIENT", "")}

def stripe_keys(request):
    return {"STRIPE_PUBLIC_KEY": os.environ.get("STRIPE_PUBLIC_KEY", "")}




def user_tier(request):
    tier = "Guest"
    if request.user.is_authenticated:
        sub = Subscription.objects.filter(user=request.user).first()
        tier = "Premium" if (sub and sub.is_active()) else "Free"
    return {"USER_TIER": tier}
