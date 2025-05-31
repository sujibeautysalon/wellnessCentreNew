import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';

// This would come from an API call in a real application
const mockAnalyticsData = {
  overviewMetrics: [
    { id: 1, name: 'Total Appointments', value: 427, change: 12.4, trend: 'up' },
    { id: 2, name: 'Customer Satisfaction', value: '4.8/5', change: 3.2, trend: 'up' },
    { id: 3, name: 'Revenue per Customer', value: '$250', change: 5.7, trend: 'up' },
    { id: 4, name: 'Cancellation Rate', value: '4.2%', change: -2.1, trend: 'down' }
  ],
  servicePerformance: [
    { id: 1, name: 'Massage Therapy', appointments: 156, revenue: 23400, satisfaction: 4.9 },
    { id: 2, name: 'Acupuncture', appointments: 98, revenue: 14700, satisfaction: 4.7 },
    { id: 3, name: 'Physiotherapy', appointments: 87, revenue: 13050, satisfaction: 4.8 },
    { id: 4, name: 'Nutrition Counseling', appointments: 52, revenue: 6240, satisfaction: 4.6 },
    { id: 5, name: 'Yoga Classes', appointments: 34, revenue: 2380, satisfaction: 4.9 }
  ],
  customerJourney: {
    acquisition: { count: 85, conversion: '34%' },
    engagement: { count: 190, conversion: '78%' },
    retention: { count: 152, conversion: '80%' }
  },
  monthlyTrend: [
    { month: 'Jan', appointments: 342, revenue: 51300 },
    { month: 'Feb', appointments: 356, revenue: 53400 },
    { month: 'Mar', appointments: 375, revenue: 56250 },
    { month: 'Apr', appointments: 401, revenue: 60150 },
    { month: 'May', appointments: 427, revenue: 64050 }
  ]
};

const AdminAnalytics = () => {
  const [analyticsData, setAnalyticsData] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);
  const [timeRange, setTimeRange] = useState('month');

  useEffect(() => {
    // In a real application, we would fetch from API with the timeRange
    const fetchData = async () => {
      try {
        // Simulate API delay
        await new Promise(resolve => setTimeout(resolve, 500));
        setAnalyticsData(mockAnalyticsData);
        setIsLoading(false);
      } catch (err) {
        setError('Failed to load analytics data');
        setIsLoading(false);
      }
    };

    fetchData();
  }, [timeRange]);

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
        <h2 className="text-2xl font-bold text-gray-800">Analytics Dashboard</h2>
        <div className="flex items-center space-x-2">
          <span className="text-sm text-gray-500">Time Range:</span>
          <select 
            value={timeRange}
            onChange={(e) => setTimeRange(e.target.value)}
            className="border border-gray-300 rounded-md text-sm p-1"
          >
            <option value="week">Last 7 Days</option>
            <option value="month">Last 30 Days</option>
            <option value="quarter">Last Quarter</option>
            <option value="year">Last Year</option>
          </select>
          <button className="px-4 py-2 border border-gray-300 rounded-md hover:bg-gray-50">
            Export Report
          </button>
        </div>
      </div>

      {/* Overview Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {analyticsData.overviewMetrics.map((metric) => (
          <div key={metric.id} className="bg-white rounded-lg shadow p-6">
            <p className="text-gray-500 text-sm">{metric.name}</p>
            <div className="flex items-end justify-between mt-2">
              <h3 className="text-2xl font-bold">{metric.value}</h3>
              <div className={`flex items-center text-sm ${
                metric.trend === 'up' 
                  ? metric.name === 'Cancellation Rate' ? 'text-red-600' : 'text-green-600' 
                  : metric.name === 'Cancellation Rate' ? 'text-green-600' : 'text-red-600'
              }`}>
                <span>{metric.change}%</span>
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Appointment Trend */}
      <div className="bg-white rounded-lg shadow p-6">
        <h3 className="text-lg font-medium text-gray-800 mb-4">Monthly Performance</h3>
        <div className="relative h-72">
          {/* In a real app, we would use a charting library like Chart.js or Recharts */}
          <div className="flex justify-between h-full items-end">
            {analyticsData.monthlyTrend.map((data, index) => (
              <div key={index} className="flex flex-col items-center w-1/5">
                <div className="w-full flex flex-col items-center">
                  <div 
                    className="w-10 bg-primary-500 rounded-t"
                    style={{ 
                      height: `${(data.appointments / Math.max(...analyticsData.monthlyTrend.map(d => d.appointments))) * 200}px`
                    }}
                  ></div>
                  <span className="text-xs text-gray-600 mt-1">{data.month}</span>
                </div>
              </div>
            ))}
          </div>
          <div className="absolute top-0 left-0 text-xs text-gray-400">Appointments</div>
        </div>
      </div>

      {/* Service Performance */}
      <div className="bg-white rounded-lg shadow">
        <div className="px-6 py-4 border-b border-gray-200">
          <h3 className="text-lg font-medium text-gray-800">Service Performance</h3>
        </div>
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Service
                </th>
                <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Appointments
                </th>
                <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Revenue
                </th>
                <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Satisfaction
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {analyticsData.servicePerformance.map((service) => (
                <tr key={service.id}>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="text-sm font-medium text-gray-900">{service.name}</div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="text-sm text-gray-900">{service.appointments}</div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="text-sm text-gray-900">${service.revenue.toLocaleString()}</div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="flex items-center">
                      <span className="text-sm text-gray-900 mr-2">{service.satisfaction}</span>
                      <div className="flex">
                        {[...Array(5)].map((_, i) => (
                          <svg 
                            key={i}
                            className={`w-4 h-4 ${i < Math.floor(service.satisfaction) ? 'text-yellow-400' : 'text-gray-300'}`} 
                            xmlns="http://www.w3.org/2000/svg" 
                            viewBox="0 0 20 20"
                            fill="currentColor"
                          >
                            <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
                          </svg>
                        ))}
                      </div>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Customer Journey */}
      <div className="bg-white rounded-lg shadow p-6">
        <h3 className="text-lg font-medium text-gray-800 mb-4">Customer Journey</h3>
        <div className="flex flex-col md:flex-row justify-between">
          <div className="bg-green-50 p-4 rounded-lg text-center flex-1 md:mx-2 mb-4 md:mb-0">
            <div className="text-3xl font-bold text-green-700">{analyticsData.customerJourney.acquisition.count}</div>
            <p className="text-green-600 font-medium mt-1">New Customers</p>
            <p className="text-sm text-gray-500 mt-1">Conversion: {analyticsData.customerJourney.acquisition.conversion}</p>
          </div>
          <div className="bg-blue-50 p-4 rounded-lg text-center flex-1 md:mx-2 mb-4 md:mb-0">
            <div className="text-3xl font-bold text-blue-700">{analyticsData.customerJourney.engagement.count}</div>
            <p className="text-blue-600 font-medium mt-1">Engaged Customers</p>
            <p className="text-sm text-gray-500 mt-1">Conversion: {analyticsData.customerJourney.engagement.conversion}</p>
          </div>
          <div className="bg-purple-50 p-4 rounded-lg text-center flex-1 md:mx-2">
            <div className="text-3xl font-bold text-purple-700">{analyticsData.customerJourney.retention.count}</div>
            <p className="text-purple-600 font-medium mt-1">Retained Customers</p>
            <p className="text-sm text-gray-500 mt-1">Conversion: {analyticsData.customerJourney.retention.conversion}</p>
          </div>
        </div>
      </div>

      <div className="text-center">
        <Link to="/admin/analytics/reports" className="inline-block px-6 py-3 bg-primary-600 text-white font-medium rounded-md hover:bg-primary-700 transition">
          View Detailed Analytics Reports
        </Link>
      </div>
    </div>
  );
};

export default AdminAnalytics;
