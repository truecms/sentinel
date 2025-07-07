const LandingPageSimple = () => {
  return (
    <div className="container mx-auto px-4 py-16">
      <div className="text-center max-w-4xl mx-auto">
        <h1 className="text-5xl font-bold mb-6">
          Monitor Your Drupal Sites' Security
        </h1>
        <p className="text-xl text-gray-600 mb-8">
          Real-time monitoring and alerting for security updates across all your Drupal installations
        </p>
        <div className="flex gap-4 justify-center">
          <button className="bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700">
            Start Free Trial
          </button>
          <button className="border border-gray-300 px-6 py-3 rounded-lg hover:bg-gray-50">
            View Demo
          </button>
        </div>
      </div>
      
      <div className="grid md:grid-cols-4 gap-8 mt-16">
        <div className="text-center">
          <div className="text-3xl font-bold text-blue-600">10K+</div>
          <div className="text-gray-600">Sites Monitored</div>
        </div>
        <div className="text-center">
          <div className="text-3xl font-bold text-blue-600">99.9%</div>
          <div className="text-gray-600">Uptime</div>
        </div>
        <div className="text-center">
          <div className="text-3xl font-bold text-blue-600">24/7</div>
          <div className="text-gray-600">Monitoring</div>
        </div>
        <div className="text-center">
          <div className="text-3xl font-bold text-blue-600">&lt;5min</div>
          <div className="text-gray-600">Alert Time</div>
        </div>
      </div>
    </div>
  );
};

export default LandingPageSimple;