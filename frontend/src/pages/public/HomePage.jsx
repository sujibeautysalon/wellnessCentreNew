import { Link } from 'react-router-dom';

const HomePage = () => {
  return (
    <div>
      {/* Hero Section */}
      <section className="bg-primary-50 py-16">
        <div className="container mx-auto px-4">
          <div className="flex flex-col lg:flex-row items-center">
            <div className="lg:w-1/2 lg:pr-12 mb-10 lg:mb-0">
              <h1 className="text-4xl md:text-5xl font-bold text-gray-800 mb-6">
                Your Journey to Wellness Starts Here
              </h1>
              <p className="text-lg text-gray-600 mb-8">
                Experience holistic health and wellness services tailored to your individual needs.
                Our expert team is dedicated to helping you achieve balance, health, and vitality.
              </p>
              <div className="flex flex-col sm:flex-row space-y-4 sm:space-y-0 sm:space-x-4">
                <Link
                  to="/services"
                  className="px-6 py-3 bg-primary-600 text-white font-semibold rounded-md hover:bg-primary-700 transition text-center"
                >
                  Explore Our Services
                </Link>
                <Link
                  to="/contact"
                  className="px-6 py-3 border border-primary-600 text-primary-600 font-semibold rounded-md hover:bg-primary-50 transition text-center"
                >
                  Book Appointment
                </Link>
              </div>
            </div>
            <div className="lg:w-1/2">
              <img
                src="/hero-image.jpg"
                alt="Wellness Center"
                className="rounded-lg shadow-xl"
              />
            </div>
          </div>
        </div>
      </section>

      {/* Services Preview */}
      <section className="py-16">
        <div className="container mx-auto px-4">
          <div className="text-center mb-12">
            <h2 className="text-3xl font-bold text-gray-800 mb-4">Our Services</h2>
            <p className="text-lg text-gray-600 max-w-3xl mx-auto">
              We offer a comprehensive range of wellness services to address your physical,
              mental, and emotional health needs.
            </p>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            <div className="bg-white rounded-lg shadow-md overflow-hidden">
              <img src="/massage.jpg" alt="Massage Therapy" className="w-full h-48 object-cover" />
              <div className="p-6">
                <h3 className="text-xl font-semibold text-gray-800 mb-2">Massage Therapy</h3>
                <p className="text-gray-600 mb-4">
                  Relieve tension and promote relaxation with our therapeutic massage services.
                </p>
                <Link to="/services" className="text-primary-600 hover:text-primary-800 font-medium">
                  Learn More →
                </Link>
              </div>
            </div>
            
            <div className="bg-white rounded-lg shadow-md overflow-hidden">
              <img src="/acupuncture.jpg" alt="Acupuncture" className="w-full h-48 object-cover" />
              <div className="p-6">
                <h3 className="text-xl font-semibold text-gray-800 mb-2">Acupuncture</h3>
                <p className="text-gray-600 mb-4">
                  Experience the ancient practice of acupuncture for pain relief and wellness.
                </p>
                <Link to="/services" className="text-primary-600 hover:text-primary-800 font-medium">
                  Learn More →
                </Link>
              </div>
            </div>
            
            <div className="bg-white rounded-lg shadow-md overflow-hidden">
              <img src="/physio.jpg" alt="Physiotherapy" className="w-full h-48 object-cover" />
              <div className="p-6">
                <h3 className="text-xl font-semibold text-gray-800 mb-2">Physiotherapy</h3>
                <p className="text-gray-600 mb-4">
                  Restore movement and function with our expert physiotherapy services.
                </p>
                <Link to="/services" className="text-primary-600 hover:text-primary-800 font-medium">
                  Learn More →
                </Link>
              </div>
            </div>
          </div>
          
          <div className="text-center mt-12">
            <Link
              to="/services"
              className="px-6 py-3 bg-primary-600 text-white font-semibold rounded-md hover:bg-primary-700 transition"
            >
              View All Services
            </Link>
          </div>
        </div>
      </section>

      {/* Testimonials */}
      <section className="bg-gray-50 py-16">
        <div className="container mx-auto px-4">
          <div className="text-center mb-12">
            <h2 className="text-3xl font-bold text-gray-800 mb-4">What Our Clients Say</h2>
            <p className="text-lg text-gray-600 max-w-3xl mx-auto">
              Don't just take our word for it. Here's what our clients have to say about their experiences.
            </p>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            <div className="bg-white p-6 rounded-lg shadow">
              <div className="flex items-center space-x-1 mb-4">
                <span className="text-yellow-400">★★★★★</span>
                <span className="text-gray-600">(5.0)</span>
              </div>
              <p className="text-gray-600 mb-6">
                "The massage therapy at Wellness Center has completely transformed my chronic back pain.
                The therapists are highly skilled and attentive to my needs."
              </p>
              <div className="flex items-center">
                <img
                  src="/avatar1.jpg"
                  alt="Sarah Johnson"
                  className="w-12 h-12 rounded-full object-cover mr-4"
                />
                <div>
                  <h4 className="font-semibold">Sarah Johnson</h4>
                  <p className="text-sm text-gray-500">Regular Client</p>
                </div>
              </div>
            </div>
            
            <div className="bg-white p-6 rounded-lg shadow">
              <div className="flex items-center space-x-1 mb-4">
                <span className="text-yellow-400">★★★★★</span>
                <span className="text-gray-600">(5.0)</span>
              </div>
              <p className="text-gray-600 mb-6">
                "I've been coming here for acupuncture for six months and have seen incredible improvements
                in my energy levels and overall wellbeing. Highly recommended!"
              </p>
              <div className="flex items-center">
                <img
                  src="/avatar2.jpg"
                  alt="Michael Chen"
                  className="w-12 h-12 rounded-full object-cover mr-4"
                />
                <div>
                  <h4 className="font-semibold">Michael Chen</h4>
                  <p className="text-sm text-gray-500">Regular Client</p>
                </div>
              </div>
            </div>
            
            <div className="bg-white p-6 rounded-lg shadow">
              <div className="flex items-center space-x-1 mb-4">
                <span className="text-yellow-400">★★★★★</span>
                <span className="text-gray-600">(5.0)</span>
              </div>
              <p className="text-gray-600 mb-6">
                "The nutritionist at Wellness Center created a personalized plan that helped me achieve
                my health goals. Their holistic approach makes all the difference."
              </p>
              <div className="flex items-center">
                <img
                  src="/avatar3.jpg"
                  alt="Emily Rodriguez"
                  className="w-12 h-12 rounded-full object-cover mr-4"
                />
                <div>
                  <h4 className="font-semibold">Emily Rodriguez</h4>
                  <p className="text-sm text-gray-500">Regular Client</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="bg-primary-700 text-white py-16">
        <div className="container mx-auto px-4 text-center">
          <h2 className="text-3xl font-bold mb-6">Start Your Wellness Journey Today</h2>
          <p className="text-lg mb-8 max-w-3xl mx-auto">
            Take the first step towards a healthier, more balanced life. Schedule your appointment
            with our expert team of wellness professionals.
          </p>
          <Link
            to="/contact"
            className="px-8 py-4 bg-white text-primary-700 font-semibold rounded-md hover:bg-gray-100 transition"
          >
            Book Your Appointment
          </Link>
        </div>
      </section>
    </div>
  );
};

export default HomePage;
