from django.urls import path
from . import views

urlpatterns = [
    path('create-payment-intent/', views.StripeIntentView.as_view(), name='create-payment-intent'),
    path('webhooks/stripe/', views.StripeWebhookView.as_view(), name='stripe-webhook'),
    path('create-checkout-session/<pk>/', views.CreateCheckoutSessionView.as_view(), name='create-checkout-session')
]
