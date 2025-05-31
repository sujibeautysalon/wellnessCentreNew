# filepath: c:\Users\cadsa\OneDrive\Personal\Full stack web development\wellnessCentre\backend\apps\finance\serializers.py
from rest_framework import serializers
from apps.finance.models import (
    BudgetCategory, Expense, FinancialAccount, 
    Transaction, Budget, TaxRate, FinancialReport
)
from apps.core.serializers import UserSerializer
from apps.clinic.serializers import BranchSerializer


class BudgetCategorySerializer(serializers.ModelSerializer):
    """Serializer for BudgetCategory model."""
    
    class Meta:
        model = BudgetCategory
        fields = '__all__'


class ExpenseSerializer(serializers.ModelSerializer):
    """Serializer for Expense model."""
    
    approved_by_detail = UserSerializer(source='approved_by', read_only=True)
    created_by_detail = UserSerializer(source='created_by', read_only=True)
    category_detail = BudgetCategorySerializer(source='category', read_only=True)
    branch_detail = BranchSerializer(source='branch', read_only=True)
    
    class Meta:
        model = Expense
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at')


class FinancialAccountSerializer(serializers.ModelSerializer):
    """Serializer for FinancialAccount model."""
    
    branch_detail = BranchSerializer(source='branch', read_only=True)
    transaction_count = serializers.SerializerMethodField()
    
    class Meta:
        model = FinancialAccount
        fields = '__all__'
        
    def get_transaction_count(self, obj):
        """Get number of transactions for this account."""
        return obj.transactions.count()


class TransactionSerializer(serializers.ModelSerializer):
    """Serializer for Transaction model."""
    
    account_detail = FinancialAccountSerializer(source='account', read_only=True)
    category_detail = BudgetCategorySerializer(source='category', read_only=True)
    created_by_detail = UserSerializer(source='created_by', read_only=True)
    
    class Meta:
        model = Transaction
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at')


class BudgetSerializer(serializers.ModelSerializer):
    """Serializer for Budget model."""
    
    branch_detail = BranchSerializer(source='branch', read_only=True)
    category_detail = BudgetCategorySerializer(source='category', read_only=True)
    created_by_detail = UserSerializer(source='created_by', read_only=True)
    actual_spending = serializers.SerializerMethodField()
    variance = serializers.SerializerMethodField()
    variance_percentage = serializers.SerializerMethodField()
    
    class Meta:
        model = Budget
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at')
        
    def get_actual_spending(self, obj):
        """Get actual amount spent against this budget."""
        # Get transactions in the budget category during the budget period
        transactions = Transaction.objects.filter(
            category=obj.category,
            date__range=(obj.start_date, obj.end_date)
        )
        
        # For expense categories, sum expenses
        if obj.category.category_type == 'expense':
            return sum(t.amount for t in transactions if t.type == 'expense')
        
        # For income categories, sum income
        return sum(t.amount for t in transactions if t.type == 'income')
    
    def get_variance(self, obj):
        """Calculate variance (budget - actual)."""
        actual = self.get_actual_spending(obj)
        return float(obj.amount) - float(actual)
    
    def get_variance_percentage(self, obj):
        """Calculate variance as a percentage of budget."""
        variance = self.get_variance(obj)
        if obj.amount == 0:
            return 0
        return (variance / float(obj.amount)) * 100


class TaxRateSerializer(serializers.ModelSerializer):
    """Serializer for TaxRate model."""
    
    class Meta:
        model = TaxRate
        fields = '__all__'


class FinancialReportSerializer(serializers.ModelSerializer):
    """Serializer for FinancialReport model."""
    
    branch_detail = BranchSerializer(source='branch', read_only=True)
    generated_by_detail = UserSerializer(source='generated_by', read_only=True)
    
    class Meta:
        model = FinancialReport
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at', 'file', 'report_data')