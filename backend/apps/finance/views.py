# filepath: c:\Users\cadsa\OneDrive\Personal\Full stack web development\wellnessCentre\backend\apps\finance\views.py
from rest_framework import viewsets, permissions, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Sum, Q
from django.utils import timezone
from datetime import timedelta

from apps.finance.models import (
    BudgetCategory, Expense, FinancialAccount, 
    Transaction, Budget, TaxRate, FinancialReport
)
from apps.finance.serializers import (
    BudgetCategorySerializer, ExpenseSerializer, FinancialAccountSerializer,
    TransactionSerializer, BudgetSerializer, TaxRateSerializer, FinancialReportSerializer
)
from apps.core.permissions import IsAdminUser, IsTherapistUser, IsOwnerOrReadOnly


class BudgetCategoryViewSet(viewsets.ModelViewSet):
    """ViewSet for BudgetCategory model."""
    
    queryset = BudgetCategory.objects.all()
    serializer_class = BudgetCategorySerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminUser]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category_type', 'is_active']
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'created_at']
    

class ExpenseViewSet(viewsets.ModelViewSet):
    """ViewSet for Expense model."""
    
    queryset = Expense.objects.all()
    serializer_class = ExpenseSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminUser]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['branch', 'category', 'status', 'recurring', 'date']
    search_fields = ['description', 'vendor_name', 'reference_number']
    ordering_fields = ['date', 'total_amount', 'created_at']
    
    def perform_create(self, serializer):
        """Set the created_by field to the current user."""
        serializer.save(created_by=self.request.user)
    
    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        """Approve an expense."""
        expense = self.get_object()
        
        if expense.status != 'pending':
            return Response(
                {"detail": "Only pending expenses can be approved."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        expense.status = 'approved'
        expense.approved_by = request.user
        expense.save()
        
        return Response(
            {"detail": "Expense approved successfully."},
            status=status.HTTP_200_OK
        )
    
    @action(detail=True, methods=['post'])
    def reject(self, request, pk=None):
        """Reject an expense."""
        expense = self.get_object()
        
        if expense.status != 'pending':
            return Response(
                {"detail": "Only pending expenses can be rejected."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        expense.status = 'rejected'
        expense.approved_by = request.user
        expense.save()
        
        return Response(
            {"detail": "Expense rejected successfully."},
            status=status.HTTP_200_OK
        )


class FinancialAccountViewSet(viewsets.ModelViewSet):
    """ViewSet for FinancialAccount model."""
    
    queryset = FinancialAccount.objects.all()
    serializer_class = FinancialAccountSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminUser]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['account_type', 'branch', 'is_active']
    search_fields = ['name', 'account_number', 'description']
    ordering_fields = ['name', 'current_balance', 'created_at']
    
    @action(detail=True, methods=['get'])
    def transactions(self, request, pk=None):
        """Get all transactions for an account."""
        account = self.get_object()
        transactions = Transaction.objects.filter(account=account)
        
        # Apply filters from query params
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        transaction_type = request.query_params.get('type')
        
        if start_date:
            transactions = transactions.filter(date__gte=start_date)
        if end_date:
            transactions = transactions.filter(date__lte=end_date)
        if transaction_type:
            transactions = transactions.filter(type=transaction_type)
            
        # Paginate results
        page = self.paginate_queryset(transactions)
        if page is not None:
            serializer = TransactionSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = TransactionSerializer(transactions, many=True)
        return Response(serializer.data)


class TransactionViewSet(viewsets.ModelViewSet):
    """ViewSet for Transaction model."""
    
    queryset = Transaction.objects.all()
    serializer_class = TransactionSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminUser]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['account', 'type', 'category', 'date']
    search_fields = ['description', 'reference_number']
    ordering_fields = ['date', 'amount', 'created_at']
    
    def perform_create(self, serializer):
        """Set the created_by field to the current user."""
        serializer.save(created_by=self.request.user)
    
    @action(detail=False, methods=['get'])
    def summary(self, request):
        """Get a summary of transactions."""
        period = request.query_params.get('period', 'month')
        transaction_type = request.query_params.get('type')
        
        # Determine the date range based on the period
        today = timezone.now().date()
        if period == 'week':
            start_date = today - timedelta(days=today.weekday())
            end_date = start_date + timedelta(days=6)
        elif period == 'month':
            start_date = today.replace(day=1)
            # Get last day of month
            if today.month == 12:
                end_date = today.replace(year=today.year+1, month=1, day=1) - timedelta(days=1)
            else:
                end_date = today.replace(month=today.month+1, day=1) - timedelta(days=1)
        elif period == 'year':
            start_date = today.replace(month=1, day=1)
            end_date = today.replace(month=12, day=31)
        else:  # Custom period
            start_date = request.query_params.get('start_date', today - timedelta(days=30))
            end_date = request.query_params.get('end_date', today)
        
        # Filter transactions
        transactions = Transaction.objects.filter(date__range=(start_date, end_date))
        if transaction_type:
            transactions = transactions.filter(type=transaction_type)
        
        # Calculate summary
        total = transactions.aggregate(total=Sum('amount'))['total'] or 0
        
        # Get breakdowns
        by_type = transactions.values('type').annotate(total=Sum('amount'))
        by_category = transactions.values(
            'category__name', 'category__category_type'
        ).annotate(total=Sum('amount'))
        
        return Response({
            'start_date': start_date,
            'end_date': end_date,
            'total': total,
            'by_type': by_type,
            'by_category': list(by_category),
        })


class BudgetViewSet(viewsets.ModelViewSet):
    """ViewSet for Budget model."""
    
    queryset = Budget.objects.all()
    serializer_class = BudgetSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminUser]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['branch', 'category', 'period']
    search_fields = ['notes']
    ordering_fields = ['start_date', 'amount', 'created_at']
    
    def perform_create(self, serializer):
        """Set the created_by field to the current user."""
        serializer.save(created_by=self.request.user)
    
    @action(detail=False, methods=['get'])
    def current(self, request):
        """Get currently active budgets."""
        today = timezone.now().date()
        budgets = self.queryset.filter(start_date__lte=today, end_date__gte=today)
        
        # Apply filters
        branch = request.query_params.get('branch')
        category_type = request.query_params.get('category_type')
        
        if branch:
            budgets = budgets.filter(branch_id=branch)
        if category_type:
            budgets = budgets.filter(category__category_type=category_type)
        
        serializer = self.get_serializer(budgets, many=True)
        return Response(serializer.data)


class TaxRateViewSet(viewsets.ModelViewSet):
    """ViewSet for TaxRate model."""
    
    queryset = TaxRate.objects.all()
    serializer_class = TaxRateSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminUser]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['is_active']
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'percentage', 'created_at']


class FinancialReportViewSet(viewsets.ModelViewSet):
    """ViewSet for FinancialReport model."""
    
    queryset = FinancialReport.objects.all()
    serializer_class = FinancialReportSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminUser]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['report_type', 'branch']
    search_fields = ['name']
    ordering_fields = ['name', 'created_at']
    
    def perform_create(self, serializer):
        """Set the generated_by field to the current user."""
        serializer.save(generated_by=self.request.user)
    
    @action(detail=False, methods=['post'])
    def generate(self, request):
        """Generate a new financial report."""
        # Get parameters from request
        report_type = request.data.get('report_type')
        start_date = request.data.get('start_date')
        end_date = request.data.get('end_date')
        branch_id = request.data.get('branch')
        name = request.data.get('name')
        
        if not all([report_type, start_date, end_date, name]):
            return Response({
                "detail": "Missing required parameters."
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Generate report data based on type
        report_data = {}
        
        if report_type == 'income_statement':
            # Calculate income
            income_transactions = Transaction.objects.filter(
                date__range=(start_date, end_date),
                type='income'
            )
            if branch_id:
                income_transactions = income_transactions.filter(
                    Q(account__branch_id=branch_id) | Q(invoice__appointment__branch_id=branch_id)
                )
            
            total_income = income_transactions.aggregate(total=Sum('amount'))['total'] or 0
            
            # Calculate expenses
            expense_transactions = Transaction.objects.filter(
                date__range=(start_date, end_date),
                type='expense'
            )
            if branch_id:
                expense_transactions = expense_transactions.filter(
                    Q(account__branch_id=branch_id) | Q(expense__branch_id=branch_id)
                )
            
            total_expenses = expense_transactions.aggregate(total=Sum('amount'))['total'] or 0
            
            # Calculate net income
            net_income = total_income - total_expenses
            
            # Build report data
            report_data = {
                'total_income': float(total_income),
                'total_expenses': float(total_expenses),
                'net_income': float(net_income),
                'income_by_category': list(income_transactions.values(
                    'category__name'
                ).annotate(total=Sum('amount'))),
                'expenses_by_category': list(expense_transactions.values(
                    'category__name'
                ).annotate(total=Sum('amount')))
            }
        
        # Create the report
        report = FinancialReport.objects.create(
            name=name,
            report_type=report_type,
            start_date=start_date,
            end_date=end_date,
            branch_id=branch_id if branch_id else None,
            parameters=request.data,
            report_data=report_data,
            generated_by=request.user
        )
        
        serializer = self.get_serializer(report)
        return Response(serializer.data, status=status.HTTP_201_CREATED)