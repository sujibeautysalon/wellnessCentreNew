import { Link } from 'react-router-dom';

const Header = () => {
  return (
    <header className="bg-white border-b border-gray-200">
      <div className="container mx-auto px-4 py-4 flex items-center justify-between">
        <div className="flex items-center">
          <Link to="/" className="text-2xl font-bold text-primary-600">
            Wellness Center
          </Link>
        </div>
        
        <nav className="hidden md:flex space-x-8">
          <Link to="/" className="text-gray-600 hover:text-primary-600 transition">
            Home
          </Link>
          <Link to="/about" className="text-gray-600 hover:text-primary-600 transition">
            About
          </Link>
          <Link to="/services" className="text-gray-600 hover:text-primary-600 transition">
            Services
          </Link>
          <Link to="/contact" className="text-gray-600 hover:text-primary-600 transition">
            Contact
          </Link>
        </nav>
        
        <div className="flex items-center space-x-4">
          <Link to="/login" className="text-gray-600 hover:text-primary-600 transition">
            Log In
          </Link>
          <Link to="/register" className="bg-primary-600 text-white px-4 py-2 rounded-md hover:bg-primary-700 transition">
            Sign Up
          </Link>
        </div>
      </div>
    </header>
  );
};

export default Header;
