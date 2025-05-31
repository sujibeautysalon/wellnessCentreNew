# filepath: c:\Users\cadsa\OneDrive\Personal\Full stack web development\wellnessCentre\backend\apps\finance\urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from apps.finance.views import (
    BudgetCategoryViewSet, ExpenseViewSet, FinancialAccountViewSet,
    TransactionViewSet, BudgetViewSet, TaxRateViewSet, FinancialReportViewSet
)

router = DefaultRouter()
router.register(r'budget-categories', BudgetCategoryViewSet)
router.register(r'expenses', ExpenseViewSet)
router.register(r'financial-accounts', FinancialAccountViewSet)
router.register(r'transactions', TransactionViewSet)
router.register(r'budgets', BudgetViewSet)
router.register(r'tax-rates', TaxRateViewSet)
router.register(r'financial-reports', FinancialReportViewSet)

urlpatterns = [
    path('', include(router.urls)),
]