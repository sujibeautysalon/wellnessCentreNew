from django.urls import path, include
from rest_framework.routers import DefaultRouter

from apps.inventory.views import (
    ProductCategoryViewSet, ProductViewSet, InventoryViewSet,
    InventoryTransactionViewSet, VendorViewSet, VendorProductViewSet,
    PurchaseOrderViewSet, PurchaseOrderItemViewSet
)

router = DefaultRouter()
router.register('categories', ProductCategoryViewSet, basename='product-category')
router.register('products', ProductViewSet, basename='product')
router.register('inventory', InventoryViewSet, basename='inventory')
router.register('transactions', InventoryTransactionViewSet, basename='inventory-transaction')
router.register('vendors', VendorViewSet, basename='vendor')
router.register('vendor-products', VendorProductViewSet, basename='vendor-product')
router.register('purchase-orders', PurchaseOrderViewSet, basename='purchase-order')
router.register('purchase-order-items', PurchaseOrderItemViewSet, basename='purchase-order-item')

urlpatterns = [
    path('', include(router.urls)),
]