from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from apps.inventory.models import (
    ProductCategory, Product, Inventory, InventoryTransaction,
    Vendor, VendorProduct, PurchaseOrder, PurchaseOrderItem
)


class ProductCategoryAdmin(admin.ModelAdmin):
    """Admin interface for product categories."""
    list_display = ['name', 'parent', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'description']
    prepopulated_fields = {'name': ('name',)}
    readonly_fields = ['created_at', 'updated_at']


class InventoryInline(admin.TabularInline):
    """Inline admin for inventory levels across branches."""
    model = Inventory
    extra = 0
    readonly_fields = ['last_updated_at']


class ProductAdmin(admin.ModelAdmin):
    """Admin interface for products."""
    list_display = ['name', 'sku', 'category', 'product_type', 'cost_price', 
                   'retail_price', 'track_inventory', 'is_active']
    list_filter = ['category', 'product_type', 'is_active', 'track_inventory', 'created_at']
    search_fields = ['name', 'description', 'sku', 'barcode']
    readonly_fields = ['created_at', 'updated_at', 'created_by']
    inlines = [InventoryInline]
    fieldsets = [
        (_('Basic Information'), {
            'fields': ['name', 'description', 'category', 'product_type', 'is_active']
        }),
        (_('Identification'), {
            'fields': ['sku', 'barcode']
        }),
        (_('Pricing'), {
            'fields': ['cost_price', 'retail_price', 'sale_price', 'is_taxable', 'tax_rate']
        }),
        (_('Inventory'), {
            'fields': ['track_inventory', 'minimum_stock', 'unit_of_measure']
        }),
        (_('Display'), {
            'fields': ['image', 'featured']
        }),
        (_('Metadata'), {
            'fields': ['created_at', 'updated_at', 'created_by'],
            'classes': ['collapse']
        }),
    ]

    def save_model(self, request, obj, form, change):
        """Set the created_by field when creating a new product."""
        if not change:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)


class InventoryAdmin(admin.ModelAdmin):
    """Admin interface for inventory levels."""
    list_display = ['product', 'branch', 'quantity_in_stock', 'quantity_reserved', 'shelf_location', 'last_counted_at']
    list_filter = ['branch', 'last_counted_at']
    search_fields = ['product__name', 'product__sku', 'branch__name']
    readonly_fields = ['last_updated_at']
    raw_id_fields = ['product', 'branch']


class InventoryTransactionAdmin(admin.ModelAdmin):
    """Admin interface for inventory transactions."""
    list_display = ['get_product_name', 'get_branch_name', 'transaction_type', 'quantity', 'created_at']
    list_filter = ['transaction_type', 'created_at']
    search_fields = ['inventory__product__name', 'reference_number', 'notes']
    readonly_fields = ['created_at', 'created_by']
    raw_id_fields = ['inventory', 'source_branch', 'destination_branch']

    def get_product_name(self, obj):
        """Get the product name for the transaction."""
        return obj.inventory.product.name
    get_product_name.short_description = _('Product')
    get_product_name.admin_order_field = 'inventory__product__name'

    def get_branch_name(self, obj):
        """Get the branch name for the transaction."""
        return obj.inventory.branch.name
    get_branch_name.short_description = _('Branch')
    get_branch_name.admin_order_field = 'inventory__branch__name'


class VendorProductInline(admin.TabularInline):
    """Inline admin for vendor products."""
    model = VendorProduct
    extra = 0
    readonly_fields = ['last_ordered_at']


class VendorAdmin(admin.ModelAdmin):
    """Admin interface for vendors."""
    list_display = ['name', 'contact_name', 'email', 'phone', 'rating', 'is_active']
    list_filter = ['is_active', 'rating', 'created_at']
    search_fields = ['name', 'contact_name', 'email', 'phone']
    readonly_fields = ['created_at', 'updated_at']
    inlines = [VendorProductInline]
    fieldsets = [
        (_('Basic Information'), {
            'fields': ['name', 'contact_name', 'is_active']
        }),
        (_('Contact Details'), {
            'fields': ['email', 'phone', 'address', 'website']
        }),
        (_('Terms & Rating'), {
            'fields': ['payment_terms', 'delivery_terms', 'rating']
        }),
        (_('Notes'), {
            'fields': ['notes']
        }),
        (_('Metadata'), {
            'fields': ['created_at', 'updated_at'],
            'classes': ['collapse']
        }),
    ]


class VendorProductAdmin(admin.ModelAdmin):
    """Admin interface for vendor products."""
    list_display = ['product', 'vendor', 'vendor_price', 'minimum_order_quantity', 'lead_time_days', 'is_preferred_vendor']
    list_filter = ['is_preferred_vendor', 'vendor']
    search_fields = ['product__name', 'vendor__name', 'vendor_product_code', 'vendor_product_name']
    readonly_fields = ['last_ordered_at', 'created_at', 'updated_at']
    raw_id_fields = ['product', 'vendor']


class PurchaseOrderItemInline(admin.TabularInline):
    """Inline admin for purchase order items."""
    model = PurchaseOrderItem
    extra = 1
    raw_id_fields = ['product']


class PurchaseOrderAdmin(admin.ModelAdmin):
    """Admin interface for purchase orders."""
    list_display = ['order_number', 'vendor', 'branch', 'status', 'order_date', 'expected_delivery_date', 'total']
    list_filter = ['status', 'order_date', 'vendor', 'branch']
    search_fields = ['order_number', 'vendor__name', 'notes']
    readonly_fields = ['subtotal', 'total', 'created_at', 'updated_at', 'created_by']
    raw_id_fields = ['vendor', 'branch']
    inlines = [PurchaseOrderItemInline]
    fieldsets = [
        (_('Basic Information'), {
            'fields': ['order_number', 'vendor', 'branch', 'status', 'order_date']
        }),
        (_('Delivery Information'), {
            'fields': ['expected_delivery_date', 'delivery_date', 'shipping_address', 'tracking_number']
        }),
        (_('Financial Information'), {
            'fields': ['subtotal', 'tax', 'shipping_cost', 'total']
        }),
        (_('Additional Information'), {
            'fields': ['notes']
        }),
        (_('Metadata'), {
            'fields': ['created_at', 'updated_at', 'created_by'],
            'classes': ['collapse']
        }),
    ]

    def save_model(self, request, obj, form, change):
        """Set the created_by field when creating a new purchase order."""
        if not change:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)


class PurchaseOrderItemAdmin(admin.ModelAdmin):
    """Admin interface for purchase order items."""
    list_display = ['purchase_order', 'product', 'quantity_ordered', 'quantity_received', 'unit_price', 'total']
    list_filter = ['purchase_order']
    search_fields = ['product__name', 'notes']
    raw_id_fields = ['purchase_order', 'product']


# Register models with custom admin classes
admin.site.register(ProductCategory, ProductCategoryAdmin)
admin.site.register(Product, ProductAdmin)
admin.site.register(Inventory, InventoryAdmin)
admin.site.register(InventoryTransaction, InventoryTransactionAdmin)
admin.site.register(Vendor, VendorAdmin)
admin.site.register(VendorProduct, VendorProductAdmin)
admin.site.register(PurchaseOrder, PurchaseOrderAdmin)
admin.site.register(PurchaseOrderItem, PurchaseOrderItemAdmin)