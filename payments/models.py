from django.db import models
from django.conf import settings

# Create your models here.

class UserWallet(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    currency = models.CharField(max_length=10, default='GHS')  # GHS for Ghana Cedis
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self) ->str:
        return str(f"{self.user}'s wallet")
    
    
class WalletTransaction(models.Model):
    TRANSACTION_TYPE = (
        ('CREDIT', 'Credit'),
        ('DEBIT', 'Debit'),
    )

    wallet = models.ForeignKey(UserWallet, on_delete=models.CASCADE, related_name='transactions')
    transaction_type = models.CharField(max_length=10, choices=TRANSACTION_TYPE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    reference = models.CharField(max_length=100, unique=True)  # e.g. Paystack ref
    created_at = models.DateTimeField(auto_now_add=True)
    description = models.TextField(blank=True)

    # def __str__(self):
    #     return f"{self.transaction_type} - {self.amount} ({self.reference})"

class PaymentLog(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    gateway = models.CharField(max_length=50)  # 'stripe' or 'paystack'
    reference = models.CharField(max_length=100, unique=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, default='pending')  # or 'success', 'failed'
    created_at = models.DateTimeField(auto_now_add=True)

