import { createBrowserRouter } from 'react-router-dom';

// Layouts
import RootLayout from '../components/layouts/RootLayout';
import AdminLayout from '../components/layouts/AdminLayout';
import CustomerLayout from '../components/layouts/CustomerLayout';
import TherapistLayout from '../components/layouts/TherapistLayout';

// Public Pages
import HomePage from '../pages/public/HomePage';
import AboutPage from '../pages/public/AboutPage';
import ServicesPage from '../pages/public/ServicesPage';
import ContactPage from '../pages/public/ContactPage';
import LoginPage from '../pages/public/LoginPage';
import RegisterPage from '../pages/public/RegisterPage';

// Customer Pages
import CustomerDashboard from '../pages/customer/Dashboard';
import CustomerAppointments from '../pages/customer/Appointments';
import CustomerProfile from '../pages/customer/Profile';
import CustomerBilling from '../pages/customer/Billing';
import CustomerMedicalRecords from '../pages/customer/MedicalRecords';

// Therapist Pages
import TherapistDashboard from '../pages/therapist/Dashboard';
import TherapistSchedule from '../pages/therapist/Schedule';
import TherapistPatients from '../pages/therapist/Patients';
import TherapistProfile from '../pages/therapist/Profile';

// Admin Pages
import AdminDashboard from '../pages/admin/Dashboard';
import AdminUsers from '../pages/admin/Users';
import AdminAppointments from '../pages/admin/Appointments';
import AdminServices from '../pages/admin/Services';
import AdminInventory from '../pages/admin/Inventory';
import AdminFinance from '../pages/admin/Finance';
import AdminAnalytics from '../pages/admin/Analytics';
import AdminSettings from '../pages/admin/Settings';

// Error pages
import ErrorPage from '../pages/ErrorPage';

const router = createBrowserRouter([
  {
    path: '/',
    element: <RootLayout />,
    errorElement: <ErrorPage />,
    children: [
      // Public routes
      { index: true, element: <HomePage /> },
      { path: 'about', element: <AboutPage /> },
      { path: 'services', element: <ServicesPage /> },
      { path: 'contact', element: <ContactPage /> },
      { path: 'login', element: <LoginPage /> },
      { path: 'register', element: <RegisterPage /> },
      
      // Customer routes
      {
        path: 'customer',
        element: <CustomerLayout />,
        children: [
          { index: true, element: <CustomerDashboard /> },
          { path: 'appointments', element: <CustomerAppointments /> },
          { path: 'profile', element: <CustomerProfile /> },
          { path: 'billing', element: <CustomerBilling /> },
          { path: 'medical-records', element: <CustomerMedicalRecords /> },
        ],
      },
      
      // Therapist routes
      {
        path: 'therapist',
        element: <TherapistLayout />,
        children: [
          { index: true, element: <TherapistDashboard /> },
          { path: 'schedule', element: <TherapistSchedule /> },
          { path: 'patients', element: <TherapistPatients /> },
          { path: 'profile', element: <TherapistProfile /> },
        ],
      },
      
      // Admin routes
      {
        path: 'admin',
        element: <AdminLayout />,
        children: [
          { index: true, element: <AdminDashboard /> },
          { path: 'users', element: <AdminUsers /> },
          { path: 'appointments', element: <AdminAppointments /> },
          { path: 'services', element: <AdminServices /> },
          { path: 'inventory', element: <AdminInventory /> },
          { path: 'finance', element: <AdminFinance /> },
          { path: 'analytics', element: <AdminAnalytics /> },
          { path: 'settings', element: <AdminSettings /> },
        ],
      },
    ],
  },
]);

export default router;
