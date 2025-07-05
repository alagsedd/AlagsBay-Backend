from rest_framework import serializers
from .models import UserWallet, WalletTransaction, PaymentLog


class UserWalletSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserWallet
        fields = ['id', 'user', 'balance', 'currency', 'created_at']
        read_only_fields = ['id', 'user', 'balance', 'created_at']


class WalletTransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = WalletTransaction
        fields = '__all__'
        read_only_fields = ['id', 'wallet', 'created_at']


class PaymentLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentLog
        fields = '__all__'
        read_only_fields = ['id', 'user', 'created_at']
