# views.py
import requests
from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet
from .models import UserWallet, WalletTransaction, PaymentLog
from .serializers import UserWalletSerializer, WalletTransactionSerializer, PaymentLogSerializer
from django.conf import settings
# pylint: disable=no-member

class UserWalletViewSet(ModelViewSet):
    serializer_class = UserWalletSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return UserWallet.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=False, methods=['GET'])
    def balance(self, request):
        wallet = UserWallet.objects.get(user=request.user)
        return Response({'balance': wallet.balance, 'currency': wallet.currency})

class WalletTransactionViewSet(ReadOnlyModelViewSet):
    serializer_class = WalletTransactionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return WalletTransaction.objects.filter(wallet__user=self.request.user)

class PaymentLogViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = PaymentLogSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return PaymentLog.objects.filter(user=self.request.user)

class PaystackPaymentViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=['post'], url_path='initialize')
    def initialize_payment(self, request):
        """
        Initialize Paystack payment
        """
        amount = request.data.get('amount')
        email = request.data.get('email')
        
        if not amount or not email:
            return Response(
                {'error': 'Amount and email are required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            # Convert amount to integer (kobo/pesewas)
            amount_in_kobo = int(float(amount) * 100)
        except (ValueError, TypeError):
            return Response(
                {'error': 'Invalid amount format'},
                status=status.HTTP_400_BAD_REQUEST
            )

        url = "https://api.paystack.co/transaction/initialize"
        headers = {
            "Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}",
            "Content-Type": "application/json",
        }
        payload = {
            "email": email,
            "amount": str(amount_in_kobo),
            "metadata": {
                "user_id": request.user.id,
                "custom_fields": [
                    {
                        "display_name": "User ID",
                        "variable_name": "user_id",
                        "value": request.user.id
                    }
                ]
            }
        }

        try:
            response = requests.post(url, headers=headers, json=payload)
            response.raise_for_status()
            data = response.json()
            
            # Create a pending payment log
            PaymentLog.objects.create(
                user=request.user,
                gateway='paystack',
                reference=data['data']['reference'],
                amount=amount,
                status='pending'
            )
            
            return Response(data)
        except requests.exceptions.RequestException as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=False, methods=['post'], url_path='verify')
    def verify_payment(self, request):
        """
        Verify Paystack payment
        """
        reference = request.data.get('reference')
        if not reference:
            return Response(
                {'error': 'Reference is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        url = f"https://api.paystack.co/transaction/verify/{reference}"
        headers = {
            "Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}",
        }

        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            data = response.json()

            if not data.get('status') or data['data']['status'] != 'success':
                PaymentLog.objects.filter(reference=reference).update(status='failed')
                return Response(
                    {'status': 'failed', 'message': 'Payment not successful'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            amount = data['data']['amount'] / 100  # Convert back from kobo/pesewas
            
            try:
                payment_log = PaymentLog.objects.get(reference=reference)
                payment_log.status = 'success'
                payment_log.amount = amount
                payment_log.save()

                # Credit user's wallet
                wallet, created = UserWallet.objects.get_or_create(user=request.user)
                wallet.balance += amount
                wallet.save()

                # Create wallet transaction
                WalletTransaction.objects.create(
                    wallet=wallet,
                    transaction_type='CREDIT',
                    amount=amount,
                    reference=reference,
                    description='Payment via Paystack'
                )

                return Response({
                    'status': 'success',
                    'message': 'Payment verified and wallet credited',
                    'amount': amount,
                    'reference': reference
                })

            except PaymentLog.DoesNotExist:
                return Response(
                    {'error': 'Payment reference not found'},
                    status=status.HTTP_404_NOT_FOUND
                )

        except requests.exceptions.RequestException as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=False, methods=['get'], url_path='history')
    def payment_history(self, request):
        """
        Get user's payment history
        """
        payments = PaymentLog.objects.filter(user=request.user).order_by('-created_at')
        serializer = PaymentLogSerializer(payments, many=True)
        return Response(serializer.data)