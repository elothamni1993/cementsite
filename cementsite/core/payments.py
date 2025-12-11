import os
from django.shortcuts import redirect
from django.urls import reverse
import stripe

stripe.api_key = os.environ.get("STRIPE_SECRET_KEY","")

def create_checkout_session(request, price_id):
    site = os.environ.get("SITE_URL","http://127.0.0.1:8000")
    session = stripe.checkout.Session.create(
        mode="subscription",
        payment_method_types=["card"],
        line_items=[{"price": price_id, "quantity": 1}],
        success_url=f"{site}{reverse('checkout_success')}?session_id={{CHECKOUT_SESSION_ID}}",
        cancel_url=f"{site}{reverse('checkout_cancel')}",

        customer_email=request.user.email if request.user.is_authenticated else None,
    )
    return redirect(session.url, code=303)
