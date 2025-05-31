const CustomerHeader = () => {
  return (
    <header className="bg-white border-b border-gray-200 shadow-sm">
      <div className="flex items-center justify-between p-4">
        <div>
          <h1 className="text-2xl font-semibold text-gray-800">My Dashboard</h1>
          <p className="text-gray-500">Welcome back, Customer Name</p>
        </div>
        
        <div className="flex items-center space-x-4">
          <div className="relative">
            <button className="p-2 text-gray-500 rounded-full hover:bg-gray-100">
              <span>Notifications</span>
            </button>
          </div>
          
          <div className="relative">
            <button className="flex items-center text-gray-700 hover:text-primary-600">
              <img
                src="/profile-placeholder.jpg"
                alt="Profile"
                className="w-8 h-8 rounded-full"
              />
              <span className="ml-2">Customer Name</span>
            </button>
          </div>
        </div>
      </div>
    </header>
  );
};

export default CustomerHeader;
