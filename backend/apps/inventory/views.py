from django.db.models import Count, Sum, Q, F
from django.utils import timezone
from rest_framework import viewsets, permissions, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.core.permissions import IsAdminOrTherapist
from apps.inventory.models import (
    ProductCategory, Product, Inventory, InventoryTransaction,
    Vendor, VendorProduct, PurchaseOrder, PurchaseOrderItem
)
from apps.inventory.serializers import (
    ProductCategorySerializer, ProductSerializer, ProductDetailSerializer,
    InventorySerializer, InventoryTransactionSerializer,
    VendorSerializer, VendorDetailSerializer, VendorProductSerializer,
    PurchaseOrderSerializer, PurchaseOrderDetailSerializer, 
    PurchaseOrderItemSerializer
)


class ProductCategoryViewSet(viewsets.ModelViewSet):
    """
    ViewSet for product categories. Only admin and therapists can create/modify categories.
    """
    queryset = ProductCategory.objects.all()
    serializer_class = ProductCategorySerializer
    permission_classes = [IsAdminOrTherapist]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'created_at']
    ordering = ['name']

    def get_queryset(self):
        """
        Get categories with counts of subcategories and products.
        """
        queryset = ProductCategory.objects.annotate(
            subcategory_count=Count('subcategories', distinct=True),
            product_count=Count('products', distinct=True)
        )
        
        # Filter by active status if specified
        is_active = self.request.query_params.get('is_active')
        if is_active is not None:
            is_active = is_active.lower() == 'true'
            queryset = queryset.filter(is_active=is_active)
            
        # Filter by parent category if specified
        parent = self.request.query_params.get('parent')
        if parent:
            if parent.lower() == 'null':
                queryset = queryset.filter(parent__isnull=True)
            else:
                queryset = queryset.filter(parent_id=parent)
                
        return queryset


class ProductViewSet(viewsets.ModelViewSet):
    """
    ViewSet for products. Only admin and therapists can create/modify products.
    """
    queryset = Product.objects.all()
    permission_classes = [IsAdminOrTherapist]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description', 'sku', 'barcode']
    ordering_fields = ['name', 'created_at', 'retail_price']
    ordering = ['name']

    def get_serializer_class(self):
        """
        Return different serializers for list and detail views.
        """
        if self.action == 'retrieve':
            return ProductDetailSerializer
        return ProductSerializer

    def get_queryset(self):
        """
        Get products with total quantity aggregated from inventory.
        """
        queryset = Product.objects.annotate(
            total_quantity=Sum('inventories__quantity_in_stock', default=0)
        )
        
        # Filter by minimum stock if specified
        low_stock = self.request.query_params.get('low_stock')
        if low_stock is not None and low_stock.lower() == 'true':
            queryset = queryset.filter(
                Q(total_quantity__lt=F('minimum_stock')) & Q(track_inventory=True)
            )
            
        # Filter by category name
        category_name = self.request.query_params.get('category_name')
        if category_name:
            queryset = queryset.filter(category__name__icontains=category_name)
            
        # Filter by product type if specified
        product_type = self.request.query_params.get('product_type')
        if product_type:
            queryset = queryset.filter(product_type=product_type)
            
        # Filter by active status if specified
        is_active = self.request.query_params.get('is_active')
        if is_active is not None:
            is_active = is_active.lower() == 'true'
            queryset = queryset.filter(is_active=is_active)
            
        # Filter by featured status if specified
        featured = self.request.query_params.get('featured')
        if featured is not None:
            featured = featured.lower() == 'true'
            queryset = queryset.filter(featured=featured)
            
        return queryset
    
    def perform_create(self, serializer):
        """Set the created_by field to current user."""
        serializer.save(created_by=self.request.user)
    
    @action(detail=True, methods=['post'])
    def update_stock(self, request, pk=None):
        """
        Update product stock levels with an adjustment transaction.
        """
        product = self.get_object()
        branch_id = request.data.get('branch_id')
        quantity = request.data.get('quantity')
        notes = request.data.get('notes', '')
        
        if not branch_id or quantity is None:
            return Response({
                'error': 'branch_id and quantity are required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            # Get or create inventory record for this product/branch
            inventory, created = Inventory.objects.get_or_create(
                product=product,
                branch_id=branch_id,
                defaults={'quantity_in_stock': 0}
            )
            
            # Create a transaction for this adjustment
            transaction = InventoryTransaction.objects.create(
                inventory=inventory,
                transaction_type='adjustment',
                quantity=quantity,
                notes=notes,
                created_by=request.user
            )
            
            # Update inventory quantity
            inventory.quantity_in_stock += int(quantity)
            inventory.last_counted_at = timezone.now()
            inventory.save()
            
            return Response({
                'success': True,
                'inventory': InventorySerializer(inventory).data,
                'transaction': InventoryTransactionSerializer(transaction).data
            })
        except Exception as e:
            return Response({
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class InventoryViewSet(viewsets.ModelViewSet):
    """
    ViewSet for inventory records. Only admin and therapists can access.
    """
    queryset = Inventory.objects.all()
    serializer_class = InventorySerializer
    permission_classes = [IsAdminOrTherapist]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['product__name', 'product__sku', 'branch__name']
    ordering_fields = ['quantity_in_stock', 'last_updated_at']
    ordering = ['-quantity_in_stock']

    def get_queryset(self):
        """
        Add available_quantity to queryset.
        """
        queryset = Inventory.objects.all().select_related('product', 'branch')
        
        # Filter by low stock status
        low_stock = self.request.query_params.get('low_stock')
        if low_stock is not None and low_stock.lower() == 'true':
            queryset = queryset.filter(
                Q(quantity_in_stock__lt=F('product__minimum_stock')) & 
                Q(product__track_inventory=True)
            )
            
        # Filter by product name
        product_name = self.request.query_params.get('product_name')
        if product_name:
            queryset = queryset.filter(product__name__icontains=product_name)
            
        # Filter by branch if specified
        branch = self.request.query_params.get('branch')
        if branch:
            queryset = queryset.filter(branch_id=branch)
            
        # Filter by product category if specified
        category = self.request.query_params.get('product__category')
        if category:
            queryset = queryset.filter(product__category_id=category)
            
        return queryset
    
    @action(detail=True, methods=['post'])
    def count(self, request, pk=None):
        """
        Record a physical inventory count.
        """
        inventory = self.get_object()
        quantity = request.data.get('quantity')
        notes = request.data.get('notes', 'Physical inventory count')
        
        if quantity is None:
            return Response({
                'error': 'quantity is required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            quantity = int(quantity)
            difference = quantity - inventory.quantity_in_stock
            
            # Create a transaction for this count
            transaction = InventoryTransaction.objects.create(
                inventory=inventory,
                transaction_type='adjustment',
                quantity=difference,
                notes=notes,
                created_by=request.user
            )
            
            # Update inventory quantity
            inventory.quantity_in_stock = quantity
            inventory.last_counted_at = timezone.now()
            inventory.save()
            
            return Response({
                'success': True,
                'inventory': InventorySerializer(inventory).data,
                'transaction': InventoryTransactionSerializer(transaction).data
            })
        except Exception as e:
            return Response({
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class InventoryTransactionViewSet(viewsets.ModelViewSet):
    """
    ViewSet for inventory transactions. Only admin and therapists can access.
    """
    queryset = InventoryTransaction.objects.all()
    serializer_class = InventoryTransactionSerializer
    permission_classes = [IsAdminOrTherapist]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['inventory__product__name', 'reference_number', 'notes']
    ordering_fields = ['created_at']
    ordering = ['-created_at']
    
    def get_queryset(self):
        """
        Filter inventory transactions.
        """
        queryset = InventoryTransaction.objects.all()
        
        # Filter by transaction type if specified
        transaction_type = self.request.query_params.get('transaction_type')
        if transaction_type:
            queryset = queryset.filter(transaction_type=transaction_type)
            
        # Filter by inventory product if specified
        product = self.request.query_params.get('inventory__product')
        if product:
            queryset = queryset.filter(inventory__product_id=product)
            
        # Filter by inventory branch if specified
        branch = self.request.query_params.get('inventory__branch')
        if branch:
            queryset = queryset.filter(inventory__branch_id=branch)
            
        return queryset
    
    def perform_create(self, serializer):
        """Set the created_by field to current user."""
        serializer.save(created_by=self.request.user)


class VendorViewSet(viewsets.ModelViewSet):
    """
    ViewSet for vendors. Only admin and therapists can access.
    """
    queryset = Vendor.objects.all()
    permission_classes = [IsAdminOrTherapist]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'contact_name', 'email', 'phone']
    ordering_fields = ['name', 'rating', 'created_at']
    ordering = ['name']

    def get_serializer_class(self):
        """
        Return different serializers for list and detail views.
        """
        if self.action == 'retrieve':
            return VendorDetailSerializer
        return VendorSerializer

    def get_queryset(self):
        """
        Get vendors with product count.
        """
        queryset = Vendor.objects.annotate(
            product_count=Count('products', distinct=True)
        )
        
        # Filter by active status if specified
        is_active = self.request.query_params.get('is_active')
        if is_active is not None:
            is_active = is_active.lower() == 'true'
            queryset = queryset.filter(is_active=is_active)
            
        return queryset


class VendorProductViewSet(viewsets.ModelViewSet):
    """
    ViewSet for vendor products. Only admin and therapists can access.
    """
    queryset = VendorProduct.objects.all()
    serializer_class = VendorProductSerializer
    permission_classes = [IsAdminOrTherapist]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['product__name', 'vendor__name', 'vendor_product_code']
    ordering_fields = ['vendor_price', 'lead_time_days']
    ordering = ['vendor_price']
    
    def get_queryset(self):
        """
        Filter vendor products.
        """
        queryset = VendorProduct.objects.all()
        
        # Filter by vendor if specified
        vendor = self.request.query_params.get('vendor')
        if vendor:
            queryset = queryset.filter(vendor_id=vendor)
            
        # Filter by product if specified
        product = self.request.query_params.get('product')
        if product:
            queryset = queryset.filter(product_id=product)
            
        # Filter by preferred vendor status if specified
        is_preferred_vendor = self.request.query_params.get('is_preferred_vendor')
        if is_preferred_vendor is not None:
            is_preferred_vendor = is_preferred_vendor.lower() == 'true'
            queryset = queryset.filter(is_preferred_vendor=is_preferred_vendor)
            
        return queryset


class PurchaseOrderViewSet(viewsets.ModelViewSet):
    """
    ViewSet for purchase orders. Only admin and therapists can access.
    """
    queryset = PurchaseOrder.objects.all()
    permission_classes = [IsAdminOrTherapist]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['order_number', 'vendor__name', 'notes']
    ordering_fields = ['order_date', 'expected_delivery_date', 'total']
    ordering = ['-order_date']

    def get_serializer_class(self):
        """
        Return different serializers for list and detail views.
        """
        if self.action == 'retrieve' or self.action == 'create':
            return PurchaseOrderDetailSerializer
        return PurchaseOrderSerializer

    def get_queryset(self):
        """
        Get purchase orders with items count.
        """
        queryset = PurchaseOrder.objects.annotate(
            items_count=Count('items', distinct=True)
        )
        
        # Filter by vendor if specified
        vendor = self.request.query_params.get('vendor')
        if vendor:
            queryset = queryset.filter(vendor_id=vendor)
            
        # Filter by status if specified
        status_param = self.request.query_params.get('status')
        if status_param:
            queryset = queryset.filter(status=status_param)
            
        # Filter by branch if specified
        branch = self.request.query_params.get('branch')
        if branch:
            queryset = queryset.filter(branch_id=branch)
            
        return queryset
    
    def perform_create(self, serializer):
        """Set the created_by field to current user."""
        serializer.save(created_by=self.request.user)
    
    @action(detail=True, methods=['post'])
    def receive(self, request, pk=None):
        """
        Record receipt of purchase order items.
        """
        purchase_order = self.get_object()
        
        # Check if PO can be received
        if purchase_order.status not in ['submitted', 'confirmed', 'partial']:
            return Response({
                'error': 'Only submitted, confirmed, or partially received purchase orders can be received.'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Process receipt data
        receipt_data = request.data.get('items', [])
        if not receipt_data:
            return Response({
                'error': 'No items provided for receipt'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            processed_items = []
            fully_received = True
            
            for item_data in receipt_data:
                item_id = item_data.get('id')
                quantity_received = int(item_data.get('quantity_received', 0))
                
                # Skip if invalid data
                if not item_id or quantity_received <= 0:
                    continue
                
                try:
                    # Get the PO item
                    item = PurchaseOrderItem.objects.get(id=item_id, purchase_order=purchase_order)
                    
                    # Calculate the quantity to add (don't exceed ordered quantity)
                    quantity_to_add = min(quantity_received, item.quantity_ordered - item.quantity_received)
                    
                    if quantity_to_add <= 0:
                        continue
                    
                    # Update the item's received quantity
                    item.quantity_received += quantity_to_add
                    item.save()
                    
                    # Get or create inventory for this product at the PO's branch
                    inventory, created = Inventory.objects.get_or_create(
                        product=item.product,
                        branch=purchase_order.branch,
                        defaults={'quantity_in_stock': 0}
                    )
                    
                    # Create inventory transaction
                    transaction = InventoryTransaction.objects.create(
                        inventory=inventory,
                        transaction_type='purchase',
                        quantity=quantity_to_add,
                        reference_number=purchase_order.order_number,
                        notes=f"Received from PO #{purchase_order.order_number}",
                        created_by=request.user
                    )
                    
                    # Update inventory quantity
                    inventory.quantity_in_stock += quantity_to_add
                    inventory.save()
                    
                    processed_items.append({
                        'item_id': item.id,
                        'product_name': item.product.name,
                        'quantity_received': quantity_to_add,
                        'total_received': item.quantity_received
                    })
                    
                    # Check if all items are fully received
                    if item.quantity_received < item.quantity_ordered:
                        fully_received = False
                        
                except PurchaseOrderItem.DoesNotExist:
                    continue
            
            # Update purchase order status
            if fully_received:
                purchase_order.status = 'received'
                purchase_order.delivery_date = timezone.now().date()
            elif processed_items:
                purchase_order.status = 'partial'
            
            purchase_order.save()
            
            return Response({
                'success': True,
                'purchase_order_status': purchase_order.status,
                'processed_items': processed_items
            })
            
        except Exception as e:
            return Response({
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class PurchaseOrderItemViewSet(viewsets.ModelViewSet):
    """
    ViewSet for purchase order items. Only admin and therapists can access.
    """
    queryset = PurchaseOrderItem.objects.all()
    serializer_class = PurchaseOrderItemSerializer
    permission_classes = [IsAdminOrTherapist]
    filter_backends = [filters.SearchFilter]
    search_fields = ['product__name', 'notes']
    
    def get_queryset(self):
        """
        Filter purchase order items.
        """
        queryset = PurchaseOrderItem.objects.all()
        
        # Filter by purchase order if specified
        purchase_order = self.request.query_params.get('purchase_order')
        if purchase_order:
            queryset = queryset.filter(purchase_order_id=purchase_order)
            
        # Filter by product if specified
        product = self.request.query_params.get('product')
        if product:
            queryset = queryset.filter(product_id=product)
            
        return queryset