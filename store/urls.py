from rest_framework.routers import DefaultRouter
from rest_framework_nested.routers import NestedSimpleRouter
from . import views

router = DefaultRouter()
router.register('products', views.ProductViewSet)
router.register('collections', views.CollectionViewSet, basename='collections')
router.register('carts', views.CartViewSet, basename='carts')
router.register('customers', views.CustomerViewSet, basename='customers')
router.register('orders', views.OrderViewSet, basename='orders')


product_router = NestedSimpleRouter(router, 'products', lookup='product')
product_router.register('images', views.ProductImageViewSet, basename='product-images')

carts_router = NestedSimpleRouter(router, 'carts', lookup='cart')
carts_router.register('items', views.CartItemViewSet, basename='cart-items')

 
urlpatterns = router.urls + product_router.urls + carts_router.urls