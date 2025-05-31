import { Link } from 'react-router-dom';

const Footer = () => {
  return (
    <footer className="bg-gray-800 text-white py-12">
      <div className="container mx-auto px-4">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
          <div>
            <h3 className="text-xl font-bold mb-4">Wellness Center</h3>
            <p className="text-gray-300 mb-4">
              Your one-stop destination for holistic health and wellness services.
            </p>
          </div>
          
          <div>
            <h4 className="text-lg font-semibold mb-4">Quick Links</h4>
            <ul className="space-y-2">
              <li>
                <Link to="/" className="text-gray-300 hover:text-white transition">
                  Home
                </Link>
              </li>
              <li>
                <Link to="/about" className="text-gray-300 hover:text-white transition">
                  About Us
                </Link>
              </li>
              <li>
                <Link to="/services" className="text-gray-300 hover:text-white transition">
                  Services
                </Link>
              </li>
              <li>
                <Link to="/contact" className="text-gray-300 hover:text-white transition">
                  Contact
                </Link>
              </li>
            </ul>
          </div>
          
          <div>
            <h4 className="text-lg font-semibold mb-4">Services</h4>
            <ul className="space-y-2">
              <li>
                <Link to="/services" className="text-gray-300 hover:text-white transition">
                  Massage Therapy
                </Link>
              </li>
              <li>
                <Link to="/services" className="text-gray-300 hover:text-white transition">
                  Acupuncture
                </Link>
              </li>
              <li>
                <Link to="/services" className="text-gray-300 hover:text-white transition">
                  Physiotherapy
                </Link>
              </li>
              <li>
                <Link to="/services" className="text-gray-300 hover:text-white transition">
                  Nutrition Counseling
                </Link>
              </li>
            </ul>
          </div>
          
          <div>
            <h4 className="text-lg font-semibold mb-4">Contact Us</h4>
            <address className="text-gray-300 not-italic">
              <p>123 Wellness Street</p>
              <p>Healthy City, HC 12345</p>
              <p className="mt-2">Email: info@wellnesscenter.com</p>
              <p>Phone: (123) 456-7890</p>
            </address>
          </div>
        </div>
        
        <div className="border-t border-gray-700 mt-8 pt-6">
          <p className="text-center text-gray-300">
            © {new Date().getFullYear()} Wellness Center. All rights reserved.
          </p>
        </div>
      </div>
    </footer>
  );
};

export default Footer;
