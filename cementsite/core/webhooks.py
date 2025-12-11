import os, stripe, datetime
from django.http import HttpResponse, HttpResponseBadRequest
from django.utils import timezone
from .models import Subscription, Plan

stripe.api_key = os.environ.get("STRIPE_SECRET_KEY","")

def stripe_webhook(request):
    payload = request.body
    sig_header = request.META.get("HTTP_STRIPE_SIGNATURE")
    endpoint_secret = os.environ.get("STRIPE_WEBHOOK_SECRET","")
    try:
        event = stripe.Webhook.construct_event(payload, sig_header, endpoint_secret)
    except Exception:
        return HttpResponseBadRequest("Invalid payload/signature")

    if event["type"] in ("checkout.session.completed","invoice.paid","customer.subscription.updated","customer.subscription.created"):
        data = event["data"]["object"]
        if event["type"] == "checkout.session.completed":
            sub_id = data.get("subscription")
            cust_id = data.get("customer")
        elif event["type"] in ("invoice.paid","customer.subscription.updated","customer.subscription.created"):
            sub_id = data.get("id") if data.get("object") == "subscription" else data.get("subscription")
            cust_id = data.get("customer")
        else:
            sub_id, cust_id = None, None

        if sub_id:
            sub_obj = stripe.Subscription.retrieve(sub_id, expand=["plan","items.data.price"])
            price_id = sub_obj["items"]["data"][0]["price"]["id"]
            try:
                plan = Plan.objects.get(stripe_price_id=price_id)
            except Plan.DoesNotExist:
                plan = None

            # Try to map via customer email
            email = None
            try:
                cust = stripe.Customer.retrieve(cust_id)
                email = cust.get("email")
            except Exception:
                pass

            from django.contrib.auth import get_user_model
            User = get_user_model()
            user = User.objects.filter(email=email).first() if email else None
            if user:
                s, _ = Subscription.objects.get_or_create(user=user)
                s.plan = plan
                s.stripe_customer_id = cust_id or s.stripe_customer_id
                s.stripe_subscription_id = sub_id
                s.active = sub_obj["status"] in ("active","trialing")
                period_end = sub_obj["current_period_end"]
                s.current_period_end = timezone.make_aware(datetime.datetime.fromtimestamp(period_end))
                s.save()

    return HttpResponse(status=200)
