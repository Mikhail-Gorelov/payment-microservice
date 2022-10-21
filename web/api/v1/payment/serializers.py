from rest_framework import serializers


class StripeIntentSerializer(serializers.Serializer):
    email = serializers.EmailField()


class CreateCheckoutSessionSerializer(serializers.Serializer):
    quantity = serializers.IntegerField()
