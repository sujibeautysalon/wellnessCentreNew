import { Outlet } from 'react-router-dom';
import TherapistSidebar from '../ui/TherapistSidebar';
import TherapistHeader from '../ui/TherapistHeader';

const TherapistLayout = () => {
  return (
    <div className="flex h-screen">
      <TherapistSidebar />
      <div className="flex flex-col flex-1 overflow-hidden">
        <TherapistHeader />
        <main className="flex-1 overflow-auto p-6 bg-gray-50">
          <Outlet />
        </main>
      </div>
    </div>
  );
};

export default TherapistLayout;
