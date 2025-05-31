import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';

// This would come from an API call in a real application
const mockDashboardData = {
  summary: {
    totalAppointments: 427,
    activeCustomers: 285,
    therapists: 12,
    revenue: 85000
  },
  recentAppointments: [
    { id: 101, date: '2025-05-31', time: '10:00 AM', service: 'Massage Therapy', customer: 'Jane Smith', therapist: 'Dr. Williams', status: 'Completed' },
    { id: 102, date: '2025-05-31', time: '11:30 AM', service: 'Acupuncture', customer: 'John Davis', therapist: 'Dr. Chen', status: 'Completed' },
    { id: 103, date: '2025-05-31', time: '2:00 PM', service: 'Physiotherapy', customer: 'Michael Brown', therapist: 'Dr. Johnson', status: 'In Progress' },
    { id: 104, date: '2025-06-01', time: '9:00 AM', service: 'Nutrition Counseling', customer: 'Sarah Wilson', therapist: 'Dr. Martinez', status: 'Scheduled' },
    { id: 105, date: '2025-06-01', time: '10:30 AM', service: 'Massage Therapy', customer: 'Robert Lee', therapist: 'Dr. Williams', status: 'Scheduled' }
  ],
  upcomingTasks: [
    { id: 1, title: 'Staff Meeting', date: '2025-05-31', time: '4:00 PM', priority: 'High' },
    { id: 2, title: 'Order New Supplies', date: '2025-06-01', priority: 'Medium' },
    { id: 3, title: 'Review Monthly Reports', date: '2025-06-02', priority: 'High' },
    { id: 4, title: 'Follow up with New Clients', date: '2025-06-03', priority: 'Medium' }
  ],
  alerts: [
    { id: 1, type: 'warning', message: 'Low inventory on massage oils', date: '2025-05-30' },
    { id: 2, type: 'info', message: 'New staff training scheduled for next week', date: '2025-05-29' },
    { id: 3, type: 'error', message: 'Maintenance required for therapy room #3', date: '2025-05-28' }
  ]
};

const AdminDashboard = () => {
  const [dashboardData, setDashboardData] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    // In a real application, we would fetch from API
    const fetchData = async () => {
      try {
        // Simulate API delay
        await new Promise(resolve => setTimeout(resolve, 500));
        setDashboardData(mockDashboardData);
        setIsLoading(false);
      } catch (err) {
        setError('Failed to load dashboard data');
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
      <h2 className="text-2xl font-bold text-gray-800">Admin Dashboard</h2>

      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <div className="bg-white rounded-lg shadow p-6">
          <p className="text-gray-500 text-sm">Total Appointments</p>
          <h3 className="text-2xl font-bold">{dashboardData.summary.totalAppointments}</h3>
          <div className="mt-2">
            <Link to="/admin/appointments" className="text-primary-600 text-sm hover:underline">
              View Details →
            </Link>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <p className="text-gray-500 text-sm">Active Customers</p>
          <h3 className="text-2xl font-bold">{dashboardData.summary.activeCustomers}</h3>
          <div className="mt-2">
            <Link to="/admin/users" className="text-primary-600 text-sm hover:underline">
              View Details →
            </Link>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <p className="text-gray-500 text-sm">Therapists</p>
          <h3 className="text-2xl font-bold">{dashboardData.summary.therapists}</h3>
          <div className="mt-2">
            <Link to="/admin/users" className="text-primary-600 text-sm hover:underline">
              View Details →
            </Link>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <p className="text-gray-500 text-sm">Monthly Revenue</p>
          <h3 className="text-2xl font-bold">${dashboardData.summary.revenue.toLocaleString()}</h3>
          <div className="mt-2">
            <Link to="/admin/finance" className="text-primary-600 text-sm hover:underline">
              View Details →
            </Link>
          </div>
        </div>
      </div>

      {/* Recent Appointments */}
      <div className="bg-white rounded-lg shadow">
        <div className="px-6 py-4 border-b border-gray-200 flex justify-between items-center">
          <h3 className="text-lg font-medium text-gray-800">Recent Appointments</h3>
          <Link to="/admin/appointments" className="text-primary-600 hover:text-primary-800 text-sm font-medium">
            View All
          </Link>
        </div>
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Date & Time
                </th>
                <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Service
                </th>
                <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Customer
                </th>
                <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Therapist
                </th>
                <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Status
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {dashboardData.recentAppointments.map((appointment) => (
                <tr key={appointment.id}>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {appointment.date} <br /> {appointment.time}
                  </td>
                  <td className="px-6 py-4 text-sm text-gray-900">
                    {appointment.service}
                  </td>
                  <td className="px-6 py-4 text-sm text-gray-500">
                    {appointment.customer}
                  </td>
                  <td className="px-6 py-4 text-sm text-gray-500">
                    {appointment.therapist}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                      appointment.status === 'Completed' ? 'bg-green-100 text-green-800' :
                      appointment.status === 'In Progress' ? 'bg-blue-100 text-blue-800' :
                      'bg-yellow-100 text-yellow-800'
                    }`}>
                      {appointment.status}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Bottom Row: Tasks and Alerts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Tasks */}
        <div className="bg-white rounded-lg shadow">
          <div className="px-6 py-4 border-b border-gray-200">
            <h3 className="text-lg font-medium text-gray-800">Upcoming Tasks</h3>
          </div>
          <div className="p-6">
            <ul className="divide-y divide-gray-200">
              {dashboardData.upcomingTasks.map((task) => (
                <li key={task.id} className="py-4 flex justify-between">
                  <div>
                    <p className="font-medium text-gray-900">{task.title}</p>
                    <p className="text-sm text-gray-500">
                      {task.date} {task.time && `at ${task.time}`}
                    </p>
                  </div>
                  <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                    task.priority === 'High' ? 'bg-red-100 text-red-800' : 'bg-yellow-100 text-yellow-800'
                  }`}>
                    {task.priority}
                  </span>
                </li>
              ))}
            </ul>
          </div>
        </div>

        {/* Alerts */}
        <div className="bg-white rounded-lg shadow">
          <div className="px-6 py-4 border-b border-gray-200">
            <h3 className="text-lg font-medium text-gray-800">System Alerts</h3>
          </div>
          <div className="p-6">
            <ul className="divide-y divide-gray-200">
              {dashboardData.alerts.map((alert) => (
                <li key={alert.id} className="py-4">
                  <div className={`flex items-start ${
                    alert.type === 'error' ? 'text-red-600' :
                    alert.type === 'warning' ? 'text-yellow-600' : 'text-blue-600'
                  }`}>
                    <p className="font-medium">{alert.message}</p>
                  </div>
                  <p className="text-sm text-gray-500 mt-1">Reported on {alert.date}</p>
                </li>
              ))}
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AdminDashboard;
