import { Outlet } from 'react-router-dom';
import CustomerSidebar from '../ui/CustomerSidebar';
import CustomerHeader from '../ui/CustomerHeader';

const CustomerLayout = () => {
  return (
    <div className="flex h-screen">
      <CustomerSidebar />
      <div className="flex flex-col flex-1 overflow-hidden">
        <CustomerHeader />
        <main className="flex-1 overflow-auto p-6 bg-gray-50">
          <Outlet />
        </main>
      </div>
    </div>
  );
};

export default CustomerLayout;
