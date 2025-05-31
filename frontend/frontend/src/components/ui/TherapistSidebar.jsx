import { Link, useLocation } from 'react-router-dom';

const TherapistSidebar = () => {
  const location = useLocation();
  
  // Navigation items
  const navItems = [
    { path: '/therapist', label: 'Dashboard', icon: 'home' },
    { path: '/therapist/schedule', label: 'My Schedule', icon: 'calendar' },
    { path: '/therapist/patients', label: 'Patients', icon: 'users' },
    { path: '/therapist/profile', label: 'My Profile', icon: 'user' },
  ];

  // Check if path is active
  const isActive = (path) => {
    return location.pathname === path;
  };

  return (
    <aside className="w-64 bg-secondary-800 text-white flex flex-col">
      <div className="p-5 border-b border-secondary-700">
        <Link to="/therapist" className="text-xl font-bold flex items-center">
          <span className="ml-2">Therapist Portal</span>
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
                  ? 'bg-secondary-600 text-white'
                  : 'text-gray-200 hover:bg-secondary-700'
              }`}
            >
              <span>{item.label}</span>
            </Link>
          ))}
        </nav>
      </div>
      
      <div className="p-4 border-t border-secondary-700">
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

export default TherapistSidebar;
