import { Link, useLocation } from 'react-router-dom';

const AdminSidebar = () => {
  const location = useLocation();
  
  // Navigation items
  const navItems = [
    { path: '/admin', label: 'Dashboard', icon: 'home' },
    { path: '/admin/users', label: 'Users', icon: 'users' },
    { path: '/admin/appointments', label: 'Appointments', icon: 'calendar' },
    { path: '/admin/services', label: 'Services', icon: 'briefcase' },
    { path: '/admin/inventory', label: 'Inventory', icon: 'archive' },
    { path: '/admin/finance', label: 'Finance', icon: 'dollar-sign' },
    { path: '/admin/analytics', label: 'Analytics', icon: 'chart-bar' },
    { path: '/admin/settings', label: 'Settings', icon: 'cog' },
  ];

  // Check if path is active
  const isActive = (path) => {
    return location.pathname === path;
  };

  return (
    <aside className="w-64 bg-gray-800 text-white flex flex-col">
      <div className="p-5 border-b border-gray-700">
        <Link to="/admin" className="text-xl font-bold flex items-center">
          <span className="ml-2">Admin Panel</span>
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
                  : 'text-gray-300 hover:bg-gray-700'
              }`}
            >
              <span>{item.label}</span>
            </Link>
          ))}
        </nav>
      </div>
      
      <div className="p-4 border-t border-gray-700">
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

export default AdminSidebar;
