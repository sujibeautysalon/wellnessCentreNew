from rest_framework import serializers
from apps.inventory.models import (
    ProductCategory, Product, Inventory, InventoryTransaction,
    Vendor, VendorProduct, PurchaseOrder, PurchaseOrderItem
)
from apps.clinic.serializers import BranchSerializer


class ProductCategorySerializer(serializers.ModelSerializer):
    """Serializer for product categories."""

    subcategory_count = serializers.IntegerField(read_only=True, required=False)
    product_count = serializers.IntegerField(read_only=True, required=False)
    parent_name = serializers.SerializerMethodField()
    
    class Meta:
        model = ProductCategory
        fields = [
            'id', 'name', 'description', 'parent', 'parent_name', 'is_active',
            'subcategory_count', 'product_count', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']
    
    def get_parent_name(self, obj):
        """Get the parent category name if it exists."""
        if obj.parent:
            return obj.parent.name
        return None


class ProductSerializer(serializers.ModelSerializer):
    """Serializer for products."""
    
    category_name = serializers.CharField(source='category.name', read_only=True)
    product_type_display = serializers.CharField(
        source='get_product_type_display', read_only=True)
    total_quantity = serializers.IntegerField(read_only=True, required=False)
    
    class Meta:
        model = Product
        fields = [
            'id', 'name', 'description', 'category', 'category_name',
            'product_type', 'product_type_display', 'sku', 'barcode',
            'cost_price', 'retail_price', 'sale_price', 'is_taxable',
            'tax_rate', 'track_inventory', 'minimum_stock', 'unit_of_measure',
            'is_active', 'image', 'featured', 'total_quantity',
            'created_at', 'updated_at', 'created_by'
        ]
        read_only_fields = ['created_at', 'updated_at', 'created_by']


class ProductDetailSerializer(ProductSerializer):
    """Extended serializer for product details."""
    
    inventories = serializers.SerializerMethodField()
    vendors = serializers.SerializerMethodField()
    
    class Meta(ProductSerializer.Meta):
        fields = ProductSerializer.Meta.fields + ['inventories', 'vendors']
    
    def get_inventories(self, obj):
        """Get inventory levels across branches."""
        inventories = obj.inventories.all()
        return InventorySerializer(inventories, many=True).data
    
    def get_vendors(self, obj):
        """Get vendor information for this product."""
        vendor_products = obj.vendors.all()
        return VendorProductSerializer(vendor_products, many=True).data


class InventorySerializer(serializers.ModelSerializer):
    """Serializer for inventory records."""
    
    product_name = serializers.CharField(source='product.name', read_only=True)
    product_sku = serializers.CharField(source='product.sku', read_only=True)
    branch_name = serializers.CharField(source='branch.name', read_only=True)
    available_quantity = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = Inventory
        fields = [
            'id', 'product', 'product_name', 'product_sku', 
            'branch', 'branch_name', 'quantity_in_stock', 'quantity_reserved',
            'available_quantity', 'shelf_location', 'last_counted_at', 'last_updated_at'
        ]
        read_only_fields = ['last_updated_at']


class InventoryTransactionSerializer(serializers.ModelSerializer):
    """Serializer for inventory transactions."""
    
    product_name = serializers.SerializerMethodField()
    branch_name = serializers.SerializerMethodField()
    transaction_type_display = serializers.CharField(
        source='get_transaction_type_display', read_only=True)
    created_by_name = serializers.SerializerMethodField()
    
    class Meta:
        model = InventoryTransaction
        fields = [
            'id', 'inventory', 'product_name', 'branch_name',
            'transaction_type', 'transaction_type_display', 'quantity',
            'source_branch', 'destination_branch', 'reference_number',
            'notes', 'created_at', 'created_by', 'created_by_name'
        ]
        read_only_fields = ['created_at', 'created_by']
    
    def get_product_name(self, obj):
        """Get the product name associated with this transaction."""
        return obj.inventory.product.name
    
    def get_branch_name(self, obj):
        """Get the branch name associated with this transaction."""
        return obj.inventory.branch.name
    
    def get_created_by_name(self, obj):
        """Get the name of the user who created the transaction."""
        if obj.created_by:
            if obj.created_by.first_name:
                return f"{obj.created_by.first_name} {obj.created_by.last_name}"
            return obj.created_by.email
        return None


class VendorSerializer(serializers.ModelSerializer):
    """Serializer for vendors."""
    
    product_count = serializers.IntegerField(read_only=True, required=False)
    
    class Meta:
        model = Vendor
        fields = [
            'id', 'name', 'contact_name', 'email', 'phone', 'address',
            'website', 'rating', 'is_active', 'payment_terms', 'delivery_terms',
            'notes', 'product_count', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']


class VendorDetailSerializer(VendorSerializer):
    """Extended serializer for vendor details."""
    
    products = serializers.SerializerMethodField()
    purchase_orders = serializers.SerializerMethodField()
    
    class Meta(VendorSerializer.Meta):
        fields = VendorSerializer.Meta.fields + ['products', 'purchase_orders']
    
    def get_products(self, obj):
        """Get products associated with this vendor."""
        vendor_products = obj.products.all()
        return VendorProductSerializer(vendor_products, many=True).data
    
    def get_purchase_orders(self, obj):
        """Get recent purchase orders for this vendor."""
        # Only get the 5 most recent purchase orders
        purchase_orders = obj.purchase_orders.all().order_by('-order_date')[:5]
        return PurchaseOrderListSerializer(purchase_orders, many=True).data


class VendorProductSerializer(serializers.ModelSerializer):
    """Serializer for vendor-specific product information."""
    
    product_name = serializers.CharField(source='product.name', read_only=True)
    product_sku = serializers.CharField(source='product.sku', read_only=True)
    vendor_name = serializers.CharField(source='vendor.name', read_only=True)
    
    class Meta:
        model = VendorProduct
        fields = [
            'id', 'vendor', 'vendor_name', 'product', 'product_name', 'product_sku',
            'vendor_product_code', 'vendor_product_name', 'vendor_price',
            'minimum_order_quantity', 'lead_time_days', 'is_preferred_vendor',
            'last_ordered_at', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']


class PurchaseOrderItemSerializer(serializers.ModelSerializer):
    """Serializer for purchase order items."""
    
    product_name = serializers.CharField(source='product.name', read_only=True)
    product_sku = serializers.CharField(source='product.sku', read_only=True)
    total = serializers.DecimalField(read_only=True, max_digits=10, decimal_places=2)
    received_status = serializers.CharField(read_only=True)
    
    class Meta:
        model = PurchaseOrderItem
        fields = [
            'id', 'purchase_order', 'product', 'product_name', 'product_sku',
            'quantity_ordered', 'quantity_received', 'unit_price', 'tax_rate',
            'notes', 'total', 'received_status'
        ]


class PurchaseOrderSerializer(serializers.ModelSerializer):
    """Serializer for purchase orders."""
    
    vendor_name = serializers.CharField(source='vendor.name', read_only=True)
    branch_name = serializers.CharField(source='branch.name', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    items_count = serializers.IntegerField(read_only=True, required=False)
    created_by_name = serializers.SerializerMethodField()
    
    class Meta:
        model = PurchaseOrder
        fields = [
            'id', 'vendor', 'vendor_name', 'branch', 'branch_name',
            'order_number', 'status', 'status_display', 'order_date',
            'expected_delivery_date', 'delivery_date', 'subtotal', 'tax',
            'shipping_cost', 'total', 'notes', 'shipping_address',
            'tracking_number', 'items_count', 'created_at', 'updated_at',
            'created_by', 'created_by_name'
        ]
        read_only_fields = ['subtotal', 'total', 'created_at', 'updated_at', 'created_by']
    
    def get_created_by_name(self, obj):
        """Get the name of the user who created the purchase order."""
        if obj.created_by:
            if obj.created_by.first_name:
                return f"{obj.created_by.first_name} {obj.created_by.last_name}"
            return obj.created_by.email
        return None


class PurchaseOrderDetailSerializer(PurchaseOrderSerializer):
    """Extended serializer for purchase order details with items."""
    
    items = PurchaseOrderItemSerializer(many=True, read_only=True)
    
    class Meta(PurchaseOrderSerializer.Meta):
        fields = PurchaseOrderSerializer.Meta.fields + ['items']


class PurchaseOrderListSerializer(serializers.ModelSerializer):
    """Simplified serializer for purchase order listings."""
    
    vendor_name = serializers.CharField(source='vendor.name', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = PurchaseOrder
        fields = [
            'id', 'order_number', 'vendor_name', 'status', 'status_display',
            'order_date', 'expected_delivery_date', 'total'
        ]