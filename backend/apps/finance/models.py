# filepath: c:\Users\cadsa\OneDrive\Personal\Full stack web development\wellnessCentre\backend\apps\finance\models.py
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from apps.clinic.models import Branch
from apps.booking.models import Invoice, Payment


class BudgetCategory(models.Model):
    """Model for budget categories."""
    
    CATEGORY_TYPES = [
        ('income', 'Income'),
        ('expense', 'Expense'),
    ]
    
    name = models.CharField(_('name'), max_length=100)
    category_type = models.CharField(_('category type'), max_length=10, choices=CATEGORY_TYPES)
    description = models.TextField(_('description'), blank=True, null=True)
    is_active = models.BooleanField(_('is active'), default=True)
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)
    
    class Meta:
        verbose_name = _('budget category')
        verbose_name_plural = _('budget categories')
        ordering = ['name']
        
    def __str__(self):
        return f"{self.name} ({self.get_category_type_display()})"


class Expense(models.Model):
    """Model for tracking expenses."""
    
    PAYMENT_METHODS = [
        ('cash', 'Cash'),
        ('bank_transfer', 'Bank Transfer'),
        ('card', 'Card'),
        ('cheque', 'Cheque'),
        ('other', 'Other'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('paid', 'Paid'),
    ]
    
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE, 
                             related_name='expenses')
    category = models.ForeignKey(BudgetCategory, on_delete=models.CASCADE, 
                               related_name='expenses',
                               limit_choices_to={'category_type': 'expense'})
    amount = models.DecimalField(_('amount'), max_digits=10, decimal_places=2)
    tax_amount = models.DecimalField(_('tax amount'), max_digits=10, decimal_places=2, default=0)
    total_amount = models.DecimalField(_('total amount'), max_digits=10, decimal_places=2)
    date = models.DateField(_('date'))
    description = models.TextField(_('description'))
    payment_method = models.CharField(_('payment method'), max_length=20, choices=PAYMENT_METHODS)
    reference_number = models.CharField(_('reference number'), max_length=100, blank=True, null=True)
    receipt = models.FileField(_('receipt'), upload_to='expense_receipts/', blank=True, null=True)
    status = models.CharField(_('status'), max_length=20, choices=STATUS_CHOICES, default='pending')
    approved_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, 
                                  null=True, blank=True, related_name='approved_expenses')
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                                 related_name='created_expenses')
    vendor_name = models.CharField(_('vendor name'), max_length=255, blank=True, null=True)
    recurring = models.BooleanField(_('recurring'), default=False)
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)
    
    class Meta:
        verbose_name = _('expense')
        verbose_name_plural = _('expenses')
        ordering = ['-date']
        
    def __str__(self):
        return f"{self.category.name}: {self.total_amount} ({self.date})"


class FinancialAccount(models.Model):
    """Model for financial accounts (banks, cash, etc.)."""
    
    ACCOUNT_TYPES = [
        ('bank', 'Bank Account'),
        ('cash', 'Cash Account'),
        ('credit_card', 'Credit Card'),
        ('other', 'Other'),
    ]
    
    name = models.CharField(_('name'), max_length=100)
    account_type = models.CharField(_('account type'), max_length=20, choices=ACCOUNT_TYPES)
    account_number = models.CharField(_('account number'), max_length=100, blank=True, null=True)
    current_balance = models.DecimalField(_('current balance'), max_digits=12, decimal_places=2)
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE, 
                             related_name='financial_accounts', null=True, blank=True)
    description = models.TextField(_('description'), blank=True, null=True)
    is_active = models.BooleanField(_('is active'), default=True)
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)
    
    class Meta:
        verbose_name = _('financial account')
        verbose_name_plural = _('financial accounts')
        ordering = ['name']
        
    def __str__(self):
        return f"{self.name} ({self.get_account_type_display()})"


class Transaction(models.Model):
    """Model for financial transactions."""
    
    TRANSACTION_TYPES = [
        ('income', 'Income'),
        ('expense', 'Expense'),
        ('transfer', 'Transfer'),
        ('refund', 'Refund'),
        ('adjustment', 'Adjustment'),
    ]
    
    account = models.ForeignKey(FinancialAccount, on_delete=models.CASCADE, 
                              related_name='transactions')
    type = models.CharField(_('type'), max_length=20, choices=TRANSACTION_TYPES)
    amount = models.DecimalField(_('amount'), max_digits=10, decimal_places=2)
    date = models.DateField(_('date'))
    description = models.TextField(_('description'))
    category = models.ForeignKey(BudgetCategory, on_delete=models.SET_NULL, 
                               null=True, blank=True, related_name='transactions')
    reference_number = models.CharField(_('reference number'), max_length=100, blank=True, null=True)
    payment = models.ForeignKey(Payment, on_delete=models.SET_NULL, 
                              null=True, blank=True, related_name='transactions')
    expense = models.ForeignKey(Expense, on_delete=models.SET_NULL, 
                              null=True, blank=True, related_name='transactions')
    invoice = models.ForeignKey(Invoice, on_delete=models.SET_NULL, 
                              null=True, blank=True, related_name='transactions')
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, 
                                 null=True, related_name='created_transactions')
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)
    
    class Meta:
        verbose_name = _('transaction')
        verbose_name_plural = _('transactions')
        ordering = ['-date', '-created_at']
        
    def __str__(self):
        return f"{self.get_type_display()}: {self.amount} - {self.date}"


class Budget(models.Model):
    """Model for budgeting."""
    
    PERIOD_CHOICES = [
        ('monthly', 'Monthly'),
        ('quarterly', 'Quarterly'),
        ('yearly', 'Yearly'),
    ]
    
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE, related_name='budgets')
    category = models.ForeignKey(BudgetCategory, on_delete=models.CASCADE, related_name='budgets')
    amount = models.DecimalField(_('amount'), max_digits=12, decimal_places=2)
    period = models.CharField(_('period'), max_length=20, choices=PERIOD_CHOICES, default='monthly')
    start_date = models.DateField(_('start date'))
    end_date = models.DateField(_('end date'))
    notes = models.TextField(_('notes'), blank=True, null=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, 
                                 null=True, related_name='created_budgets')
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)
    
    class Meta:
        verbose_name = _('budget')
        verbose_name_plural = _('budgets')
        ordering = ['-start_date']
        
    def __str__(self):
        return f"{self.category.name} - {self.amount} - {self.period} ({self.start_date} to {self.end_date})"


class TaxRate(models.Model):
    """Model for tax rates."""
    
    name = models.CharField(_('name'), max_length=100)
    percentage = models.DecimalField(_('percentage'), max_digits=5, decimal_places=2)
    description = models.TextField(_('description'), blank=True, null=True)
    is_active = models.BooleanField(_('is active'), default=True)
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)
    
    class Meta:
        verbose_name = _('tax rate')
        verbose_name_plural = _('tax rates')
        ordering = ['name']
        
    def __str__(self):
        return f"{self.name} ({self.percentage}%)"


class FinancialReport(models.Model):
    """Model for storing generated financial reports."""
    
    REPORT_TYPES = [
        ('income_statement', 'Income Statement'),
        ('balance_sheet', 'Balance Sheet'),
        ('cash_flow', 'Cash Flow Statement'),
        ('tax_summary', 'Tax Summary'),
        ('revenue_by_service', 'Revenue by Service'),
        ('expense_by_category', 'Expense by Category'),
        ('custom', 'Custom Report'),
    ]
    
    name = models.CharField(_('name'), max_length=255)
    report_type = models.CharField(_('report type'), max_length=50, choices=REPORT_TYPES)
    start_date = models.DateField(_('start date'))
    end_date = models.DateField(_('end date'))
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE, 
                             related_name='financial_reports', null=True, blank=True)
    parameters = models.JSONField(_('parameters'), blank=True, null=True)
    report_data = models.JSONField(_('report data'), blank=True, null=True)
    file = models.FileField(_('file'), upload_to='financial_reports/', blank=True, null=True)
    generated_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                                   related_name='generated_reports')
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)
    
    class Meta:
        verbose_name = _('financial report')
        verbose_name_plural = _('financial reports')
        ordering = ['-created_at']
        
    def __str__(self):
        return f"{self.name} - {self.get_report_type_display()} ({self.start_date} to {self.end_date})"