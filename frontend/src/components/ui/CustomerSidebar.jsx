import { Link, useLocation } from 'react-router-dom';

const CustomerSidebar = () => {
  const location = useLocation();
  
  // Navigation items
  const navItems = [
    { path: '/customer', label: 'Dashboard', icon: 'home' },
    { path: '/customer/appointments', label: 'Appointments', icon: 'calendar' },
    { path: '/customer/profile', label: 'My Profile', icon: 'user' },
    { path: '/customer/billing', label: 'Billing', icon: 'credit-card' },
    { path: '/customer/medical-records', label: 'Medical Records', icon: 'file-medical' },
  ];

  // Check if path is active
  const isActive = (path) => {
    return location.pathname === path;
  };

  return (
    <aside className="w-64 bg-primary-800 text-white flex flex-col">
      <div className="p-5 border-b border-primary-700">
        <Link to="/customer" className="text-xl font-bold flex items-center">
          <span className="ml-2">Customer Portal</span>
        </Link>
      </div>
      
      <div className="flex-grow overflow-y-auto">
        <nav className="p-4 space-y-1">
          {navItems.map((item) => (
            <Link
              key={item.path}
              to={item.path}
              className={`flex items-center px-4 py-3 rounded-md transition ${
                isActive(item.path)
                  ? 'bg-primary-600 text-white'
                  : 'text-gray-200 hover:bg-primary-700'
              }`}
            >
              <span>{item.label}</span>
            </Link>
          ))}
        </nav>
      </div>
      
      <div className="p-4 border-t border-primary-700">
        <Link
          to="/"
          className="flex items-center text-gray-300 hover:text-white transition"
        >
          <span>Back to Site</span>
        </Link>
      </div>
    </aside>
  );
};

export default CustomerSidebar;
