from django.db import models
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from apps.clinic.models import Branch


class ProductCategory(models.Model):
    """Model for organizing products into categories."""
    
    name = models.CharField(_('name'), max_length=100)
    description = models.TextField(_('description'), blank=True)
    is_active = models.BooleanField(_('is active'), default=True)
    
    # For category hierarchy
    parent = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True,
                              related_name='subcategories')
    
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)
    
    class Meta:
        verbose_name = _('product category')
        verbose_name_plural = _('product categories')
        ordering = ['name']
    
    def __str__(self):
        return self.name


class Product(models.Model):
    """Model for products and services used in the wellness center."""
    
    PRODUCT_TYPES = [
        ('retail', 'Retail Product'),
        ('service_material', 'Service Material'),
        ('equipment', 'Equipment'),
        ('consumable', 'Consumable'),
    ]
    
    name = models.CharField(_('name'), max_length=255)
    description = models.TextField(_('description'), blank=True)
    category = models.ForeignKey(ProductCategory, on_delete=models.SET_NULL, 
                               null=True, blank=True, related_name='products')
    product_type = models.CharField(_('product type'), max_length=20, 
                                  choices=PRODUCT_TYPES, default='retail')
    sku = models.CharField(_('SKU'), max_length=50, unique=True)
    barcode = models.CharField(_('barcode'), max_length=100, blank=True, null=True)
    
    # Pricing info
    cost_price = models.DecimalField(_('cost price'), max_digits=10, decimal_places=2)
    retail_price = models.DecimalField(_('retail price'), max_digits=10, decimal_places=2)
    sale_price = models.DecimalField(_('sale price'), max_digits=10, decimal_places=2,
                                   null=True, blank=True)
    
    # Tax and accounting
    is_taxable = models.BooleanField(_('is taxable'), default=True)
    tax_rate = models.DecimalField(_('tax rate'), max_digits=5, decimal_places=2,
                                 default=0, help_text=_('Tax rate as a percentage'))
    
    # Inventory management
    track_inventory = models.BooleanField(_('track inventory'), default=True)
    minimum_stock = models.IntegerField(_('minimum stock'), default=0)
    
    # Units
    unit_of_measure = models.CharField(_('unit of measure'), max_length=50, 
                                     default='each')
    
    # Status
    is_active = models.BooleanField(_('is active'), default=True)
    
    # For the frontend display
    image = models.ImageField(_('image'), upload_to='products/', blank=True, null=True)
    featured = models.BooleanField(_('featured'), default=False)
    
    # Metadata
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
                                 null=True, related_name='+')
    
    class Meta:
        verbose_name = _('product')
        verbose_name_plural = _('products')
        ordering = ['name']
    
    def __str__(self):
        return self.name


class Inventory(models.Model):
    """Model for tracking product inventory at specific branches."""
    
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='inventories')
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE, related_name='inventories')
    
    # Stock levels
    quantity_in_stock = models.IntegerField(_('quantity in stock'), default=0)
    quantity_reserved = models.IntegerField(_('quantity reserved'), default=0)
    
    # Location within the branch
    shelf_location = models.CharField(_('shelf location'), max_length=100, blank=True, null=True)
    
    # Timestamps
    last_counted_at = models.DateTimeField(_('last counted at'), null=True, blank=True)
    last_updated_at = models.DateTimeField(_('last updated at'), auto_now=True)
    
    class Meta:
        verbose_name = _('inventory')
        verbose_name_plural = _('inventories')
        unique_together = ('product', 'branch')
    
    def __str__(self):
        return f"{self.product.name} at {self.branch.name}"
    
    @property
    def available_quantity(self):
        """Calculate available quantity by subtracting reserved from total stock."""
        return self.quantity_in_stock - self.quantity_reserved


class InventoryTransaction(models.Model):
    """Model for tracking inventory movements."""
    
    TRANSACTION_TYPES = [
        ('purchase', 'Purchase'),
        ('sale', 'Sale'),
        ('adjustment', 'Adjustment'),
        ('transfer', 'Transfer'),
        ('return', 'Return'),
        ('write_off', 'Write-off'),
    ]
    
    inventory = models.ForeignKey(Inventory, on_delete=models.CASCADE,
                                related_name='transactions')
    transaction_type = models.CharField(_('transaction type'), max_length=20,
                                      choices=TRANSACTION_TYPES)
    quantity = models.IntegerField(_('quantity'))
    
    # For transfers between branches
    source_branch = models.ForeignKey(Branch, on_delete=models.SET_NULL, 
                                    null=True, blank=True, related_name='+')
    destination_branch = models.ForeignKey(Branch, on_delete=models.SET_NULL,
                                         null=True, blank=True, related_name='+')
    
    # Reference information for traceability
    reference_number = models.CharField(_('reference number'), max_length=100,
                                      blank=True, null=True)
    notes = models.TextField(_('notes'), blank=True)
    
    # Timestamps and user
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
                                 null=True, related_name='+')
    
    class Meta:
        verbose_name = _('inventory transaction')
        verbose_name_plural = _('inventory transactions')
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.transaction_type}: {self.quantity} x {self.inventory.product.name}"


class Vendor(models.Model):
    """Model for product suppliers and vendors."""
    
    name = models.CharField(_('name'), max_length=255)
    contact_name = models.CharField(_('contact name'), max_length=255, blank=True, null=True)
    email = models.EmailField(_('email'), blank=True, null=True)
    phone = models.CharField(_('phone'), max_length=20, blank=True, null=True)
    address = models.TextField(_('address'), blank=True, null=True)
    website = models.URLField(_('website'), blank=True, null=True)
    
    # Vendor rating and status
    rating = models.IntegerField(_('rating'), default=0,
                               help_text=_('Rating from 0 to 5'))
    is_active = models.BooleanField(_('is active'), default=True)
    
    # Payment and delivery terms
    payment_terms = models.TextField(_('payment terms'), blank=True, null=True)
    delivery_terms = models.TextField(_('delivery terms'), blank=True, null=True)
    
    # Additional information
    notes = models.TextField(_('notes'), blank=True, null=True)
    
    # Timestamps
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)
    
    class Meta:
        verbose_name = _('vendor')
        verbose_name_plural = _('vendors')
        ordering = ['name']
    
    def __str__(self):
        return self.name


class VendorProduct(models.Model):
    """Model for tracking products supplied by specific vendors."""
    
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE, related_name='products')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='vendors')
    
    # Vendor specific details
    vendor_product_code = models.CharField(_('vendor product code'), max_length=100,
                                         blank=True, null=True)
    vendor_product_name = models.CharField(_('vendor product name'), max_length=255,
                                         blank=True, null=True)
    vendor_price = models.DecimalField(_('vendor price'), max_digits=10,
                                     decimal_places=2)
    
    # Ordering information
    minimum_order_quantity = models.IntegerField(_('minimum order quantity'), default=1)
    lead_time_days = models.IntegerField(_('lead time days'), default=1,
                                      help_text=_('Typical delivery time in days'))
    
    # Status
    is_preferred_vendor = models.BooleanField(_('is preferred vendor'), default=False)
    
    # Timestamps
    last_ordered_at = models.DateTimeField(_('last ordered at'), null=True, blank=True)
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)
    
    class Meta:
        verbose_name = _('vendor product')
        verbose_name_plural = _('vendor products')
        unique_together = ('vendor', 'product')
    
    def __str__(self):
        return f"{self.product.name} from {self.vendor.name}"


class PurchaseOrder(models.Model):
    """Model for tracking purchase orders to vendors."""
    
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('submitted', 'Submitted'),
        ('confirmed', 'Confirmed'),
        ('partial', 'Partially Received'),
        ('received', 'Received'),
        ('cancelled', 'Cancelled'),
    ]
    
    vendor = models.ForeignKey(Vendor, on_delete=models.PROTECT, related_name='purchase_orders')
    branch = models.ForeignKey(Branch, on_delete=models.PROTECT, related_name='purchase_orders')
    order_number = models.CharField(_('order number'), max_length=50, unique=True)
    status = models.CharField(_('status'), max_length=20, choices=STATUS_CHOICES, default='draft')
    
    # Dates
    order_date = models.DateField(_('order date'))
    expected_delivery_date = models.DateField(_('expected delivery date'), null=True, blank=True)
    delivery_date = models.DateField(_('delivery date'), null=True, blank=True)
    
    # Financial information
    subtotal = models.DecimalField(_('subtotal'), max_digits=10, decimal_places=2, default=0)
    tax = models.DecimalField(_('tax'), max_digits=10, decimal_places=2, default=0)
    shipping_cost = models.DecimalField(_('shipping cost'), max_digits=10, decimal_places=2, default=0)
    total = models.DecimalField(_('total'), max_digits=10, decimal_places=2, default=0)
    
    # Additional information
    notes = models.TextField(_('notes'), blank=True, null=True)
    
    # Shipping information
    shipping_address = models.TextField(_('shipping address'), blank=True, null=True)
    tracking_number = models.CharField(_('tracking number'), max_length=100, blank=True, null=True)
    
    # Timestamps and user
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
                                 null=True, related_name='+')
    
    class Meta:
        verbose_name = _('purchase order')
        verbose_name_plural = _('purchase orders')
        ordering = ['-order_date']
    
    def __str__(self):
        return f"PO-{self.order_number} ({self.vendor.name})"
    
    def save(self, *args, **kwargs):
        """Calculate totals before saving."""
        # Calculate only if items have been added (for new POs, items are added after initial save)
        if self.id:
            self.subtotal = sum(item.total for item in self.items.all())
            self.total = self.subtotal + self.tax + self.shipping_cost
        super().save(*args, **kwargs)


class PurchaseOrderItem(models.Model):
    """Model for items within a purchase order."""
    
    purchase_order = models.ForeignKey(PurchaseOrder, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.PROTECT, related_name='+')
    
    # Quantity and pricing
    quantity_ordered = models.IntegerField(_('quantity ordered'))
    quantity_received = models.IntegerField(_('quantity received'), default=0)
    unit_price = models.DecimalField(_('unit price'), max_digits=10, decimal_places=2)
    tax_rate = models.DecimalField(_('tax rate'), max_digits=5, decimal_places=2, default=0)
    
    # Additional information
    notes = models.TextField(_('notes'), blank=True, null=True)
    
    class Meta:
        verbose_name = _('purchase order item')
        verbose_name_plural = _('purchase order items')
    
    def __str__(self):
        return f"{self.quantity_ordered} x {self.product.name}"
    
    @property
    def total(self):
        """Calculate the total cost for this line item."""
        return self.quantity_ordered * self.unit_price
    
    @property
    def received_status(self):
        """Calculate the receiving status."""
        if self.quantity_received == 0:
            return 'pending'
        elif self.quantity_received < self.quantity_ordered:
            return 'partial'
        else:
            return 'complete'