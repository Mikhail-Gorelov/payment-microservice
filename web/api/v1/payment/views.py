from django.core.mail import send_mail
from django.views.decorators.csrf import csrf_exempt
from rest_framework.generics import GenericAPIView
import stripe
from django.conf import settings
from . import serializers
from rest_framework.response import Response

from .services import ProductsService

stripe.api_key = settings.STRIPE_SECRET_KEY


class StripeIntentView(GenericAPIView):
    serializer_class = serializers.StripeIntentSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        customer = stripe.Customer.create(**serializer.data)
        service = ProductsService(request=request, url=f"/api/v1/product-variant/{kwargs.get('pk')}/")
        response = service.service_response(method="get")
        product = response.data
        price = int(product.get('full_price') * 100)
        intent = stripe.PaymentIntent.create(
            amount=price,  # cents
            currency=product['currency'].lower(),
            customer=customer['id'],
            metadata={
                "product_id": product['id']
            }
        )
        return Response({'clientSecret': intent.get('client_secret')})


class CreateCheckoutSessionView(GenericAPIView):
    serializer_class = serializers.CreateCheckoutSessionSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        service = ProductsService(request=request, url=f"/api/v1/product-variant/{kwargs.get('pk')}/")
        response = service.service_response(method="get")
        product = response.data
        price = int(product.get('full_price') * 100)
        domain = settings.BASE_DOMAIN
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[
                {
                    'price_data': {
                        'currency': product['currency'].lower(),
                        'unit_amount': price,
                        'product_data': {
                            'name': product.get('name'),
                            # 'images': ['https://i.imgur.com/EHyR2nP.png'],
                        },
                    },
                    'quantity': serializer.data.get('quantity'),
                },
            ],
            metadata={
                "product_id": product.get('id'),
            },
            mode='payment',
            success_url=domain + '/success-payment/',
            cancel_url=domain + '/cancel-payment/',
        )
        return Response(
            {
                'id': checkout_session.id,
                'success_url': checkout_session.success_url,
                'url': checkout_session.url,
                'cancel_url': checkout_session.cancel_url,
            }
        )


@csrf_exempt
def stripe_webhook(request):
    payload = request.body
    sig_header = request.META['HTTP_STRIPE_SIGNATURE']
    event = None

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
    except ValueError as e:
        # Invalid payload
        return Response(status=400)
    except stripe.error.SignatureVerificationError as e:
        # Invalid signature
        return Response(status=400)

    # Handle the checkout.session.completed event
    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']

        customer_email = session["customer_details"]["email"]
        product_id = session["metadata"]["product_id"]

        service = ProductsService(request=request, url=f"/api/v1/product-variant/{product_id}/")
        response = service.service_response(method="get")
        product = response.data

        send_mail(
            subject="Here is your product",
            message=f"Thanks for your purchase. Here is the product you ordered. The name is {product.get('name')}",
            recipient_list=[customer_email],
            from_email="webshop.project@yandex.ru"
        )

        # TODO - decide whether you want to send the file or the URL

    elif event["type"] == "payment_intent.succeeded":
        intent = event['data']['object']

        stripe_customer_id = intent["customer"]
        stripe_customer = stripe.Customer.retrieve(stripe_customer_id)

        customer_email = stripe_customer['email']
        product_id = intent["metadata"]["product_id"]

        service = ProductsService(request=request, url=f"/api/v1/product-variant/{product_id}/")
        response = service.service_response(method="get")
        product = response.data

        send_mail(
            subject="Here is your product",
            message=f"Thanks for your purchase. Here is the product you ordered. The name is {product.get('name')}",
            recipient_list=[customer_email],
            from_email="webshop.project@yandex.ru"
        )

    return Response(status=200)