from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()

router.register('/payments', views.PaymentLogViewSet, basename='payments')
router.register('/verify-payment', views.PaymentLogViewSet, basename='verify-payments')
router.register('/transactions', views.PaymentLogViewSet, basename='transactions')
router.register('/wallet', views.PaymentLogViewSet, basename='wallet')

urlpatterns = router.urls
