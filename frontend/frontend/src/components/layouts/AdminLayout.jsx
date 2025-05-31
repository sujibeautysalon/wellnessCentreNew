import { Outlet } from 'react-router-dom';
import AdminSidebar from '../ui/AdminSidebar';
import AdminHeader from '../ui/AdminHeader';

const AdminLayout = () => {
  return (
    <div className="flex h-screen">
      <AdminSidebar />
      <div className="flex flex-col flex-1 overflow-hidden">
        <AdminHeader />
        <main className="flex-1 overflow-auto p-6 bg-gray-50">
          <Outlet />
        </main>
      </div>
    </div>
  );
};

export default AdminLayout;
