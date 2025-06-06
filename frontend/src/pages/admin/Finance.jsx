import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';

// This would come from an API call in a real application
const mockFinanceData = {
  budgets: [
    { id: 1, name: 'Q2 2025 Operations', amount: 120000, spent: 78500, category: 'Operations' },
    { id: 2, name: 'Q2 2025 Marketing', amount: 45000, spent: 32000, category: 'Marketing' },
    { id: 3, name: 'Q2 2025 Equipment', amount: 30000, spent: 12000, category: 'Equipment' }
  ],
  recentTransactions: [
    { id: 101, date: '2025-05-28', description: 'Medical supplies', amount: -1250.00, account: 'Operations Expense' },
    { id: 102, date: '2025-05-26', description: 'Patient payment - Treatment #45892', amount: 780.00, account: 'Revenue' },
    { id: 103, date: '2025-05-25', description: 'Utility bill', amount: -450.00, account: 'Operations Expense' },
    { id: 104, date: '2025-05-23', description: 'Insurance payment', amount: 1200.00, account: 'Revenue' },
    { id: 105, date: '2025-05-20', description: 'Staff payroll', amount: -9800.00, account: 'Payroll' }
  ],
  financialSummary: {
    revenue: {
      currentMonth: 85000,
      previousMonth: 78000,
      percentChange: 8.97
    },
    expenses: {
      currentMonth: 65000,
      previousMonth: 68000,
      percentChange: -4.41
    },
    profit: {
      currentMonth: 20000,
      previousMonth: 10000,
      percentChange: 100
    }
  }
};

const AdminFinance = () => {
  const [financeData, setFinanceData] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    // In a real application, we would fetch from API
    const fetchData = async () => {
      try {
        // Simulate API delay
        await new Promise(resolve => setTimeout(resolve, 500));
        setFinanceData(mockFinanceData);
        setIsLoading(false);
      } catch (err) {
        setError('Failed to load financial data');
        setIsLoading(false);
      }
    };

    fetchData();
  }, []);

  if (isLoading) {
    return (
      <div className="flex justify-center items-center h-full">
        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-primary-600"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="text-center py-10">
        <p className="text-red-500 text-lg">{error}</p>
        <button 
          className="mt-4 px-4 py-2 bg-primary-600 text-white rounded-md hover:bg-primary-700"
          onClick={() => window.location.reload()}
        >
          Try Again
        </button>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h2 className="text-2xl font-bold text-gray-800">Financial Management</h2>
        <div className="flex space-x-3">
          <button className="px-4 py-2 bg-primary-600 text-white rounded-md hover:bg-primary-700">
            Generate Report
          </button>
          <button className="px-4 py-2 border border-gray-300 rounded-md hover:bg-gray-50">
            Export Data
          </button>
        </div>
      </div>

      {/* Financial Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex justify-between items-start">
            <div>
              <p className="text-gray-500 text-sm">Revenue</p>
              <h3 className="text-2xl font-bold">${financeData.financialSummary.revenue.currentMonth.toLocaleString()}</h3>
            </div>
            <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
              financeData.financialSummary.revenue.percentChange >= 0 
                ? 'bg-green-100 text-green-800' 
                : 'bg-red-100 text-red-800'
            }`}>
              {financeData.financialSummary.revenue.percentChange >= 0 ? '+' : ''}
              {financeData.financialSummary.revenue.percentChange}%
            </span>
          </div>
          <p className="text-sm text-gray-500 mt-2">vs. ${financeData.financialSummary.revenue.previousMonth.toLocaleString()} last month</p>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex justify-between items-start">
            <div>
              <p className="text-gray-500 text-sm">Expenses</p>
              <h3 className="text-2xl font-bold">${financeData.financialSummary.expenses.currentMonth.toLocaleString()}</h3>
            </div>
            <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
              financeData.financialSummary.expenses.percentChange <= 0 
                ? 'bg-green-100 text-green-800' 
                : 'bg-red-100 text-red-800'
            }`}>
              {financeData.financialSummary.expenses.percentChange >= 0 ? '+' : ''}
              {financeData.financialSummary.expenses.percentChange}%
            </span>
          </div>
          <p className="text-sm text-gray-500 mt-2">vs. ${financeData.financialSummary.expenses.previousMonth.toLocaleString()} last month</p>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex justify-between items-start">
            <div>
              <p className="text-gray-500 text-sm">Profit</p>
              <h3 className="text-2xl font-bold">${financeData.financialSummary.profit.currentMonth.toLocaleString()}</h3>
            </div>
            <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
              financeData.financialSummary.profit.percentChange >= 0 
                ? 'bg-green-100 text-green-800' 
                : 'bg-red-100 text-red-800'
            }`}>
              {financeData.financialSummary.profit.percentChange >= 0 ? '+' : ''}
              {financeData.financialSummary.profit.percentChange}%
            </span>
          </div>
          <p className="text-sm text-gray-500 mt-2">vs. ${financeData.financialSummary.profit.previousMonth.toLocaleString()} last month</p>
        </div>
      </div>

      {/* Budget Tracking */}
      <div className="bg-white rounded-lg shadow">
        <div className="px-6 py-4 border-b border-gray-200">
          <h3 className="text-lg font-medium text-gray-800">Budget Tracking</h3>
        </div>
        <div className="p-6">
          <div className="space-y-4">
            {financeData.budgets.map(budget => (
              <div key={budget.id} className="border-b border-gray-100 pb-4 last:border-0 last:pb-0">
                <div className="flex justify-between items-center mb-2">
                  <div>
                    <h4 className="font-medium">{budget.name}</h4>
                    <p className="text-sm text-gray-500">{budget.category}</p>
                  </div>
                  <div className="text-right">
                    <p className="font-medium">${budget.spent.toLocaleString()} / ${budget.amount.toLocaleString()}</p>
                    <p className="text-sm text-gray-500">
                      {Math.round((budget.spent / budget.amount) * 100)}% used
                    </p>
                  </div>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2.5">
                  <div 
                    className={`h-2.5 rounded-full ${
                      (budget.spent / budget.amount) > 0.9 
                        ? 'bg-red-500'
                        : (budget.spent / budget.amount) > 0.7
                          ? 'bg-yellow-500' 
                          : 'bg-green-500'
                    }`} 
                    style={{ width: `${Math.min(100, Math.round((budget.spent / budget.amount) * 100))}%` }}
                  ></div>
                </div>
              </div>
            ))}
          </div>
          <div className="mt-4 text-center">
            <Link to="/admin/finance/budgets" className="text-primary-600 hover:text-primary-800 text-sm font-medium">
              View All Budgets
            </Link>
          </div>
        </div>
      </div>

      {/* Recent Transactions */}
      <div className="bg-white rounded-lg shadow">
        <div className="px-6 py-4 border-b border-gray-200 flex justify-between items-center">
          <h3 className="text-lg font-medium text-gray-800">Recent Transactions</h3>
          <Link to="/admin/finance/transactions" className="text-primary-600 hover:text-primary-800 text-sm font-medium">
            View All
          </Link>
        </div>
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Date
                </th>
                <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Description
                </th>
                <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Account
                </th>
                <th scope="col" className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Amount
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {financeData.recentTransactions.map((transaction) => (
                <tr key={transaction.id}>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {transaction.date}
                  </td>
                  <td className="px-6 py-4 text-sm text-gray-900">
                    {transaction.description}
                  </td>
                  <td className="px-6 py-4 text-sm text-gray-500">
                    {transaction.account}
                  </td>
                  <td className={`px-6 py-4 whitespace-nowrap text-sm font-medium text-right ${
                    transaction.amount >= 0 ? 'text-green-600' : 'text-red-600'
                  }`}>
                    {transaction.amount >= 0 ? '+' : ''}${Math.abs(transaction.amount).toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

export default AdminFinance;
