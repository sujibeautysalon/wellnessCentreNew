import { useRouteError, Link } from 'react-router-dom';

const ErrorPage = () => {
  const error = useRouteError();
  
  return (
    <div className="min-h-screen flex flex-col items-center justify-center bg-gray-50 px-4">
      <div className="text-center">
        <h1 className="text-6xl font-bold text-red-600 mb-4">Oops!</h1>
        <h2 className="text-3xl font-semibold text-gray-800 mb-6">
          {error.status === 404 ? "Page Not Found" : "An Error Occurred"}
        </h2>
        <p className="text-xl text-gray-600 mb-8">
          {error.statusText || error.message || 
            "Sorry, we couldn't find the page you're looking for or something went wrong."}
        </p>
        <Link
          to="/"
          className="bg-primary-600 text-white px-6 py-3 rounded-md hover:bg-primary-700 transition inline-block"
        >
          Return to Homepage
        </Link>
      </div>
    </div>
  );
};

export default ErrorPage;
