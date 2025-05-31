# filepath: c:\Users\cadsa\OneDrive\Personal\Full stack web development\wellnessCentre\backend\apps\finance\tests\test_models.py
import pytest
from django.test import TestCase
from django.utils import timezone
from decimal import Decimal
from datetime import date, timedelta

from apps.finance.models import (
    BudgetCategory, Expense, FinancialAccount, 
    Transaction, Budget, TaxRate, FinancialReport
)
from apps.core.models import User
from apps.clinic.models import Branch


class BudgetCategoryTests(TestCase):
    """Test the BudgetCategory model."""
    
    def setUp(self):
        self.income_category = BudgetCategory.objects.create(
            name="Service Revenue",
            category_type="income",
            description="Revenue from wellness services"
        )
        
        self.expense_category = BudgetCategory.objects.create(
            name="Office Supplies",
            category_type="expense",
            description="Paper, pens, etc."
        )

    def test_budget_category_creation(self):
        """Test that BudgetCategory instances are created correctly."""
        self.assertEqual(self.income_category.name, "Service Revenue")
        self.assertEqual(self.income_category.category_type, "income")
        self.assertEqual(self.expense_category.name, "Office Supplies")
        self.assertEqual(self.expense_category.category_type, "expense")
        
    def test_budget_category_string_representation(self):
        """Test the string representation of BudgetCategory."""
        self.assertEqual(
            str(self.income_category), 
            "Service Revenue (Income)"
        )
        self.assertEqual(
            str(self.expense_category), 
            "Office Supplies (Expense)"
        )


class ExpenseTests(TestCase):
    """Test the Expense model."""
    
    def setUp(self):
        # Create a user
        self.user = User.objects.create_user(
            email="test@example.com",
            password="password123",
            first_name="Test",
            last_name="User",
            role="admin"
        )
        
        # Create a branch
        self.branch = Branch.objects.create(
            name="Main Branch",
            address="123 Main St",
            phone_number="555-123-4567"
        )
        
        # Create a budget category
        self.expense_category = BudgetCategory.objects.create(
            name="Office Supplies",
            category_type="expense",
            description="Paper, pens, etc."
        )
        
        # Create an expense
        self.expense = Expense.objects.create(
            branch=self.branch,
            category=self.expense_category,
            amount=Decimal('50.00'),
            tax_amount=Decimal('5.00'),
            total_amount=Decimal('55.00'),
            date=date.today(),
            description="Office supplies for reception",
            payment_method="cash",
            created_by=self.user
        )

    def test_expense_creation(self):
        """Test that Expense instances are created correctly."""
        self.assertEqual(self.expense.branch, self.branch)
        self.assertEqual(self.expense.category, self.expense_category)
        self.assertEqual(self.expense.amount, Decimal('50.00'))
        self.assertEqual(self.expense.tax_amount, Decimal('5.00'))
        self.assertEqual(self.expense.total_amount, Decimal('55.00'))
        self.assertEqual(self.expense.payment_method, "cash")
        self.assertEqual(self.expense.status, "pending")
        
    def test_expense_string_representation(self):
        """Test the string representation of Expense."""
        expected = f"Office Supplies: {Decimal('55.00')} ({date.today()})"
        self.assertEqual(str(self.expense), expected)


class FinancialAccountTests(TestCase):
    """Test the FinancialAccount model."""
    
    def setUp(self):
        self.branch = Branch.objects.create(
            name="Main Branch",
            address="123 Main St",
            phone_number="555-123-4567"
        )
        
        self.bank_account = FinancialAccount.objects.create(
            name="Main Checking Account",
            account_type="bank",
            account_number="12345678",
            current_balance=Decimal('10000.00'),
            branch=self.branch
        )
        
        self.cash_account = FinancialAccount.objects.create(
            name="Cash Register",
            account_type="cash",
            current_balance=Decimal('500.00'),
            branch=self.branch
        )

    def test_financial_account_creation(self):
        """Test that FinancialAccount instances are created correctly."""
        self.assertEqual(self.bank_account.name, "Main Checking Account")
        self.assertEqual(self.bank_account.account_type, "bank")
        self.assertEqual(self.bank_account.current_balance, Decimal('10000.00'))
        
        self.assertEqual(self.cash_account.name, "Cash Register")
        self.assertEqual(self.cash_account.account_type, "cash")
        self.assertEqual(self.cash_account.current_balance, Decimal('500.00'))
        
    def test_financial_account_string_representation(self):
        """Test the string representation of FinancialAccount."""
        self.assertEqual(
            str(self.bank_account), 
            "Main Checking Account (Bank Account)"
        )
        self.assertEqual(
            str(self.cash_account), 
            "Cash Register (Cash Account)"
        )


@pytest.mark.django_db
class TransactionTests(TestCase):
    """Test the Transaction model."""
    
    def setUp(self):
        # Create user
        self.user = User.objects.create_user(
            email="test@example.com",
            password="password123",
            role="admin"
        )
        
        # Create branch
        self.branch = Branch.objects.create(
            name="Main Branch",
            address="123 Main St",
            phone_number="555-123-4567"
        )
        
        # Create account
        self.account = FinancialAccount.objects.create(
            name="Main Checking Account",
            account_type="bank",
            current_balance=Decimal('10000.00'),
            branch=self.branch
        )
        
        # Create budget category
        self.income_category = BudgetCategory.objects.create(
            name="Service Revenue",
            category_type="income"
        )
        
        # Create transaction
        self.transaction = Transaction.objects.create(
            account=self.account,
            type="income",
            amount=Decimal('200.00'),
            date=date.today(),
            description="Service payment",
            category=self.income_category,
            created_by=self.user
        )

    def test_transaction_creation(self):
        """Test that Transaction instances are created correctly."""
        self.assertEqual(self.transaction.account, self.account)
        self.assertEqual(self.transaction.type, "income")
        self.assertEqual(self.transaction.amount, Decimal('200.00'))
        self.assertEqual(self.transaction.category, self.income_category)
        
    def test_transaction_string_representation(self):
        """Test the string representation of Transaction."""
        expected = f"Income: {Decimal('200.00')} - {date.today()}"
        self.assertEqual(str(self.transaction), expected)


@pytest.mark.django_db
class BudgetTests(TestCase):
    """Test the Budget model."""
    
    def setUp(self):
        # Create a user
        self.user = User.objects.create_user(
            email="test@example.com",
            password="password123",
            role="admin"
        )
        
        # Create a branch
        self.branch = Branch.objects.create(
            name="Main Branch",
            address="123 Main St",
            phone_number="555-123-4567"
        )
        
        # Create a budget category
        self.expense_category = BudgetCategory.objects.create(
            name="Office Supplies",
            category_type="expense",
        )
        
        # Create a budget
        self.budget = Budget.objects.create(
            branch=self.branch,
            category=self.expense_category,
            amount=Decimal('500.00'),
            period="monthly",
            start_date=date.today().replace(day=1),
            end_date=date.today().replace(day=1) + timedelta(days=30),
            created_by=self.user
        )

    def test_budget_creation(self):
        """Test that Budget instances are created correctly."""
        self.assertEqual(self.budget.branch, self.branch)
        self.assertEqual(self.budget.category, self.expense_category)
        self.assertEqual(self.budget.amount, Decimal('500.00'))
        self.assertEqual(self.budget.period, "monthly")
        
    def test_budget_string_representation(self):
        """Test the string representation of Budget."""
        expected = f"Office Supplies - 500.00 - Monthly ({self.budget.start_date} to {self.budget.end_date})"
        self.assertEqual(str(self.budget), expected)


class TaxRateTests(TestCase):
    """Test the TaxRate model."""
    
    def setUp(self):
        self.tax_rate = TaxRate.objects.create(
            name="GST",
            percentage=Decimal('5.00'),
            description="Goods and Services Tax"
        )

    def test_tax_rate_creation(self):
        """Test that TaxRate instances are created correctly."""
        self.assertEqual(self.tax_rate.name, "GST")
        self.assertEqual(self.tax_rate.percentage, Decimal('5.00'))
        self.assertEqual(self.tax_rate.description, "Goods and Services Tax")
        
    def test_tax_rate_string_representation(self):
        """Test the string representation of TaxRate."""
        self.assertEqual(str(self.tax_rate), "GST (5.00%)")


@pytest.mark.django_db
class FinancialReportTests(TestCase):
    """Test the FinancialReport model."""
    
    def setUp(self):
        # Create a user
        self.user = User.objects.create_user(
            email="test@example.com",
            password="password123",
            role="admin"
        )
        
        # Create a branch
        self.branch = Branch.objects.create(
            name="Main Branch",
            address="123 Main St",
            phone_number="555-123-4567"
        )
        
        # Create a financial report
        self.report = FinancialReport.objects.create(
            name="Q1 2023 Income Statement",
            report_type="income_statement",
            start_date=date(2023, 1, 1),
            end_date=date(2023, 3, 31),
            branch=self.branch,
            parameters={"include_tax": True},
            report_data={
                "total_income": 15000.00,
                "total_expenses": 8000.00,
                "net_income": 7000.00
            },
            generated_by=self.user
        )

    def test_financial_report_creation(self):
        """Test that FinancialReport instances are created correctly."""
        self.assertEqual(self.report.name, "Q1 2023 Income Statement")
        self.assertEqual(self.report.report_type, "income_statement")
        self.assertEqual(self.report.start_date, date(2023, 1, 1))
        self.assertEqual(self.report.end_date, date(2023, 3, 31))
        self.assertEqual(self.report.branch, self.branch)
        self.assertEqual(self.report.parameters, {"include_tax": True})
        self.assertEqual(
            self.report.report_data, 
            {"total_income": 15000.00, "total_expenses": 8000.00, "net_income": 7000.00}
        )
        
    def test_financial_report_string_representation(self):
        """Test the string representation of FinancialReport."""
        expected = f"Q1 2023 Income Statement - Income Statement (2023-01-01 to 2023-03-31)"
        self.assertEqual(str(self.report), expected)