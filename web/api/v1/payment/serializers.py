from rest_framework import serializers


class CartData(serializers.Serializer):
    product_variant_id = serializers.IntegerField(min_value=1)
    quantity = serializers.IntegerField(min_value=1)
    unit_price = serializers.DecimalField(max_digits=8, decimal_places=2)
    price = serializers.DecimalField(max_digits=8, decimal_places=2)


class StripeIntentSerializer(serializers.Serializer):
    email = serializers.EmailField()
    phone_number = serializers.CharField()
    user_id = serializers.IntegerField(required=False)
    price_list = CartData(many=True)
    total_sum = serializers.DecimalField(max_digits=8, decimal_places=2)
    currency = serializers.CharField(max_length=3)
    notes = serializers.CharField()


class CreateCheckoutSessionSerializer(serializers.Serializer):
    product_variant_id = serializers.IntegerField(min_value=1)
    quantity = serializers.IntegerField(min_value=1)
